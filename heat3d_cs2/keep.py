"""
Everything a demo holds that the table and the match document do not, kept
whole beside them, and the self-check of where each thing went - the rule all
3DHeat converters follow:
https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md

Four sidecars, `<match>.<what>.parquet`, each with `time` on the table's
clock, the demo `tick` and the `part` (the demo file, in the match's order):

- `events`: every game event the parser reads, every key of it as the parser
  gives it (`decoded`, JSON), warmup and all - the table has them in part.
- `props`: every entity property the parser can read, each time it changed
  (long: one row per change - tick, entity, property, value). The players'
  pawns and controllers, their active weapon, every grenade, the game rules,
  the teams, the players' commands.
- `strings`: every entry of the string tables, as each snapshot holds them.
- `packets`: every other frame and network message of the demo, whole
  (`stream.py`); a few decoded in part.

Nothing is thinned in them. The self-check (`completeness`) counts, for each
kind of thing as the demo has it, how many there were, how many went whole
into the table or document, in part, raw only, and lost.
"""

from __future__ import annotations

import json
import math
import struct
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from . import stream
from .demo import EVENT_PLAYER, TICKRATE
from .events import plain

RULE = "https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md"

#: What the parser adds to an event besides its own keys: the players'
#: state at that tick (kept in the props sidecar) and the round count.
_ADDED = {"total_rounds_played", "is_warmup_period"} | {
    f"{who}_{f}" for who in ("user", "attacker", "assister") for f in EVENT_PLAYER
}

#: An event of the demo -> the table's `event` values its rows carry where they are not its own name.
IN_TABLE = {
    "chat_message": ("chat",),
    "player_death": ("death",),
    "player_hurt": ("hurt",),
    "player_blind": ("blind",),
    "weapon_fire": ("shot", "throw", "slash"),
    "smokegrenade_detonate": ("smoke",),
    "flashbang_detonate": ("flash",),
    "hegrenade_detonate": ("he",),
    "inferno_startburn": ("molotov",),
    "decoy_detonate": ("decoy",),
    "bomb_planted": ("plant",),
    "bomb_defused": ("defuse",),
    "bomb_exploded": ("explode", "bomb_exploded"),
}

#: The players' commands as the parser reads them (their whole messages are svc_UserCmds in the packets sidecar).
USERCMD = [
    "usercmd_viewangle_x",
    "usercmd_viewangle_y",
    "usercmd_viewangle_z",
    "usercmd_buttonstate_1",
    "usercmd_buttonstate_2",
    "usercmd_buttonstate_3",
    "usercmd_consumed_server_angle_changes",
    "usercmd_forward_move",
    "usercmd_left_move",
    "usercmd_impulse",
    "usercmd_mouse_dx",
    "usercmd_mouse_dy",
    "usercmd_left_hand_desired",
    "usercmd_weapon_select",
]

#: What one parser call may hold, in bytes: a number is 8 a row, a list or text about 25 times that. The
#: players' properties are read in windows of ticks, the grenades' (which the parser gives only whole) in
#: fewer properties at a time the longer the demo.
BUDGET = 800 << 20
#: Ticks per window of the players' properties.
WINDOW = 20_000
#: Weight of a property the parser gives as objects (lists, text) against a number.
OBJECT = 25

#: Message and frame numbers read in part elsewhere (besides `stream.DECODERS`): the game events and the bullets
#: (the parser's events), the entity stream and the commands (its props), the file header (the document's header).
READ_ELSEWHERE = {("message", 207), ("message", 452), ("message", 55), ("message", 76), ("frame", 1)}


# ---------------------------------------------------------------- the clock


def _clock(source) -> tuple[float, float, float]:
    """A part's (server clock at its first tick, that tick, the match's zero on the server clock)."""
    _, clock0, tick0, offset = source
    return clock0, tick0, offset


