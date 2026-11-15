---
title: "Една датотека по натпревар"
nav_order: 10
lang: "mk"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Една датотека по натпревар (`<match>.3dheat`) {#one-file-a-match-3dheat}

Стандардно `demos` го пакува секој натпревар во една датотека, `out/<map>/<match>.3dheat`:
табелата за топлинска мапа, документот на натпреварот и четирите придружни
датотеки заедно - еден натпревар, една датотека, за копирање, чување или споделување.
Тоа е форматот на контејнер на прегледувачот 3DHeat, специфициран во
документацијата на прегледувачот:
[Една датотека по натпревар (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([извор](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Код: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Чекор по чекор {#step-by-step}

1. Претворете како обично; ништо не треба да се подеси:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Секој натпревар е една датотека во папката на неговата мапа:

   ![demos на синтетичко демо](../assets/img/demos-run.svg)

3. Отворете ја во прегледувачот (таб Топлинска мапа или таб Натпревар), или
   прочитајте ја сами: тоа е обичен ZIP.

   ![внатре во контејнер .3dheat](../assets/img/container-members.svg)

За да ги задржите одделните датотеки - за алатки што сакаат Parquet датотека на
дискот - додајте `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Што има внатре {#what-is-inside}

ZIP чиј прв член е `manifest.json`, потоа членовите. Parquet членовите се
*складирани* (stored; Parquet е веќе компресиран, а складиран член е еден
опсег на бајти што читачот може да го користи на место); JSON членовите се
deflate-компресирани.

| Улога | Член | Што |
|---|---|---|
| `table` | `<match>.parquet` | [Табелата за топлинска мапа](output-table.md) (шема `heat3d-table`) |
| `match` | `<match>.match.json` | [Документот на натпреварот](output-match-json.md) (шема `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | секој настан на играта што го чита парсерот, цел |
| `props` | `<match>.props.parquet` | секоја промена на својство што ја чита парсерот |
| `strings` | `<match>.strings.parquet` | секој запис од табелите со низи |
| `packets` | `<match>.packets.parquet` | секоја друга рамка и мрежна порака, цела |

Манифестот го именува форматот и верзијата, играта (`cs2`), изворот (`demo`),
конверторот и неговата верзија, натпреварот, мапата, кога е запишан, мапа `roles`
од улога до член, и по член неговиот тип на медиум, компресија, големина,
SHA-256, број на редови и, каде што има, неговата шема. На синтетичкото демо
од тестовите (скратено):

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

## Читање без прегледувачот {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` го чита документот на натпреварот директно од контејнерот (или од
одделен `.match.json`).

## Прескокнување и препишување {#skipping-and-rewriting}

Контејнерот се пишува цел или воопшто не, па `.3dheat` под `--out` се смета за
завршен натпревар; `--force` го препишува. Натпревар претворен претходно со `--loose` се
смета за завршен исто така.
