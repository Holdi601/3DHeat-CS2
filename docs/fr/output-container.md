---
title: "Un fichier par match"
nav_order: 10
lang: fr
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Un fichier par match (`<match>.3dheat`) {#one-file-a-match-3dheat}

Par défaut, `demos` regroupe chaque match dans un seul fichier, `out/<carte>/<match>.3dheat` : la table de carte de chaleur, le document de match et les quatre fichiers annexes ensemble - un match, un fichier, à copier, garder ou partager. C'est le format de conteneur de la visionneuse 3DHeat, décrit dans sa documentation :
[Un fichier par match (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([source](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Code : [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Étape par étape {#step-by-step}

1. Convertissez comme d'habitude ; rien à régler :

   ```bash
   python -m heat3d_cs2 demos <fichiers ou dossiers de démo> -o out
   ```

2. Chaque match est un fichier dans le dossier de sa carte :

   ![demos sur une démo synthétique](../assets/img/demos-run.svg)

3. Ouvrez-le dans la visionneuse (onglet Carte de chaleur ou onglet Match), ou lisez-le vous-même : c'est un ZIP ordinaire.

   ![à l'intérieur d'un conteneur .3dheat](../assets/img/container-members.svg)

Pour garder les fichiers séparés à la place - pour des outils qui veulent un fichier Parquet sur le disque - ajoutez `--loose` :

![demos --loose](../assets/img/demos-loose.svg)

## Ce qu'il contient {#what-is-inside}

Un ZIP dont le premier élément est `manifest.json`, suivi des éléments. Les éléments Parquet sont *stockés* (Parquet est déjà compressé, et un élément stocké est une plage d'octets qu'un lecteur peut utiliser sur place) ; les éléments JSON sont compressés en deflate.

| Rôle | Élément | Contenu |
|---|---|---|
| `table` | `<match>.parquet` | [La table de carte de chaleur](output-table.md) (schéma `heat3d-table`) |
| `match` | `<match>.match.json` | [Le document du match](output-match-json.md) (schéma `heat3d-cs2-match`) |
| `events` | `<match>.events.parquet` | chaque événement de jeu lu par l'analyseur, en entier |
| `props` | `<match>.props.parquet` | chaque changement de propriété lu par l'analyseur |
| `strings` | `<match>.strings.parquet` | chaque entrée de table de chaînes |
| `packets` | `<match>.packets.parquet` | chaque autre image et message réseau, en entier |

Le manifeste indique le format et sa version, le jeu (`cs2`), la source (`demo`), le convertisseur et sa version, le match, la carte, la date d'écriture, une table `roles` qui associe chaque rôle à un élément, et pour chaque élément son type de média, sa compression, sa taille, son SHA-256, son nombre de lignes et, s'il en a un, son schéma. Sur la démo synthétique des tests (abrégé) :

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

## Lire un conteneur sans la visionneuse {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` lit le document de match directement dans le conteneur (ou dans un `.match.json` séparé).

## Ignorer et réécrire {#skipping-and-rewriting}

Un conteneur est écrit en entier ou pas du tout, donc un `.3dheat` présent sous `--out` compte comme match fait ; `--force` le réécrit. Un match converti plus tôt avec `--loose` compte aussi comme fait.
