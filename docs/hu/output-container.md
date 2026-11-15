---
title: "Egy fájl meccsenként"
nav_order: 10
lang: "hu"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Egy fájl meccsenként (`<match>.3dheat`) {#one-file-a-match-match3dheat}

Alapértelmezetten a `demos` meccsenként egy fájlba csomagol, `out/<map>/<match>.3dheat` néven: a hőtérképes táblázat, a
meccsdokumentum és a négy kísérőfájl együtt - egy meccs, egy fájl, amelyet másolhatsz, megtarthatsz vagy megoszthatsz. Ez a
3DHeat megjelenítő konténer-formátuma, amelyet a megjelenítő dokumentációja ír le:
[Egy fájl meccsenként (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([forrás](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kód: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Lépésről lépésre {#step-by-step}

1. Konvertálj a szokásos módon; nincs mit beállítani:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Minden meccs egy fájl a pályája mappájában:

   ![demók szintetikus demón](../assets/img/demos-run.svg)

3. Nyisd meg a megjelenítőben (a **Hőtérkép** fülön vagy a **Meccs** fülön), vagy olvasd el magad: ez egy közönséges ZIP.

   ![egy .3dheat konténer belseje](../assets/img/container-members.svg)

Ha ehelyett a külön fájlokat szeretnéd megtartani - olyan eszközökhöz, amelyek lemezen akarnak Parquet-fájlt -, add hozzá a
`--loose` kapcsolót:

![demos --loose](../assets/img/demos-loose.svg)

## Mi van benne {#what-is-inside}

Egy ZIP, amelynek első tagja a `manifest.json`, utána a többi tag. A Parquet-tagok *tárolva* (stored) vannak - a Parquet
már eleve tömörített, és egy tárolt tag egy bájttartomány, amelyet az olvasó helyben használhat -; a JSON-tagok
tömörítettek.

| Szerep | Tag | Mi |
|---|---|---|
| `table` | `<match>.parquet` | [A hőtérképes táblázat](output-table.md) (séma: `heat3d-table`) |
| `match` | `<match>.match.json` | [A meccsdokumentum](output-match-json.md) (séma: `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | minden játékesemény, amelyet a parser olvas, egészben |
| `props` | `<match>.props.parquet` | minden tulajdonságváltozás, amelyet a parser olvas |
| `strings` | `<match>.strings.parquet` | minden string-tábla bejegyzés |
| `packets` | `<match>.packets.parquet` | minden más képkocka és hálózati üzenet, egészben |

A manifest megnevezi a formátumot és a verziót, a játékot (`cs2`), a forrást (`demo`), a konvertálót és a verzióját, a
meccset, a pályát, azt, mikor íródott, egy `roles` leképezést a szerepről a tagra, és tagonként a médiatípusát, a
tömörítését, a méretét, az SHA-256-ot, a sorok számát, és ahol van, a sémáját. A teszt szintetikus demóján (rövidítve):

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

## Olvasás megjelenítő nélkül {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

A `scoreboard` a meccsdokumentumot közvetlenül a konténerből olvassa (vagy egy különálló `.match.json`-ből).

## Kihagyás és újraírás {#skipping-and-rewriting}

A konténer egészben íródik vagy egyáltalán nem, így az `--out` alatti `.3dheat` kész meccsnek számít; a `--force` újraírja.
Az a meccs, amelyet korábban `--loose`-zal konvertáltunk, szintén készként számít.
