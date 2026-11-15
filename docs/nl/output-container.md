---
title: Eén bestand per match
nav_order: 10
lang: "nl"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Eén bestand per match (`<match>.3dheat`) {#one-file-a-match-3dheat}

Standaard pakt `demos` elke wedstrijd in één bestand, `out/<map>/<match>.3dheat`: de heatmaptabel, het matchdocument en de vier zijbestanden samen - één wedstrijd, één bestand, om te kopiëren, te bewaren of te delen. Het is het containerformaat van de 3DHeat-viewer, beschreven in de documentatie van de viewer: [Eén bestand per match (.3dheat)](https://holdi601.github.io/3DHeat/container.html) ([bron](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)). Code: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Stap voor stap {#step-by-step}

1. Zet om zoals gewoonlijk; er valt niets in te stellen:

   ```bash
   python -m heat3d_cs2 demos <demobestanden of mappen> -o out
   ```

2. Elke wedstrijd is één bestand in de map van zijn map:

   ![demos op een synthetische demo](../assets/img/demos-run.svg)

3. Open het in de viewer (tabblad Heatmap of tabblad Match), of lees het zelf: het is een gewone ZIP.

   ![in een .3dheat-container](../assets/img/container-members.svg)

Wil je de losse bestanden houden - voor tools die een Parquet-bestand op schijf willen - voeg dan `--loose` toe:

![demos --loose](../assets/img/demos-loose.svg)

## Wat erin zit {#what-is-inside}

Een ZIP waarvan het eerste item `manifest.json` is, daarna de items. Parquet-items worden *stored* opgeslagen (Parquet is al gecomprimeerd, en een opgeslagen item is één bytebereik dat een lezer op zijn plaats kan gebruiken); JSON-items worden met deflate gecomprimeerd.

| Rol | Item | Wat |
|---|---|---|
| `table` | `<match>.parquet` | [De heatmaptabel](output-table.md) (schema `heat3d-table`) |
| `match` | `<match>.match.json` | [Het matchdocument](output-match-json.md) (schema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | elke spelgebeurtenis die de parser leest, volledig |
| `props` | `<match>.props.parquet` | elke eigenschapswijziging die de parser leest |
| `strings` | `<match>.strings.parquet` | elke stringtabelregel |
| `packets` | `<match>.packets.parquet` | elk ander frame- en netwerkbericht, volledig |

Het manifest noemt het formaat en de versie, het spel (`cs2`), de bron (`demo`), de converter en zijn versie, de wedstrijd, de map, wanneer het is geschreven, een `roles`-overzicht van rol naar item, en per item het mediatype, de compressie, de grootte, de SHA-256, het aantal rijen en, waar het er een heeft, het schema. Op de synthetische demo uit de tests (ingekort):

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

## Lezen zonder de viewer {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` leest het matchdocument rechtstreeks uit de container (of uit een losse `.match.json`).

## Overslaan en opnieuw schrijven {#skipping-and-rewriting}

Een container wordt geheel of helemaal niet geschreven, dus een `.3dheat` onder `--out` telt als een klare wedstrijd; `--force` schrijft hem opnieuw. Een wedstrijd die eerder met `--loose` is omgezet, telt ook als klaar.
