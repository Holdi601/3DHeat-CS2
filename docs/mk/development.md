---
title: "Развој"
nav_order: 15
lang: "mk"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Развој {#development}

## Распоред {#layout}

| Патека | Што е |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: проверката за изданија, потоа командната линија |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | командите и опциите; групирање на датотеки со демо во натпревари; базенот на работници |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | една датотека со демо низ demoparser2 во `RawPart` - [Читање демо](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | делови, синџири, часовникот, рунди, тимови, редови, убиства, штета, заслепувања - [Составување на натпревар](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | резимеа на рунди, табелата со резултати, документот на натпреварот, текстуалната табела со резултати - [Статистика](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet табелата со нејзините `heat3d` навестувања, и JSON - [Табелата за топлинска мапа](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | наоѓање на CS2 и Source2Viewer, колизионата мрежа во координатниот систем на прегледувачот - [Извоз на мапа](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | минимален читач и писател на glTF бинарен формат (без зависност освен numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | проверката за изданија и ажурирачот - [Ажурирања](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | тестовите и синтетичкото демо |
| `VERSION` | верзијата, една линија |

Текот на податоците:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Користење од Python {#using-it-from-python}

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

`Match.kills`, `Match.damage` и `Match.blinds` се pandas DataFrame-и со повеќе
отколку што носат излезите - позиции и места на напаѓачот и жртвата по
убиство, `utility` по удар - за ваши сопствени анализи.

## Тестови {#tests}

```bash
python -m pytest
```

`pytest.ini` ги пушта `tests/` тивко. Тестовите не бараат демо, игра ниту
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
рачно гради демо, онака како што би го дал demoparser2 - две рунди, по два
играчи на страна (`ace`, `ash` од тимот Alpha; `bob`, `ben` од Bravo),
доволно мало за да е секој одговор познат:

- Рунда 1, победа на T со елиминација: ace го убива bob со хедшот (отворањето),
  ben го убива ace 1,9 s подоцна (размена: смртта на bob е разменета), ash го
  убива ben 3,1 s после тоа - сам против еден, добиен клач.
- Рунда 2, победа на T со бомбата: ash поставува на A, никој не умира, бомбата
  експлодира.

`fixtures.halves` гради подолг натпревар од празни рунди, со тимовите на нивните
први страни или заменети, со бројачот на продолженија на играта или без него,
за должината на полувремето и пиштолските рунди.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
проверува на него: победникот, причината, резултатот и страните на секоја
рунда; часовникот што почнува со натпреварот; економијата и поставувањето (неговото
време во рундата, местото, експлозијата на бомбата); страната на поставувањето
секогаш буква или празна, никогаш број на ентитет; нерешено одлучено без
победник; пиштолските рунди од таму каде што страните се менуваат,
продолжението изоставено, и само рундата 1 без менување; тимови без имиња на
кланови (`Started T` / `Started CT`); отворања, размени и знамиња;
самоубиство што не е убиство на свој, и отворањето пренесено на првото убиство
на непријател; `noscope` и `attackerBlind` во табелата и документот на натпреварот;
штета како изгубено здравје (60, потоа 40 од 137 на 40 здравје); броевите на
табелата со резултати и KAST; клачеви; текстуалната табела со резултати;
настаните на табелата и каде се (детонација без свое место, местото на
фрлачот во `throwerPlace`; експлозијата на тимот што поставува); дека
позициите се живи, означени и имаат единечни вектори на гледање; дека
запишаната датотека ги носи своите навестувања; делови подредени без оглед на
нивните имиња; рестартиран часовник на серверот што сепак следува; и
дуплирани редови на вратена рунда решени на оној што води натаму.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
проверува дека демоата во папки се наоѓаат без оглед на големината на буквите
на `.dem`, и дека натпреварот се смета за запишан само со неговата табела и
неговиот документ за натпревар.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
ги проверува претворањата на координатни системи (метрите на Source2Viewer во
инчите на играта, и натаму во координатниот систем на прегледувачот, ротација
со детерминанта 1), дека клиповите и небото се изоставени без оглед на
големината на буквите и именуваните површини, поделбата земја/структура по
нормала, и `.glb` запишан и прочитан назад.

### Проверката на подот на вистинска мапа {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Со поставени двете променливи се извршува и `test_players_stand_on_the_exported_floor`:
го претвора демото, ја извезува неговата мапа од инсталираната игра, и
проверува дека најмалку 98 % од 300 случајни примероци на позиција имаат
земја под себе, со медијана на висината над неа под 5 единици
([Извоз на мапа](map-export.md#the-check-that-the-frame-is-right)).

## Конвенции на кодот {#conventions-of-the-code}

- Времињата внатре во `match.py` се секунди на натпреварот, освен `time` на
  поставувањето, секунди во неговата рунда како што го пишува документот на
  натпреварот; тактовите стануваат секунди само преку `_Part.at`.
- Страните се низи `T` / `CT` насекаде надвор од суровите податоци на
  парсерот (`team_num` 2 / 3).
- Нова колона на табелата оди во `ROW_COLUMNS` (и `NUMERIC` ако е нумеричка)
  во `match.py`; `output.table` го избира својот Parquet тип од множествата
  `INT16`, `INT32`, `FLOAT64` и знамињата 0/1, инаку float32.
- Менувањето на тоа што прегледувачот треба да прави со колона значи менување
  на `HINTS` во `output.py`.

## Лиценца {#licence}

MIT. Пакетите од трети страни и она што го обврзуваат игрите:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Демоата и мапите никогаш не се дел од складиштето; неговиот `.gitignore` ги
држи `*.dem`, `*.parquet`, `*.match.json`, `*.glb` и слично надвор по тип.
