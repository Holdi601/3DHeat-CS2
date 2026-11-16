---
title: Vývoj
nav_order: 15
lang: "sk"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Vývoj {#development}

## Rozloženie {#layout}

| Cesta | Čo je |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: najprv kontrola vydania, potom príkazový riadok |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | príkazy a možnosti; zoskupovanie súborov dema do zápasov; zbierka pracovných procesov |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | jeden súbor dema cez demoparser2 do `RawPart` - [Čítanie dema](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | časti, reťazce, hodiny, kolá, tímy, riadky, zabitia, poškodenie, oslepenia - [Zostavenie zápasu](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | súhrny kôl, výsledková tabuľka, dokument zápasu, textová výsledková tabuľka - [Štatistika](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | tabuľka Parquet s nápovedami `heat3d` a JSON - [Tabuľka heatmapy](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | hľadanie CS2 a Source2Viewer, kolízna sieť do rámca prehliadača - [Export mapy](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | minimálny čítač a zapisovač binárneho glTF (bez závislosti okrem numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | kontrola vydania a aktualizátor - [Aktualizácie](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testy a syntetické demo |
| `VERSION` | verzia, jeden riadok |

Tok dát:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Používanie z Pythonu {#using-it-from-python}

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

`Match.kills`, `Match.damage` a `Match.blinds` sú pandas DataFrame s viac údajmi,
než nesú výstupy - pozície a miesta útočníka a obete pri každom zabití, zásah
po zásahu `utility` - na vlastné analýzy.

## Testy {#tests}

```bash
python -m pytest
```

`pytest.ini` spúšťa `tests/` potichu. Testy nepotrebujú demo, hru ani
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
zostaví demo ručne, tak ako by ho dal demoparser2 - dve kolá, dvaja hráči na
strane (`ace`, `ash` z tímu Alpha; `bob`, `ben` z Bravo), dostatočne malé, aby
bola každá odpoveď známa:

- Kolo 1, víťazstvo T likvidáciou: ace zabije bob headshotom (otvorenie),
  ben zabije ace o 1,9 s neskôr (odveta: smrť bob je odvetená), ash zabije ben
  3,1 s po tom - sám proti jednému, vyhratý clutch.
- Kolo 2, víťazstvo T bombou: ash položí bombu na A, nikto nezomrie, bomba
  vybuchne.

`fixtures.halves` zostaví dlhší zápas z prázdnych kôl, tímy na prvých stranách
alebo vymenené, s počtom predĺžení hry alebo bez neho, pre dĺžku polčasu a
pistolové kolá.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
overuje na ňom: víťaza, dôvod, skóre a strany každého kola; hodiny začínajúce
so zápasom; ekonomiku a položenie (jeho čas v kole, miesto, výbuch bomby);
miesto položenia vždy písmeno alebo prázdne, nikdy číslo entity; remízu
rozhodnutú bez víťaza; pistolové kolá od miesta, kde sa strany vymenia,
predĺženie vynechané, a len kolo 1 bez výmeny; tímy bez názvov klanov
(`Started T` / `Started CT`); otvorenia, odvety a príznaky; samovraždu, ktorá
nie je tímovým zabitím, a otvorenie prenesené na prvé zabitie nepriateľa;
`noscope` a `attackerBlind` v tabuľke a v dokumente zápasu; poškodenie ako
stratené zdravie (60, potom 40 zo 137 pri 40 zdravia); čísla výsledkovej
tabuľky a KAST; clutche; textovú výsledkovú tabuľku; udalosti tabuľky a ich
miesta (výbuch bez vlastného miesta, miesto hádzajúceho v `throwerPlace`;
výbuch patrí položiacemu tímu); že pozície sú živé, označené a majú jednotkové
vektory pohľadu; že zapísaný súbor nesie svoje nápovedy; že časti sa zoradia
bez ohľadu na názvy; že reštartované hodiny servera pokračujú; a že duplicitné
riadky obnoveného kola sa vyriešia na ten, ktorý vedie ďalej.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
overuje, že dema v priečinkoch sa nájdu bez ohľadu na veľkosť písmen v `.dem`
a že zápas sa počíta ako zapísaný, iba keď má tabuľku aj dokument zápasu.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
overuje prepočty rámca (metre Source2Viewer na palce hry a ďalej do rámca
prehliadača, rotácia s determinantom 1), že clip a obloha sa vynechajú bez
ohľadu na veľkosť písmen a označenie povrchov, rozdelenie na zem a konštrukciu
podľa normály, a že `.glb` sa zapíše a znovu prečíta.

### Kontrola podlahy na skutočnej mape {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Keď sú nastavené obe premenné, spustí sa aj `test_players_stand_on_the_exported_floor`:
prevedie demo, exportuje jeho mapu z nainštalovanej hry a overí, že aspoň 98 %
z 300 náhodných vzoriek pozícií má pod sebou zem, s mediánom výšky nad ňou
menším ako 5 jednotiek ([Export mapy](map-export.md#the-check-that-the-frame-is-right)).

## Konvencie kódu {#conventions-of-the-code}

- Časy vo vnútri `match.py` sú sekundy zápasu, okrem `time` položenia, ktoré je
  v sekundách v kole, ako ho zapisuje dokument zápasu; tiky sa stanú sekundami
  iba cez `_Part.at`.
- Strany sú všade mimo surových údajov parsera reťazce `T` / `CT` (`team_num`
  2 / 3).
- Nový stĺpec tabuľky ide do `ROW_COLUMNS` (a do `NUMERIC`, ak je číselný) v
  `match.py`; `output.table` vyberie jeho typ Parquet podľa množín `INT16`,
  `INT32`, `FLOAT64` a príznakov 0/1, inak float32.
- Zmena toho, čo má prehliadač robiť s nejakým stĺpcom, znamená zmenu `HINTS` v
  `output.py`.

## Licencia {#licence}

MIT. Balíky tretích strán:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Dema a mapy nikdy nie sú súčasťou repozitára; jeho `.gitignore` ich podľa typu
vynechá: `*.dem`, `*.parquet`, `*.match.json`, `*.glb` a podobné.
