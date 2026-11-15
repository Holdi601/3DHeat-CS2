---
title: "Jedna datoteka po meču"
nav_order: 10
lang: "hr"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Jedna datoteka po meču (`<meč>.3dheat`) {#one-file-a-match-3dheat}

Prema zadanom `demos` pakira svaki meč u jednu datoteku, `out/<karta>/<meč>.3dheat`: toplinska tablica, dokument meča i četiri prateće datoteke zajedno - jedan meč, jedna datoteka, za kopiranje, čuvanje ili dijeljenje. To je format spremnika preglednika 3DHeat, opisan u dokumentaciji preglednika:
[Jedna datoteka po meču (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([izvor](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kod: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Korak po korak {#step-by-step}

1. Pretvorite kao i inače; ništa se ne postavlja:

   ```bash
   python -m heat3d_cs2 demos <demo datoteke ili mape> -o out
   ```

2. Svaki meč je jedna datoteka u mapi svoje karte:

   ![demos na sintetičkoj demo snimci](../assets/img/demos-run.svg)

3. Otvorite je u pregledniku (karticu Toplinska karta ili Meč), ili je sami pročitajte: obična je ZIP datoteka.

   ![unutrašnjost .3dheat spremnika](../assets/img/container-members.svg)

Ako umjesto toga želite zadržati zasebne datoteke - za alate koji žele Parquet datoteku na disku - dodajte `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Što je unutra {#what-is-inside}

ZIP čiji je prvi član `manifest.json`, pa ostali članovi. Parquet članovi su *pohranjeni* (Parquet je već komprimiran, a pohranjen član je jedan neprekinuti niz bajtova kojim čitatelj može izravno raditi); JSON članovi su deflate-komprimirani.

| Uloga | Član | Što |
|---|---|---|
| `table` | `<meč>.parquet` | [Toplinska tablica](output-table.md) (shema `heat3d-table`) |
| `match` | `<meč>.match.json` | [Dokument meča](output-match-json.md) (shema `heat3d-cs2-match`) |
| `events` | `<meč>.events.parquet` | svaki događaj igre koji parser čita, cijel |
| `props` | `<meč>.props.parquet` | svaka promjena svojstva koju parser čita |
| `strings` | `<meč>.strings.parquet` | svaki unos tablice nizova |
| `packets` | `<meč>.packets.parquet` | svaki drugi okvir i mrežna poruka, cijeli |

Manifest imenuje format i verziju, igru (`cs2`), izvor (`demo`), pretvarač i njegovu verziju, meč, kartu, vrijeme zapisa, `roles` kartu od uloge do člana, i za svakog člana njegov medijski tip, kompresiju, veličinu, SHA-256, broj redaka i, gdje ga ima, shemu. Na sintetičkoj demo snimci iz testova (skraćeno):

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

## Čitanje bez preglednika {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` čita dokument meča izravno iz spremnika (ili iz samostalnog `.match.json`).

## Preskakanje i ponovno pisanje {#skipping-and-rewriting}

Spremnik se piše cijel ili nimalo, pa se `.3dheat` pod `--out` računa kao gotov meč; `--force` ga ponovno piše. Meč pretvoren ranije s `--loose` također se računa kao gotov.
