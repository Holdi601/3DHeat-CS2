"""
Nothing of a demo is lost: everything lands in the table, the match document
or a sidecar, and the self-check says which and how much - on a demo built
byte by byte, and the hand-built match.
"""

from __future__ import annotations

import json
from collections import Counter

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from heat3d_cs2 import keep, stream
from heat3d_cs2.match import build_match
from heat3d_cs2.output import write

from .fixtures import SYNTHETIC_ITEMS, player_columns, synthetic_demo, synthetic_props, two_rounds


def test_the_demo_splits_into_its_frames_and_messages():
    items = list(stream.items(synthetic_demo()))
    counts = Counter((i.source, i.id) for i in items if i.source != "strings")
    assert counts == Counter(SYNTHETIC_ITEMS)
    assert [i.seq for i in items] == list(range(len(items)))
    by = {(i.source, i.id): i for i in items}
    assert by[("message", 6)].tick == -1
    assert by[("message", 118)].tick == 1100
    assert by[("message", 999)].payload == b"unknown"
    assert by[("frame", 16)].payload == b"animation"
    # Unaligned in the bit stream, whole out of it.
    assert [i.payload for i in items if i.id == 55 and i.source == "message"] == [b"\x01\x02\x03entities", bytes(range(40))]
    assert by[("message", 55)].name == "svc_PacketEntities" and by[("message", 999)].name == ""


def test_what_is_decoded_of_the_messages():
    by = {(i.source, i.id): i for i in stream.items(synthetic_demo())}
    assert stream.convars(by[("message", 6)].payload) == {"convars": [["mp_friendlyfire", "true"]]}
    info = stream.server_info(by[("message", 40)].payload)
    assert info == {"map": "de_test", "gameDir": "/game/csgo", "tickInterval": 1 / 64}
    chat = stream.say_text2(by[("message", 118)].payload)
    assert (chat["name"], chat["text"], chat["kind"], chat["entity"]) == ("bob", "gl hf", "Cstrike_Chat_All", 4)
    assert stream.string_table_name(by[("message", 44)].payload) == {"table": "userinfo"}


def test_the_string_tables_entry_by_entry():
    tables = [i for i in stream.items(synthetic_demo()) if i.source == "strings"]
    assert len(tables) == 1
    rows = list(stream.string_tables(tables[0].payload))
    assert [(r["table"], r["index"], r["key"]) for r in rows] == [
        ("userinfo", -1, None), ("userinfo", 0, "0"), ("userinfo", 1, "1"), ("lightstyles", -1, None), ("lightstyles", 0, "0")
    ]
    ace = stream.player_info(rows[2]["data"])
    assert ace == {"name": "ace", "xuid": "1", "steamid": "1", "userid": 2}
    assert stream.player_info(rows[1]["data"])["ishltv"] is True


def test_a_property_is_kept_where_it_changed():
    tick = np.array([1, 2, 3, 4, 1, 2, 3])
    entity = np.array([7, 7, 7, 7, 8, 8, 8])
    health = np.array([100.0, 100.0, 90.0, np.nan, np.nan, 50.0, 50.0])
    f = keep.changes("health", tick, entity, health)
    # Its first value, the change, where it went empty; the other entity from its first value.
    assert list(zip(f["tick"], f["entity"])) == [(1, 7), (3, 7), (4, 7), (2, 8)]
    assert np.isnan(f["value"][2]) and list(f["value"][[0, 1, 3]]) == [100.0, 90.0, 50.0]
    angles = np.array([[1.0, 2.0], [1.0, 2.0], [1.0, 3.0], None, None, [0.0, 0.0], [0.0, 0.0]], dtype=object)
    f = keep.changes("angles", tick, entity, angles)
    assert f["vector"] == [[1.0, 2.0], [1.0, 3.0], None, [0.0, 0.0]]
    big = np.array([76561198000000001, 76561198000000001, 76561198000000002, 0, 1, 1, 1], dtype=np.uint64)
    f = keep.changes("steamid", tick, entity, big)
    # Past what a float holds: as text, exactly.
    assert f["decoded"][:2] == ['"76561198000000001"', '"76561198000000002"']
    flags = np.array([True, None, None, False, True, True, False], dtype=object)
    f = keep.changes("flag", tick, entity, flags)
    assert list(f["tick"]) == [1, 2, 4, 1, 3] and list(f["value"][[0, 2, 3, 4]]) == [1.0, 0.0, 1.0, 0.0]


def test_a_grenade_number_used_again_starts_again():
    tick = np.array([10, 11, 20, 21])
    entity = np.array([5, 5, 5, 5])
    f = keep.changes("m_nBounces", tick, entity, np.array([1.0, 1.0, 1.0, 1.0]), gaps=True)
    assert list(f["tick"]) == [10, 20]


@pytest.fixture
def written(tmp_path):
    demo = tmp_path / "synthetic.dem"
    demo.write_bytes(synthetic_demo())
    raw = two_rounds()
    raw.path = str(demo)
    raw.props = synthetic_props()
    raw.header = {"map_name": "de_test"}
    raw.player_info = pd.DataFrame({"steamid": ["1", "2"], "name": ["ace", "ash"], "team_number": [2, 2]})
    # Warmup: an event the table leaves out, kept whole in the events sidecar.
    raw.events["player_jump"] = pd.DataFrame(
        [{"tick": 100, **player_columns("user", "3", 100), "is_warmup_period": True},
         {"tick": 700, **player_columns("user", "3", 700), "is_warmup_period": False}]
    )
    match = build_match([raw], "synthetic")
    return match, tmp_path


