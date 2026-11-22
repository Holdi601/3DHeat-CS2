"""
A match from its demo parts: the rounds and how each was won, every player's
position through them, every event where it happened, and what each player
did with it.

Everything is put on one clock, the match's: seconds from the start of the
live match, read from the server's own clock so a match split across demo
files runs on across the join. A round runs from the end of its freeze time
(players can move) to the next round's start; the part after it was decided
is its "after" phase, where the winners hunt and the losers save.

The conventions, where the game itself does not define them:

- A death is **traded** when its killer is killed by one of the victim's
  teammates within 5 s; that kill is a **trade kill**.
- The round's first kill of an enemy, while it is live, is its **opening**
  duel; a teamkill, a suicide or a death to the world before it is passed
  over.
- **KAST**: the share of rounds in which a player killed, assisted (a flash
  assist counts), survived, or was traded.
- **Damage** is what the victim actually lost: a 137 damage headshot on a
  player with 40 health is 40, as the scoreboard counts it.
- A **clutch** is being the last player alive on a side with enemies still
  standing; it is won when the side wins the round.
- **Buy**, per side, from the average equipment value at the end of freeze
  time: the first round of each regulation half is a pistol round, then under
  $1,500 is an eco, under $4,000 a force buy, and anything more a full buy.
  The half is as long as the match played it: the sides first swap after it.
  Overtime starts with money set by the server and has no pistol round.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import events as more
from . import impact
from .demo import OVERTIME, TICKRATE, RawPart

TRADE_SECONDS = 5.0

#: The game's round win status: who won the round, once it is decided.
WIN_STATUS = {1: "", 2: "T", 3: "CT"}

#: The game's round end reasons (CSRoundEndReason) that occur in a defusal match.
REASONS = {
    1: "bomb",
    7: "defuse",
    8: "elimination",
    9: "elimination",
    10: "draw",
    12: "time",
    17: "surrender",
    18: "surrender",
}

#: A death or damage event's weapon id -> the name the game shows, as the
#: players' own `active_weapon_name` has it.
WEAPONS = {
    "ak47": "AK-47",
    "aug": "AUG",
    "awp": "AWP",
    "bizon": "PP-Bizon",
    "c4": "C4 Explosive",
    "planted_c4": "C4 Explosive",
    "cz75a": "CZ75-Auto",
    "deagle": "Desert Eagle",
    "decoy": "Decoy Grenade",
    "elite": "Dual Berettas",
    "famas": "FAMAS",
    "fiveseven": "Five-SeveN",
    "flashbang": "Flashbang",
    "g3sg1": "G3SG1",
    "galilar": "Galil AR",
    "glock": "Glock-18",
    "hegrenade": "High Explosive Grenade",
    "hkp2000": "P2000",
    "incgrenade": "Incendiary Grenade",
    "inferno": "Molotov",
    "m249": "M249",
    "m4a1": "M4A4",
    "m4a1_silencer": "M4A1-S",
    "mac10": "MAC-10",
    "mag7": "MAG-7",
    "molotov": "Molotov",
    "mp5sd": "MP5-SD",
    "mp7": "MP7",
    "mp9": "MP9",
    "negev": "Negev",
    "nova": "Nova",
    "p250": "P250",
    "p90": "P90",
    "revolver": "R8 Revolver",
    "sawedoff": "Sawed-Off",
    "scar20": "SCAR-20",
    "sg556": "SG 553",
    "smokegrenade": "Smoke Grenade",
    "ssg08": "SSG 08",
    "taser": "Zeus x27",
    "tec9": "Tec-9",
    "ump45": "UMP-45",
    "usp_silencer": "USP-S",
    "world": "World",
    "xm1014": "XM1014",
}

SIDES = ("T", "CT")

#: Knife skins, as the players' active weapon names them.
KNIVES = ("Knife", "Bayonet", "Karambit", "Daggers")

GRENADES = {"smokegrenade", "flashbang", "hegrenade", "molotov", "incgrenade", "decoy"}
UTILITY_DAMAGE = {"hegrenade", "inferno", "molotov", "incgrenade"}

#: Detonation events -> the row's event name.
DETONATIONS = {
    "smokegrenade_detonate": "smoke",
    "flashbang_detonate": "flash",
    "hegrenade_detonate": "he",
    "inferno_startburn": "molotov",
    "decoy_detonate": "decoy",
}


def weapon_name(weapon: object) -> str:
    """A weapon id from an event (`ak47`, `weapon_ak47`, `knife_karambit`) as the game names it."""
    w = str(weapon or "").removeprefix("weapon_")
    if not w:
        return ""
    if "knife" in w or "bayonet" in w:
        return "Knife"
    return WEAPONS.get(w, w)


def held(name: object) -> str:
    """A player's active weapon by its name, every knife skin as `Knife`."""
    w = str(name or "")
    return "Knife" if any(k in w for k in KNIVES) else w


def side_of(team_num: object) -> str:
    try:
        n = int(team_num)
    except (TypeError, ValueError):
        return ""
    return "T" if n == 2 else "CT" if n == 3 else ""


def buy_type(average_equipment: float, pistol: bool) -> str:
    if pistol:
        return "pistol"
    if average_equipment < 1500:
        return "eco"
    if average_equipment < 4000:
        return "force"
    return "full"


@dataclass
class Round:
    #: The game's round number, 1-based.
    number: int
    #: Match seconds: freeze time over, the round decided, the next round started.
    start: float
    end: float
    until: float
    #: `T` or `CT`; empty for a draw, which the game decides with no winner.
    winner: str
    reason: str
    #: Team name -> rounds won after this one, and the side it played.
    score: dict[str, int]
    sides: dict[str, str]
    #: Side -> team equipment value at the end of freeze time, and the buy.
    equipment: dict[str, int] = field(default_factory=dict)
    buy: dict[str, str] = field(default_factory=dict)
    #: The bomb plant, if any: site, seconds into the round, planter, position, place.
    plant: dict | None = None
    #: Match seconds the planted bomb went off, if it did.
    exploded: float | None = None


@dataclass
class Match:
    name: str
    map: str
    parts: list[str]
    rounds: list[Round]
    #: steamid -> name and team.
    players: dict[str, dict]
    #: Team names, in the order they first played T then CT... as first seen.
    teams: list[str]
    #: The long table: every position sample and every event, one row each.
    rows: pd.DataFrame
    #: One row per death, with who, how, opening, traded.
    kills: pd.DataFrame
    #: Effective damage between enemies, one row per hit.
    damage: pd.DataFrame
    #: Enemies blinded by a flash, one row per player blinded.
    blinds: pd.DataFrame
    #: Skipped rounds (cut off by the end of a demo), by the game's number.
    incomplete: list[int] = field(default_factory=list)
    #: Rounds in a regulation half, where the recording shows the sides swap; and the pistol rounds.
    half: int | None = None
    pistol: list[int] = field(default_factory=list)
    #: Events about no player (round beeps, server messages, the broadcast camera...): name, time, fields.
    events: list[dict] = field(default_factory=list)
    #: The game's state where it changed: time, field, value.
    state: list[dict] = field(default_factory=list)
    #: The team that won the match, and how that is known (`_match_winner`); empty and None where it is not.
    winner: str = ""
    winner_source: str | None = None
    #: steamid -> what stays the same through the match (crosshair, music kit, rank, colour).
    profiles: dict[str, dict] = field(default_factory=dict)
    #: The first part's header; every part's players as the demo lists them, skins and item drops.
    header: dict = field(default_factory=dict)
    player_info: list[dict] = field(default_factory=list)
    skins: list[dict] = field(default_factory=list)
    item_drops: list[dict] = field(default_factory=list)
    #: Each part as read, in order, and its clock: (the part, server clock at its first sampled tick, that
    #: tick, the match's zero on the server clock) - for the sidecars (`keep.py`), which put everything on
    #: the table's clock.
    sources: list[tuple] = field(default_factory=list)


# ---------------------------------------------------------------- the clock


