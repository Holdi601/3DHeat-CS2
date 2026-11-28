"""
Where every player looked, tick by tick, and which enemies they had a clear
line to: the `view` sidecar, `<match>.view.parquet`.

The table and its other sidecars keep the players eight times a second. How
someone aims - how fast the view turns onto a target, whether it stops dead on
a head, when the shot goes off - plays out in a few hundredths of a second, so
this sidecar keeps every tick (64 a second) of every living player in a round
(from the end of freeze time until four seconds after the round was decided):
position, the view (the game's eye angles and the angles of the player's own
command), the mouse movement the command carried, how far the command's view
was from the server's (`cmdOff`), the aim punch of the recoil, crouch,
speed, flash, zoom and the gun in hand.

`sees` is a bitmask of the enemies (by `slot`, the players' order in the
file's `heat3d` key) to whom the player had a clear line of sight at that
tick - through the map, not counting where the player looked. A line is
clear when no wall stands between the player's eye and any of five points on
the enemy (head, chest, chest a little to either side, knee), and no smoke
stands in the way:

- The map is the level `map` wrote (mapexport.py), the same the viewer draws,
  as a grid of 12-unit cubes (30 cm) marked solid where a surface passes; a
  line that reaches a solid cube is tested against that cube's triangles, and
  is blocked only where one of them really lies on it.
  What can be seen through - glass, chain-link, railings, grates, foliage,
  the map's bullet-passing parts - is left out; so are doors and other
  moving parts, which the level does not have. A line walks the grid in steps
  as long as the distance to the nearest solid cube allows (a distance field),
  so open ground costs few steps. The first and last 16 units of a line are
  not looked at: a player pressed to a wall, or peeking past its edge, is not
  hidden by it.
- A smoke is a 150 x 150 x 110 unit ellipsoid around where it went off, from
  a second after it popped until a second and a half before it was gone; a
  line through more than 80 units of its inner two thirds is blocked. An HE grenade
  bursting next to it clears it for a second and a half. (Checked on 2,197 kills of
  16 demos: of the kills the game says were through no wall and no smoke, the
  line was clear within a quarter second before the kill on 96 %; 2 % were
  blocked by the map - collision shapes fuller than what is drawn, such as the
  trains - and 1.5 % by a smoke, which the smaller core above lowers.)

The five points are on the generous side: an enemy just
showing at a corner counts as in sight. The lines are checked sixteen times a
second (every fourth tick), and where one changes between two checks, at each
tick in between. `smoked` is the mask of the enemies whose line was clear of
walls but not of smoke.

Without the map's level the column is empty (null) and the rest is written.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .demo import TICKRATE

#: What is read of every player at every tick, demoparser2's name -> the sidecar's column.
FIELDS = {
    "X": "x",
    "Y": "y",
    "Z": "z",
    "pitch": "pitch",
    "yaw": "yaw",
    "usercmd_viewangle_x": "cmdPitch",
    "usercmd_viewangle_y": "cmdYaw",
    "usercmd_mouse_dx": "mouseX",
    "usercmd_mouse_dy": "mouseY",
    "duck_amount": "duck",
    "velocity_X": "vx",
    "velocity_Y": "vy",
    "velocity_Z": "vz",
    "flash_duration": "flash",
    "aim_punch_angle": "punch",
    "zoom_lvl": "zoom",
    "is_airborne": "airborne",
    "active_weapon_name": "weapon",
    "is_alive": "alive",
    "team_num": "team",
}

#: The grid's cube (game units, 30 cm) and the stretch of a line at either end not looked at.
VOXEL = 12.0
NEAR = FAR = 16.0
#: Surfaces that can be seen through.
SEE_THROUGH = frozenset({"glass", "chainlink", "metalrailing", "metalvent", "metal_grate", "grate", "foliage", "wire",
                         "metalgrate", "chain", "glass_breakable", "glassbottle", "watermelon"})
PASS = "passbullets"
#: Eye height standing and crouched (game units); the eye is between by the crouch.
EYE, EYE_DUCKED = 64.0, 46.0
#: Every this many ticks the lines are checked; where one changes, every tick in between.
EVERY = 4
#: The smoke's ellipsoid (radii, units), its centre above where it went off, the part of it that blocks, how far a
#: line must run through that part, and the time after the pop / before it is gone that it blocks.
SMOKE_RADII = np.array([150.0, 150.0, 110.0])
SMOKE_LIFT = 60.0
SMOKE_CORE = 0.65
SMOKE_CHORD = 80.0
SMOKE_BLOOM, SMOKE_FADE = 1.0, 1.5
#: An HE grenade this close to a smoke clears it for this long.
HE_CLEARS, HE_CLEAR_FOR = 220.0, 1.5
#: Seconds of a round kept after it was decided.
AFTER = 4.0
#: The most players a mask holds.
SLOTS = 31


class Occluder:
    """A map's see-blocking surfaces as a grid of solid cubes, with each free cube's distance to the nearest solid."""

    def __init__(self, triangles: np.ndarray, voxel: float = VOXEL):
        from scipy.ndimage import distance_transform_cdt

        tri = np.asarray(triangles, dtype=np.float64).reshape(-1, 3, 3)
        self.voxel = voxel
        self.lo = tri.reshape(-1, 3).min(axis=0) - 2 * voxel
        hi = tri.reshape(-1, 3).max(axis=0) + 2 * voxel
        self.dims = np.ceil((hi - self.lo) / voxel).astype(np.int64)
        solid = np.zeros(tuple(self.dims), dtype=bool)
        self.tri = tri
        self._rasterise(tri, solid)
        self.solid = solid
        # Chessboard distance (in cubes) from each free cube to the nearest solid one; never more than a bound,
        # for the step taken from it is a step safely short of any solid.
        dist = distance_transform_cdt(~solid, metric="chessboard")
        self.dist = np.minimum(dist, 250).astype(np.uint8)

    def _rasterise(self, tri: np.ndarray, solid: np.ndarray) -> None:
        """Mark the cubes each triangle passes, and keep which triangles pass each cube (for the exact test)."""
        a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
        longest = np.max(np.stack([np.linalg.norm(b - a, axis=1), np.linalg.norm(c - b, axis=1),
                                   np.linalg.norm(a - c, axis=1)]), axis=0)
        # Points on the triangle no further apart than a third of a cube: every cube the surface passes is marked.
        steps = np.maximum(1, np.ceil(longest / (self.voxel / 3))).astype(np.int64)
        dims = self.dims
        pairs = []
        for n in np.unique(steps):
            pick = np.flatnonzero(steps == n)
            i, j = np.meshgrid(np.arange(n + 1), np.arange(n + 1), indexing="ij")
            keep = (i + j) <= n
            u = (i[keep] / n)[None, :, None]
            v = (j[keep] / n)[None, :, None]
            for chunk in np.array_split(pick, max(1, int(len(pick) * u.shape[1] // 4_000_000) + 1)):
                if not len(chunk):
                    continue
                pa_, pb, pc_ = a[chunk][:, None, :], b[chunk][:, None, :], c[chunk][:, None, :]
                pts = (pa_ + u * (pb - pa_) + v * (pc_ - pa_)).reshape(-1, 3)
                ijk = np.clip(np.floor((pts - self.lo) / self.voxel).astype(np.int64), 0, dims - 1)
                solid[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True
                lin = (ijk[:, 0] * dims[1] + ijk[:, 1]) * dims[2] + ijk[:, 2]
                owner = np.repeat(chunk, u.shape[1])
                pairs.append(np.unique(lin * len(tri) + owner))
        both = np.unique(np.concatenate(pairs)) if pairs else np.zeros(0, dtype=np.int64)
        cell, self.cell_tri = both // len(tri), both % len(tri)
        # CSR: the triangles of cube `lin` are cell_tri[start[k]:start[k+1]] where cells[k] == lin.
        self.cells, first = np.unique(cell, return_index=True)
        self.cell_start = np.r_[first, len(cell)]

    def _exact(self, origin: np.ndarray, unit: np.ndarray, end: np.ndarray, lin: np.ndarray,
               near: float) -> np.ndarray:
        """For rays standing in a solid cube: whether one of the cube's triangles really lies on the segment."""
        k = np.searchsorted(self.cells, lin)
        k = np.clip(k, 0, len(self.cells) - 1)
        found = self.cells[k] == lin
        lo = np.where(found, self.cell_start[k], 0)
        hi = np.where(found, self.cell_start[np.minimum(k + 1, len(self.cell_start) - 1)], 0)
        count = hi - lo
        ray = np.repeat(np.arange(len(lin)), count)
        if not len(ray):
            return np.zeros(len(lin), dtype=bool)
        offs = np.arange(len(ray)) - np.repeat(np.cumsum(count) - count, count)
        t_ = self.tri[self.cell_tri[np.repeat(lo, count) + offs]]
        o, d = origin[ray], unit[ray]
        e1, e2 = t_[:, 1] - t_[:, 0], t_[:, 2] - t_[:, 0]
        p = np.cross(d, e2)
        det = np.einsum("ij,ij->i", e1, p)
        ok = np.abs(det) > 1e-9
        inv = 1.0 / np.where(ok, det, 1.0)
        s = o - t_[:, 0]
        u = np.einsum("ij,ij->i", s, p) * inv
        q = np.cross(s, e1)
        v = np.einsum("ij,ij->i", d, q) * inv
        t = np.einsum("ij,ij->i", e2, q) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t >= near) & (t <= end[ray])
        out = np.zeros(len(lin), dtype=bool)
        out[ray[hit]] = True
        return out

    def blocked(self, a: np.ndarray, b: np.ndarray, near: float = NEAR, far: float = FAR) -> np.ndarray:
        """For each segment a[k] -> b[k] (game units), whether a solid cube stands on it (ends left out)."""
        a = np.asarray(a, dtype=np.float64)
        b = np.asarray(b, dtype=np.float64)
        d = b - a
        length = np.linalg.norm(d, axis=1)
        out = np.zeros(len(a), dtype=bool)
        live = np.flatnonzero(length > near + far)
        if not len(live):
            return out
        unit = d[live] / length[live, None]
        s = np.full(len(live), near)
        end = length[live] - far
        origin = a[live]
        dims = self.dims
        for _ in range(2000):
            if not len(live):
                break
            p = origin + unit * s[:, None]
            ijk = np.floor((p - self.lo) / self.voxel).astype(np.int64)
            inside = np.all((ijk >= 0) & (ijk < dims), axis=1)
            dv = np.full(len(live), 250, dtype=np.int64)
            q = ijk[inside]
            dv[inside] = self.dist[q[:, 0], q[:, 1], q[:, 2]]
            hit = dv == 0
            if hit.any():
                # A solid cube on the way: blocked only where one of its triangles really is on the segment.
                h = np.flatnonzero(hit)
                qq = ijk[h]
                lin = (qq[:, 0] * dims[1] + qq[:, 1]) * dims[2] + qq[:, 2]
                real = self._exact(origin[h], unit[h], end[h], lin, near)
                hit[h[~real]] = False
            out[live[hit]] = True
            step = np.maximum(dv - 1, 0).astype(np.float64) * self.voxel
            step = np.maximum(step, self.voxel * 0.5)
            s = s + step
            go = ~hit & (s < end)
            live, unit, s, end, origin = live[go], unit[go], s[go], end[go], origin[go]
        return out


