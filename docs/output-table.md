---
title: The heatmap table
nav_order: 7
---

# The heatmap table (`<match>.parquet`)

One Parquet file per match: every live player's position, sampled, and every
event where it happened, one row each - a long table the 3DHeat viewer reads
as a heatmap, and anything else as an ordinary table. Code:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(the file), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(the rows; see [Building a match](building-matches.md)).

The file is written with Snappy compression in row groups of 256,000 rows.
Rows are sorted by `time`, then by `event`. Only rows inside a round (from
the end of its freeze time to the next round's start) are in it.

## Columns

35 columns, always in this order. Text columns are dictionary-encoded strings
(`dictionary<int32, string>`) and are never null: "no value" is an empty
string. Numeric columns are null where a row has no value.

| Column | Type | What |
|---|---|---|
| `match` | string | the match name (`alpha-vs-bravo-m1`, or `...-b` for a second chain) |
| `map` | string | the map, from the demo header (`de_inferno`) |
| `round` | int16 | the round number, 1-based |
| `roundId` | string | `<match> #NN`, the round number in two digits (`alpha-vs-bravo-m1 #07`): unique across matches, the viewer's session |
| `phase` | string | `live` until the round is decided, `after` while the winners hunt and the losers save |
| `time` | float64 | seconds since the match started (the live start of its first file), on one clock across its files |
| `roundTime` | float32 | seconds since this round's freeze time ended |
| `event` | string | what the row is - see [Events](#events) |
| `player` | string | the player's name (for each event, which player is said below) |
| `steamid` | string | the player's Steam ID (64-bit, as text) |
| `side` | string | `T` or `CT` this round; empty when the player was on no side |
| `team` | string | the player's team name (or `Started T` / `Started CT`); for `explode`, the planting team |
| `x`, `y`, `z` | float32 | position in the game's own coordinates: inches (game units), **Z up**, right-handed |
| `dirX`, `dirY`, `dirZ` | float32 | where the player looks, a unit vector in the same frame; positions only |
| `health` | int16 | 0-100; positions only |
| `armor` | int16 | 0-100; positions only |
| `money` | int32 | the player's money; positions only |
| `equipment` | int32 | the value of what the player carries; positions only |
| `weapon` | string | the weapon as the game names it (`AK-47`, `M4A1-S`, `Knife` for every knife skin) |
| `place` | string | the map's own place name at the row's position (`BombsiteA`, `TopofMid`, `CTSpawn`); empty on grenade detonations: the demo names no place for where a grenade went off |
| `throwerPlace` | string | the thrower's place name when the grenade went off; grenade detonations only |
| `other` | string | the other player of a kill, death, hit or flash |
| `damage` | float32 | health lost; `hurt` only |
| `duration` | float32 | seconds blinded; `blind` only |
| `headshot` | int8 | 0/1; `kill` and `death` only |
| `opening` | int8 | 0/1, the round's first kill of an enemy; `kill` and `death` only |
| `traded` | int8 | 0/1. For a `kill`: it was a trade kill. For a `death`: it was avenged within 5 s. `kill` and `death` only. |
| `noscope` | int8 | 0/1, the kill was with a scoped weapon fired unscoped (the event's `noscope`); `kill` and `death` only |
| `attackerBlind` | int8 | 0/1, the killer was flashed when they killed (the event's `attackerblind`); `kill` and `death` only |
| `won` | int8 | 0/1, whether this row's side won the round; null when `side` is empty |
| `buy` | string | this row's side's buy this round: `pistol`, `eco`, `force`, `full` |

## Events

Which player a row names, where it stands, and which columns it fills.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won` and `buy` are filled on every row.

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Also filled |
|---|---|---|---|
| `position` | the player | the player (feet) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (held), `place` |
| `kill` | the killer | where the killer stood | `other` (victim), `weapon`, `headshot`, `opening`, `traded` (a trade kill), `noscope`, `attackerBlind`, `place` |
| `death` | the victim | where the victim fell | `other` (killer; empty for the world), `weapon`, `headshot`, `opening`, `traded` (avenged), `noscope`, `attackerBlind`, `place` |
| `hurt` | the victim | where the victim was hit | `other` (attacker), `damage`, `weapon`, `place` |
| `shot` | the shooter | where the shot was fired from | `weapon`, `place` |
| `throw` | the thrower | where the grenade was thrown from | `weapon` (the grenade), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | the thrower | where it went off | `weapon`, `throwerPlace` (the thrower's place at that moment); `place` stays empty |
| `blind` | the player flashed | where they stood | `other` (flasher), `duration`, `weapon` = `Flashbang`, `place` |
| `plant` | the planter | where they planted | `weapon` = `C4 Explosive`, `place` |
| `defuse` | the defuser | where they defused | `weapon` = `C4 Explosive`, `place` |
| `explode` | the planter (with their Steam ID), side `T`, the planting team | the plant's position | `weapon` = `C4 Explosive`, `place` (the planter's at the plant: where the bomb lay); its time is when the bomb went off |

What is in and what is not:

- **position** rows are living players on a side, outside freeze time and
  warmup, every `--every` ticks (eight a second by default).
- **kill** rows are kills by an enemy only - no teamkill, suicide or death to
  the world. **death** rows are every death, those included.
- **explode** rows are every planted bomb that went off, by the demo's
  `bomb_exploded`: in the after phase too, when the Ts had already won by
  elimination. A demo without that event gets one for each round won by the
  bomb, at the round's end.
- **hurt** and **blind** rows are between enemies only.
- **shot** leaves out knives and the C4; grenades are **throw** rows.
- **molotov** covers molotovs and incendiaries (the fire starting).
- Teammates' damage, flashes of teammates and spectators, freeze-time
  events and anything between rounds are not in the table.

A worked example, from the synthetic demo of the tests (a smoke thrown, a
headshot opening kill, trades):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

bob's death is avenged by ben's kill of ace 1.9 s later (bob's `death` row:
traded 1; ben's `kill` row: a trade kill, traded 1); the second hit on bob was
137 damage on 40 health, so it counts 40.

## The `heat3d` footer hints

The file's Parquet footer (schema key/value metadata) carries reading
instructions under the key **`heat3d`**, a JSON object:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Entry | Says |
|---|---|
| `version`, `kind` | the hints' version (1) and what wrote them (`cs2-demo`) |
| `axes.up` | the file's Z is up |
| `axes.flipY` | negate the file's Y (see below) |
| `axes.scale` | 1: positions are used as they are, in game units |
| `entity.size` | a player is **32 units** across - the CS2 player's width - the size a box replay draws one |
| `columns.x` / `y` / `z` | the position columns |
| `columns.time`, `timeUnit` | `time`, in seconds |
| `columns.personId` | the player is the person |
| `columns.teamId` | the side is the group (so T and CT, not the team names, colour the groups) |
| `columns.sessionId` | each round (`roundId`) is a session |
| `columns.lookMode` and `dirX`-`dirZ` | the look direction is a vector in those columns |
| `columns.extra` | the columns to keep as filters, in order of usefulness |

A viewer that knows the key opens the file with nothing to set. Anything else
ignores it. To read it yourself:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_inferno/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Axes and units

The coordinates are the game's own: **inches** (one game unit; a player is 72
units tall standing and 32 across), **Z up**, and right-handed.

A viewer whose world is Y-up must draw the game's (x, y, z) as
**(x, z, -y)** - Z becomes the height and Y is negated. That is a rotation,
not a mirror. Drawn the way a left-handed Z-up world is, as (x, z, y), every
map comes out mirrored, A site on the wrong side; `flipY: true` is what the
hints say to prevent it. The [map export](map-export.md) writes its geometry
already in the (x, z, -y) frame, in the same units, so it lies under the
table without any adjustment.

Distances in the viewer are labelled in metres; with a scale of 1 they are
game units. Multiply by 0.0254 for metres.

## Size

Positions dominate: about ten players x 8 samples a second of live play at
the default `--every 8`, less for dead players and freeze time. Halving
`--every` doubles them; events are unaffected.
