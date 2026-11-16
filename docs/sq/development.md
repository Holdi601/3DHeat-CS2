---
title: "Zhvillimi"
nav_order: 15
lang: "sq"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Zhvillimi {#development}

## Struktura {#layout}

| Shtegu | Çfarë |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: kontrolli i botimit, pastaj rreshti i komandave |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | komandat dhe opsionet; grupimi i skedarëve të demove në ndeshje; grupi i punëtorëve |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | një skedar demoje përmes demoparser2 në një `RawPart` - [Leximi i një demoje](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | pjesët, zinxhirët, ora, raundet, ekipet, rreshtat, vrasjet, dëmi, verbimet - [Ndërtimi i një ndeshjeje](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | përmbledhjet e raundeve, tabela e rezultateve, dokumenti i ndeshjes, tabela e rezultateve si tekst - [Statistikat](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | tabela Parquet me sugjerimet e saj `heat3d`, dhe JSON - [Tabela e hartës së nxehtësisë](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | gjetja e CS2 dhe Source2Viewer, rrjeta e përplasjes në sistemin e shikuesit - [Eksporti i hartës](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | një lexues dhe shkrues minimal glTF binar (pa varësi përveç numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | kontrolli i botimit dhe përditësuesi - [Përditësimet](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testet dhe demoja sintetike |
| `VERSION` | versioni, një rresht |

Rrjedha e të dhënave:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Përdorimi nga Python {#using-it-from-python}

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

`Match.kills`, `Match.damage` dhe `Match.blinds` janë DataFrame-e pandas me
më shumë se ç'mbajnë daljet - pozicionet dhe vendet e sulmuesit dhe të viktimës për
çdo vrasje, `utility` për çdo goditje - për analiza të tuat.

## Testet {#tests}

```bash
python -m pytest
```

`pytest.ini` i xhiron `tests/` në heshtje. Testet nuk kërkojnë demo, lojë apo
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
ndërton një demo me dorë, siç do ta jepte demoparser2 - dy raunde, dy
lojtarë në anë (`ace`, `ash` të ekipit Alpha; `bob`, `ben` të Bravo), mjaft të vogla
që çdo përgjigje të dihet:

- Raundi 1, fitore e T me eliminim: ace vret bob me një goditje në kokë (hapja),
  ben vret ace 1.9 s më vonë (një trade: vdekja e bob është traded), ash
  vret ben 3.1 s pas kësaj - një kundër një, një clutch i fituar.
- Raundi 2, fitore e T me bombën: ash vendos në A, askush nuk vdes, bomba
  shpërthen.

`fixtures.halves` ndërton një ndeshje më të gjatë me raunde bosh, ekipet në
anët e tyre të para ose të ndërruara, me numrin e kohës shtesë të lojës ose pa të, për
gjatësinë e pjesës dhe raundet e pistoletave.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
kontrollon mbi të: fituesin, arsyen, rezultatin dhe anët e çdo raundi; orën
që nis me ndeshjen; ekonominë dhe vendosjen e bombës (koha e saj brenda raundit, vendi i saj,
bomba që shpërthen); site e një vendosjeje gjithmonë shkronjë ose bosh, kurrë
numër entiteti; një barazim i vendosur pa fitues; raundet e pistoletave nga
ku ndërrohen anët, kohën shtesë të lënë jashtë, dhe vetëm raundin 1 pa ndërrim;
ekipet pa emra klanesh (`Started T` / `Started CT`); hapjet, trade-et dhe
flamujt; një vetëvrasje që nuk është teamkill, dhe hapjen që kalon te vrasja e parë
e një armiku; `noscope` dhe `attackerBlind` në tabelë dhe në dokumentin e ndeshjes;
dëmin si shëndet të humbur (60, pastaj 40 nga një 137 mbi 40 shëndet); numrat e
tabelës së rezultateve dhe KAST; clutch-et; tabelën e rezultateve si tekst; ngjarjet e tabelës dhe
ku janë (një shpërthim pa vend të vetin, vendi i hedhësit te
`throwerPlace`; shpërthimi i ekipit që vendosi); që pozicionet janë live,
të shënuara dhe kanë vektorë shikimi njësi; që skedari i shkruar mban
sugjerimet e tij; pjesët të vëna në rregull sido që quhen; një orë serveri e rinisur
që prapë vazhdon; dhe rreshtat e dyfishtë të një raundi të rikthyer të zgjidhur te
ai që të çon përpara.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
kontrollon që demot në dosje gjenden sido që të shkruhet `.dem`, dhe që
një ndeshje llogaritet e shkruar vetëm me tabelën dhe dokumentin e ndeshjes të dyja.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
kontrollon konvertimet e sistemit (metrat e Source2Viewer në inçet e lojës,
dhe më tej në sistemin e shikuesit, një rrotullim me përcaktor 1), që clip-et dhe
qielli lihen jashtë sido që të shkruhen dhe sipërfaqet e emërtuara, ndarjen ground/structure sipas normales,
dhe një `.glb` të shkruar e të lexuar përsëri.

### Kontrolli i dyshemesë në një hartë të vërtetë {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Me të dyja variablat të vendosura, xhirohet edhe `test_players_stand_on_the_exported_floor`:
konverton demon, eksporton hartën e saj nga loja e instaluar, dhe
kontrollon që të paktën 98 % e 300 mostrave të rastësishme të pozicionit kanë tokë nën
vete, me një lartësi mediane mbi të nën 5 njësi
([Eksporti i hartës](map-export.md#the-check-that-the-frame-is-right)).

## Konventat e kodit {#conventions-of-the-code}

- Kohët brenda `match.py` janë sekonda ndeshjeje, përveç `time` të një vendosjeje,
  sekonda brenda raundit të saj siç i shkruan dokumenti i ndeshjes; tick-et bëhen sekonda vetëm
  përmes `_Part.at`.
- Anët janë vargje `T` / `CT` kudo jashtë të dhënave të papërpunuara të parserit
  (`team_num` 2 / 3).
- Një kolonë e re e tabelës shkon te `ROW_COLUMNS` (dhe `NUMERIC` nëse është numerike) në
  `match.py`; `output.table` e zgjedh llojin e saj Parquet nga bashkësitë `INT16`,
  `INT32`, `FLOAT64` dhe flamujt 0/1, përndryshe float32.
- Të ndryshosh çfarë duhet të bëjë shikuesi me një kolonë do të thotë të ndryshosh `HINTS` në
  `output.py`.

## Licenca {#licence}

MIT. Paketat e palëve të treta:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demot dhe hartat nuk janë kurrë pjesë e depos; `.gitignore` i saj mban jashtë
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` e të ngjashme sipas llojit.