def _one_per_tick(samples: pd.DataFrame) -> pd.DataFrame:
    """
    One row per player per tick.

    Where a round was restored from a backup, the demo carries the players'
    old bodies alongside the new ones for some seconds: two rows for one
    player at one tick, one where the voided round left them, one at the
    restored round's spawn. The one that leads on into the player's next
    single row is theirs - so each is chosen walking back from there.
    """
    dup = samples.duplicated(["steamid", "tick"], keep=False)
    if not dup.any():
        return samples
    s = samples.reset_index(drop=True)
    dup = dup.reset_index(drop=True)
    xyz = s[["X", "Y", "Z"]].to_numpy(dtype=float)
    drop: list[int] = []
    for sid, rows in s[dup].groupby("steamid"):
        ticks = sorted(rows["tick"].unique(), reverse=True)
        after = s.index[(s["steamid"] == sid) & ~dup & (s["tick"] > ticks[0])]
        ref = xyz[after.min()] if len(after) else None
        for tick in ticks:
            candidates = rows.index[rows["tick"] == tick]
            if ref is None or not np.isfinite(ref).all():
                best = candidates[-1]
            else:
                best = candidates[int(np.nanargmin(((xyz[candidates] - ref) ** 2).sum(axis=1)))]
            drop.extend(i for i in candidates if i != best)
            ref = xyz[best]
    return s.drop(index=drop)


class _Part:
    """One demo file on the match clock."""

    def __init__(self, raw: RawPart):
        raw.samples = _one_per_tick(raw.samples)
        self.raw = raw
        s = raw.samples
        clock = s[["tick", "game_time"]].dropna().drop_duplicates("tick").sort_values("tick")
        self.ticks = clock["tick"].to_numpy(dtype=float)
        self.clock = clock["game_time"].to_numpy(dtype=float)
        start = raw.events.get("round_announce_match_start")
        self.live_from = int(start["tick"].max()) if start is not None and len(start) else 0
        self.first_clock = float(self.at([self.live_from])[0]) if len(self.ticks) else math.inf
        self.last_clock = float(self.at([self.ticks[-1]])[0]) if len(self.ticks) else -math.inf
        # The game's index of the first and last round that starts here (its
        # freeze time ending), as the match's rounds count them.
        freezes = raw.events.get("round_freeze_end")
        index = (
            freezes.loc[(freezes["tick"] >= self.live_from) & ~_flag(freezes, "is_warmup_period"), "total_rounds_played"].dropna()
            if freezes is not None and "total_rounds_played" in freezes
            else pd.Series(dtype=float)
        )
        self.has_rounds = bool(len(index))
        self.rounds = (int(index.min()), int(index.max())) if len(index) else (0, 0)
        #: Server clock at the match's zero: set when the parts are put in order.
        self.offset = self.first_clock
        #: The ticks between player samples, as the part was read.
        ticks = np.unique(s["tick"].to_numpy()) if len(s) else np.array([])
        self.every = int(np.median(np.diff(ticks))) if len(ticks) > 1 else 8

    def at(self, ticks):
        """
        Seconds on the server's clock at `ticks`: from where the file starts,
        counted in ticks. The ticks never stop; the server's own clock can - it
        stands still through a pause while the ticks run on - and read through
        it two moments would share a time.
        """
        t = np.atleast_1d(np.asarray(ticks, dtype=float))
        if not len(self.ticks):
            return t / TICKRATE
        return self.clock[0] + (t - self.ticks[0]) / TICKRATE


def _flag(df: pd.DataFrame, column: str) -> pd.Series:
    """A boolean column, False where the demo does not have it."""
    if column not in df:
        return pd.Series(False, index=df.index)
    return df[column].fillna(False).astype(bool)


def _rules(samples: pd.DataFrame) -> pd.DataFrame:
    """The game state once per sampled tick, from the players' rows."""
    s = samples[samples["team_num"].isin([2, 3])]
    columns = ["tick", "total_rounds_played", "round_win_status", "round_win_reason", "is_warmup_period"]
    return s.drop_duplicates("tick").sort_values("tick")[columns + [c for c in (OVERTIME,) if c in s]]


def _plant_sites(plants: pd.DataFrame) -> list[str]:
    """
    `A` or `B` for each plant. The game says which bomb zone the planter
    stood in (1 is A, 2 is B); a demo without it has the planter's place name.
    The event's own `site` is the zone's entity, a number: where one plant
    does not say its letter, another plant on the same entity can.
    """
    zones = plants["user_which_bomb_zone"] if "user_which_bomb_zone" in plants else pd.Series(np.nan, index=plants.index)
    places = plants["user_last_place_name"] if "user_last_place_name" in plants else pd.Series("", index=plants.index)
    entities = plants["site"] if "site" in plants else pd.Series(np.nan, index=plants.index)
    letters = []
    for zone, place in zip(zones, places.fillna("").astype(str)):
        zone = int(zone) if pd.notna(zone) else 0
        letters.append(
            "A" if zone == 1 else "B" if zone == 2 else "A" if "BombsiteA" in place else "B" if "BombsiteB" in place else ""
        )
    by_entity: dict[str, set[str]] = {}
    for entity, letter in zip(entities.astype(str), letters):
        if letter:
            by_entity.setdefault(entity, set()).add(letter)
    known = {e: next(iter(v)) for e, v in by_entity.items() if len(v) == 1}
    return [letter or known.get(entity, "") for entity, letter in zip(entities.astype(str), letters)]


@dataclass
class _Window:
    """Where a round lies in its part, and its score by the game's team numbers."""

    part: _Part
    freeze_tick: int
    end_tick: int
    #: team number (2 T, 3 CT) -> rounds won after this one, NaN where the demo had none.
    score: dict[int, float]
    #: side -> living players at the end of freeze time, whose equipment is summed.
    players: dict[str, int] = field(default_factory=dict)
    #: The game's overtime count at the end of freeze time (0 in regulation); None where the demo has none.
    overtime: int | None = None


def _rounds_in(part: _Part, origin: float) -> tuple[dict[int, tuple[Round, _Window]], list[int]]:
    """Every round decided in one part, by the game's 0-based round index. Teams are named later."""
    raw = part.raw
    freezes = raw.events.get("round_freeze_end")
    if freezes is None or not len(freezes):
        return {}, []
    freezes = freezes[(freezes["tick"] >= part.live_from) & ~_flag(freezes, "is_warmup_period")]
    freezes = freezes.sort_values("tick")
    rules = _rules(raw.samples)
    prestarts = raw.events.get("round_prestart")
    prestart_ticks = np.sort(prestarts["tick"].to_numpy()) if prestarts is not None else np.array([])
    teams = raw.samples[raw.samples["team_num"].isin([2, 3])]
    last_tick = int(raw.samples["tick"].max())
    plants = raw.events.get("bomb_planted")
    if plants is not None and len(plants):
        plants = plants[(plants["tick"] >= part.live_from) & ~_flag(plants, "is_warmup_period")].sort_values("tick")
        plants = plants.assign(letter=_plant_sites(plants))
    exploded = raw.events.get("bomb_exploded")
    exploded_ticks = np.sort(exploded["tick"].to_numpy()) if exploded is not None else np.array([])
    out: dict[int, tuple[Round, _Window]] = {}
    cut: list[int] = []
    freeze_ticks = freezes["tick"].to_numpy()
    for k, (tick, index) in enumerate(zip(freeze_ticks, freezes["total_rounds_played"].to_numpy())):
        index = int(index)
        limit = freeze_ticks[k + 1] if k + 1 < len(freeze_ticks) else last_tick + 1
        done = rules[
            (rules["tick"] > tick)
            & (rules["tick"] < limit)
            & (rules["total_rounds_played"] == index + 1)
            & rules["round_win_status"].isin(list(WIN_STATUS))
        ]
        if not len(done):
            cut.append(index + 1)
            continue
        end_tick = int(done["tick"].iloc[0])
        status = int(done["round_win_status"].iloc[0])
        reason = REASONS.get(int(done["round_win_reason"].iloc[0]), "other")
        after = prestart_ticks[prestart_ticks > end_tick]
        until_tick = int(after[0]) if len(after) and after[0] < limit else min(limit, last_tick)
        at_end = teams[teams["tick"] == end_tick].drop_duplicates("team_num")
        score_by_num = {int(r.team_num): float(r.team_rounds_total) for r in at_end.itertuples()}
        # Equipment at the end of freeze time: the first sample from then, alive players.
        frozen = teams[(teams["tick"] >= tick) & teams["is_alive"].astype(bool)]
        first = frozen["tick"].min() if len(frozen) else None
        equipment: dict[str, int] = {}
        counts: dict[str, int] = {}
        if first is not None:
            at_start = frozen[frozen["tick"] == first]
            for team_num, group in at_start.groupby("team_num"):
                equipment[side_of(team_num)] = int(group["current_equip_value"].fillna(0).sum())
                counts[side_of(team_num)] = len(group)
        overtime = None
        if OVERTIME in rules:
            playing = rules.loc[rules["tick"] >= tick, OVERTIME].dropna()
            overtime = int(playing.iloc[0]) if len(playing) else None
        number = index + 1
        start, end, until = part.at([tick, end_tick, until_tick]) - origin
        plant = None
        bomb = None
        if plants is not None and len(plants):
            p = plants[(plants["tick"] > tick) & (plants["tick"] <= end_tick)]
            if len(p):
                row = p.iloc[0]
                plant = {
                    "site": row["letter"],
                    # Seconds into the round, as the kills' times are.
                    "time": float(part.at([row["tick"]])[0] - origin - start),
                    "player": str(row.get("user_name") or ""),
                    "steamid": str(row.get("user_steamid") or ""),
                    "x": float(row["user_X"]),
                    "y": float(row["user_Y"]),
                    "z": float(row["user_Z"]),
                    # Where the planter stood is where the bomb lies.
                    "place": str(row.get("user_last_place_name") or ""),
                }
                went_off = exploded_ticks[(exploded_ticks > row["tick"]) & (exploded_ticks < limit)]
                if len(went_off):
                    bomb = float(part.at([went_off[0]])[0] - origin)
        out[index] = (
            Round(
                number=number,
                start=float(start),
                end=float(end),
                until=float(max(until, end)),
                winner=WIN_STATUS[status],
                reason=reason,
                score={},
                sides={},
                equipment=equipment,
                plant=plant,
                exploded=bomb,
            ),
            _Window(part, int(tick), end_tick, score_by_num, counts, overtime),
        )
    return out, cut


