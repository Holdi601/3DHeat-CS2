---
title: Vývoj
nav_order: 15
lang: "cs"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Vývoj {#development}

## Rozložení {#layout}

| Cesta | Co je |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: nejdřív kontrola vydání, pak příkazový řádek |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | příkazy a volby; seskupování souborů dema do zápasů; fond pracovních procesů |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | jeden soubor dema přes demoparser2 do `RawPart` - [Čtení dema](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | části, řetězy, hodiny, kola, týmy, řádky, zabití, poškození, oslepení - [Sestavení zápasu](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | souhrny kol, výsledková tabule, dokument zápasu, textová výsledková tabule - [Statistiky](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | tabulka Parquet s nápovědami `heat3d`, a JSON - [Teplotní tabulka](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | hledání CS2 a Source2Viewer, kolizní síť do rámce prohlížeče - [Export mapy](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | minimální čtečka a zapisovač binárního glTF (žádná závislost kromě numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | kontrola vydání a aktualizátor - [Aktualizace](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testy a syntetické dema |
| `VERSION` | verze, jeden řádek |

Tok dat:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Použití z Pythonu {#using-it-from-python}

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

`Match.kills`, `Match.damage` a `Match.blinds` jsou tabulky pandas s více údaji,
než výstupy nesou - pozice útočníka a oběti a místa u každého zabití, `utility`
u každého zásahu - pro vlastní analýzy.

## Testy {#tests}

```bash
python -m pytest
```

`pytest.ini` spouští `tests/` potichu. Testy nepotřebují dema, hru ani
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
sestaví dema ručně, tak jak by je dal demoparser2 - dvě kola, dva hráči na
straně (`ace`, `ash` z týmu Alpha; `bob`, `ben` z Bravo), dost malé na to,
aby byla každá odpověď známá:

- Kolo 1, výhra T eliminací: ace zabije bob headshotem (otevření), ben zabije
  ace 1,9 s později (odplata: smrt boba je odplacena), ash zabije bena 3,1 s
  potom - sám proti jednomu, vyhraný clutch.
- Kolo 2, výhra T bombou: ash položí bombu na A, nikdo nezemře, bomba vybuchne.

`fixtures.halves` sestaví delší zápas prázdných kol, týmy na prvních stranách
nebo prohozené, s počtem prodloužení hry nebo bez něj, pro délku poločasu a
pistolová kola.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
na nich kontroluje: vítěze, důvod, skóre a strany každého kola; hodiny začínající
u zápasu; ekonomiku a položení (jeho čas do kola, jeho místo, výbuch bomby);
že místo položení je vždy písmeno nebo prázdné, nikdy číslo entity; kolo
rozhodnuté remízou bez vítěze; pistolová kola od místa, kde se strany
prohodí, bez prodloužení, a jen kolo 1 bez prohození; týmy bez názvů klanů
(`Started T` / `Started CT`); otevření, odplaty a příznaky; sebevraždu, která
není týmovým zabitím, a otevření předané prvnímu zabití nepřítele; `noscope`
a `attackerBlind` v tabulce i v dokumentu zápasu; poškození jako ztracené
zdraví (60, pak 40 z 137 na 40 zdraví); čísla výsledkové tabule a KAST;
clutche; textovou výsledkovou tabuli; události tabulky a kde jsou (detonace
bez vlastního místa, místo hodícího v `throwerPlace`; výbuch náleží týmu,
který bombu položil); že pozice jsou živé, označené a mají jednotkové vektory
pohledu; že zapsaný soubor nese své nápovědy; že se části seřadí bez ohledu
na jejich názvy; restartovaný herní čas serveru, který přesto navazuje; a
zdvojené řádky obnoveného kola vyřešené na ten, který vede dál.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
kontroluje, že dema ve složkách se najdou bez ohledu na velikost písmen u `.dem`
a že se zápas počítá jako zapsaný jen s tabulkou i dokumentem zápasu.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
kontroluje převody rámce (metry Source2Viewer na palce hry a dál do rámce
prohlížeče, rotace s determinantem 1), že clipy a obloha se vynechají bez
ohledu na velikost písmen a na pojmenování ploch, rozdělení na zem a
konstrukci podle normály a že se `.glb` zapíše a zase přečte.

### Kontrola podlahy na skutečné mapě {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Když jsou obě proměnné nastavené, poběží také `test_players_stand_on_the_exported_floor`:
převede dema, exportuje jeho mapu z nainstalované hry a zkontroluje, že aspoň
98 % z 300 náhodných vzorků pozic má pod sebou zem, s mediánem výšky nad ní
menším než 5 jednotek ([Export mapy](map-export.md#the-check-that-the-frame-is-right)).

## Konvence kódu {#conventions-of-the-code}

- Časy uvnitř `match.py` jsou sekundy zápasu, kromě `time` položení, což jsou
  sekundy do kola, jak je zapisuje dokument zápasu; takty se stanou sekundami
  jen přes `_Part.at`.
- Strany jsou řetězce `T` / `CT` všude mimo surová data parseru (`team_num`
  2 / 3).
- Nový sloupec tabulky jde do `ROW_COLUMNS` (a do `NUMERIC`, je-li číselný)
  v `match.py`; `output.table` volí jeho typ Parquet podle množin `INT16`,
  `INT32`, `FLOAT64` a příznaků 0/1, jinak float32.
- Změna toho, co má prohlížeč s sloupcem dělat, znamená změnu `HINTS` v
  `output.py`.

## Licence {#licence}

MIT. Balíčky třetích stran:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Dema a mapy nejsou nikdy součástí repozitáře; jeho `.gitignore` je podle
typu vynechává: `*.dem`, `*.parquet`, `*.match.json`, `*.glb` a podobné.
