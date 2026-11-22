"""
The standalone app's description of this tool (app/spec.py): the CS2 install
it reads, the checks before a map can be exported, the install's maps (new ones
after a game update are found by app/manifest.py), and the demo conversion, the
catalogue and the model pack as tasks. `python -m heat3d_cs2.standalone_spec`
runs the app from a checkout; the release executables run the same.
"""

from __future__ import annotations

from pathlib import Path

from . import __version__
from .app import paths
from .app.spec import Check, GameSpec, Input, MapSource, Replays, Spec, Task, game_folders

#: The install's folder name in a Steam library.
STEAM_FOLDER = "Counter-Strike Global Offensive"
#: Map name prefixes of the game's modes (defuse, hostage, arms race, ...); the rest are menus and previews.
MAP_PREFIXES = ("de_", "cs_", "ar_", "gd_", "dz_")


def tool(argv: list[str] | None = None) -> int:
    """The tool's own command line (`python -m heat3d_cs2`), runnable from the frozen program too."""
    import multiprocessing

    # `demos` converts matches in worker processes; a frozen program starts them through itself.
    multiprocessing.freeze_support()
    from .cli import main

    return main(argv)


def _as_root(p: Path) -> Path | None:
    """The install's top folder from it, its `game` or its `game/csgo` folder."""
    for r in (p, p.parent, p.parent.parent):
        if (r / "game" / "csgo" / "pak01_dir.vpk").is_file():
            return r
    return None


def _find(given: str | None) -> Path | None:
    if given:
        return _as_root(Path(given).expanduser())
    from .mapexport import steam_libraries

    candidates = [*paths.steam_game_dirs(STEAM_FOLDER),
                  *(lib / "steamapps" / "common" / STEAM_FOLDER for lib in steam_libraries())]
    for c in candidates:
        root = _as_root(c)
        if root is not None:
            return root
    return None


def _maps(game: Path) -> list[MapSource]:
    folder = game / "game" / "csgo" / "maps"
    out = []
    for p in sorted(folder.glob("*.vpk")):
        stem = p.stem.lower()
        if stem.startswith(MAP_PREFIXES) and not stem.endswith(("_vanity", "_preview")):
            out.append(MapSource(p.stem, p.stem, [p]))
    return out


def _extract(game: Path, m: MapSource, out: Path, log) -> list[Path]:
    from . import cli

    out.mkdir(parents=True, exist_ok=True)
    level = out / f"{m.id}.glb"
    code = cli.main(["map", m.id, "-o", str(level), "--game", str(game)])
    if code != 0 or not level.is_file():
        raise RuntimeError(f"heat3d_cs2 map {m.id} exited {code}")
    # Bomb sites, buy zones and spawns beside it; a map without any is not an error.
    try:
        cli.main(["layouts", m.id, "-o", str(out), "--game", str(game)])
    except Exception as e:
        log(f"{m.id}: no layouts ({type(e).__name__}: {e})")
    return [p for p in (level, out / f"{m.id}.layouts.json") if p.is_file()]


def _build(game: Path) -> str | None:
    from .gear import game_build

    b = game_build(game / "game" / "csgo")
    return None if b == "unknown" else b


def _checks(found: dict, levels: Path) -> list[Check]:
    from .mapexport import SOURCE2VIEWER_URL, find_source2viewer

    try:
        s2v, ok = str(find_source2viewer()), True
    except FileNotFoundError:
        s2v, ok = (f"not found; maps, the catalogue and the model pack need it (demos do not). Download its "
                   f"command-line build for this system from {SOURCE2VIEWER_URL}, then put it on PATH or set "
                   "HEAT3D_SOURCE2VIEWER to it."), False
    return [Check("source2viewer", "Source2Viewer-CLI (reads the maps of your own CS2 install)", ok, s2v)]


def _game_args() -> list[str]:
    game = game_folders(SPEC).get("cs2")
    return ["--game", str(game)] if game else []


def _replays(levels: Path) -> str:
    """Where the game puts the matches downloaded in it: `game/csgo/replays` in the install."""
    game = game_folders(SPEC).get("cs2")
    folder = game / "game" / "csgo" / "replays" if game else None
    return str(folder) if folder and folder.is_dir() else ""

def _replay_info(path: Path) -> dict:
    """`info <replay> --json`: the header only (replay_info.py)."""
    from .replay_info import info

    return info(path)


SPEC = Spec(
    id="heat3d-cs2",
    name="3DHeat CS2",
    repo="Holdi601/3DHeat-CS2",
    version=__version__,
    tools={"heat3d_cs2": "heat3d_cs2.standalone_spec:tool"},
    default_tool="heat3d_cs2",
    description="Counter-Strike 2 demos and maps for the 3DHeat viewer",
    module="heat3d_cs2.standalone_spec",
    games=[GameSpec(
        key="cs2", label="Counter-Strike 2", find=_find, subdir="cs2", build=_build,
        maps=_maps, extract=_extract,
        existing_outputs=lambda out, m: [out / f"{m.id}.glb"],
        output_version="1.0.0",
        platforms=("windows-x64", "linux-x64"),
    )],
    checks=_checks,
    tasks=[
        Task(
            "demos", "Convert demos",
            [Input("src", "Folder with .dem demos", "folder", default=_replays),
             Input("out", "Where the matches go", "folder", default=lambda levels: str(paths.data_dir() / "matches" / "cs2"))],
            lambda v, levels: ["heat3d_cs2", "demos", v["src"], "-o", v["out"]],
            help="each match becomes one .3dheat file the viewer opens",
        ),
        Task(
            "catalog", "Weapons, items and agents catalogue", [],
            lambda v, levels: ["heat3d_cs2", "catalog", *_game_args()],
            help="catalog.json in the levels folder's cs2 folder, from your install",
        ),
        Task(
            "models", "Agents' and weapons' models (local model pack)", [],
            lambda v, levels: ["heat3d_cs2", "models", *_game_args()],
            help="a model pack in the levels folder, from your install; it stays on this machine",
        ),
    ],
    min_free_gb=2.0,
    replays=Replays("cs2", (".dem",), lambda r, out: ["heat3d_cs2", "demos", str(r), "-o", str(out)], info=_replay_info),
    notice="Not affiliated with or endorsed by Valve Corporation.",
)

if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import heat3d_update

    from .app.entry import main

    raise SystemExit(main(SPEC, apply_source=heat3d_update.apply))
