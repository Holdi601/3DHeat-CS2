
# Reading a demo

What is taken out of one `.dem` file, before anything is interpreted. Code:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

A CS2 demo is the server's own recording (SourceTV): every player, every
tick, 64 ticks a second (`TICKRATE = 64`). It is read with
[demoparser2](https://github.com/LaihoE/demoparser) in three calls, and the
result is kept as it comes, in a `RawPart`:

| Field | Holds |
|---|---|
| `path` | the file |
| `map` | `map_name` from the demo header (`de_mirage`); empty if the header has none |
| `samples` | one row per player per sampled tick: the player and rules fields below, plus `tick`, `steamid`, `name` |
| `events` | event name -> its rows, with the players' fields prefixed `user_`, `attacker_`, `assister_` as the parser names them |

Nothing in `demo.py` decides what a round is or who won; that is
[Building a match](building-matches).

## The sampled ticks

`parse_ticks` is asked for ticks `0, N, 2N, ...` up to 4,000,000 (`LAST_TICK`,
far past any match - 17 hours at 64 ticks a second), where *N* is `--every`
(default 8). The parser stops at the demo's end. Every player present at a
sampled tick gives one row, whether alive, dead, spectating or a coach;
filtering happens later.

The sampling stride matters beyond the heatmap's density: the moment a round
is decided is read from these samples (see
[Building a match](building-matches#rounds)), so round end times are
accurate to one stride (1/8 s by default).

### Player fields

| Property | Becomes |
|---|---|
| `X`, `Y`, `Z` | the position, in the game's units (inches), Z up. demoparser2 gives the player's origin, i.e. the feet. |
| `yaw`, `pitch` | the look direction (degrees), turned into a unit vector |
| `health`, `armor_value` | health, armour |
| `team_num` | the side: 2 = T, 3 = CT; anything else (spectators, 0, 1) is no side |
| `team_clan_name` | the team's name as the server shows it, used to name the teams |
| `active_weapon_name` | the weapon held, as the game names it (`AK-47`, `Karambit`) |
| `is_alive` | whether the player is alive - only living players become positions |
| `last_place_name` | the map's own place name (`BombsiteA`, `TopofMid`) |
| `balance` | money |
| `current_equip_value` | the value of what the player carries |

### Game-rules fields

Read alongside, once per player row (they are the same for everyone at a tick):

| Property | Used for |
|---|---|
| `game_time` | the server's clock, in seconds |
| `total_rounds_played` | the round count, which carries on across a match's files |
| `round_win_status` | who won the round just played: 1 a draw, 2 T, 3 CT |
| `round_win_reason` | how (the game's `CSRoundEndReason`) |
| `team_rounds_total` | each side's score |
| `is_warmup_period` | warmup is left out everywhere |
| `is_freeze_period` | freeze time is left out of the positions |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | the overtime being played, 0 in regulation: overtime rounds are no pistol rounds (the parser has no shorter name for it) |

## The events

Each event below is read when the demo declares it (`list_game_events`), with
`X`, `Y`, `Z`, `team_num`, `last_place_name` and `which_bomb_zone` (the bomb
zone the player stands in: 0 none, 1 A, 2 B) for every player the event
names, and `total_rounds_played` and `is_warmup_period` of the game at that
tick:

| Event | Becomes |
|---|---|
| `player_death` | kills and deaths; uses `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | damage; uses `dmg_health` (damage dealt to health), `health` (health left), `weapon` |
| `player_blind` | flashed players; uses `blind_duration` |
| `weapon_fire` | shots and grenade throws; uses `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | where grenades went off; uses the event's own `x`, `y`, `z` (the event has no place name for that point, only the thrower's) |
| `bomb_planted` | the plant; uses the planter's `which_bomb_zone` and place, and `site` (the zone's entity number) |
| `bomb_defused` | the defuse |
| `bomb_exploded` | when the bomb went off: the time of the `explode` row |
| `round_freeze_end` | where each round starts |
| `round_prestart` | where the time after a decided round ends |
| `round_announce_match_start` | where the live match starts |

## Two facts about demos that decide how they are read

- **A match can be split across files**, and the files' names do not say
  their order. The round count (`total_rounds_played`) carries on across
  them, and usually the server's clock too, so the parts can be ordered from
  what they contain.
- **A recording can start before the match**: warmup, a restart, a knife
  round. The match starts at the **last** `round_announce_match_start` in a
  file; before it everything is left out, and warmup is left out everywhere.
