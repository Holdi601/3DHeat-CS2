"""
Where on the body a bullet struck: the shot's ray traced to the victim.

A hurt event names the body part hit (`hitgroup`), not the point. The point
is found here from the shot itself: the game's own account of the bullets
fired that tick by the attacker (`fire_bullets`: the eye position the shot
left from and its angles), else the attacker's eye and view angles at the
hurt. The ray is traced against a body of simple shapes posed where the
victim stood - facing their yaw, lowered as far as they were crouched - and
the point taken where it first enters the shape of the part the game says
was hit. Where it passes that part by (spread, recoil, the victim moving
within the tick), the point is the part's surface nearest the ray: the part
is the game's word, the ray only says where on it.

The shot's angles are where the shooter aimed; the bullet left them by the
weapon's spread, which the game draws from the shot's own seed (`fire_bullets`
`seed`, `inaccuracy`, `spread`) with Valve's uniform random stream - the same
draw is made here, so the line is the bullet's own. A shotgun's pellet is not
known, so only the shot's inaccuracy is applied to it.

The body is drawn from a player's standing proportions in game units (72
tall, the eye at 64), not from the game's hitboxes. The point is written in
the victim's own frame in metres - x forward, y up from the feet, z to the
victim's right - with the shot's direction in the same frame, as the
viewer's vehicle heatmap reads them (`hitLocalX/Y/Z`, `hitDirX/Y/Z`).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: Game units to metres.
METRES = 0.0254
#: Standing eye height and how far a full crouch lowers the body (game units).
EYE = 64.0
CROUCH_DROP = 18.0
HIP = 36.0

#: Each part as capsules (end, end, radius) in the victim's frame, standing, in game units:
#: x forward, y up from the feet, z to the right.
BODY: dict[str, list[tuple[tuple[float, float, float], tuple[float, float, float], float]]] = {
    "head": [((1.0, 63.5, 0.0), (1.5, 67.5, 0.0), 4.6)],
    "neck": [((0.0, 57.5, 0.0), (0.5, 61.0, 0.0), 3.3)],
    "chest": [((0.0, 46.5, -3.5), (0.0, 55.5, -3.5), 5.5), ((0.0, 46.5, 3.5), (0.0, 55.5, 3.5), 5.5)],
    "stomach": [((0.0, 37.0, -2.5), (0.0, 45.5, -2.5), 5.5), ((0.0, 37.0, 2.5), (0.0, 45.5, 2.5), 5.5)],
    "left_arm": [((0.0, 55.0, -9.5), (6.0, 46.0, -10.0), 2.8), ((6.0, 46.0, -10.0), (16.0, 50.5, -3.0), 2.4)],
    "right_arm": [((0.0, 55.0, 9.5), (5.0, 45.5, 9.0), 2.8), ((5.0, 45.5, 9.0), (12.0, 51.5, 2.0), 2.4)],
    "left_leg": [((0.0, 36.0, -4.5), (1.0, 18.0, -4.8), 4.6), ((1.0, 18.0, -4.8), (0.0, 2.0, -4.8), 3.4)],
    "right_leg": [((0.0, 36.0, 4.5), (1.0, 18.0, 4.8), 4.6), ((1.0, 18.0, 4.8), (0.0, 2.0, 4.8), 3.4)],
}
#: The numeric columns a hurt row gains (and `hitFrom`, text).
COLUMNS = ["hitLocalX", "hitLocalY", "hitLocalZ", "hitDirX", "hitDirY", "hitDirZ", "hitMiss"]

#: Hitgroups that are not a place on the body (a grenade, fire, a fall), and names the game uses for the same part.
NOT_A_PLACE = {"", "generic", "gear", "special", "invalid"}
ALIAS = {"leftarm": "left_arm", "rightarm": "right_arm", "leftleg": "left_leg", "rightleg": "right_leg"}


def posed(point: tuple[float, float, float], duck: float) -> np.ndarray:
    """A body point lowered for a crouch of `duck` (0 standing, 1 crouched): the legs fold, the body above drops."""
    x, y, z = point
    if y >= HIP:
        y -= CROUCH_DROP * duck
    else:
        # The legs fold to half their height; the knee goes forward as they do.
        y *= 1.0 - 0.5 * duck
        x += 7.0 * duck * np.sin(np.pi * point[1] / HIP)
    return np.array([x, y, z])


def frame(yaw_deg: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A player's forward, up and right in the game's axes (z up; yaw counter-clockwise from +x)."""
    yaw = np.radians(yaw_deg)
    f = np.array([np.cos(yaw), np.sin(yaw), 0.0])
    u = np.array([0.0, 0.0, 1.0])
    r = np.array([np.sin(yaw), -np.cos(yaw), 0.0])
    return f, u, r


def direction(pitch_deg: float, yaw_deg: float) -> np.ndarray:
    """A view direction in the game's axes (pitch down is positive)."""
    p, y = np.radians(pitch_deg), np.radians(yaw_deg)
    return np.array([np.cos(p) * np.cos(y), np.cos(p) * np.sin(y), -np.sin(p)])


