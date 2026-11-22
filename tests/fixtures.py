"""
A demo as the parser gives it, built by hand: two rounds, two players a side,
small enough to know every answer. The columns and their meaning are
demoparser2's, as `demo.read_part` asks for them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from heat3d_cs2.demo import OVERTIME, RawPart

#: steamid -> (name, team, team_num in the first half)
PLAYERS = {
    "1": ("ace", "Alpha", 2),
    "2": ("ash", "Alpha", 2),
    "3": ("bob", "Bravo", 3),
    "4": ("ben", "Bravo", 3),
}
POSITIONS = {"1": (100.0, 0.0), "2": (120.0, 10.0), "3": (-500.0, -300.0), "4": (-520.0, -320.0)}


def samples(
    rounds: list[dict],
    every: int = 8,
    clock0: float = 1000.0,
    last_tick: int | None = None,
    clans: bool = True,
    overtime: bool = False,
) -> pd.DataFrame:
    """
    Every player every `every` ticks. `rounds`: dicts with `freeze` (tick the
    freeze time ends), `end` (tick decided), `winner` (2 or 3, 1 a draw),
    `reason`, `deaths` {steamid: tick}, and optionally `swapped` (the teams on
    the other sides) and `overtime` (the game's overtime count, a column only
    with `overtime`). Before a round's freeze ends the players are frozen;
    between rounds the next round's count is shown, as the game does.
    """
    last_tick = last_tick or rounds[-1]["end"] + 640
    rows = []

    def side(num: int, r: dict) -> int:
        return 5 - num if r.get("swapped") else num

    for tick in range(0, last_tick + 1, every):
        played = sum(1 for r in rounds if tick >= r["end"])
        current = rounds[min(played, len(rounds) - 1)]
        decided = [r for r in rounds if r["end"] <= tick]
        status = decided[-1]["winner"] if decided and tick < decided[-1]["end"] + 448 else 0
        reason = decided[-1]["reason"] if status else 0
        freeze = tick < current["freeze"] and played < len(rounds)
        for sid, (name, clan, first) in PLAYERS.items():
            num = side(first, current)
            # The team's rounds won, whichever side it won them on.
            score = sum(1 for r in decided if r["winner"] == side(first, r))
            died = current.get("deaths", {}).get(sid)
            alive = not (died is not None and tick >= died and tick < current["end"] + 448)
            x, y = POSITIONS[sid]
            rows.append(
                {
                    "tick": tick,
                    "steamid": sid,
                    "name": name,
                    "X": x + (tick % 64),
                    "Y": y,
                    "Z": -160.0,
                    "yaw": 90.0,
                    "pitch": 10.0,
                    "health": 100 if alive else 0,
                    "armor_value": 100,
                    "team_num": num,
                    "team_clan_name": clan if clans else None,
                    "active_weapon_name": "Karambit" if sid == "1" else "AK-47",
                    "is_alive": alive,
                    "last_place_name": "BombsiteA" if num == 2 else "CTSpawn",
                    "balance": 800,
                    "current_equip_value": 4800 if played else 800,
                    "game_time": clock0 + tick / 64,
                    "total_rounds_played": played,
                    "round_win_status": status,
                    "round_win_reason": reason,
                    "team_rounds_total": score,
                    "is_warmup_period": False,
                    "is_freeze_period": freeze,
                    **({OVERTIME: current.get("overtime", 0)} if overtime else {}),
                }
            )
    return pd.DataFrame(rows)


def player_columns(prefix: str, sid: str | None, tick: int) -> dict:
    if sid is None:
        return {f"{prefix}_{k}": None for k in ("name", "steamid", "X", "Y", "Z", "team_num", "last_place_name")}
    name, _, num = PLAYERS[sid]
    x, y = POSITIONS[sid]
    return {
        f"{prefix}_name": name,
        f"{prefix}_steamid": sid,
        f"{prefix}_X": x,
        f"{prefix}_Y": y,
        f"{prefix}_Z": -160.0,
        f"{prefix}_team_num": num,
        f"{prefix}_last_place_name": "BombsiteA" if num == 2 else "CTSpawn",
    }


def death(tick: int, attacker: str | None, victim: str, *, headshot=False, weapon="ak47", assister: str | None = None) -> dict:
    return {
        "tick": tick,
        **player_columns("attacker", attacker, tick),
        **player_columns("user", victim, tick),
        **player_columns("assister", assister, tick),
        "weapon": weapon,
        "headshot": headshot,
        "assistedflash": False,
        "penetrated": 0,
        "thrusmoke": False,
        "noscope": False,
        "attackerblind": False,
        "total_rounds_played": 0,
        "is_warmup_period": False,
    }


def hurt(tick: int, attacker: str, victim: str, dmg: int, health_after: int, weapon="ak47") -> dict:
    return {
        "tick": tick,
        **player_columns("attacker", attacker, tick),
        **player_columns("user", victim, tick),
        "user_yaw": 90.0,
        "user_pitch": 0.0,
        "weapon": weapon,
        "dmg_health": dmg,
        "health": health_after,
        "is_warmup_period": False,
    }


def two_rounds(clans: bool = True, clock0: float = 1000.0) -> RawPart:
    """
    Round 1 (T win by elimination): ace kills bob (the opening), ben kills ace
    1.9 s later (a trade: bob's death is traded), ash kills ben - alone
    against one, a clutch won. Round 2 (T win, the bomb): ash plants on A,
    nobody dies, the bomb goes off.
    """
    rounds = [
        {"freeze": 640, "end": 1664, "winner": 2, "reason": 9, "deaths": {"3": 1280, "1": 1400, "4": 1600}},
        {"freeze": 2560, "end": 4800, "winner": 2, "reason": 1, "deaths": {}},
    ]
    s = samples(rounds, clock0=clock0, clans=clans)
    events = {
        "round_freeze_end": pd.DataFrame(
            {"tick": [640, 2560], "total_rounds_played": [0, 1], "is_warmup_period": [False, False]}
        ),
        "round_prestart": pd.DataFrame({"tick": [0, 2112]}),
        "player_death": pd.DataFrame(
            [
                death(1280, "1", "3", headshot=True),
                death(1400, "4", "1"),
                death(1600, "2", "4"),
            ]
        ),
        "player_hurt": pd.DataFrame(
            [
                hurt(1270, "1", "3", 60, 40),
                hurt(1280, "1", "3", 137, 0),
                hurt(1300, "4", "1", 100, 0),
                hurt(1600, "2", "4", 120, 0),
            ]
        ),
        "bomb_planted": pd.DataFrame(
            [{"tick": 4000, **player_columns("user", "2", 4000), "site": 325, "is_warmup_period": False}]
        ),
        "bomb_exploded": pd.DataFrame(
            [{"tick": 4790, "user_name": "ash", "user_steamid": "2", "site": 325, "is_warmup_period": False}]
        ),
        "weapon_fire": pd.DataFrame(
            [
                {"tick": 1270, **player_columns("user", "1", 1270), "weapon": "weapon_ak47", "is_warmup_period": False},
                {"tick": 1200, **player_columns("user", "2", 1200), "weapon": "weapon_smokegrenade", "is_warmup_period": False},
                {"tick": 1210, **player_columns("user", "2", 1210), "weapon": "weapon_knife_karambit", "is_warmup_period": False},
            ]
        ),
        "smokegrenade_detonate": pd.DataFrame(
            [{"tick": 1290, **player_columns("user", "2", 1290), "x": 50.0, "y": 60.0, "z": -150.0, "is_warmup_period": False}]
        ),
    }
    for df in events.values():
        df.columns = [str(c) for c in df.columns]
    return RawPart("synthetic.dem", "de_test", s, events)


def halves(plan: list[tuple[bool, int]], overtime: bool = True) -> RawPart:
    """
    One round per entry of `plan`, (swapped, overtime count): the teams on
    their first sides or swapped, and the game's overtime count - a column
    only with `overtime`. Every round a T win by elimination, nobody dies.
    """
    rounds = [
        {"freeze": 2000 * k + 640, "end": 2000 * k + 1600, "winner": 2, "reason": 9, "swapped": swapped, "overtime": ot}
        for k, (swapped, ot) in enumerate(plan)
    ]
    s = samples(rounds, overtime=overtime)
    events = {
        "round_freeze_end": pd.DataFrame(
            {"tick": [r["freeze"] for r in rounds], "total_rounds_played": list(range(len(rounds))), "is_warmup_period": False}
        ),
        "round_prestart": pd.DataFrame({"tick": [2000 * k for k in range(len(rounds))]}),
    }
    return RawPart("halves.dem", "de_test", s, events)


def frame_series(n: int, value) -> np.ndarray:
    return np.full(n, value)


# ---------------------------------------------------------------- a demo file, built byte by byte


def varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def pb(number: int, value) -> bytes:
    """One protobuf field: a whole number as a varint, bytes or text length-delimited, a float as 32 bits."""
    if isinstance(value, float):
        import struct

        return varint(number << 3 | 5) + struct.pack("<f", value)
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    data = value.encode() if isinstance(value, str) else value
    return varint(number << 3 | 2) + varint(len(data)) + data


def bitstream(messages: list[tuple[int, bytes]]) -> bytes:
    """Network messages as a demo packet holds them: type, size and bytes, bit by bit - none aligned to bytes."""
    bits: list[int] = []

    def put(value: int, n: int) -> None:
        bits.extend((value >> i) & 1 for i in range(n))

    for kind, body in messages:
        if kind < 16:
            put(kind, 6)
        elif kind < 256:
            put((kind & 15) | 0x10, 6)
            put(kind >> 4, 4)
        elif kind < 4096:
            put((kind & 15) | 0x20, 6)
            put(kind >> 4, 8)
        else:
            put((kind & 15) | 0x30, 6)
            put(kind >> 4, 28)
        for b in varint(len(body)) + body:
            put(b, 8)
    bits.extend([0] * (-len(bits) % 8))
    return bytes(sum(bits[i + j] << j for j in range(8)) for i in range(0, len(bits), 8))


def demo_file(frames: list[tuple[int, int, bytes, bool]]) -> bytes:
    """A demo of (command, tick, data, compressed) frames."""
    import pyarrow as pa

    out = bytearray(b"PBDEMS2\0" + bytes(8))
    for cmd, tick, data, compressed in frames:
        if compressed:
            data = pa.Codec("snappy").compress(data).to_pybytes()
            cmd |= 64
        out += varint(cmd) + varint(tick & 0xFFFFFFFF) + varint(len(data)) + data
    return bytes(out)


#: What `synthetic_demo` holds: (source, number) -> how many.
SYNTHETIC_ITEMS = {
    ("frame", 1): 1,
    ("message", 6): 1,
    ("message", 40): 1,
    ("message", 44): 1,
    ("message", 4): 2,
    ("message", 55): 2,
    ("message", 118): 1,
    ("message", 999): 1,
    ("frame", 16): 1,
    ("frame", 0): 1,
}


def synthetic_demo() -> bytes:
    """
    A small demo: its header; a signon packet with a console variable, the
    server's info and a string table created; the string tables (userinfo:
    ace and the SourceTV slot); two packets of ticks, entities, a chat line
    and a message nobody knows; an animation frame; the end.
    """
    signon = bitstream([
        (6, pb(1, pb(1, pb(1, "mp_friendlyfire") + pb(2, "true")))),
        (40, pb(13, 1 / 64) + pb(14, "/game/csgo") + pb(15, "de_test")),
        (44, pb(1, "userinfo") + pb(2, 2)),
    ])
    ace = pb(1, "ace") + varint(2 << 3 | 1) + (1).to_bytes(8, "little") + pb(3, 2) + varint(4 << 3 | 1) + (1).to_bytes(8, "little")
    tv = pb(1, "SourceTV") + pb(5, 1) + pb(6, 1)
    tables = pb(1, pb(1, "userinfo") + pb(2, pb(1, "0") + pb(2, tv)) + pb(2, pb(1, "1") + pb(2, ace)) + pb(4, 0))
    tables += pb(1, pb(1, "lightstyles") + pb(2, pb(1, "0") + pb(2, b"m")))
    first = bitstream([(4, pb(1, 640)), (55, b"\x01\x02\x03entities")])
    second = bitstream([
        (4, pb(1, 1100)),
        (55, bytes(range(40))),
        (118, pb(1, 4) + pb(2, 1) + pb(3, "Cstrike_Chat_All") + pb(4, "bob") + pb(5, "gl hf")),
        (999, b"unknown"),
    ])
    return demo_file([
        (1, 0, pb(1, "PBDEMS2\0") + pb(5, "de_test"), False),
        (8, -1, pb(3, signon), False),
        (6, -1, tables, True),
        (7, 640, pb(3, first), False),
        (7, 1100, pb(3, second), True),
        (16, 1100, b"animation", False),
        (0, 1200, b"", False),
    ])


def synthetic_props() -> pd.DataFrame:
    """Property changes as `keep.read_props` gives them: a health, a view angle, the rules' phase, a team name."""
    return pd.DataFrame({
        "tick": [640, 1280, 1400, 640, 1100, 0, 1664, 0],
        "type": ["CCSPlayerPawn.m_iHealth"] * 3 + ["CCSPlayerPawn.m_angEyeAngles"] * 2
        + ["CCSGameRulesProxy.CCSGameRules.m_gamePhase"] * 2 + ["CCSTeam.m_szTeamname"],
        "name": ["bob", "bob", "ace", "ace", "ace", "CCSGameRulesProxy", "CCSGameRulesProxy", "CCSTeam"],
        "player": ["3", "3", "1", "1", "1", "", "", ""],
        "entity": [3, 3, 1, 1, 1, -1, -1, 2],
        "value": [100.0, 0.0, 0.0, None, None, 2.0, 4.0, None],
        "vector": [None, None, None, [10.0, 90.0, 0.0], [12.0, 80.0, 0.0], None, None, None],
        "decoded": [None] * 7 + ['"Alpha"'],
    })
