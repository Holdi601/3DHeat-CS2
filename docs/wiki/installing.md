
# Installing

3DHeat CS2 is a Python package run from its own folder. There is nothing to
build and no installer; it needs Python, four packages, and - only for the map
export - Counter-Strike 2 installed and Source2Viewer's command-line build.

## Getting the code

Either clone the repository:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

or download a release archive from the
[releases page](https://github.com/Holdi601/3DHeat-CS2/releases) and unpack it.
Both kinds of copy can update themselves (see [Updates](updates)). The
installed version is the one line in the file `VERSION`.

Run every command from that folder: `python -m heat3d_cs2` finds the package
because it is in the current directory. The package is not installed into
`site-packages`.

## Python and the packages

No minimum Python version is declared. The code uses features of Python 3.9
and later (`str.removeprefix`, built-in generic types); a current Python 3
(3.10 or later) is the safe choice. A virtual environment keeps the packages
apart from anything else:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

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
name. See [Map export](map-export).

## Checking the install

```bash
python -m heat3d_cs2 --help
python -m pytest
```

The tests run on a synthetic demo built in code and need no demo, game or
Source2Viewer (see [Development](development)).

Every start of `python -m heat3d_cs2` first checks, at most every six hours,
whether a newer release is out; set `HEAT3D_NO_UPDATE=1` to switch that off
(see [Updates](updates)).
