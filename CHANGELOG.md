# Changelog

## 1.3.0

- Wallbangs on every hit, not only kills: each `hurt` row says whether the shot went through a wall (`wallbang`),
  how many (`wallCount`), how thick in all (`wallThickness`, m), which surfaces (`wallSurfaces`) and the fences and
  grates it crossed (`wallGrates`), traced through the map's level from `map`.
- The trace: the shot's own line (the game's `fire_bullets`: where it left and its direction) as far as the point
  struck, through the map's collision mesh in a 2 m grid. Fences, grates and foliage that bullets pass are no wall,
  nor is a wall's edge grazed (under 1 cm); a line through more than 80 cm of solid, or solid metal, cannot be the
  bullet's and stays empty. Doors, other moving parts and players are not in the mesh, so a shot through one is
  not seen.
- Checked against the game's own count on 25,372 kills of 176 demos on 8 maps: they agree on 97.0 % (both yes 530,
  both no 24,086; traced only 399, game only 357; 1.1 % of the kills left empty as above). On hits that did not
  kill, 80 % of the traced wallbangs dealt clearly less damage than the weapon deals at that range (a wall's
  damage drop), against 6 % of the clear shots.
- `demos --levels <folder>`: where the maps' `.glb` are (default `HEAT3D_LEVELS`, else the 3DHeat levels folder).
  Without the match's map there, the new columns stay empty and nothing else changes.