def _players(parts: list[_Part]) -> dict[str, dict]:
    """
    steamid -> name and team, for everyone who played: alive at least once
    while the match was live. A coach or a caster on a team's side never is.

    A player's team is the clan name the game gives their side, the one seen
    most - the demo clears it at its very end. A match played without clan
    names has its teams named by the side they started on.
    """
    names: dict[str, str] = {}
    clans: dict[str, Counter] = {}
    first: dict[str, tuple[float, int]] = {}
    for part in parts:
        s = part.raw.samples
        s = s[
            s["team_num"].isin([2, 3])
            & _flag(s, "is_alive")
            & ~_flag(s, "is_freeze_period")
            & ~_flag(s, "is_warmup_period")
            & (s["tick"] >= part.live_from)
        ]
        for sid, group in s.groupby("steamid"):
            sid = str(sid)
            names[sid] = str(group["name"].iloc[-1])
            clans.setdefault(sid, Counter()).update(str(c) for c in group["team_clan_name"].dropna() if str(c))
            at = (part.first_clock, int(group["tick"].iloc[0]))
            if sid not in first or at < first[sid][0:2]:
                first[sid] = (*at, int(group["team_num"].iloc[0]))
    out = {}
    for sid, name in names.items():
        clan = clans[sid].most_common(1)
        team = clan[0][0] if clan else f"Started {side_of(first[sid][2])}"
        out[sid] = {"name": name, "team": team}
    return out


def _pistol_rounds(rounds: list[Round], windows: list[_Window]) -> tuple[int | None, list[int]]:
    """
    The length of a regulation half and the pistol rounds: the first round,
    and the first after the half. A half ends where the sides first swap
    between two rounds that follow each other, both in regulation; the game's
    overtime count says which rounds are overtime, and where a demo has none,
    every round past two halves is. A recording that never shows the swap
    leaves the half unknown, and only round 1 a pistol round.
    """
    half = None
    for a, (b, wb) in zip(rounds, zip(rounds[1:], windows[1:])):
        if b.number != a.number + 1 or (wb.overtime or 0) > 0:
            continue
        common = set(a.sides) & set(b.sides)
        if common and all(a.sides[t] != b.sides[t] for t in common):
            half = a.number
            break
    firsts = {1} if half is None else {1, half + 1}
    pistol = []
    for r, w in zip(rounds, windows):
        regulation = w.overtime == 0 if w.overtime is not None else half is None or r.number <= 2 * half
        if r.number in firsts and regulation:
            pistol.append(r.number)
    return half, pistol


def _name_teams(rounds: list[Round], windows: list[_Window], players: dict[str, dict]) -> list[str]:
    """Each round's sides and score by team name, from who was on which side; the teams in order of appearance."""
    teams: list[str] = []
    previous: dict[str, int] = {}
    for r, w in zip(rounds, windows):
        s = w.part.raw.samples
        s = s[(s["tick"] >= w.freeze_tick) & (s["tick"] <= w.end_tick) & s["team_num"].isin([2, 3])]
        team_of: dict[int, str] = {}
        for num, group in s.groupby("team_num"):
            labels = Counter(players[str(sid)]["team"] for sid in group["steamid"].astype(str).unique() if str(sid) in players)
            if labels:
                team_of[int(num)] = labels.most_common(1)[0][0]
        r.sides = {team: side_of(num) for num, team in team_of.items()}
        for num in (2, 3):
            team = team_of.get(num)
            if team is None:
                continue
            if team not in teams:
                teams.append(team)
            won = w.score.get(num, math.nan)
            # The game's own count where the demo has it; else counted on.
            r.score[team] = int(won) if math.isfinite(won) else previous.get(team, 0) + int(r.winner == side_of(num))
        previous = dict(r.score)
    return teams


# ---------------------------------------------------------------- the rows


ROW_COLUMNS = [
    "match",
    "map",
    "round",
    "roundId",
    "phase",
    "time",
    "roundTime",
    "event",
    "player",
    "steamid",
    "side",
    "team",
    "x",
    "y",
    "z",
    "dirX",
    "dirY",
    "dirZ",
    "health",
    "armor",
    "money",
    "equipment",
    "weapon",
    "place",
    "throwerPlace",
    "other",
    "damage",
    "duration",
    "headshot",
    "opening",
    "traded",
    "noscope",
    "attackerBlind",
    "won",
    "matchWon",
    "roundEndReason",
    "buy",
]
# Everything else the demo says about a row: see `events`.
ROW_COLUMNS += [c for c in more.EXTRA_TEXT + more.EXTRA_NUMERIC + more.SAMPLE_COLUMNS if c not in ROW_COLUMNS]
#: The player's state at every row of theirs, events included (`_states`), and
#: the round's objective income (`_round_ends`): the viewer's factor and money
#: columns (`state_*`, `earn_*`).
STATE_COLUMNS = ["state_helmet", "state_defuser", "state_kevlar", "state_scoped", "state_flashed", "state_utility",
                 "state_weapon"]
ROW_COLUMNS += STATE_COLUMNS + ["earn_round_cs2"]

#: Round rewards in competitive play: a win (by the bomb or a defuse, more),
#: the loss bonus by the losing streak, the planting side's bonus for a lost
#: round with the bomb down, and the planter's and the defuser's own. What a
#: round paid is read from the players' money where it can be (`_round_ends`);
#: these are for the rounds it cannot (a half's last, money at the cap).
WIN_REWARD = {"elimination": 3250, "time": 3250, "bomb": 3500, "defuse": 3500}
LOSS_BONUS = [1400, 1900, 2400, 2900, 3400]
PLANT_BONUS = 600
MONEY_CAP = 16000
OBJECTIVE_REWARD = 300
#: What counts as utility in an inventory.
UTILITY = re.compile(r"grenade|flashbang|molotov|incendiary|decoy", re.I)


