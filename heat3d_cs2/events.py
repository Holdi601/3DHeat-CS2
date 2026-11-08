"""
Everything else a demo holds, beside what the match is built from: the rest
of each sampled player's state, every hit and flash (teammates' too), every
other game event, every grenade's flight, the game's state as it changed, and
what stays the same for a player through a match.

`match.build_match` calls these per demo part; nothing here decides a round.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd

from .demo import PROFILE_FIELDS, SAMPLE_FIELDS, STATE_FIELDS

#: Events the match is built from, or read into rows of their own by `match` - not read again here.
HANDLED = {
    "player_death",
    "player_hurt",
    "player_blind",
    "weapon_fire",
    "fire_bullets",
    "smokegrenade_detonate",
    "flashbang_detonate",
    "hegrenade_detonate",
    "inferno_startburn",
    "decoy_detonate",
    "bomb_planted",
    "bomb_defused",
}

#: An event's fields that are not its own: the parser's additions.
_NOT_OWN = {"tick", "total_rounds_played", "is_warmup_period"}

#: A grenade in flight, by the game's class -> the name the game shows.
PROJECTILES = {
    "CSmokeGrenadeProjectile": "Smoke Grenade",
    "CFlashbangProjectile": "Flashbang",
    "CHEGrenadeProjectile": "High Explosive Grenade",
    "CMolotovProjectile": "Molotov",
    "CDecoyProjectile": "Decoy Grenade",
}

#: The sampled players' extra columns that are text, not numbers.
TEXT_SAMPLES = {"spottedBy", "inventory"}

#: The extra columns the rows gain here, besides the sampled players' (SAMPLE_COLUMNS).
EXTRA_TEXT = ["detail", "hitgroup", "assister", "text", "hitFrom"]
EXTRA_NUMERIC = ["entity", "armorDamage", "penetrated", "throughSmoke", "distance", "punchPitch", "punchYaw",
                 "hitLocalX", "hitLocalY", "hitLocalZ", "hitDirX", "hitDirY", "hitDirZ", "hitMiss"]
SAMPLE_COLUMNS = [c for c in SAMPLE_FIELDS.values() if c != "aimPunch"]


def plain(v: object) -> object:
    """A parser value as JSON: numpy scalars as numbers, NaN as null, lists as lists."""
    if isinstance(v, (list, tuple, np.ndarray)):
        return [plain(x) for x in v]
    if isinstance(v, (np.integer, int)) and not isinstance(v, (bool, np.bool_)):
        # A steamid does not fit a JSON reader's number (53 bits): as text, as the table has it.
        return int(v) if abs(int(v)) < 2**53 else str(int(v))
    if isinstance(v, (np.floating, float)):
        return None if not math.isfinite(float(v)) else float(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return v if isinstance(v, (int, str)) else str(v)


def detail(df: pd.DataFrame, skip: set[str] = frozenset()) -> list[str]:
    """Each row's own fields - all but the players' and the parser's - as a JSON object."""
    own = [c for c in df.columns if c not in _NOT_OWN and c not in skip and not c.startswith(("user_", "attacker_", "assister_"))]
    if not own:
        return [""] * len(df)
    records = df[own].to_dict("records")
    return [json.dumps({k: plain(v) for k, v in r.items()}, ensure_ascii=False, separators=(",", ":")) for r in records]


def sample_columns(live: pd.DataFrame) -> dict[str, object]:
    """The sampled players' extra state, as row columns: flags 0/1, lists as text."""
    out: dict[str, object] = {}
    for field, column in SAMPLE_FIELDS.items():
        if field not in live:
            continue
        col = live[field]
        if column == "aimPunch":
            punch = [v if isinstance(v, (list, np.ndarray)) and len(v) >= 2 else (np.nan, np.nan) for v in col]
            out["punchPitch"] = np.array([float(p[0]) for p in punch])
            out["punchYaw"] = np.array([float(p[1]) for p in punch])
        elif column in TEXT_SAMPLES:
            out[column] = ["|".join(str(x) for x in v) if isinstance(v, (list, np.ndarray)) else "" for v in col]
        else:
            out[column] = pd.to_numeric(col, errors="coerce").astype(float).to_numpy()
    return out


