# 3DHeat CS2

**What is it?** Counter-Strike 2 can save a recording of a match, called a
*demo*. This tool turns a demo into files the 3DHeat viewer can show in 3D:
where everyone stood, died, threw and planted, round by round. It can also
turn a CS2 map into a 3D model to show them on.

**Why would I use it?** To review your own matches, to lay many matches of
one map over each other as one heatmap, and for match statistics such as ADR
(average damage a round) and KAST (the share of rounds a player killed,
assisted, survived or was traded).

**Example:** `alpha-vs-bravo-m1.dem` in, `out/de_x/alpha-vs-bravo-m1.3dheat`
out (`de_x` is a made-up map name).

![demos: from demo files to one file a match](https://holdi601.github.io/3DHeat-CS2/assets/img/pipeline.svg)

In more detail: 3DHeat CS2 turns **Counter-Strike 2 demos** into a heatmap table and a match
document per match, and a **CS2 map** into level geometry. The outputs are made
for the [3DHeat](https://holdi601.github.io/3DHeat/) telemetry viewer
([source](https://github.com/Holdi601/3DHeat)), but they
are ordinary files - Parquet, JSON and glTF binary - that anything else can
read too.

It is a small Python package, `heat3d_cs2`, run from the command line. It reads
demos from disk (it downloads none) with
[demoparser2](https://github.com/LaihoE/demoparser), and exports maps from the
installed game with the command-line build of Source2Viewer
([ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)).

## Quick start

New to the command line? Read [Before you start](before-you-start) first.

```bash
pip install -r requirements.txt
python -m heat3d_cs2 demos <demo files or folders> -o out   # every match in them
python -m heat3d_cs2 map <map> -o out/<map>/<map>.glb       # the map from the installed game
python -m heat3d_cs2 scoreboard out/<map>/<match>.3dheat    # a match's scoreboard as text
```

You should see `1 match(es), 1 at a time ...` and then one line per match
(see [Commands](commands#what-is-printed)).

`demos` writes, per match, one file into a folder named after the map:
`out/<map>/<match>.3dheat`, a [`.3dheat` container](output-container) - the
viewer's one-file-a-match format ([spec](https://holdi601.github.io/3DHeat/container.html)).
It holds these members; `--loose` writes them as separate files instead:

| Member | What it holds | Loaded in the viewer's |
|---|---|---|
| `<match>.parquet` (role `table`) | every live player eight times a second with their state (health, money, flash, scoped, zone, inventory, ...), and every event where it happened (kill, death, hurt, shot, throw, grenade detonations, blind, plant, defuse, explode, and a round end per player with what the round paid them), one row each | Heatmap tab |
| `<match>.match.json` (role `match`, the match document) | teams, score, every round (winner, how, economy, plant, kills in order, clutches, survivors) and every player's scoreboard line | Match tab |
| `<match>.events/props/strings/packets.parquet` | everything else the demo holds, whole (sidecars) | kept for completeness |

`map` writes `<map>.glb`: the map's collision mesh - floors, walls, boxes,
without decoration - split into ground and structure, in the same frame and
units as the tables, so it lies exactly under the heatmap (Background / level panel).

## Map of this documentation

| Page | What it covers |
|---|---|
| [Before you start](before-you-start) | Python, a terminal, placeholders, what success and the common errors look like |
| [Installing](installing) | Python, the packages, Source2Viewer's CLI, where CS2 must be |
| [Commands](commands) | `demos`, `map`, `scoreboard`: every option, what is printed, exit codes |
| [Reading a demo](reading-demos) | what is read from a demo file: sampled ticks, player properties, game rules, events |
| [Building a match](building-matches) | parts and chains, the match clock, rounds, teams and sides, rows, kills, trades, openings, damage, flashes, economy |
| [Statistics](statistics) | the scoreboard: K/D/A, ADR, KAST, HS%, openings, trades, multi-kills, clutches, utility, flashes |
| [The heatmap table](output-table) | the Parquet file: every column, its type, which events fill it, the `heat3d` footer hints, the axes |
| [The match document](output-match-json) | the `.match.json` document, field by field |
| [One file a match](output-container) | the `.3dheat` container `demos` writes by default, `--loose` |
| [Map export](map-export) | how a map's collision mesh is exported, the frame, node naming, units |
| [Using it with 3DHeat](using-with-3dheat) | loading tables, match documents and maps into the viewer's Heatmap and Match tabs |
| [Limits](limits) | what is assumed, what is not handled, what is unverified |
| [Updates](updates) | the release check at start-up and `python -m heat3d_update` |
| [Development](development) | code layout, tests, the synthetic demo fixture |
| [Command reference](cli-reference) | every command's `--help`, generated from the code |
| [Maintaining](maintaining) | the release checklist for these pages |

## What it is checked against

Demos from the wild are not one clean file per match. The converter handles a
match split across files in any order, a server restarted mid-match, two
different matches stored under one name, rounds restored from a backup, a
recording that starts late or ends early, pauses, and coaches on a team's side -
see [Building a match](building-matches). Checked over a large collection
of tournament demos: in every match the
score follows the round winners, each side's kills are the other side's deaths,
and every round starts five against five.

## What to point it at

Your own matches' demos, demos you downloaded by hand from a tournament site, or
demos from an API you have access to. A demo is a recording whose content
belongs to its publisher and organisers: use what comes out for your own
analysis, and do not redistribute demos or data derived from them. The tool
reads demos from disk and downloads none, and nothing from the game ships with
it: no game files, no game code, no DLLs.

3DHeat CS2 is not affiliated with or endorsed by Valve. Counter-Strike 2 and
related names and trademarks belong to their owners. Rights holders: open an
issue at
[github.com/Holdi601/3DHeat-CS2/issues](https://github.com/Holdi601/3DHeat-CS2/issues) -
we respond quickly and remove anything on request.

## Part of 3DHeat

3DHeat CS2 is one of the free tools around the 3DHeat viewer, each its own
repository with its own releases and licence:

| Tool | What it does | Docs |
|---|---|---|
| [3DHeat](https://github.com/Holdi601/3DHeat) | the viewer: heatmaps, race analysis and match review in 3D | [site](https://holdi601.github.io/3DHeat/) |
| [GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | courses and levels out of the files games ship, as 3D models | [site](https://holdi601.github.io/3DHeat-GameFiles/) |
| [GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | lap telemetry from racing games; levels rebuilt from gameplay video | [site](https://holdi601.github.io/3DHeat-GameCapture/) |
| [Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | an Unreal Editor plugin that exports a level as one 3D model | [site](https://holdi601.github.io/3DHeat-UnrealExporter/) |
| [CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demos into tables and match documents; maps into 3D models | [site](https://holdi601.github.io/3DHeat-CS2/) |
| [Watcher](https://github.com/Holdi601/3DHeat-Watcher) | records what games publish about your play, in the background | [site](https://holdi601.github.io/3DHeat-Watcher/) |
| [Ext-WarThunder](https://github.com/Holdi601/3DHeat-Ext-WarThunder) | War Thunder replays into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-WarThunder/) |
| [Ext-WoT](https://github.com/Holdi601/3DHeat-Ext-WoT) | World of Tanks replays into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-WoT/) |
| [Ext-WoWs](https://github.com/Holdi601/3DHeat-Ext-WoWs) | World of Warships replays into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-WoWs/) |
| [Ext-Squad](https://github.com/Holdi601/3DHeat-Ext-Squad) | Squad server demos into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-Squad/) |
| [Ext-DCS](https://github.com/Holdi601/3DHeat-Ext-DCS) | DCS World maps into 3D models | [site](https://holdi601.github.io/3DHeat-Ext-DCS/) |
| [Ext-IL2](https://github.com/Holdi601/3DHeat-Ext-IL2) | IL-2 Sturmovik maps into 3D models | [site](https://holdi601.github.io/3DHeat-Ext-IL2/) |
| [Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota) | the Dota 2 map from your own install as a 3D level | [site](https://holdi601.github.io/3DHeat-Ext-Dota/) |
| [Ext-DotaReplay](https://github.com/Holdi601/3DHeat-Ext-DotaReplay) | Dota 2 replays | [site](https://holdi601.github.io/3DHeat-Ext-DotaReplay/) |
| [Ext-Riot](https://github.com/Holdi601/3DHeat-Ext-Riot) | League of Legends and VALORANT replays (what they carry unencrypted) | [site](https://holdi601.github.io/3DHeat-Ext-Riot/) |
| [Ext-Forza](https://github.com/Holdi601/3DHeat-Ext-Forza) | Forza courses, races and cars from your own install | [site](https://holdi601.github.io/3DHeat-Ext-Forza/) |
| [Ext-Battlefield](https://github.com/Holdi601/3DHeat-Ext-Battlefield) | Battlefield levels (Frostbite) as 3D levels | [site](https://holdi601.github.io/3DHeat-Ext-Battlefield/) |
| [Ext-BeamNG](https://github.com/Holdi601/3DHeat-Ext-BeamNG) | BeamNG.drive courses | [site](https://holdi601.github.io/3DHeat-Ext-BeamNG/) |
| [Ext-ACRally](https://github.com/Holdi601/3DHeat-Ext-ACRally) | Assetto Corsa Rally stages as courses | [site](https://holdi601.github.io/3DHeat-Ext-ACRally/) |
| [Ext-Reforger](https://github.com/Holdi601/3DHeat-Ext-Reforger) | Arma Reforger worlds (Enfusion) as 3D levels | [site](https://holdi601.github.io/3DHeat-Ext-Reforger/) |
| [Ext-R6](https://github.com/Holdi601/3DHeat-Ext-R6) | Rainbow Six Siege match replays | [site](https://holdi601.github.io/3DHeat-Ext-R6/) |

## Licence

MIT - see [`LICENSE`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSE),
and [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md)
for the third-party packages.
