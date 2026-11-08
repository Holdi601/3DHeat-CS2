# CS2 demos and maps

Counter-Strike 2 demos into heatmap tables and match summaries, and CS2 maps
into level geometry, for the 3DHeat viewer - or anything that reads Parquet,
JSON and glTF.

```bash
pip install -r requirements.txt
python -m heat3d_cs2 demos <demo files or folders> -o out          # every match in them
python -m heat3d_cs2 map de_mirage -o out/de_mirage/de_mirage.glb  # the map from the installed game
python -m heat3d_cs2 scoreboard out/de_mirage/<match>.match.json   # a match's scoreboard as text
```

Per match, `demos` writes into a folder per map (`out/de_mirage/...`), so a
map's matches load together:

- `<match>.parquet` - every player eight times a second (`--every 8` ticks of
  64) with everything the demo says of them, freeze time included, every
  grenade's flight, and every event where it happened, one row each: the
  heatmap's data.
- `<match>.match.json` - teams, score, every round (winner, how, economy, the
  plant, every kill in order, clutches, survivors), every player's
  scoreboard line, the chat, every event about no player, and the game's
  state as it changed: the match analysis' data. Its `selfCheck` says where
  everything of the demo went.
- `<match>.events.parquet`, `.props.parquet`, `.strings.parquet`,
  `.packets.parquet` - everything else the demo holds, whole (see
  [Completeness](#completeness)).

A folder of a few hundred demos takes minutes (`--jobs`, half the cores by
default). Matches already written are skipped unless `--force`.

## The table

| Column | What |
|---|---|
| `match`, `map`, `round`, `roundId` | which match and round; `roundId` is `<match> #NN` |
| `phase` | `freeze` in freeze time, `live` until the round is decided, `after` while the winners hunt and the losers save |
| `time`, `roundTime` | seconds since the match started; since this round's freeze time ended |
| `event` | `position`, `kill` (where the killer stood), `death` (where the victim fell), `hurt` (the victim), `shot`, `slash` (a knife), `throw`, `grenade` (in flight), `smoke` / `flash` / `he` / `molotov` / `decoy` (where it went off), `blind` (the player flashed), `plant`, `defuse`, `explode`, `chat`, and every other game event about a player under the game's name (`item_pickup`, `player_footstep`, `weapon_reload`, `bomb_dropped`, ...) |
| `player`, `steamid`, `side`, `team` | who: `side` is `T` or `CT` this round, `team` the team's name |
| `x`, `y`, `z` | the game's own coordinates (inches, Z up) |
| `dirX`, `dirY`, `dirZ` | where a player looks, a unit vector in the same frame |
| `health`, `armor`, `money`, `equipment` | for positions |
| `weapon`, `place` | the weapon as the game names it (every knife skin as `Knife`); the map's own place name (none where a grenade went off) |
| `throwerPlace` | for a grenade going off: where its thrower was at that moment |
| `other`, `damage`, `duration` | the other player of a kill, hit or flash; health lost; seconds blinded |
| `headshot`, `opening`, `traded` | 0/1: a headshot; the round's first kill of an enemy; for a kill, a trade - for a death, avenged within 5 s |
| `noscope`, `attackerBlind` | 0/1, for a kill or death: a scoped weapon fired unscoped; the killer was flashed |
| `won`, `buy` | 0/1 whether this row's side won the round; its side's buy that round |
| `detail`, `text`, `entity` | every other field of the event as JSON; a chat line; a grenade's entity (flight, detonation and flashes share it) |
| `hitgroup`, `armorDamage`, `penetrated`, `throughSmoke`, `distance`, `assister` | where a bullet struck, armour lost; for a kill: walls, smoke, distance, assist |
| the player's state, on positions | flash, helmet, defuser, scoped, zoom, walking, crouch, airborne, buy and bomb zone, defusing, spotted and by whom, inventory, ammunition, recoil, ping, the game's scoreboard counts, money spent |

Every column, and which events fill which: [docs/output-table.md](docs/output-table.md).
Not in the table: the players' velocity (not in the demo: the parser derives it from
positions), voice, and grenade flights between the players' samples (every
tick in the props sidecar).

The file's Parquet footer carries reading instructions under the key
`heat3d`: which column is the position, the time, the player, the side, the
session and the look direction, how big a player is (32 units across, the
size a box replay draws one), and that the world is drawn with the vertical
as Y and the game's Y negated. CS2's world is right-handed with Z
up; drawn the way a left-handed Z-up world is, it comes out mirrored, A site
on the wrong side. The viewer reads the instructions and opens the file with
nothing to set.

## The conventions

Where the game does not define them:

