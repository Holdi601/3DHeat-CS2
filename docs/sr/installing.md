---
title: "Инсталација"
nav_order: 3
lang: "sr"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Инсталација {#installing}

Први пут у командној линији? Прво прочитајте [Пре почетка](before-you-start.md).

3DHeat CS2 је Python пакет који се покреће из свог фолдера. Ништа се не прави и нема инсталатера; треба вам Python, четири пакета (плус pytest за тестове) и - само за извоз мапе - Counter-Strike 2 инсталиран и командна верзија Source2Viewer-а.

## Преузимање кода {#getting-the-code}

Преузмите архиву издања са [странице издања](https://github.com/Holdi601/3DHeat-CS2/releases) и распакујте је, или, ако имате Git, клонирајте репозиторијум:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Обе врсте копије могу саме да се ажурирају (видите [Ажурирања](updates.md)). Инсталисана верзија је онај један ред у фајлу `VERSION`.

Покрећите сваку команду из тог фолдера: `python -m heat3d_cs2` налази пакет јер је у текућем фолдеру. Пакет се не инсталира у `site-packages`.

## Python и пакети {#python-and-the-packages}

Python 3.10 или новији. Виртуелно окружење држи пакете одвојеним од свега осталог. На Windows-у (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ако PowerShell одбије да покрене скрипту, прво покрените `Set-ExecutionPolicy -Scope Process RemoteSigned` (важи само за тај прозор). На Linux-у или macOS-у:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ради кад `python -m heat3d_cs2 --help` испише `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Пакет | Најмање | За шта служи | Лиценца |
|---|---|---|---|
| `demoparser2` | 0.42 | читање `.dem` фајлова (играчи по такту, догађаји игре) | MIT |
| `pyarrow` | 15 | писање Parquet табеле | Apache-2.0 |
| `pandas` | 2.0 | табеле у међукорацима | BSD-3-Clause |
| `numpy` | 1.24 | рачунање над њима | BSD-3-Clause |
| `pytest` | 8.0 | само за тестове | MIT |

Команде `demos` и `scoreboard` не треба ништа друго.

## За извоз мапе: Counter-Strike 2 и CLI Source2Viewer-а {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` чита мапу из игре коју сте инсталирали, и декодира је **командном линијом Source2Viewer-а**, посебним програмом из пројекта [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (MIT лиценца). Није укључен и не може се инсталирати преко pip-а.

1. Преузмите **CLI** верзију за свој систем са [ValveResourceFormat издања](https://github.com/ValveResourceFormat/ValveResourceFormat/releases) и распакујте је било где.
2. Учините је нађеном, на један од три начина. Пробају се овим редом:
   1. `--source2viewer <путања до извршне датотеке>` у командној линији;
   2. променљива окружења `HEAT3D_SOURCE2VIEWER` са путањом до извршне датотеке;
   3. извршна датотека која се зове `Source2Viewer-CLI` или `Source2Viewer-CLI.exe` на `PATH`-у.

   Кандидат се користи само ако путања постоји. Ако се ниједан не нађе, команда се зауставља с порукама `Source2Viewer-CLI not found: download the command line build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Постављање променљиве, на пример:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Где се тражи CS2 {#where-cs2-is-looked-for}

Мапа је `.vpk` архива под фолдером игре: `<Steam библиотека>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`. Steam библиотеке се налазе из ових корена, и из сваке `"path"` ставке у `config\libraryfolders.vdf` сваког корена:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Кад је Steam на другом месту, наведите сам CS2 фолдер помоћу `--game` (фолдер који садржи `game\csgo`), или путању до `.vpk`-а уместо имена мапе. Видите [Извоз мапе](map-export.md).

## Провера инсталације {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Тестови раде на синтетичком демоу направљеном у коду и не требају демо, игру нити Source2Viewer (видите [Развој](development.md)).

Свако покретање `python -m heat3d_cs2` прво проверава, највише на сваких шест сати, има ли новијег издања; поставите `HEAT3D_NO_UPDATE=1` да то искључите (видите [Ажурирања](updates.md)).
