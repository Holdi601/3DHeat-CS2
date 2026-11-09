"""
A match packed into one `.3dheat` file: the loose files come back byte for
byte, Parquet stored (a byte range the viewer reads in place), JSON deflated.
"""

import json
import zipfile

import pyarrow as pa
import pyarrow.parquet as pq

from heat3d_cs2.cli import written
from heat3d_cs2.container import members_of, pack


def _match(folder):
    folder.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"x": list(range(1000))}), folder / "m.parquet")
    pq.write_table(pa.table({"type": ["a", "b"]}), folder / "m.events.parquet")
    (folder / "m.match.json").write_text(json.dumps({"format": "heat3d-cs2-match", "match": "m"}), encoding="utf-8")
    (folder / "other.parquet").write_bytes(b"not this match")
    return {p.name: p.read_bytes() for p in folder.iterdir() if p.name.startswith("m.")}


def test_a_match_packs_into_one_file_and_comes_back_whole(tmp_path):
    loose = _match(tmp_path)
    assert [r for r, _ in members_of(tmp_path / "m.parquet")] == ["table", "match", "events"]
    out = pack(tmp_path / "m.parquet", {"game": "cs2", "match": "m"})
    assert sorted(p.name for p in tmp_path.iterdir()) == ["m.3dheat", "other.parquet"]
    with zipfile.ZipFile(out) as z:
        infos = z.infolist()
        assert infos[0].filename == "manifest.json"
        manifest = json.loads(z.read("manifest.json"))
        assert manifest["format"] == "3dheat" and manifest["roles"]["table"] == "m.parquet"
        assert manifest["members"][0]["rows"] == 1000
        for i in infos[1:]:
            assert i.compress_type == (zipfile.ZIP_DEFLATED if i.filename.endswith(".json") else zipfile.ZIP_STORED)
            assert z.read(i) == loose[i.filename]
    assert written(tmp_path) == {"m"}  # a container counts as written


def test_loose_files_stay_when_asked(tmp_path):
    _match(tmp_path)
    pack(tmp_path / "m.parquet", {}, delete_loose=False)
    assert (tmp_path / "m.parquet").exists() and (tmp_path / "m.3dheat").exists()