- A death is **traded** when its killer is killed by one of the victim's
  teammates within 5 s; that kill is a **trade kill**.
- **KAST**: the share of rounds in which a player killed, assisted (a flash
  assist counts), survived, or was traded.
- **Damage** is health actually lost: a 137 damage headshot on a player with
  40 health is 40, as the scoreboard counts it. Enemies only.
- A **clutch** is being the last player alive on a side with enemies still
  standing; it is won when the side wins the round.
- **Buy**, per side, from the average equipment value when freeze time ends:
  the first round of each regulation half is a pistol round (the half as
  long as the match played it; overtime has none), then under $1,500 an eco,
  under $4,000 a force buy, anything more a full buy.

## Demos as they come

Demos from the wild are not all one clean file per match, and each of these
was met in a collection of 177 tournament demos:

- **A match split across files.** Parts are put in order by the round count,
  which carries on across them, then by the server's clock. A part's
  suffix (`-p1`, `-p2`) says nothing: a `-p2` can be the earlier half.
- **A server restarted mid-match** to restore a round starts its clock
  again; the next part still follows on.
- **Two different matches under one name** - the same teams on the same map
  at two events - overlap in their round counts and are written apart
  (`<match>-b`).
- **A round restored from a backup** inside one file leaves the players'
  old bodies in the demo beside the new ones for some seconds; each player
  keeps the row that leads on into where they go next.
- **A demo that starts late** (round 2) or ends during the last round says
  so (`missing`, `incomplete` in the match summary) rather than guessing.
- **The clock.** Within a file, time is counted in ticks: the server's clock
  stands still through a pause while the ticks run on.
- **Coaches** on a team's side are never alive and are not players.

Checked over all of it: 165 matches, 3,565 rounds; in every match the score
follows the round winners, each side's kills are the other side's deaths,
and every round starts five against five.

The rest of the demo, checked on a Dust2 match of it (22 rounds): every
player's kills and damage counted from the events equal the game's own
scoreboard counts at the end (`kills_total`, `damage_total`: 10 of 10
players), deaths 8 of 10 (one apart for the other two); the health a `hurt`
leaves equals the next sample's for 365 of 395 hits (the rest were hit again
before it); every smoke, flash, HE and decoy that went off (329) has a
flight with its entity, ending a median 0 units (95% within 50) from where it
went off - the fires (103) carry the fire's entity, not the bottle's.

## Completeness

3DHeat's converters keep everything a recording holds:
[Converters keep everything](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md).
Beside each match's table and document, `demos` writes four sidecars, each
with `time` on the table's clock (empty before the first tick), the demo's
`tick` and `part` (which file of the match, in order), and the match
document's `selfCheck.completeness` counts, for every kind of thing as the
demo has it - every event name, every property class, every network message
and frame, every string table - how many there were, how many went into the
table or document in part (`partial`), how many only into a sidecar (`raw`),
and how many were lost.

### Read

Into the table and the document: as above. What the sidecars decode besides,
each checked against something independent on five demos and over the whole
collection (below):

- **Console variables** (`net_SetConVar`, `decoded` in `packets`): every name
  and value equals the parser's `server_cvar` (which repeats the start's list
  once per stretch of the demo it reads apart: 1,770 rows for 59 variables).
- **Chat lines** (`UM_SayText2`): speaker, text and kind equal the parser's
  `chat_message`, tick for tick.
- **The server's info** (`svc_ServerInfo`): the map and the game folder equal
  the demo's header, the tick interval is 1/64 s.
- **String tables created** (`svc_CreateStringTable`): the table's name, the
  same as the tables' own snapshot.
- **Players' entries** (`userinfo` in `strings`): name, steamid, user id, bot
  or SourceTV; every player the parser lists is there with the same steamid
  (names can differ: the entry is from the start, `BIT` where the scoreboard
  later says `Coach | BIT`).

### Kept raw

- `<match>.events.parquet` - every game event the parser reads, warmup and
  all, every key as the parser gives it (`decoded`: the players named by
  name and steamid, not where they stood - that is in `props`); `name` and
  `player` the event's player, `entity` its entity where it has one.
- `<match>.props.parquet` - every property the parser can read, one row each
  time it changed (`type` the property's path, `value` a number - flags 0/1 -
  `vector` a list of numbers, `decoded` anything else as JSON, whole numbers
  past 2^53 as text): every player's pawn and controller, their active weapon
  (`Weapon.*`), their commands (`usercmd_*`: view angles, buttons, mouse,
  moves), keyed by the controller's entity with `name` and `player` (steamid);
  the game rules (entity -1), the teams (entity 2/3, `CCSTeam`), and every
  grenade, held or flying, by its own entity, its class as `name` and its
  thrower as `player`. Read a tick at a time, the demo's own resolution: a
  first value, each change, and where a value went empty.