def occluder_from_level(path: str | Path) -> Occluder:
    """The see-blocking surfaces of a level written by `map`."""
    from . import glb
    from .mapexport import surface_name
    from .wallbang import to_game

    doc, blob = glb.read(path)
    tris = []
    for name, positions, triangles in glb.meshes(doc, blob):
        kind, _, what = name.partition(":")
        if kind not in ("ground", "structure") or not len(triangles) or what.startswith(PASS + ":"):
            continue
        if surface_name(what) in SEE_THROUGH:
            continue
        tris.append(to_game(positions[triangles]))
    if not tris:
        raise ValueError(f"{path}: no ground or structure parts")
    return Occluder(np.concatenate(tris))


_CACHE: dict[tuple[str, float], Occluder] = {}


def occluder_for(map_name: str, levels: str | Path | None = None) -> Occluder | None:
    from .wallbang import find

    found = find(map_name, levels)
    if found is None:
        return None
    key = (str(found), found.stat().st_mtime)
    if key not in _CACHE:
        _CACHE.clear()
        _CACHE[key] = occluder_from_level(found)
    return _CACHE[key]


# ---------------------------------------------------------------- smokes


def smokes_of(rows: pd.DataFrame) -> np.ndarray:
    """(n, 6): centre x, y, z, from, to, entity - the time each smoke blocks sight."""
    pops = rows[rows["event"] == "smoke"]
    gone = rows[rows["event"] == "smokegrenade_expired"]
    ends = {}
    for e, t in zip(gone["entity"].to_numpy(dtype=float), gone["time"].to_numpy(dtype=float)):
        if np.isfinite(e):
            ends.setdefault(int(e), []).append(t)
    out = []
    for x, y, z, t, e in pops[["x", "y", "z", "time", "entity"]].itertuples(index=False):
        later = [u for u in ends.get(int(e), []) if u > t] if np.isfinite(e) else []
        until = min(later) if later else t + 20.0
        out.append((x, y, z + SMOKE_LIFT, t + SMOKE_BLOOM, until - SMOKE_FADE, e))
    return np.array(out, dtype=np.float64).reshape(-1, 6)