def health_lost(hurts: pd.DataFrame, which: np.ndarray) -> np.ndarray:
    """What each hit really took: no more than the victim had left in that round (100 at its start)."""
    remaining: dict[tuple[int, str], float] = {}
    lost = np.zeros(len(hurts))
    for i, (k, victim, dmg, after) in enumerate(
        zip(which, hurts["user_steamid"].astype(str), hurts["dmg_health"].fillna(0), hurts["health"].fillna(0))
    ):
        key = (int(k), victim)
        lost[i] = min(float(dmg), remaining.get(key, 100.0))
        remaining[key] = float(after)
    return lost


def fire_details(fire: pd.DataFrame, bullets: pd.DataFrame | None) -> list[str]:
    """
    For each shot (weapon_fire), the game's own account of the bullets
    (fire_bullets: where from, the angles, inaccuracy, spread, recoil, the
    seed), matched on the tick and the shooter.
    """
    if bullets is None or not len(bullets) or not len(fire):
        return [""] * len(fire)
    texts = detail(bullets, skip={"player"})
    by_key = {}
    for (tick, sid), text in zip(zip(bullets["tick"], bullets["user_steamid"].astype(str)), texts):
        by_key.setdefault((int(tick), sid), text)
    return [by_key.get((int(t), s), "") for t, s in zip(fire["tick"], fire["user_steamid"].astype(str))]


def other_events(events: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """The events not read elsewhere: those about a player (with a place), and the rest."""
    about, rest = {}, {}
    for name, df in events.items():
        if name in HANDLED or df is None or not len(df):
            continue
        (about if "user_X" in df and df["user_X"].notna().any() else rest)[name] = df
    return about, rest


def flights(grenades: pd.DataFrame | None, every: int) -> pd.DataFrame:
    """
    Every grenade in flight, as the parser has it each tick, kept at the
    players' sampling (every `every` ticks) and at its last tick. The held
    grenades (the weapon in a hand) have no place and are left out.
    """
    if grenades is None or not len(grenades):
        return pd.DataFrame()
    g = grenades[grenades["grenade_type"].isin(PROJECTILES) & grenades["x"].notna()]
    if not len(g):
        return g
    g = g.sort_values(["grenade_entity_id", "tick"])
    last = ~g["grenade_entity_id"].duplicated(keep="last")
    return g[(g["tick"] % every == 0) | last]


def state_changes(samples: pd.DataFrame) -> list[tuple[int, str, object]]:
    """The game's state (timeouts, the bomb, players alive, streaks, phase) where it changed: tick, field, value."""
    have = [c for c in STATE_FIELDS if c in samples]
    if not have:
        return []
    s = samples.drop_duplicates("tick").sort_values("tick")
    out = []
    for c in have:
        values = s[c].to_numpy()
        prev = object()
        for tick, v in zip(s["tick"].to_numpy(), values):
            v = plain(v)
            if v != prev:
                out.append((int(tick), c, v))
                prev = v
    return out


def profiles(samples: pd.DataFrame) -> dict[str, dict]:
    """What stays the same for a player through a match: crosshair, music kit, rank, colour - the last seen."""
    have = [c for c in PROFILE_FIELDS if c in samples]
    if not have:
        return {}
    last = samples.dropna(subset=["steamid"]).drop_duplicates("steamid", keep="last")
    return {str(r["steamid"]): {c: plain(r[c]) for c in have} for _, r in last.iterrows()}


def table_records(df: pd.DataFrame | None) -> list[dict]:
    """A parser table (players, skins, drops) as JSON records."""
    if df is None or not len(df):
        return []
    return [{k: plain(v) for k, v in r.items()} for r in df.to_dict("records")]
