---
title: "Ena datoteka na tekmo"
nav_order: 10
lang: "sl"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Ena datoteka na tekmo (`<tekma>.3dheat`) {#one-file-a-match-match3dheat}

Privzeto `demos` spakira vsako tekmo v eno datoteko, `out/<karta>/<tekma>.3dheat`: toplotno tabelo, dokument tekme in
štiri spremljevalne datoteke skupaj – ena tekma, ena datoteka, za kopiranje, hranjenje ali deljenje. To je vsebniška
oblika pregledovalnika 3DHeat, opisana v njegovi dokumentaciji:
[Ena datoteka na tekmo (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([vir](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Koda: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Korak za korakom {#step-by-step}

1. Pretvorite kot običajno; nič ni treba nastaviti:

   ```bash
   python -m heat3d_cs2 demos <datoteke demo ali mape> -o out
   ```

2. Vsaka tekma je ena datoteka v mapi svoje karte:

   ![demos na sintetičnem demu](../assets/img/demos-run.svg)

3. Odprite jo v pregledovalniku (zavihek Toplotni zemljevid ali Tekma) ali jo preberite sam: je navaden ZIP.

   ![znotraj vsebnika .3dheat](../assets/img/container-members.svg)

Če namesto tega želite ohraniti ločene datoteke – za orodja, ki hočejo datoteko Parquet na disku – dodajte `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Kaj je znotraj {#what-is-inside}

ZIP, katerega prvi člen je `manifest.json`, nato členi. Členi Parquet so *shranjeni* brez stiskanja (Parquet je že
stisnjen, shranjen člen pa je en bajtni razpon, ki ga bralnik lahko uporabi na mestu); členi JSON so stisnjeni z deflate.

| Vloga | Člen | Kaj |
|---|---|---|
| `table` | `<tekma>.parquet` | [Toplotna tabela](output-table.md) (shema `heat3d-table`) |
| `match` | `<tekma>.match.json` | [Dokument tekme](output-match-json.md) (shema `heat3d-cs2-match`) |
| `events` | `<tekma>.events.parquet` | vsak dogodek igre, ki ga razčlenjevalnik prebere, v celoti |
| `props` | `<tekma>.props.parquet` | vsaka sprememba lastnosti, ki jo razčlenjevalnik prebere |
| `strings` | `<tekma>.strings.parquet` | vsak vnos tabele nizov |
| `packets` | `<tekma>.packets.parquet` | vsak drug okvir in omrežno sporočilo, v celoti |

Manifest navaja obliko in njeno različico, igro (`cs2`), vir (`demo`), pretvornik in njegovo različico, tekmo, karto,
kdaj je bil zapisan, zemljevid `roles` od vloge do člena in za vsak člen njegov medijski tip, stiskanje, velikost,
SHA-256, število vrstic in, kjer jo ima, shemo. Na sintetičnem demu iz testov (skrajšano):

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

## Branje brez pregledovalnika {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` prebere dokument tekme naravnost iz vsebnika (ali iz samostojne `.match.json`).

## Preskakovanje in prepisovanje {#skipping-and-rewriting}

Vsebnik se zapiše celoten ali pa nič, zato se `.3dheat` pod `--out` šteje kot opravljena tekma; `--force` ga prepiše.
Tekma, prej pretvorjena z `--loose`, se prav tako šteje kot opravljena.
