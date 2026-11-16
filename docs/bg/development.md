---
title: "Разработка"
nav_order: 15
lang: "bg"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Разработка {#development}

## Структура {#layout}

| Път | Какво е |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: проверката за нова версия, после командният ред |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | командите и опциите; групирането на файловете с демо в мачове; групата работници |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | един файл с демо през demoparser2 в `RawPart` - [Четене на демо](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | части, вериги, часовникът, рундовете, отборите, редовете, убийствата, щетите, заслепяванията - [Изграждане на мач](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | резюмета на рундовете, таблото, документът на мача, текстовото табло - [Статистика](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet таблицата с нейните подсказки `heat3d`, и JSON - [Топлинната таблица](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | намиране на CS2 и Source2Viewer, колизионната мрежа в координатната система на визуализатора - [Експорт на карта](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | минимален четец и писач на glTF binary (без зависимост освен numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | проверката за нова версия и актуализаторът - [Актуализации](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | тестовете и синтетичното демо |
| `VERSION` | версията, един ред |

Потокът на данните:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Използване от Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # the heatmap table as a pandas DataFrame
    kills = match.kills        # one row per death, with every flag
    doc = summary(match)       # the .match.json document as a dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` и `Match.blinds` са DataFrame на pandas с повече от това, което носят изходите - позициите и местата на атакуващия и жертвата при всяко убийство, `utility` за всяко попадение - за ваши собствени анализи.

## Тестове {#tests}

```bash
python -m pytest
```

`pytest.ini` пуска `tests/` тихо. Тестовете не се нуждаят от демо, от играта или от Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) сглобява демо на ръка, така както би го дал demoparser2 - два рунда, по двама играчи на страна (`ace`, `ash` от отбор Alpha; `bob`, `ben` от Bravo), достатъчно малко, за да е известен всеки отговор:

- Рунд 1, победа на Т с елиминиране: ace убива bob с попадение в главата (първото убийство), ben убива ace 1.9 s по-късно (размяна: смъртта на bob е разменена), ash убива ben 3.1 s след това - сам срещу един, спечелен clutch.
- Рунд 2, победа на Т с бомбата: ash поставя на A, никой не умира, бомбата избухва.

`fixtures.halves` сглобява по-дълъг мач от празни рундове, отборите - на първите си страни или разменени, с брой овертайми на играта или без, за дължината на полувремето и пистолните рундове.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) проверява върху него: победителя, причината, резултата и страните на всеки рунд; часовника, който започва с мача; икономиката и поставянето (времето му в рунда, мястото му, избухването на бомбата); site на поставяне винаги буква или празно, никога номер на същност; равенство, решено без победител; пистолните рундове от това, къде страните си сменят местата, овертаймът изключен, и само рунд 1 без смяна; отбори без имена на кланове (`Started T` / `Started CT`); първи убийства, размени и флагове; самоубийство, което не е teamkill, и първото убийство, прехвърлено на първия враг; `noscope` и `attackerBlind` в таблицата и в документа на мача; щети като загубено здраве (60, после 40 от 137 при 40 здраве); числата на таблото и KAST; clutch-ове; текстовото табло; събитията на таблицата и къде са (взривяване без свое място, мястото на хвърлящия в `throwerPlace`; експлозията - на отбора, който е поставил); че позициите са живи, етикетирани и с единични вектори на погледа; че записаният файл носи своите подсказки; че частите се подреждат, каквито и да са имената им; възстановен часовник на рестартиран сървър, който продължава напред; и дублираните редове на възстановен рунд, решени в полза на този, който води напред.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) проверява, че демата в папки се намират, без значение от регистъра на `.dem`, и че мач се смята за записан само с таблицата и документа си на мача и двете.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) проверява преобразуванията на кадрите (метрите на Source2Viewer към инчовете на играта, и оттам към координатната система на визуализатора, въртене с детерминанта 1), че clip и sky се пропускат, без значение от регистъра, и имената на повърхностите, разделянето на терен и структура по нормала и един `.glb`, записан и прочетен обратно.

### Проверка на пода върху реална карта {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Когато и двете променливи са зададени, се пуска и `test_players_stand_on_the_exported_floor`: превръща демото, експортира картата от инсталираната игра и проверява дали поне 98 % от 300 случайни проби на позиция имат терен под себе си, с медианна височина над него под 5 единици ([Експорт на карта](map-export.md#проверката-че-кадърът-е-верен)).

## Правила в кода {#conventions-of-the-code}

- Времената в `match.py` са секунди на мача, освен `time` на поставянето - секунди в рунда, така както ги записва документът на мача; тиковете стават секунди само през `_Part.at`.
- Страните са низове `T` / `CT` навсякъде извън суровите данни на парсера (`team_num` 2 / 3).
- Нова колона в таблицата отива в `ROW_COLUMNS` (и в `NUMERIC`, ако е числова) в `match.py`; `output.table` избира типа ѝ в Parquet от множествата `INT16`, `INT32`, `FLOAT64` и флаговете 0/1, а останалите са float32.
- Промяната на това, какво да прави визуализаторът с колона, означава промяна на `HINTS` в `output.py`.

## Лиценз {#licence}

MIT. Сторонни пакети: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Демата и картите никога не са част от хранилището; неговият `.gitignore` пази `*.dem`, `*.parquet`, `*.match.json`, `*.glb` и подобни по тип извън него.
