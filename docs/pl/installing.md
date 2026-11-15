---
title: Instalacja
nav_order: 3
lang: "pl"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalacja {#installing}

Nie znasz wiersza poleceń? Najpierw przeczytaj [Zanim zaczniesz](before-you-start.md).

3DHeat CS2 to pakiet Pythona uruchamiany ze swojego własnego folderu. Nie ma nic do budowania ani instalatora; potrzebny jest Python, cztery pakiety (plus pytest do testów) i - tylko do eksportu mapy - zainstalowany Counter-Strike 2 oraz wersja Source2Viewer do wiersza poleceń.

## Pobranie kodu {#getting-the-code}

Pobierz archiwum wydania ze
[strony wydań](https://github.com/Holdi601/3DHeat-CS2/releases) i rozpakuj je
albo, jeśli masz Git, sklonuj repozytorium:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Obie wersje mogą się same aktualizować (zob. [Aktualizacje](updates.md)). Zainstalowana wersja to jedna linia w pliku `VERSION`.

Uruchamiaj każde polecenie z tego folderu: `python -m heat3d_cs2` znajduje pakiet, bo jest on w bieżącym folderze. Pakiet nie jest instalowany w `site-packages`.

## Python i pakiety {#python-and-the-packages}

Python 3.10 lub nowszy. Środowisko wirtualne trzyma pakiety osobno od reszty. W Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Jeśli PowerShell odmawia uruchomienia skryptu, najpierw wykonaj
`Set-ExecutionPolicy -Scope Process RemoteSigned` (działa to tylko w tym oknie). W Linux albo macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Instalacja działa, gdy `python -m heat3d_cs2 --help` wypisuje `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pakiet | Minimum | Do czego | Licencja |
|---|---|---|---|
| `demoparser2` | 0.42 | czytanie plików `.dem` (gracze na tick, zdarzenia gry) | MIT |
| `pyarrow` | 15 | zapis tabeli Parquet | Apache-2.0 |
| `pandas` | 2.0 | tabele pośrednie | BSD-3-Clause |
| `numpy` | 1.24 | obliczenia na nich | BSD-3-Clause |
| `pytest` | 8.0 | tylko testy | MIT |

Polecenia `demos` i `scoreboard` nie potrzebują niczego więcej.

## Do eksportu mapy: Counter-Strike 2 i wiersz poleceń Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` czyta mapę z zainstalowanej gry i dekoduje ją **wierszem poleceń Source2Viewer**, osobnym programem z projektu
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(licencja MIT). Nie jest dołączony i nie da się go zainstalować przez pip.

1. Pobierz wersję **CLI** dla swojego systemu z
   [wydań ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   i rozpakuj ją w dowolnym miejscu.
2. Spraw, by była widoczna, na jeden z trzech sposobów. Są sprawdzane w tej kolejności:
   1. `--source2viewer <ścieżka do pliku wykonywalnego>` w linii poleceń;
   2. zmienna środowiskowa `HEAT3D_SOURCE2VIEWER` ustawiona na ścieżkę pliku wykonywalnego;
   3. plik wykonywalny o nazwie `Source2Viewer-CLI` albo `Source2Viewer-CLI.exe` w `PATH`.

   Kandydat jest użyty tylko wtedy, gdy ścieżka istnieje. Jeśli żaden nie zostanie znaleziony, polecenie kończy się komunikatem `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Ustawienie zmiennej, na przykład:

```bash
# Windows (PowerShell), na bieżącą sesję
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Gdzie szukana jest CS2 {#where-cs2-is-looked-for}

Mapa to archiwum `.vpk` w folderze gry:
`<biblioteka Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<mapa>.vpk`.
Biblioteki Steam są szukane w tych katalogach głównych oraz w każdej `"path"` wymienionej w `config\libraryfolders.vdf` każdego z nich:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Gdy Steam jest gdzie indziej, podaj sam folder CS2 przez `--game` (folder zawierający `game\csgo`) albo podaj ścieżkę do pliku `.vpk` zamiast nazwy mapy. Zobacz [Eksport mapy](map-export.md).

## Sprawdzenie instalacji {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testy działają na syntetycznym demie zbudowanym w kodzie i nie potrzebują dema, gry ani Source2Viewer (zob. [Rozwój](development.md)).

Każde uruchomienie `python -m heat3d_cs2` najpierw sprawdza, nie częściej niż co sześć godzin, czy nie ma nowszego wydania; ustaw `HEAT3D_NO_UPDATE=1`, by to wyłączyć (zob. [Aktualizacje](updates.md)).
