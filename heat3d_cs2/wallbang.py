"""
Whether a hit went through a wall: the shot traced through the map.

The game says so only for kills (`penetrated` on the death). For every other
hit the shot is traced here: a segment from where the bullet left the
shooter (the game's own account of the shot, `fire_bullets`, else the
shooter's eye) to the point struck on the victim (impact.py), through the
map's collision mesh as `map` exports it (mapexport.py) - the same level the
viewer draws.

What bullets pass through untouched (the map's `passbullets` groups:
chain-link fences, grates; foliage) is counted on its own, as grates, not as
walls; so is a wall's edge grazed (thinner than MIN_WALL along the line).
Clip brushes and the sky are not in the level at all. The mesh is binned
in a uniform grid of 2 m cells; a segment walks the cells it crosses
(Amanatides and Woo) and is tested against their triangles (Moller and
Trumbore). A solid is entered where the segment crosses a face from its
front and left where it crosses one from its back, so overlapping pieces of
one wall are one wall and its thickness is how far the segment ran inside.

Per hurt row:

- `wallbang`: 1 where the shot crossed at least one solid, 0 where its line
  was clear, NaN where it was not traced (no level, no place on the body:
  grenades, fire, falls; no shot origin) or the line cannot be the bullet's:
  more solid than a bullet passes (MAX_SOLID, or solid metal) yet it hit.
- `wallCount`: the solids passed.
- `wallThickness`: metres of solid passed, all together.
- `wallSurfaces`: their surfaces in order from the shooter, `;`-joined.
- `wallGrates`: bullet-passing surfaces crossed.

Doors and other moving parts are not in the world's collision mesh, so a
shot through one is not seen here.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import glb

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
#: The numeric columns a hurt row gains (and `wallSurfaces`, text).
COLUMNS = ["wallbang", "wallCount", "wallThickness", "wallGrates"]
PASS = "passbullets"


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
        seg = b - a
        length = float(np.linalg.norm(seg))
        if length <= NEAR + FAR:
            return 0, 0.0, [], 0
        t0, t1 = NEAR / length, 1.0 - FAR / length
        ids = self.candidates(a, b)
        if not len(ids):
            return 0, 0.0, [], 0
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
            return 0, 0.0, [], 0
        ids, t = ids[hit], t[hit]
        entering = (self.normal[ids] @ seg) < 0
        grates = self.passes[ids]
        # Grates: each crossing of a sheet, a shared edge once.
        gt = np.sort(t[grates]) * length
        n_grates = int(len(gt) and 1 + (np.diff(gt) > SAME).sum())
        solid = ~grates
        order = np.argsort(t[solid], kind="stable")
        ts, ins, surf = t[solid][order] * length, entering[solid][order], self.surface[ids[solid]][order]
        walls: list[list] = []  # [surface, thickness in game units]
        depth, last = 0, None
        for tt, enter, s in zip(ts, ins, surf):
            if last is not None and tt - last[0] < SAME and enter == last[1]:
                continue  # the same face, through a shared edge
            last = (tt, enter)
            if enter:
                if depth == 0:
                    walls.append([self.names[s], -tt])
                depth += 1
            elif depth > 0:
                depth -= 1
                if depth == 0:
                    walls[-1][1] += tt
            else:
                # Left a solid it never entered: an open face, or the muzzle inside it; a wall of no known depth.
                walls.append([self.names[s], 0.0])
        if depth > 0:
            walls[-1][1] += t1 * length
        n_grates += sum(1 for w in walls if w[0] in SOFT)
        walls = [w for w in walls if w[0] not in SOFT and w[1] * METRES >= MIN_WALL]
        count, thick, names = len(walls), sum(w[1] for w in walls), [w[0] for w in walls]
        return count, thick, names, n_grates


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
        what = what[len(PASS) + 1 :] if passing else what
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


def columns(level: Level | None, origins: np.ndarray, points: np.ndarray) -> dict[str, np.ndarray]:
    """
    The wallbang columns for shots from `origins` to `points` (n x 3, game
    units; NaN where not known). All NaN and "" without a level.
    """
    n = len(origins)
    out = {k: np.full(n, np.nan) for k in COLUMNS}
    surfaces = np.full(n, "", dtype=object)
    if level is not None:
        for i in np.nonzero(np.isfinite(origins).all(axis=1) & np.isfinite(points).all(axis=1))[0]:
            count, thick, names, grates = level.trace(origins[i], points[i])
            if thick * METRES > MAX_SOLID or STOPS.intersection(names):
                continue
            out["wallbang"][i] = 1.0 if count else 0.0
            out["wallCount"][i] = count
            out["wallThickness"][i] = round(thick * METRES, 3)
            out["wallGrates"][i] = grates
            surfaces[i] = ";".join(names)
    return {**out, "wallSurfaces": surfaces}
