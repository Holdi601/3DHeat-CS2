
# 3DHeat CS2

3DHeat CS2 turns **Counter-Strike 2 demos** into a heatmap table and a match
summary per match, and a **CS2 map** into level geometry. The outputs are made
for the [3DHeat](https://holdi601.github.io/3DHeat-Docs) telemetry viewer, but they
are ordinary files - Parquet, JSON and glTF binary - that anything else can
read too.

It is a small Python package, `heat3d_cs2`, run from the command line. It reads
demos from disk (it downloads none) with
[demoparser2](https://github.com/LaihoE/demoparser), and exports maps from the
installed game with the command-line build of Source2Viewer
([ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)).

## Quick start

```bash
pip install -r requirements.txt
python -m heat3d_cs2 demos <demo files or folders> -o out          # every match in them
python -m heat3d_cs2 map de_mirage -o out/de_mirage/de_mirage.glb  # the map from the installed game
python -m heat3d_cs2 scoreboard out/de_mirage/<match>.match.json   # a match's scoreboard as text
```

`demos` writes, per match, into a folder named after the map:

| File | What it holds | Loaded in the viewer's |
|---|---|---|
| `out/<map>/<match>.parquet` | every live player eight times a second, and every event where it happened (kill, death, hurt, shot, throw, grenade detonations, blind, plant, defuse, explode), one row each | Heatmap tab |
| `out/<map>/<match>.match.json` | teams, score, every round (winner, how, economy, plant, kills in order, clutches, survivors) and every player's scoreboard line | Match tab |

`map` writes `<map>.glb`: the map's collision mesh - floors, walls, boxes,
without decoration - split into ground and structure, in the same frame and
units as the tables, so it lies exactly under the heatmap (Level panel).

## Map of this documentation

| Page | What it covers |
|---|---|
| [Installing](installing) | Python, the packages, Source2Viewer's CLI, where CS2 must be |
| [Commands](commands) | `demos`, `map`, `scoreboard`: every option, what is printed, exit codes |
| [Reading a demo](reading-demos) | what is read from a demo file: sampled ticks, player properties, game rules, events |
| [Building a match](building-matches) | parts and chains, the match clock, rounds, teams and sides, rows, kills, trades, openings, damage, flashes, economy |
| [Statistics](statistics) | the scoreboard: K/D/A, ADR, KAST, HS%, openings, trades, multi-kills, clutches, utility, flashes |
| [The heatmap table](output-table) | the Parquet file: every column, its type, which events fill it, the `heat3d` footer hints, the axes |
| [The match summary](output-match-json) | the `.match.json` document, field by field |
| [Map export](map-export) | how a map's collision mesh is exported, the frame, node naming, units |
| [Using it with 3DHeat](using-with-3dheat) | loading tables, summaries and maps into the viewer's Heatmap and Match tabs |
| [Limits](limits) | what is assumed, what is not handled, what is unverified |
| [Updates](updates) | the release check at start-up and `python -m heat3d_update` |
| [Development](development) | code layout, tests, the synthetic demo fixture |

## What it is checked against

Demos from the wild are not one clean file per match. The converter handles a
match split across files in any order, a server restarted mid-match, two
different matches stored under one name, rounds restored from a backup, a
recording that starts late or ends early, pauses, and coaches on a team's side -
see [Building a match](building-matches). The repository's README states the
checks run over a large collection of tournament demos: in every match the
score follows the round winners, each side's kills are the other side's deaths,
and every round starts five against five.

## What to point it at

Your own matches' demos, demos you downloaded by hand from a tournament site,
or demos from an API you have access to. A demo is a recording whose content
belongs to its publisher and organisers: use what comes out for your own
analysis, and do not redistribute demos or data derived from them. Sites that
offer demos often forbid automated downloading in their terms, which is why
the tool reads demos from disk and fetches none.

## Part of 3DHeat

3DHeat CS2 is one of several free tools around the 3DHeat viewer, each its own
repository with its own releases and licence:

| Tool | What it does |
|---|---|
| [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | courses and levels out of the archives games ship, as glTF |
| [3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | lap telemetry from racing games' published interfaces; levels reconstructed from gameplay video |
| [3DHeat Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | an Unreal Editor plugin that exports a level as glTF |
| [3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2) | this tool |
| [3DHeat Watcher](https://github.com/Holdi601/3DHeat-Watcher) | records your play in the background from what games publish |

## Licence

MIT - see [`LICENSE`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSE),
and [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md)
for the third-party packages and what the games it reads oblige.
