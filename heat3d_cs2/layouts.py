"""
A CS2 map's bomb sites, buy zones, hostage spots and spawn points, read from
the map's own `.vpk` in the installed game, as `<map>.layouts.json` beside the
map's `.glb` (the 3DHeat layouts format, the same frame as `map` writes).

The map's entities (`maps/<map>/entities/default_ents.vents_c`) are written as
text by Source2Viewer's command line; each bomb site and buy zone is a brush
whose shape is its own small model, exported the same way and reduced to its
outline seen from above (a convex hull) and its floor and top heights.

Layouts: `competitive` (the standard spawns) and, where the map has its own
spawns for it, `wingman`; `hostage` on a hostage map. Teams: 1 is T, 2 is CT.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from . import glb
from .mapexport import find_source2viewer, find_vpk, to_game, to_viewer

FORMAT = "3dheat-layouts"
TEAMS = {"1": "T", "2": "CT"}
#: The game's team numbers -> the layout's.
TEAM_OF = {2: 1, 3: 2}
RECORD = re.compile(r"^====\d+====\s*$")
VALUE = re.compile(r"^(\S+)\s+(.*)$")


def parse_entities(text: str) -> list[dict]:
    """Source2Viewer's entity dump: one `key value` a line, a `====N====` line before each entity."""
    out: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        if RECORD.match(line):
            cur = {}
            out.append(cur)
            continue
        if cur is None or not line.strip() or line.startswith("@"):
            continue
        m = VALUE.match(line.strip())
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                cur[key] = [float(v) for v in raw[1:-1].split(",")]
                continue
            except ValueError:
                pass
        if raw.startswith('"') and raw.endswith('"'):
            cur[key] = raw[1:-1]
        elif raw.startswith("resource_name:"):
            cur[key] = raw.split(":", 1)[1].strip('"')
        else:
            try:
                cur[key] = float(raw) if "." in raw else int(raw)
            except ValueError:
                cur[key] = {"true": True, "false": False}.get(raw, raw)
    return out


def _hull(points: np.ndarray) -> np.ndarray:
    """The convex hull of (x, z) points, counter-clockwise (monotone chain)."""
    pts = sorted(set(map(tuple, np.round(points, 2))))
    if len(pts) < 3:
        return np.asarray(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.asarray(lower[:-1] + upper[:-1])


def _yaw(angles) -> float:
    """The game's yaw (degrees about +z from +x) as a heading in the viewer's frame (from +z towards +x)."""
    if not isinstance(angles, list) or len(angles) < 2:
        return 0.0
    # The game's +x is the viewer's +x and its +y the viewer's -z.
    return round((90.0 + float(angles[1])) % 360.0, 1)


class Brushes:
    """Brush models of the map exported once, as viewer-frame points."""

    def __init__(self, tool: Path, vpk: Path):
        self.tool, self.vpk = tool, vpk
        self.tmp = tempfile.TemporaryDirectory()

    def points(self, model: str, origin) -> np.ndarray | None:
        name = model if model.endswith("_c") else model + "_c"
        out = Path(self.tmp.name) / Path(name).stem
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(self.tool), "-i", str(self.vpk), "-d", "-f", name, "--gltf_export_format", "glb", "-o", str(out)],
                       capture_output=True, text=True, cwd=self.tmp.name)
        found = sorted(out.rglob("*.glb"), key=lambda f: f.stat().st_size, reverse=True)
        for f in found:
            try:
                doc, blob = glb.read(f)
                meshes = glb.meshes(doc, blob)
            except (ValueError, KeyError, OSError):
                continue
            pts = [m[1] for m in meshes if len(m[1])]
            if pts:
                game = to_game(np.concatenate(pts))
                if isinstance(origin, list) and len(origin) == 3:
                    game = game + np.asarray(origin)
                return to_viewer(game)
        return None

    def close(self):
        self.tmp.cleanup()


def _area(kind: str, team: int | None, pts: np.ndarray, **extra) -> dict:
    hull = _hull(pts[:, [0, 2]])
    floor = float(pts[:, 1].min())
    rec = {
        "type": kind,
        "team": team,
        "shape": "outline",
        "position": [round(float(v), 1) for v in pts.mean(axis=0)],
        "points": [[round(float(x), 1), round(floor, 1), round(float(z), 1)] for x, z in hull],
        "height": round(float(pts[:, 1].max()) - floor, 1),
    }
    rec.update(extra)
    return rec


