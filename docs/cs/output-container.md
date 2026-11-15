---
title: Jeden soubor na zápas
nav_order: 10
lang: "cs"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Jeden soubor na zápas (`<zápas>.3dheat`) {#one-file-a-match-3dheat}

Ve výchozím nastavení `demos` sbalí každý zápas do jednoho souboru,
`out/<map>/<zápas>.3dheat`: teplotní tabulku, dokument zápasu a čtyři pomocné
soubory dohromady - jeden zápas, jeden soubor, který lze zkopírovat, uchovat
nebo sdílet. Je to kontejnerový formát prohlížeče 3DHeat, popsaný v jeho
dokumentaci:
[Jeden soubor na zápas (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([zdroj](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kód: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Krok za krokem {#step-by-step}

1. Převeďte jako obvykle; nic nenastavujte:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Každý zápas je jeden soubor ve složce své mapy:

   ![demos na syntetickém demu](../assets/img/demos-run.svg)

3. Otevřete ho v prohlížeči (karta Teplotní mapa nebo Zápas), nebo si ho
   přečtěte sami: je to obyčejný ZIP.

   ![uvnitř kontejneru .3dheat](../assets/img/container-members.svg)

Chcete-li místo toho ponechat samostatné soubory - pro nástroje, které chtějí
soubor Parquet na disku - přidejte `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Co je uvnitř {#what-is-inside}

ZIP, jehož první položka je `manifest.json`, pak ostatní položky. Položky Parquet
jsou *uložené* bez komprese (Parquet je už komprimovaný a uložená položka je
jeden bajtový rozsah, který čtenář může použít přímo na místě); položky JSON jsou
komprimované deflate.

| Role | Položka | Co |
|---|---|---|
| `table` | `<match>.parquet` | [Teplotní tabulka](output-table.md) (schéma `heat3d-table`) |
| `match` | `<match>.match.json` | [Dokument zápasu](output-match-json.md) (schéma `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | každá herní událost, kterou parser čte, celá |
| `props` | `<match>.props.parquet` | každá změna vlastnosti, kterou parser čte |
| `strings` | `<match>.strings.parquet` | každý záznam tabulky řetězců |
| `packets` | `<match>.packets.parquet` | každý další snímek a síťová zpráva, celé |

Manifest uvádí formát a verzi, hru (`cs2`), zdroj (`demo`), převodník a jeho
verzi, zápas, mapu, kdy byl zapsán, mapu `roles` od role k položce, a u každé
položky její typ médií, kompresi, velikost, SHA-256, počet řádků a případně
schéma. Na syntetickém demu z testů (zkráceně):

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

## Čtení bez prohlížeče {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` čte dokument zápasu přímo z kontejneru (nebo ze samostatného
`.match.json`).

## Přeskakování a přepisování {#skipping-and-rewriting}

Kontejner se zapíše celý, nebo vůbec, takže `.3dheat` pod `--out` se počítá jako
hotový zápas; `--force` ho přepíše. Zápas převedený dříve s `--loose` se počítá
jako hotový také.
