---
title: "Një skedar për ndeshje"
nav_order: 10
lang: "sq"
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Një skedar për ndeshje (`<match>.3dheat`) {#one-file-a-match-3dheat}

Si parazgjedhje `demos` e paketon çdo ndeshje në një skedar, `out/<map>/<match>.3dheat`:
tabelën e hartës së nxehtësisë, dokumentin e ndeshjes dhe katër sidecar-ët së bashku - një
ndeshje, një skedar, për ta kopjuar, mbajtur ose ndarë. Është formati kontejner
i shikuesit 3DHeat, i specifikuar në dokumentimin e shikuesit:
[Një skedar për ndeshje (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([burimi](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Kodi: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Hap pas hapi {#step-by-step}

1. Konverto si zakonisht; nuk ka gjë për të vendosur:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Çdo ndeshje është një skedar në dosjen e hartës së saj:

   ![demos në një demo sintetike](../assets/img/demos-run.svg)

3. Hape në shikues (skeda Harta e nxehtësisë ose skeda Ndeshja), ose lexoje vetë: është
   një ZIP i zakonshëm.

   ![brenda një kontejneri .3dheat](../assets/img/container-members.svg)

Për të mbajtur skedarët e ndarë në vend të tij - për mjete që duan një skedar Parquet në
disk - shto `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Çfarë ka brenda {#what-is-inside}

Një ZIP anëtari i parë i të cilit është `manifest.json`, pastaj anëtarët. Anëtarët Parquet
ruhen *stored* (Parquet është i ngjeshur tashmë, dhe një anëtar stored është një diapazon
bajtesh që një lexues mund ta përdorë aty ku është); anëtarët JSON ngjeshen me deflate.

| Roli | Anëtari | Çfarë |
|---|---|---|
| `table` | `<match>.parquet` | [Tabela e hartës së nxehtësisë](output-table.md) (skema `heat3d-table`) |
| `match` | `<match>.match.json` | [Dokumenti i ndeshjes](output-match-json.md) (skema `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | çdo ngjarje loje që lexon parseri, e tëra |
| `props` | `<match>.props.parquet` | çdo ndryshim vetie që lexon parseri |
| `strings` | `<match>.strings.parquet` | çdo hyrje e tabelës së vargjeve |
| `packets` | `<match>.packets.parquet` | çdo kuadër dhe mesazh rrjeti tjetër, i tëri |

Manifesti emërton formatin dhe versionin, lojën (`cs2`), burimin
(`demo`), konverterin dhe versionin e tij, ndeshjen, hartën, kur u
shkrua, një hartë `roles` nga roli te anëtari, dhe për secilin anëtar llojin e tij të medias,
ngjeshjen, madhësinë, SHA-256, numrin e rreshtave dhe, ku e ka, skemën e tij. Në
demon sintetike të testeve (e shkurtuar):

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

## Leximi i një skedari pa shikuesin {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` e lexon dokumentin e ndeshjes drejt nga kontejneri (ose nga një
`.match.json` i lirë).

## Anashkalimi dhe rishkrimi {#skipping-and-rewriting}

Një kontejner shkruhet i tëri ose aspak, kështu që një `.3dheat` nën `--out`
llogaritet si ndeshje e bërë; `--force` e rishkruan. Një ndeshje e konvertuar më parë me
`--loose` llogaritet e bërë gjithashtu.
