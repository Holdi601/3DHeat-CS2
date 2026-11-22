---
title: Installing
nav_order: 3
---

# Installing

New to the command line? Read [Before you start](before-you-start.md) first.

## The standalone program (no Python needed)

Each [release](https://github.com/Holdi601/3DHeat-CS2/releases/latest) has a
ready-to-run program for Windows (`heat3d-cs2-<version>-windows-x64.zip`) and
Linux (`...-linux-x64.tar.gz`, also for Steam Deck), with a `SHA256SUMS` file
to check the download. Unpack it anywhere and start `heat3d-cs2`.

Started without arguments it opens a window that:

- finds your Counter-Strike 2 install (Steam on Windows and Linux, also
  flatpak and Steam Deck), or lets you choose its folder;
- says what is missing: the game, Source2Viewer-CLI (maps, the catalogue and
  the model pack need it, demos do not; see [Map export](map-export.md)),
  free disk space;
- lists the install's maps as new, changed by a game update, exported by an
  older version, or up to date, and exports the ones you pick, one at a time,
  into the 3DHeat levels folder (`HEAT3D_LEVELS`, by default
  `%LOCALAPPDATA%\3DHeat\levels` on Windows and `~/.local/share/3dheat/levels`
  elsewhere), as `cs2/<map>.glb` with `cs2/<map>.layouts.json` beside it;
- converts a folder of demos, and writes the catalogue and the model pack;
- checks for updates and asks before installing one, unless you tick
  *Update automatically*.

The same program runs every command below: `heat3d-cs2 demos <demos> -o <folder>`,
`heat3d-cs2 map <map> -o <map>.glb`. For scripts: `heat3d-cs2 status --json`
reports the maps' state, `heat3d-cs2 extract --new` exports only the new and
`heat3d-cs2 --check --json` what is found and missing.
The 3DHeat app's Extractors panel installs, updates and starts it for you.

The window walks through four steps (find the game, choose, work, done) in the 3DHeat look, dark or light. On Windows the program opens only its window, with no console window; in a terminal it prints as usual, and `heat3d-cs2-cli.cmd` in the same folder makes the terminal wait for it and pass on its exit code.

Replays from the command line: `heat3d-cs2 convert <replay>... -o <folder> [--progress-json]` converts them (one JSON line per replay with `--progress-json`), and `heat3d-cs2 info <replay> --json` prints what a replay says about its match (map, mode, date, length, players, teams, result, game version), read from its header without converting it. The 3DHeat Library uses both.

## From the source (Python)

3DHeat CS2 is a Python package run from its own folder. There is nothing to
build and no installer; it needs Python, four packages (plus pytest for the tests), and - only for the map
export - Counter-Strike 2 installed and Source2Viewer's command-line build.

## Getting the code

Download a release archive from the
[releases page](https://github.com/Holdi601/3DHeat-CS2/releases) and unpack it,
or, if you have Git, clone the repository:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Both kinds of copy can update themselves (see [Updates](updates.md)). The
installed version is the one line in the file `VERSION`.

Run every command from that folder: `python -m heat3d_cs2` finds the package
because it is in the current directory. The package is not installed into
`site-packages`.

## Python and the packages

Python 3.10 or later. A virtual environment keeps the packages apart from
anything else. On Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell refuses to run the script, run
`Set-ExecutionPolicy -Scope Process RemoteSigned` first (it lasts only for that
window). On Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

It works when `python -m heat3d_cs2 --help` prints `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Package | Minimum | Used for | Licence |
|---|---|---|---|
| `demoparser2` | 0.42 | reading `.dem` files (players per tick, game events) | MIT |
| `pyarrow` | 15 | writing the Parquet table | Apache-2.0 |
| `pandas` | 2.0 | the tables in between | BSD-3-Clause |
| `numpy` | 1.24 | arithmetic on them | BSD-3-Clause |
| `pytest` | 8.0 | the tests only | MIT |

The `demos` and `scoreboard` commands need nothing else.

## For the map export: Counter-Strike 2 and Source2Viewer's CLI

`python -m heat3d_cs2 map` reads the map from the game you have installed, and
decodes it with **Source2Viewer's command line**, a separate program from the
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
project (MIT licensed). It is not bundled and cannot be installed with pip.

1. Download the **CLI** build for your system from
   [the ValveResourceFormat releases](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   and unpack it anywhere.
2. Make it findable, in any of three ways. They are tried in this order:
   1. `--source2viewer <path to the executable>` on the command line;
   2. the environment variable `HEAT3D_SOURCE2VIEWER` set to the executable's path;
   3. an executable named `Source2Viewer-CLI` or `Source2Viewer-CLI.exe` on `PATH`.

   A candidate is used only if the path exists. If none is found the command
   stops with `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Setting the variable, for example:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Where CS2 is looked for

The map is a `.vpk` archive under the game's folder:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
The Steam libraries are found from these roots, and from every `"path"` listed
in each root's `config\libraryfolders.vdf`:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

When Steam is elsewhere, pass the CS2 folder itself with `--game` (the folder
that contains `game\csgo`), or pass the path of the `.vpk` instead of the map
name. See [Map export](map-export.md).

## Checking the install

```bash
python -m heat3d_cs2 --help
python -m pytest
```

The tests run on a synthetic demo built in code and need no demo, game or
Source2Viewer (see [Development](development.md)).

Every start of `python -m heat3d_cs2` first checks, at most every six hours,
whether a newer release is out; set `HEAT3D_NO_UPDATE=1` to switch that off
(see [Updates](updates.md)).