def _times(source, ticks) -> np.ndarray:
    clock0, tick0, offset = _clock(source)
    t = np.asarray(ticks, dtype=float)
    out = clock0 + (t - tick0) / TICKRATE - offset
    # Before the first tick (the signon) there is no time.
    return np.where(t < 0, np.nan, out)


# ---------------------------------------------------------------- events


def _event_rows(name: str, df: pd.DataFrame) -> dict:
    own = [c for c in df.columns if c != "tick" and c not in _ADDED]
    records = df[own].to_dict("records") if own else [{}] * len(df)
    decoded = [json.dumps({k: plain(v) for k, v in r.items()}, ensure_ascii=False, separators=(",", ":")) for r in records]

    def text(c):
        return df[c].map(lambda v: "" if v is None or (isinstance(v, float) and math.isnan(v)) else str(plain(v))).tolist() if c in df else [""] * len(df)

    entity = next((c for c in ("entityid", "entindex") if c in df), None)
    return {
        "tick": df["tick"].to_numpy(dtype=np.int64),
        "type": [name] * len(df),
        "name": text("user_name"),
        "player": text("user_steamid"),
        "entity": pd.to_numeric(df[entity], errors="coerce").to_numpy(dtype=float) if entity else np.full(len(df), np.nan),
        "decoded": decoded,
    }


EVENTS_SCHEMA = pa.schema([
    ("time", pa.float64()), ("tick", pa.int32()), ("part", pa.int8()), ("type", pa.string()), ("name", pa.string()),
    ("player", pa.string()), ("entity", pa.int32()), ("decoded", pa.string()),
])


def write_events(match, path: Path) -> tuple[Counter, Counter]:
    """Every game event of every part, whole. Returns (seen, written) per event name."""
    seen: Counter = Counter()
    written: Counter = Counter()
    tables = []
    for k, source in enumerate(match.sources):
        raw = source[0]
        for name, df in sorted(raw.events.items()):
            if df is None or not len(df):
                continue
            seen[name] += len(df)
            rows = _event_rows(name, df)
            tables.append(pa.table({
                "time": pa.array(_times(source, rows["tick"]), pa.float64()),
                "tick": pa.array(rows["tick"], pa.int32()),
                "part": pa.array(np.full(len(df), k), pa.int8()),
                "type": pa.array(rows["type"], pa.string()),
                "name": pa.array(rows["name"], pa.string()),
                "player": pa.array(rows["player"], pa.string()),
                "entity": pa.array(rows["entity"], pa.float64(), from_pandas=True).cast(pa.int32(), safe=False),
                "decoded": pa.array(rows["decoded"], pa.string()),
            }, schema=EVENTS_SCHEMA))
            written[name] += len(df)
    table = pa.concat_tables(tables) if tables else EVENTS_SCHEMA.empty_table()
    pq.write_table(table, path, compression="zstd", use_dictionary=["type", "name", "player"])
    return seen, written


def events_in_document(match) -> Counter:
    """How many rows of the table and entries of the document carry each event of the demo."""
    table = Counter(match.rows["event"].astype(str)) if len(match.rows) else Counter()
    doc = Counter(e["event"] for e in match.events)
    out: Counter = Counter()
    names = {name for source in match.sources for name in source[0].events}
    for name in names:
        out[name] = sum(table[t] for t in IN_TABLE.get(name, (name,))) + doc[name]
    if "fire_bullets" in names and len(match.rows):
        # The bullets are told in the shots' detail.
        shots = match.rows[match.rows["event"].isin(["shot", "throw", "slash"])]
        out["fire_bullets"] = int((shots["detail"].astype(str) != "").sum())
    return out


# ---------------------------------------------------------------- props


PROPS_SCHEMA = pa.schema([
    ("time", pa.float64()), ("tick", pa.int32()), ("part", pa.int8()), ("type", pa.string()), ("name", pa.string()),
    ("player", pa.string()), ("entity", pa.int32()), ("value", pa.float64()), ("vector", pa.list_(pa.float64())),
    ("decoded", pa.string()),
])


