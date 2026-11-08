"""
A CS2 demo's own structure, read without the parser: its frames and the
network messages inside them, each whole, for the sidecars (`keep.py`).

Written from the format as the files show it. A demo starts `PBDEMS2\\0` and
two offsets (16 bytes), then frames: a varint command, a varint tick and a
varint size, then that many bytes - Snappy-compressed when the command has
64 added. Three commands carry network messages: a packet (7) and a signon
packet (8) hold a protobuf whose field 3 is a bit stream of messages; a full
packet (13) holds the string tables (field 1) and such a packet (field 2).
In the bit stream each message is a type (6 bits, widened by 4, 8 or 28 more
where the top two of them say so), a varint size and that many bytes, none of
it aligned to bytes. Every other command is a frame of its own.

The names are Valve's for the message and command numbers; only those whose
content was seen to match are listed. A few messages are decoded in part,
each checked against something independent (see `DECODERS`); the rest are
kept whole.
"""

from __future__ import annotations

import struct
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

MAGIC = b"PBDEMS2\0"

#: Demo commands (frames), Valve's names.
FRAMES = {
    0: "DEM_Stop",
    1: "DEM_FileHeader",
    2: "DEM_FileInfo",
    3: "DEM_SyncTick",
    4: "DEM_SendTables",
    5: "DEM_ClassInfo",
    6: "DEM_StringTables",
    7: "DEM_Packet",
    8: "DEM_SignonPacket",
    9: "DEM_ConsoleCmd",
    10: "DEM_CustomData",
    11: "DEM_CustomDataCallbacks",
    12: "DEM_UserCmd",
    13: "DEM_FullPacket",
    14: "DEM_SaveGame",
    15: "DEM_SpawnGroups",
    16: "DEM_AnimationData",
    17: "DEM_AnimationHeaderData",
}
#: The frames that hold network messages, split here into them.
PACKETS = {7, 8, 13}

#: Network messages, Valve's names, for the numbers met in tournament demos.
MESSAGES = {
    0: "net_NOP",
    4: "net_Tick",
    5: "net_StringCmd",
    6: "net_SetConVar",
    7: "net_SignonState",
    8: "net_SpawnGroup_Load",
    9: "net_SpawnGroup_ManifestUpdate",
    11: "net_SpawnGroup_SetCreationTick",
    12: "net_SpawnGroup_Unload",
    13: "net_SpawnGroup_LoadCompleted",
    40: "svc_ServerInfo",
    41: "svc_FlattenedSerializer",
    42: "svc_ClassInfo",
    43: "svc_SetPause",
    44: "svc_CreateStringTable",
    45: "svc_UpdateStringTable",
    46: "svc_VoiceInit",
    47: "svc_VoiceData",
    48: "svc_Print",
    49: "svc_Sounds",
    50: "svc_SetView",
    51: "svc_ClearAllStringTables",
    52: "svc_CmdKeyValues",
    55: "svc_PacketEntities",
    62: "svc_HLTVStatus",
    63: "svc_ServerSteamID",
    76: "svc_UserCmds",
    117: "UM_SayText",
    118: "UM_SayText2",
    124: "UM_TextMsg",
    205: "GE_Source1LegacyGameEventList",
    207: "GE_Source1LegacyGameEvent",
    208: "GE_SosStartSoundEvent",
    209: "GE_SosStopSoundEvent",
    336: "CS_UM_PlayerStatsUpdate",
    350: "CS_UM_ServerRankRevealAll",
    369: "CS_UM_WeaponSound",
    375: "CS_UM_EndOfMatchAllPlayersData",
    400: "TE_EffectDispatch",
    452: "GE_FireBullets",
}

#: The bulk of a demo, more than half its size: the entity stream (every
#: entity's properties), the players' commands (sub-tick inputs) and the
#: animation stream. Kept whole by default; `--no-bulk` leaves them out and
#: the self-check counts them lost.
BULK = {("message", 55), ("message", 76), ("frame", 16)}


class FormatError(ValueError):
    pass


def _varint(buf: bytes, pos: int) -> tuple[int, int]:
    out = shift = 0
    while True:
        if pos >= len(buf):
            raise FormatError("varint past the end")
        b = buf[pos]
        pos += 1
        out |= (b & 0x7F) << shift
        if b < 0x80:
            return out, pos
        shift += 7


def fields(buf: bytes) -> Iterator[tuple[int, int, object]]:
    """A protobuf message's fields as they are on the wire: number, wire type, value (int or bytes)."""
    pos = 0
    while pos < len(buf):
        key, pos = _varint(buf, pos)
        kind = key & 7
        if kind == 0:
            value, pos = _varint(buf, pos)
        elif kind == 2:
            n, pos = _varint(buf, pos)
            value = buf[pos : pos + n]
            if len(value) != n:
                raise FormatError("field past the end")
            pos += n
        elif kind == 5:
            value = buf[pos : pos + 4]
            pos += 4
        elif kind == 1:
            value = buf[pos : pos + 8]
            pos += 8
        else:
            raise FormatError(f"wire type {kind}")
        yield key >> 3, kind, value


