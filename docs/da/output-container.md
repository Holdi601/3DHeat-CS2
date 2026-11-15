---
title: "En fil pr. kamp"
nav_order: 10
lang: "da"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# En fil pr. kamp (`<match>.3dheat`) {#one-file-a-match-3dheat}

Som standard pakker `demos` hver kamp i én fil, `out/<map>/<match>.3dheat`:
heatmap-tabellen, kampdokumentet og de fire sidecars sammen - én kamp, én fil, til at kopiere, gemme eller dele. Det er 3DHeat-visningens containerformat, specificeret i visningens dokumentation:
[En fil pr. kamp (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([kilde](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kode: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Trin for trin {#step-by-step}

1. Konverter som sædvanligt; der er intet at sætte:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Hver kamp er én fil i sin kortmappe:

   ![demos på en syntetisk demo](../assets/img/demos-run.svg)

3. Åbn den i visningen (fanen Heatmap eller fanen Kamp), eller læs den selv: den er en almindelig ZIP.

   ![inde i en .3dheat-container](../assets/img/container-members.svg)

Hvis du i stedet vil beholde de separate filer - til værktøjer, der vil have en Parquet-fil på disken - så tilføj `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Hvad der er indeni {#what-is-inside}

En ZIP, hvis første medlem er `manifest.json`, og derefter medlemmerne. Parquet-medlemmer er *gemt* (Parquet er allerede komprimeret, og et gemt medlem er ét bytes-område, en læser kan bruge direkte), mens JSON-medlemmer er deflate-komprimeret.

| Rolle | Medlem | Hvad |
|---|---|---|
| `table` | `<match>.parquet` | [Heatmap-tabellen](output-table.md) (skema `heat3d-table`) |
| `match` | `<match>.match.json` | [Kampdokumentet](output-match-json.md) (skema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | hver spilhændelse parseren læser, hel |
| `props` | `<match>.props.parquet` | hver egenskabsændring parseren læser |
| `strings` | `<match>.strings.parquet` | hver strengtabel-post |
| `packets` | `<match>.packets.parquet` | hver anden frame og netværksbesked, hel |

Manifestet navngiver format og version, spillet (`cs2`), kilden (`demo`), konverteren og dens version, kampen, kortet, hvornår den blev skrevet, et `roles`-kort fra rolle til medlem, og for hvert medlem dets medietype, komprimering, størrelse, SHA-256, antal rækker og, hvor det har et, dets skema. På den syntetiske demo fra testene (forkortet):

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

## Læs en uden visningen {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` læser kampdokumentet direkte fra containeren (eller fra et løst `.match.json`).

## Springe over og omskrive {#skipping-and-rewriting}

En container bliver skrevet hel eller slet ikke, så en `.3dheat` under `--out` tæller som en færdig kamp; `--force` skriver den om. En kamp, der tidligere er konverteret med `--loose`, tæller også som færdig.
