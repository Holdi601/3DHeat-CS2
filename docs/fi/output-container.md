---
title: "Yksi tiedosto per ottelu (`<match>.3dheat`)"
nav_order: 10
lang: "fi"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Yksi tiedosto per ottelu (`<match>.3dheat`) {#one-file-a-match-3dheat}

Oletuksena `demos` pakkaa kunkin ottelun yhteen tiedostoon, `out/<map>/<match>.3dheat`:
lämpökarttataulukko, ottelun asiakirja ja neljä sivutiedostoa yhdessä - yksi ottelu,
yksi tiedosto, kopioitavaksi, säilytettäväksi tai jaettavaksi. Se on 3DHeat-katselimen
säilömuoto, joka on määritelty katselimen dokumentaatiossa:
[Yksi tiedosto per ottelu (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([lähde](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Koodi: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Vaihe vaiheelta {#step-by-step}

1. Muunna kuten tavallisesti; mitään ei tarvitse asettaa:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Jokainen ottelu on yksi tiedosto sen kartan kansiossa:

   ![demot synteettisellä demolla](../assets/img/demos-run.svg)

3. Avaa se katselimessa (**Lämpökartta**-välilehti tai **Ottelu**-välilehti), tai lue se itse:
   se on tavallinen ZIP.

   ![.3dheat-säilön sisältö](../assets/img/container-members.svg)

Jos haluat pitää erilliset tiedostot - työkaluille, jotka haluavat Parquet-tiedoston
levyllä - lisää `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Mitä sen sisällä on {#what-is-inside}

ZIP, jonka ensimmäinen jäsen on `manifest.json`, sitten muut jäsenet. Parquet-jäsenet
ovat *tallennettuja* (Parquet on jo pakattu, ja tallennettu jäsen on yksi tavualue, jonka
lukija voi käyttää paikallaan); JSON-jäsenet ovat deflate-pakattuja.

| Rooli | Jäsen | Mitä |
|---|---|---|
| `table` | `<match>.parquet` | [Lämpökarttataulukko](output-table.md) (skeema `heat3d-table`) |
| `match` | `<match>.match.json` | [Ottelun asiakirja](output-match-json.md) (skeema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | jokainen pelitapahtuma, jonka jäsentäjä lukee, kokonaisena |
| `props` | `<match>.props.parquet` | jokainen ominaisuuden muutos, jonka jäsentäjä lukee |
| `strings` | `<match>.strings.parquet` | jokainen merkkijonotaulun merkintä |
| `packets` | `<match>.packets.parquet` | jokainen muu kehys ja verkkoviesti, kokonaisena |

Manifesti kertoo muodon ja version, pelin (`cs2`), lähteen (`demo`), muuntajan ja sen
version, ottelun, kartan, kirjoitusajan, `roles`-kartan roolista jäseneen, ja jokaisen
jäsenen median tyypin, pakkauksen, koon, SHA-256:n, rivimäärän ja skeeman, jos sellainen
on. Testien synteettisessä demossa (lyhennettynä):

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

## Lukeminen ilman katselinta {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` lukee ottelun asiakirjan suoraan säilöstä (tai erillisestä `.match.json`-tiedostosta).

## Ohittaminen ja uudelleenkirjoittaminen {#skipping-and-rewriting}

Säiliö kirjoitetaan kokonaan tai ei lainkaan, joten `--out`-kansion alla oleva `.3dheat` lasketaan
tehdyksi otteluksi; `--force` kirjoittaa sen uudelleen. Ottelu, joka muunnettiin aiemmin
`--loose`-valinnalla, lasketaan myös tehdyksi.
