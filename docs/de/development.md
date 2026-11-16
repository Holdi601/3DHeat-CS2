---
title: "Entwicklung"
nav_order: 15
lang: "de"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Entwicklung {#development}

## Aufbau {#layout}

| Pfad | Was |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: erst die Versionsprüfung, dann die Kommandozeile |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | die Befehle und Optionen; das Gruppieren der Demo-Dateien zu Matches; der Arbeiter-Pool |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | eine Demo-Datei durch demoparser2 in einen `RawPart` - [Ein Demo lesen](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | Teile, Ketten, die Uhr, Runden, Teams, Zeilen, Kills, Schaden, Blendungen - [Ein Match aufbauen](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | Rundenübersichten, das Scoreboard, das Match-Dokument, das Text-Scoreboard - [Statistiken](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | die Parquet-Tabelle mit ihren `heat3d`-Hinweisen und das JSON - [Die Heatmap-Tabelle](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | das Finden von CS2 und Source2Viewer, das Kollisionsnetz im Koordinatensystem des Viewers - [Karten-Export](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | ein minimaler Leser und Schreiber für glTF-Binär (keine Abhängigkeit außer numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | die Versionsprüfung und der Updater - [Updates](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | die Tests und das synthetische Demo |
| `VERSION` | die Version, eine Zeile |

Der Datenfluss:

```text
.dem-Dateien --demo.read_part--> RawPart --match.chains--> [RawPart, ...] pro Match
          --match.build_match--> Match (Runden, Spieler, Teams, Zeilen, Kills, Schaden, Blendungen)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer-CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Verwendung aus Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # die Heatmap-Tabelle als pandas DataFrame
    kills = match.kills        # eine Zeile pro Tod, mit allen Flags
    doc = summary(match)       # das .match.json-Dokument als dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` und `Match.blinds` sind pandas-DataFrames mit mehr, als die Ausgaben
enthalten - Angreifer- und Opfer-Positionen und -Orte pro Kill, Treffer für Treffer `utility` - für
eigene Auswertungen.

## Tests {#tests}

```bash
python -m pytest
```

`pytest.ini` führt `tests/` leise aus. Die Tests brauchen kein Demo, kein Spiel und keine
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
baut von Hand ein Demo, so wie demoparser2 es liefern würde - zwei Runden, zwei Spieler pro Seite
(`ace`, `ash` vom Team Alpha; `bob`, `ben` vom Team Bravo), klein genug, dass jede Antwort bekannt ist:

- Runde 1, ein T-Sieg durch Eliminierung: ace tötet bob mit einem Kopftreffer (das Opening), ben tötet
  ace 1,9 s später (ein Trade: bobs Tod ist getradet), ash tötet ben 3,1 s danach - allein gegen einen,
  ein gewonnener Clutch.
- Runde 2, ein T-Sieg durch die Bombe: ash legt auf A, niemand stirbt, die Bombe explodiert.

`fixtures.halves` baut ein längeres Match aus leeren Runden, die Teams auf ihren ersten Seiten oder
getauscht, mit dem Verlängerungszähler des Spiels oder ohne, für die Länge der Hälfte und die
Pistolenrunden.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) prüft
darauf: den Sieger, den Grund, das Ergebnis und die Seiten jeder Runde; die Uhr, die beim Match beginnt;
Wirtschaft und Bombenlegung (ihre Zeit in der Runde, ihr Ort, die Explosion der Bombe); dass der Site
einer Legung immer ein Buchstabe oder leer ist, nie eine Entity-Nummer; ein Unentschieden, entschieden
ohne Gewinner; die Pistolenrunden dort, wo die Seiten tauschen, Verlängerungen ausgenommen, und nur Runde
1 ohne Tausch; Teams ohne Clan-Namen (`Started T` / `Started CT`); Openings, Trades und Flags; ein Suizid,
der kein Teamkill ist, und das Opening, das an den ersten Gegner-Kill weitergegeben wird; `noscope` und
`attackerBlind` in der Tabelle und im Match-Dokument; Schaden als verlorene Gesundheit (60, dann 40 von
einem 137er-Treffer bei 40 Gesundheit); die Zahlen des Scoreboards und KAST; Clutches; das Text-Scoreboard;
die Ereignisse der Tabelle und wo sie liegen (eine Detonation ohne eigenen Ort, der des Werfers in
`throwerPlace`; die Explosion beim Team, das die Bombe legte); dass Positionen live sind, beschriftet und
Blickvektoren der Länge 1 haben; dass die geschriebene Datei ihre Hinweise trägt; dass Teile unabhängig
von ihren Namen in die richtige Reihenfolge kommen; eine neu gestartete Serveruhr, die weiterläuft; und
eine wiederhergestellte Runde, deren doppelte Zeilen auf die führende aufgelöst werden.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) prüft, dass
Demos in Ordnern gefunden werden, egal wie `.dem` geschrieben ist, und dass ein Match nur dann als
geschrieben gilt, wenn Tabelle und Match-Dokument beide da sind.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
prüft die Umrechnungen der Koordinaten (von Source2Viewers Metern in die Zoll des Spiels und weiter in
das Koordinatensystem des Viewers, eine Drehung mit Determinante 1), dass Clips und Himmel weggelassen
werden, egal in welcher Schreibweise und welchen Oberflächen sie benannt sind, die Trennung von Boden und
Struktur nach der Normale, und dass eine `.glb` geschrieben und wieder gelesen wird.

### Die Bodenprüfung auf einer echten Karte {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<ein Demo> HEAT3D_SOURCE2VIEWER=<die CLI> python -m pytest
```

Sind beide Variablen gesetzt, läuft zusätzlich `test_players_stand_on_the_exported_floor`: Er wandelt das
Demo um, exportiert seine Karte aus dem installierten Spiel und prüft, dass mindestens 98 % von 300
zufälligen Positionsproben Boden unter sich haben, bei einem Median der Höhe darüber von unter 5 Einheiten
([Karten-Export](map-export.md#the-check-that-the-frame-is-right)).

## Konventionen im Code {#conventions-of-the-code}

- Zeiten in `match.py` sind Match-Sekunden, außer der `time` einer Bombenlegung: Sekunden in ihrer Runde,
  so wie das Match-Dokument sie schreibt; Ticks werden nur über `_Part.at` zu Sekunden.
- Seiten sind überall außerhalb der Rohdaten des Parsers die Strings `T` / `CT` (`team_num` 2 / 3).
- Eine neue Tabellenspalte kommt in `ROW_COLUMNS` (und in `NUMERIC`, wenn sie numerisch ist) in
  `match.py`; `output.table` wählt ihren Parquet-Typ aus den Mengen `INT16`, `INT32`, `FLOAT64` und den
  0/1-Flags, sonst float32.
- Ändert sich, was der Viewer mit einer Spalte tun soll, müssen die `HINTS` in `output.py` geändert werden.

## Lizenz {#licence}

MIT. Fremde Pakete:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demos und Karten sind nie Teil des Repositorys; seine `.gitignore` hält `*.dem`, `*.parquet`,
`*.match.json`, `*.glb` und ähnliche Dateien nach Typ fern.
