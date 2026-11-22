"""
What a CS2 demo says about its match, without converting it.

    info(path) -> {"map", "map_title", "mode", "date", "duration_s", "players", "teams", "outcome",
                   "game_version", ...}

The file header (the first frame: server, map, network protocol, build) and
the file info (the frame the header's first offset points at: playback time
and ticks) are read directly with `stream.py`. The signon's console
variables give the mode and the regulation length where the server sends
them. The players, their teams and the score come from demoparser2 at the
recording's last ticks: one pass that takes about a second for a full match.
A demo holds no date; `date` stays None.
"""

from __future__ import annotations

import struct
from pathlib import Path

from . import stream

#: (game_type, game_mode) as the game's console variables set them.
MODES = {
    (0, 0): "casual",
    (0, 1): "competitive",
    (0, 2): "wingman",
    (1, 0): "arms race",
    (1, 1): "demolition",
    (1, 2): "deathmatch",
}
SIDES = {2: "T", 3: "CT"}
#: The game's phase once the match is over.
MATCH_ENDED = 5
#: How far before the recording's end the players are read as well: the demo clears the clan names at its very end.
BEFORE_END = 320


def _frame(buf: bytes, pos: int) -> tuple[int, int, bytes]:
    """One frame at `pos`: command (compression bit cleared), tick, payload."""
    cmd, pos = stream._varint(buf, pos)
    tick, pos = stream._varint(buf, pos)
    size, pos = stream._varint(buf, pos)
    data = bytes(buf[pos : pos + size])
    if len(data) < size:
        raise stream.FormatError("frame past the end")
    if cmd & 64:
        data = stream._snappy(data)
        cmd &= ~64
    return cmd, tick, data


def _header(path: Path) -> tuple[dict, dict]:
    """The file header's fields and the file info's (empty where the recording stopped before writing it)."""
    with open(path, "rb") as f:
        head = f.read(1 << 16)
        if head[:8] != stream.MAGIC:
            raise ValueError("not a Counter-Strike 2 demo")
        try:
            cmd, _, data = _frame(head, 16)
            fields = {n: v for n, _, v in stream.fields(data)} if cmd == 1 else {}
        except (stream.FormatError, ValueError):
            fields = {}
        if not fields:
            raise ValueError("not a Counter-Strike 2 demo: no file header")
        file_info: dict = {}
        offset = struct.unpack_from("<i", head, 8)[0] if len(head) >= 16 else 0
        if 16 < offset:
            f.seek(offset)
            tail = f.read(1 << 16)
            try:
                cmd, _, data = _frame(tail, 0)
                if cmd == 2:
                    file_info = {n: v for n, _, v in stream.fields(data)}
            except (stream.FormatError, ValueError):
                pass
    return fields, file_info


def _text(v) -> str | None:
    return stream._text(v) if isinstance(v, (bytes, bytearray)) and v else None


def _convars(path: Path) -> dict[str, str]:
    """The console variables the signon sets (the frames before the first tick)."""
    out: dict[str, str] = {}
    try:
        for it in stream.items(path):
            if it.tick > 0:
                break
            if it.source == "message" and it.id == 6:
                out.update(stream.convars(it.payload)["convars"])
    except (stream.FormatError, ValueError, OSError):
        pass
    return out


def _late_state(path: Path, ticks: list[int]):
    """The players at these ticks, from demoparser2; None where the parser cannot read them."""
    try:
        from demoparser2 import DemoParser

        return DemoParser(str(path)).parse_ticks(
            ["team_num", "team_clan_name", "team_rounds_total", "game_phase", "kills_total", "deaths_total",
             "assists_total"], ticks=ticks)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException:  # noqa: BLE001 - the parser's own errors (a Rust panic is a BaseException)
        return None


def _int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _players(rows) -> tuple[list[dict], list[dict], dict | None]:
    """Players, teams and the outcome from the parser's rows: each player as last seen, the clan name as last given."""
    if rows is None or len(rows) == 0:
        return [], [], None
    rows = rows.sort_values("tick")
    last = {}
    clan: dict[str, str] = {}
    for r in rows.to_dict("records"):
        sid = str(r.get("steamid"))
        last[sid] = r
        c = r.get("team_clan_name")
        if isinstance(c, str) and c:
            clan[sid] = c
    players, teams, phase = [], {}, None
    for sid, r in last.items():
        side = SIDES.get(_int(r.get("team_num")))
        name = clan.get(sid)
        team = (name or side) if side else None
        players.append({"name": r.get("name"), "team": team, "steamid": sid, "side": side,
                        "kills": _int(r.get("kills_total")), "deaths": _int(r.get("deaths_total")),
                        "assists": _int(r.get("assists_total"))})
        if team is not None and team not in teams:
            teams[team] = {"id": team, "name": name, "side": side, "score": _int(r.get("team_rounds_total"))}
        phase = _int(r.get("game_phase"))
    team_list = list(teams.values())
    outcome = None
    if phase == MATCH_ENDED and len(team_list) == 2 and all(t["score"] is not None for t in team_list):
        a, b = sorted(team_list, key=lambda t: -t["score"])
        outcome = {"winner": None, "result": "draw"} if a["score"] == b["score"] else {"winner": a["id"], "result": "win"}
    return players, team_list, outcome


def info(path: str | Path) -> dict:
    """What the demo says about its match. Raises ValueError for a file that is not a CS2 demo."""
    path = Path(path)
    fields, file_info = _header(path)
    convars = _convars(path)
    duration = None
    if isinstance(file_info.get(1), (bytes, bytearray)) and len(file_info[1]) == 4:
        duration = round(struct.unpack("<f", file_info[1])[0], 3)
    ticks = file_info.get(2) if isinstance(file_info.get(2), int) else None
    mode = None
    game_type, game_mode = _int(convars.get("game_type")), _int(convars.get("game_mode"))
    if game_type is not None and game_mode is not None:
        mode = MODES.get((game_type, game_mode), f"game_type {game_type} game_mode {game_mode}")
    rows = _late_state(path, sorted({max(0, ticks - BEFORE_END), ticks})) if ticks else None
    players, teams, outcome = _players(rows)
    build = fields.get(13)
    protocol = fields.get(2)
    return {
        "map": _text(fields.get(5)),
        "map_title": None,
        "mode": mode,
        "date": None,
        "duration_s": duration,
        "players": players,
        "teams": teams,
        "outcome": outcome,
        "game_version": str(protocol) if isinstance(protocol, int) else None,
        "build": build if isinstance(build, int) else None,
        "server": _text(fields.get(3)),
        "client": _text(fields.get(4)),
        "ticks": ticks,
        "max_rounds": _int(convars.get("mp_maxrounds")),
    }
