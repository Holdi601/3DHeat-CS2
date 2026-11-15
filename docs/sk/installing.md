---
title: Inštalácia
nav_order: 3
lang: "sk"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Inštalácia {#installing}

Nový v príkazovom riadku? Najprv si prečítajte [Ako začať](before-you-start.md).

3DHeat CS2 je balík Pythonu spúšťaný zo svojho vlastného priečinka. Nič sa
nestavia a nie je tu inštalátor; treba Python, štyri balíky (a pytest na testy)
a - iba pre export mapy - nainštalovanú Counter-Strike 2 a príkazovú verziu
Source2Viewer.

## Získanie kódu {#getting-the-code}

Stiahnite archív vydania zo
[stránky vydaní](https://github.com/Holdi601/3DHeat-CS2/releases) a rozbaľte
ho, alebo, ak máte Git, naklonujte repozitár:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Obe kópie sa vedia aktualizovať samy (pozrite [Aktualizácie](updates.md)).
Nainštalovaná verzia je jeden riadok v súbore `VERSION`.

Každý príkaz spúšťajte z tohto priečinka: `python -m heat3d_cs2` nájde balík,
lebo je v aktuálnom priečinku. Balík sa neinštaluje do `site-packages`.

## Python a balíky {#python-and-the-packages}

Python 3.10 alebo novší. Virtuálne prostredie oddelí balíky od všetkého
ostatného. Vo Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ak PowerShell odmietne skript spustiť, najprv spustite
`Set-ExecutionPolicy -Scope Process RemoteSigned` (platí len pre toto okno). Na
Linuxe alebo macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funguje, keď `python -m heat3d_cs2 --help` vypíše `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Balík | Minimum | Na čo | Licencia |
|---|---|---|---|
| `demoparser2` | 0.42 | čítanie súborov `.dem` (hráči v každom tiku, herné udalosti) | MIT |
| `pyarrow` | 15 | zápis tabuľky Parquet | Apache-2.0 |
| `pandas` | 2.0 | tabuľky medzi tým | BSD-3-Clause |
| `numpy` | 1.24 | aritmetika nad nimi | BSD-3-Clause |
| `pytest` | 8.0 | iba testy | MIT |

Príkazy `demos` a `scoreboard` nepotrebujú nič iné.

## Pre export mapy: Counter-Strike 2 a príkazová verzia Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` číta mapu z hry, ktorú máte nainštalovanú, a
dekóduje ju **príkazovým riadkom Source2Viewer**, samostatným programom z
projektu [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(licencia MIT). Nie je priložený a nedá sa nainštalovať cez pip.

1. Stiahnite zostavenie **CLI** pre váš systém z
   [vydaní ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   a rozbaľte ho kamkoľvek.
2. Nastavte, aby sa dal nájsť, jedným z troch spôsobov. Skúšajú sa v tomto poradí:
   1. `--source2viewer <cesta k spustiteľnému súboru>` na príkazovom riadku;
   2. premenná prostredia `HEAT3D_SOURCE2VIEWER` nastavená na cestu k spustiteľnému súboru;
   3. spustiteľný súbor s názvom `Source2Viewer-CLI` alebo `Source2Viewer-CLI.exe` v `PATH`.

   Kandidát sa použije, iba ak jeho cesta existuje. Ak sa nenájde žiadny, príkaz
   sa zastaví s hlásením `Source2Viewer-CLI not found: download the command line
   build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Nastavenie premennej, napríklad:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Kde sa hľadá CS2 {#where-cs2-is-looked-for}

Mapa je archív `.vpk` v priečinku hry:
`<knižnica Steamu>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Knižnice Steamu sa hľadajú z týchto koreňov a z každej `"path"` uvedenej v
`config\libraryfolders.vdf` každého koreňa:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Keď je Steam inde, zadajte samotný priečinok CS2 cez `--game` (priečinok, ktorý
obsahuje `game\csgo`), alebo zadajte cestu k `.vpk` namiesto názvu mapy. Pozrite
[Export mapy](map-export.md).

## Kontrola inštalácie {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testy bežia na syntetickom deme zostavenom v kóde a nepotrebujú demo, hru ani
Source2Viewer (pozrite [Vývoj](development.md)).

Každé spustenie `python -m heat3d_cs2` najprv najviac raz za šesť hodín skontroluje,
či nie je vydaná novšia verzia; nastavte `HEAT3D_NO_UPDATE=1`, ak to chcete
vypnúť (pozrite [Aktualizácie](updates.md)).
