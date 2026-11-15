---
title: "Uppsetning"
nav_order: 3
lang: "is"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Uppsetning {#installing}

Hefurðu aldrei notað skipanalínu? Lestu fyrst [Áður en þú byrjar](before-you-start.md).

3DHeat CS2 er Python-pakki sem er keyrður úr sinni eigin möppu. Ekkert þarf að
smíða og enginn uppsetningarforrit er til; það þarf Python, fjóra pakka (auk pytest fyrir prófanirnar), og - aðeins fyrir kortaútflutning -
uppsett Counter-Strike 2 og skipanalínuútgáfu Source2Viewer.

## Að ná í kóðann {#getting-the-code}

Sæktu útgáfusafn af
[útgáfusíðunni](https://github.com/Holdi601/3DHeat-CS2/releases) og pakkaðu því upp,
eða, ef þú ert með Git, klónaðu hugbúnaðarsafnið:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Báðar gerðir afrits geta uppfært sig sjálfar (sjá [Uppfærslur](updates.md)). Uppsetta
útgáfan er línan í skránni `VERSION`.

Keyrðu hverja skipun úr þeirri möppu: `python -m heat3d_cs2` finnur pakkann
því hann er í núverandi möppu. Pakkinn er ekki settur upp í
`site-packages`.

## Python og pakkarnir {#python-and-the-packages}

Python 3.10 eða nýrra. Sýndarumhverfi heldur pökkunum aðskildum frá
öllu öðru. Á Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ef PowerShell neitar að keyra skriftuna, keyrðu fyrst
`Set-ExecutionPolicy -Scope Process RemoteSigned` (það gildir aðeins í þeim
glugga). Á Linux eða macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Það virkar þegar `python -m heat3d_cs2 --help` prentar `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pakki | Lágmark | Notaður í | Leyfi |
|---|---|---|---|
| `demoparser2` | 0.42 | að lesa `.dem`-skrár (leikmenn á hverju tikki, leikatburðir) | MIT |
| `pyarrow` | 15 | að skrifa Parquet-töfluna | Apache-2.0 |
| `pandas` | 2.0 | töflurnar þar á milli | BSD-3-Clause |
| `numpy` | 1.24 | reikning á þeim | BSD-3-Clause |
| `pytest` | 8.0 | aðeins prófanirnar | MIT |

Skipanirnar `demos` og `scoreboard` þurfa ekkert annað.

## Fyrir kortaútflutning: Counter-Strike 2 og CLI Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` les kortið úr leiknum sem þú hefur uppsettan, og
afkóðar það með **skipanalínu Source2Viewer**, sérstöku forriti úr
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
verkefninu (MIT-leyfi). Það fylgir ekki með og er ekki hægt að setja upp með pip.

1. Sæktu **CLI**-útgáfuna fyrir þitt kerfi af
   [útgáfusíðu ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   og pakkaðu henni upp hvar sem er.
2. Gerðu hana finnanlega, á einhvern af þremur vegum. Þeir eru reyndir í þessari röð:
   1. `--source2viewer <path to the executable>` í skipanalínunni;
   2. umhverfisbreytan `HEAT3D_SOURCE2VIEWER` stillt á slóð keyrsluskrárinnar;
   3. keyrsluskrá sem heitir `Source2Viewer-CLI` eða `Source2Viewer-CLI.exe` á `PATH`.

   Frambjóðandi er aðeins notaður ef slóðin er til. Ef ekkert finnst stöðvast skipunin
   með `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Að stilla breytuna, til dæmis:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Hvar CS2 er leitað {#where-cs2-is-looked-for}

Kortið er `.vpk`-safnskrá undir möppu leiksins:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Steam-söfnin eru fundin út frá þessum rótum, og út frá hverju `"path"` sem er talið upp
í `config\libraryfolders.vdf` hverrar rótar:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Þegar Steam er annars staðar, gefðu CS2-möppuna sjálfa með `--game` (mappan
sem inniheldur `game\csgo`), eða gefðu slóð `.vpk`-skrárinnar í stað kortaheitisins.
Sjá [Kortaútflutningur](map-export.md).

## Að athuga uppsetninguna {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Prófanirnar keyra á gervi-demo-skrá smíðaðri í kóða og þurfa enga demo-skrá, leik eða
Source2Viewer (sjá [Þróun](development.md)).

Hver ræsing á `python -m heat3d_cs2` athugar fyrst, í mesta lagi á sex tíma fresti,
hvort nýrri útgáfa sé komin; stilltu `HEAT3D_NO_UPDATE=1` til að slökkva á því
(sjá [Uppfærslur](updates.md)).