def _direction(yaw_deg, pitch_deg):
    """Where a player looks, as a unit vector in the game's frame (pitch down is positive)."""
    yaw = np.radians(np.asarray(yaw_deg, dtype=float))
    pitch = np.radians(np.asarray(pitch_deg, dtype=float))
    cp = np.cos(pitch)
    return cp * np.cos(yaw), cp * np.sin(yaw), -np.sin(pitch)


def _assign(times: np.ndarray, rounds: list[Round]) -> tuple[np.ndarray, np.ndarray]:
    """For each time: the index into `rounds` it falls in (-1 if none), and whether after the round was decided."""
    which = np.full(len(times), -1, dtype=int)
    after = np.zeros(len(times), dtype=bool)
    for k, r in enumerate(rounds):
        inside = (times >= r.start) & (times < r.until)
        which[inside] = k
        after[inside] = times[inside] > r.end
    return which, after


def _assign_phases(times: np.ndarray, rounds: list[Round]) -> tuple[np.ndarray, np.ndarray]:
    """
    For each time: the round it belongs to (-1 if none) and its phase: `freeze`
    from the previous round's end (two minutes before the first round's start)
    to the end of this round's freeze time, then `live`, then `after`.
    """
    which, after = _assign(times, rounds)
    phase = np.where(after, "after", "live").astype(object)
    for k, r in enumerate(rounds):
        since = rounds[k - 1].until if k else r.start - 120.0
        frozen = (which < 0) & (times >= since) & (times < r.start)
        which[frozen] = k
        phase[frozen] = "freeze"
    return which, phase


def _frame(columns: dict) -> pd.DataFrame:
    df = pd.DataFrame(columns)
    for c in ROW_COLUMNS:
        if c not in df:
            df[c] = np.nan if c in NUMERIC else ""
    return df[ROW_COLUMNS]


NUMERIC = {
    "round",
    "time",
    "roundTime",
    "x",
    "y",
    "z",
    "dirX",
    "dirY",
    "dirZ",
    "health",
    "armor",
    "money",
    "equipment",
    "damage",
    "duration",
    "headshot",
    "opening",
    "traded",
    "noscope",
    "attackerBlind",
    "won",
    "matchWon",
    "earn_round_cs2",
}
NUMERIC |= set(STATE_COLUMNS) - {"state_weapon"}
NUMERIC |= set(more.EXTRA_NUMERIC) | {c for c in more.SAMPLE_COLUMNS if c not in more.TEXT_SAMPLES}


def _event_rows(part: _Part, origin: float, prefix: str, df: pd.DataFrame, event: str, **extra) -> dict:
    """The common columns of an event's rows, for the player named by `prefix` (`user`, `attacker`)."""
    return {
        "time": part.at(df["tick"].to_numpy()) - origin,
        "event": event,
        "player": df[f"{prefix}_name"].fillna("").astype(str).to_numpy(),
        "steamid": df[f"{prefix}_steamid"].fillna("").astype(str).to_numpy(),
        "side": [side_of(v) for v in df[f"{prefix}_team_num"]],
        "x": df[f"{prefix}_X"].to_numpy(dtype=float),
        "y": df[f"{prefix}_Y"].to_numpy(dtype=float),
        "z": df[f"{prefix}_Z"].to_numpy(dtype=float),
        "place": df[f"{prefix}_last_place_name"].fillna("").astype(str).to_numpy(),
        **extra,
    }


def _in_order(parts: list[_Part]) -> list[_Part]:
    """Parts by the rounds they hold, then by the server's clock."""
    return sorted(parts, key=lambda p: (p.rounds[0], p.first_clock))


def chains(raws: list[RawPart]) -> list[list[RawPart]]:
    """
    Demo files named as one match, sorted into the matches they really are,
    the one with most rounds first.

    Parts of one match follow each other with the round count carrying on,
    and usually the server's clock too - but not always: a server restarted
    to restore a round starts its clock again, so the count decides and the
    clock only breaks a tie. A collection can also hold two different matches
    under one name - the same teams on the same map at two events - whose
    counts overlap, and those are kept apart. A file with no round in it
    (a pause, warmup) belongs to none.
    """
    out: list[list[_Part]] = []
    for part in _in_order([_Part(r) for r in raws]):
        if not part.has_rounds:
            continue
        for chain in out:
            last = chain[-1]
            clock_runs_on = part.first_clock >= last.last_clock - 5
            count_runs_on = last.rounds[1] <= part.rounds[0] <= last.rounds[1] + 1
            if part.rounds[0] >= last.rounds[1] and (clock_runs_on or count_runs_on):
                chain.append(part)
                break
        else:
            out.append([part])
    out.sort(key=lambda chain: -sum(p.rounds[1] - p.rounds[0] + 1 for p in chain))
    return [[p.raw for p in chain] for chain in out]


def _offsets(parts: list[_Part]) -> None:
    """
    Each part's place on the match clock: seconds from the start of the live
    match. Where the server's clock runs on between parts it is used as it
    is; where it was restarted, the part follows on a second after the last.
    """
    origin = parts[0].first_clock
    parts[0].offset = origin
    for prev, part in zip(parts, parts[1:]):
        if part.first_clock >= prev.last_clock - 5:
            part.offset = origin
        else:
            ended = prev.last_clock - prev.offset
            part.offset = part.first_clock - (ended + 1.0)