def test_nothing_is_lost(written):
    match, folder = written
    _, doc = write(match, folder)
    check = json.loads(doc.read_text(encoding="utf-8"))["selfCheck"]["completeness"]
    assert check["rule"].endswith("/docs/converters.md")
    assert check["lost"] == 0
    assert all(t["lost"] == 0 for t in check["types"].values())
    assert sorted(check["sidecars"]) == sorted(f"synthetic.{w}.parquet" for w in ("events", "props", "strings", "packets"))
    for name in check["sidecars"]:
        assert (folder / name).is_file()
    types = check["types"]
    # Every item of every kind is counted where it was met.
    for (source, number), n in SYNTHETIC_ITEMS.items():
        key = (stream.MESSAGES if source == "message" else stream.FRAMES).get(number, f"{source} {number}")
        assert types[key]["seen"] == n, key
    assert types["message 999"] == {"seen": 1, "decoded": 0, "partial": 0, "raw": 1, "lost": 0}
    assert types["svc_PacketEntities"]["partial"] == 2
    assert types["UM_SayText2"]["partial"] == 1
    assert types["stringtable userinfo"] == {"seen": 3, "decoded": 0, "partial": 2, "raw": 1, "lost": 0}
    assert types["player_death"]["seen"] == 3 and types["player_death"]["partial"] == 3
    assert types["player_jump"] == {"seen": 2, "decoded": 0, "partial": 1, "raw": 1, "lost": 0}
    assert types["CCSPlayerPawn"]["seen"] == 5 and types["CCSTeam"]["raw"] == 1
    assert types["playerInfo"] == {"seen": 2, "decoded": 2, "partial": 0, "raw": 0, "lost": 0}


def test_the_sidecars_hold_everything_whole(written):
    match, folder = written
    write(match, folder)
    events = pq.read_table(folder / "synthetic.events.parquet").to_pandas()
    jumps = events[events["type"] == "player_jump"]
    assert list(jumps["tick"]) == [100, 700]
    assert set(jumps["player"]) == {"3"}
    # The event's own keys, not the parser's additions.
    death = json.loads(events[events["type"] == "player_death"]["decoded"].iloc[0])
    assert death["headshot"] is True and death["attacker_name"] == "ace" and "attacker_X" not in death
    packets = pq.read_table(folder / "synthetic.packets.parquet").to_pandas()
    assert list(packets["seq"]) == sorted(packets["seq"])
    chat = packets[packets["name"] == "UM_SayText2"].iloc[0]
    assert json.loads(chat["decoded"])["text"] == "gl hf"
    assert packets[packets["type"] == "message 999"]["payload"].iloc[0] == b"unknown"
    # The clock is the table's: tick 1100 of this part is 1100/64 s on, from the match's zero.
    zero = match.sources[0][1] - match.sources[0][2] / 64 - match.sources[0][3]
    assert chat["time"] == pytest.approx(zero + 1100 / 64)
    assert np.isnan(packets[packets["name"] == "net_SetConVar"]["time"].iloc[0])
    strings = pq.read_table(folder / "synthetic.strings.parquet").to_pandas()
    ace = strings[(strings["type"] == "userinfo") & (strings["name"] == "1")].iloc[0]
    assert json.loads(ace["decoded"])["name"] == "ace" and ace["payload"]
    props = pq.read_table(folder / "synthetic.props.parquet").to_pandas()
    assert len(props) == len(synthetic_props())
    eye = props[props["type"] == "CCSPlayerPawn.m_angEyeAngles"]
    assert list(eye["vector"].iloc[1]) == [12.0, 80.0, 0.0]
    assert props[props["type"] == "CCSTeam.m_szTeamname"]["decoded"].iloc[0] == '"Alpha"'


def test_leaving_the_bulk_out_is_counted_lost(written):
    match, folder = written
    _, doc = write(match, folder, bulk=False)
    check = json.loads(doc.read_text(encoding="utf-8"))["selfCheck"]["completeness"]
    assert check["lost"] == 3
    lost = {t: c["lost"] for t, c in check["types"].items() if c["lost"]}
    assert lost == {"svc_PacketEntities": 2, "DEM_AnimationData": 1}
    assert check["leftOut"] == ["frame 16", "message 55", "message 76"]
    packets = pq.read_table(folder / "synthetic.packets.parquet").to_pandas()
    assert not (packets["type"] == "message 55").any()


def test_a_demo_cut_off_keeps_what_there_is():
    demo = synthetic_demo()
    whole = list(stream.items(demo))
    for cut in (len(demo) - 3, 60, 17):
        items = list(stream.items(demo[:cut]))
        # Every whole frame before the cut as it was, then the rest as it is.
        assert items[-1].source == "frame"
        assert [(i.source, i.id, i.payload) for i in items[:-1]] == [(i.source, i.id, i.payload) for i in whole[: len(items) - 1]]
