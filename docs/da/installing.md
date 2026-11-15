---
title: "Installation"
nav_order: 3
lang: "da"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installation {#installing}

Ny til kommandolinjen? Læs [Før du går i gang](before-you-start.md) først.

3DHeat CS2 er en Python-pakke, der køres fra sin egen mappe. Der er intet at bygge
og intet installationsprogram; den har brug for Python, fire pakker (plus pytest til
testene) og - kun til kortudtrækket - Counter-Strike 2 installeret og Source2Viewers
kommandolinjeversion.

## Hent koden {#getting-the-code}

Hent et udgivelsesarkiv fra
[udgivelsessiden](https://github.com/Holdi601/3DHeat-CS2/releases) og pak det ud,
eller, hvis du har Git, klon repositoriet:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Begge slags kopier kan opdatere sig selv (se [Opdateringer](updates.md)). Den installerede
version er den ene linje i filen `VERSION`.

Kør hver kommando fra den mappe: `python -m heat3d_cs2` finder pakken, fordi den
ligger i den aktuelle mappe. Pakken bliver ikke installeret i `site-packages`.

## Python og pakkerne {#python-and-the-packages}

Python 3.10 eller nyere. Et virtuelt miljø holder pakkerne adskilt fra alt andet. På Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Hvis PowerShell nægter at køre scriptet, så kør først
`Set-ExecutionPolicy -Scope Process RemoteSigned` (det gælder kun for det vindue). På Linux eller macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Det virker, når `python -m heat3d_cs2 --help` udskriver `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pakke | Minimum | Bruges til | Licens |
|---|---|---|---|
| `demoparser2` | 0.42 | læsning af `.dem`-filer (spillere pr. tick, spilhændelser) | MIT |
| `pyarrow` | 15 | skrivning af Parquet-tabellen | Apache-2.0 |
| `pandas` | 2.0 | tabellerne undervejs | BSD-3-Clause |
| `numpy` | 1.24 | regning på dem | BSD-3-Clause |
| `pytest` | 8.0 | kun testene | MIT |

Kommandoerne `demos` og `scoreboard` har ikke brug for andet.

## Til kortudtrækket: Counter-Strike 2 og Source2Viewers CLI {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` læser kortet fra det spil, du har installeret, og
afkoder det med **Source2Viewers kommandolinje**, et andet program end
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)-
projektet (MIT-licens). Det er ikke med i pakken og kan ikke installeres med pip.

1. Hent **CLI**-builden til dit system fra
   [ValveResourceFormat-udgivelserne](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   og pak den ud et vilkårligt sted.
2. Gør den findbar, på en af tre måder. De bliver prøvet i denne rækkefølge:
   1. `--source2viewer <sti til den kørbare fil>` på kommandolinjen;
   2. miljøvariablen `HEAT3D_SOURCE2VIEWER` sat til den kørbare fils sti;
   3. en kørbar fil ved navn `Source2Viewer-CLI` eller `Source2Viewer-CLI.exe` på `PATH`.

   En kandidat bliver kun brugt, hvis stien findes. Hvis ingen bliver fundet, stopper
   kommandoen med `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Sådan sætter du variablen, for eksempel:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Hvor CS2 bliver søgt {#where-cs2-is-looked-for}

Kortet er et `.vpk`-arkiv under spillets mappe:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Steam-bibliotekerne bliver fundet fra disse rødder og fra hver `"path"`, der står i
hver rods `config\libraryfolders.vdf`:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Når Steam er et andet sted, så giv selve CS2-mappen med `--game` (mappen der
indeholder `game\csgo`), eller giv stien til `.vpk`-filen i stedet for kortnavnet.
Se [Kortudtræk](map-export.md).

## Tjek installationen {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testene kører på en syntetisk demo, bygget i kode, og har ikke brug for demo, spil
eller Source2Viewer (se [Udvikling](development.md)).

Hver start af `python -m heat3d_cs2` tjekker først, højst hver sjette time, om der er
kommet en nyere udgivelse; sæt `HEAT3D_NO_UPDATE=1` for at slå det fra (se
[Opdateringer](updates.md)).
