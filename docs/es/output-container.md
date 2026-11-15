---
title: Un archivo por partida
nav_order: 10
lang: es
source: output-container.md
source_hash: "e2690f688075"
nav_exclude: true
search_exclude: true
---
# Un archivo por partida (`<partida>.3dheat`) {#one-file-a-match-3dheat}

Por defecto, `demos` empaqueta cada partida en un solo archivo, `out/<mapa>/<partida>.3dheat`: la tabla
del mapa de calor, el documento de la partida y los cuatro archivos auxiliares juntos - una partida, un
archivo, para copiar, guardar o compartir. Es el formato de contenedor del visor de 3DHeat, especificado
en la documentación del visor:
[Un archivo por partida (.3dheat)](https://holdi601.github.io/3DHeat/container.html)
([fuente](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).
Código: [`heat3d_cs2/container.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/container.py).

## Paso a paso {#step-by-step}

1. Convierte como de costumbre; no hay nada que definir:

   ```bash
   python -m heat3d_cs2 demos <demo files or folders> -o out
   ```

2. Cada partida es un archivo en la carpeta de su mapa:

   ![demos sobre una demo sintética](../assets/img/demos-run.svg)

3. Ábrelo en el visor (pestaña Mapa de calor o pestaña Partida), o léelo tú mismo: es un ZIP corriente.

   ![dentro de un contenedor .3dheat](../assets/img/container-members.svg)

Para guardar los archivos separados en su lugar - para herramientas que quieren un archivo Parquet en
disco - añade `--loose`:

![demos --loose](../assets/img/demos-loose.svg)

## Qué hay dentro {#what-is-inside}

Un ZIP cuyo primer miembro es `manifest.json`, y después los demás miembros. Los miembros Parquet van
*almacenados* (Parquet ya está comprimido, y un miembro almacenado es un rango de bytes que un lector
puede usar en su sitio); los miembros JSON van comprimidos con deflate.

| Función | Miembro | Qué |
|---|---|---|
| `table` | `<partida>.parquet` | [La tabla del mapa de calor](output-table.md) (esquema `heat3d-table`) |
| `match` | `<partida>.match.json` | [El documento de la partida](output-match-json.md) (esquema `heat3d-cs2-match`) |
| `events` | `<partida>.events.parquet` | cada evento del juego que lee el analizador, completo |
| `props` | `<partida>.props.parquet` | cada cambio de propiedad que lee el analizador |
| `strings` | `<partida>.strings.parquet` | cada entrada de la tabla de cadenas |
| `packets` | `<partida>.packets.parquet` | cada otro fotograma y mensaje de red, completo |

El manifiesto indica el formato y la versión, el juego (`cs2`), la fuente (`demo`), el convertidor y su
versión, la partida, el mapa, cuándo se escribió, un mapa `roles` de función a miembro, y por cada
miembro su tipo de medio, compresión, tamaño, SHA-256, número de filas y, cuando tiene, su esquema. En la
demo sintética de las pruebas (abreviado):

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

## Leer uno sin el visor {#reading-one-without-the-viewer}

```python
import io, json, zipfile
import pandas as pd

with zipfile.ZipFile("out/de_test/alpha-vs-bravo-m1.3dheat") as z:
    manifest = json.loads(z.read("manifest.json"))
    table = pd.read_parquet(io.BytesIO(z.read(manifest["roles"]["table"])))
    match_document = json.loads(z.read(manifest["roles"]["match"]))
```

`scoreboard` lee el documento de la partida directamente del contenedor (o de un `.match.json` suelto).

## Omitir y reescribir {#skipping-and-rewriting}

Un contenedor se escribe completo o no se escribe, así que un `.3dheat` bajo `--out` cuenta como partida
hecha; `--force` lo reescribe. Una partida convertida antes con `--loose` también cuenta como hecha.