def _he_clears(rows: pd.DataFrame, smokes: np.ndarray) -> list[tuple[int, float, float]]:
    hes = rows[rows["event"] == "he"][["x", "y", "z", "time"]].to_numpy(dtype=float)
    out = []
    for k, s in enumerate(smokes):
        for x, y, z, t in hes:
            if s[3] - SMOKE_BLOOM <= t <= s[4] and np.linalg.norm(np.array([x, y, z + SMOKE_LIFT]) - s[:3]) < HE_CLEARS:
                out.append((k, t, t + HE_CLEAR_FOR))
    return out


def smoked(a: np.ndarray, b: np.ndarray, t: np.ndarray, smokes: np.ndarray, clears=()) -> np.ndarray:
    """For each segment a[k] -> b[k] at time t[k], whether a smoke blocks it."""
    out = np.zeros(len(a), dtype=bool)
    radii = SMOKE_RADII * SMOKE_CORE
    for k, s in enumerate(smokes):
        on = (t >= s[3]) & (t <= s[4])
        for c, c0, c1 in clears:
            if c == k:
                on &= ~((t >= c0) & (t <= c1))
        idx = np.flatnonzero(on)
        if not len(idx):
            continue
        # The ellipsoid as a unit sphere: scale the segment, intersect, scale the chord back.
        p = (a[idx] - s[:3]) / radii
        q = (b[idx] - s[:3]) / radii
        d = q - p
        dd = np.einsum("ij,ij->i", d, d)
        pd_ = np.einsum("ij,ij->i", p, d)
        pp = np.einsum("ij,ij->i", p, p)
        disc = pd_ ** 2 - dd * (pp - 1.0)
        ok = (disc > 0) & (dd > 0)
        root = np.sqrt(np.where(ok, disc, 0.0))
        t0 = np.clip((-pd_ - root) / np.where(dd > 0, dd, 1), 0, 1)
        t1 = np.clip((-pd_ + root) / np.where(dd > 0, dd, 1), 0, 1)
        chord = (t1 - t0) * np.linalg.norm(b[idx] - a[idx], axis=1)
        out[idx[ok & (chord > SMOKE_CHORD)]] = True
    return out


