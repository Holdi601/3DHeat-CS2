---
title: "Един файл за мач"
nav_order: 10
lang: "bg"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Един файл за мач (`<match>.3dheat`) {#one-file-a-match-3dheat}

По подразбиране `demos` събира всеки мач в един файл, `out/<map>/<match>.3dheat`:
топлинната таблица, документът на мача и четирите помощни файла заедно - един мач, един файл, за да се копира, пази или споделя. Това е форматът на контейнера на визуализатора 3DHeat, описан в документацията на визуализатора:
[Един файл за мач (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([изходен код](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Код: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Стъпка по стъпка {#step-by-step}

1. Конвертирайте както обикновено; нищо за настройка:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Всеки мач е един файл в папката на картата си:

   ![demos на синтетично демо](../assets/img/demos-run.svg)

3. Отворете го във визуализатора (раздела Топлинна карта или раздела Мач) или го прочетете сами: това е обикновен ZIP.

   ![вътрешността на контейнер .3dheat](../assets/img/container-members.svg)

За да запазите отделните файлове вместо това - за инструменти, които искат Parquet файл на диска - добавете `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Какво има вътре {#what-is-inside}

ZIP, чийто първи елемент е `manifest.json`, после останалите елементи. Елементите Parquet се пазят *без компресия* (Parquet е вече компресиран и записаният елемент е един байтов диапазон, който четецът може да ползва на мястото му); JSON елементите се компресират с deflate.

| Роля | Елемент | Какво е |
|---|---|---|
| `table` | `<match>.parquet` | [Топлинната таблица](output-table.md) (схема `heat3d-table`) |
| `match` | `<match>.match.json` | [Документът на мача](output-match-json.md) (схема `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | всяко игрово събитие, което парсерът чете, цяло |
| `props` | `<match>.props.parquet` | всяка промяна на свойство, която парсерът чете |
| `strings` | `<match>.strings.parquet` | всеки запис в таблицата на низовете |
| `packets` | `<match>.packets.parquet` | всеки друг кадър и мрежово съобщение, цяло |

Манифестът назовава формата и версията, играта (`cs2`), източника (`demo`), конвертора и версията му, мача, картата, кога е записан, карта `roles` от роля към елемент, и за всеки елемент - типа на медията, компресията, размера, SHA-256, броя редове и, когато има такава, схемата. На синтетичното демо от тестовете (съкратено):

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

## Четене без визуализатора {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` чете документа на мача direktno от контейнера (или от отделен `.match.json`).

## Пропускане и презаписване {#skipping-and-rewriting}

Контейнерът се записва изцяло или изобщо не се записва, така че `.3dheat` под `--out` се брои като готов мач; `--force` го презаписва. Мач, превърнат по-рано с `--loose`, също се брои като готов.
