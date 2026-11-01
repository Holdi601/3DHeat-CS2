---
title: Building a match
nav_order: 5
---

# Building a match

How a match is made from its demo parts: which files belong together, one
clock across them, the rounds and how each was won, the teams and their
sides, and every row of the heatmap table with kills, trades, openings,
damage, flashes and economy. Code:
[`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py).
The scoreboard computed from it is on [Statistics](statistics.md).

## Overview

1. Every file of a match name is read ([Reading a demo](reading-demos.md)).
2. Each file's duplicate player rows (restored rounds) are resolved.
3. The files are sorted into **chains** - matches - and each chain is put in
   order.
4. Each part is placed on the **match clock**.
5. The **rounds** are found in each part; a later part's account of a round
   replaces an earlier one's.
6. The **players** and **teams** are named, and each round's sides and score
   are given by team name. With the sides known, the half's length, the
   pistol rounds and each side's **buy** follow.
7. The **rows** are built: positions, shots, throws, detonations, plants,
   defuses, kills, deaths, hurts, blinds, explosions.
8. Each row is labelled with its round, phase, round time, whether its side
   won, and its side's buy; rows outside every round are dropped.

## Restored rounds: one row per player per tick

When a round is restored from a backup inside one file, the demo carries the
players' old bodies alongside the new ones for some seconds: two rows for one
player at one tick, one where the voided round left them, one at the restored
round's spawn. For each such player, the duplicated ticks are walked
**backwards** from the first single row after them: at each tick the candidate
nearest to the position that follows is kept, and that becomes the reference
for the tick before. With no single row after them, the last candidate is
kept. So each player keeps the row that leads on into where they go next.

## The live part of a file

A file's **live start** is the tick of its last `round_announce_match_start`
event, or tick 0 if it has none (a later part of a split match usually has
none). Everything before the live start is left out, and so is everything
flagged `is_warmup_period`. A knife round or a restart before the
announcement is therefore left out; a knife round *not* followed by a match
start announcement is not recognised as one (see [Limits](limits.md)).

A file's **rounds** are the `round_freeze_end` events from the live start on,
outside warmup, identified by their `total_rounds_played` (the game's 0-based
index of the round about to be played). A file with none has no rounds and
belongs to no match.

## The clock

Times are in seconds. Within a file, time is counted in **ticks**: the
server's `game_time` at the first sampled tick, plus ticks since then / 64.
The server's own clock stands still through a pause while the ticks run on;
read through the clock, two moments of a paused match would share a time.

Each file has a *first clock* (the time at its live start) and a *last clock*
(at its last sampled tick).

### Parts and chains

Files named as one match ([Commands](commands.md#which-files-are-one-match))
are first sorted by the index of their first round, then by their first
clock. Then each, in that order, joins the first chain it continues, or
starts a new chain. A part continues a chain when its first round index is at
least the chain's last part's last index, **and** either

- the server's clock runs on: its first clock is no earlier than the chain's
  last clock minus 5 s; or
- the round count runs on: its first round index is the chain's last index or
  the one after.

The count decides and the clock breaks ties, because a server restarted to
restore a round starts its clock again, while two different matches under
one name (the same teams on the same map at two events) have overlapping
round counts. Chains are ordered by how many rounds they span, most first;
the first keeps the match name, the others are written as `<name>-b`,
`<name>-c`, ...

### The match clock

The match's zero is the first part's first clock: **match time 0 is the live
start of the first file**. Each later part is placed on it:

- where the server's clock runs on (its first clock is no earlier than the
  previous part's last clock minus 5 s), the server's clock is used as it is;
- where it was restarted, the part is placed to follow **one second** after
  the previous part ended.

## Rounds

For each `round_freeze_end` of a part (in tick order), the round's window
runs to the next freeze end in that part, or to the file's end. Within it,
the round is **decided** at the first sampled tick where the game state shows
`total_rounds_played` = the round's index + 1 and `round_win_status` 1 (a
draw), 2 (T won) or 3 (CT won). A round with no such sample in its window
was cut off by the end of the file; its number goes into the match's
**incomplete** list (unless another part has the round complete).

| Round field | From |
|---|---|
| `number` | the index + 1 (1-based, as the game counts) |
| `start` | match time of the freeze time's end - players can move |
| `end` | match time of the first sample showing the round decided |
| `until` | match time of the next `round_prestart` after `end`, if it is inside the window; otherwise the window's end or the file's last tick, whichever comes first (and never before `end`) |
| `winner` | `T` for win status 2, `CT` for 3, empty for 1: a draw is decided, with no winner |
| `reason` | `round_win_reason` at that sample, named as below |
| `score` | team name -> rounds won after this one: each side's `team_rounds_total` at the deciding sample; where the demo has none, the previous round's score plus one for the winner |
| `sides` | team name -> `T` / `CT` this round |
| `equipment` | side -> the summed `current_equip_value` of that side's **living** players at the first sample at or after freeze end |
| `buy` | side -> `pistol`, `eco`, `force` or `full` ([Economy](#economy-and-buy-types)) |
| `plant` | the first `bomb_planted` after freeze end and up to `end`, or none |
| `exploded` | match time of the first `bomb_exploded` after that plant and before the next freeze end, if any (not in the summary; it times the `explode` row) |

`reason`, from the game's `CSRoundEndReason`:

| Code | `reason` |
|---|---|
| 1 | `bomb` (target bombed) |
| 7 | `defuse` |
| 8, 9 | `elimination` (CTs win / Ts win by elimination) |
| 10 | `draw` |
| 12 | `time` (target saved) |
| 17, 18 | `surrender` |
| anything else | `other` |

When several parts hold the same round (by index), the later part's version
is kept. The rounds are then listed by index. A match whose first round is
not round 1 records the missing numbers (`missing` in the summary); the
command line says *recorded from round N*.

### The plant

| Field | From |
|---|---|
| `site` | `A` or `B`: the bomb zone the game says the planter stood in (`which_bomb_zone`, 1 A, 2 B); without it, the planter's place name (`BombsiteA`, `BombsiteB`); without that, the letter another plant of the same file on the same zone gave (the event's `site` is the zone's entity number). Empty when nothing says - never the number. |
| `time` | seconds **into the round** (since its freeze end), as a kill's time |
| `player`, `steamid` | the planter |
| `x`, `y`, `z` | the planter's position, game units: where the bomb lies |
| `place` | the planter's place name at the plant |

### The phases

The time from `start` to `end` is the round's **live** phase; from `end` to
`until` its **after** phase, where the winners hunt and the losers save. A
row belongs to the round whose `[start, until)` contains its time, and is
`after` when its time is later than `end`. Freeze time lies between rounds
and is in none.

## Players and teams

A **player** is everyone who was alive at least once on a side (team 2 or 3),
outside freeze time and warmup, after the live start. A coach or a caster on
a team's side is never alive and is no player. Each player is keyed by Steam
ID; the name is the last one seen.

A player's **team** is the clan name the game gave their side
(`team_clan_name`), the one seen most often for them - the demo clears it at
its very end. A match played without clan names names its teams by the side
they started on: `Started T` and `Started CT`.

Each round's **sides** come from who was on which side between freeze end
and the round's end: each side is given the team label most of its players
carry. The match's `teams` list is in order of appearance, round by round, T
side before CT; usually the team that started on T is first.

## The rows

Every position sample and every event becomes one row of the
[heatmap table](output-table.md). Players are on a side only when their
`team_num` is 2 or 3.

### Positions

From the sampled rows of living players on a side, outside freeze time and
warmup, after the live start: position, look direction, health, armour,
money, equipment value, held weapon, place.

The look direction is a unit vector in the game's frame:
`(cos pitch * cos yaw, cos pitch * sin yaw, -sin pitch)` - the game's pitch is
positive looking down, so looking down gives a negative Z.

The held weapon is `active_weapon_name` as the game names it, except that any
name containing `Knife`, `Bayonet`, `Karambit` or `Daggers` becomes `Knife`.

### Shots and throws

From `weapon_fire`, at the shooter's position. Knives (`knife`, `bayonet` in
the weapon id) and the C4 are left out. Grenades (`smokegrenade`,
`flashbang`, `hegrenade`, `molotov`, `incgrenade`, `decoy`) are **throw**
rows, everything else **shot** rows. The weapon is named as the game shows
it (below).

### Grenade detonations

| Event | Row | `weapon` |
|---|---|---|
| `smokegrenade_detonate` | `smoke` | Smoke Grenade |
| `flashbang_detonate` | `flash` | Flashbang |
| `hegrenade_detonate` | `he` | High Explosive Grenade |
| `inferno_startburn` (molotov and incendiary) | `molotov` | Molotov |
| `decoy_detonate` | `decoy` | Decoy Grenade |

The position is **where the grenade went off** (the event's `x`, `y`, `z`);
the player and side are the thrower's. The demo names no place for a
grenade, only for players, so `place` is left empty: a row does not claim a
place it was not at. The thrower's place at that moment is kept as
`throwerPlace`.

### Plants and defuses

`plant` and `defuse` rows at the player's position, weapon `C4 Explosive`.
A planted bomb that went off gets an **explode** row: at the plant's
position, at the time of `bomb_exploded`, the planter as the player (with
their Steam ID), side `T`, the round's T team as `team`, and the plant's
place. That includes a bomb going off after the Ts already won by
elimination. Where the demo has no `bomb_exploded`, a round won by the bomb
(`reason` = `bomb`) with a plant gets the row at the round's `end`.

### Kills and deaths

Every `player_death` in a round gives one **kill record** (the match's
`kills` table) with:

| Field | Is |
|---|---|
| attacker, victim, assister | names, Steam IDs, sides; the attacker is empty for the world (fall damage, the bomb) |
| `weapon` | the event's weapon named as the game shows it |
| `headshot` | the event's flag |
| `wallbang` | `penetrated` > 0 |
| `throughSmoke` | `thrusmoke` |
| `flashAssist` | `assistedflash` |
| `noscope`, `attackerBlind` | the event's flags (`noscope`, `attackerblind`); columns of the `kill` and `death` rows, and in the summary's kills |
| `suicide` | attacker and victim the same player: an own grenade, say |
| `teamkill` | attacker and victim on the same side, with an attacker, and not a suicide |
| `opening` | the round's first kill of an enemy (below) |
| `traded`, `trade` | below |
| positions | the attacker's and the victim's position and place |

From each record the table gets a **death** row at the victim's position
(every death, the world's, teamkills and suicides included) and - for kills
by an enemy (an attacker, no teamkill, no suicide) - a **kill** row at the
killer's position.

**Opening.** The first kill of an enemy in each round while it is live is its
opening duel. A teamkill, a suicide or a death to the world before it is
passed over, so the opening is still the first duel of the round; a round
with no enemy kill while it is live has none.

**Traded** and **trade.** A death by an enemy is **traded** when its killer
is killed by one of the victim's side within **5 seconds** after it (more than
0 and at most 5 s later, in the same round); the first such kill is a
**trade** kill. On the table, a `kill` row's `traded` column is 1 for a trade
kill; a `death` row's is 1 for a death that was avenged. Kills of the after
phase count as well.

### Damage

From `player_hurt`, between **enemies** only (both on a side, different
sides). The damage is health actually **lost**: for each victim in each
round, health starts at 100; each hit counts `min(dmg_health, health before)`,
and the event's `health` (what is left) becomes the next hit's "before". A 137
damage headshot on a player with 40 health counts 40, as the game's
scoreboard counts it. Hits from `hegrenade`, `inferno`, `molotov` and
`incgrenade` are **utility** damage. Each hit is a **hurt** row at the
victim's position, the attacker as `other`. Team damage and self damage are
in neither the table nor the statistics.

### Flashes

From `player_blind`, **enemies** only (not teammates, and not a coach or a
caster watching): one **blind** row per player blinded, at the flashed
player's position, the flasher as `other`, the blind time in seconds as
`duration`. Every duration is kept; the statistics count only blinds of at
least one second.

## Weapon names

A weapon id from an event (`ak47`, `weapon_ak47`, `knife_karambit`) is shown
as the game names it in the players' own `active_weapon_name`, so a kill's
weapon and a held weapon read the same: `ak47` -> `AK-47`, `m4a1` -> `M4A4`,
`m4a1_silencer` -> `M4A1-S`, `hkp2000` -> `P2000`, `taser` -> `Zeus x27`,
`inferno` and `molotov` -> `Molotov`, `incgrenade` -> `Incendiary Grenade`,
`c4` and `planted_c4` -> `C4 Explosive`, `world` -> `World`, and so on for
every gun and grenade (the `WEAPONS` table in `match.py`). Anything with
`knife` or `bayonet` in its id is `Knife`. An id not in the table is kept as
it is.

## Economy and buy types

At the end of freeze time, each side's equipment value is summed over its
living players at the first sample from then on, and divided by how many
there were:

| Round | Average equipment per player | `buy` |
|---|---|---|
| a pistol round (first of each regulation half) | any | `pistol` |
| other | under $1,500 | `eco` |
| other | $1,500 to under $4,000 | `force` |
| other | $4,000 or more | `full` |

The pistol rounds follow the half the match was played with, not a fixed
format. The half ends where the sides first swap between two rounds that
follow each other, both in regulation: its length (`halfLength` in the
summary) is the round before the swap - 12 in the 24-round format, 15 in
the 30-round one. Round 1 and the round after the half are the pistol
rounds. A round is overtime when the game's overtime count
(`m_nOvertimePlaying`) is above 0 at its freeze end; where a demo has no
such count, every round after two halves is. Overtime halves start with
money the server sets and have no pistol round, though their sides swap
too. A recording that never shows the halftime swap - it starts after it, or
ends before - leaves the half unknown, and only round 1 is a pistol round.

## Labelling and order

Finally every row is given:

- `match` - the match name; `map` - the demo header's map;
- `round` and `roundId` (`<match> #NN`, two digits);
- `phase` - `live` or `after`;
- `roundTime` - seconds since the round's freeze time ended;
- `won` - 1 if the row's side won the round, 0 if not, empty for a row with
  no side;
- `buy` - the buy of the row's side that round;
- `team` - the team of the row's player, by Steam ID.

Rows whose time is in no round - before the first round's freeze end,
during freeze time, after the last round - are dropped. The rows are sorted
by time, and by event name within a time.
