---
title: "Telepítés"
nav_order: 3
lang: "hu"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Telepítés {#installing}

Még nem használt parancssort? Olvasd el először a [Mielőtt elkezded](before-you-start.md) oldalt.

A 3DHeat CS2 egy Python-csomag, amelyet a saját mappájából futtatunk. Nincs mit építeni, és nincs telepítő; kell hozzá
Python, négy csomag (plusz a pytest a tesztekhez), és - csak a pályaexporthoz - a telepített Counter-Strike 2 és a
Source2Viewer parancssori változata.

## A kód megszerzése {#getting-the-code}

Töltsd le a kiadási archívumot a
[kiadások oldaláról](https://github.com/Holdi601/3DHeat-CS2/releases), és csomagold ki, vagy ha van Gitod, klónozd a
tárolót:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Mindkét másolat tud magától frissülni (lásd: [Frissítések](updates.md)). A telepített verzió a `VERSION` fájl egy sora.

Minden parancsot abból a mappából futtass: a `python -m heat3d_cs2` azért találja meg a csomagot, mert az az aktuális
mappában van. A csomag nincs telepítve a `site-packages`-be.

## Python és a csomagok {#python-and-the-packages}

Python 3.10 vagy újabb. Egy virtuális környezet elválasztja a csomagokat mindentől, ami mással van. Windowson (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ha a PowerShell nem futtatja a szkriptet, előbb futtasd a
`Set-ExecutionPolicy -Scope Process RemoteSigned` parancsot (csak ebben az ablakban marad érvényben). Linuxon vagy
macOS-en:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Működik, ha a `python -m heat3d_cs2 --help` a `usage: heat3d_cs2 ...` sort írja ki.

`requirements.txt`:

| Csomag | Minimum | Mire használjuk | Licenc |
|---|---|---|---|
| `demoparser2` | 0.42 | a `.dem` fájlok olvasása (játékosok tickenként, játékesemények) | MIT |
| `pyarrow` | 15 | a Parquet-táblázat írása | Apache-2.0 |
| `pandas` | 2.0 | a közbenső táblázatok | BSD-3-Clause |
| `numpy` | 1.24 | számítások rajtuk | BSD-3-Clause |
| `pytest` | 8.0 | csak a tesztek | MIT |

A `demos` és a `scoreboard` parancsokhoz nincs szükség másra.

## A pályaexporthoz: Counter-Strike 2 és a Source2Viewer parancssori változata {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

A `python -m heat3d_cs2 map` a telepített játékból olvassa be a pályát, és a **Source2Viewer parancssori változatával**
dekódolja, amely a [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) projekttől
különálló program (MIT licenc). Nincs benne a csomagban, és pip-pel nem telepíthető.

1. Töltsd le a rendszerednek megfelelő **CLI** változatot a
   [ValveResourceFormat kiadásai](https://github.com/ValveResourceFormat/ValveResourceFormat/releases) közül, és
   csomagold ki bárhová.
2. Tedd megtalálhatóvá három módon. Ebben a sorrendben próbálkozik:
   1. `--source2viewer <a futtatható fájl útvonala>` a parancssorban;
   2. a `HEAT3D_SOURCE2VIEWER` környezeti változó, amely a futtatható fájl útvonalára mutat;
   3. a `PATH`-on lévő, `Source2Viewer-CLI` vagy `Source2Viewer-CLI.exe` nevű futtatható fájl.

   Csak akkor használunk egy jelöltet, ha az útvonala létezik. Ha egyet sem találunk, a parancs leáll ezzel:
   `Source2Viewer-CLI not found: download the command line build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

A változó beállítása, például:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Hol keressük a CS2-t {#where-cs2-is-looked-for}

A pálya a játék mappájában lévő `.vpk` archívum:
`<Steam-könyvtár>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
A Steam-könyvtárakat ezekből a gyökerekből keressük, és minden `"path"` bejegyzésből, amely az egyes gyökerek
`config\libraryfolders.vdf` fájljában szerepel:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Ha a Steam máshol van, add meg magát a CS2 mappát a `--game` kapcsolóval (az a mappa, amelyben a `game\csgo` van), vagy
add meg a `.vpk` útvonalát a pálya neve helyett. Lásd: [Pályaexport](map-export.md).

## A telepítés ellenőrzése {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

A tesztek egy kódban épített szintetikus demón futnak, és nincs szükségük demóra, játékra vagy Source2Viewerre (lásd:
[Fejlesztés](development.md)).

Minden `python -m heat3d_cs2` indításkor, legfeljebb hatoránként egyszer ellenőrzi, hogy megjelent-e újabb kiadás; a
`HEAT3D_NO_UPDATE=1` beállítással ez kikapcsolható (lásd: [Frissítések](updates.md)).
