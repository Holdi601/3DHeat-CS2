---
title: Instalace
nav_order: 3
lang: "cs"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalace {#installing}

Nejste zvyklí na příkazový řádek? Nejdřív si přečtěte [Než začnete](before-you-start.md).

3DHeat CS2 je balíček Pythonu, který se spouští ze své vlastní složky. Nic se
nesestavuje a není žádný instalátor; potřebuje Python, čtyři balíčky (plus pytest
pro testy) a - jen pro export mapy - nainstalovaný Counter-Strike 2 a
příkazořádkovou verzi Source2Viewer.

## Získání kódu {#getting-the-code}

Stáhněte si archiv vydání ze
[stránky vydání](https://github.com/Holdi601/3DHeat-CS2/releases) a rozbalte ho,
nebo, máte-li Git, naklonujte repozitář:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Obě podoby kopie se umějí aktualizovat samy (viz [Aktualizace](updates.md)).
Nainstalovaná verze je ten jeden řádek v souboru `VERSION`.

Spouštějte každý příkaz z této složky: `python -m heat3d_cs2` najde balíček,
protože je v aktuální složce. Balíček se neinstaluje do `site-packages`.

## Python a balíčky {#python-and-the-packages}

Python 3.10 nebo novější. Virtuální prostředí udrží balíčky odděleně od všeho
ostatního. Ve Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Odmítne-li PowerShell skript spustit, nejdřív spusťte
`Set-ExecutionPolicy -Scope Process RemoteSigned` (platí jen pro toto okno).
V Linuxu nebo na macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funguje to, když `python -m heat3d_cs2 --help` vypíše `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Balíček | Minimum | K čemu slouží | Licence |
|---|---|---|---|
| `demoparser2` | 0.42 | čtení souborů `.dem` (hráči v každém taktu, herní události) | MIT |
| `pyarrow` | 15 | zápis tabulky Parquet | Apache-2.0 |
| `pandas` | 2.0 | tabulky mezi kroky | BSD-3-Clause |
| `numpy` | 1.24 | výpočty nad nimi | BSD-3-Clause |
| `pytest` | 8.0 | jen testy | MIT |

Příkazy `demos` a `scoreboard` nepotřebují nic dalšího.

## Pro export mapy: Counter-Strike 2 a příkazořádková verze Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` čte mapu z hry, kterou máte nainstalovanou, a
dekóduje ji pomocí **příkazořádkové verze Source2Vieweru**, samostatného
programu z projektu
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(licence MIT). Není přibalený a nedá se nainstalovat přes pip.

1. Stáhněte si verzi **CLI** pro svůj systém z
   [vydání ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   a rozbalte ji kamkoli.
2. Zpřístupněte ji některým ze tří způsobů. Zkouší se v tomto pořadí:
   1. `--source2viewer <cesta ke spustitelnému souboru>` na příkazovém řádku;
   2. proměnná prostředí `HEAT3D_SOURCE2VIEWER` nastavená na cestu ke
      spustitelnému souboru;
   3. spustitelný soubor pojmenovaný `Source2Viewer-CLI` nebo `Source2Viewer-CLI.exe`
      na `PATH`.

   Kandidát se použije, jen když cesta existuje. Když se nenajde žádný, příkaz
   se zastaví s hláškou `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Nastavení proměnné, například:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Kde se hledá CS2 {#where-cs2-is-looked-for}

Mapa je archiv `.vpk` ve složce hry:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Knihovny Steamu se hledají z těchto kořenů a z každé `"path"` uvedené v souboru
`config\libraryfolders.vdf` u každého kořene:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Je-li Steam jinde, předejte samotnou složku CS2 pomocí `--game` (složka, která
obsahuje `game\csgo`), nebo předejte cestu k `.vpk` místo názvu mapy. Viz
[Export mapy](map-export.md).

## Kontrola instalace {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testy běží na syntetickém demu sestaveném v kódu a nepotřebují dema, hru ani
Source2Viewer (viz [Vývoj](development.md)).

Při každém spuštění `python -m heat3d_cs2` se nejdřív zkontroluje, zda není
vydáno novější vydání, nejvýš jednou za šest hodin; `HEAT3D_NO_UPDATE=1` to
vypne (viz [Aktualizace](updates.md)).
