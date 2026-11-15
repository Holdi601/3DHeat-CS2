---
title: Jedna datoteka po meču
nav_order: 10
lang: "bs"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Jedna datoteka po meču (`<match>.3dheat`) {#one-file-a-match-3dheat}

Zadano `demos` pakuje svaki meč u jednu datoteku, `out/<map>/<match>.3dheat`:
tabelu toplotne mape, dokument meča i četiri pomoćne datoteke zajedno - jedan
meč, jedna datoteka, za kopiranje, čuvanje ili dijeljenje. To je format kontejnera
preglednika 3DHeat, određen u dokumentaciji preglednika:
[Jedna datoteka po meču (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([izvor](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kod: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Korak po korak {#step-by-step}

1. Pretvorite kao obično; ništa se ne postavlja:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Svaki meč je jedna datoteka u folderu svoje mape:

   ![demos na sintetičkom demou](../assets/img/demos-run.svg)

3. Otvorite je u pregledniku (kartica Toplotna mapa ili kartica Meč), ili je čitajte sami: to je
   obični ZIP.

   ![unutar .3dheat kontejnera](../assets/img/container-members.svg)

Da zadržite odvojene datoteke - za alate koji žele Parquet datoteku
na disku - dodajte `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Šta je unutra {#what-is-inside}

ZIP čiji je prvi član `manifest.json`, zatim članovi. Parquet članovi
su *stored* (Parquet je već komprimiran, a stored član je jedan raspon bajtova koji čitač može koristiti na mjestu); JSON članovi su deflated.

| Uloga | Član | Šta |
|---|---|---|
| `table` | `<match>.parquet` | [Tabela toplotne mape](output-table.md) (shema `heat3d-table`) |
| `match` | `<match>.match.json` | [Dokument meča](output-match-json.md) (shema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | svaki događaj igre koji parser čita, cijeli |
| `props` | `<match>.props.parquet` | svaka promjena svojstva koju parser čita |
| `strings` | `<match>.strings.parquet` | svaki unos tabele stringova |
| `packets` | `<match>.packets.parquet` | svaki drugi okvir i mrežna poruka, cijeli |

Manifest navodi format i verziju, igru (`cs2`), izvor
(`demo`), konverter i njegovu verziju, meč, mapu, kad je
napisan, mapu `roles` od uloge do člana, i po članu njegov tip medija,
kompresiju, veličinu, SHA-256, broj redova i, gdje ga ima, njegovu shemu. Na
sintetičkom demou iz testova (skraćeno):

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

`scoreboard` čita dokument meča direktno iz kontejnera (ili iz
slobodnog `.match.json`).

## Preskakanje i prepisivanje {#skipping-and-rewriting}

Kontejner se piše cijeli ili nikako, pa se `.3dheat` pod `--out`
računa kao gotov meč; `--force` ga prepisuje. Meč pretvoren ranije s
`--loose` također se računa kao gotov.