class Stream:
    """
    Valve's uniform random stream (a Park-Miller generator with a Bays-Durham
    shuffle, Numerical Recipes' ran1): seeded per shot, its first draws place
    the bullet within the weapon's spread.
    """

    A, M, Q, R, TABLE = 16807, 2147483647, 127773, 2836, 32
    DIV = 1 + (M - 1) // TABLE

    def __init__(self, seed: int):
        seed = int(seed) & 0xFFFFFFFF
        seed = seed - (1 << 32) if seed >= 1 << 31 else seed
        self.state = seed if seed < 0 else -seed
        self.last = 0
        self.table = [0] * self.TABLE

    def _step(self) -> None:
        k = self.state // self.Q
        self.state = self.A * (self.state - k * self.Q) - self.R * k
        if self.state < 0:
            self.state += self.M

    def number(self) -> int:
        if self.state <= 0 or not self.last:
            self.state = 1 if -self.state < 1 else -self.state
            for j in range(self.TABLE + 7, -1, -1):
                self._step()
                if j < self.TABLE:
                    self.table[j] = self.state
            self.last = self.table[0]
        self._step()
        j = self.last // self.DIV
        if not 0 <= j < self.TABLE:
            j = (j % self.TABLE) & 0x7FFFFFFF
        self.last = self.table[j]
        self.table[j] = self.state
        return self.last

    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        return min(self.number() / self.M, 1.0 - 1.2e-7) * (high - low) + low


#: Weapons that fire pellets (the game's item numbers): which pellet struck is not known.
PELLETS = {25, 27, 29, 35}


def spread(seed: float, inaccuracy: float, spread: float, item: float = np.nan) -> tuple[float, float]:
    """How far the bullet left the aim (right, up; tangents) for a shot's seed, inaccuracy and spread."""
    if not (np.isfinite(seed) and np.isfinite(inaccuracy)):
        return 0.0, 0.0
    s = Stream(int(seed) + 1)
    r0, a0, r1, a1 = s.uniform(), s.uniform(0, 2 * np.pi), s.uniform(), s.uniform(0, 2 * np.pi)
    r0 *= inaccuracy
    r1 = 0.0 if (np.isfinite(item) and int(item) in PELLETS) or not np.isfinite(spread) else r1 * spread
    return float(np.cos(a0) * r0 + np.cos(a1) * r1), float(np.sin(a0) * r0 + np.sin(a1) * r1)


def bullet(pitch_deg: float, yaw_deg: float, right: float = 0.0, up: float = 0.0) -> np.ndarray:
    """The aim's direction moved by a spread (tangents right and up), as a unit vector."""
    p, y = np.radians(pitch_deg), np.radians(yaw_deg)
    d = direction(pitch_deg, yaw_deg)
    d = d + right * np.array([np.sin(y), -np.cos(y), 0.0]) + up * np.array([np.sin(p) * np.cos(y), np.sin(p) * np.sin(y), np.cos(p)])
    return d / np.linalg.norm(d)


