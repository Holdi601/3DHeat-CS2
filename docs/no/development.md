---
title: "Utvikling"
nav_order: 15
lang: "no"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Utvikling {#development}

## Oppsett {#layout}

| Sti | Hva |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: sjekken for nye utgivelser, deretter kommandolinjen |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | verbene og valgene; gruppering av demofiler til kamper; arbeiderpoolen |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | én demofil gjennom demoparser2 til en `RawPart` - [Lese en demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | deler, kjeder, klokken, runder, lag, rader, drap, skade, blendinger - [Bygge en kamp](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | rundesammendrag, resultattavlen, kampdokumentet, tekstresultattavlen - [Statistikk](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet-tabellen med sine `heat3d`-hint, og JSON - [Varmekarttabellen](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | finne CS2 og Source2Viewer, kollisjonsnettet over i visningens koordinatsystem - [Eksport av kart](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | en minimal leser og skriver for glTF-binær (ingen avhengighet utover numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | sjekken for nye utgivelser og oppdateringsprogrammet - [Oppdateringer](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testene og den syntetiske demoen |
| `VERSION` | versjonen, én linje |

Dataflyten:

```text
.dem-filer --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per kamp
          --match.build_match--> Match (runder, spillere, lag, rader, drap, skade, blendinger)
          --output.write--> <map>/<kamp>.parquet  (output.table + HINTS)
                            <map>/<kamp>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Bruk fra Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # varmekarttabellen som en pandas DataFrame
    kills = match.kills        # én rad per dødsfall, med alle flagg
    doc = summary(match)       # .match.json-dokumentet som en dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` og `Match.blinds` er pandas DataFrames med mer enn
utdataene har - angriperens og offerets posisjoner og steder per drap, og `utility` per
treff - til analyser du lager selv.

## Tester {#tests}

```bash
python -m pytest
```

`pytest.ini` kjører `tests/` stille. Testene trenger ingen demo, ingen spill og ingen
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
bygger en demo for hånd, slik demoparser2 ville gitt den - to runder, to spillere per side
(`ace`, `ash` i laget Alpha; `bob`, `ben` i Bravo), liten nok til at hvert svar er kjent:

- Runde 1, en T-seier ved eliminering: ace dreper bob med et hodeskudd (åpningen), ben
  dreper ace 1,9 s senere (en trade: bobs død er tradet), ash dreper ben 3,1 s etter
  det - alene mot én, en vunnet clutch.
- Runde 2, en T-seier ved bomben: ash planter på A, ingen dør, bomben går av.

`fixtures.halves` bygger en lengre kamp med tomme runder, lagene på sine første sider
eller byttet, med spillets antall forlengelser eller uten, for halvdelens lengde og
pistolrundene.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
sjekker på den: hver rundes vinner, grunn, score og sider; klokken som starter ved
kampen; økonomi og plantingen (dens tid inn i runden, dens sted, bomben som går av); en
plantings site alltid en bokstav eller tom, aldri et entitetsnummer; en uavgjort runde
avgjort uten vinner; pistolrundene der sidene bytter, forlengelse utelatt, og bare runde 1
uten bytte; lag uten klannavn (`Started T` / `Started CT`); åpninger, trades og flagg; et
selvmord som ikke er et lagkameraddrap, og åpningen som går videre til første fiendedrap;
`noscope` og `attackerBlind` i tabellen og kampdokumentet; skade som tapt helse (60, så 40
av et 137-treff på 40 helse); resultattavlens tall og KAST; clutcher; tekstresultattavlen;
hendelsene i tabellen og hvor de står (en detonasjon uten sted eget, kasterens i
`throwerPlace`; eksplosjonen til plantende lag); at posisjonene er levende, merket og har
enhetsvektorer som sikte; at den skrevne filen bærer sine hint; deler satt i rekkefølge
uansett navn; en omstartet serverklokke som likevel fortsetter; og en gjenopprettet rundes
doble rader løst til den som fører videre.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
sjekker at demoer i mapper finnes uansett bokstavstørrelse på `.dem`, og at en kamp bare
regnes som skrevet når både tabellen og kampdokumentet finnes.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
sjekker koordinatomregningene (Source2Viewers meter til spillets tommer, og videre til
visningens koordinatsystem, en rotasjon med determinant 1), at clip og himmel utelates
uansett bokstavstørrelse og navn på flater, deling i gulv og konstruksjon etter normalen,
og at en `.glb` skrives og leses tilbake.

### Gulvsjekken på et ekte kart {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<en demo> HEAT3D_SOURCE2VIEWER=<CLI-en> python -m pytest
```

Når begge variablene er satt, kjøres også `test_players_stand_on_the_exported_floor`: den
konverterer demoen, eksporterer kartet fra det installerte spillet, og sjekker at minst 98 %
av 300 tilfeldige posisjonsprøver har gulv under seg, med en median høyde over det under 5
enheter ([Eksport av kart](map-export.md#the-check-that-the-frame-is-right)).

## Kodekonvensjoner {#conventions-of-the-code}

- Tider inne i `match.py` er kampsekunder, bortsett fra en plantings `time`, sekunder inn i
  runden slik kampdokumentet skriver den; tick blir sekunder bare gjennom `_Part.at`.
- Sider er strengene `T` / `CT` overalt utenfor den rå parserdataen (`team_num` 2 / 3).
- En ny tabellkolonne går i `ROW_COLUMNS` (og `NUMERIC` hvis den er numerisk) i `match.py`;
  `output.table` velger sin Parquet-type fra settene `INT16`, `INT32`, `FLOAT64` og 0/1-flaggene,
  ellers float32.
- Å endre hva visningen skal gjøre med en kolonne, betyr å endre `HINTS` i `output.py`.

## Lisens {#licence}

MIT. Tredjepartspakker:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demoer og kart er aldri en del av repositoriet; dets `.gitignore` holder `*.dem`,
`*.parquet`, `*.match.json`, `*.glb` og lignende ute etter type.
