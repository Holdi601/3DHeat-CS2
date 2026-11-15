"""
Command line.

    python -m heat3d_cs2 demos <demo files or folders> -o <folder> [--every 8] [--jobs N] [--no-bulk] [--loose]
    python -m heat3d_cs2 map <map name | path to its .vpk> -o <map>.glb
    python -m heat3d_cs2 scoreboard <match.3dheat | match.json>

`demos` groups a match's parts by name (`...-p1.dem`, `...-p2.dem` are one
match) and writes `<map>/<match>.parquet` and `<map>/<match>.match.json` for
each, with the sidecars beside them (`<match>.events|props|strings|packets.parquet`),
skipping what is already written unless `--force`. Each match is then packed
into one file, `<map>/<match>.3dheat` (container.py); `--loose` keeps the
separate files instead.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

PART = re.compile(r"[-_]p(\d+)$", re.IGNORECASE)


def matches_in(paths: list[str]) -> dict[str, list[Path]]:
    """Match name -> its demo files, from files and folders (recursively)."""
    files: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            # `.dem` in any case, as for a file given by name.
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() == ".dem" and f.is_file())
        elif p.suffix.lower() == ".dem":
            files.append(p)
    out: dict[str, list[Path]] = {}
    for f in files:
        out.setdefault(PART.sub("", f.stem), []).append(f)
    return out


def _version() -> str | None:
    try:
        return (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return None


def convert(name: str, files: list[Path], folder: Path, every: int, bulk: bool = True, container: bool = True) -> str:
    from .demo import read_part
    from .match import build_match, chains
    from .output import write

    lines = []
    # Files named as one match can be two: each chain of parts is its own.
    raws_all = [read_part(f, every) for f in files]
    groups = chains(raws_all)
    if not groups:
        return f"{name}: no round in {len(files)} file(s) - nothing written"
    used = {id(r) for g in groups for r in g}
    alone = [Path(r.path).name for r in raws_all if id(r) not in used]
    if alone:
        # A file with no round of any match in it (a pause, warmup) is in no match, nor its sidecars.
        lines.append(f"{name}: no round in {', '.join(alone)} - not written")
    for k, raws in enumerate(groups):
        label = name if k == 0 else f"{name}-{chr(ord('a') + k)}"
        match = build_match(raws, label)
        if not match.rounds:
            lines.append(f"{label}: no complete round in {len(raws)} file(s) - nothing written")
            continue
        # A folder per map: a heatmap is of one map, so loading one folder is loading one map.
        data, doc = write(match, folder / (match.map or "unknown"), bulk=bulk)
        score = " ".join(f"{t} {s}" for t, s in match.rounds[-1].score.items()) if match.rounds else "no rounds"
        cut = f", {len(match.incomplete)} incomplete round(s) left out" if match.incomplete else ""
        late = f", recorded from round {match.rounds[0].number}" if match.rounds and match.rounds[0].number > 1 else ""
        check = json.loads(doc.read_text(encoding="utf-8"))["selfCheck"]["completeness"]
        if container:
            from .container import pack

            pack(data, {"game": "cs2", "source": "demo", "converter": {"name": "heat3d_cs2", "version": _version()},
                        "match": match.name, "map": match.map, "mode": None, "started": None})
        gone = [t for t, c in check["types"].items() if c["lost"]]
        lost = f", lost {check['lost']:,} ({', '.join(gone)})" if check["lost"] else ", lost 0"
        lines.append(f"{label}: {match.map}, {len(match.rounds)} rounds ({score}), {len(match.rows):,} rows{cut}{late}{lost}")
    return "\n".join(lines)


def written(folder: Path) -> set[str]:
    """
    The matches already written under `folder`: a table with its summary
    beside it. A run stopped between the two left the match unfinished.
    """
    if not folder.exists():
        return set()
    loose = {p.stem for p in folder.rglob("*.parquet") if p.with_name(p.stem + ".match.json").is_file()}
    # A container is written whole or not at all.
    return loose | {p.stem for p in folder.rglob("*.3dheat")}


def _demos(args) -> int:
    folder = Path(args.out)
    done = written(folder)
    todo = {n: f for n, f in matches_in(args.paths).items() if args.force or n not in done}
    if args.map:
        todo = {n: f for n, f in todo.items() if args.map.lower() in n.lower()}
    if not todo:
        print("nothing to do: no demos found, or every match already written (--force redoes them)")
        return 0
    jobs = max(1, min(args.jobs or max(1, (os.cpu_count() or 2) // 2), len(todo)))
    print(f"{len(todo)} match(es), {jobs} at a time")
    failed = 0
    with ProcessPoolExecutor(jobs) as pool:
        futures = {pool.submit(convert, n, f, folder, args.every, not args.no_bulk, not args.loose): n
                   for n, f in todo.items()}
        for done in as_completed(futures):
            try:
                print(done.result(), flush=True)
            except Exception as e:  # one bad demo does not stop the rest
                failed += 1
                print(f"{futures[done]}: failed - {e}", flush=True)
    return 1 if failed else 0


def _map(args) -> int:
    from .mapexport import export_map

    out = export_map(args.name, args.out, game=args.game, source2viewer=args.source2viewer)
    print(out)
    return 0


def _scoreboard(args) -> int:
    from .stats import scoreboard_text

    print(scoreboard_text(read_match_document(Path(args.match))))
    return 0


def read_match_document(path: Path) -> dict:
    """The match document of a `.3dheat` container, or of a loose `<match>.match.json`."""
    if path.suffix.lower() == ".3dheat":
        import zipfile

        with zipfile.ZipFile(path) as z:
            roles = json.loads(z.read("manifest.json")).get("roles", {}) if "manifest.json" in z.namelist() else {}
            names = [roles["match"]] if roles.get("match") else [n for n in z.namelist() if n.endswith(".match.json")]
            if not names:
                raise ValueError(f"{path}: no .match.json inside")
            return json.loads(z.read(names[0]).decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="heat3d_cs2", description="CS2 demos and maps for the 3DHeat viewer")
    sub = parser.add_subparsers(dest="verb", required=True)
    d = sub.add_parser("demos", help="demos -> one heatmap table and one match document per match")
    d.add_argument("paths", nargs="+", help="demo files or folders")
    d.add_argument("-o", "--out", required=True, help="folder to write into")
    d.add_argument("--every", type=int, default=8, help="sample players every N ticks (64 a second; default 8: 8 a second)")
    d.add_argument("--jobs", type=int, default=0, help="matches converted at once (default: half the cores)")
    d.add_argument("--map", help="only matches whose file name contains this text")
    d.add_argument("--force", action="store_true", help="rewrite matches already written")
    d.add_argument("--no-bulk", action="store_true",
                   help="leave the entity stream, the players' commands and the animation (over half a demo's size) "
                        "out of the packets sidecar; the self-check counts them lost")
    d.add_argument("--container", action="store_true", help="pack each match into one .3dheat file (the default)")
    d.add_argument("--loose", action="store_true",
                   help="keep each match as separate files (table, match.json, sidecars), not one .3dheat container")
    d.set_defaults(run=_demos)
    m = sub.add_parser("map", help="a map's collision geometry -> .glb in the demos' frame")
    m.add_argument("name", help="the map's name (like de_x) or the path to its .vpk")
    m.add_argument("-o", "--out", required=True, help=".glb to write")
    m.add_argument("--game", help="the CS2 install folder, when Steam does not know it")
    m.add_argument("--source2viewer", help="Source2Viewer-CLI executable, when it is not on PATH")
    m.set_defaults(run=_map)
    s = sub.add_parser("scoreboard", help="print a match's scoreboard")
    s.add_argument("match", help="<match>.3dheat, or <match>.match.json from --loose")
    s.set_defaults(run=_scoreboard)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