def _snappy(data: bytes) -> bytes:
    import pyarrow as pa

    size, _ = _varint(data, 0)
    return pa.Codec("snappy").decompress(data, decompressed_size=size).to_pybytes()


class _Bits:
    """A message bit stream, least significant bit first."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.end = len(data) * 8

    def read(self, n: int) -> int:
        if self.pos + n > self.end:
            raise FormatError("bits past the end")
        start = self.pos >> 3
        chunk = int.from_bytes(self.data[start : start + 8], "little")
        self.pos += n
        return (chunk >> ((self.pos - n) & 7)) & ((1 << n) - 1)

    def ubitvar(self) -> int:
        v = self.read(6)
        wide = v & 0x30
        if wide == 0x10:
            v = (v & 15) | (self.read(4) << 4)
        elif wide == 0x20:
            v = (v & 15) | (self.read(8) << 4)
        elif wide == 0x30:
            v = (v & 15) | (self.read(28) << 4)
        return v

    def varint(self) -> int:
        out = shift = 0
        while True:
            b = self.read(8)
            out |= (b & 0x7F) << shift
            if b < 0x80:
                return out
            shift += 7

    def take(self, n: int) -> bytes:
        if self.pos + 8 * n > self.end:
            raise FormatError("message past the end")
        start, shift = self.pos >> 3, self.pos & 7
        self.pos += 8 * n
        if not shift:
            return self.data[start : start + n]
        v = int.from_bytes(self.data[start : start + n + 1], "little") >> shift
        return (v & ((1 << (8 * n)) - 1)).to_bytes(n, "little")


def messages(data: bytes) -> Iterator[tuple[int, bytes]]:
    """The network messages of a packet: type and bytes. What is left at the end is under a byte of padding."""
    bits = _Bits(data)
    while bits.end - bits.pos >= 8:
        kind = bits.ubitvar()
        size = bits.varint()
        yield kind, bits.take(size)


@dataclass
class Item:
    """One thing of the demo, whole: a frame, a network message, or a frame's string tables."""

    #: Its place in the file, counting every item.
    seq: int
    #: The frame's tick; -1 before the first (the signon).
    tick: int
    #: `frame`, `message`, or `strings` (a frame's string tables, read by `string_tables`).
    source: str
    #: The command or message number.
    id: int
    payload: bytes

    @property
    def name(self) -> str:
        if self.source == "message":
            return MESSAGES.get(self.id, "")
        return FRAMES.get(self.id, "")

    @property
    def type(self) -> str:
        return f"{'frame' if self.source != 'message' else 'message'} {self.id}"


def items(path: str | Path | bytes) -> Iterator[Item]:
    """Every item of a demo, in file order. Container frames (packets) are given as their parts."""
    if isinstance(path, (bytes, bytearray)):
        yield from _items(path)
        return
    import mmap

    # Mapped, not read: a demo can be over a gigabyte.
    with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as buf:
        yield from _items(buf)


def _items(buf) -> Iterator[Item]:
    if buf[:8] != MAGIC:
        raise FormatError("not a CS2 demo")
    pos = 16
    seq = 0
    tick = -1
    while pos < len(buf):
        start = pos
        try:
            cmd, pos = _varint(buf, pos)
            tick, pos = _varint(buf, pos)
            size, pos = _varint(buf, pos)
        except FormatError:
            # Cut off inside a frame's head: the bytes after the last whole frame, as they are (frame -1).
            yield Item(seq, tick if tick != 0xFFFFFFFF else -1, "frame", -1, bytes(buf[start:]))
            break
        data = buf[pos : pos + size]
        pos += size
        tick = -1 if tick == 0xFFFFFFFF else tick
        if len(data) < size:
            # A demo cut off in the middle of a frame (a recording that stopped): what there is, as it is.
            yield Item(seq, tick, "frame", cmd, data)
            break
        if cmd & 64:
            try:
                data = _snappy(data)
            except Exception:  # noqa: BLE001 - kept compressed, whole, under its full command number
                yield Item(seq, tick, "frame", cmd, data)
                seq += 1
                continue
            cmd &= ~64
        packet = None
        rest: list[tuple[int, int, object]] = []
        if cmd in PACKETS:
            try:
                parts = list(fields(data))
            except FormatError:
                parts = [(0, 2, data)]
            for number, kind, value in parts:
                if cmd == 13 and number == 1:
                    yield Item(seq, tick, "strings", cmd, value)
                    seq += 1
                elif cmd == 13 and number == 2 and isinstance(value, (bytes, bytearray)):
                    try:
                        inner = list(fields(value))
                    except FormatError:
                        inner = [(0, 2, value)]
                    for n2, k2, v2 in inner:
                        if n2 == 3:
                            packet = v2
                        else:
                            rest.append((number, kind, value))
                elif cmd != 13 and number == 3:
                    packet = value
                else:
                    rest.append((number, kind, value))
        if cmd == 6:
            yield Item(seq, tick, "strings", cmd, data)
            seq += 1
        elif cmd not in PACKETS or rest:
            # A frame of its own - or a packet with more than its messages, kept whole besides.
            yield Item(seq, tick, "frame", cmd, data)
            seq += 1
        if packet is not None:
            try:
                found = list(messages(packet))
            except FormatError:
                # A packet that does not split: whole, as its frame.
                found = []
                yield Item(seq, tick, "frame", cmd, data)
                seq += 1
            for kind, body in found:
                yield Item(seq, tick, "message", kind, body)
                seq += 1
        if cmd == 0:
            break


