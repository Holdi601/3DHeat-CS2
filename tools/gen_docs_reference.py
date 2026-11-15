"""
Writes docs/cli-reference.md from the code, so the reference cannot drift:
every command's `--help`, and the columns of the files `demos` writes, read from
a conversion of the tests' synthetic demo.

    python tools/gen_docs_reference.py          (from the repository's root)
    python tools/gen_docs_reference.py --check  (exit 1 when the page is out of date; writes nothing)
"""

from __future__ import annotations

import concurrent.futures as cf
import contextlib
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "cli-reference.md"
PROG = "python -m heat3d_cs2"


def help_text(args: list[str]) -> str:
    from heat3d_cs2 import cli

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.suppress(SystemExit):
        cli.main(args + ["--help"])
    return buf.getvalue().rstrip()


def columns() -> tuple[dict[str, list[tuple[str, str]]], list[str]]:
    """The columns of every Parquet file, and the match document's top-level keys, of the synthetic match."""
    import pyarrow.parquet as pq

    from heat3d_cs2 import cli, demo
    from tests import fixtures

    demo.read_part = lambda path, *a, **k: fixtures.two_rounds()
    cli.ProcessPoolExecutor = cf.ThreadPoolExecutor
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "demos"
        src.mkdir()
        (src / "alpha-vs-bravo-m1.dem").write_bytes(b"")
        with contextlib.redirect_stdout(io.StringIO()):
            cli.main(["demos", str(src), "-o", str(Path(tmp) / "out"), "--loose", "--jobs", "1"])
        tables = {}
        for p in sorted((Path(tmp) / "out").rglob("*.parquet"), key=lambda p: (p.name.count("."), p.name)):
            role = p.name.split(".")[1] if p.name.count(".") > 1 else "table"
            tables[role] = [(f.name, str(f.type)) for f in pq.read_schema(p)]
        doc = next((Path(tmp) / "out").rglob("*.match.json"))
        keys = list(json.loads(doc.read_text(encoding="utf-8")))
    return tables, keys


def build() -> str:
    top = help_text([])
    verbs = re.search(r"\{([a-z0-9_,-]+)\}", top).group(1).split(",")
    out = ["---", "title: Reference", "nav_order: 16", "---", "", "# Command and column reference", "",
           "Generated from the code by `tools/gen_docs_reference.py`. The other pages explain each",
           "command step by step; this one lists everything exactly as the program has it.", "",
           f"## `{PROG}`", "", "```text", top, "```", ""]
    for v in verbs:
        out += [f"## `{v}`", "", "```text", help_text([v]), "```", ""]
    tables, keys = columns()
    out += ["## Columns of the files `demos` writes", "",
            "Read from a conversion of the tests' synthetic demo. What each column means:",
            "[The heatmap table](output-table.md) and [One file a match](output-container.md).", ""]
    for role, cols in tables.items():
        name = "`<match>.parquet` (role `table`)" if role == "table" else f"`<match>.{role}.parquet` (role `{role}`)"
        out += [f"### {name}", "", "| Column | Type |", "|---|---|"]
        out += [f"| `{c}` | {t} |" for c, t in cols]
        out.append("")
    out += ["### `<match>.match.json` (role `match`)", "",
            "Top-level keys: " + ", ".join(f"`{k}`" for k in keys) + ". Field by field: "
            "[The match document](output-match-json.md).", ""]
    return "\n".join(out)


def main() -> int:
    os.environ.setdefault("HEAT3D_NO_UPDATE", "1")
    os.environ["COLUMNS"] = "88"  # argparse wraps to the terminal; the page must not depend on it
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    text = build()
    if "--check" in sys.argv[1:]:
        old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if old != text:
            print(f"out of date: {OUT.relative_to(ROOT)}")
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