def build_match(raws: list[RawPart], name: str) -> Match:
    """One match from its demo parts, in whatever order they come."""
    parts = _in_order([_Part(r) for r in raws])
    if not parts:
        raise ValueError("no demo parts")
    _offsets(parts)
    by_index: dict[int, tuple[Round, _Window]] = {}
    incomplete: set[int] = set()
    for part in parts:
        found, cut = _rounds_in(part, part.offset)
        incomplete.update(cut)
        # A later part's account of a round replaces an earlier one's.
        by_index.update(found)
    rounds = [by_index[i][0] for i in sorted(by_index)]
    windows = [by_index[i][1] for i in sorted(by_index)]
    incomplete -= {r.number for r in rounds}
    map_name = next((p.raw.map for p in parts if p.raw.map), "")
    players = _players(parts)
    teams = _name_teams(rounds, windows, players)
    # The buy waits for the teams: a pistol round is known from where they swap sides.
    half, pistol = _pistol_rounds(rounds, windows)
    for r, w in zip(rounds, windows):
        r.buy = {s: buy_type(v / max(1, w.players.get(s, 1)), r.number in pistol) for s, v in r.equipment.items()}

    frames: list[pd.DataFrame] = []
    other_events: list[dict] = []
    state: list[dict] = []
    deaths: list[pd.DataFrame] = []
    hurts: list[pd.DataFrame] = []
    blinds: list[pd.DataFrame] = []
    for part in parts:
        s = part.raw.samples
        s = s[s["team_num"].isin([2, 3])]
        # Freeze time too: where the players wait and what they buy.
        live = s[_flag(s, "is_alive") & ~_flag(s, "is_warmup_period") & (s["tick"] >= part.live_from)]
        origin = part.offset
        times = part.at(live["tick"].to_numpy()) - origin
        dx, dy, dz = _direction(live["yaw"].to_numpy(), live["pitch"].to_numpy())
        frames.append(
            _frame(
                {
                    "time": times,
                    "event": "position",
                    "player": live["name"].astype(str).to_numpy(),
                    "steamid": live["steamid"].astype(str).to_numpy(),
                    "side": [side_of(v) for v in live["team_num"]],
                    "x": live["X"].to_numpy(dtype=float),
                    "y": live["Y"].to_numpy(dtype=float),
                    "z": live["Z"].to_numpy(dtype=float),
                    "dirX": dx,
                    "dirY": dy,
                    "dirZ": dz,
                    "health": live["health"].to_numpy(dtype=float),
                    "armor": live["armor_value"].to_numpy(dtype=float),
                    "money": live["balance"].to_numpy(dtype=float),
                    "equipment": live["current_equip_value"].to_numpy(dtype=float),
                    "weapon": [held(w) for w in live["active_weapon_name"]],
                    "place": live["last_place_name"].fillna("").astype(str).to_numpy(),
                    **more.sample_columns(live),
                }
            )
        )
        ev = part.raw.events

        def live_ev(df: pd.DataFrame, part: _Part = part) -> pd.DataFrame:
            return df[(df["tick"] >= part.live_from) & ~_flag(df, "is_warmup_period")]
        if "player_death" in ev:
            d = live_ev(ev["player_death"])
            d = d.assign(time=part.at(d["tick"].to_numpy()) - origin)
            deaths.append(d)
        if "player_hurt" in ev:
            h = live_ev(ev["player_hurt"])
            # Where on the body: traced in the part, whose ticks the shots share.
            h = h.assign(**impact.hit_points(h, ev.get("fire_bullets")))
            hurts.append(h.assign(time=part.at(h["tick"].to_numpy()) - origin))
        if "player_blind" in ev:
            b = live_ev(ev["player_blind"])
            blinds.append(b.assign(time=part.at(b["tick"].to_numpy()) - origin))
        if "weapon_fire" in ev:
            f = live_ev(ev["weapon_fire"])
            w = f["weapon"].fillna("").astype(str).str.removeprefix("weapon_")
            # The bomb's "shot" is the start of a plant, which bomb_beginplant has.
            keep = w != "c4"
            f, w = f[keep], w[keep]
            thrown = w.isin(GRENADES).to_numpy()
            slashed = w.str.contains("knife|bayonet").to_numpy()
            frames.append(
                _frame(
                    _event_rows(
                        part,
                        origin,
                        "user",
                        f,
                        "shot",
                        weapon=[weapon_name(v) for v in w],
                        detail=more.fire_details(f, ev.get("fire_bullets")),
                    )
                ).assign(event=np.where(thrown, "throw", np.where(slashed, "slash", "shot")))
            )
        # Every other event about a player, where the player was; the rest for the summary.
        about, rest = more.other_events(ev)
        for event_name, g in about.items():
            g = live_ev(g)
            if not len(g):
                continue
            rows = _event_rows(part, origin, "user", g, "chat" if event_name == "chat_message" else event_name)
            if {"x", "y", "z"} <= set(g.columns):
                rows.update(x=g["x"].to_numpy(dtype=float), y=g["y"].to_numpy(dtype=float), z=g["z"].to_numpy(dtype=float))
            for key in ("weapon", "item"):
                if key in g:
                    rows["weapon"] = [weapon_name(v) for v in g[key]]
                    break
            if event_name == "chat_message":
                rows["text"] = g["chat_message"].fillna("").astype(str).to_numpy()
            if "entityid" in g:
                rows["entity"] = g["entityid"].to_numpy(dtype=float)
            rows["detail"] = more.detail(g)
            frames.append(_frame(rows))
        for event_name, g in rest.items():
            times = part.at(g["tick"].to_numpy()) - origin
            for t, fields in zip(times, more.detail(g)):
                other_events.append({"event": event_name, "time": round(float(t), 3), **(json.loads(fields) if fields else {})})
        for tick, field_name, value in more.state_changes(part.raw.samples):
            state.append({"time": round(float(part.at([tick])[0] - origin), 3), "field": field_name, "value": value})
        g = more.flights(part.raw.grenades, part.every)
        if len(g):
            g = g[g["tick"] >= part.live_from]
            frames.append(
                _frame(
                    {
                        "time": part.at(g["tick"].to_numpy()) - origin,
                        "event": "grenade",
                        "player": g["name"].fillna("").astype(str).to_numpy(),
                        "steamid": g["steamid"].fillna("").astype(str).to_numpy(),
                        "x": g["x"].to_numpy(dtype=float),
                        "y": g["y"].to_numpy(dtype=float),
                        "z": g["z"].to_numpy(dtype=float),
                        "weapon": [more.PROJECTILES[c] for c in g["grenade_type"]],
                        "entity": g["grenade_entity_id"].to_numpy(dtype=float),
                    }
                )
            )
        for event_name, kind in DETONATIONS.items():
            if event_name not in ev:
                continue
            g = live_ev(ev[event_name])
            if not len(g):
                continue
            rows = _event_rows(part, origin, "user", g, kind)
            rows.update(x=g["x"].to_numpy(dtype=float), y=g["y"].to_numpy(dtype=float), z=g["z"].to_numpy(dtype=float))
            # The event names no place where the grenade went off, only the
            # thrower's at that moment: kept, under its own name.
            rows["throwerPlace"] = rows.pop("place")
            rows["weapon"] = {"smoke": "Smoke Grenade", "flash": "Flashbang", "he": "High Explosive Grenade", "molotov": "Molotov", "decoy": "Decoy Grenade"}[kind]
            if "entityid" in g:
                rows["entity"] = g["entityid"].to_numpy(dtype=float)
            frames.append(_frame(rows))
        for event_name, kind in (("bomb_planted", "plant"), ("bomb_defused", "defuse")):
            if event_name in ev and len(ev[event_name]):
                b = live_ev(ev[event_name])
                frames.append(_frame(_event_rows(part, origin, "user", b, kind, weapon="C4 Explosive")))

    kills = _kills(pd.concat(deaths, ignore_index=True) if deaths else pd.DataFrame(), rounds)
    damage = _damage(pd.concat(hurts, ignore_index=True) if hurts else pd.DataFrame(), rounds)
    flashed = _blinds(pd.concat(blinds, ignore_index=True) if blinds else pd.DataFrame(), rounds)
    frames.extend(_kill_rows(kills))
    # Every hit and every flash, teammates' and the world's too (the statistics count enemies only).
    all_hurts = pd.concat(hurts, ignore_index=True).sort_values("time").reset_index(drop=True) if hurts else pd.DataFrame()
    if len(all_hurts):
        which, _ = _assign(all_hurts["time"].to_numpy(dtype=float), rounds)
        frames.append(
            _frame(
                {
                    "time": all_hurts["time"].to_numpy(dtype=float),
                    "event": "hurt",
                    "player": all_hurts["user_name"].fillna("").astype(str).to_numpy(),
                    "steamid": all_hurts["user_steamid"].fillna("").astype(str).to_numpy(),
                    "side": [side_of(v) for v in all_hurts["user_team_num"]],
                    "x": all_hurts["user_X"].to_numpy(dtype=float),
                    "y": all_hurts["user_Y"].to_numpy(dtype=float),
                    "z": all_hurts["user_Z"].to_numpy(dtype=float),
                    "place": all_hurts["user_last_place_name"].fillna("").astype(str).to_numpy(),
                    # Which way the victim looked at the hit, and where the shooter stood and on which side: the
                    # shot's angle against the victim's facing and its distance, worked out by the viewer.
                    **dict(zip(("dirX", "dirY", "dirZ"), _direction(_numbers(all_hurts, "user_yaw"), _numbers(all_hurts, "user_pitch")))),
                    "attackerX": _numbers(all_hurts, "attacker_X"),
                    "attackerY": _numbers(all_hurts, "attacker_Y"),
                    "attackerZ": _numbers(all_hurts, "attacker_Z"),
                    "attackerSide": [side_of(v) for v in all_hurts["attacker_team_num"]] if "attacker_team_num" in all_hurts else "",
                    "other": all_hurts["attacker_name"].fillna("").astype(str).to_numpy(),
                    "damage": more.health_lost(all_hurts, which),
                    "health": all_hurts["health"].to_numpy(dtype=float),
                    "armor": _numbers(all_hurts, "armor"),
                    "armorDamage": _numbers(all_hurts, "dmg_armor"),
                    "hitgroup": _texts(all_hurts, "hitgroup"),
                    **{c: _numbers(all_hurts, c) for c in impact.COLUMNS},
                    "hitFrom": _texts(all_hurts, "hitFrom"),
                    "weapon": [weapon_name(w) for w in all_hurts["weapon"]],
                    "detail": more.detail(all_hurts),
                }
            )
        )
    all_blinds = pd.concat(blinds, ignore_index=True) if blinds else pd.DataFrame()
    if len(all_blinds):
        frames.append(
            _frame(
                {
                    "time": all_blinds["time"].to_numpy(dtype=float),
                    "event": "blind",
                    "player": all_blinds["user_name"].fillna("").astype(str).to_numpy(),
                    "steamid": all_blinds["user_steamid"].fillna("").astype(str).to_numpy(),
                    "side": [side_of(v) for v in all_blinds["user_team_num"]],
                    "x": all_blinds["user_X"].to_numpy(dtype=float),
                    "y": all_blinds["user_Y"].to_numpy(dtype=float),
                    "z": all_blinds["user_Z"].to_numpy(dtype=float),
                    "place": all_blinds["user_last_place_name"].fillna("").astype(str).to_numpy(),
                    "other": all_blinds["attacker_name"].fillna("").astype(str).to_numpy(),
                    "duration": all_blinds["blind_duration"].fillna(0).to_numpy(dtype=float),
                    "weapon": "Flashbang",
                    "entity": _numbers(all_blinds, "entityid"),
                }
            )
        )
    # The bomb going off, where it was planted: when the demo says it did,
    # else when a round won by the bomb was decided. It is the planting team's.
    for r in rounds:
        if r.plant and (r.exploded is not None or r.reason == "bomb"):
            frames.append(
                _frame(
                    {
                        "time": [r.exploded if r.exploded is not None else r.end],
                        "event": "explode",
                        "player": [r.plant["player"]],
                        "steamid": [r.plant["steamid"]],
                        "side": ["T"],
                        "team": [next((t for t, s in r.sides.items() if s == "T"), "")],
                        "x": [r.plant["x"]],
                        "y": [r.plant["y"]],
                        "z": [r.plant["z"]],
                        "place": [r.plant["place"]],
                        "weapon": ["C4 Explosive"],
                    }
                )
            )
    filled = [f for f in frames if len(f)]
    rows = pd.concat(filled, ignore_index=True) if filled else _frame({})
    # Events name the player; the team is the player's.
    team_of = {pid: info["team"] for pid, info in players.items()}
    rows = pd.concat([rows, _round_ends(rows, rounds)], ignore_index=True)
    missing = rows["team"].fillna("") == ""
    rows.loc[missing, "team"] = rows.loc[missing, "steamid"].map(team_of).fillna("")
    winner, winner_source = _match_winner(rounds, half, any("cs_win_panel_match" in p.raw.events for p in parts))
    rows = _states(_label(rows, rounds, name, map_name, winner))
    first = parts[0].raw
    return Match(
        name=name,
        map=map_name,
        parts=[p.raw.path for p in parts],
        rounds=rounds,
        players=players,
        teams=teams,
        rows=rows,
        kills=kills,
        damage=damage,
        blinds=flashed,
        incomplete=sorted(incomplete),
        half=half,
        pistol=pistol,
        events=sorted(other_events, key=lambda e: e["time"]),
        state=state,
        winner=winner,
        winner_source=winner_source,
        profiles={k: v for p in parts for k, v in more.profiles(p.raw.samples).items()},
        header=dict(first.header),
        player_info=[r for p in parts for r in more.table_records(p.raw.player_info)],
        skins=[r for p in parts for r in more.table_records(p.raw.skins)],
        item_drops=[r for p in parts for r in more.table_records(p.raw.item_drops)],
        sources=[
            (p.raw, float(p.clock[0]) if len(p.ticks) else 0.0, float(p.ticks[0]) if len(p.ticks) else 0.0, p.offset)
            for p in parts
        ],
    )


