---
title: "Инсталиране"
nav_order: 3
lang: "bg"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Инсталиране {#installing}

Ново в командния ред? Първо прочетете [Преди да започнете](before-you-start.md).

3DHeat CS2 е Python пакет, който се пуска от собствената си папка. Няма нищо за компилиране и няма инсталатор; нужни са Python, четири пакета (плюс pytest за тестовете) и - само за експорта на карта - Counter-Strike 2, инсталиран, и командният вариант на Source2Viewer.

## Вземане на кода {#getting-the-code}

Изтеглете архив с версия от
[страницата с версиите](https://github.com/Holdi601/3DHeat-CS2/releases) и го разопаковайте,
или, ако имате Git, клонирайте хранилището:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

И двата вида копия могат да се обновяват сами (вижте [Актуализации](updates.md)). Инсталираната версия е редът в файла `VERSION`.

Пускайте всяка команда от тази папка: `python -m heat3d_cs2` намира пакета, защото той е в текущата папка. Пакетът не се инсталира в `site-packages`.

## Python и пакетите {#python-and-the-packages}

Python 3.10 или по-нов. Виртуална среда пази пакетите отделно от всичко останало. На Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ако PowerShell откаже да пусне скрипта, първо пуснете
`Set-ExecutionPolicy -Scope Process RemoteSigned` (важи само за този прозорец). На Linux или macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Всичко е наред, когато `python -m heat3d_cs2 --help` отпечата `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Пакет | Минимум | За какво се ползва | Лиценз |
|---|---|---|---|
| `demoparser2` | 0.42 | четене на файлове `.dem` (играчи по тик, събития в играта) | MIT |
| `pyarrow` | 15 | записване на Parquet таблицата | Apache-2.0 |
| `pandas` | 2.0 | междинните таблици | BSD-3-Clause |
| `numpy` | 1.24 | изчисления върху тях | BSD-3-Clause |
| `pytest` | 8.0 | само за тестовете | MIT |

Командите `demos` и `scoreboard` нямат нужда от нищо друго.

## За експорта на карта: Counter-Strike 2 и командният Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` чете картата от играта, която имате инсталирана, и я декодира с **командния ред на Source2Viewer** - отделна програма от проекта
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (лиценз MIT). Тя не е включена в пакета и не може да се инсталира с pip.

1. Изтеглете **CLI** версията за вашата система от
   [версиите на ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   и я разопаковайте където и да е.
2. Направете я откриваема, по един от три начина. Пробват се в този ред:
   1. `--source2viewer <път до изпълнимия файл>` в командния ред;
   2. променливата на средата `HEAT3D_SOURCE2VIEWER`, зададена на пътя до изпълнимия файл;
   3. изпълним файл с име `Source2Viewer-CLI` или `Source2Viewer-CLI.exe` в `PATH`.

   Кандидат се използва само ако пътят съществува. Ако не се намери нито един, командата спира с `Source2Viewer-CLI not found: download the command line build for your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Задаване на променливата, например:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Къде се търси CS2 {#where-cs2-is-looked-for}

Картата е архив `.vpk` в папката на играта:
`<Steam библиотека>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Библиотеките на Steam се намират от тези корени и от всеки `"path"`, изброен в `config\libraryfolders.vdf` на всеки корен:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Когато Steam е на друго място, подайте самата папка на CS2 с `--game` (папката, която съдържа `game\csgo`), или подайте пътя до `.vpk` вместо името на картата. Вижте [Експорт на карта](map-export.md).

## Проверка на инсталацията {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Тестовете работят на синтетично демо, сглобено в кода, и не се нуждаят от демо, от играта или от Source2Viewer (вижте [Разработка](development.md)).

При всеки старт на `python -m heat3d_cs2` се проверява, най-много на всеки шест часа, дали има по-нова версия; задайте `HEAT3D_NO_UPDATE=1`, за да изключите това (вижте [Актуализации](updates.md)).
