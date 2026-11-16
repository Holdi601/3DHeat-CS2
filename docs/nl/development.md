---
title: Ontwikkeling
nav_order: 15
lang: "nl"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Ontwikkeling {#development}

## Indeling {#layout}

| Pad | Wat |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: eerst de controle op nieuwe releases, dan de opdrachtregel |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | de verbs en opties; het groeperen van demobestanden in wedstrijden; de werkpool |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | één demobestand via demoparser2 naar een `RawPart` - [Een demo lezen](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | delen, ketens, de klok, rondes, teams, rijen, kills, schade, verblindingen - [Een wedstrijd opbouwen](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | rondeoverzichten, het scorebord, het matchdocument, het tekstscorebord - [Statistieken](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | de Parquet-tabel met haar `heat3d`-hints, en de JSON - [De heatmaptabel](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | CS2 en Source2Viewer vinden, het collision mesh naar het assenstelsel van de viewer - [Kaart exporteren](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | een minimale lezer en schrijver van glTF binary (geen afhankelijkheid behalve numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | de controle op releases en de updater - [Updates](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | de tests en de synthetische demo |
| `VERSION` | de versie, één regel |

De gegevensstroom:

```text
.dem-bestanden --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per wedstrijd
          --match.build_match--> Match (rondes, spelers, teams, rijen, kills, schade, verblindingen)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Gebruiken vanuit Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # de heatmaptabel als pandas DataFrame
    kills = match.kills        # één rij per dood, met elke vlag
    doc = summary(match)       # het .match.json-document als dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` en `Match.blinds` zijn pandas DataFrames met meer dan de uitvoer bevat - posities en plekken van aanvaller en slachtoffer per kill, `utility` per treffer - voor je eigen analyses.

## Tests {#tests}

```bash
python -m pytest
```

`pytest.ini` draait `tests/` stil. De tests hebben geen demo, geen spel en geen Source2Viewer nodig: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) bouwt met de hand een demo, zoals demoparser2 die zou geven - twee rondes, twee spelers per kant (`ace`, `ash` van team Alpha; `bob`, `ben` van Bravo), klein genoeg dat elk antwoord bekend is:

- Ronde 1, een T-overwinning door eliminatie: ace doodt bob met een headshot (de opening), ben doodt ace 1,9 s later (een trade: bobs dood is gewroken), ash doodt ben 3,1 s daarna - alleen tegen één, een clutch gewonnen.
- Ronde 2, een T-overwinning door de bom: ash plant op A, niemand sterft, de bom gaat af.

`fixtures.halves` bouwt een langere wedstrijd van lege rondes, de teams op hun eerste kanten of gewisseld, met het overtime-aantal van de game of zonder, voor de lengte van de helft en de pistoolrondes.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) controleert daarop: de winnaar, reden, score en kanten van elke ronde; de klok die bij de wedstrijd begint; economie en de plant (zijn tijd in de ronde, zijn plek, de bom die afgaat); een site van een plant die altijd een letter of leeg is, nooit een entiteitsnummer; een gelijkspel dat is beslist zonder winnaar; de pistoolrondes vanaf waar de kanten wisselen, overtime buiten beschouwing, en alleen ronde 1 zonder wissel; teams zonder clannamen (`Started T` / `Started CT`); openingen, trades en vlaggen; een suïcide die geen teamkill is, en de opening die doorgaat naar de eerste kill van een vijand; `noscope` en `attackerBlind` in de tabel en het matchdocument; schade als verloren gezondheid (60, dan 40 van een 137 op 40 gezondheid); de getallen van het scorebord en KAST; clutches; het tekstscorebord; de gebeurtenissen van de tabel en waar ze staan (een ontploffing zonder eigen plek, die van de gooier in `throwerPlace`; de explosie van het planterende team); dat posities live zijn, gelabeld, en eenheidsvectoren als kijkrichting hebben; dat het geschreven bestand zijn hints draagt; dat delen in volgorde worden gezet, welke naam ze ook hebben; een herstarte klok van de server die toch doorloopt; en de dubbele rijen van een herstelde ronde die worden opgelost tot degene die vooruit leidt.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) controleert dat demo's in mappen worden gevonden, ongeacht de schrijfwijze van `.dem`, en dat een wedstrijd alleen als geschreven telt met zowel zijn tabel als zijn matchdocument.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) controleert de conversies van het assenstelsel (de meters van Source2Viewer naar de inches van de game, en verder naar het assenstelsel van de viewer, een rotatie met determinant 1), dat clips en lucht worden weggelaten, ongeacht de schrijfwijze en de namen van oppervlakken, de splitsing grond/structuur op de normaal, en een `.glb` die wordt geschreven en weer gelezen.

### De vloercontrole op een echte map {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<een demo> HEAT3D_SOURCE2VIEWER=<de CLI> python -m pytest
```

Met beide variabelen gezet, draait ook `test_players_stand_on_the_exported_floor`: die zet de demo om, exporteert zijn map uit het geïnstalleerde spel, en controleert dat minstens 98 % van 300 willekeurige positiemonsters grond onder zich heeft, met een mediane hoogte erboven van minder dan 5 eenheden ([Kaart exporteren](map-export.md#de-controle-dat-het-assenstelsel-klopt)).

## Conventies van de code {#conventions-of-the-code}

- De tijden in `match.py` zijn matchseconden, behalve de `time` van een plant, de seconden in zijn ronde zoals het matchdocument ze schrijft; ticks worden alleen via `_Part.at` seconden.
- Kanten zijn overal buiten de ruwe parserdata de tekenreeksen `T` / `CT` (`team_num` 2 / 3).
- Een nieuwe tabelkolom gaat in `ROW_COLUMNS` (en `NUMERIC` als ze numeriek is) in `match.py`; `output.table` kiest zijn Parquet-type uit de sets `INT16`, `INT32`, `FLOAT64` en de 0/1-vlaggen, anders float32.
- Verandert wat de viewer met een kolom moet doen, dan verander je `HINTS` in `output.py`.

## Licentie {#licence}

MIT. Pakketten van derden: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md). Demo's en kaarten maken nooit deel uit van de repository; de `.gitignore` houdt `*.dem`, `*.parquet`, `*.match.json`, `*.glb` en dergelijke op soort buiten de deur.
