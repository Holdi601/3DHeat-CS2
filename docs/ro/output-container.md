---
title: Un fișier pentru fiecare meci
nav_order: 10
lang: "ro"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Un fișier pentru fiecare meci (`<meci>.3dheat`) {#one-file-a-match-3dheat}

În mod implicit, `demos` împachetează fiecare meci într-un singur fișier,
`out/<map>/<match>.3dheat`: tabelul hărții termice, documentul meciului și cele patru
fișiere anexe împreună - un meci, un fișier, de copiat, de păstrat sau de trimis. Este
formatul de container al vizualizatorului 3DHeat, specificat în documentația vizualizatorului:
[Un fișier pentru fiecare meci (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([sursa](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Cod: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Pas cu pas {#step-by-step}

1. Convertește ca de obicei; nu trebuie setat nimic:

   ```bash
   python -m heat3d_cs2 demos <fișiere demo sau foldere> -o out
   ```

2. Fiecare meci este un fișier în folderul hărții sale:

   ![demos pe un demo sintetic](../assets/img/demos-run.svg)

3. Deschide-l în vizualizator (fila Hartă termică sau fila Meci), sau citește-l tu: este un
   ZIP obișnuit.

   ![în interiorul unui container .3dheat](../assets/img/container-members.svg)

Ca să păstrezi fișierele separate - pentru instrumente care vor un fișier Parquet pe disc -
adaugă `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Ce este înăuntru {#what-is-inside}

Un ZIP al cărui prim membru este `manifest.json`, apoi membrii. Membrii Parquet sunt
*stocați* (Parquet este deja comprimat, iar un membru stocat este un interval de octeți pe
care un cititor îl poate folosi direct); membrii JSON sunt comprimați cu deflate.

| Rol | Membru | Ce este |
|---|---|---|
| `table` | `<match>.parquet` | [Tabelul hărții termice](output-table.md) (schema `heat3d-table`) |
| `match` | `<match>.match.json` | [Documentul meciului](output-match-json.md) (schema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | fiecare eveniment de joc citit de parser, întreg |
| `props` | `<match>.props.parquet` | fiecare schimbare de proprietate citită de parser |
| `strings` | `<match>.strings.parquet` | fiecare intrare din tabelele de șiruri |
| `packets` | `<match>.packets.parquet` | fiecare alt cadru și mesaj de rețea, întreg |

Manifestul spune formatul și versiunea, jocul (`cs2`), sursa (`demo`), convertorul și
versiunea sa, meciul, harta, când a fost scris, o hartă `roles` de la rol la membru și, pentru
fiecare membru, tipul său media, compresia, dimensiunea, SHA-256, numărul de rânduri și, dacă
are una, schema sa. Pe demo-ul sintetic din teste (prescurtat):

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

## Citirea fără vizualizator {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` citește documentul meciului direct din container (sau dintr-un `.match.json`
separat).

## Omiterea și rescrierea {#skipping-and-rewriting}

Un container se scrie întreg sau deloc, deci un `.3dheat` aflat sub `--out` contează ca meci
terminat; `--force` îl rescrie. Un meci convertit mai devreme cu `--loose` contează și el ca
terminat.
