---
title: Desarrollo
nav_order: 15
lang: "es"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Desarrollo {#development}

## Estructura {#layout}

| Ruta | Qué es |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: primero la comprobación de versión, luego la línea de comandos |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | los verbos y las opciones; agrupar los archivos de demo en partidas; el grupo de trabajadores |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | un archivo de demo pasado por demoparser2 a un `RawPart` - [Leer una demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | partes, cadenas, el reloj, rondas, equipos, filas, eliminaciones, daño, cegados - [Cómo se arma una partida](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | resúmenes de ronda, el marcador, el documento de partida, el marcador de texto - [Estadísticas](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | la tabla Parquet con sus pistas `heat3d`, y el JSON - [La tabla del mapa de calor](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | encontrar CS2 y Source2Viewer, la malla de colisión en el sistema del visor - [Exportar el mapa](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | un lector y escritor mínimo de glTF binario (sin más dependencia que numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | la comprobación de versión y el actualizador - [Actualizaciones](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | las pruebas y la demo sintética |
| `VERSION` | la versión, en una línea |

El flujo de datos:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Uso desde Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # la tabla del mapa de calor como DataFrame de pandas
    kills = match.kills        # una fila por muerte, con todas las marcas
    doc = summary(match)       # el documento .match.json como diccionario
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` y `Match.blinds` son DataFrames de pandas con más de lo que llevan las
salidas: posiciones y lugares del atacante y de la víctima en cada eliminación, y `utility` por golpe,
para análisis propios.

## Pruebas {#tests}

```bash
python -m pytest
```

`pytest.ini` ejecuta `tests/` en silencio. Las pruebas no necesitan demo, juego ni Source2Viewer:
[`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) construye
a mano una demo, tal como la daría demoparser2: dos rondas, dos jugadores por bando (`ace`, `ash` del
equipo Alpha; `bob`, `ben` del Bravo), lo bastante pequeña para que cada respuesta sea conocida:

- Ronda 1, victoria de T por eliminación: ace mata a bob de un disparo en la cabeza (la apertura);
  ben mata a ace 1,9 s después (una venganza: la muerte de bob queda vengada); ash mata a ben 3,1 s
  después de eso - solo contra uno, un clutch ganado.
- Ronda 2, victoria de T por la bomba: ash coloca la bomba en A, nadie muere, la bomba explota.

`fixtures.halves` construye una partida más larga de rondas vacías, con los equipos en sus primeros
bandos o cambiados, con el número de prórroga del juego o sin él, para la duración de la mitad y las
rondas de pistola.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) comprueba
sobre ella: el ganador, la causa, el marcador y los bandos de cada ronda; el reloj que empieza en la
partida; la economía y la colocación (su tiempo dentro de la ronda, su lugar, la explosión de la
bomba); que el sitio de una colocación sea siempre una letra o vacío, nunca un número de entidad; una
ronda empatada decidida sin ganador; las rondas de pistola desde donde cambian de bando, sin la
prórroga, y solo la ronda 1 sin cambio; equipos sin nombres de clan (`Started T` / `Started CT`);
aperturas, venganzas y marcas; un suicidio que no es una muerte de compañero, y la apertura pasada a la
primera eliminación de un enemigo; `noscope` y `attackerBlind` en la tabla y en el documento de la
partida; el daño como salud perdida (60, luego 40 de un golpe de 137 sobre 40 de salud); los números
del marcador y el KAST; los clutches; el marcador de texto; los eventos de la tabla y dónde están (una
detonación sin lugar propio, el del lanzador en `throwerPlace`; la explosión del equipo que colocó la
bomba); que las posiciones están en vivo, etiquetadas y tienen vectores de mirada unitarios; que el
archivo escrito lleva sus pistas; que las partes se ponen en orden sea cual sea su nombre; un reloj de
servidor reiniciado que aun así continúa; y las filas duplicadas de una ronda restaurada resueltas en
la que sigue hacia adelante.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) comprueba que
las demos en carpetas se encuentran sea cual sea la mayúscula de `.dem`, y que una partida cuenta como
escrita solo con su tabla y su documento de partida.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
comprueba las conversiones de sistema (los metros de Source2Viewer a las pulgadas del juego, y de ahí
al sistema del visor, una rotación con determinante 1), que los clips y el cielo se dejan fuera sea
cual sea la mayúscula y los nombres de superficie, la división suelo/estructura por normal, y que un
`.glb` se escribe y se vuelve a leer.

### La comprobación del suelo en un mapa real {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Con ambas variables definidas, también se ejecuta `test_players_stand_on_the_exported_floor`: convierte
la demo, exporta su mapa desde el juego instalado y comprueba que al menos el 98 % de 300 muestras de
posición aleatorias tiene suelo debajo, con una altura media por encima de él menor de 5 unidades
([Exportar el mapa](map-export.md#the-check-that-the-frame-is-right)).

## Convenciones del código {#conventions-of-the-code}

- Los tiempos dentro de `match.py` son segundos de partida, salvo el `time` de una colocación, que son
  segundos dentro de su ronda, como lo escribe el documento de la partida; los ticks pasan a segundos
  solo a través de `_Part.at`.
- Los bandos son las cadenas `T` / `CT` en todas partes, salvo en los datos del analizador en bruto
  (`team_num` 2 / 3).
- Una columna nueva de la tabla va a `ROW_COLUMNS` (y a `NUMERIC` si es numérica) en `match.py`;
  `output.table` elige su tipo Parquet entre los conjuntos `INT16`, `INT32`, `FLOAT64` y las marcas
  0/1, y float32 en el resto.
- Cambiar lo que debe hacer el visor con una columna significa cambiar `HINTS` en `output.py`.

## Licencia {#licence}

MIT. Paquetes de terceros:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Las demos y los mapas nunca forman parte del repositorio; su `.gitignore` excluye por tipo `*.dem`,
`*.parquet`, `*.match.json`, `*.glb` y similares.