- `map`: what bullets pass (the map's `passbullets` groups) is kept as its own parts, `ground|structure:passbullets:<surface>`,
  and surfaces are named from the group's own surface property. Export your maps again for the trace to tell
  fences from walls (the window lists maps from before 1.3.0 as exported by an older version); a level from an
  older version is still traced, with its fences as walls.

## 1.2.0

- `hurt` rows say which way the victim looked at the hit (`dirX`, `dirY`, `dirZ`, from the event's own view angles) and
  where the shooter stood and on which side (`attackerX`, `attackerY`, `attackerZ`, `attackerSide`), so a hit's
  distance and its angle against the victim's facing are exact at the hit, not read from the 8-a-second samples.
  Tables converted before keep working; convert again for the new columns.
- Its own icon: the 3DHeat cube with a text badge for its game (letters in 3DHeat's colours), as the
  program, window, taskbar and docs icon.
- A new window: the 3DHeat look in dark and light (follows the system, switchable), the logo and
  icon, sharp at any display scaling. Four steps: find the game (each requirement with its fix),
  choose (maps ticked when there is something to do, filters, search; jobs with their fields
  inline), work (progress, time left, cancel), done (open in 3DHeat, open the output folder, and
  for a failure what went wrong and what to do, copy details, report a problem).
- No console window on Windows: the program is a window program. From a terminal it still prints
  as before; `heat3d-cs2-cli.cmd` beside it waits for it in a terminal and passes its exit code.
- The update offer in the same look: Update now / Later / Skip this version, and "Update
  automatically" from the dialog.
- CI draws every page and dialog of the window (on Linux under a virtual display) and checks the
  Windows build is a window program.
- `heat3d-cs2 convert <replay>... -o <out> [--progress-json]` and `heat3d-cs2 info <replay> --json` (what the
  replay says about its match, read from its header without converting it), the same verbs in every
  3DHeat replay reader; the old command lines work as before.

## 1.1.0

- A standalone program for Windows and Linux (no Python needed), built by CI with a `SHA256SUMS` file. Without
  arguments it opens a window: what is found and what is missing (install, Source2Viewer-CLI, disk space), the
  levels folder, the install's maps as new / changed by a game update / exported by an older version / up to date,
  export of the picked ones one at a time (`cs2/<map>.glb` and its layouts), demo conversion, the catalogue, the
  model pack, and updates.
- Each exported map is recorded in `<levels>/cs2/.heat3d-extract.json` (extractor version, game build, size and
  SHA-256 of its `.vpk`), so maps a game update adds are found and only those exported: `status --json`,
  `extract --new` / `--changed` / `--outdated` / `<map>...`, `--progress-json`.
- Updates ask first (update now / later / skip this version) unless automatic updates were chosen
  (`--auto-update`, the window's checkbox, or `HEAT3D_AUTO_UPDATE=1`).
- The install is also found in Steam libraries on Linux (native, flatpak, Steam Deck) and through the registry on
  Windows. A `pyproject.toml` makes `pip install .` possible.

## 1.0.7

- `models`: the knives, grenades and health shot lie like the guns, long side along x and the business end (blade
  tip, the grenade's top, the needle) forward; a knife's edge faces down. Their world models are drawn in the frame
  of the hand that holds them, and they are held through the fist, so they came out standing up. The armour and the
  defuser kit face forward instead of sideways.

## 1.0.6

- `catalog` and `models` read the installed game's `weapons.vdata` through Source2Viewer 21.1; `--vdata` stays as an
  override for older builds.
- `models`: the AUG, C4 and R8 Revolver, and the knives, grenades and kit (armour, defuser, health shot), whose
  world models only `weapons.vdata` names: 211 models in all. A weapon's world model is read from one of its two
  bodies, not both on top of each other.

## 1.0.5

- `catalog`: every weapon, item and agent of the installed game as `catalog.json` (class, side, numbers; the
  agents' units), for the viewer's names and order.
- `models`: the agents' and weapons' models of the installed game as a local model pack (`model-pack.json` and a
  `.glb` per unit, three levels of detail; the agents' hit groups), drawn by the viewer in place of its figures.

## 1.0.4

- `layouts <map>|all -o <folder>`: a map's bomb sites and buy zones (their outlines and heights), hostage spots
  and rescue zones, and the T and CT spawns, from the map's own entities, as `<map>.layouts.json` beside its
  `.glb`; `competitive`, and `wingman` where the map has its own spawns for it. The viewer draws them on the map.

## 1.0.3

- The table says the outcome on every row, as the viewer's outcome contract has it: `matchWon` (0/1, the row's
  team won the match, where the recording shows the end) and `roundEndReason` (`elimination`, `bomb`, `defuse`,
  `time`, `surrender`, `draw`); the match document names the match's `winner` and how it is known.
- `scoreboard` reads the match document straight from a `.3dheat` container, as well as from a loose
  `.match.json`.
- Documentation: a "Before you start" page for newcomers, a generated command and column reference
  (`tools/gen_docs_reference.py`), the release checklist (`docs/maintaining.md`), and made-up names in
  every example.
- README: a quick start for new users.

## Docs

Where each feature is documented (<https://holdi601.github.io/3DHeat-CS2/>):

| Feature | Page |
|---|---|
| Installing, first run | [Before you start](docs/before-you-start.md), [Installing](docs/installing.md) |
| `demos`: demos into one file a match | [Commands](docs/commands.md#demos---demos-into-tables-and-match-documents) |
| Parts of a match, chains, the clock, rounds | [Building a match](docs/building-matches.md) |
| What is read from a demo | [Reading a demo](docs/reading-demos.md) |
| ADR, KAST, trades, clutches, economy | [Statistics](docs/statistics.md) |
| The table's columns, the player's state, round pay | [The heatmap table](docs/output-table.md) |
| The match document | [The match document](docs/output-match-json.md) |
| `.3dheat` containers, `--loose`, sidecars, completeness | [One file a match](docs/output-container.md) |
| `map`: a map's collision mesh | [Map export](docs/map-export.md), [Commands](docs/commands.md#map---a-maps-geometry-as-glb) |
| `scoreboard` | [Commands](docs/commands.md#scoreboard---a-match-as-text) |
| Loading it in the viewer | [Using it with 3DHeat](docs/using-with-3dheat.md) |
| Every option and column, generated | [Reference](docs/cli-reference.md) |
| Release checks | [Updates](docs/updates.md), [Maintaining](docs/maintaining.md) |
