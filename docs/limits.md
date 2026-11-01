---
title: Limits
nav_order: 11
---

# Limits

What the converter assumes, what it does not handle, and what is not
verified. Each point is from the code as it stands.

## What it reads

- **Uncompressed `.dem` files only.** `.dem.zst`, `.dem.bz2`, `.rar` and
  `.zip` must be unpacked first. The extension is matched in any case
  (`.dem`, `.DEM`), in folders as for files given by name.
- **Defusal matches.** The round end reasons, the bomb plant and site, the
  buy types and the pistol rounds are those of bomb defusal. Hostage maps,
  Wingman and other modes are not handled specially and are not verified.
- **64 ticks a second** is assumed (`TICKRATE = 64`) for every time
  computed from ticks; CS2 servers run at 64.
- **A demo from the server** (SourceTV) is assumed: it has every player.
  A client-side recording (POV demo) was not tried.

## Matches and rounds

- **Files are grouped by name.** The parts of one match must share a name
  apart from a `-pN` / `_pN` suffix; files of one match under unrelated names
  become separate matches, and same-named files in different folders are
  grouped together (then split into chains if they do not continue one
  another).
- **The live match starts at the last `round_announce_match_start`** in a
  file. A knife round that is not followed by that announcement is counted
  as a round.
- **Round end times are accurate to one sample** (`--every` ticks, 1/8 s by
  default), because the decision is read from sampled game state. A very
  large `--every` can miss a short window between a round's end and the
  next round's start and leave the round out as incomplete.
- **Draws.** A drawn round (win status 1, reason 10) is decided with no
  winner: `winner` is empty and neither side won it. No draw was met in a
  real demo to check this against; it is checked on the synthetic one.
- **Rounds cut off** by the end of a file are left out (`incomplete`), not
  guessed; rounds before the first in the files are listed as `missing`.
- **Pistol rounds** follow the half length the recording shows: where the
  sides first swap between two consecutive regulation rounds. A recording
  that does not show that swap (it starts after halftime, or ends before it,
  or a round either side of it is missing) knows only round 1 as a pistol
  round. Overtime has none.
- **Teams.** A team is the clan name seen most for its players. Without clan
  names the teams are `Started T` and `Started CT`. A player who changes
  team mid-match keeps one team.

## Events

- **Detonation rows** (`smoke`, `flash`, `he`, `molotov`, `decoy`) have no
  `place`: the demo names places for players, not for grenades. The
  thrower's place at that moment is in `throwerPlace`.
- **The plant's site** comes from the bomb zone the game says the planter
  stood in, else the planter's place name, else another plant on the same
  zone in the same file. Where none of these says, `site` is empty.
- **A death to the world** (a fall, the bomb) has no attacker: no kill, no
  teamkill, no opening; it is a death.

## Statistics

- **Rounds played** come from who had a position in the first second after
  freeze time. A player who connects later in a round does not count as
  having played it (their kills still count).
- **Survival for KAST**: a player killed in the after phase did not survive
  for KAST, while the round list still names them among the survivors.
- **Both players of a 1v1** can be credited a clutch in one round; see
  [Statistics](statistics.md#clutches).
- **Utility damage** is HE grenades, molotovs and incendiaries; a kill or hit
  by a thrown flash or decoy is not utility damage.

## Map export

- Needs the game installed (or the `.vpk`) and Source2Viewer's CLI; nothing
  is downloaded.
- Exports `world_physics` only; clip brushes and the sky are left out by
  their names containing `clip` or `sky`, in any case.
- Ground is told from structure by the face normal alone (Z component 0.7 or
  more), so a steep ramp is structure and a flat roof is ground.
- The file is in inches, not metres.

## Memory and time

- A match is held in memory whole while it is built, in one worker per
  match. With many workers and a small `--every`, memory adds up: lower
  `--jobs` if a machine runs short.
- A match is written only when it is built: the `.parquet` first, then the
  `.match.json`. A run stopped in between leaves a table without its summary;
  a match counts as written only with both, so the next run converts it
  again. Matches not yet started are simply picked up by the next run.
