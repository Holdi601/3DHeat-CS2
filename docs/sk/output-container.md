---
title: Jeden súbor na zápas
nav_order: 10
lang: "sk"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Jeden súbor na zápas (`<match>.3dheat`) {#one-file-a-match-3dheat}

Predvolene `demos` zabalí každý zápas do jedného súboru, `out/<map>/<match>.3dheat`:
tabuľku heatmapy, dokument zápasu a štyri pomocné súbory spolu - jeden zápas, jeden
súbor, ktorý sa dá skopírovať, uschovať alebo zdieľať. Je to kontajnerový formát
prehliadača 3DHeat, popísaný v jeho dokumentácii:
[Jeden súbor na zápas (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([zdroj](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kód: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Krok za krokom {#step-by-step}

1. Konvertujte ako obvykle; nič sa nenastavuje:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Každý zápas je jeden súbor vo svojom priečinku mapy:

   ![demos na syntetickom deme](../assets/img/demos-run.svg)

3. Otvorte ho v prehliadači (karta Heatmapa alebo karta Zápas), alebo si ho prečítajte
   sami: je to obyčajný ZIP.

   ![vnútri kontajnera .3dheat](../assets/img/container-members.svg)

Ak chcete namiesto toho ponechať oddelené súbory - pre nástroje, ktoré chcú
súbor Parquet na disku - pridajte `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Čo je vo vnútri {#what-is-inside}

ZIP, ktorého prvý člen je `manifest.json`, potom ostatné členy. Členy Parquet sú
*uložené bez kompresie* (Parquet je už komprimovaný a uložený člen je jeden
bajtový rozsah, ktorý čitateľ môže použiť na mieste); členy JSON sú deflate.

| Rola | Člen | Čo |
|---|---|---|
| `table` | `<match>.parquet` | [Tabuľka heatmapy](output-table.md) (schéma `heat3d-table`) |
| `match` | `<match>.match.json` | [Dokument zápasu](output-match-json.md) (schéma `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | každá herná udalosť, ktorú parser číta, celá |
| `props` | `<match>.props.parquet` | každá zmena vlastnosti, ktorú parser číta |
| `strings` | `<match>.strings.parquet` | každý záznam tabuľky reťazcov |
| `packets` | `<match>.packets.parquet` | každý iný snímok a sieťová správa, celé |

Manifest uvádza formát a verziu, hru (`cs2`), zdroj (`demo`), konvertor a jeho
verziu, zápas, mapu, kedy bol zapísaný, mapu `roles` z roly na člena, a pre každý
člen jeho typ média, kompresiu, veľkosť, SHA-256, počet riadkov a - ak ho má -
schému. Na syntetickom deme z testov (skrátené):

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

## Čítanie bez prehliadača {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` číta dokument zápasu priamo z kontajnera (alebo zo samostatného
`.match.json`).

## Preskakovanie a prepisovanie {#skipping-and-rewriting}

Kontajner sa zapíše celý, alebo vôbec, takže `.3dheat` pod `--out` sa počíta ako
hotový zápas; `--force` ho prepíše. Zápas skôr prevedený s `--loose` sa tiež
počíta ako hotový.
