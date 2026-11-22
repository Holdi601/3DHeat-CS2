"""replay_info on a demo built by hand: a file header, the signon's console variables, the file info."""

from __future__ import annotations

import struct

import pandas as pd
import pytest

from heat3d_cs2 import replay_info


def _varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _field(number: int, value) -> bytes:
    if isinstance(value, int):
        return _varint(number << 3) + _varint(value)
    if isinstance(value, float):
        return _varint(number << 3 | 5) + struct.pack("<f", value)
    if isinstance(value, str):
        value = value.encode()
    return _varint(number << 3 | 2) + _varint(len(value)) + value


def _frame(cmd: int, tick: int, data: bytes) -> bytes:
    return _varint(cmd) + _varint(tick) + _varint(len(data)) + data


def _bits(messages: list[tuple[int, bytes]]) -> bytes:
    """A packet's bit stream: each message a 6-bit type (under 16 here), a varint size, its bytes; LSB first."""
    value = width = 0
    for kind, body in messages:
        for v, n in [(kind, 6)] + [(b, 8) for b in _varint(len(body)) + body]:
            value |= v << width
            width += n
    return value.to_bytes((width + 7) // 8, "little")


def _demo(convars: dict[str, str], seconds: float, ticks: int) -> bytes:
    header = b"".join([
        _field(1, "PBDEMS2\0"), _field(2, 12345), _field(3, "Test Server"), _field(4, "SourceTV Demo"),
        _field(5, "de_test"), _field(6, "csgo"), _field(11, "valve_demo_2"), _field(13, 999),
    ])
    setcvar = _field(1, b"".join(_field(1, _field(1, k) + _field(2, v)) for k, v in convars.items()))
    body = _frame(1, 0xFFFFFFFF, header) + _frame(8, 0xFFFFFFFF, _field(3, _bits([(6, setcvar)])))
    body += _frame(7, 10, _field(3, b""))
    info_at = 16 + len(body)
    body += _frame(2, ticks, _field(1, seconds) + _field(2, ticks) + _field(3, ticks)) + _frame(0, ticks, b"")
    return b"PBDEMS2\0" + struct.pack("<ii", info_at, 0) + body


def test_header_fileinfo_and_players(tmp_path, monkeypatch):
    f = tmp_path / "match.dem"
    f.write_bytes(_demo({"game_type": "0", "game_mode": "1", "mp_maxrounds": "24"}, 1800.5, 115232))
    rows = pd.DataFrame([
        {"tick": 114912, "steamid": "1", "name": "one", "team_num": 2, "team_clan_name": "Alpha",
         "team_rounds_total": 13, "game_phase": 5, "kills_total": 20, "deaths_total": 10, "assists_total": 3},
        {"tick": 115232, "steamid": "1", "name": "one", "team_num": 2, "team_clan_name": "",
         "team_rounds_total": 13, "game_phase": 5, "kills_total": 20, "deaths_total": 10, "assists_total": 3},
        {"tick": 115232, "steamid": "2", "name": "two", "team_num": 3, "team_clan_name": "",
         "team_rounds_total": 7, "game_phase": 5, "kills_total": 9, "deaths_total": 18, "assists_total": 4},
        {"tick": 115232, "steamid": "3", "name": "caster", "team_num": 1, "team_clan_name": "",
         "team_rounds_total": 0, "game_phase": 5, "kills_total": 0, "deaths_total": 0, "assists_total": 0},
    ])
    asked = []
    monkeypatch.setattr(replay_info, "_late_state", lambda path, ticks: asked.append(ticks) or rows)
    d = replay_info.info(f)
    assert asked == [[115232 - replay_info.BEFORE_END, 115232]]
    assert d["map"] == "de_test" and d["map_title"] is None
    assert d["mode"] == "competitive" and d["max_rounds"] == 24
    assert d["date"] is None
    assert d["duration_s"] == pytest.approx(1800.5)
    assert d["game_version"] == "12345" and d["build"] == 999 and d["server"] == "Test Server"
    assert d["ticks"] == 115232
    by = {p["name"]: p for p in d["players"]}
    assert by["one"]["team"] == "Alpha" and by["one"]["side"] == "T" and by["one"]["kills"] == 20
    assert by["two"]["team"] == "CT" and by["caster"]["team"] is None
    assert d["teams"] == [{"id": "Alpha", "name": "Alpha", "side": "T", "score": 13},
                          {"id": "CT", "name": None, "side": "CT", "score": 7}]
    assert d["outcome"] == {"winner": "Alpha", "result": "win"}


def test_parser_failure_keeps_the_header(tmp_path):
    f = tmp_path / "short.dem"
    f.write_bytes(_demo({}, 12.0, 768))
    d = replay_info.info(f)
    assert d["map"] == "de_test" and d["mode"] is None and d["duration_s"] == pytest.approx(12.0)
    assert d["outcome"] is None or d["outcome"]["winner"] is None


def test_garbage_is_refused(tmp_path):
    f = tmp_path / "x.dem"
    f.write_bytes(b"HL2DEMO\0" + bytes(64))
    with pytest.raises(ValueError):
        replay_info.info(f)
    g = tmp_path / "y.dem"
    g.write_bytes(b"PBDEMS2\0" + b"\xff" * 40)
    with pytest.raises(ValueError):
        replay_info.info(g)