def group_of(prop: str) -> str:
    """A property's group for the self-check: its class (`CCSPlayerPawn`, `Weapon`...) or `usercmd`."""
    return "usercmd" if prop.startswith("usercmd_") else prop.split(".", 1)[0]


def _plain(v: object) -> object:
    """A value as JSON takes it, nested lists and maps too (`events.plain` for the rest)."""
    if isinstance(v, dict):
        return {str(k): _plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, np.ndarray)):
        return [_plain(x) for x in v]
    return plain(v)


def _json(v) -> str:
    return json.dumps(_plain(v), ensure_ascii=False, separators=(",", ":"))


def changes(prop: str, tick: np.ndarray, entity: np.ndarray, col: np.ndarray, gaps: bool = False) -> dict | None:
    """
    One property's values, one per entity per tick, ordered by entity then
    tick: the rows where it changed - its first value, every new one, and
    where it went empty (`keep`, a mask over the rows). Numbers (flags as
    0/1) in `value`, lists of numbers in `vector`, anything else - text, and
    whole numbers past what a float holds exactly - as JSON in `decoded`.
    With `gaps`, an entity missing for a tick starts again: an entity number
    used again by a new grenade.
    """
    n = len(tick)
    if not n:
        return None
    first = np.ones(n, bool)
    first[1:] = entity[1:] != entity[:-1]
    if gaps:
        first[1:] |= tick[1:] - tick[:-1] > 1
    notnull = ~pd.isna(col) if col.dtype == object else ~np.isnan(col.astype(float))
    same = np.zeros(n, bool)
    value = vector = decoded = None
    kinds = _kinds(col, notnull) if col.dtype == object else {col.dtype.type}
    if kinds <= {bool, np.bool_}:
        value = np.full(n, np.nan)
        value[notnull] = col[notnull] == True  # noqa: E712 - numpy compares element by element
    elif all(issubclass(k, (int, float, np.integer, np.floating)) for k in kinds) and not _too_big(col, notnull):
        value = np.full(n, np.nan)
        value[notnull] = col[notnull].astype(float)
    elif kinds <= {list, np.ndarray} and (matrix := _matrix(col[notnull])) is not None:
        vector = np.full((n, matrix.shape[1]), np.nan)
        vector[notnull] = matrix
        eq = (vector[1:] == vector[:-1]) | (np.isnan(vector[1:]) & np.isnan(vector[:-1]))
        same[1:] = eq.all(axis=1)
    elif kinds <= {str} or all(issubclass(k, (int, np.integer)) for k in kinds):
        same[1:] = col[1:] == col[:-1]
        decoded = col
    else:
        decoded = np.array([_json(x) if ok else None for x, ok in zip(col, notnull)], dtype=object)
        same[1:] = decoded[1:] == decoded[:-1]
    if value is not None:
        same[1:] = value[1:] == value[:-1]
    # Equal only where both have a value; both empty is no change either.
    same[1:] &= notnull[1:] & notnull[:-1]
    same[1:] |= ~notnull[1:] & ~notnull[:-1]
    keep = (~same | first) & ~(first & ~notnull)
    if not keep.any():
        return None
    out = {"tick": tick[keep], "entity": entity[keep], "type": prop, "keep": keep}
    if value is not None:
        out["value"] = value[keep]
    if vector is not None:
        out["vector"] = [row.tolist() if ok else None for row, ok in zip(vector[keep], notnull[keep])]
    if decoded is not None:
        out["decoded"] = [_json(x) if ok else None for x, ok in zip(decoded[keep], notnull[keep])]
    return out


def _too_big(col: np.ndarray, notnull: np.ndarray) -> bool:
    """Whole numbers a float64 does not hold exactly (steamids, item ids): kept as text."""
    if col.dtype.kind == "f" or not notnull.any():
        return False
    values = col[notnull]
    if col.dtype == object:
        return any(isinstance(v, (int, np.integer)) and abs(int(v)) >= 2**53 for v in values)
    return bool((np.abs(values.astype(np.float64)) >= 2**53).any())


