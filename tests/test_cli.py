"""
Which demo files are read, and which matches are skipped as already written.
"""

from __future__ import annotations

from heat3d_cs2.cli import matches_in, written


def test_demos_in_folders_are_found_in_any_case(tmp_path):
    (tmp_path / "event").mkdir()
    for name in ("alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.DEM", "alpha-vs-bravo-m2.Dem", "notes.txt"):
        (tmp_path / "event" / name).write_bytes(b"")
    found = matches_in([str(tmp_path)])
    assert sorted(found) == ["alpha-vs-bravo-m1", "alpha-vs-bravo-m2"]
    assert len(found["alpha-vs-bravo-m1"]) == 2


def test_a_match_is_written_when_its_table_and_summary_both_are(tmp_path):
    folder = tmp_path / "de_test"
    folder.mkdir()
    (folder / "done.parquet").write_bytes(b"")
    (folder / "done.match.json").write_text("{}")
    # Stopped between the two: a table without its summary is not done.
    (folder / "stopped.parquet").write_bytes(b"")
    assert written(tmp_path) == {"done"}
    assert written(tmp_path / "nowhere") == set()