# ---------------------------------------------------------------- sight


def eye_of(pos: np.ndarray, duck: np.ndarray) -> np.ndarray:
    e = pos.copy()
    e[..., 2] = e[..., 2] + EYE - (EYE - EYE_DUCKED) * np.clip(duck, 0, 1)
    return e


def body_points(pos: np.ndarray, duck: np.ndarray, toward: np.ndarray) -> np.ndarray:
    """(n, 5, 3): head, chest, chest 16 units to either side (across the line from `toward`), knee."""
    h = EYE - (EYE - EYE_DUCKED) * np.clip(duck, 0, 1)
    side = np.stack([-(toward[:, 1] - pos[:, 1]), toward[:, 0] - pos[:, 0], np.zeros(len(pos))], axis=1)
    n = np.linalg.norm(side, axis=1, keepdims=True)
    side = np.where(n > 0, side / np.where(n > 0, n, 1), 0.0) * 16.0
    up = lambda z: np.stack([np.zeros(len(pos)), np.zeros(len(pos)), z], axis=1)  # noqa: E731
    chest = pos + up(h * 0.72)
    return np.stack([pos + up(h - 2), chest, chest + side, chest - side, pos + up(np.full(len(pos), 18.0))], axis=1)


def clear_lines(occ: Occluder | None, eye: np.ndarray, pos: np.ndarray, duck: np.ndarray, t: np.ndarray,
                smokes: np.ndarray, clears=()) -> tuple[np.ndarray, np.ndarray]:
    """
    For each pair (observer's eye, target's feet + crouch, time): (a line to any of the target's points clear of
    walls, a line clear of walls and smoke).
    """
    pts = body_points(pos, duck, eye)
    n = len(eye)
    a = np.repeat(eye, 5, axis=0)
    b = pts.reshape(-1, 3)
    tt = np.repeat(t, 5)
    walls = np.ones(n * 5, dtype=bool)
    if occ is not None:
        walls &= ~occ.blocked(a, b)
    free = walls.copy()
    if len(smokes):
        idx = np.flatnonzero(free)
        free[idx] &= ~smoked(a[idx], b[idx], tt[idx], smokes, clears)
    return walls.reshape(n, 5).any(axis=1), free.reshape(n, 5).any(axis=1)