def _kinds(col: np.ndarray, notnull: np.ndarray) -> set:
    return {type(x) for x in col[notnull][:1000]}


def _matrix(values: np.ndarray) -> np.ndarray | None:
    """Lists of numbers, all as long, as a matrix; None otherwise."""
    try:
        lists = pa.array(values, type=pa.list_(pa.float64()))
    except (pa.ArrowInvalid, pa.ArrowTypeError, TypeError, ValueError):
        return None
    lengths = pc.list_value_length(lists).to_numpy(zero_copy_only=False)
    if not len(lengths) or lengths[0] < 1 or (lengths != lengths[0]).any():
        return None
    return lists.flatten().to_numpy(zero_copy_only=False).reshape(len(lengths), int(lengths[0]))


def _props_table(found: list[dict], names: np.ndarray, players: np.ndarray) -> pa.Table:
    """
    Change rows of several properties as one table (no time yet). `names`
    and `players` are per row of the properties' common order, as the masks
    in `found` select them.
    """
    if not found:
        return PROPS_SCHEMA.empty_table().drop_columns(["time", "part"])
    n = [len(f["tick"]) for f in found]
    vector: list = []
    decoded: list = []
    for f, k in zip(found, n):
        vector.extend(f.get("vector", [None] * k))
        decoded.extend(f.get("decoded", [None] * k))
    entity = np.concatenate([np.asarray(f["entity"], dtype=float) for f in found])
    return pa.table({
        "tick": pa.array(np.concatenate([f["tick"] for f in found]).astype(np.int64), pa.int32()),
        "type": pa.array(np.repeat(np.array([f["type"] for f in found], dtype=object), n), pa.string()),
        "name": pa.array(np.concatenate([names[f["keep"]] for f in found]), pa.string()),
        "player": pa.array(np.concatenate([players[f["keep"]] for f in found]), pa.string()),
        "entity": pa.array(entity, pa.float64(), from_pandas=True).cast(pa.int32(), safe=False),
        "value": pa.array(np.concatenate([f.get("value", np.full(k, np.nan)) for f, k in zip(found, n)]), pa.float64(),
                          from_pandas=True),
        "vector": pa.array(vector, pa.list_(pa.float64())),
        "decoded": pa.array(decoded, pa.string()),
    })


def _labels(values: pd.Series) -> np.ndarray:
    """A column as text in an object array, cheaply: each distinct value converted once."""
    codes, uniques = pd.factorize(values, use_na_sentinel=True)
    labels = np.array([("" if pd.isna(u) else str(u)) for u in uniques] + [""], dtype=object)
    return labels[codes]


