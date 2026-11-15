---
title: "Инсталирање"
nav_order: 3
lang: "mk"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Инсталирање {#installing}

Нови сте со командната линија? Прво прочитајте [Пред да започнете](before-you-start.md).

3DHeat CS2 е пакет на Python што се извршува од својата папка. Нема што да се
гради и нема инсталатор; потребни се Python, четири пакети (плус pytest за
тестовите) и - само за извозот на мапа - инсталиран Counter-Strike 2 и
верзијата на Source2Viewer за командна линија.

## Добивање на кодот {#getting-the-code}

Преземете архива на издание од
[страницата со изданија](https://github.com/Holdi601/3DHeat-CS2/releases) и
распакувајте ја, или, ако имате Git, клонирајте го складиштето:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Двата вида копија можат сами да се ажурираат (видете [Ажурирања](updates.md)).
Инсталираната верзија е единствената линија во датотеката `VERSION`.

Извршувајте ја секоја команда од таа папка: `python -m heat3d_cs2` го наоѓа
пакетот затоа што е во тековната папка. Пакетот не се инсталира во
`site-packages`.

## Python и пакетите {#python-and-the-packages}

Python 3.10 или понов. Виртуелна околина ги држи пакетите одвоени од сè друго.
На Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ако PowerShell одбие да ја изврши скриптата, прво извршете
`Set-ExecutionPolicy -Scope Process RemoteSigned` (важи само за тој прозорец).
На Linux или macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Работи кога `python -m heat3d_cs2 --help` печати `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Пакет | Минимум | Се користи за | Лиценца |
|---|---|---|---|
| `demoparser2` | 0.42 | читање `.dem` датотеки (играчи по такт, настани на играта) | MIT |
| `pyarrow` | 15 | пишување на Parquet табелата | Apache-2.0 |
| `pandas` | 2.0 | табелите помеѓу | BSD-3-Clause |
| `numpy` | 1.24 | пресметките врз нив | BSD-3-Clause |
| `pytest` | 8.0 | само за тестовите | MIT |

Командите `demos` и `scoreboard` не бараат ништо друго.

## За извозот на мапа: Counter-Strike 2 и CLI на Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` ја чита мапата од играта што ја имате инсталирано и
ја декодира со **командната линија на Source2Viewer**, посебна програма од
проектот [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(лиценца MIT). Не е вградена и не може да се инсталира со pip.

1. Преземете ја **CLI** верзијата за вашиот систем од
   [изданијата на ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   и распакувајте ја каде било.
2. Направете ја пронаоѓлива, на еден од три начини. Се обидуваат по овој редослед:
   1. `--source2viewer <патека до извршната датотека>` на командната линија;
   2. променливата на околината `HEAT3D_SOURCE2VIEWER` поставена на патеката на извршната датотека;
   3. извршна датотека со име `Source2Viewer-CLI` или `Source2Viewer-CLI.exe` на `PATH`.

   Кандидатот се користи само ако патеката постои. Ако не се најде ниеден,
   командата запира со `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Поставување на променливата, на пример:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Каде се бара CS2 {#where-cs2-is-looked-for}

Мапата е архива `.vpk` под папката на играта:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Библиотеките на Steam се наоѓаат од овие корени, и од секој `"path"` наведен
во `config\libraryfolders.vdf` на секој корен:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Кога Steam е на друго место, пренесете ја самата папка на CS2 со `--game`
(папката што содржи `game\csgo`), или пренесете ја патеката до `.vpk` наместо
името на мапата. Видете [Извоз на мапа](map-export.md).

## Проверка на инсталацијата {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Тестовите се извршуваат на синтетичко демо изградено во код и не бараат демо,
игра ниту Source2Viewer (видете [Развој](development.md)).

Секое стартување на `python -m heat3d_cs2` најпрво проверува, најмногу на
секои шест часа, дали има ново издание; поставете `HEAT3D_NO_UPDATE=1` за да
го исклучите тоа (видете [Ажурирања](updates.md)).
