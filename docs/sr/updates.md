---
title: "Ажурирања"
nav_order: 14
lang: "sr"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Ажурирања {#updates}

3DHeat CS2 се држи актуелним преко [GitHub издања](https://github.com/Holdi601/3DHeat-CS2/releases) овог репозиторијума. Код: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py), [`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Провера при покретању {#the-check-at-start-up}

Свако `python -m heat3d_cs2 ...` прво пита да ли је новије издање изашло, пре него што уопште прочита своје аргументе:

1. Инсталирана верзија је фајл `VERSION` у корену репозиторијума (`0` ако се не може прочитати).
2. Најновије издање се тражи од `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, с роком од **5 секунди**. Одговор се кешира **6 сати** у `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (на системима без `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), тако да се захтев шаље највише сваких шест сати. "Ништа није објављено" (HTTP 404) кешира се као и сваки други одговор. Ван мреже, ограничено бројем захтева, иза проксија - било која друга грешка - алат наставља с верзијом коју има, и ништа се не кешира.
3. Верзије се пореде као бројеви: `v1.2.3` и `1.2.3` су једнаке, све после `-` или `+` се занемарује, недостајући делови се рачунају као 0.

Кад је новије издање изашло, јавља то на току грешака:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- На терминалу (и улаз и ток грешака су терминали) пита. Enter, `y`, `yes`, `j` или `ja` ажурира; све остало наставља непромењено. После ажурирања **иста наредба се покреће поново**, на новом коду.
- Без терминала - заказано покретање, цев - само исписује где се ажурира и наставља: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` искључује проверу. Свака вредност осим празне, `0`, `false` или `no` значи укључено.

## Ажурирање на захтев {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Ово увек пита GitHub (кеш се не користи). Исписује `Up to date: <version>.`, `No release found (this is <version>); offline, or nothing published yet.`, или `<new> is out (this is <current>): <url>` па ажурира (осим уз `--check`). Излазни код `1` кад је ажурирање покушано а није успело, иначе `0`.

## Како се ажурирање примењује {#how-an-update-is-applied}

Зависи од тога како је копија инсталирана:

- **Git checkout** (има `.git` у корену и `git` на `PATH`-у): `git pull --ff-only`. Одбија се док праћени фајлови имају локалне измене ("this checkout has local changes; commit or stash them, then run `git pull`"): то је нечији рад, а ажурирање не одлучује шта се с њим дешава. Непраћени фајлови га не блокирају.
- **Преузета копија**: архива изворног кода издања (GitHub-ов zipball) се преузима и распакује у привремени фолдер - уноси који би пали ван њега се прескачу - а њен `VERSION` мора бити верзија коју издање тврди, иначе се ништа не мења ("the archive is version X, not Y"). Затим се њени фајлови копирају преко фолдера. Фајлови који нису део издања - ваши демои, излази, виртуелно окружење, било шта што сте направили - никад се не дирају. Python модули које издање више нема бришу се из сопствених пакета алата (фолдери `heat3d_*`), тако да застарели модул не може засенити своју замену.

Ако ажурирање не успе, порука се исписује и алат ради с верзијом коју има.
