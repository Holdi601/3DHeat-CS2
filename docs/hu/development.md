---
title: "Fejlesztés"
nav_order: 15
lang: "hu"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Fejlesztés {#development}

## Felépítés {#layout}

| Útvonal | Mi |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: előbb a kiadás-ellenőrzés, azután a parancssor |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | az igék és a kapcsolók; a demófájlok meccsekbe csoportosítása; a munkavégző-készlet |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | egy demófájl a demoparser2-n át `RawPart`-ba - [Demó beolvasása](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | részek, láncok, az óra, körök, csapatok, sorok, ölések, sebzés, vakítások - [Meccs felépítése](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | körösszegzések, az eredménytábla, a meccsdokumentum dokumentuma, a szöveges eredménytábla - [Statisztika](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | a Parquet-táblázat a `heat3d` tippjeivel, és a JSON - [A hőtérképes táblázat](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | a CS2 és a Source2Viewer megtalálása, az ütközési háló a megjelenítő koordinátarendszerébe - [Pályaexport](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | egy minimális glTF bináris olvasó és író (a numpy-n kívül nincs függősége) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | a kiadás-ellenőrzés és a frissítő - [Frissítések](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | a tesztek és a szintetikus demó |
| `VERSION` | a verzió, egy sorban |

Az adatok útja:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Használat Pythonból {#using-it-from-python}

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

A `Match.kills`, `Match.damage` és `Match.blinds` pandas DataFrame-ek, amelyekben több van, mint a kimenetekben: a
támadó és az áldozat pozíciója és helye ölésenként, találatonként a `utility` - saját elemzésekhez.

## Tesztek {#tests}

```bash
python -m pytest
```

A `pytest.ini` csendben futtatja a `tests/` mappát. A teszteknek nincs szükségük demóra, játékra vagy Source2Viewerre:
a [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) kézzel épít egy demót,
úgy, ahogy a demoparser2 adná - két kör, oldalanként két játékos (`ace`, `ash` az Alpha csapatból; `bob`, `ben` a
Bravóból) -, elég kicsi ahhoz, hogy minden válasz ismert legyen:

- 1. kör, T-győzelem eliminálással: ace fejlövéssel megöli bobot (a nyitó), ben 1,9 másodperccel később megöli acet
  (egy trade: bob halálát megbosszulták), ash ezután 3,1 másodperccel megöli bent - egyedül egy ellen, egy klucs
  megnyerve.
- 2. kör, T-győzelem a bombával: ash A-n lerakja a bombát, senki nem hal meg, a bomba felrobban.

A `fixtures.halves` hosszabb meccset épít üres körökből, a csapatok az első oldalukon vagy felcserélve, a játék
hosszabbítási számával vagy anélkül, a félidő hosszához és a pisztolykörökhöz.

A [`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) ezeket ellenőrzi rajta:
minden kör győztesét, okát, állását és oldalait; az órát, amely a meccsnél indul; a gazdaságot és a lerakást (a
körbeli ideje, a helye, a bomba felrobbanása); hogy a lerakás helyszíne mindig betű vagy üres, sosem egy entitásszám;
egy eldöntött döntetlent győztes nélkül; a pisztolyköröket ott, ahol az oldalak cserélnek, a hosszabbítást kihagyva, és
csak az 1. kört cserék nélkül; a klánnevek nélküli csapatokat (`Started T` / `Started CT`); a nyitókat, trade-eket és
jelzőket; az öngyilkosságot, amely nem csapattárs-ölés, és a nyitó átadását az első ellenséges gyilkosságra; a
`noscope` és `attackerBlind` értékeket a táblázatban és a meccsdokumentumban; a sebzést elvesztett életerőként (60, majd
40 egy 137-esből 40 életerőn); az eredménytábla számait és a KAST-ot; a klucsokat; a szöveges eredménytáblát; a
táblázat eseményeit és helyüket (egy robbanás hely nélkül, a dobó helye a `throwerPlace`-ben; a robbanás a lerakó
csapaté); hogy a pozíciók élők, címkézettek és egységnyi nézési vektorúak; hogy a kiírt fájl hordozza a tippjeit; hogy
a részek sorrendbe kerülnek, bármilyen nevük is van; hogy egy újraindított szerver órája is tovább fut; és hogy egy
visszaállított kör duplikált sorai arra a sorra oldódnak fel, amelyik továbbvezet.

A [`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) ellenőrzi, hogy a mappákban
lévő demókat megtalálja, akármilyen a `.dem` betűkészlete, és hogy egy meccs csak akkor számít megírtnak, ha megvan a
táblázata és a meccsdokumentuma is.

A [`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) a koordináta-
átalakításokat ellenőrzi (a Source2Viewer méterei játékegységekké, majd tovább a megjelenítő koordinátarendszerébe, egy
determinánsú 1-es forgatással), hogy a klipek és az égbolt - bármilyen nagybetűvel és név szerint - kimaradnak, a
talaj/szerkezet szétválasztását a normálvektor alapján, és egy `.glb` megírását és visszaolvasását.

### A padló-ellenőrzés valódi pályán {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Ha mindkét változó be van állítva, lefut a `test_players_stand_on_the_exported_floor` is: átalakítja a demót,
exportálja a pályát a telepített játékból, és ellenőrzi, hogy 300 véletlen pozíciómintából legalább 98%-nál van talaj
alattuk, a talajtól mért medián magasság pedig 5 egység alatt van ([Pályaexport](map-export.md#the-check-that-the-frame-is-right)).

## A kód szabályai {#conventions-of-the-code}

- A `match.py` időpontjai meccs-másodpercek, kivéve a lerakás `time`-ját, amely másodperc a körbe, ahogy a meccsdokumentum
  írja; a tickek csak a `_Part.at`-on keresztül lesznek másodpercekké.
- Az oldalak `T` / `CT` szövegek mindenhol a nyers demóadaton kívül (`team_num` 2 / 3).
- Új táblázatoszlop a `ROW_COLUMNS`-ba (és ha számszerű, a `NUMERIC`-ba) kerül a `match.py`-ban; az `output.table` a
  Parquet-típusát az `INT16`, `INT32`, `FLOAT64` halmazokból és a 0/1 jelzőkből választja, egyébként float32.
- Ha változtatni akarjuk, mit csináljon vele a megjelenítő, az `output.py` `HINTS` részét kell módosítani.

## Licenc {#licence}

MIT. A harmadik féltől származó csomagok és amit a játékok előírnak:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
A demók és a pályák sosem részei a tárolónak; a `.gitignore` a típusuk szerint kizárja a `*.dem`, `*.parquet`,
`*.match.json`, `*.glb` és hasonló fájlokat.
