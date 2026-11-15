---
title: "Installasjon"
nav_order: 3
lang: "no"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installasjon {#installing}

Ny på kommandolinjen? Les [Før du begynner](before-you-start.md) først.

3DHeat CS2 er en Python-pakke som kjøres fra sin egen mappe. Det er ingenting å
bygge og ingen installasjonsprogram; det trenger Python, fire pakker (pluss pytest
for testene) og - bare for karteksporten - Counter-Strike 2 installert og
kommandolinjeversjonen av Source2Viewer.

## Å hente koden {#getting-the-code}

Last ned en utgivelsesarkiv fra
[utgivelsessiden](https://github.com/Holdi601/3DHeat-CS2/releases) og pakk den ut,
eller, hvis du har Git, klon repositoriet:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Begge typer kopier kan oppdatere seg selv (se [Oppdateringer](updates.md)). Den installerte
versjonen er den ene linjen i filen `VERSION`.

Kjør hver kommando fra denne mappen: `python -m heat3d_cs2` finner pakken fordi den er i
gjeldende mappe. Pakken installeres ikke i `site-packages`.

## Python og pakkene {#python-and-the-packages}

Python 3.10 eller nyere. Et virtuelt miljø holder pakkene adskilt fra alt annet. På Windows
(PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Hvis PowerShell nekter å kjøre skriptet, kjør først
`Set-ExecutionPolicy -Scope Process RemoteSigned` (det gjelder bare for det vinduet). På Linux
eller macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Det fungerer når `python -m heat3d_cs2 --help` skriver ut `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pakke | Minimum | Brukes til | Lisens |
|---|---|---|---|
| `demoparser2` | 0.42 | lese `.dem`-filer (spillere per tick, spillhendelser) | MIT |
| `pyarrow` | 15 | skrive Parquet-tabellen | Apache-2.0 |
| `pandas` | 2.0 | tabellene i mellomtrinnene | BSD-3-Clause |
| `numpy` | 1.24 | regning på dem | BSD-3-Clause |
| `pytest` | 8.0 | bare testene | MIT |

Kommandoene `demos` og `scoreboard` trenger ikke noe mer.

## For karteksporten: Counter-Strike 2 og Source2Viewers CLI {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` leser kartet fra spillet du har installert, og dekoder det med
**Source2Viewers kommandolinje**, et eget program fra
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)-prosjektet
(MIT-lisensiert). Det følger ikke med, og kan ikke installeres med pip.

1. Last ned **CLI**-versjonen for ditt system fra
   [ValveResourceFormat-utgivelsene](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   og pakk den ut hvor som helst.
2. Gjør den findbar, på en av tre måter. De prøves i denne rekkefølgen:
   1. `--source2viewer <sti til den kjørbare filen>` på kommandolinjen;
   2. miljøvariabelen `HEAT3D_SOURCE2VIEWER` satt til stien til den kjørbare filen;
   3. en kjørbar fil som heter `Source2Viewer-CLI` eller `Source2Viewer-CLI.exe` på `PATH`.

   Et kandidat brukes bare hvis stien finnes. Finnes ingen, stopper kommandoen med
   `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH,
   set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Slik setter du variabelen, for eksempel:

```bash
# Windows (PowerShell), for gjeldende økt
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Hvor CS2 leties etter {#where-cs2-is-looked-for}

Kartet er et `.vpk`-arkiv under spillets mappe:
`<Steam-bibliotek>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<kart>.vpk`.
Steam-bibliotekene finnes fra disse rotene, og fra hver `"path"` som står i hver rots
`config\libraryfolders.vdf`:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Er Steam et annet sted, gi selve CS2-mappen med `--game` (mappen som inneholder
`game\csgo`), eller gi stien til `.vpk`-filen i stedet for kartnavnet. Se
[Eksport av kart](map-export.md).

## Sjekke installasjonen {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testene kjører på en syntetisk demo bygget i kode, og trenger ingen demo, ingen spill og
ingen Source2Viewer (se [Utvikling](development.md)).

Hver start av `python -m heat3d_cs2` sjekker først, høyst hvert sjette timer, om en nyere
utgivelse finnes; sett `HEAT3D_NO_UPDATE=1` for å slå det av (se [Oppdateringer](updates.md)).
