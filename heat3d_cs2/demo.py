"""
What a CS2 demo holds, read with demoparser2: the players sampled through the
match, and every event with a place on the map.

A demo is the server's own recording - SourceTV - so it has every player, every
tick (64 a second). Two things about the demos found in the wild decide how it
is read:

- A match can be split across files. The parts' names do not say their order
  (a "-p2" can be the earlier half), but the server's clock runs on across
  them, so parts are put in order by it, and so is everything in them.
- A recording can start before the match: warmup, a restart, a knife round.
  The match starts at the last "match start" announcement in a part, and
  warmup is left out everywhere.

Nothing here interprets the match; that is `match.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

TICKRATE = 64

#: What is read for every sampled player.
PLAYER_FIELDS = [
    "X",
    "Y",
    "Z",
    "yaw",
    "pitch",
    "health",
    "armor_value",
    "team_num",
    "team_clan_name",
    "active_weapon_name",
    "is_alive",
    "last_place_name",
    "balance",
    "current_equip_value",
]

#: More of each sampled player, demoparser2's name -> the table's column. Counters ending in `_total` are the
#: game's own scoreboard counts for the match so far.
SAMPLE_FIELDS = {
    "flash_duration": "flash",
    "flash_max_alpha": "flashAlpha",
    "has_helmet": "helmet",
    "has_defuser": "defuser",
    "is_scoped": "scoped",
    "zoom_lvl": "zoom",
    "is_walking": "walking",
    "duck_amount": "duck",
    "is_airborne": "airborne",
    "in_buy_zone": "buyZone",
    "in_bomb_zone": "bombZone",
    "is_defusing": "defusing",
    "spotted": "spotted",
    "approximate_spotted_by": "spottedBy",
    "inventory": "inventory",
    "active_weapon_ammo": "ammo",
    "total_ammo_left": "ammoReserve",
    "shots_fired": "shotsFired",
    "aim_punch_angle": "aimPunch",
    "move_type": "moveType",
    "ping": "ping",
    "kills_total": "killsTotal",
    "deaths_total": "deathsTotal",
    "assists_total": "assistsTotal",
    "headshot_kills_total": "headshotKillsTotal",
    "damage_total": "damageTotal",
    "utility_damage_total": "utilityDamageTotal",
    "enemies_flashed_total": "enemiesFlashedTotal",
    "objective_total": "objectiveTotal",
    "ace_rounds_total": "aceRoundsTotal",
    "3k_rounds_total": "threeKillRoundsTotal",
    "alive_time_total": "aliveTimeTotal",
    "money_saved_total": "moneySavedTotal",
    "mvps": "mvps",
    "score": "score",
    "cash_spent_this_round": "cashSpent",
    "total_cash_spent": "cashSpentTotal",
    "round_start_equip_value": "roundStartEquipment",
}

#: What stays the same for a player through a match: read with the samples, kept once per player.
PROFILE_FIELDS = ["crosshair_code", "music_kit_id", "rank", "comp_wins", "player_color", "is_connected"]

#: The game's state besides the round count: timeouts, the bomb, players alive, losing streaks, its clock.
STATE_FIELDS = [
    "game_phase",
    "round_in_progress",
    "is_terrorist_timeout",
    "is_ct_timeout",
    "num_terrorist_timeouts",
    "num_ct_timeouts",
    "is_technical_timeout",
    "is_waiting_for_resume",
    "is_bomb_planted",
    "is_bomb_dropped",
    "num_player_alive_ct",
    "num_player_alive_t",
    "ct_losing_streak",
    "t_losing_streak",
    "match_start_time",
    "round_start_time",
]

#: The game's count of the overtime being played, 0 in regulation: it has no
#: shorter name in the parser, so it is asked for by the game's own.
OVERTIME = "CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying"

#: The game's own state, read alongside: the round count, who won it and how,
#: the score, the clock, overtime.
RULES_FIELDS = [
    "game_time",
    "total_rounds_played",
    "round_win_status",
    "round_win_reason",
    "team_rounds_total",
    "is_warmup_period",
    "is_freeze_period",
    OVERTIME,
]

#: For each player in an event: where they were, on which side, and which bomb
#: zone they stood in (0 none, 1 A, 2 B) - what names a plant's site; which way
#: they looked and how far they crouched - where a hit's ray is traced from and
#: to (`impact.py`).
EVENT_PLAYER = ["X", "Y", "Z", "team_num", "last_place_name", "which_bomb_zone", "pitch", "yaw", "duck_amount"]

#: Events the match is built from. Every other event the demo lists is read too (`read_part`).
EVENTS = [
    "player_death",
    "player_hurt",
    "player_blind",
    "weapon_fire",
    "smokegrenade_detonate",
    "flashbang_detonate",
    "hegrenade_detonate",
    "inferno_startburn",
    "decoy_detonate",
    "bomb_planted",
    "bomb_defused",
    "bomb_exploded",
    "round_freeze_end",
    "round_prestart",
    "round_announce_match_start",
]

#: Far past the end of any match: the sampled ticks are a stride up to here,
#: and the parser stops at the demo's end.
LAST_TICK = 4_000_000


@dataclass
class RawPart:
    """One demo file as the parser gives it, untouched."""

    path: str
    map: str
    #: One row per player per sampled tick: PLAYER_FIELDS, RULES_FIELDS,
    #: tick, steamid, name.
    samples: pd.DataFrame
    #: Event name -> its rows, players' fields prefixed `user_`, `attacker_`,
    #: `assister_` as the parser names them.
    events: dict[str, pd.DataFrame] = field(default_factory=dict)
    #: Every grenade in flight, every tick: type, entity, thrower, x, y, z.
    grenades: pd.DataFrame | None = None
    #: The demo's header, its players (coaches and casters too), skins and item drops where it has them.
    header: dict = field(default_factory=dict)
    player_info: pd.DataFrame | None = None
    skins: pd.DataFrame | None = None
    item_drops: pd.DataFrame | None = None
    #: Every entity property's changes, as `keep.read_props` gives them; None reads them from the file when
    #: the sidecars are written (`keep.py`), which is where the rest of the demo is read too.
    props: pd.DataFrame | None = None


def _safe(read):
    """What a parser call returns, or None where this demo has nothing of the kind (the parser raises)."""
    try:
        return read()
    except Exception:  # noqa: BLE001 - one missing table does not stop the rest
        return None


def read_part(path: str | Path, every: int = 8) -> RawPart:
    """Read one demo file: players every `every` ticks, every event, every grenade's flight."""
    from demoparser2 import DemoParser

    parser = DemoParser(str(path))
    header = parser.parse_header()
    available = sorted(set(parser.list_game_events()))
    fields = PLAYER_FIELDS + list(SAMPLE_FIELDS) + PROFILE_FIELDS + RULES_FIELDS + STATE_FIELDS
    samples = parser.parse_ticks(fields, ticks=list(range(0, LAST_TICK, every)))
    events: dict[str, pd.DataFrame] = {}
    # Every event in one pass over the file.
    for name, df in parser.parse_events(available, player=EVENT_PLAYER, other=["total_rounds_played", "is_warmup_period"]):
        events[name] = df
    return RawPart(
        str(path),
        header.get("map_name", ""),
        samples,
        events,
        grenades=_safe(parser.parse_grenades),
        header=dict(header),
        player_info=_safe(parser.parse_player_info),
        skins=_safe(parser.parse_skins),
        item_drops=_safe(parser.parse_item_drops),
    )
