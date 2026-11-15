---
title: "Installera"
nav_order: 3
lang: "sv"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installera {#installing}

Ny på kommandoraden? Läs [Innan du börjar](before-you-start.md) först.

3DHeat CS2 är ett Python-paket som körs från sin egen mapp. Där finns inget att bygga och
inget installationsprogram; det behöver Python, fyra paket (plus pytest för testerna), och -
bara för kartexporten - Counter-Strike 2 installerat och Source2Viewers kommandoradsversion.

## Hämta koden {#getting-the-code}

Ladda ner ett utgivningsarkiv från
[utgivningssidan](https://github.com/Holdi601/3DHeat-CS2/releases) och packa upp det, eller,
om du har Git, klona förrådet:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Båda sorternas kopior kan uppdatera sig själva (se [Uppdateringar](updates.md)). Den
installerade versionen är raden i filen `VERSION`.

Kör alla kommandon från den mappen: `python -m heat3d_cs2` hittar paketet för att det ligger i
den aktuella mappen. Paketet installeras inte i `site-packages`.

## Python och paketen {#python-and-the-packages}

Python 3.10 eller senare. En virtuell miljö håller paketen åtskilda från allt annat. På Windows
(PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Om PowerShell vägrar köra skriptet, kör först
`Set-ExecutionPolicy -Scope Process RemoteSigned` (det gäller bara för det fönstret). På Linux
eller macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Det fungerar när `python -m heat3d_cs2 --help` skriver ut `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paket | Minst | Används till | Licens |
|---|---|---|---|
| `demoparser2` | 0.42 | läsa `.dem`-filer (spelare per tick, spelhändelser) | MIT |
| `pyarrow` | 15 | skriva Parquet-tabellen | Apache-2.0 |
| `pandas` | 2.0 | tabellerna mellan stegen | BSD-3-Clause |
| `numpy` | 1.24 | räkning på dem | BSD-3-Clause |
| `pytest` | 8.0 | bara testerna | MIT |

Kommandona `demos` och `scoreboard` behöver inget annat.

## För kartexporten: Counter-Strike 2 och Source2Viewers CLI {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` läser kartan från spelet du har installerat, och avkodar den med
**Source2Viewers kommandorad**, ett separat program från projektet
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (MIT-licens).
Det ingår inte och kan inte installeras med pip.

1. Ladda ner **CLI**-versionen för ditt system från
   [ValveResourceFormats utgivningar](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   och packa upp den var som helst.
2. Gör den hittbar, på något av tre sätt. De prövas i den här ordningen:
   1. `--source2viewer <sökväg till den körbara filen>` på kommandoraden;
   2. miljövariabeln `HEAT3D_SOURCE2VIEWER` satt till den körbara filens sökväg;
   3. en körbar fil som heter `Source2Viewer-CLI` eller `Source2Viewer-CLI.exe` på `PATH`.

   En kandidat används bara om sökvägen finns. Hittas ingen stoppar kommandot med
   `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH,
   set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Att sätta variabeln, till exempel:

```bash
# Windows (PowerShell), för den aktuella sessionen
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Var CS2 letas {#where-cs2-is-looked-for}

Kartan är ett `.vpk`-arkiv under spelets mapp:
`<Steam-bibliotek>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<karta>.vpk`.
Steam-biblioteken hittas från dessa rötter, och från varje `"path"` som står i varje rots
`config\libraryfolders.vdf`:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

När Steam ligger någon annanstans, skicka själva CS2-mappen med `--game` (mappen som innehåller
`game\csgo`), eller skicka sökvägen till `.vpk`-filen i stället för kartnamnet. Se
[Kartexport](map-export.md).

## Kontrollera installationen {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testerna körs på en syntetisk demo byggd i kod och behöver ingen demo, inget spel och ingen
Source2Viewer (se [Utveckling](development.md)).

Varje start av `python -m heat3d_cs2` kontrollerar först, högst var sjätte timme, om en nyare
utgåva finns; sätt `HEAT3D_NO_UPDATE=1` för att stänga av det (se [Uppdateringar](updates.md)).
