---
title: "Једна датотека по мечу"
nav_order: 10
lang: "sr"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Једна датотека по мечу (`<match>.3dheat`) {#one-file-a-match-3dheat}

Подразумевано `demos` пакује сваки меч у једну датотеку, `out/<map>/<match>.3dheat`: табелу топлотне мапе, документ меча и четири пратеће датотеке заједно - један меч, један фајл, за копирање, чување или дељење. То је формат контејнера прегледача 3DHeat, описан у документацији прегледача: [Једна датотека по мечу (.3dheat)](https://holdi601.github.io/3DHeat/container.html) ([извор](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)). Код: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Корак по корак {#step-by-step}

1. Претворите као обично; ништа не треба подешавати:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Сваки меч је један фајл у фолдеру своје мапе:

   ![demos над вештачким демом](../assets/img/demos-run.svg)

3. Отворите га у прегледачу (картица Топлотна мапа или картица Меч), или га сами прочитајте: то је обичан ZIP.

   ![унутрашњост .3dheat контејнера](../assets/img/container-members.svg)

Ако уместо тога желите одвојене датотеке - за алате који хоће Parquet фајл на диску - додајте `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Шта је унутра {#what-is-inside}

ZIP чији је први члан `manifest.json`, па остали чланови. Parquet чланови се *чувају* (Parquet је већ компресован, а сачуван члан је један опсег бајтова који читач може да користи на месту); JSON чланови се компресују deflate-ом.

| Улога | Члан | Шта |
|---|---|---|
| `table` | `<match>.parquet` | [Табела топлотне мапе](output-table.md) (шема `heat3d-table`) |
| `match` | `<match>.match.json` | [Документ меча](output-match-json.md) (шема `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | сваки догађај игре који парсер чита, цео |
| `props` | `<match>.props.parquet` | свака промена својства коју парсер чита |
| `strings` | `<match>.strings.parquet` | сваки унос табеле стрингова |
| `packets` | `<match>.packets.parquet` | сваки други оквир и мрежна порука, цели |

Манифест наводи формат и верзију, игру (`cs2`), извор (`demo`), конвертор и његову верзију, меч, мапу, кад је писан, мапу `roles` од улоге до члана, и за сваки члан његов медијски тип, компресију, величину, SHA-256, број редова и, где га има, шему. На синтетичком демоу из тестова (скраћено):

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

## Читање без прегледача {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` чита документ меча право из контејнера (или из самосталног `.match.json`-а).

## Прескакање и поновно писање {#skipping-and-rewriting}

Контејнер се пише целиком или никако, па се `.3dheat` испод `--out` рачуна као урађен меч; `--force` га пише поново. Меч претворен раније с `--loose` такође се рачуна као урађен.
