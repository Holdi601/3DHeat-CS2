---
title: Using it with 3DHeat
nav_order: 10
---

# Using it with 3DHeat

The three outputs go into three places of the
[3DHeat viewer](https://holdi601.github.io/3DHeat-Docs):

| File | Where | What it gives |
|---|---|---|
| `<match>.parquet` | **Heatmap** tab, **Source** panel | positions and events as a heatmap, box replay, routes |
| `<match>.match.json` | **Match** tab, **Load match files…** | the scoreboard, the rounds, the kill feed, statistics across matches, links into the heatmap |
| `<map>.glb` | **Background / level** panel, **3D model…** | the map under the heatmap |

The viewer's own documentation describes each tab in full: its
[Match analysis](https://holdi601.github.io/3DHeat-Docs/match-analysis.html),
[Loading files](https://holdi601.github.io/3DHeat-Docs/loading-files.html),
[Column mapping](https://holdi601.github.io/3DHeat-Docs/column-mapping.html)
and [Box replay](https://holdi601.github.io/3DHeat-Docs/box-replay.html)
pages. This page is the CS2 side of it.

## A typical session

```bash
python -m heat3d_cs2 demos D:\Demos\event -o out
python -m heat3d_cs2 map de_inferno -o out/de_inferno/de_inferno.glb
```

1. **Heatmap tab -> Source:** choose the folder `out/de_inferno` (or drop it).
   Every `.parquet` in it becomes one dataset; the `.json` and `.glb` files in
   the same folder are skipped as "not a csv/parquet file". Load it.
2. **Background / level -> 3D model…:** pick `out/de_inferno/de_inferno.glb`.
   **Save to library** keeps it in the browser for next time.
3. **Match tab -> Load match files…:** pick the `.match.json` files of the
   same folder (several at once), or drop them on the view while the Match
   tab is open.

Load only one map's tables at a time: the coordinates of different maps
overlap, and a heatmap of two maps at once means nothing. The folder per map
is there for that.

## The table opens with nothing to set

The viewer reads the first selected file's `heat3d` footer entry
([The heatmap table](output-table.md#the-heat3d-footer-hints)) and lays it
over its own guesses:

| Viewer setting | Set to |
|---|---|
| Position | `x`, `y`, `z` |
| Up axis in source | Z is up |
| Flip Y | on - so the map is the right way round, not mirrored |
| Unit scale | 1 - distances in game units (labelled "m"; 1 unit = 1 inch) |
| Time | `time`, seconds |
| Person | `player` |
| Group | `side` (T / CT) |
| Session | `roundId` - each round is a session, `<match> #NN` |
| Look direction | vector, `dirX` / `dirY` / `dirZ` |
| Filter columns | `event`, `match`, `round`, `roundTime`, `phase`, `weapon`, `place`, `won`, `buy`, `opening`, `team` |
| Entity size | 32 - the box replay draws a player 32 units across, with a look ray of 4 x 32 |

Every hinted value still shows in the column mapping and can be changed. The
other columns (`headshot`, `traded`, `other`, `steamid`, `health`, `money`,
`damage`, `duration`, ...) can be added as filters there by hand.

Keep the unit scale at 1 when a map is loaded: the `.glb` is in the same game
units, and the level is not rescaled with the table.

### Useful filters

- `event` = `position` for where players were; `kill` / `death` for where
  duels were won and lost; `smoke`, `flash`, `molotov`, `he` for where
  utility landed; `throw` for where it was thrown from; `plant` for plant
  spots.
- `side` (the group) = `T` or `CT`, `phase` = `live` to leave out the after
  phase, `buy` = `eco` / `force` / `full` for rounds of one economy,
  `won` = 1 for rounds the row's side won.
- `opening` = 1 with `kill` and `death` for the opening duels.
- `roundTime` as a range for a moment of the round: the first 20 seconds,
  the post-plant.

## The match tab

The Match tab accepts a JSON file whose `format` is `heat3d-cs2-match` and
which has `rounds`, `players` and `teams` arrays
([The match summary](output-match-json.md)). It shows the score and halves,
a strip of rounds coloured by the winning side with a mark for how each ended,
each round's economy, plant, kill feed, clutches and survivors, the scoreboard,
and statistics across all loaded matches.

Its **Show in the heatmap** links do not load anything: they set filters on
the table already loaded in the Heatmap tab - `match`, `round` (and the
round's session `<match> #NN`), `event`, the player, the side. That works
because the summary and the table carry the same match names, round numbers,
player names and sides. **Replay round** switches the heatmap to box replay
and plays the round's session from its start.

So load both: the tables of a map in the Heatmap tab, their summaries in the
Match tab. A summary without its table still shows the scoreboard and rounds,
and the links say that no heatmap data is loaded.

## Without 3DHeat

- The table is plain Parquet: pandas, Polars, DuckDB, Spark, R's `arrow` all
  read it, the `heat3d` entry is ignored, and the text columns read as strings
  or categoricals.
- The summary is plain JSON.
- The map is a valid glTF binary, in inches rather than metres: scale by
  0.0254 for tools that assume metres. Its frame is glTF's own (Y up), so to
  overlay the table elsewhere draw each row's (x, y, z) as (x, z, -y), as
  3DHeat does.