# ---------------------------------------------------------------- what is decoded


def _text(v: object) -> str:
    return v.decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


def convars(payload: bytes) -> dict:
    """net_SetConVar: every console variable it sets, name and value, in order."""
    out = []
    for n, _, group in fields(payload):
        if n == 1:
            for m, _, cvar in fields(group):
                if m == 1:
                    f = {k: v for k, _, v in fields(cvar)}
                    out.append([_text(f.get(1, b"")), _text(f.get(2, b""))])
    return {"convars": out}


def say_text2(payload: bytes) -> dict:
    """UM_SayText2, a chat line: the speaker's entity, the kind (`Cstrike_Chat_All`...), name and text."""
    f = {n: v for n, _, v in fields(payload)}
    out = {"entity": f.get(1), "chat": bool(f.get(2, 0)), "kind": _text(f.get(3, b"")), "name": _text(f.get(4, b"")),
           "text": _text(f.get(5, b""))}
    for k, n in (("param3", 6), ("param4", 7)):
        if f.get(n):
            out[k] = _text(f[n])
    return out


def server_info(payload: bytes) -> dict:
    """svc_ServerInfo, what is checked of it: the map, the game folder, the tick interval."""
    f = {n: v for n, _, v in fields(payload)}
    out = {}
    if 15 in f:
        out["map"] = _text(f[15])
    if 14 in f:
        out["gameDir"] = _text(f[14])
    if isinstance(f.get(13), (bytes, bytearray)) and len(f[13]) == 4:
        out["tickInterval"] = struct.unpack("<f", f[13])[0]
    return out


def string_table_name(payload: bytes) -> dict:
    """svc_CreateStringTable: the table's name (its entries are kept whole, not read)."""
    for n, _, v in fields(payload):
        if n == 1:
            return {"table": _text(v)}
    return {}


#: Message number -> what is decoded of it. Each was checked: the console
#: variables against the parser's `server_cvar` (every name and value), the
#: chat against its `chat_message` (speaker and text), the server's map and
#: game folder against the demo's header and its tick interval against 64
#: ticks a second, the table names against the string tables' own.
DECODERS = {6: convars, 118: say_text2, 40: server_info, 44: string_table_name}


def string_tables(payload: bytes) -> Iterator[dict]:
    """
    A frame's string tables, every entry whole: table, entry index, its key,
    its data, whether it is a client-side entry, the table's flags. Each
    table first gives a row of its own (index -1, no key), its data the whole
    table where it has fields beyond these; anything in the frame that is not
    a table is given whole the same way.
    """
    for n, _, table in fields(payload):
        if n != 1:
            # Not a table: kept whole.
            yield {"table": "", "index": -1, "key": None, "data": bytes(table) if isinstance(table, (bytes, bytearray))
                   else str(table).encode(), "clientside": False, "flags": None}
            continue
        name, flags, other = "", None, False
        entries: list[tuple[int, bool, bytes | None, bytes | None]] = []
        index = {2: 0, 3: 0}
        for m, kind, v in fields(table):
            if m == 1:
                name = _text(v)
            elif m in (2, 3):
                f = {k: x for k, _, x in fields(v)}
                entries.append((index[m], m == 3, f.get(1), f.get(2)))
                index[m] += 1
                other = other or bool(set(f) - {1, 2})
            elif m == 4:
                flags = v
            else:
                other = True
        # The table itself, entries or none; whole where it has fields beyond these.
        yield {"table": name, "index": -1, "key": None, "data": bytes(table) if other else None, "clientside": False,
               "flags": flags}
        for i, clientside, key, data in entries:
            yield {"table": name, "index": i, "key": None if key is None else _text(key), "data": data,
                   "clientside": clientside, "flags": flags}


def player_info(data: bytes) -> dict:
    """A `userinfo` entry: name, steamid, user id, whether a bot or SourceTV. Checked against the parser's players."""
    f = {n: v for n, _, v in fields(data)}
    out = {"name": _text(f.get(1, b""))}
    for key, n in (("xuid", 2), ("steamid", 4)):
        v = f.get(n)
        if isinstance(v, (bytes, bytearray)) and len(v) == 8:
            out[key] = str(int.from_bytes(v, "little"))
    for key, n in (("userid", 3), ("fakeplayer", 5), ("ishltv", 6)):
        if n in f:
            out[key] = f[n] if key == "userid" else bool(f[n])
    return out
