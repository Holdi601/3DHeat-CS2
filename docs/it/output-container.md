---
title: "Un file per partita"
nav_order: 10
lang: "it"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Un file per partita (`<partita>.3dheat`) {#one-file-a-match-3dheat}

Per impostazione predefinita `demos` impacchetta ogni partita in un unico file, `out/<mappa>/<partita>.3dheat`: la tabella
della mappa di calore, il documento partita e i quattro file accessori insieme - una partita, un file, da copiare, conservare
o condividere. È il formato contenitore del visualizzatore di 3DHeat, descritto nella documentazione del visualizzatore:
[Un file per partita (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([sorgente](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Codice: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Passo dopo passo {#step-by-step}

1. Converti come al solito; non c'è nulla da impostare:

   ```bash
   python -m heat3d_cs2 demos <file demo o cartelle> -o out
   ```

2. Ogni partita è un file nella cartella della sua mappa:

   ![demos su un demo sintetico](../assets/img/demos-run.svg)

3. Aprilo nel visualizzatore (scheda Mappa di calore o scheda Partita), oppure leggilo da solo: è un normale ZIP.

   ![dentro un contenitore .3dheat](../assets/img/container-members.svg)

Per tenere invece i file separati - per gli strumenti che vogliono un file Parquet su disco - aggiungi `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Cosa contiene {#what-is-inside}

Uno ZIP il cui primo elemento è `manifest.json`, seguito dagli altri elementi. Gli elementi Parquet sono *memorizzati* senza
compressione (Parquet è già compresso, e un elemento memorizzato è un unico intervallo di byte che un lettore può usare sul
posto); gli elementi JSON sono compressi con deflate.

| Ruolo | Elemento | Cosa |
|---|---|---|
| `table` | `<partita>.parquet` | [La tabella della mappa di calore](output-table.md) (schema `heat3d-table`) |
| `match` | `<partita>.match.json` | [Il documento partita](output-match-json.md) (schema `heat3d-cs2-match`) |
| `events` | `<partita>.events.parquet` | ogni evento di gioco letto dal parser, intero |
| `props` | `<partita>.props.parquet` | ogni cambiamento di proprietà letto dal parser |
| `strings` | `<partita>.strings.parquet` | ogni voce della tabella delle stringhe |
| `packets` | `<partita>.packets.parquet` | ogni altro frame e messaggio di rete, interi |

Il manifest indica il formato e la sua versione, il gioco (`cs2`), la fonte (`demo`), il convertitore e la sua versione, la
partita, la mappa, quando è stato scritto, una mappa `roles` da ruolo a elemento, e per ogni elemento il suo tipo di media,
la compressione, la dimensione, lo SHA-256, il numero di righe e, dove ne ha uno, il suo schema. Sul demo sintetico dei test
(abbreviato):

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

## Leggerlo senza il visualizzatore {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` legge il documento partita direttamente dal contenitore (oppure da un `.match.json` separato).

## Saltare e riscrivere {#skipping-and-rewriting}

Un contenitore viene scritto per intero o per niente, quindi un `.3dheat` sotto `--out` conta come partita già fatta;
`--force` lo riscrive. Una partita convertita prima con `--loose` conta anche lei come fatta.