def _round_ends(rows: pd.DataFrame, rounds: list[Round]) -> pd.DataFrame:
    """
    A `round_end` row for every player who played a decided round, where they
    last stood: whether their side won, how (`detail`), and what the round paid
    them (`earn_round_cs2`): the win reward, or the loss bonus plus the
    planting side's bonus after a plant; nothing for a T alive when the time
    ran out. The amount is what the side's players' money rose by from their
    last sample in the round to the next freeze time (the most common rise of
    those below the cap), where that is one the rules can pay; else the rules'
    own: the loss bonus by the side's losing streak (one at each half's start,
    a win shortens it by one). Plants and defuses get their own 300.
    """
    events = rows["event"].to_numpy()
    pos = rows[events == "position"]
    deaths = rows[events == "death"]
    rows.loc[np.isin(events, ["plant", "defuse"]), "earn_round_cs2"] = OBJECTIVE_REWARD
    out = []
    streak = {"T": 1, "CT": 1}
    previous_sides: dict[str, str] = {}
    pos_t = pos["time"].to_numpy(dtype=float)
    for k, r in enumerate(rounds):
        if r.sides != previous_sides:
            # A new half (the sides swapped, or the match began): the streaks start again.
            streak = {"T": 1, "CT": 1}
            previous_sides = dict(r.sides)
        if r.winner not in ("T", "CT") or r.reason not in WIN_REWARD:
            continue
        loser = "CT" if r.winner == "T" else "T"
        loss = LOSS_BONUS[min(streak[loser], len(LOSS_BONUS) - 1)]
        streak[loser] += 1
        streak[r.winner] = max(streak[r.winner] - 1, 0)
        here = pos[(pos["time"] >= r.start) & (pos["time"] <= r.end) & (pos["side"] != "")]
        if not len(here):
            continue
        last = here.sort_values("time", kind="stable").groupby("steamid", sort=False).tail(1)
        dead = set(deaths.loc[(deaths["time"] >= r.start) & (deaths["time"] <= r.end), "steamid"])
        bonus = PLANT_BONUS if loser == "T" and r.plant else 0
        paid = {r.winner: WIN_REWARD[r.reason], loser: loss + bonus}
        if k + 1 < len(rounds):
            nxt = pos[(pos_t >= r.until) & (pos_t < rounds[k + 1].start)].groupby("steamid")["money"].first()
            for side in ("T", "CT"):
                rise = [nxt[sid] - m for sid, sd, m in zip(last["steamid"], last["side"], last["money"])
                        if sd == side and sid in nxt.index and nxt[sid] < MONEY_CAP
                        and not (side == "T" and r.reason == "time" and sid not in dead)]
                if rise:
                    common = Counter(rise).most_common(1)[0][0]
                    allowed = {WIN_REWARD[r.reason]} if side == r.winner else {b + bonus for b in LOSS_BONUS}
                    if common in allowed:
                        paid[side] = int(common)
        loss = paid[loser] - bonus
        if loss in LOSS_BONUS:
            # The streak as the game counts it, for the rounds the money cannot tell.
            streak[loser] = LOSS_BONUS.index(loss) + 1
        reward = []
        for sid, side in zip(last["steamid"], last["side"]):
            if side == "T" and side == loser and r.reason == "time" and sid not in dead:
                reward.append(0)
            else:
                reward.append(paid[side])
        detail = {side: json.dumps({"winner": r.winner, "reason": r.reason, "lossBonus": loss if side == loser else 0,
                                    "plant": bool(r.plant)}) for side in ("T", "CT")}
        out.append(_frame({
            "time": np.full(len(last), r.end),
            "event": "round_end",
            "player": last["player"].to_numpy(),
            "steamid": last["steamid"].to_numpy(),
            "side": last["side"].to_numpy(),
            "x": last["x"].to_numpy(dtype=float),
            "y": last["y"].to_numpy(dtype=float),
            "z": last["z"].to_numpy(dtype=float),
            "place": last["place"].to_numpy(),
            "detail": [detail[x] for x in last["side"]],
            "earn_round_cs2": np.asarray(reward, dtype=float),
        }))
    return pd.concat(out, ignore_index=True) if out else _frame({})


