---
title: "Развој"
nav_order: 15
lang: "sr"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Развој {#development}

## Распоред {#layout}

| Путања | Шта је |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: провера издања, па командна линија |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | команде и опције; груписање демо-датотека у мечеве; скуп радника |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | једна демо-датотека кроз demoparser2 у `RawPart` - [Читање демоа](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | делови, ланци, сат, рунде, тимови, редови, убиства, штета, блицеви - [Како се прави меч](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | резимеи рунди, табела резултата, документ меча, текстуална табела резултата - [Статистика](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet табела са својим `heat3d` наговештајима, и JSON - [Табела топлотне мапе](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | налажење CS2 и Source2Viewer, колизиона мрежа у оквир прегледача - [Извоз мапе](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | мали читач и писач glTF бинарног формата (без зависности осим numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | провера издања и ажурирање - [Ажурирања](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | тестови и синтетички демо |
| `VERSION` | верзија, један ред |

Ток података:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Коришћење из Python-а {#using-it-from-python}

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

`Match.kills`, `Match.damage` и `Match.blinds` су pandas DataFrame-ови са више од онога што излази носе - положаји и места нападача и жртве по убиству, штета по погоду у `utility` - за ваше сопствене анализе.

## Тестови {#tests}

```bash
python -m pytest
```

`pytest.ini` покреће `tests/` тихо. Тестовима не треба ни демо, ни игра, ни Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) прави демо руком, како би га дао demoparser2 - две рунде, по два играча на страни (`ace`, `ash` тима Alpha; `bob`, `ben` тима Bravo), довољно мали да је сваки одговор познат:

- Рунда 1, победа T елиминацијом: ace убија bob-а погодком у главу (отварање), ben убија ace-а 1,9 s касније (размена: bob-ова смрт је размењена), ash убија ben-а 3,1 s после тога - сам против једног, освојен клач.
- Рунда 2, победа T бомбом: ash поставља на A, нико не гине, бомба експлодира.

`fixtures.halves` прави дужи меч празних рунди, тимови на својим првим странама или замењени, са или без продужетка игре, ради дужине половине и пистол-рунди.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) проверава на њему: побједника, разлог, резултат и стране сваке рунде; да сат почиње од меча; економију и постављање (његово време у рунди, његово место, експлозију бомбе); да је сајт постављања увек слово или празно, никад број ентитета; нерешену рунду без победника; пистол-рунде од места замене страна, продужетак изостављен, и само рунда 1 без замене; тимове без клан-назива (`Started T` / `Started CT`); отварања, размене и ознаке; самоубиство које није тимско убиство, и отварање пренето на први непријатељски kill; `noscope` и `attackerBlind` у табели и документу меча; штету као изгубљено здравље (60, па 40 од 137 на 40 здравља); бројеве табеле резултата и KAST; клачеве; текстуалну табелу резултата; догађаје табеле и где су (експлозија бацача без свог места, бацачево у `throwerPlace`; експлозија на страни постављача); да су позиције живе, означене и да имају јединичне векторе погледа; да уписана датотека носи своје наговештаје; делове стављене у редослед без обзира на имена; поново покренут серверов сат који и даље тече; и дупле редове враћене рунде разрешене на онај који води даље.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) проверава да се демои у фолдерима налазе без обзира на величину слова у `.dem`, и да се меч рачуна као написан само кад има и своју табелу и свој документ меча.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) проверава претварања оквира (Source2Viewer-ових метара у игрине инче, па даље у оквир прегледача, ротација са детерминантом 1), да су клипови и небо изостављени без обзира на величину слова и на имена површина, поделу на под и конструкцију по нормали, и да се `.glb` напише и поново прочита.

### Провера пода на правој мапи {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Кад су обе променљиве постављене, покреће се и `test_players_stand_on_the_exported_floor`: претвара демо, извози његову мапу из инсталиране игре и проверава да је најмање 98 % од 300 случајних узорака положаја играча има под испод себе, са средњом висином изнад њега мањом од 5 јединица ([Извоз мапе](map-export.md#провера-да-је-оквир-исправан)).

## Конвенције кода {#conventions-of-the-code}

- Времена унутар `match.py` су секунде меча, осим `time` постављања, секунде у његовој рунди, како га документ меча пише; такови постају секунде тек преко `_Part.at`.
- Стране су стрингови `T` / `CT` свуда ван сирових података парсера (`team_num` 2 / 3).
- Нова колона табеле иде у `ROW_COLUMNS` (и `NUMERIC` ако је бројчана) у `match.py`; `output.table` бира њен Parquet тип из скупова `INT16`, `INT32`, `FLOAT64` и 0/1 ознака, а float32 у осталим случајевима.
- Ако желите да прегледач другачије ради са колоном, мења се `HINTS` у `output.py`.

## Лиценца {#licence}

MIT. Пакети трећих страна и шта игре захтевају: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md). Демои и мапе никад нису део репозиторијума; његов `.gitignore` по врсти држи `*.dem`, `*.parquet`, `*.match.json`, `*.glb` и сличне ван њега.