def _segment_distance(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """For points p (n x 3): the distance to the segment a-b, and the nearest point on it."""
    ab = b - a
    denom = float(ab @ ab) or 1e-9
    t = np.clip(((p - a) @ ab) / denom, 0.0, 1.0)
    near = a + t[:, None] * ab
    return np.linalg.norm(p - near, axis=1), near


def trace(origin: np.ndarray, d: np.ndarray, capsules: list[tuple[np.ndarray, np.ndarray, float]], step: float = 0.2) -> tuple[np.ndarray, float]:
    """
    Where the ray from `origin` along unit `d` first enters the capsules
    (local game units), and 0; where it misses them, the capsules' surface
    point nearest the ray and how far the ray passed it by.
    """
    # March the stretch of the ray that passes the body: from 60 units before its nearest approach to 60 after.
    centre = np.mean([(a + b) / 2 for a, b, _ in capsules], axis=0)
    t0 = float((centre - origin) @ d)
    ts = np.arange(max(0.0, t0 - 60.0), t0 + 60.0, step)
    if not len(ts):
        ts = np.array([0.0])
    pts = origin + ts[:, None] * d
    best_gap = np.full(len(ts), np.inf)
    best_near = np.zeros((len(ts), 3))
    best_r = np.zeros(len(ts))
    for a, b, r in capsules:
        dist, near = _segment_distance(pts, a, b)
        gap = dist - r
        better = gap < best_gap
        best_gap[better], best_near[better], best_r[better] = gap[better], near[better], r
    inside = np.nonzero(best_gap <= 0)[0]
    if len(inside):
        return pts[inside[0]], 0.0
    i = int(np.argmin(best_gap))
    out = pts[i] - best_near[i]
    n = np.linalg.norm(out) or 1.0
    return best_near[i] + out / n * best_r[i], float(best_gap[i])


def hit_points(hurts: pd.DataFrame, bullets: pd.DataFrame | None) -> dict[str, np.ndarray]:
    """
    For each hurt row: the point struck in the victim's frame (m), the shot's
    direction in that frame, how far the traced ray passed the part named
    (m, 0 where it went through it) and where the ray came from ("bullet":
    the game's account of the shot; "aim": the attacker's eye and view).
    NaN and "" where the hit is no place on the body or nothing says where
    the shot came from. Besides, in the game's frame and units, for the
    wallbang trace (wallbang.py; not written to the table): where the shot
    left (`_fromX/Y/Z`), the point on its line as far as the point struck
    (`_atX/Y/Z`) and the weapon by the game's item number (`_weapon`, from
    the shot).
    """
    n = len(hurts)
    out = {k: np.full(n, np.nan) for k in ("hitLocalX", "hitLocalY", "hitLocalZ", "hitDirX", "hitDirY", "hitDirZ", "hitMiss",
                                           "_fromX", "_fromY", "_fromZ", "_atX", "_atY", "_atZ")}
    source = np.full(n, "", dtype=object)
    out["_weapon"] = np.full(n, np.nan)
    shots: dict[tuple[int, str], tuple[np.ndarray, np.ndarray, float]] = {}
    if bullets is not None and len(bullets) and {"origin_x", "angles_x", "angles_y", "tick", "user_steamid"} <= set(bullets.columns):

        def shot_col(name: str) -> np.ndarray:
            return pd.to_numeric(bullets[name], errors="coerce").to_numpy(dtype=float) if name in bullets else np.full(len(bullets), np.nan)

        seed, inacc, spr, item = shot_col("seed"), shot_col("inaccuracy"), shot_col("spread"), shot_col("item_def_index")
        for k, (tick, sid, ox, oy, oz, ax, ay) in enumerate(zip(bullets["tick"], bullets["user_steamid"].astype(str), bullets["origin_x"],
                                                                 bullets["origin_y"], bullets["origin_z"], bullets["angles_x"], bullets["angles_y"])):
            if (int(tick), sid) not in shots:
                d = bullet(float(ax), float(ay), *spread(seed[k], inacc[k], spr[k], item[k]))
                shots[(int(tick), sid)] = (np.array([ox, oy, oz], dtype=float), d, item[k])

    def col(name: str) -> np.ndarray:
        return pd.to_numeric(hurts[name], errors="coerce").to_numpy(dtype=float) if name in hurts else np.full(n, np.nan)

    groups = hurts["hitgroup"].fillna("").astype(str).str.lower().to_numpy() if "hitgroup" in hurts else np.full(n, "")
    ticks = col("tick")
    attackers = hurts["attacker_steamid"].fillna("").astype(str).to_numpy() if "attacker_steamid" in hurts else np.full(n, "")
    vx, vy, vz, vyaw, vduck = col("user_X"), col("user_Y"), col("user_Z"), col("user_yaw"), col("user_duck_amount")
    ax, ay, az, apitch, ayaw, aduck = col("attacker_X"), col("attacker_Y"), col("attacker_Z"), col("attacker_pitch"), col("attacker_yaw"), col("attacker_duck_amount")
    for i in range(n):
        part = ALIAS.get(groups[i].replace(" ", "_"), groups[i].replace(" ", "_"))
        if part in NOT_A_PLACE or part not in BODY or not np.isfinite(vx[i]) or not np.isfinite(vyaw[i]):
            continue
        shot = shots.get((int(ticks[i]), attackers[i])) if np.isfinite(ticks[i]) else None
        if shot is not None:
            origin, d, source[i] = shot[0], shot[1], "bullet"
            out["_weapon"][i] = shot[2]
        elif np.isfinite(ax[i]) and np.isfinite(apitch[i]) and np.isfinite(ayaw[i]):
            eye = EYE - CROUCH_DROP * (aduck[i] if np.isfinite(aduck[i]) else 0.0)
            origin, d, source[i] = np.array([ax[i], ay[i], az[i] + eye]), direction(apitch[i], ayaw[i]), "aim"
        else:
            continue
        f, u, r = frame(vyaw[i])
        rel = origin - np.array([vx[i], vy[i], vz[i]])
        lo = np.array([rel @ f, rel @ u, rel @ r])
        ld = np.array([d @ f, d @ u, d @ r])
        duck = vduck[i] if np.isfinite(vduck[i]) else 0.0
        capsules = [(posed(a, duck), posed(b, duck), rad) for a, b, rad in BODY[part]]
        p, miss = trace(lo, ld, capsules)
        out["hitLocalX"][i], out["hitLocalY"][i], out["hitLocalZ"][i] = p * METRES
        out["hitDirX"][i], out["hitDirY"][i], out["hitDirZ"][i] = ld
        out["hitMiss"][i] = miss * METRES
        # The shot's own line, as far as the point struck: the shot's direction is exact, the victim's place is the
        # server's at the tick (lag compensation struck them where the shooter saw them).
        struck = np.array([vx[i], vy[i], vz[i]]) + p[0] * f + p[1] * u + p[2] * r
        at = origin + d * max(0.0, float((struck - origin) @ d))
        out["_fromX"][i], out["_fromY"][i], out["_fromZ"][i] = origin
        out["_atX"][i], out["_atY"][i], out["_atZ"][i] = at
    return {**out, "hitFrom": source}
