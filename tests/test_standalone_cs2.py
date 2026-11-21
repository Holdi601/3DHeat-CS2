"""The standalone spec on a synthetic CS2 install (tiny fake files, no game data)."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from heat3d_cs2 import cli, standalone_spec as S
from heat3d_cs2.app import entry


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "appdata"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "appdata"))
    monkeypatch.setenv("HEAT3D_LEVELS", str(tmp_path / "levels"))
    monkeypatch.setenv("HEAT3D_NO_UPDATE", "1")


def install(tmp_path: Path) -> Path:
    root = tmp_path / "Counter-Strike Global Offensive"
    csgo = root / "game" / "csgo"
    (csgo / "maps").mkdir(parents=True)
    (csgo / "pak01_dir.vpk").write_bytes(b"pak")
    (csgo / "gameinfo.gi").write_text("x")
    (csgo / "steam.inf").write_text("ClientVersion=99\nPatchVersion=1.2.3\n")
    for name in ("de_alpha", "cs_bravo", "lobby_mapveto", "de_alpha_vanity"):
        (csgo / "maps" / f"{name}.vpk").write_bytes(name.encode())
    return root


def fake_map(argv):
    """`heat3d_cs2 map|layouts` without Source2Viewer: writes a placeholder."""
    out = Path(argv[argv.index("-o") + 1])
    if argv[0] == "map":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"glb " + argv[1].encode())
    else:
        (out / f"{argv[1]}.layouts.json").write_text("{}")
    return 0


def spec_on(root: Path):
    g = dataclasses.replace(S.SPEC.games[0], find=lambda given: root)
    return dataclasses.replace(S.SPEC, games=[g])


def test_find_maps_build(tmp_path):
    root = install(tmp_path)
    assert S._find(str(root)) == root
    assert S._find(str(root / "game" / "csgo")) == root
    assert S._find(str(tmp_path / "nowhere")) is None
    assert [m.id for m in S._maps(root)] == ["cs_bravo", "de_alpha"]
    assert S._build(root) == "1.2.3-99"


def test_extract_writes_level_and_layouts(tmp_path, monkeypatch):
    root = install(tmp_path)
    monkeypatch.setattr(cli, "main", fake_map)
    m = S._maps(root)[1]
    out = tmp_path / "levels" / "cs2"
    files = S._extract(root, m, out, print)
    assert [f.name for f in files] == ["de_alpha.glb", "de_alpha.layouts.json"]


def test_install_that_gains_a_map(tmp_path, monkeypatch, capsys):
    root = install(tmp_path)
    monkeypatch.setattr(cli, "main", fake_map)
    spec = spec_on(root)

    def status():
        entry.main(spec, ["status", "--json"])
        g = json.loads(capsys.readouterr().out)["games"][0]
        return g, {m["id"]: m["state"] for m in g["maps"]}

    g, states = status()
    assert g["found"] and g["build"] == "1.2.3-99" and states == {"cs_bravo": "new", "de_alpha": "new"}
    assert entry.main(spec, ["extract", "--new", "--progress-json"]) == 0
    capsys.readouterr()
    man = json.loads((tmp_path / "levels" / "cs2" / ".heat3d-extract.json").read_text())
    assert man["entries"]["de_alpha"]["outputs"] == ["cs2/de_alpha.glb", "cs2/de_alpha.layouts.json"]
    assert "game/csgo/maps/de_alpha.vpk" in man["entries"]["de_alpha"]["sources"]

    # A game update brings a map: it is the only new one.
    (root / "game" / "csgo" / "maps" / "de_charlie.vpk").write_bytes(b"c")
    _, states = status()
    assert states == {"cs_bravo": "current", "de_alpha": "current", "de_charlie": "new"}


def test_tasks_and_tools():
    assert S.SPEC.version == (Path(__file__).resolve().parents[1] / "VERSION").read_text().strip()
    argv = S.SPEC.tasks[0].argv({"src": "in", "out": "o"}, Path("levels"))
    assert argv == ["heat3d_cs2", "demos", "in", "-o", "o"]
    assert entry.run_tool(S.SPEC, "heat3d_cs2", ["--help"]) == 0
