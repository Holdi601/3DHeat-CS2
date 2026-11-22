---
title: Reference
nav_order: 16
---

# Command and column reference

Generated from the code by `tools/gen_docs_reference.py`. The other pages explain each
command step by step; this one lists everything exactly as the program has it.

## `python -m heat3d_cs2`

```text
usage: heat3d_cs2 [-h] {demos,map,layouts,scoreboard} ...

CS2 demos and maps for the 3DHeat viewer

positional arguments:
  {demos,map,layouts,scoreboard}
    demos               demos -> one heatmap table and one match document per match
    map                 a map's collision geometry -> .glb in the demos' frame
    layouts             a map's bomb sites, buy zones, hostage spots and spawns ->
                        <map>.layouts.json
    scoreboard          print a match's scoreboard

options:
  -h, --help            show this help message and exit
```

## `demos`

```text
usage: heat3d_cs2 demos [-h] -o OUT [--every EVERY] [--jobs JOBS] [--map MAP]
                        [--force] [--no-bulk] [--container] [--loose]
                        paths [paths ...]

positional arguments:
  paths          demo files or folders

options:
  -h, --help     show this help message and exit
  -o, --out OUT  folder to write into
  --every EVERY  sample players every N ticks (64 a second; default 8: 8 a second)
  --jobs JOBS    matches converted at once (default: half the cores)
  --map MAP      only matches whose file name contains this text
  --force        rewrite matches already written
  --no-bulk      leave the entity stream, the players' commands and the animation
                 (over half a demo's size) out of the packets sidecar; the self-check
                 counts them lost
  --container    pack each match into one .3dheat file (the default)
  --loose        keep each match as separate files (table, match.json, sidecars), not
                 one .3dheat container
```

## `map`

```text
usage: heat3d_cs2 map [-h] -o OUT [--game GAME] [--source2viewer SOURCE2VIEWER] name

positional arguments:
  name                  the map's name (like de_x) or the path to its .vpk

options:
  -h, --help            show this help message and exit
  -o, --out OUT         .glb to write
  --game GAME           the CS2 install folder, when Steam does not know it
  --source2viewer SOURCE2VIEWER
                        Source2Viewer-CLI executable, when it is not on PATH
```

## `layouts`

```text
usage: heat3d_cs2 layouts [-h] -o OUT [--game GAME] [--source2viewer SOURCE2VIEWER]
                          names [names ...]

positional arguments:
  names                 maps by name (like de_x) or .vpk path; `all` for every map
                        with a .glb in the output folder

options:
  -h, --help            show this help message and exit
  -o, --out OUT         the folder to write into (beside the maps' .glb), or a .json
                        for one map
  --game GAME           the CS2 install folder, when Steam does not know it
  --source2viewer SOURCE2VIEWER
                        Source2Viewer-CLI executable, when it is not on PATH
```

## `scoreboard`

```text
usage: heat3d_cs2 scoreboard [-h] match

positional arguments:
  match       <match>.3dheat, or <match>.match.json from --loose

options:
  -h, --help  show this help message and exit
```

## Columns of the files `demos` writes

Read from a conversion of the tests' synthetic demo. What each column means:
[The heatmap table](output-table.md) and [One file a match](output-container.md).

### `<match>.parquet` (role `table`)