def _states(rows: pd.DataFrame) -> pd.DataFrame:
    """
    Every row of a player's carries their state at the time, as their last
    position sample up to it had it: helmet, defuser, armour, scoped, utility
    count, the weapon in hand (`state_*`), and flashed from the blinds that
    hit them. Events also get the inventory, money and equipment value where
    they have none of their own.
    """
    rows = rows.reset_index(drop=True)
    n = len(rows)
    sid = rows["steamid"].fillna("").astype(str).to_numpy()
    t = rows["time"].to_numpy(dtype=float)
    ev = rows["event"].to_numpy()
    dur = rows["duration"].to_numpy(dtype=float)
    src = np.full(n, -1, dtype=np.int64)
    flashed = np.zeros(n)
    for player, idx in pd.Series(np.arange(n)).groupby(sid).groups.items():
        if not player:
            continue
        idx = np.sort(np.asarray(idx))
        p = idx[ev[idx] == "position"]
        if len(p):
            k = np.searchsorted(t[p], t[idx], side="right") - 1
            src[idx[k >= 0]] = p[k[k >= 0]]
        for start, length in zip(t[idx][ev[idx] == "blind"], dur[idx][ev[idx] == "blind"]):
            if length > 0:
                flashed[idx[(t[idx] >= start) & (t[idx] < start + length)]] = 1
    has = src >= 0
    pick = np.where(has, src, 0)

    def taken(column: str) -> np.ndarray:
        return np.where(has, rows[column].to_numpy(dtype=float)[pick], np.nan)

    rows["state_helmet"] = taken("helmet")
    rows["state_defuser"] = taken("defuser")
    rows["state_kevlar"] = np.where(has, (taken("armor") > 0).astype(float), np.nan)
    rows["state_scoped"] = taken("scoped")
    rows["state_flashed"] = np.where(sid != "", flashed, np.nan)
    inventory = rows["inventory"].fillna("").astype(str).to_numpy()
    held = inventory[pick]
    count = np.array([sum(1 for x in h.split("|") if x and UTILITY.search(x)) for h in held], dtype=float)
    rows["state_utility"] = np.where(has, count, np.nan)
    rows["state_weapon"] = np.where(has, rows["weapon"].fillna("").astype(str).to_numpy()[pick], "")
    rows["inventory"] = np.where((inventory == "") & has, held, inventory)
    for column in ("money", "equipment"):
        v = rows[column].to_numpy(dtype=float)
        rows[column] = np.where(np.isnan(v) & has, taken(column), v)
    return rows


def _numbers(df: pd.DataFrame, column: str) -> np.ndarray:
    return df[column].to_numpy(dtype=float) if column in df else np.full(len(df), np.nan)


def _texts(df: pd.DataFrame, column: str) -> np.ndarray:
    return df[column].fillna("").astype(str).to_numpy() if column in df else np.full(len(df), "", dtype=object)


def _match_winner(rounds: list[Round], half: int | None, win_panel: bool) -> tuple[str, str | None]:
    """
    The team that won the match, where the recording shows the end: the game's
    match win panel (`cs_win_panel_match`), a surrender, or a regulation win -
    more than half of the regulation rounds, which the other team can no
    longer reach. Then the team with the most rounds after the last one. A
    recording that stops before the end, an overtime without the panel, or a
    tie leaves it empty.
    """
    if not rounds:
        return "", None
    score = rounds[-1].score
    if len(score) != 2:
        return "", None
    (a, sa), (b, sb) = sorted(score.items(), key=lambda kv: -kv[1])
    if sa == sb:
        return "", None
    if win_panel:
        return a, "winPanel"
    if rounds[-1].reason == "surrender":
        return a, "surrender"
    if half is not None and sa > half and sa + sb <= 2 * half:
        return a, "regulation"
    return "", None


def _label(rows: pd.DataFrame, rounds: list[Round], name: str, map_name: str, winner: str = "") -> pd.DataFrame:
    """
    Round, phase, round time, won, the match's outcome and the round's end
    reason, and buy for every row; rows outside a round and its freeze time
    are dropped.
    """
    which, phase = _assign_phases(rows["time"].to_numpy(dtype=float), rounds)
    keep = which >= 0
    rows = rows[keep].copy()
    which, phase = which[keep], phase[keep]
    numbers = np.array([r.number for r in rounds])
    starts = np.array([r.start for r in rounds])
    winners = np.array([r.winner for r in rounds])
    rows["match"] = name
    rows["map"] = map_name
    rows["round"] = numbers[which]
    rows["roundId"] = [f"{name} #{n:02d}" for n in numbers[which]]
    rows["phase"] = phase
    rows["roundTime"] = rows["time"].to_numpy(dtype=float) - starts[which]
    sides = rows["side"].to_numpy()
    rows["won"] = np.where(sides == "", np.nan, (winners[which] == sides).astype(float))
    reasons = np.array([r.reason for r in rounds], dtype=object)
    rows["roundEndReason"] = reasons[which]
    teams = rows["team"].fillna("").astype(str).to_numpy()
    rows["matchWon"] = np.where((teams == "") | (winner == ""), np.nan, (teams == winner).astype(float))
    rows["buy"] = [rounds[k].buy.get(s, "") for k, s in zip(which, sides)]
    return rows.sort_values(["time", "event"], kind="stable").reset_index(drop=True)


# ---------------------------------------------------------------- kills


def _kills(deaths: pd.DataFrame, rounds: list[Round]) -> pd.DataFrame:
    """One row per death: who killed whom where, opening, traded, trade kill, assist."""
    columns = [
        "round", "time", "roundTime", "phase", "attacker", "attackerId", "attackerSide", "victim", "victimId",
        "victimSide", "assister", "assisterId", "flashAssist", "weapon", "headshot", "teamkill", "suicide", "wallbang",
        "throughSmoke", "noscope", "attackerBlind", "opening", "traded", "trade",
        "ax", "ay", "az", "aplace", "vx", "vy", "vz", "vplace",
        "penetrated", "distance", "hitgroup", "detail",
    ]
    if not len(deaths):
        return pd.DataFrame(columns=columns)
    d = deaths.sort_values("time").reset_index(drop=True)
    which, after = _assign(d["time"].to_numpy(dtype=float), rounds)
    d = d[which >= 0].reset_index(drop=True)
    after = after[which >= 0]
    which = which[which >= 0]
    out = pd.DataFrame(
        {
            "round": [rounds[k].number for k in which],
            "time": d["time"].to_numpy(dtype=float),
            "roundTime": d["time"].to_numpy(dtype=float) - np.array([rounds[k].start for k in which]),
            "phase": np.where(after, "after", "live"),
            "attacker": d["attacker_name"].fillna("").astype(str),
            "attackerId": d["attacker_steamid"].fillna("").astype(str),
            "attackerSide": [side_of(v) for v in d["attacker_team_num"]],
            "victim": d["user_name"].fillna("").astype(str),
            "victimId": d["user_steamid"].fillna("").astype(str),
            "victimSide": [side_of(v) for v in d["user_team_num"]],
            "assister": d.get("assister_name", pd.Series([""] * len(d))).fillna("").astype(str),
            "assisterId": d.get("assister_steamid", pd.Series([""] * len(d))).fillna("").astype(str),
            "flashAssist": d.get("assistedflash", pd.Series([False] * len(d))).fillna(False).astype(bool),
            "weapon": [weapon_name(w) for w in d["weapon"]],
            "headshot": d.get("headshot", pd.Series([False] * len(d))).fillna(False).astype(bool),
            "wallbang": d.get("penetrated", pd.Series([0] * len(d))).fillna(0).astype(int) > 0,
            "throughSmoke": d.get("thrusmoke", pd.Series([False] * len(d))).fillna(False).astype(bool),
            "noscope": d.get("noscope", pd.Series([False] * len(d))).fillna(False).astype(bool),
            "attackerBlind": d.get("attackerblind", pd.Series([False] * len(d))).fillna(False).astype(bool),
            "ax": d["attacker_X"].to_numpy(dtype=float),
            "ay": d["attacker_Y"].to_numpy(dtype=float),
            "az": d["attacker_Z"].to_numpy(dtype=float),
            "aplace": d["attacker_last_place_name"].fillna("").astype(str),
            "vx": d["user_X"].to_numpy(dtype=float),
            "vy": d["user_Y"].to_numpy(dtype=float),
            "vz": d["user_Z"].to_numpy(dtype=float),
            "vplace": d["user_last_place_name"].fillna("").astype(str),
            "penetrated": _numbers(d, "penetrated"),
            "distance": _numbers(d, "distance"),
            "hitgroup": _texts(d, "hitgroup"),
            # Everything else the game says of the death: dominated, revenge, in the air, a wipe...
            "detail": more.detail(d),
        }
    )
    # A suicide - an own grenade, say - is no teamkill.
    out["suicide"] = (out["attackerId"] != "") & (out["attackerId"] == out["victimId"])
    out["teamkill"] = (out["attackerSide"] == out["victimSide"]) & (out["attackerId"] != "") & ~out["suicide"]
    enemy = _enemy(out)
    # Opening: the first kill of an enemy in each round, while it was live.
    out["opening"] = False
    live = out[(out["phase"] == "live") & enemy]
    out.loc[live.groupby("round").head(1).index, "opening"] = True
    # Traded: the killer killed by a teammate of the victim within TRADE_SECONDS.
    out["traded"] = False
    out["trade"] = False
    for i in out.index[enemy]:
        r, t, killer, side = out.at[i, "round"], out.at[i, "time"], out.at[i, "attackerId"], out.at[i, "victimSide"]
        later = out[
            (out["round"] == r)
            & (out["time"] > t)
            & (out["time"] <= t + TRADE_SECONDS)
            & (out["victimId"] == killer)
            & (out["attackerSide"] == side)
        ]
        if len(later):
            out.at[i, "traded"] = True
            out.at[later.index[0], "trade"] = True
    return out[columns]


