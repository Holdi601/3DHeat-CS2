---
title: "Utveckling"
nav_order: 15
lang: "sv"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Utveckling {#development}

## Struktur {#layout}

| Sökväg | Vad |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: versionskontrollen, sedan kommandoraden |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | kommandona och alternativen; gruppering av demofiler till matcher; arbetsprocesspoolen |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | en demofil genom demoparser2 till en `RawPart` - [Läsa en demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | delar, kedjor, klockan, rundor, lag, rader, kills, skada, blindningar - [Bygga en match](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | rundsammanfattningar, resultattavlan, matchdokumentet, den textbaserade resultattavlan - [Statistik](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet-tabellen med dess `heat3d`-tips, och JSON - [Värmekartetabellen](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | att hitta CS2 och Source2Viewer, kollisionsnätet i visarens koordinatsystem - [Kartexport](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | en minimal läsare och skrivare för glTF-binärt format (inget beroende utöver numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | versionskontrollen och uppdateraren - [Uppdateringar](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testerna och den syntetiska demon |
| `VERSION` | versionen, en rad |

Dataflödet:

```text
.dem-filer --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rundor, spelare, lag, rader, kills, skada, blindningar)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Använda det från Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # värmekartetabellen som en pandas-DataFrame
    kills = match.kills        # en rad per dödsfall, med alla flaggor
    doc = summary(match)       # .match.json-dokumentet som en dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` och `Match.blinds` är pandas-DataFrames med mer än vad
utdata innehåller - angripares och offrens positioner och platser per kill, per träff
`utility` - för egna analyser.

## Tester {#tests}

```bash
python -m pytest
```

`pytest.ini` kör `tests/` tyst. Testerna behöver ingen demo, inget spel och ingen
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
bygger en demo för hand, så som demoparser2 skulle ge den - två rundor, två spelare per
sida (`ace`, `ash` i laget Alpha; `bob`, `ben` i Bravo), tillräckligt små för att varje svar
är känt:

- Runda 1, en T-vinst genom eliminering: ace dödar bob med ett huvudskott (öppningen), ben
  dödar ace 1,9 s senare (en trade: bobs död är hämnad), ash dödar ben 3,1 s efter det -
  ensam mot en, en vunnen clutch.
- Runda 2, en T-vinst genom bomben: ash planterar på A, ingen dör, bomben går av.

`fixtures.halves` bygger en längre match av tomma rundor, lagen på sina första sidor eller
bytta, med spelets övertidsräknare eller utan, för halvlekens längd och pistolrundorna.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
kontrollerar på den: varje rundas vinnare, orsak, ställning och sidor; klockan som startar
vid matchen; ekonomi och plantering (dess tid in i rundan, dess plats, bomben som går av); en
plantering vars sida alltid är en bokstav eller tom, aldrig ett entitetsnummer; en oavgjord
runda avgjord utan vinnare; pistolrundorna från där sidorna byter, övertid utesluten, och
bara runda 1 utan byte; lag utan klannamn (`Started T` / `Started CT`); öppningar, trades och
flaggor; ett suicide som inte är en teamkill, och öppningen överlämnad till första fiendekillen;
`noscope` och `attackerBlind` i tabellen och matchdokumentet; skada som förlorad hälsa (60, sedan
40 av en 137 på 40 hälsa); resultattavlans siffror och KAST; clutchar; den textbaserade
resultattavlan; tabellens händelser och var de ligger (en detonation utan egen plats, kastarens i
`throwerPlace`; explosionen i det planterande lagets namn); att positionerna är levande, märkta
och har enhetsvektorer som blickriktning; att den skrivna filen bär sina tips; delar satta i
ordning oavsett deras namn; en omstartad serverklocka som ändå fortsätter; och en återställd
runda vars dubbla rader löses till den som leder vidare.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
kontrollerar att demos i mappar hittas oavsett versaler i `.dem`, och att en match bara räknas
som skriven när både dess tabell och dess matchdokument finns.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
kontrollerar koordinatomvandlingarna (Source2Viewers meter till spelets tum, och vidare till
visarens koordinatsystem, en rotation med determinant 1), att clip och himmel utelämnas oavsett
versaler och namngivna ytor, delningen mellan mark och konstruktion efter normalen, och en
`.glb` som skrivs och läses tillbaka.

### Golvkontrollen på en riktig karta {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<en demo> HEAT3D_SOURCE2VIEWER=<CLI:n> python -m pytest
```

När båda variablerna är satta körs även `test_players_stand_on_the_exported_floor`: den
konverterar demon, exporterar dess karta från det installerade spelet, och kontrollerar att
minst 98 % av 300 slumpmässiga positionssampel har mark under sig, med en medianhöjd över den
under 5 enheter ([Kartexport](map-export.md#the-check-that-the-frame-is-right)).

## Kodens konventioner {#conventions-of-the-code}

- Tider inne i `match.py` är matchsekunder, utom en planterings `time`, sekunder in i sin runda
  så som matchdokumentet skriver den; ticks blir sekunder först genom `_Part.at`.
- Sidor är strängarna `T` / `CT` överallt utanför den råa parserdatan (`team_num` 2 / 3).
- En ny tabellkolumn går i `ROW_COLUMNS` (och `NUMERIC` om den är numerisk) i `match.py`;
  `output.table` väljer dess Parquet-typ ur mängderna `INT16`, `INT32`, `FLOAT64` och 0/1-flaggorna,
  annars float32.
- Att ändra vad visaren ska göra med en kolumn betyder att ändra `HINTS` i `output.py`.

## Licens {#licence}

MIT. Tredjepartspaket: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demos och kartor ingår aldrig i arkivet; dess `.gitignore` håller `*.dem`, `*.parquet`,
`*.match.json`, `*.glb` och liknande borta, efter typ.
