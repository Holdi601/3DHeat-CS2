---
title: Her maç için tek dosya
nav_order: 10
lang: "tr"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Her maç için tek dosya (`<match>.3dheat`) {#one-file-a-match-3dheat}

Varsayılan olarak `demos` her maçı tek bir dosyaya paketler, `out/<map>/<match>.3dheat`: ısı haritası tablosu,
maç belgesi ve dört yan dosya birlikte - bir maç, bir dosya; kopyalamak, saklamak veya paylaşmak için. 3DHeat
görüntüleyicisinin kapsayıcı biçimidir ve görüntüleyicinin belgelerinde tanımlanmıştır:
[Her maç için tek dosya (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([kaynak](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kod: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Adım adım {#step-by-step}

1. Her zamanki gibi çevirin; ayarlanacak bir şey yok:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Her maç, haritasının klasöründe bir dosyadır:

   ![demos sentetik bir demoda](../assets/img/demos-run.svg)

3. Görüntüleyicide açın (Isı haritası sekmesi veya Maç sekmesi) ya da kendiniz okuyun: sıradan bir ZIP dosyasıdır.

   ![.3dheat kapsayıcısının içi](../assets/img/container-members.svg)

Bunun yerine ayrı dosyaları tutmak için - diskte bir Parquet dosyası isteyen araçlar için - `--loose` ekleyin:

![demos --loose](../assets/img/demos-loose.svg)

## İçinde ne var {#what-is-inside}

İlk öğesi `manifest.json` olan bir ZIP, ardından öğeler. Parquet öğeleri *depolanır* (Parquet zaten sıkıştırılmıştır
ve depolanan bir öğe, bir okuyucunun yerinde kullanabileceği tek bir bayt aralığıdır); JSON öğeleri sıkıştırılır.

| Rol | Öğe | Ne |
|---|---|---|
| `table` | `<match>.parquet` | [Isı haritası tablosu](output-table.md) (şema `heat3d-table`) |
| `match` | `<match>.match.json` | [Maç belgesi](output-match-json.md) (şema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | çözümleyicinin okuduğu her oyun olayı, tamamı |
| `props` | `<match>.props.parquet` | çözümleyicinin okuduğu her özellik değişikliği |
| `strings` | `<match>.strings.parquet` | her dize tablosu girdisi |
| `packets` | `<match>.packets.parquet` | diğer her kare ve ağ mesajı, tamamı |

Manifest, biçimi ve sürümünü, oyunu (`cs2`), kaynağı (`demo`), dönüştürücüyü ve sürümünü, maçı, haritayı, ne zaman
yazıldığını, rolden öğeye bir `roles` haritasını ve her öğe için medya türünü, sıkıştırmayı, boyutu, SHA-256'yı, satır
sayısını ve varsa şemasını içerir. Testlerdeki sentetik demoda (kısaltılmış):

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

## Görüntüleyici olmadan okumak {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard`, maç belgesini doğrudan kapsayıcıdan (veya ayrı bir `.match.json`'dan) okur.

## Atlama ve yeniden yazma {#skipping-and-rewriting}

Bir kapsayıcı tamamen yazılır ya da hiç yazılmaz; bu yüzden `--out` altındaki bir `.3dheat` tamamlanmış bir maç
sayılır; `--force` onu yeniden yazar. Daha önce `--loose` ile çevrilmiş bir maç da tamamlanmış sayılır.
