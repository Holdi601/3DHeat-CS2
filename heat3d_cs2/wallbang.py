"""
Whether a hit went through a wall: the damage it dealt, and the shot traced
through the map.

The game says so only for kills (`penetrated` on the death). For every other
hit two things tell:

- The damage. A gun's damage is exact: its base damage, less its range
  falloff over the distance flown, times the part struck, through the armour
  worn (and a third for a team-mate). Anything a bullet passes on its way -
  a wall, a door, a crate, a player - costs it at least a twentieth of its
  damage and a few points more; so a hit that dealt less than that much under
  the weapon's full damage went through something, and one that dealt its
  full damage did not. On 25,649 kills of 176 demos this agrees with the
  game's own count on every shot but the railings below.
- The trace: a segment from where the bullet left the shooter (the game's own
  account of the shot, `fire_bullets`, with the weapon's spread drawn from the
  shot's seed - impact.py) to the point struck on the victim, through the
  map's collision mesh as `map` exports it (mapexport.py) - the same level the
  viewer draws. It says what was passed: the walls' surfaces and thickness.

Railings (surface `metalrailing`) are the one thing bullets pass at no cost
that the game still counts as passed; they are seen by the trace only. What
bullets pass through untouched (the map's `passbullets` groups: chain-link
fences, grates; foliage) is counted on its own, as grates, not as walls; so
is a wall's edge grazed (thinner than MIN_WALL along the line). Clip brushes
and the sky are not in the level at all. The mesh is binned in a uniform grid
of 2 m cells; a segment walks the cells it crosses (Amanatides and Woo) and is
tested against their triangles (Moller and Trumbore). A solid is entered where
the segment crosses a face from its front and left where it crosses one from
its back, so overlapping pieces of one wall are one wall and its thickness is
how far the segment ran inside.

Per hurt row:

- `wallbang`: 1 where the bullet went through something on its way, 0 where
  not. From the damage where the weapon is known and the hit is a place on
  the body; else from the trace (1 where it crossed a solid or a railing),
  NaN where it was not traced (no level, no place on the body: grenades,
  fire, falls; no shot origin) or the line cannot be the bullet's: more solid
  than a bullet passes (MAX_SOLID, or solid metal) yet it hit.
- `wallCount`: the solids passed (and railings). Where the damage says the
  bullet went through something the trace does not see (a door, a prop, a
  player), NaN.
- `wallThickness`: metres of solid passed, all together (NaN as above).
- `wallSurfaces`: their surfaces in order from the shooter, `;`-joined.
- `wallGrates`: bullet-passing surfaces crossed.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from . import glb
from .mapexport import surface_name

#: Game units to metres.
METRES = 0.0254
#: The grid's cell: 2 m in game units.
CELL = 2.0 / METRES
#: The ends of the segment left untraced (game units): the muzzle side against a corner the shooter peeks, the
#: victim's side where the point struck sits on a body pressed to a wall.
NEAR = 4.0
FAR = 4.0
#: Crossings closer than this along the segment (game units) are one (a shared edge of two triangles).
SAME = 0.05
#: A wall thinner than this (m) is a graze of its edge, not a wall the bullet went through.
MIN_WALL = 0.01
#: More solid than this (m) in all, or any of STOPS, is more than a bullet passes: the hit shows the shot did not
#: take the traced line (a moving part, the victim placed back by lag compensation), so it is not known.
MAX_SOLID = 0.8
STOPS = frozenset({"solidmetal", "metal_barrel", "metal_sand_barrel", "metalvehicle"})
#: Solid in the mesh, but bullets pass through as through a fence: counted with the grates.
SOFT = frozenset({"foliage"})
#: Passed at no cost to the bullet, but counted by the game as passed.
RAILINGS = frozenset({"metalrailing"})
#: The numeric columns a hurt row gains (and `wallSurfaces`, text).
COLUMNS = ["wallbang", "wallCount", "wallThickness", "wallGrates"]
PASS = "passbullets"

#: The guns by the game's item number (`fire_bullets` `item_def_index`): name as hurt rows give it, damage, range
#: modifier (the damage kept per 500 units flown), armour ratio, headshot multiplier, penetration power. From the
#: game's own weapons script (`scripts/weapons.vdata`, CS2 1.42).
GUNS: dict[int, tuple[str, int, float, float, float, float]] = {
    1: ("deagle", 53, 0.85, 1.864, 3.9, 2.0), 2: ("elite", 38, 0.79, 1.15, 4.0, 1.0),
    3: ("fiveseven", 32, 0.81, 1.823, 4.0, 1.0), 4: ("glock", 30, 0.85, 0.94, 4.0, 1.0),
    7: ("ak47", 36, 0.98, 1.55, 4.0, 2.0), 8: ("aug", 28, 0.98, 1.8, 4.0, 2.0),
    9: ("awp", 115, 0.99, 1.95, 4.0, 2.5), 10: ("famas", 30, 0.96, 1.4, 4.0, 2.0),
    11: ("g3sg1", 80, 0.98, 1.65, 4.0, 2.5), 13: ("galilar", 30, 0.98, 1.55, 4.0, 2.0),
    14: ("m249", 32, 0.97, 1.6, 4.0, 2.0), 16: ("m4a1", 33, 0.97, 1.4, 4.0, 2.0),
    17: ("mac10", 29, 0.8, 1.15, 4.0, 1.0), 19: ("p90", 26, 0.86, 1.38, 4.0, 1.0),
    23: ("mp5sd", 28, 0.87, 1.25, 4.0, 1.0), 24: ("ump45", 35, 0.75, 1.3, 4.0, 1.0),
    25: ("xm1014", 20, 0.7, 1.6, 4.0, 1.0), 26: ("bizon", 27, 0.8, 1.26, 4.0, 1.0),
    27: ("mag7", 30, 0.45, 1.5, 4.0, 1.0), 28: ("negev", 35, 0.97, 1.42, 4.0, 2.0),
    29: ("sawedoff", 32, 0.45, 1.5, 4.0, 1.0), 30: ("tec9", 33, 0.79, 1.812, 4.0, 1.0),
    32: ("hkp2000", 35, 0.91, 1.01, 4.0, 1.0), 33: ("mp7", 30, 0.87, 1.25, 4.0, 1.0),
    34: ("mp9", 26, 0.87, 1.2, 4.0, 1.0), 35: ("nova", 26, 0.7, 1.0, 4.0, 1.0),
    36: ("p250", 38, 0.9, 1.28, 4.0, 1.0), 38: ("scar20", 80, 0.98, 1.65, 4.0, 2.5),
    39: ("sg556", 30, 0.98, 2.0, 4.0, 2.0), 40: ("ssg08", 88, 0.98, 1.7, 4.0, 2.5),
    60: ("m4a1_silencer", 38, 0.94, 1.4, 3.475, 2.0), 61: ("usp_silencer", 35, 0.91, 1.01, 4.0, 1.0),
    63: ("cz75a", 31, 0.85, 1.553, 4.0, 1.0), 64: ("revolver", 86, 0.94, 1.864, 4.0, 2.0),
}
#: Hurt rows name two guns each by one name (M4A4 and M4A1-S as `m4a1`, ...): by name only the others are known.
_NAMES = [g[0] for g in GUNS.values()]
BY_NAME = {g[0]: k for k, g in GUNS.items() if _NAMES.count(g[0]) == 1 and g[0] not in ("m4a1", "hkp2000", "deagle", "mp7")}
#: The damage a hit on each part takes, against a body hit (the head: the gun's own headshot multiplier).
PART = {"neck": 1.0, "chest": 1.0, "stomach": 1.25, "left_arm": 1.0, "right_arm": 1.0, "left_leg": 0.75, "right_leg": 0.75}
#: Parts no armour covers.
BARE = {"left_leg", "right_leg"}
#: What a team-mate's bullet deals (the game's friendly-fire bullet damage).
FRIENDLY = 0.33
#: The least anything passed costs a bullet: this share of its damage (a grate's or glass's), and this much over
#: the gun's penetration power.
LEAST_SHARE, LEAST_POINTS = 0.05, 3.75


def to_game(viewer: np.ndarray) -> np.ndarray:
    """The frame the level is written in, (X, Z, -Y), back to the game's (X, Y, Z)."""
    return np.stack([viewer[..., 0], -viewer[..., 2], viewer[..., 1]], axis=-1)