| Column | Type |
|---|---|
| `match` | dictionary<values=string, indices=int32, ordered=0> |
| `map` | dictionary<values=string, indices=int32, ordered=0> |
| `round` | int16 |
| `roundId` | dictionary<values=string, indices=int32, ordered=0> |
| `phase` | dictionary<values=string, indices=int32, ordered=0> |
| `time` | double |
| `roundTime` | float |
| `event` | dictionary<values=string, indices=int32, ordered=0> |
| `player` | dictionary<values=string, indices=int32, ordered=0> |
| `steamid` | dictionary<values=string, indices=int32, ordered=0> |
| `side` | dictionary<values=string, indices=int32, ordered=0> |
| `team` | dictionary<values=string, indices=int32, ordered=0> |
| `x` | float |
| `y` | float |
| `z` | float |
| `dirX` | float |
| `dirY` | float |
| `dirZ` | float |
| `health` | int16 |
| `armor` | int16 |
| `money` | int32 |
| `equipment` | int32 |
| `weapon` | dictionary<values=string, indices=int32, ordered=0> |
| `place` | dictionary<values=string, indices=int32, ordered=0> |
| `throwerPlace` | dictionary<values=string, indices=int32, ordered=0> |
| `other` | dictionary<values=string, indices=int32, ordered=0> |
| `damage` | float |
| `duration` | float |
| `headshot` | int8 |
| `opening` | int8 |
| `traded` | int8 |
| `noscope` | int8 |
| `attackerBlind` | int8 |
| `won` | int8 |
| `matchWon` | int8 |
| `roundEndReason` | dictionary<values=string, indices=int32, ordered=0> |
| `buy` | dictionary<values=string, indices=int32, ordered=0> |
| `detail` | dictionary<values=string, indices=int32, ordered=0> |
| `hitgroup` | dictionary<values=string, indices=int32, ordered=0> |
| `assister` | dictionary<values=string, indices=int32, ordered=0> |
| `text` | dictionary<values=string, indices=int32, ordered=0> |
| `hitFrom` | dictionary<values=string, indices=int32, ordered=0> |
| `attackerSide` | dictionary<values=string, indices=int32, ordered=0> |
| `entity` | int32 |
| `armorDamage` | int16 |
| `penetrated` | int16 |
| `throughSmoke` | int8 |
| `distance` | float |
| `punchPitch` | float |
| `punchYaw` | float |
| `hitLocalX` | float |
| `hitLocalY` | float |
| `hitLocalZ` | float |
| `hitDirX` | float |
| `hitDirY` | float |
| `hitDirZ` | float |
| `hitMiss` | float |
| `attackerX` | float |
| `attackerY` | float |
| `attackerZ` | float |
| `flash` | float |
| `flashAlpha` | float |
| `helmet` | int8 |
| `defuser` | int8 |
| `scoped` | int8 |
| `zoom` | int16 |
| `walking` | int8 |
| `duck` | float |
| `airborne` | int8 |
| `buyZone` | int8 |
| `bombZone` | int8 |
| `defusing` | int8 |
| `spotted` | int8 |
| `spottedBy` | dictionary<values=string, indices=int32, ordered=0> |
| `inventory` | dictionary<values=string, indices=int32, ordered=0> |
| `ammo` | int16 |
| `ammoReserve` | int16 |
| `shotsFired` | int16 |
| `moveType` | int16 |
| `ping` | int16 |
| `killsTotal` | int16 |
| `deathsTotal` | int16 |
| `assistsTotal` | int16 |
| `headshotKillsTotal` | int16 |
| `damageTotal` | int32 |
| `utilityDamageTotal` | int32 |
| `enemiesFlashedTotal` | int16 |
| `objectiveTotal` | int16 |
| `aceRoundsTotal` | int16 |
| `threeKillRoundsTotal` | int16 |
| `aliveTimeTotal` | int32 |
| `moneySavedTotal` | int32 |
| `mvps` | int16 |
| `score` | int16 |
| `cashSpent` | int32 |
| `cashSpentTotal` | int32 |
| `roundStartEquipment` | int32 |
| `state_helmet` | int8 |
| `state_defuser` | int8 |
| `state_kevlar` | int8 |
| `state_scoped` | int8 |
| `state_flashed` | int8 |
| `state_utility` | int16 |
| `state_weapon` | dictionary<values=string, indices=int32, ordered=0> |
| `earn_round_cs2` | int16 |

### `<match>.events.parquet` (role `events`)

| Column | Type |
|---|---|
| `time` | double |
| `tick` | int32 |
| `part` | int8 |
| `type` | string |
| `name` | string |
| `player` | string |
| `entity` | int32 |
| `decoded` | string |

### `<match>.packets.parquet` (role `packets`)

| Column | Type |
|---|---|
| `time` | double |
| `tick` | int32 |
| `part` | int8 |
| `seq` | int64 |
| `type` | string |
| `name` | string |
| `id` | int32 |
| `decoded` | string |
| `payload` | binary |

### `<match>.props.parquet` (role `props`)

| Column | Type |
|---|---|
| `time` | double |
| `tick` | int32 |
| `part` | int8 |
| `type` | string |
| `name` | string |
| `player` | string |
| `entity` | int32 |
| `value` | double |
| `vector` | list<element: double> |
| `decoded` | string |

### `<match>.strings.parquet` (role `strings`)

| Column | Type |
|---|---|
| `time` | double |
| `tick` | int32 |
| `part` | int8 |
| `snapshot` | int64 |
| `type` | string |
| `name` | string |
| `entity` | int32 |
| `clientside` | bool |
| `flags` | int32 |
| `decoded` | string |
| `payload` | binary |

### `<match>.match.json` (role `match`)

Top-level keys: `format`, `version`, `match`, `map`, `demos`, `teams`, `score`, `winner`, `winnerSource`, `rounds`, `incomplete`, `missing`, `halfLength`, `pistolRounds`, `players`, `header`, `profiles`, `playerInfo`, `skins`, `itemDrops`, `chat`, `events`, `state`, `conventions`, `selfCheck`. Field by field: [The match document](output-match-json.md).