- `<match>.strings.parquet` - every entry of every string table snapshot
  (`type` the table, `name` the key, `entity` the index, `payload` the data;
  each table also as a row of its own, index -1), the players' entries decoded.
- `<match>.packets.parquet` - every other frame and network message, whole,
  in file order (`seq`): `type` `message <n>` or `frame <n>`, `name` Valve's
  name where it was matched, `payload` the bytes. Among them the server info,
  string table updates, sounds, user messages (the end-of-match scoreboard
  data, player stats, weapon sounds, text messages), temp entities, the game
  events as sent (with their list), the bullets, SourceTV status, the send
  tables and class list (what a decoder of the entity stream needs), and -
  unless `--no-bulk` - the bulk: the entity stream (`svc_PacketEntities`),
  the players' commands (`svc_UserCmds`, sub-tick inputs) and the animation
  stream (`DEM_AnimationData`).

The bulk is over half a demo's size even compressed (on a 258 MB demo:
commands 67 MB, animation 39 MB, entities 35 MB); everything else together
is about a tenth (props 8%, packets without the bulk 2%, events, strings).
`--no-bulk` leaves it out, and the self-check then counts it lost, by name.

### Not available

- **Entities the parser does not read**: the world, dropped weapons, the
  bomb, fires, chickens, doors - and the properties it lists but gives no
  value for (`unreadProps` in the self-check: weapon lists, ammunition,
  purchase records, fire positions). They are in the entity stream, kept
  whole with what decoding it needs, but not decoded here.
- **Within a tick**: the props are as the parser has them at each tick, the
  demo's own resolution; the sub-tick inputs are in the commands, whole.
- **Voice**: these SourceTV demos announce a voice codec (`svc_VoiceInit`,
  Speex) but carry no voice data; where a demo does (`svc_VoiceData`), it is
  kept whole in `packets`.
- **A file with no round in it** (a pause, warmup only) belongs to no match
  and is not written; the command line names it.

## The map

`map` exports the world's collision mesh - what players stand on and hide
behind, without the decoration - from the map's `.vpk` in the installed
game, using Source2Viewer's command line
([ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat),
MIT licensed; download the CLI build, then put it on `PATH`, set
`HEAT3D_SOURCE2VIEWER` or pass `--source2viewer`). Clip brushes and the sky
are left out; each surface is split into ground (facing up, walkable) and
structure. It is written in the frame the tables are drawn in.

The check that the frame is right is the players standing on it: over a
match on each of the eight maps of the current pools (Mirage, Nuke, Ancient,
Inferno, Dust2, Train, Anubis, Overpass), 99.9-100% of player samples have
ground beneath them, a median of 0.03 to 2.1 units (under 6 cm) below their
feet. The same maps mirrored leave 36-64% over ground.

## What to point it at

Your own matches' demos, demos you downloaded from a tournament site by hand,
demos from an API you have access to. A demo is a recording of a match whose
content belongs to its publisher and organisers; use what comes out for your
own analysis, and do not redistribute demos or data derived from them -
Valve has had a dataset built from professional demos taken down. Sites that
offer demos often forbid automated downloading in their terms.

## Tests

```bash
python -m pytest
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<cli> python -m pytest   # also the floor check on a real map
```

---

## Part of 3DHeat

3DHeat CS2 is one of the free tools around the 3DHeat telemetry viewer. Each is its
own project, with its own releases and licence:

| Tool | What it does |
|---|---|
| [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | courses and levels out of the archives games ship, as glTF |
| [3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | lap telemetry from racing games' published interfaces; levels reconstructed from gameplay video |
| [3DHeat Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | an Unreal Editor plugin that exports a level as glTF |
| [3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demos into heatmap tables and match summaries; maps into geometry |
| [3DHeat Watcher](https://github.com/Holdi601/3DHeat-Watcher) | records your play in the background from what games publish, for your own statistics |

## Updates

3DHeat CS2 checks this repository's releases when it starts (at most every few
hours, never holding it up for more than a few seconds), says when a newer
version is out, and offers to update: a clone with `git pull` when it has no
local changes, a downloaded copy by replacing its files from the release archive,
after checking the archive is the version it claims. Your own files - recordings,
settings, exports - are never touched. To update on request: `python -m heat3d_update`.
`HEAT3D_NO_UPDATE=1` switches the check off.

## Licence

MIT - see [`LICENSE`](LICENSE), and [`LICENSES.md`](LICENSES.md) for the
third-party packages it uses and what the games it reads oblige.

Documentation: the [wiki](https://github.com/Holdi601/3DHeat-CS2/wiki).