class Level:
    """A map's collision triangles in the game's frame, binned for tracing."""

    def __init__(self, triangles: np.ndarray, surface: np.ndarray, names: list[str], passes: np.ndarray):
        self.tri = triangles.astype(np.float64)
        self.surface = surface.astype(np.int32)
        self.names = names
        self.passes = passes.astype(bool)
        a, b, c = self.tri[:, 0], self.tri[:, 1], self.tri[:, 2]
        self.e1, self.e2 = b - a, c - a
        self.normal = np.cross(self.e1, self.e2)
        self.origin = self.tri.reshape(-1, 3).min(axis=0) - 1.0 if len(self.tri) else np.zeros(3)
        top = self.tri.reshape(-1, 3).max(axis=0) + 1.0 if len(self.tri) else np.ones(3)
        self.dims = np.maximum(1, np.ceil((top - self.origin) / CELL).astype(np.int64))
        self._bin()

    def _key(self, ijk: np.ndarray) -> np.ndarray:
        return (ijk[..., 0] * self.dims[1] + ijk[..., 1]) * self.dims[2] + ijk[..., 2]

    def _bin(self) -> None:
        lo = np.floor((self.tri.min(axis=1) - self.origin) / CELL).astype(np.int64)
        hi = np.floor((self.tri.max(axis=1) - self.origin) / CELL).astype(np.int64)
        span = hi - lo
        keys, ids = [], []
        small = np.nonzero((span <= 2).all(axis=1))[0]
        for dx in range(3):
            for dy in range(3):
                for dz in range(3):
                    off = np.array([dx, dy, dz])
                    keep = small[((lo[small] + off) <= hi[small]).all(axis=1)]
                    keys.append(self._key(lo[keep] + off))
                    ids.append(keep)
        for i in np.nonzero(~(span <= 2).all(axis=1))[0]:
            g = np.stack(np.meshgrid(*(np.arange(lo[i, k], hi[i, k] + 1) for k in range(3)), indexing="ij"), axis=-1).reshape(-1, 3)
            keys.append(self._key(g))
            ids.append(np.full(len(g), i))
        key = np.concatenate(keys) if keys else np.zeros(0, np.int64)
        tid = np.concatenate(ids).astype(np.int32) if ids else np.zeros(0, np.int32)
        order = np.argsort(key, kind="stable")
        key, self.cell_tris = key[order], tid[order]
        self.cell_keys, self.cell_start = np.unique(key, return_index=True)
        self.cell_end = np.append(self.cell_start[1:], len(key))

    def cells(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """The keys of the cells the segment a-b passes, in order."""
        d = b - a
        p = (a - self.origin) / CELL
        i = np.floor(p).astype(np.int64)
        end = np.floor((b - self.origin) / CELL).astype(np.int64)
        step = np.sign(d).astype(np.int64)
        with np.errstate(divide="ignore", invalid="ignore"):
            delta = np.where(d != 0, np.abs(CELL / d), np.inf)
            bound = self.origin + (i + (step > 0)) * CELL
            t_max = np.where(d != 0, (bound - a) / d, np.inf)
        out = [i.copy()]
        for _ in range(int(np.abs(end - i).sum()) + 3):
            if (i == end).all():
                break
            k = int(np.argmin(t_max))
            if t_max[k] > 1.0:
                break
            i[k] += step[k]
            t_max[k] += delta[k]
            out.append(i.copy())
        cells = np.array(out)
        inside = ((cells >= 0) & (cells < self.dims)).all(axis=1)
        return self._key(cells[inside])

    def candidates(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        keys = self.cells(a, b)
        if not len(keys) or not len(self.cell_keys):
            return np.zeros(0, np.int32)
        at = np.minimum(np.searchsorted(self.cell_keys, keys), len(self.cell_keys) - 1)
        at = at[self.cell_keys[at] == keys]
        if not len(at):
            return np.zeros(0, np.int32)
        parts = [self.cell_tris[s:e] for s, e in zip(self.cell_start[at], self.cell_end[at])]
        return np.unique(np.concatenate(parts))

    def trace(self, a: np.ndarray, b: np.ndarray) -> tuple[int, float, list[str], int]:
        """
        The segment a-b (game units) through the level: solids passed, their
        thickness in game units, their surfaces in order, grates crossed.
        """
        walls, sheets = self.passed(a, b)
        return len(walls), sum(w[1] for w in walls), [w[0] for w in walls], len(sheets)

    def passed(self, a: np.ndarray, b: np.ndarray) -> tuple[list[list], list[str]]:
        """
        The segment a-b (game units) through the level: the solids passed, as
        [surface, thickness in game units] in order from a, and the surfaces of
        the bullet-passing sheets crossed (fences, grates, railings, foliage),
        one for each crossing, in order.
        """
        seg = b - a
        length = float(np.linalg.norm(seg))
        if length <= NEAR + FAR:
            return [], []
        t0, t1 = NEAR / length, 1.0 - FAR / length
        ids = self.candidates(a, b)
        if not len(ids):
            return [], []
        # Moller-Trumbore on every candidate at once.
        e1, e2 = self.e1[ids], self.e2[ids]
        pv = np.cross(seg, e2)
        det = np.einsum("ij,ij->i", e1, pv)
        ok = np.abs(det) > 1e-9
        inv = np.divide(1.0, det, out=np.zeros_like(det), where=ok)
        tv = a - self.tri[ids, 0]
        u = np.einsum("ij,ij->i", tv, pv) * inv
        qv = np.cross(tv, e1)
        v = (qv @ seg) * inv
        t = np.einsum("ij,ij->i", e2, qv) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > t0) & (t < t1)
        if not hit.any():
            return [], []
        ids, t = ids[hit], t[hit]
        entering = (self.normal[ids] @ seg) < 0
        grates = self.passes[ids]
        # Grates: each crossing of a sheet, a shared edge once.
        order = np.argsort(t[grates], kind="stable")
        sheets: list[str] = []
        last_t = None
        for tt, k in zip(t[grates][order] * length, self.surface[ids[grates]][order]):
            if last_t is None or tt - last_t > SAME:
                sheets.append(self.names[k])
            last_t = tt
        solid = ~grates
        order = np.argsort(t[solid], kind="stable")
        ts, ins, surf = t[solid][order] * length, entering[solid][order], self.surface[ids[solid]][order]
        walls: list[list] = []  # [surface, thickness in game units]
        depth, last = 0, None
        for tt, enter, k in zip(ts, ins, surf):
            if last is not None and tt - last[0] < SAME and enter == last[1]:
                continue  # the same face, through a shared edge
            last = (tt, enter)
            if enter:
                if depth == 0:
                    walls.append([self.names[k], -tt])
                depth += 1
            elif depth > 0:
                depth -= 1
                if depth == 0:
                    walls[-1][1] += tt
            else:
                # Left a solid it never entered: an open face, or the muzzle inside it; a wall of no known depth.
                walls.append([self.names[k], 0.0])
        if depth > 0:
            walls[-1][1] += t1 * length
        sheets += [w[0] for w in walls if w[0] in SOFT]
        walls = [w for w in walls if w[0] not in SOFT and w[1] * METRES >= MIN_WALL]
        return walls, sheets


def load(path: str | Path) -> Level:
    """A level written by `map` (mapexport.py), ready to trace."""
    doc, blob = glb.read(path)
    tris, surface, passes, names = [], [], [], []
    index: dict[str, int] = {}
    for name, positions, triangles in glb.meshes(doc, blob):
        kind, _, what = name.partition(":")
        if kind not in ("ground", "structure") or not len(triangles):
            continue
        passing = what.startswith(PASS + ":")
        what = surface_name(what[len(PASS) + 1 :] if passing else what)
        k = index.setdefault(what, len(names))
        if k == len(names):
            names.append(what)
        tris.append(to_game(positions[triangles]))
        surface.append(np.full(len(triangles), k))
        passes.append(np.full(len(triangles), passing))
    if not tris:
        raise ValueError(f"{path}: no ground or structure parts")
    return Level(np.concatenate(tris), np.concatenate(surface), names, np.concatenate(passes))


@lru_cache(maxsize=2)
def cached(path: str, stamp: float) -> Level:
    return load(path)


def find(map_name: str, levels: str | Path | None = None) -> Path | None:
    """The level `map` wrote for this map: `<levels>/cs2/<map>.glb` or `<levels>/<map>.glb`, where `levels` is
    given, else HEAT3D_LEVELS, else the 3DHeat levels folder."""
    if not map_name:
        return None
    if levels is None:
        from .app import paths

        levels = paths.levels_dir()
    root = Path(levels)
    for candidate in (root / "cs2" / f"{map_name}.glb", root / f"{map_name}.glb"):
        if candidate.is_file():
            return candidate
    return None


def level_for(map_name: str, levels: str | Path | None = None) -> Level | None:
    found = find(map_name, levels)
    if found is None or os.environ.get("HEAT3D_NO_WALLBANG"):
        return None
    return cached(str(found), found.stat().st_mtime)


def _numbers(hurts: pd.DataFrame, name: str) -> np.ndarray:
    return pd.to_numeric(hurts[name], errors="coerce").to_numpy(dtype=float) if name in hurts else np.full(len(hurts), np.nan)


def health_damage(gun: int, flown: float, part: str, armour: float, friendly: bool, least: bool = False) -> float:
    """
    The health a hit takes from `gun` (item number) after `flown` game units, on
    `part`, through `armour` points (worn on the part; 0 none), from a team-mate
    or not: the gun's full damage, or with `least`, what is left after the
    least that anything passed on the way costs.
    """
    _, base, falloff, ratio, head, power = GUNS[gun]
    damage = base * falloff ** (flown / 500.0)
    if least:
        damage = damage * (1.0 - LEAST_SHARE) - LEAST_POINTS / power
    damage *= head if part == "head" else PART[part]
    if armour > 0 and part not in BARE:
        health = damage * ratio * 0.5
        # Armour takes half of the rest; what it cannot take goes to health.
        if (damage - health) * 0.5 > armour:
            health = damage - armour * 2.0
        damage = health
    return damage * (FRIENDLY if friendly else 1.0)


def damage_lost(hurts: pd.DataFrame, weapons: np.ndarray, flown: np.ndarray) -> np.ndarray:
    """
    Per hurt row: 1 where the hit dealt less than its weapon's full damage by at
    least what anything passed on the way costs (it went through something),
    0 where it dealt the full damage, NaN where that cannot be told (weapon not
    known, no place on the body, no damage). `weapons`: the game's item numbers
    (the shot's), `flown`: how far the bullet flew, game units.
    """
    n = len(hurts)
    out = np.full(n, np.nan)
    if not n:
        return out
    dealt, armour, armour_lost = _numbers(hurts, "dmg_health"), _numbers(hurts, "armor"), _numbers(hurts, "dmg_armor")
    mine, theirs = _numbers(hurts, "attacker_team_num"), _numbers(hurts, "user_team_num")
    parts = hurts["hitgroup"].fillna("").astype(str).str.lower().str.replace(" ", "_").to_numpy() if "hitgroup" in hurts else np.full(n, "")
    names = hurts["weapon"].fillna("").astype(str).str.removeprefix("weapon_").to_numpy() if "weapon" in hurts else np.full(n, "")
    for i in range(n):
        gun = int(weapons[i]) if np.isfinite(weapons[i]) else BY_NAME.get(names[i], -1)
        part = parts[i]
        if gun not in GUNS or (part != "head" and part not in PART) or not dealt[i] > 0 or not np.isfinite(flown[i]):
            continue
        # The armour before the hit; a helmet is known only from the armour a head hit took.
        worn = (armour[i] if np.isfinite(armour[i]) else 0.0) + (armour_lost[i] if np.isfinite(armour_lost[i]) else 0.0)
        if part == "head" and not armour_lost[i] > 0:
            worn = 0.0
        friendly = bool(np.isfinite(mine[i]) and mine[i] == theirs[i])
        full = health_damage(gun, flown[i], part, worn, friendly)
        least = health_damage(gun, flown[i], part, worn, friendly, least=True)
        # The game deals whole points (it drops the fraction): the line is halfway between the two.
        out[i] = 1.0 if dealt[i] < (np.floor(full) + np.floor(least)) / 2 + 0.01 else 0.0
    return out


def columns(level: Level | None, origins: np.ndarray, points: np.ndarray, hurts: pd.DataFrame | None = None,
            weapons: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """
    The wallbang columns for shots from `origins` to `points` (n x 3, game
    units; NaN where not known), with the hurt rows themselves (`hurts`: their
    damage, armour, part struck, teams) and the shots' weapons (`weapons`, the
    game's item numbers) for the damage they dealt. Without a level, the
    damage alone; without either, all NaN and "".
    """
    n = len(origins)
    out = {k: np.full(n, np.nan) for k in COLUMNS}
    surfaces = np.full(n, "", dtype=object)
    lost = np.full(n, np.nan)
    if hurts is not None and len(hurts) == n:
        flown = np.linalg.norm(points - origins, axis=1)
        lost = damage_lost(hurts.reset_index(drop=True), weapons if weapons is not None else np.full(n, np.nan), flown)
    traceable = np.isfinite(origins).all(axis=1) & np.isfinite(points).all(axis=1)
    for i in range(n):
        out["wallbang"][i] = lost[i]
        if level is None or not traceable[i]:
            continue
        walls, sheets = level.passed(origins[i], points[i])
        rails = [x for x in sheets if x in RAILINGS]
        thick = sum(w[1] for w in walls) * METRES
        names = [w[0] for w in walls]
        out["wallGrates"][i] = len(sheets)
        believable = thick <= MAX_SOLID and not STOPS.intersection(names)
        if lost[i] == 1.0:
            # Through something: the walls the trace saw, else the sheets the line crossed, else not seen (a door,
            # a prop, a player: not in the level).
            if walls and believable:
                out["wallCount"][i], out["wallThickness"][i], surfaces[i] = len(walls), round(thick, 3), ";".join(names)
            elif [x for x in sheets if x not in SOFT]:
                crossed = [x for x in sheets if x not in SOFT]
                out["wallCount"][i], out["wallThickness"][i], surfaces[i] = len(crossed), 0.0, ";".join(crossed)
        elif lost[i] == 0.0:
            # The full damage: nothing on the way but what costs a bullet nothing.
            out["wallbang"][i] = 1.0 if rails else 0.0
            out["wallCount"][i], out["wallThickness"][i], surfaces[i] = len(rails), 0.0, ";".join(rails)
        elif believable:
            out["wallbang"][i] = 1.0 if walls or rails else 0.0
            out["wallCount"][i], out["wallThickness"][i], surfaces[i] = len(walls) + len(rails), round(thick, 3), ";".join(names + rails)
    return {**out, "wallSurfaces": surfaces}
