---
title: "Ein skrá fyrir hvern leik"
nav_order: 10
lang: "is"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Ein skrá fyrir hvern leik (`<match>.3dheat`) {#one-file-a-match-matchdheat}

Sjálfgefið pakkar `demos` hverjum leik í eina skrá, `out/<map>/<match>.3dheat`:
hitakortstöfluna, leikjaskjalið og hliðarskrárnar fjórar saman - einn
leikur, ein skrá, til að afrita, geyma eða deila. Þetta er gámasnið
3DHeat-skoðarans, skilgreint í skjölum skoðarans:
[Ein skrá fyrir hvern leik (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([frumkóði](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kóði: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Skref fyrir skref {#step-by-step}

1. Umbreyttu eins og venjulega; ekkert þarf að stilla:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Hver leikur er ein skrá í möppu síns korts:

   ![demos on a synthetic demo](../assets/img/demos-run.svg)

3. Opnaðu hana í skoðaranum (Hitakorts- eða Leiks-flipinn), eða lestu hana sjálf(ur): hún er
   venjuleg ZIP-skrá.

   ![inside a .3dheat container](../assets/img/container-members.svg)

Til að geyma aðskildu skrárnar í staðinn - fyrir verkfæri sem vilja Parquet-skrá á
diski - bættu við `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Hvað er inni {#what-is-inside}

ZIP-skrá þar sem fyrsti hlutinn er `manifest.json`, síðan hinir hlutarnir. Parquet-hlutar
eru *stored* (Parquet er þegar þjappað, og stored hluti er eitt bætasvið sem lesari getur notað á
staðnum); JSON-hlutar eru þjappaðir með deflate.

| Hlutverk | Hluti | Hvað |
|---|---|---|
| `table` | `<match>.parquet` | [Hitakortstaflan](output-table.md) (skema `heat3d-table`) |
| `match` | `<match>.match.json` | [Leikjaskjalið](output-match-json.md) (skema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | hver leikatburður sem þáttarinn les, heill |
| `props` | `<match>.props.parquet` | hver eiginleikabreyting sem þáttarinn les |
| `strings` | `<match>.strings.parquet` | hver færsla strengjataflna |
| `packets` | `<match>.packets.parquet` | hver annar rammi og netskilaboð, heil |

Manifestið nefnir sniðið og útgáfu, leikinn (`cs2`), upprunann
(`demo`), breytinn og útgáfu hans, leikinn, kortið, hvenær það var
skrifað, `roles`-kort frá hlutverki til hluta, og fyrir hvern hluta gerð hans, 
þjöppun, stærð, SHA-256, fjölda raða og, þar sem hann hefur það, skema hans. Á
gervi-demo-skrá prófananna (stytt):

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

## Að lesa einn án skoðarans {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` les leikjaskjalið beint úr gámnum (eða úr lausri
`.match.json`).

## Að sleppa og endurskrifa {#skipping-and-rewriting}

Gámur er skrifaður heill eða alls ekki, svo `.3dheat` undir `--out`
telst leikur búinn; `--force` skrifar hann aftur. Leikur umbreyttur áður með
`--loose` telst líka búinn.