def _enemy(kills: pd.DataFrame) -> pd.Series:
    """The deaths that are an enemy's kill: not the world's, not a teamkill, not a suicide."""
    return (kills["attackerId"] != "") & ~kills["teamkill"] & ~kills["suicide"]


def _kill_rows(kills: pd.DataFrame) -> list[pd.DataFrame]:
    """A kill at the killer's position and a death at the victim's, for the heatmap."""
    if not len(kills):
        return []
    enemy = kills[_enemy(kills)]
    kill = _frame(
        {
            "time": enemy["time"].to_numpy(),
            "event": "kill",
            "player": enemy["attacker"].to_numpy(),
            "steamid": enemy["attackerId"].to_numpy(),
            "side": enemy["attackerSide"].to_numpy(),
            "x": enemy["ax"].to_numpy(),
            "y": enemy["ay"].to_numpy(),
            "z": enemy["az"].to_numpy(),
            "place": enemy["aplace"].to_numpy(),
            "other": enemy["victim"].to_numpy(),
            "weapon": enemy["weapon"].to_numpy(),
            "headshot": enemy["headshot"].astype(float).to_numpy(),
            "opening": enemy["opening"].astype(float).to_numpy(),
            "traded": enemy["trade"].astype(float).to_numpy(),
            "noscope": enemy["noscope"].astype(float).to_numpy(),
            "attackerBlind": enemy["attackerBlind"].astype(float).to_numpy(),
            **_death_extra(enemy),
        }
    )
    death = _frame(
        {
            "time": kills["time"].to_numpy(),
            "event": "death",
            "player": kills["victim"].to_numpy(),
            "steamid": kills["victimId"].to_numpy(),
            "side": kills["victimSide"].to_numpy(),
            "x": kills["vx"].to_numpy(),
            "y": kills["vy"].to_numpy(),
            "z": kills["vz"].to_numpy(),
            "place": kills["vplace"].to_numpy(),
            "other": kills["attacker"].to_numpy(),
            "weapon": kills["weapon"].to_numpy(),
            "headshot": kills["headshot"].astype(float).to_numpy(),
            "opening": kills["opening"].astype(float).to_numpy(),
            "traded": kills["traded"].astype(float).to_numpy(),
            "noscope": kills["noscope"].astype(float).to_numpy(),
            "attackerBlind": kills["attackerBlind"].astype(float).to_numpy(),
            **_death_extra(kills),
        }
    )
    return [kill, death]


def _death_extra(k: pd.DataFrame) -> dict:
    """What else a kill or death row carries: through walls, through smoke, how far, where hit, who assisted."""
    return {
        "penetrated": k["penetrated"].to_numpy(dtype=float),
        "throughSmoke": k["throughSmoke"].astype(float).to_numpy(),
        "distance": k["distance"].to_numpy(dtype=float),
        "hitgroup": k["hitgroup"].to_numpy(),
        "assister": k["assister"].to_numpy(),
        "detail": k["detail"].to_numpy(),
    }


def _damage(hurts: pd.DataFrame, rounds: list[Round]) -> pd.DataFrame:
    """Damage between enemies, as health actually lost."""
    columns = ["round", "time", "attacker", "attackerId", "attackerSide", "victim", "victimId", "victimSide", "weapon", "damage", "utility", "x", "y", "z", "place"]
    if not len(hurts):
        return pd.DataFrame(columns=columns)
    h = hurts.sort_values("time").reset_index(drop=True)
    which, _ = _assign(h["time"].to_numpy(dtype=float), rounds)
    h = h[which >= 0].reset_index(drop=True)
    which = which[which >= 0]
    remaining: dict[tuple[int, str], float] = {}
    lost = np.zeros(len(h))
    for i, (k, victim, dmg, after) in enumerate(zip(which, h["user_steamid"].astype(str), h["dmg_health"].fillna(0), h["health"].fillna(0))):
        key = (int(k), victim)
        before = remaining.get(key, 100.0)
        lost[i] = min(float(dmg), before)
        remaining[key] = float(after)
    raw_weapon = h["weapon"].fillna("").astype(str)
    out = pd.DataFrame(
        {
            "round": [rounds[k].number for k in which],
            "time": h["time"].to_numpy(dtype=float),
            "attacker": h["attacker_name"].fillna("").astype(str),
            "attackerId": h["attacker_steamid"].fillna("").astype(str),
            "attackerSide": [side_of(v) for v in h["attacker_team_num"]],
            "victim": h["user_name"].fillna("").astype(str),
            "victimId": h["user_steamid"].fillna("").astype(str),
            "victimSide": [side_of(v) for v in h["user_team_num"]],
            "weapon": [weapon_name(w) for w in raw_weapon],
            "damage": lost,
            "utility": raw_weapon.isin(UTILITY_DAMAGE).to_numpy(),
            "x": h["user_X"].to_numpy(dtype=float),
            "y": h["user_Y"].to_numpy(dtype=float),
            "z": h["user_Z"].to_numpy(dtype=float),
            "place": h["user_last_place_name"].fillna("").astype(str),
        }
    )
    enemy = out["attackerSide"].isin(SIDES) & out["victimSide"].isin(SIDES) & (out["attackerSide"] != out["victimSide"])
    return out[enemy].reset_index(drop=True)[columns]


def _blinds(blinds: pd.DataFrame, rounds: list[Round]) -> pd.DataFrame:
    """Enemies blinded by a flash."""
    columns = ["round", "time", "attacker", "attackerId", "victim", "victimId", "victimSide", "duration", "x", "y", "z", "place"]
    if not len(blinds):
        return pd.DataFrame(columns=columns)
    b = blinds.sort_values("time").reset_index(drop=True)
    which, _ = _assign(b["time"].to_numpy(dtype=float), rounds)
    b = b[which >= 0].reset_index(drop=True)
    which = which[which >= 0]
    out = pd.DataFrame(
        {
            "round": [rounds[k].number for k in which],
            "time": b["time"].to_numpy(dtype=float),
            "attacker": b["attacker_name"].fillna("").astype(str),
            "attackerId": b["attacker_steamid"].fillna("").astype(str),
            "attackerSide": [side_of(v) for v in b["attacker_team_num"]],
            "victim": b["user_name"].fillna("").astype(str),
            "victimId": b["user_steamid"].fillna("").astype(str),
            "victimSide": [side_of(v) for v in b["user_team_num"]],
            "duration": b["blind_duration"].fillna(0).to_numpy(dtype=float),
            "x": b["user_X"].to_numpy(dtype=float),
            "y": b["user_Y"].to_numpy(dtype=float),
            "z": b["user_Z"].to_numpy(dtype=float),
            "place": b["user_last_place_name"].fillna("").astype(str),
        }
    )
    # Enemies only: not teammates, and not the coach or a caster watching.
    enemy = out["attackerSide"].isin(SIDES) & out["victimSide"].isin(SIDES) & (out["attackerSide"] != out["victimSide"])
    return out[enemy].reset_index(drop=True)[columns]
