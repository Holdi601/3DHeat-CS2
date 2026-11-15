---
title: Installeren
nav_order: 3
lang: "nl"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installeren {#installing}

Nieuw met de opdrachtregel? Lees eerst [Voordat je begint](before-you-start.md).

3DHeat CS2 is een Python-pakket dat vanuit zijn eigen map wordt gestart. Er is niets te bouwen en geen installatieprogramma; je hebt Python nodig, vier pakketten (plus pytest voor de tests), en - alleen voor de kaartexport - Counter-Strike 2 geïnstalleerd en de opdrachtregelversie van Source2Viewer.

## De code ophalen {#getting-the-code}

Download een releasearchief van de [releasepagina](https://github.com/Holdi601/3DHeat-CS2/releases) en pak het uit, of, als je Git hebt, kloon de repository:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Beide soorten kopieën kunnen zichzelf updaten (zie [Updates](updates.md)). De geïnstalleerde versie is de ene regel in het bestand `VERSION`.

Voer elke opdracht uit vanuit die map: `python -m heat3d_cs2` vindt het pakket omdat het in de huidige map staat. Het pakket wordt niet in `site-packages` geïnstalleerd.

## Python en de pakketten {#python-and-the-packages}

Python 3.10 of later. Een virtuele omgeving houdt de pakketten gescheiden van al het andere. Op Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Als PowerShell weigert het script uit te voeren, voer eerst `Set-ExecutionPolicy -Scope Process RemoteSigned` uit (dat geldt alleen voor dat venster). Op Linux of macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Het werkt wanneer `python -m heat3d_cs2 --help` `usage: heat3d_cs2 ...` afdrukt.

`requirements.txt`:

| Pakket | Minimum | Gebruikt voor | Licentie |
|---|---|---|---|
| `demoparser2` | 0.42 | het lezen van `.dem`-bestanden (spelers per tick, spelgebeurtenissen) | MIT |
| `pyarrow` | 15 | het schrijven van de Parquet-tabel | Apache-2.0 |
| `pandas` | 2.0 | de tussentijdse tabellen | BSD-3-Clause |
| `numpy` | 1.24 | rekenen met ze | BSD-3-Clause |
| `pytest` | 8.0 | alleen de tests | MIT |

De opdrachten `demos` en `scoreboard` hebben niets anders nodig.

## Voor de kaartexport: Counter-Strike 2 en de Source2Viewer-CLI {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` leest de kaart uit het spel dat je hebt geïnstalleerd, en decodeert die met de **opdrachtregel van Source2Viewer**, een apart programma van het project [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (MIT-licentie). Het zit er niet bij en kan niet met pip worden geïnstalleerd.

1. Download de **CLI**-versie voor je systeem van [de ValveResourceFormat-releases](https://github.com/ValveResourceFormat/ValveResourceFormat/releases) en pak die ergens uit.
2. Zorg dat hij gevonden kan worden, op een van drie manieren. Ze worden in deze volgorde geprobeerd:
   1. `--source2viewer <pad naar het uitvoerbare bestand>` op de opdrachtregel;
   2. de omgevingsvariabele `HEAT3D_SOURCE2VIEWER` met het pad naar het uitvoerbare bestand;
   3. een uitvoerbaar bestand met de naam `Source2Viewer-CLI` of `Source2Viewer-CLI.exe` op `PATH`.

   Een kandidaat wordt alleen gebruikt als het pad bestaat. Wordt er niets gevonden, dan stopt de opdracht met `Source2Viewer-CLI not found: download the command line build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

De variabele instellen, bijvoorbeeld:

```bash
# Windows (PowerShell), voor de huidige sessie
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Waar naar CS2 wordt gezocht {#where-cs2-is-looked-for}

De map is een `.vpk`-archief onder de spelmap: `<Steam-bibliotheek>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`. De Steam-bibliotheken worden gevonden vanuit deze hoofdmappen, en vanuit elk `"path"` dat in het bestand `config\libraryfolders.vdf` van elke hoofdmap staat:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Staat Steam ergens anders, geef dan de CS2-map zelf op met `--game` (de map die `game\csgo` bevat), of geef het pad van het `.vpk` op in plaats van de kaartnaam. Zie [Kaart exporteren](map-export.md).

## De installatie controleren {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

De tests draaien op een synthetische demo die in code wordt gemaakt en hebben geen demo, spel of Source2Viewer nodig (zie [Ontwikkeling](development.md)).

Bij elke start van `python -m heat3d_cs2` wordt eerst gecontroleerd, hooguit eens per zes uur, of er een nieuwere release is; zet `HEAT3D_NO_UPDATE=1` om dat uit te schakelen (zie [Updates](updates.md)).
