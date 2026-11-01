---
title: Development
nav_order: 13
---

# Development

## Layout

| Path | What |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: the release check, then the command line |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | the verbs and options; grouping demo files into matches; the worker pool |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | one demo file through demoparser2 into a `RawPart` - [Reading a demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | parts, chains, the clock, rounds, teams, rows, kills, damage, blinds - [Building a match](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | round summaries, the scoreboard, the summary document, the text scoreboard - [Statistics](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | the Parquet table with its `heat3d` hints, and the JSON - [The heatmap table](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | finding CS2 and Source2Viewer, the collision mesh into the viewer's frame - [Map export](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | a minimal glTF binary reader and writer (no dependency beyond numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | the release check and the updater - [Updates](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | the tests and the synthetic demo |
| `VERSION` | the version, one line |

The data flow:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Using it from Python

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # the heatmap table as a pandas DataFrame
    kills = match.kills        # one row per death, with every flag
    doc = summary(match)       # the .match.json document as a dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` and `Match.blinds` are pandas DataFrames with
more than the outputs carry - attacker and victim positions and places per
kill, per-hit `utility` - for analyses of your own.

## Tests

```bash
python -m pytest
```

`pytest.ini` runs `tests/` quietly. The tests need no demo, no game and no
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
builds a demo by hand, as demoparser2 would give it - two rounds, two
players a side (`ace`, `ash` of team Alpha; `bob`, `ben` of Bravo), small
enough that every answer is known:

- Round 1, a T win by elimination: ace kills bob with a headshot (the
  opening), ben kills ace 1.9 s later (a trade: bob's death is traded), ash
  kills ben 3.1 s after that - alone against one, a clutch won.
- Round 2, a T win by the bomb: ash plants on A, nobody dies, the bomb goes
  off.

`fixtures.halves` builds a longer match of empty rounds, the teams on their
first sides or swapped, with the game's overtime count or without, for the
half length and the pistol rounds.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
checks on it: each round's winner, reason, score and sides; the clock
starting at the match; economy and the plant (its time into the round, its
place, the bomb going off); a plant's site always a letter or empty, never
an entity number; a draw decided with no winner; the pistol rounds from
where the sides swap, overtime left out, and only round 1 without a swap;
teams without clan names (`Started T` / `Started CT`); openings, trades and
flags; a suicide that is no teamkill, and the opening passed on to the first
enemy kill; `noscope` and `attackerBlind` in the table and the summary;
damage as health lost (60, then 40 of a 137 on 40 health); the scoreboard
numbers and KAST; clutches; the text scoreboard; the events of the table and
where they are (a detonation with no place of its own, the thrower's in
`throwerPlace`; the explosion the planting team's); that positions are live,
labelled and have unit look vectors; that the written file carries its
hints; parts put in order whatever their names; a restarted server clock
that still follows on; and a restored round's duplicate rows resolved to the
one that leads on.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
checks that demos in folders are found whatever the case of `.dem`, and that
a match counts as written only with both its table and its summary.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
checks the frame conversions (Source2Viewer's metres to the game's inches,
and on to the viewer's frame, a rotation with determinant 1), that clips and
sky are left out whatever the case and surfaces named, the ground/structure split by normal,
and a `.glb` written and read back.

### The floor check on a real map

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

With both variables set, `test_players_stand_on_the_exported_floor` also
runs: it converts the demo, exports its map from the installed game, and
checks that at least 98 % of 300 random position samples have ground under
them, with a median height above it under 5 units
([Map export](map-export.md#the-check-that-the-frame-is-right)).

## Conventions of the code

- Times inside `match.py` are match seconds, except a plant's `time`,
  seconds into its round as the summary writes it; ticks become seconds only
  through `_Part.at`.
- Sides are `T` / `CT` strings everywhere outside the raw parser data
  (`team_num` 2 / 3).
- A new table column goes into `ROW_COLUMNS` (and `NUMERIC` if numeric) in
  `match.py`; `output.table` picks its Parquet type from the sets `INT16`,
  `INT32`, `FLOAT64` and the 0/1 flags, float32 otherwise.
- Changing what the viewer should do with a column means changing `HINTS` in
  `output.py`.

## Licence

MIT. Third-party packages and what the games oblige:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demos and maps are never part of the repository; its `.gitignore` keeps
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` and the like out by type.