def build_layouts(name: str, game: str | None = None, source2viewer: str | None = None, version: str = "") -> dict:
    vpk = find_vpk(name, game)
    tool = find_source2viewer(source2viewer)
    stem = vpk.stem
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([str(tool), "-i", str(vpk), "-d", "-f", f"maps/{stem}/entities/default_ents.vents_c", "-o", tmp],
                       capture_output=True, text=True, cwd=tmp)
        found = list(Path(tmp).rglob("default_ents.vents"))
        if not found:
            raise RuntimeError(f"Source2Viewer did not write {stem}'s entities")
        ents = parse_entities(found[0].read_text(encoding="utf-8", errors="replace"))
    brushes = Brushes(tool, vpk)
    try:
        objectives: list[dict] = []
        hostage: list[dict] = []
        for e in ents:
            cls = e.get("classname")
            if cls == "func_bomb_target" and e.get("model"):
                pts = brushes.points(e["model"], e.get("origin"))
                if pts is None:
                    continue
                letter = "AB"[int(e.get("bomb_site_designation", 0) or 0) % 2]
                objectives.append(_area("bomb_site", None, pts, name=f"Bombsite {letter}", site=letter, letter=letter))
            elif cls == "func_buyzone" and e.get("model"):
                pts = brushes.points(e["model"], e.get("origin"))
                if pts is not None:
                    objectives.append(_area("buy_zone", TEAM_OF.get(int(e.get("teamnum", 0) or 0)), pts, name="Buy zone"))
            elif cls == "func_hostage_rescue" and e.get("model"):
                pts = brushes.points(e["model"], e.get("origin"))
                if pts is not None:
                    hostage.append(_area("rescue_zone", 2, pts, name="Rescue zone"))
            elif cls in ("info_hostage_spawn", "hostage_entity") and isinstance(e.get("origin"), list):
                p = to_viewer(np.asarray([e["origin"]], float))[0]
                hostage.append({"type": "objective", "kind": "hostage", "name": "Hostage", "team": None,
                                "position": [round(float(v), 1) for v in p]})
    finally:
        brushes.close()
    spawns: dict[str, list[dict]] = {}
    for e in ents:
        cls = e.get("classname")
        if cls not in ("info_player_terrorist", "info_player_counterterrorist") or not isinstance(e.get("origin"), list):
            continue
        if e.get("enabled") is False and "2v2" not in str(e.get("targetname", "")):
            continue
        tag = str(e.get("targetname", "")).lower()
        which = "wingman" if re.search(r"2v2|wingman", tag) else "competitive"
        p = to_viewer(np.asarray([e["origin"]], float))[0]
        spawns.setdefault(which, []).append({
            "type": "spawn",
            "team": 1 if cls == "info_player_terrorist" else 2,
            "position": [round(float(v), 1) for v in p],
            "heading": _yaw(e.get("angles")),
            "priority": e.get("priority"),
        })
    layouts = []
    defuse = [o for o in objectives if o["type"] in ("bomb_site", "buy_zone")]
    if any(o["type"] == "bomb_site" for o in objectives) or not hostage:
        layouts.append({"id": "competitive", "name": "Competitive", "mode": "competitive",
                        "aliases": ["defuse", "premier", "casual", "deathmatch"],
                        "objectives": defuse, "zones": [], "spawns": spawns.get("competitive", [])})
    if hostage:
        layouts.append({"id": "hostage", "name": "Hostage", "mode": "hostage", "aliases": ["competitive"],
                        "objectives": hostage + [o for o in objectives if o["type"] == "buy_zone"],
                        "zones": [], "spawns": spawns.get("competitive", [])})
    if spawns.get("wingman"):
        layouts.append({"id": "wingman", "name": "Wingman", "mode": "wingman", "aliases": ["scrimcomp2v2"],
                        "objectives": defuse, "zones": [], "spawns": spawns["wingman"]})
    return {
        "format": FORMAT,
        "version": 1,
        "game": "cs2",
        "level": stem,
        "source": f"heat3d-cs2 {version}".strip(),
        "units": "game units (inches)",
        "up": "y",
        "teams": TEAMS,
        "layouts": layouts,
    }


def write_layouts(doc: dict, out: str | Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")
    return out