def sight_masks(ticks: np.ndarray, slot: np.ndarray, team: np.ndarray, pos: np.ndarray, duck: np.ndarray,
                times: np.ndarray, occ: Occluder | None, smokes: np.ndarray, clears=()) -> tuple[np.ndarray, np.ndarray]:
    """
    The `sees` and `smoked` masks of every row (one player at one tick): which enemies' slots had a clear line. Lines are
    checked every EVERY ticks; where any pair's line differs between two checks, at every tick between them;
    elsewhere the ticks between have the lines of the check before.
    """
    order = np.lexsort((slot, ticks))
    tk = ticks[order]
    starts = np.flatnonzero(np.r_[True, tk[1:] != tk[:-1]])
    bounds = np.r_[starts, len(tk)]
    uniq = tk[starts]
    nslot = int(slot.max()) + 1 if len(slot) else 1
    masks = np.zeros((len(uniq), nslot), dtype=np.int64)
    smoky = np.zeros((len(uniq), nslot), dtype=np.int64)
    sig = np.zeros(len(uniq), dtype=np.uint64)
    checked = np.zeros(len(uniq), dtype=bool)

    def check(ks: np.ndarray) -> None:
        if not len(ks):
            return
        # Every enemy pair at each of these ticks.
        o_all, g_all, w_all = [], [], []
        for k in ks:
            rows = order[bounds[k]:bounds[k + 1]]
            if len(rows) < 2:
                continue
            i, j = np.meshgrid(rows, rows, indexing="ij")
            keep = team[i] != team[j]
            o_all.append(i[keep])
            g_all.append(j[keep])
            w_all.append(np.full(int(keep.sum()), k))
        checked[ks] = True
        if not o_all:
            return
        o, g, w = np.concatenate(o_all), np.concatenate(g_all), np.concatenate(w_all)
        res = np.zeros(len(o), dtype=bool)
        wall = np.zeros(len(o), dtype=bool)
        for c in range(0, len(o), 400_000):
            s = slice(c, c + 400_000)
            wall[s], res[s] = clear_lines(occ, eye_of(pos[o[s]], duck[o[s]]), pos[g[s]], duck[g[s]], times[o[s]],
                                          smokes, clears)
        so, sg = slot[o].astype(np.int64), slot[g].astype(np.int64)
        np.bitwise_or.at(masks, (w[res], so[res]), np.left_shift(np.int64(1), sg[res]))
        sm = wall & ~res
        np.bitwise_or.at(smoky, (w[sm], so[sm]), np.left_shift(np.int64(1), sg[sm]))
        h = ((so * 37 + sg + 1) * (res.astype(np.int64) * 1_000_003 + sm.astype(np.int64) * 7919 + 7)).astype(np.uint64)
        np.add.at(sig, w, h)

    sampled = np.flatnonzero((uniq % EVERY == 0) | (np.arange(len(uniq)) == 0) | (np.arange(len(uniq)) == len(uniq) - 1))
    check(sampled)
    # Pairs that changed between two checks: every tick between is checked.
    changed = np.flatnonzero(sig[sampled[1:]] != sig[sampled[:-1]])
    between = [np.arange(sampled[c] + 1, sampled[c + 1]) for c in changed if sampled[c + 1] - sampled[c] > 1]
    if between:
        between = np.concatenate(between)
        for c in range(0, len(between), 4000):
            check(between[c:c + 4000])
    # Each row: its own tick's check, else the check before it.
    k_of_row = np.empty(len(ticks), dtype=np.int64)
    k_of_row[order] = np.repeat(np.arange(len(uniq)), np.diff(bounds))
    done = np.flatnonzero(checked)
    use = np.where(checked[k_of_row], k_of_row, done[np.clip(np.searchsorted(done, k_of_row, side="right") - 1, 0, None)])
    return masks[use, slot.astype(np.int64)], smoky[use, slot.astype(np.int64)]


