---
title: "Asennus"
nav_order: 3
lang: "fi"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Asennus {#installing}

Uusi komentorivin kanssa? Lue ensin [Ennen kuin aloitat](before-you-start.md).

3DHeat CS2 on Python-paketti, jota ajetaan omasta kansiostaan. Mitään ei tarvitse
rakentaa eikä asentaa asentajalla; se tarvitsee Pythonin, neljä pakettia (ja pytestin
testejä varten) sekä - vain kartan vientiä varten - Counter-Strike 2:n asennettuna ja
Source2Viewerin komentorivijulkaisun.

## Koodin hankkiminen {#getting-the-code}

Lataa julkaisuarkisto
[julkaisusivulta](https://github.com/Holdi601/3DHeat-CS2/releases) ja pura se, tai
jos sinulla on Git, kloonaa repositorio:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Molemmat kopiot voivat päivittää itsensä (katso [Päivitykset](updates.md)).
Asennettu versio on tiedoston `VERSION` yksi rivi.

Aja jokainen komento tästä kansiosta: `python -m heat3d_cs2` löytää paketin, koska se on
nykyisessä kansiossa. Pakettia ei asenneta kansioon `site-packages`.

## Python ja paketit {#python-and-the-packages}

Python 3.10 tai uudempi. Virtuaaliympäristö pitää paketit erillään muista. Windowsissa
(PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Jos PowerShell ei suostu ajamaan skriptiä, aja ensin
`Set-ExecutionPolicy -Scope Process RemoteSigned` (se on voimassa vain tässä ikkunassa).
Linuxissa tai macOS:ssä:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Asennus toimii, kun `python -m heat3d_cs2 --help` tulostaa `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paketti | Vähimmäisversio | Käyttö | Lisenssi |
|---|---|---|---|
| `demoparser2` | 0.42 | `.dem`-tiedostojen lukeminen (pelaajat tikeittäin, pelin tapahtumat) | MIT |
| `pyarrow` | 15 | Parquet-taulukon kirjoittaminen | Apache-2.0 |
| `pandas` | 2.0 | välitaulukot | BSD-3-Clause |
| `numpy` | 1.24 | laskutoimitukset niillä | BSD-3-Clause |
| `pytest` | 8.0 | vain testit | MIT |

Komennot `demos` ja `scoreboard` eivät tarvitse mitään muuta.

## Kartan vientiä varten: Counter-Strike 2 ja Source2Viewerin CLI {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` lukee kartan asentamastasi pelistä ja purkaa sen
**Source2Viewerin komentoriviltä**, joka on erillinen ohjelma projektista
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(MIT-lisenssi). Sitä ei ole mukana paketissa, eikä sitä voi asentaa pip:llä.

1. Lataa järjestelmällesi **CLI**-julkaisu
   [ValveResourceFormat-julkaisuista](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   ja pura se mihin tahansa.
2. Tee se löydettäväksi jollakin kolmesta tavasta. Ne kokeillaan tässä järjestyksessä:
   1. `--source2viewer <polku suoritettavaan tiedostoon>` komentorivillä;
   2. ympäristömuuttuja `HEAT3D_SOURCE2VIEWER`, joka on asetettu suoritettavan tiedoston polkuun;
   3. suoritettava tiedosto nimeltä `Source2Viewer-CLI` tai `Source2Viewer-CLI.exe` polulla `PATH`.

   Ehdokas käytetään vain, jos polku on olemassa. Jos mitään ei löydy, komento
   pysähtyy viestiin `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Muuttujan asettaminen, esimerkiksi:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Mistä CS2 etsitään {#where-cs2-is-looked-for}

Kartta on `.vpk`-arkisto pelin kansion alla:
`<Steam-kirjasto>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Steam-kirjastot löydetään näistä juuristä ja jokaisesta juuren
`config\libraryfolders.vdf`-tiedoston `"path"`-kohdasta:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Kun Steam on muualla, anna CS2:n kansio itse valinnalla `--game` (kansio, joka sisältää
`game\csgo`), tai anna `.vpk`-tiedoston polku kartan nimen sijaan. Katso
[Kartan vienti](map-export.md).

## Asennuksen tarkistaminen {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testit ajetaan koodissa rakennetulla synteettisellä demolla, eivätkä ne tarvitse demoa,
peliä tai Source2Vieweria (katso [Kehitys](development.md)).

Jokainen `python -m heat3d_cs2` -käynnistys tarkistaa ensin, enintään kuuden tunnin
välein, onko uudempi julkaisu ilmestynyt; aseta `HEAT3D_NO_UPDATE=1`, jos haluat
tarkistuksen pois päältä (katso [Päivitykset](updates.md)).
