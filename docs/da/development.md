---
title: "Udvikling"
nav_order: 15
lang: "da"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Udvikling {#development}

## Opbygning {#layout}

| Sti | Hvad |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: udgivelsestjekket, derefter kommandolinjen |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | kommandoerne og valgene; gruppering af demo-filer i kampe; arbejderpuljen |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | én demo-fil gennem demoparser2 til en `RawPart` - [Læsning af en demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | dele, kæder, uret, runder, hold, rækker, kills, skade, blændinger - [Sådan bygges en kamp](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | rundeopsummeringer, scoreboardet, kampdokumentet, tekst-scoreboardet - [Statistik](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet-tabellen med dens `heat3d`-hints, og JSON - [Heatmap-tabellen](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | at finde CS2 og Source2Viewer, kollisionsmeshen over i visningens koordinatsystem - [Kortudtræk](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | en minimal glTF-binærlæser og -skriver (ingen afhængighed ud over numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | udgivelsestjekket og opdateringsværktøjet - [Opdateringer](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testene og den syntetiske demo |
| `VERSION` | versionen, én linje |

Dataflowet:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Brug det fra Python {#using-it-from-python}

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

`Match.kills`, `Match.damage` og `Match.blinds` er pandas-DataFrames med mere, end
outputtene indeholder - angriberens og offerets positioner og steder pr. kill, og
`utility` pr. hit - til analyser, du selv laver.

## Tests {#tests}

```bash
python -m pytest
```

`pytest.ini` kører `tests/` stille. Testene har brug for hverken demo, spil eller
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
bygger en demo i hånden, som demoparser2 ville levere den - to runder, to spillere
pr. side (`ace`, `ash` fra holdet Alpha; `bob`, `ben` fra Bravo), lille nok til, at
hvert svar er kendt:

- Runde 1, en T-sejr ved elimination: ace dræber bob med et hovedskud (åbningen),
  ben dræber ace 1,9 s senere (en trade: bobs død er hævnet), ash
  dræber ben 3,1 s efter det - alene mod én, en clutch vundet.
- Runde 2, en T-sejr ved bomben: ash planter på A, ingen dør, bomben går af.

`fixtures.halves` bygger en længere kamp med tomme runder, holdene på deres første
sider eller byttet, med spillets overtid-tæller eller uden, til halvlegens længde og
pistolrunderne.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
tjekker på den: hver rundes vinder, årsag, score og sider; uret der starter ved
kampen; økonomi og plantningen (dens tid inde i runden, dens sted, bomben der går af);
en plantnings site altid et bogstav eller tom, aldrig et entity-nummer; et uafgjort
afgjort uden vinder; pistolrunderne fra hvor siderne bytter, overtid udeladt, og
kun runde 1 uden byt; hold uden klannavne (`Started T` / `Started CT`); åbninger,
trades og flag; et selvmord, der ikke er et teamkill, og åbningen videregivet til
den første fjende-kill; `noscope` og `attackerBlind` i tabellen og kampdokumentet;
skade som mistede liv (60, derefter 40 af et 137 på 40 liv); scoreboard-tallene og
KAST; clutches; tekst-scoreboardet; hændelserne i tabellen og hvor de er (en
detonation uden et eget sted, kasterens i `throwerPlace`; eksplosionen tilhører det
plantende hold); at positioner er live, mærket og har enhedsvektorer for kig; at den
skrevne fil bærer sine hints; at dele bliver sat i rækkefølge, uanset deres navne; et
genstartet serverur, der stadig fortsætter; og en gendannet rundes dublerede rækker
løst til den, der fører videre.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
tjekker, at demoer i mapper bliver fundet, uanset hvordan `.dem` staves, og at en kamp
kun tæller som skrevet, når både dens tabel og dens kampdokument er der.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
tjekker omregningerne af koordinatsystemet (Source2Viewers meter til spillets tommer,
og videre til visningens koordinatsystem, en rotation med determinant 1), at clips og
himmel bliver udeladt, uanset store eller små bogstaver, og overflader med navne, at
gulv/struktur-opdelingen efter normalen, og en `.glb`, der bliver skrevet og læst
tilbage.

### Gulvtjekket på et rigtigt kort {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Når begge variabler er sat, kører `test_players_stand_on_the_exported_floor` også:
den konverterer demoen, eksporterer dens kort fra det installerede spil og
tjekker, at mindst 98 % af 300 tilfældige positionssamples har gulv under sig, med en
median højde over det under 5 enheder ([Kortudtræk](map-export.md#the-check-that-the-frame-is-right)).

## Konventioner i koden {#conventions-of-the-code}

- Tider inde i `match.py` er kampsekunder, undtagen en plantnings `time`, sekunder
  inde i runden, som kampdokumentet skriver den; ticks bliver kun til sekunder gennem
  `_Part.at`.
- Sider er strengene `T` / `CT` alle steder uden for den rå parserdata
  (`team_num` 2 / 3).
- En ny tabelkolonne går i `ROW_COLUMNS` (og `NUMERIC`, hvis den er numerisk) i
  `match.py`; `output.table` vælger sin Parquet-type ud fra mængderne `INT16`,
  `INT32`, `FLOAT64` og 0/1-flagene, float32 ellers.
- At ændre, hvad visningen skal gøre med en kolonne, betyder at ændre `HINTS` i
  `output.py`.

## Licens {#licence}

MIT. Tredjepartspakker og hvad spillene kræver:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demoer og kort er aldrig en del af repositoriet; dets `.gitignore` holder
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` og lignende ude efter type.