# ---------------------------------------------------------------- the sidecar


SCHEMA = pa.schema([
    ("time", pa.float64()), ("tick", pa.int32()), ("part", pa.int8()), ("round", pa.int16()),
    ("slot", pa.int8()), ("steamid", pa.dictionary(pa.int32(), pa.string())),
    ("x", pa.float32()), ("y", pa.float32()), ("z", pa.float32()),
    ("pitch", pa.float32()), ("yaw", pa.float32()), ("cmdOff", pa.float32()),
    ("mouseX", pa.int16()), ("mouseY", pa.int16()),
    ("duck", pa.float32()), ("vx", pa.float32()), ("vy", pa.float32()), ("vz", pa.float32()),
    ("flash", pa.float32()), ("punchPitch", pa.float32()), ("punchYaw", pa.float32()),
    ("zoom", pa.int8()), ("airborne", pa.int8()), ("weapon", pa.dictionary(pa.int32(), pa.string())),
    ("sees", pa.int32()), ("smoked", pa.int32()),
])
#: Floats stored split by byte (they compress much better so); the viewer reads Snappy only.
SPLIT = [f.name for f in SCHEMA if pa.types.is_floating(f.type)]


def cmd_off(df: pd.DataFrame) -> np.ndarray:
    """Degrees between the view the player's command asked for and the view the server gave them (0 in legit
    play; fake angles, anti-aim, desync show up here)."""
    dp = df["cmdPitch"].to_numpy(dtype=float) - df["pitch"].to_numpy(dtype=float)
    dy = (df["cmdYaw"].to_numpy(dtype=float) - df["yaw"].to_numpy(dtype=float) + 180.0) % 360.0 - 180.0
    out = np.hypot(dp, dy)
    return np.where(np.isfinite(out), out, 0.0)


def _read_ticks(path: str) -> pd.DataFrame:
    from demoparser2 import DemoParser

    df = DemoParser(str(path)).parse_ticks(list(FIELDS))
    return df.rename(columns=FIELDS)


def _punch(v) -> tuple[float, float]:
    try:
        return float(v[0]), float(v[1])
    except (TypeError, IndexError, ValueError):
        return 0.0, 0.0


def players_of(match) -> list[dict]:
    """The match's players in slot order: by steamid."""
    ids = sorted(s for s, p in match.players.items() if s and s != "0")
    return [{"slot": k, "steamid": s, "name": match.players[s].get("name", "")} for k, s in enumerate(ids[:SLOTS])]


