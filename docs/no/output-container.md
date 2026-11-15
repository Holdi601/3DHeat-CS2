---
title: "En fil per kamp"
nav_order: 10
lang: "no"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# En fil per kamp (`<kamp>.3dheat`) {#one-file-a-match-3dheat}

Som standard pakker `demos` hver kamp i én fil, `out/<map>/<kamp>.3dheat`: varmekarttabellen,
kampdokumentet og de fire sidefilene sammen - én kamp, én fil, å kopiere, beholde eller dele.
Det er 3DHeat-visningens beholderformat, spesifisert i visningens dokumentasjon:
[En fil per kamp (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([kilde](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kode: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Steg for steg {#step-by-step}

1. Konverter som vanlig; ingenting å sette:

   ```bash
   python -m heat3d_cs2 demos <demofiler eller mapper> -o out
   ```

2. Hver kamp er én fil i kartets mappe:

   ![demos på en syntetisk demo](../assets/img/demos-run.svg)

3. Åpne den i visningen (**Varmekart**-fanen eller **Kamp**-fanen), eller les den selv: den er en
   vanlig ZIP-fil.

   ![inni en .3dheat-beholder](../assets/img/container-members.svg)

Vil du i stedet beholde de separate filene - for verktøy som vil ha en Parquet-fil på disken - legg
til `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Hva som ligger inni {#what-is-inside}

En ZIP der første element er `manifest.json`, deretter elementene. Parquet-elementer er *lagret*
(Parquet er allerede komprimert, og et lagret element er ett bytesegment en leser kan bruke der det
står); JSON-elementer er komprimert med deflate.

| Rolle | Element | Hva |
|---|---|---|
| `table` | `<kamp>.parquet` | [Varmekarttabellen](output-table.md) (skjema `heat3d-table`) |
| `match` | `<kamp>.match.json` | [Kampdokumentet](output-match-json.md) (skjema `heat3d-cs2-match`) |
| `events` | `<kamp>.events.parquet` | hver spillhendelse parseren leser, helt |
| `props` | `<kamp>.props.parquet` | hver egenskapsendring parseren leser |
| `strings` | `<kamp>.strings.parquet` | hver streng i strengtabellen |
| `packets` | `<kamp>.packets.parquet` | hver annen ramme og nettverksmelding, helt |

Manifestet nevner formatet og versjonen, spillet (`cs2`), kilden (`demo`), konverteren og dens
versjon, kampen, kartet, når den ble skrevet, et `roles`-kart fra rolle til element, og for hvert
element dets medietype, komprimering, størrelse, SHA-256, antall rader og, der det finnes, skjemaet.
På den syntetiske demoen fra testene (forkortet):

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

## Å lese en uten visningen {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` leser kampdokumentet rett fra beholderen (eller fra en løs `.match.json`).

## Hoppe over og skrive om {#skipping-and-rewriting}

En beholder skrives enten helt eller ikke i det hele, så en `.3dheat` under `--out` teller som en
ferdig kamp; `--force` skriver den på nytt. En kamp konvertert tidligere med `--loose` teller også
som ferdig.
