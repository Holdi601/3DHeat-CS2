---
title: "En fil per match"
nav_order: 10
lang: "sv"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# En fil per match (`<match>.3dheat`) {#one-file-a-match-3dheat}

Som standard packar `demos` varje match i en fil, `out/<karta>/<match>.3dheat`: värmekartetabellen,
matchdokumentet och de fyra sidofilerna tillsammans - en match, en fil, att kopiera, spara eller dela.
Det är 3DHeat-visarens behållarformat, specificerat i visarens dokumentation:
[En fil per match (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([källa](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kod: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Steg för steg {#step-by-step}

1. Konvertera som vanligt; inget att ställa in:

   ```bash
   python -m heat3d_cs2 demos <demofiler eller mappar> -o out
   ```

2. Varje match är en fil i sin kartas mapp:

   ![demos på en syntetisk demo](../assets/img/demos-run.svg)

3. Öppna den i visaren (fliken Värmekarta eller fliken Match), eller läs den själv: den är ett vanligt
   ZIP-arkiv.

   ![inuti en .3dheat-behållare](../assets/img/container-members.svg)

Vill du i stället behålla de separata filerna - för verktyg som vill ha en Parquet-fil på disken - lägg
till `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Vad som finns inuti {#what-is-inside}

Ett ZIP-arkiv vars första medlem är `manifest.json`, sedan medlemmarna. Parquet-medlemmar är *lagrade*
(Parquet är redan komprimerat, och en lagrad medlem är ett byteintervall en läsare kan använda på plats),
JSON-medlemmar är packade (deflate).

| Roll | Medlem | Vad |
|---|---|---|
| `table` | `<match>.parquet` | [Värmekartetabellen](output-table.md) (schema `heat3d-table`) |
| `match` | `<match>.match.json` | [Matchdokumentet](output-match-json.md) (schema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | varje spelhändelse parsern läser, hel |
| `props` | `<match>.props.parquet` | varje egenskapsändring parsern läser |
| `strings` | `<match>.strings.parquet` | varje post i strängtabellerna |
| `packets` | `<match>.packets.parquet` | varje annan bildruta och nätverksmeddelande, helt |

Manifestet anger format och version, spelet (`cs2`), källan (`demo`), konverteraren och dess version,
matchen, kartan, när den skrevs, en `roles`-karta från roll till medlem, och för varje medlem dess
mediatyp, komprimering, storlek, SHA-256, antal rader och, där den har ett, sitt schema. På den syntetiska
demon i testerna (förkortat):

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

## Läsa en utan visaren {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` läser matchdokumentet direkt ur behållaren (eller ur en lös `.match.json`).

## Hoppa över och skriva om {#skipping-and-rewriting}

En behållare skrivs helt eller inte alls, så en `.3dheat` under `--out` räknas som en match som är klar;
`--force` skriver om den. En match som tidigare konverterats med `--loose` räknas också som klar.