def view_frame(match, ticks: dict[int, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Every living player's every tick in a round, all parts, on the table's clock; `sees` not yet set."""
    from .keep import _times

    slots = {p["steamid"]: p["slot"] for p in players_of(match)}
    # A round from freeze time's end until a few seconds after it was decided: the survivors are then placed back
    # at the spawns for the next one, which is no move of theirs.
    windows = np.array([(r.start, min(r.until, r.end + AFTER), r.number) for r in match.rounds],
                       dtype=np.float64).reshape(-1, 3)
    frames = []
    for k, source in enumerate(match.sources):
        raw = source[0]
        if ticks is not None and k in ticks:
            df = ticks[k]
        elif Path(raw.path).is_file():
            try:
                df = _read_ticks(raw.path)
            except Exception:  # noqa: BLE001 - a file the parser cannot read per tick has no view rows
                continue
        else:
            continue
        df = df[(df["alive"] == True) & df["team"].isin([2, 3])].copy()  # noqa: E712
        df["steamid"] = df["steamid"].astype(str)
        df = df[df["steamid"].isin(slots)]
        if not len(df):
            continue
        df["time"] = _times(source, df["tick"].to_numpy())
        t = df["time"].to_numpy()
        idx = np.searchsorted(windows[:, 0], t, side="right") - 1
        ok = (idx >= 0) & (t <= windows[np.clip(idx, 0, None), 1])
        df = df[ok].copy()
        df["round"] = windows[idx[ok], 2].astype(np.int16)
        df["part"] = k
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=SCHEMA.names)
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["time", "steamid"], kind="stable").drop_duplicates(["part", "tick", "steamid"])
    df["slot"] = df["steamid"].map(slots).astype(np.int8)
    p = np.array([_punch(v) for v in df["punch"].to_numpy()], dtype=np.float64).reshape(-1, 2)
    df["punchPitch"], df["punchYaw"] = p[:, 0], p[:, 1]
    df["cmdOff"] = cmd_off(df)
    return df.reset_index(drop=True)


def view_table(match, levels: str | Path | None = None, ticks: dict[int, pd.DataFrame] | None = None,
               occluder: Occluder | None = None) -> pa.Table:
    """The `view` sidecar of a match."""
    df = view_frame(match, ticks)
    occ = occluder if occluder is not None else occluder_for(match.map, levels)
    smokes = smokes_of(match.rows) if len(match.rows) else np.zeros((0, 6))
    clears = _he_clears(match.rows, smokes) if len(smokes) else []
    if len(df) and (occ is not None):
        # One tick numbering across parts: a part's ticks after the last one's.
        gtick = df["tick"].to_numpy(dtype=np.int64) + df["part"].to_numpy(dtype=np.int64) * 10_000_000
        pos = df[["x", "y", "z"]].to_numpy(dtype=np.float64)
        sees, smoky = sight_masks(gtick, df["slot"].to_numpy(dtype=np.int64), df["team"].to_numpy(dtype=np.int64), pos,
                           df["duck"].to_numpy(dtype=np.float64), df["time"].to_numpy(dtype=np.float64), occ, smokes, clears)
        sees_arr = pa.array(sees.astype(np.int64) & 0x7FFFFFFF, type=pa.int64()).cast(pa.int32())
        smoky_arr = pa.array(smoky.astype(np.int64) & 0x7FFFFFFF, type=pa.int64()).cast(pa.int32())
    else:
        sees_arr = pa.nulls(len(df), pa.int32())
        smoky_arr = pa.nulls(len(df), pa.int32())
    cols = []
    for f in SCHEMA:
        if f.name in ("sees", "smoked"):
            cols.append(sees_arr if f.name == "sees" else smoky_arr)
            continue
        v = df[f.name] if f.name in df else pd.Series([None] * len(df))
        if pa.types.is_dictionary(f.type):
            cols.append(pa.array(v.fillna("").astype(str).to_numpy(), type=pa.string()).dictionary_encode())
        elif pa.types.is_integer(f.type):
            vals = pd.to_numeric(v, errors="coerce").to_numpy(dtype=float)
            mask = ~np.isfinite(vals)
            cols.append(pa.array(np.where(mask, 0, vals).astype(np.int64), mask=mask).cast(f.type))
        else:
            cols.append(pa.array(pd.to_numeric(v, errors="coerce").to_numpy(dtype=float), from_pandas=True).cast(f.type))
    meta = {
        "version": 1,
        "kind": "cs2-view",
        "tickrate": TICKRATE,
        "match": match.name,
        "map": match.map,
        "players": players_of(match),
        "sight": {
            "level": occ is not None, "voxel": VOXEL, "every": EVERY, "ends": NEAR, "eye": [EYE, EYE_DUCKED],
            "points": ["head", "chest", "chest-left", "chest-right", "knee"], "seeThrough": sorted(SEE_THROUGH),
            "smoke": {"radii": SMOKE_RADII.tolist(), "core": SMOKE_CORE, "chord": SMOKE_CHORD,
                      "bloom": SMOKE_BLOOM, "fade": SMOKE_FADE},
        },
        "smokes": [[round(float(v), 3) for v in s[:5]] for s in smokes],
    }
    schema = SCHEMA.with_metadata({"heat3d": json.dumps(meta)})
    return pa.Table.from_arrays(cols, schema=schema)


def write_view(match, path: str | Path, levels: str | Path | None = None, **kw) -> int:
    """Write `<match>.view.parquet`; returns its rows."""
    t = view_table(match, levels, **kw)
    pq.write_table(t, path, compression="snappy", row_group_size=262_144, use_dictionary=["steamid", "weapon"],
                   column_encoding={**{c: "BYTE_STREAM_SPLIT" for c in SPLIT}, "tick": "DELTA_BINARY_PACKED"})
    return len(t)