def _batches(props: list[str], weight: dict[str, int], rows: int) -> list[list[str]]:
    """Properties in batches that keep a parser call of `rows` rows within the budget."""
    most = max(1, BUDGET // (8 * max(1, rows)))
    out: list[list[str]] = []
    batch: list[str] = []
    total = 0
    for prop in sorted(props, key=lambda x: (weight.get(x, OBJECT), x)):
        w = weight.get(prop, OBJECT)
        if batch and total + w > most:
            out.append(batch)
            batch, total = [], 0
        batch.append(prop)
        total += w
    return out + ([batch] if batch else [])


def _passes(read, batches: list[list[str]], unread: list[str]):
    """
    `read(batch)` for each batch: the batch and the properties the parser
    gave. One it does not give is unread; a batch it fails on is split until
    the failing ones are alone.
    """
    stack = list(reversed(batches))
    while stack:
        batch = stack.pop()
        try:
            df = read(batch)
        except Exception:  # noqa: BLE001 - the parser fails on some properties: the rest are read
            if len(batch) == 1:
                unread.append(batch[0])
            else:
                stack += [batch[len(batch) // 2 :], batch[: len(batch) // 2]]
            continue
        unread.extend(c for c in batch if c not in df)
        yield [c for c in batch if c in df], df


def _weights(parser, props: list[str], ticks: list[int]) -> dict[str, int]:
    """Each property's weight, from what the parser gives for it at a few ticks: objects are heavy."""
    try:
        df = parser.parse_ticks(props, ticks=ticks)
    except Exception:  # noqa: BLE001 - unknown: every property counts as heavy
        return {}
    # One it gives nothing for here is mostly one it gives nothing for at all (or only for grenades): light.
    return {c: (OBJECT if df[c].dtype == object else 1) if c in df else 2 for c in props}


def read_props(path: str | Path, unread: list[str], last_tick: int | None = None):
    """
    Every property the parser can read of a demo, as tables of change rows,
    one per parser call. Each player's (pawn, controller, active weapon,
    commands) is keyed by the controller's entity; the game rules' by tick
    alone (entity -1); a team's by its number; a grenade's by its own entity,
    the thrower as its player and its class as its name. Properties the
    parser lists but cannot read go into `unread`.

    The players' properties are read a window of ticks at a time, each
    window starting a tick early so that a change at its first tick is seen;
    `last_tick` is where the demo ends (read from it where not given).
    """
    from demoparser2 import DemoParser

    parser = DemoParser(str(path))
    listed = sorted(f for f in parser.list_updated_fields() if not f.endswith("."))
    grenade = [f for f in listed if f.startswith("Grenade.")]
    rules = [f for f in listed if f.startswith("CCSGameRulesProxy.")]
    teams = [f for f in listed if f.startswith("CCSTeam.")]
    player = [f for f in listed if f not in set(grenade + rules + teams)] + USERCMD
    if last_tick is None:
        last_tick = int(parser.parse_ticks(["team_num"])["tick"].max())
    weight = _weights(parser, listed + USERCMD, [last_tick // 2, last_tick // 2 + 1])
    # A property missing from one window can be there in the next: unread is what no call gave.
    missed: list[str] = []
    got: set[str] = set()
    players_per_tick = 12
    for start in range(0, last_tick + 1, WINDOW):
        ticks = list(range(max(0, start - 1), min(start + WINDOW, last_tick + 1)))
        rows = players_per_tick * len(ticks)

        def window(b, ticks=ticks, extra=("entity_id",)):
            return parser.parse_ticks(b + list(extra), ticks=ticks)

        for batch, df in _passes(window, _batches(player, weight, rows), missed):
            got.update(batch)
            if not len(df) or "entity_id" not in df:
                continue
            if df["entity_id"].isna().any():
                df = df[df["entity_id"].notna()]
            players_per_tick = max(players_per_tick, int(np.ceil(len(df) / max(1, len(ticks)))))
            order = np.lexsort((df["tick"].to_numpy(), df["entity_id"].to_numpy()))
            tick = df["tick"].to_numpy()[order]
            entity = df["entity_id"].to_numpy(dtype=np.int64)[order]
            found = [_from(changes(c, tick, entity, df[c].to_numpy()[order]), start) for c in batch]
            yield _props_table([f for f in found if f], _labels(df["name"])[order], _labels(df["steamid"])[order])

        for group in (rules, teams):
            read = lambda b, ticks=ticks: parser.parse_ticks(b + ["team_num"], ticks=ticks)  # noqa: E731
            for batch, df in _passes(read, _batches(group, weight, rows), missed):
                got.update(batch)
                if not batch or not len(df):
                    continue
                if group is rules:
                    df = df.groupby("tick", sort=True)[batch].first().reset_index()
                    entity = np.full(len(df), -1, dtype=np.int64)
                    names = np.full(len(df), "CCSGameRulesProxy", dtype=object)
                else:
                    df = df[df["team_num"].notna()].groupby(["team_num", "tick"], sort=True)[batch].first().reset_index()
                    entity = df["team_num"].to_numpy(dtype=np.int64)
                    names = np.full(len(df), "CCSTeam", dtype=object)
                tick = df["tick"].to_numpy()
                found = [_from(changes(c, tick, entity, df[c].to_numpy()), start) for c in batch]
                yield _props_table([f for f in found if f], names, np.full(len(df), "", dtype=object))

    # The grenades come whole: as many properties at a time as the budget holds for their rows.
    rows = len(parser.parse_grenades())
    for batch, df in _passes(lambda b: parser.parse_grenades(extra=b), _batches(grenade, weight, rows), missed):
        got.update(batch)
        if not len(df):
            continue
        df = df.sort_values(["grenade_entity_id", "tick"], kind="stable")
        tick = df["tick"].to_numpy()
        entity = df["grenade_entity_id"].to_numpy(dtype=np.int64)
        names = _labels(df["grenade_type"])
        players = _labels(df["steamid"])
        found = [changes(c, tick, entity, df[c].to_numpy(), gaps=True) for c in batch]
        yield _props_table([f for f in found if f], names, players)
    unread.extend(sorted(set(missed) - got))


def _from(found: dict | None, start: int) -> dict | None:
    """A window's changes from its own first tick on: the tick before it only told what was there already."""
    if found is None or not start:
        return found
    early = found["tick"] < start
    if not early.any():
        return found
    keep = found["keep"].copy()
    keep[np.flatnonzero(keep)[early]] = False
    if not keep.any():
        return None
    late = ~early
    out = {"tick": found["tick"][late], "entity": found["entity"][late], "type": found["type"], "keep": keep}
    for k in ("value", "vector", "decoded"):
        if k in found:
            v = found[k]
            out[k] = v[late] if isinstance(v, np.ndarray) else [x for x, ok in zip(v, late) if ok]
    return out


def write_props(match, path: Path) -> tuple[Counter, Counter, list[str]]:
    """The props sidecar of every part, written as it is read. Returns (seen, written) per group and the unread."""
    seen: Counter = Counter()
    written: Counter = Counter()
    unread: list[str] = []
    writer = pq.ParquetWriter(
        path,
        PROPS_SCHEMA,
        compression="zstd",
        compression_level=9,
        use_dictionary=["type", "name", "player", "decoded"],
        column_encoding={"time": "BYTE_STREAM_SPLIT", "tick": "DELTA_BINARY_PACKED", "value": "BYTE_STREAM_SPLIT"},
    )
    try:
        for k, source in enumerate(match.sources):
            raw = source[0]
            if getattr(raw, "props", None) is not None:
                batches = [pa.Table.from_pandas(raw.props, preserve_index=False)]
            elif Path(raw.path).is_file():
                last = int(raw.samples["tick"].max()) + TICKRATE if len(raw.samples) else None
                batches = read_props(raw.path, unread, last)
            else:
                continue
            for t in batches:
                if not len(t):
                    continue
                seen.update(_groups(t))
                t = _with_clock(t, source, k).select(PROPS_SCHEMA.names).cast(PROPS_SCHEMA)
                writer.write_table(t)
                written.update(_groups(t))
    finally:
        writer.close()
    return seen, written, sorted(set(unread))


def _groups(t: pa.Table) -> Counter:
    """Rows per property group."""
    out: Counter = Counter()
    for row in pc.value_counts(t.column("type")).to_pylist():
        out[group_of(row["values"])] += row["counts"]
    return out


def _with_clock(t: pa.Table, source, k: int) -> pa.Table:
    ticks = t.column("tick").to_numpy(zero_copy_only=False)
    t = t.append_column("time", pa.array(_times(source, ticks), pa.float64()))
    return t.append_column("part", pa.array(np.full(len(t), k), pa.int8()))


# ---------------------------------------------------------------- packets and string tables


PACKETS_SCHEMA = pa.schema([
    ("time", pa.float64()), ("tick", pa.int32()), ("part", pa.int8()), ("seq", pa.int64()), ("type", pa.string()),
    ("name", pa.string()), ("id", pa.int32()), ("decoded", pa.string()), ("payload", pa.binary()),
])
STRINGS_SCHEMA = pa.schema([
    ("time", pa.float64()), ("tick", pa.int32()), ("part", pa.int8()), ("snapshot", pa.int64()), ("type", pa.string()),
    ("name", pa.string()), ("entity", pa.int32()), ("clientside", pa.bool_()), ("flags", pa.int32()),
    ("decoded", pa.string()), ("payload", pa.binary()),
])
#: Rows and bytes of packets held before they are written.
_FLUSH_ROWS, _FLUSH_BYTES = 200_000, 64 << 20


def type_of(item: stream.Item) -> str:
    """An item's name for the self-check: Valve's where known, else `message <n>` / `frame <n>`."""
    return item.name or item.type


def write_packets(match, packets_path: Path, strings_path: Path, bulk: bool = True) -> dict[str, Counter]:
    """
    The packets and strings sidecars of every part, from the demo files.
    Returns per type its counts (seen, partial, raw) for packets and strings.
    """
    counts: dict[str, Counter] = {}
    pw = pq.ParquetWriter(packets_path, PACKETS_SCHEMA, compression="zstd", use_dictionary=["type", "name", "decoded"],
                          column_encoding={"seq": "DELTA_BINARY_PACKED", "tick": "DELTA_BINARY_PACKED"})
    sw = pq.ParquetWriter(strings_path, STRINGS_SCHEMA, compression="zstd", use_dictionary=["type", "name", "decoded", "payload"])
    try:
        for k, source in enumerate(match.sources):
            raw = source[0]
            if not Path(raw.path).is_file():
                continue
            rows: dict[str, list] = {c: [] for c in PACKETS_SCHEMA.names if c not in ("time", "part")}
            size = 0
            for item in stream.items(raw.path):
                if item.source == "strings":
                    _strings(sw, source, k, item, counts)
                    continue
                key = type_of(item)
                c = counts.setdefault(key, Counter())
                c["seen"] += 1
                if not bulk and (item.source, item.id) in stream.BULK:
                    continue
                decoded = ""
                decoder = stream.DECODERS.get(item.id) if item.source == "message" else None
                if decoder is not None:
                    try:
                        decoded = json.dumps(decoder(item.payload), ensure_ascii=False, separators=(",", ":"))
                    except (stream.FormatError, ValueError, struct.error):
                        decoded = ""
                c["partial" if decoded or (item.source, item.id) in READ_ELSEWHERE else "raw"] += 1
                rows["tick"].append(item.tick)
                rows["seq"].append(item.seq)
                rows["type"].append(item.type)
                rows["name"].append(item.name)
                rows["id"].append(item.id)
                rows["decoded"].append(decoded)
                rows["payload"].append(bytes(item.payload))
                size += len(item.payload)
                if len(rows["seq"]) >= _FLUSH_ROWS or size >= _FLUSH_BYTES:
                    _flush(pw, rows, source, k)
                    size = 0
            _flush(pw, rows, source, k)
    finally:
        pw.close()
        sw.close()
    return counts


def _flush(writer, rows: dict, source, k: int) -> None:
    if not rows["seq"]:
        return
    t = pa.table({
        "time": pa.array(_times(source, rows["tick"]), pa.float64()),
        "tick": pa.array(rows["tick"], pa.int32()),
        "part": pa.array(np.full(len(rows["seq"]), k), pa.int8()),
        "seq": pa.array(rows["seq"], pa.int64()),
        "type": pa.array(rows["type"], pa.string()),
        "name": pa.array(rows["name"], pa.string()),
        "id": pa.array(rows["id"], pa.int32()),
        "decoded": pa.array(rows["decoded"], pa.string()),
        "payload": pa.array(rows["payload"], pa.binary()),
    }, schema=PACKETS_SCHEMA)
    writer.write_table(t)
    for v in rows.values():
        v.clear()


def _strings(writer, source, k: int, item: stream.Item, counts: dict) -> None:
    cols: dict[str, list] = {c: [] for c in ("tick", "type", "name", "entity", "clientside", "flags", "decoded", "payload")}
    for e in stream.string_tables(item.payload):
        key = f"stringtable {e['table']}"
        c = counts.setdefault(key, Counter())
        c["seen"] += 1
        decoded = ""
        if e["table"] == "userinfo" and e["index"] >= 0 and e["data"]:
            try:
                decoded = json.dumps(stream.player_info(e["data"]), ensure_ascii=False, separators=(",", ":"))
            except (stream.FormatError, ValueError):
                decoded = ""
        c["partial" if decoded else "raw"] += 1
        cols["tick"].append(item.tick)
        cols["type"].append(e["table"])
        cols["name"].append(e["key"])
        cols["entity"].append(e["index"])
        cols["clientside"].append(e["clientside"])
        cols["flags"].append(e["flags"])
        cols["decoded"].append(decoded)
        cols["payload"].append(e["data"])
    if not cols["tick"]:
        return
    n = len(cols["tick"])
    writer.write_table(pa.table({
        "time": pa.array(_times(source, cols["tick"]), pa.float64()),
        "tick": pa.array(cols["tick"], pa.int32()),
        "part": pa.array(np.full(n, k), pa.int8()),
        "snapshot": pa.array(np.full(n, item.seq), pa.int64()),
        "type": pa.array(cols["type"], pa.string()),
        "name": pa.array(cols["name"], pa.string()),
        "entity": pa.array(cols["entity"], pa.int32()),
        "clientside": pa.array(cols["clientside"], pa.bool_()),
        "flags": pa.array(cols["flags"], pa.int32()),
        "decoded": pa.array(cols["decoded"], pa.string()),
        "payload": pa.array(cols["payload"], pa.binary()),
    }, schema=STRINGS_SCHEMA))


# ---------------------------------------------------------------- the self-check


def _entry(seen: int, decoded: int = 0, partial: int = 0, raw: int = 0) -> dict:
    return {"seen": seen, "decoded": decoded, "partial": partial, "raw": raw, "lost": seen - decoded - partial - raw}


def write_sidecars(match, folder: str | Path, bulk: bool = True, levels: str | Path | None = None) -> dict:
    """Write the sidecars beside the match's table (and the `view` one, `view.py`); the `completeness` block of its
    self-check."""
    folder = Path(folder)
    names = {what: folder / f"{match.name}.{what}.parquet" for what in ("events", "props", "strings", "packets")}
    types: dict[str, dict] = {}

    seen, written = write_events(match, names["events"])
    used = events_in_document(match)
    for name in sorted(seen):
        partial = min(used[name], written[name])
        types[name] = _entry(seen[name], partial=partial, raw=written[name] - partial)

    seen, written, unread = write_props(match, names["props"])
    for group in sorted(seen):
        types[group] = _entry(seen[group], raw=written[group])

    for key, c in sorted(write_packets(match, names["packets"], names["strings"], bulk=bulk).items()):
        types[key] = _entry(c["seen"], partial=c["partial"], raw=c["raw"])

    # The parser's tables, whole in the document.
    for key, n in (("header", 1 if match.header else 0), ("playerInfo", len(match.player_info)), ("skins", len(match.skins)),
                   ("itemDrops", len(match.item_drops))):
        if n:
            types[key] = _entry(n, decoded=n)

    from .view import write_view

    view_path = folder / f"{match.name}.view.parquet"
    if write_view(match, view_path, levels):
        names["view"] = view_path
    else:
        view_path.unlink(missing_ok=True)

    out = {
        "rule": RULE,
        "sidecars": [p.name for p in names.values()],
        "types": types,
        "lost": sum(t["lost"] for t in types.values()),
    }
    if unread:
        # Listed by the parser but not readable through it; they are in the entity stream (svc_PacketEntities).
        out["unreadProps"] = unread
    if not bulk:
        out["leftOut"] = sorted(f"{s} {i}" for s, i in stream.BULK)
    return out
