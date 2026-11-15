---
title: "Eine Datei pro Match"
nav_order: 10
lang: de
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Eine Datei pro Match (`<match>.3dheat`) {#one-file-a-match-3dheat}

Standardmäßig packt `demos` jedes Match in eine Datei, `out/<Karte>/<match>.3dheat`: die Heatmap-Tabelle, das
Match-Dokument und die vier Beiwerk-Dateien zusammen - ein Match, eine Datei, zum Kopieren, Behalten oder
Teilen. Es ist das Containerformat des 3DHeat-Viewers, beschrieben in der Dokumentation des Viewers:
[Eine Datei pro Match (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([Quelle](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Code: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Schritt für Schritt {#step-by-step}

1. Konvertiere wie gewohnt; du musst nichts einstellen:

   ```bash
   python -m heat3d_cs2 demos <Demo-Dateien oder Ordner> -o out
   ```

2. Jedes Match ist eine Datei in dem Ordner seiner Karte:

   ![demos auf einem synthetischen Demo](../assets/img/demos-run.svg)

3. Öffne sie im Viewer (Heatmap-Tab oder Match-Tab) oder lies sie selbst: Es ist eine ganz gewöhnliche ZIP-Datei.

   ![in einem .3dheat-Container](../assets/img/container-members.svg)

Willst du stattdessen die getrennten Dateien behalten - für Werkzeuge, die eine Parquet-Datei auf der Platte
brauchen -, füge `--loose` hinzu:

![demos --loose](../assets/img/demos-loose.svg)

## Was darin ist {#what-is-inside}

Eine ZIP, deren erstes Element `manifest.json` ist, dann die Elemente. Parquet-Elemente werden *gespeichert*
(Parquet ist schon komprimiert, und ein gespeichertes Element ist ein einzelner Bytebereich, den ein Leser direkt
nutzen kann); JSON-Elemente sind deflate-komprimiert.

| Rolle | Element | Was |
|---|---|---|
| `table` | `<match>.parquet` | [Die Heatmap-Tabelle](output-table.md) (Schema `heat3d-table`) |
| `match` | `<match>.match.json` | [Das Match-Dokument](output-match-json.md) (Schema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | jedes Spielereignis, das der Parser liest, vollständig |
| `props` | `<match>.props.parquet` | jede Eigenschaftsänderung, die der Parser liest |
| `strings` | `<match>.strings.parquet` | jeder Eintrag der Stringtabelle |
| `packets` | `<match>.packets.parquet` | jeder andere Frame und jede Netzwerknachricht, vollständig |

Das Manifest nennt das Format und seine Version, das Spiel (`cs2`), die Quelle (`demo`), den Konverter und seine
Version, das Match, die Karte, wann es geschrieben wurde, eine `roles`-Zuordnung von Rolle zu Element, und je
Element seinen Medientyp, die Kompression, die Größe, die SHA-256, die Zeilenanzahl und, wo vorhanden, sein
Schema. Beim synthetischen Demo der Tests (gekürzt):

```json
{
  "format": "3dheat",
  "format_version": "1.0",
  "game": "cs2",
  "source": "demo",
  "converter": { "name": "heat3d_cs2", "version": "1.0.2" },
  "match": "alpha-vs-bravo-m1",
  "map": "de_test",
  "roles": {
    "table": "alpha-vs-bravo-m1.parquet",
    "match": "alpha-vs-bravo-m1.match.json",
    "events": "alpha-vs-bravo-m1.events.parquet",
    "packets": "alpha-vs-bravo-m1.packets.parquet",
    "props": "alpha-vs-bravo-m1.props.parquet",
    "strings": "alpha-vs-bravo-m1.strings.parquet"
  },
  "members": [
    {
      "name": "alpha-vs-bravo-m1.parquet",
      "role": "table",
      "media_type": "application/vnd.apache.parquet",
      "compression": "stored",
      "bytes": 38769,
      "sha256": "1b7b7d16...",
      "rows": 2655,
      "schema": { "id": "heat3d-table", "version": "1" }
    }
  ]
}
```

## Ohne den Viewer lesen {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` liest das Match-Dokument direkt aus dem Container (oder aus einer losen `.match.json`).

## Überspringen und Neuschreiben {#skipping-and-rewriting}

Ein Container wird ganz oder gar nicht geschrieben; daher zählt eine `.3dheat` unter `--out` als erledigtes
Match, und `--force` schreibt sie neu. Ein Match, das vorher mit `--loose` konvertiert wurde, zählt ebenfalls
als erledigt.
