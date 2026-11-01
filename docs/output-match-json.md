---
title: The match summary
nav_order: 8
---

# The match summary (`<match>.match.json`)

One JSON document per match, next to its table: teams, score, every round
with its result, economy, plant, kills, clutches and survivors, and every
player's scoreboard line. It is what the 3DHeat viewer's Match tab loads.
Code: `summary()` in
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
the numbers are defined on [Statistics](statistics.md).

The file is UTF-8, indented by one space, and keeps non-ASCII characters
(player and team names) as they are. Times are seconds, rounded to three
decimals for rounds and two for kills and the plant.

## The document

| Field | Type | What |
|---|---|---|
| `format` | string | always `heat3d-cs2-match` - how a reader recognises the file |
| `version` | number | `2`. A version 1 document gives a plant's `time` in match seconds; from 2 it is seconds into the round, as a kill's. |
| `match` | string | the match name, as the files are named |
| `map` | string | the map (`de_inferno`) |
| `demos` | string[] | the demo files it was built from, file names only, in match order |
| `teams` | string[] | the team names in order of appearance (round 1: the T side first) |
| `score` | object | team name -> rounds won: the last round's score |
| `rounds` | object[] | every complete round, in order - [below](#rounds) |
| `incomplete` | number[] | round numbers cut off by the end of a demo and left out |
| `missing` | number[] | round numbers before the first one the demos hold: `[1, 2]` when the recording starts at round 3 |
| `halfLength` | number or null | rounds in a regulation half, from where the sides first swap (`12` in the 24-round format); null when the recording does not show the swap |
| `pistolRounds` | number[] | the pistol rounds the `buy` is counted with: round 1, and the round after the half when `halfLength` is known; never an overtime round |
| `players` | object[] | the scoreboard - [below](#players) |
| `conventions` | object | the definitions behind the numbers, [below](#conventions) |

## Rounds

| Field | Type | What |
|---|---|---|
| `number` | number | the round, 1-based |
| `start` | number | match seconds when freeze time ended |
| `end` | number | match seconds when the round was decided |
| `until` | number | match seconds when the next round started (the end of the after phase) |
| `winner` | string | `T` or `CT`; empty for a draw |
| `winnerTeam` | string | the winning side's team name; empty for a draw |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` or `other` |
| `score` | object | team name -> rounds won after this one |
| `sides` | object | team name -> `T` / `CT` this round |
| `equipment` | object | side -> total equipment value of its living players at freeze end, in dollars |
| `buy` | object | side -> `pistol`, `eco`, `force` or `full` |
| `plant` | object or null | the bomb plant: `site` (`A` or `B`; empty when the demo does not say), `time` (seconds **into the round**, as a kill's), `player`, `steamid`, `x`, `y`, `z` (game units), `place` (the planter's place name: where the bomb lay) |
| `survivors` | object | side -> names of the starting players still alive when the round was decided, sorted |
| `clutches` | object[] | each: `player`, `steamid`, `side`, `against` (enemies alive when the player became the last), `won` |
| `kills` | object[] | every death of the round, in order - below |

How these are found: [Building a match](building-matches.md#rounds);
clutches and survivors: [Statistics](statistics.md#clutches).

### A round's kills

Every death in the round, the after phase included:

| Field | Type | What |
|---|---|---|
| `time` | number | seconds **into the round** (since freeze end) |
| `attacker`, `attackerSide` | string | the killer and their side; empty for the world |
| `victim`, `victimSide` | string | the victim and their side |
| `assister` | string or null | the assisting player, or null |
| `flashAssist` | bool | the assist was a flash |
| `weapon` | string | as the game names it |
| `headshot` | bool | |
| `wallbang` | bool | the bullet went through something |
| `throughSmoke` | bool | the kill was through smoke |
| `noscope` | bool | a scoped weapon fired unscoped |
| `attackerBlind` | bool | the killer was flashed |
| `opening` | bool | the round's first kill of an enemy |
| `traded` | bool | this death was avenged within 5 s |
| `trade` | bool | this kill avenged a teammate within 5 s |
| `teamkill` | bool | attacker and victim on the same side, two different players |
| `suicide` | bool | attacker and victim the same player (an own grenade, say); not a teamkill |
| `after` | bool | the kill came after the round was decided |
| `place` | string | where the **victim** was (the map's place name) |

## Players

One entry per player, by team name and then best first by kills minus
deaths, then kills:

| Field | Type | What |
|---|---|---|
| `name`, `steamid`, `team` | string | who |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | assists without and with a flash |
| `diff` | number | kills - deaths |
| `adr` | number | average damage per round played, health lost |
| `kast` | number | percent of rounds played with a kill, assist, survival or traded death |
| `headshotPct` | number | percent of kills that were headshots |
| `openingKills`, `openingDeaths` | number | opening duels won and lost |
| `tradeKills`, `tradedDeaths` | number | trade kills; deaths that were traded |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: rounds with that many kills |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | damage with HE, molotov, incendiary |
| `enemiesFlashed` | number | enemies blinded at least 1 s |
| `plants`, `defuses` | number | |
| `teamkills` | number | teammates killed; suicides are not counted |
| `roundsPlayed` | number | rounds started |

Every definition: [Statistics](statistics.md#the-scoreboard-line).

## Conventions

Written into every document so a reader knows what the numbers mean without
this page:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## An example

From the synthetic two-round demo of the tests, shortened (`...` marks what
is left out):

```json
{
 "format": "heat3d-cs2-match",
 "version": 2,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

The order of keys inside `survivors`, `equipment` and `buy` is not fixed.
