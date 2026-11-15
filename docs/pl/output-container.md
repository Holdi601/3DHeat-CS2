---
title: Jeden plik na mecz
nav_order: 10
lang: "pl"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Jeden plik na mecz (`<mecz>.3dheat`) {#one-file-a-match-3dheat}

Domyślnie `demos` pakuje każdy mecz w jeden plik, `out/<mapa>/<mecz>.3dheat`: tabelę mapy cieplnej, dokument meczu i cztery pliki pomocnicze razem - jeden mecz, jeden plik, do skopiowania, zachowania albo udostępnienia. To format kontenera przeglądarki 3DHeat, opisany w jej dokumentacji:
[Jeden plik na mecz (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([źródło](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kod: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Krok po kroku {#step-by-step}

1. Konwertuj jak zwykle; nic nie trzeba ustawiać:

   ```bash
   python -m heat3d_cs2 demos <pliki dem albo foldery> -o out
   ```

2. Każdy mecz to jeden plik w folderze swojej mapy:

   ![demos na syntetycznym demie](../assets/img/demos-run.svg)

3. Otwórz go w przeglądarce (karta Mapa cieplna albo Mecz) albo przeczytaj samodzielnie: to zwykłe archiwum ZIP.

   ![wnętrze kontenera .3dheat](../assets/img/container-members.svg)

Aby zamiast tego zachować osobne pliki - dla narzędzi, które chcą mieć plik Parquet na dysku - dodaj `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Co jest w środku {#what-is-inside}

Archiwum ZIP, którego pierwszym elementem jest `manifest.json`, a potem elementy. Elementy Parquet są *zapisane bez kompresji* (Parquet jest już skompresowany, a zapisany element to jeden zakres bajtów, z którego czytnik może korzystać na miejscu); elementy JSON są kompresowane (deflate).

| Rola | Element | Co zawiera |
|---|---|---|
| `table` | `<mecz>.parquet` | [Tabela mapy cieplnej](output-table.md) (schemat `heat3d-table`) |
| `match` | `<mecz>.match.json` | [Dokument meczu](output-match-json.md) (schemat `heat3d-cs2-match`) |
| `events` | `<mecz>.events.parquet` | każde zdarzenie gry, które czyta parser, w całości |
| `props` | `<mecz>.props.parquet` | każda zmiana właściwości, którą czyta parser |
| `strings` | `<mecz>.strings.parquet` | każdy wpis tablicy łańcuchów |
| `packets` | `<mecz>.packets.parquet` | każda inna klatka i wiadomość sieciowa, w całości |

Manifest podaje format i wersję, grę (`cs2`), źródło (`demo`), konwerter i jego wersję, mecz, mapę, kiedy zapisano, mapę `roles` z roli na element, a dla każdego elementu jego typ mediów, kompresję, rozmiar, SHA-256, liczbę wierszy i - jeśli ma - schemat. Na syntetycznym demie z testów (skrócony):

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

## Czytanie bez przeglądarki {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` czyta dokument meczu wprost z kontenera (albo z luźnego `.match.json`).

## Pomijanie i przepisywanie {#skipping-and-rewriting}

Kontener jest zapisywany w całości albo wcale, więc `.3dheat` pod `--out` liczy się jako wykonany mecz; `--force` przepisuje go. Mecz wcześniej skonwertowany z `--loose` też liczy się jako wykonany.
