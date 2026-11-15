---
title: One file a match
nav_order: 10
---

# One file a match (`<match>.3dheat`)

By default `demos` packs each match into one file, `out/<map>/<match>.3dheat`:
the heatmap table, the match document and the four sidecars together - one
match, one file, to copy, keep or share. It is the 3DHeat viewer's container
format, specified in the viewer's documentation:
[One file a match (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([source](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Code: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Step by step

1. Convert as usual; nothing to set:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Each match is one file in its map's folder:

   ![demos on a synthetic demo](assets/img/demos-run.svg)

3. Open it in the viewer (Heatmap tab or Match tab), or read it yourself: it is
   an ordinary ZIP.

   ![inside a .3dheat container](assets/img/container-members.svg)

To keep the separate files instead - for tools that want a Parquet file on
disk - add `--loose`:

![demos --loose](assets/img/demos-loose.svg)

## What is inside

A ZIP whose first member is `manifest.json`, then the members. Parquet members
are *stored* (Parquet is compressed already, and a stored member is one byte
range a reader can use in place); JSON members are deflated.

| Role | Member | What |
|---|---|---|
| `table` | `<match>.parquet` | [The heatmap table](output-table.md) (schema `heat3d-table`) |
| `match` | `<match>.match.json` | [The match document](output-match-json.md) (schema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | every game event the parser reads, whole |
| `props` | `<match>.props.parquet` | every property change the parser reads |
| `strings` | `<match>.strings.parquet` | every string table entry |
| `packets` | `<match>.packets.parquet` | every other frame and network message, whole |

The manifest names the format and version, the game (`cs2`), the source
(`demo`), the converter and its version, the match, the map, when it was
written, a `roles` map from role to member, and per member its media type,
compression, size, SHA-256, row count and, where it has one, its schema. On
the synthetic demo of the tests (abridged):

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

## Reading one without the viewer

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` reads the match document straight from the container (or from a
loose `.match.json`).

## Skipping and rewriting

A container is written whole or not at all, so a `.3dheat` under `--out`
counts as a match done; `--force` rewrites it. A match converted earlier with
`--loose` counts as done too.
