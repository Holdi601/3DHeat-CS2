---
title: La tabla del mapa de calor
nav_order: 8
lang: "es"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# La tabla del mapa de calor (`<partida>.parquet`) {#the-heatmap-table-parquet}

Un archivo Parquet por partida: la posición de cada jugador vivo, muestreada, y cada evento en el momento
en que ocurrió, una fila por cada uno - una tabla larga que el visor de 3DHeat lee como mapa de calor, y
cualquier otra herramienta como una tabla corriente. Código:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(el archivo), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(las filas; ver [Cómo se arma una partida](building-matches.md)).

El archivo se escribe con compresión Snappy en grupos de filas de 256.000 filas. Las filas se ordenan por
`time` y, dentro de él, por `event`. Solo están en la tabla las filas dentro de una ronda (desde el final
de su tiempo de congelación hasta el inicio de la siguiente ronda).

En la demo sintética de las pruebas, las filas de eventos de la primera ronda:

![filas de eventos de la tabla](../assets/img/table-rows.svg)

En un contenedor `.3dheat`, la tabla es el miembro con la función `table`
([Un archivo por partida](output-container.md)).

## Columnas {#columns}

Las columnas, siempre en este orden. Las columnas de texto son cadenas codificadas por diccionario
(`dictionary<int32, string>`) y nunca son nulas: "sin valor" es una cadena vacía. Las columnas numéricas
son nulas donde una fila no tiene valor.

| Columna | Tipo | Qué |
|---|---|---|
| `match` | cadena | el nombre de la partida (`alpha-vs-bravo-m1`, o `...-b` para una segunda cadena) |
| `map` | cadena | el mapa, de la cabecera de la demo (`de_x`) |
| `round` | int16 | el número de ronda, desde 1 |
| `roundId` | cadena | `<partida> #NN`, el número de ronda con dos dígitos (`alpha-vs-bravo-m1 #07`): único entre partidas; la sesión del visor |
| `phase` | cadena | `freeze` en el tiempo de congelación de la ronda (desde el final de la ronda anterior), `live` hasta que se decide la ronda, `after` mientras los ganadores buscan y los perdedores ahorran |
| `time` | float64 | segundos desde el inicio de la partida (el inicio en vivo de su primer archivo), en un solo reloj para todos sus archivos |
| `roundTime` | float32 | segundos desde que terminó el tiempo de congelación de esta ronda; negativo en el tiempo de congelación |
| `event` | cadena | qué es la fila - ver [Eventos](#events) |
| `player` | cadena | el nombre del jugador (para cada evento, qué jugador se indica más abajo) |
| `steamid` | cadena | el ID de Steam del jugador (64 bits, como texto) |
| `side` | cadena | `T` o `CT` en esta ronda; vacío cuando el jugador no estaba en ningún bando |
| `team` | cadena | el nombre de equipo del jugador (o `Started T` / `Started CT`); para `explode`, el equipo que colocó la bomba |
| `x`, `y`, `z` | float32 | posición en las propias coordenadas del juego: pulgadas (unidades del juego), **Z hacia arriba**, sistema dextrógiro |
| `dirX`, `dirY`, `dirZ` | float32 | hacia dónde mira el jugador, un vector unitario en el mismo sistema; solo posiciones |
| `health` | int16 | 0-100; posiciones, y en `hurt` lo que quedó después del golpe |
| `armor` | int16 | 0-100; posiciones, y en `hurt` lo que quedó después del golpe |
| `money` | int32 | el dinero del jugador; solo posiciones |
| `equipment` | int32 | el valor de lo que lleva el jugador; solo posiciones |
| `weapon` | cadena | el arma tal como la nombra el juego (`AK-47`, `M4A1-S`, `Knife` para todas las skins de cuchillo) |
| `place` | cadena | el nombre de lugar del mapa en la posición de la fila (`BombsiteA`, `CTSpawn`); vacío en las detonaciones de granadas: la demo no nombra ningún lugar donde estalló una granada |
| `throwerPlace` | cadena | el nombre de lugar del lanzador cuando estalló la granada; solo detonaciones de granadas |
| `other` | cadena | el otro jugador de una eliminación, muerte, golpe o destello |
| `damage` | float32 | salud perdida; solo `hurt` |
| `duration` | float32 | segundos cegado; solo `blind` |
| `headshot` | int8 | 0/1; solo `kill` y `death` |
| `opening` | int8 | 0/1, la primera eliminación de un enemigo en la ronda; solo `kill` y `death` |
| `traded` | int8 | 0/1. Para un `kill`: fue una eliminación de venganza. Para un `death`: fue vengada dentro de 5 s. Solo `kill` y `death`. |
| `noscope` | int8 | 0/1, la eliminación fue con un arma con mira disparada sin mira (el `noscope` del evento); solo `kill` y `death` |
| `attackerBlind` | int8 | 0/1, el asesino estaba cegado cuando mató (el `attackerblind` del evento); solo `kill` y `death` |
| `won` | int8 | 0/1, si el bando de esta fila ganó la ronda; null cuando `side` está vacío |
| `buy` | cadena | la compra del bando de esta fila en esta ronda: `pistol`, `eco`, `force`, `full` |
| `detail` | cadena | cada campo del evento que no llevan las otras columnas, como objeto JSON (los nombres propios del juego): los disparos de una bala (`fire_bullets`: origen, ángulos, imprecisión, dispersión, índice de retroceso, semilla...), `dominated`, `revenge`, `attackerinair`, `wipe`... de una muerte, `defindex` de un objeto, nada en un paso |
| `text` | cadena | una línea de chat; solo `chat` |
| `entity` | int32 | la entidad de la granada: el vuelo de un `throw` (filas `grenade`), su detonación y los jugadores que cegó comparten la misma |
| `hitgroup` | cadena | dónde impactó la bala (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | armadura perdida; solo `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | dónde en el cuerpo impactó la bala, en el sistema de la víctima en metros (x hacia delante, y hacia arriba desde los pies, z a la derecha): el rayo del disparo (`fire_bullets`, si no el ojo y la vista del atacante) trazado sobre un cuerpo en la pose en que estaba la víctima, de pie y agachada, hasta la parte que nombra `hitgroup`; solo `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | la dirección del disparo en el mismo sistema; `hitMiss` cuánto (m) pasó el rayo de la parte nombrada (0: a través de ella); `hitFrom` `bullet` o `aim` |
| `penetrated` | int16 | paredes que atravesó la bala mortal; `kill` y `death` |
| `throughSmoke` | int8 | 0/1, muerte a través de humo; `kill` y `death` |
| `distance` | float32 | la distancia de la eliminación tal como la cuenta el juego (metros); `kill` y `death` |
| `assister` | cadena | quién asistió; `kill` y `death` |
| `flash`, `flashAlpha` | float32 | segundos de destello que quedan, y cuán blanco; posiciones |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; posiciones |
| `zoom`, `duck`, `moveType` | | el nivel de zoom de la mira, cuánto está agachado (0-1), el tipo de movimiento del juego; posiciones |
| `spottedBy` | cadena | los IDs de Steam de los enemigos que ven a este jugador, separados por `\|`; posiciones |
| `inventory` | cadena | todo lo que lleva el jugador, separado por `\|`; posiciones |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | el cargador y la reserva del arma en la mano; disparos en la ráfaga actual; posiciones |
| `punchPitch`, `punchYaw` | float32 | el empuje de retroceso de la mira, en grados; posiciones |
| `ping` | int16 | milisegundos; posiciones |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | los recuentos propios del marcador del juego para la partida hasta ahora; posiciones |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | dinero gastado en esta ronda y en la partida; valor de equipo cuando empezó la ronda; posiciones |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, el estado del jugador en el momento de la fila, incluidos los eventos: casco, kit de desactivación, alguna armadura, con mira (desde su última muestra de posición hasta la fila), cegado (dentro de un `blind` que lo alcanzó); cada fila que nombra a un jugador |
| `state_utility` | int16 | granadas que llevaba en ese momento (de `inventory`); cada fila que nombra a un jugador |
| `state_weapon` | cadena | el arma en la mano en ese momento (en una `death`, la propia de la víctima, mientras que `weapon` es la del asesino); cada fila que nombra a un jugador |
| `earn_round_cs2` | int16 | lo que pagó la ronda: en `round_end` la recompensa de victoria o la bonificación de derrota (con la bonificación del bando que colocó), en `plant` y `defuse` los 300 del jugador |

## Eventos {#events}

Qué jugador nombra una fila, dónde está y qué columnas rellena.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won` y `buy` se rellenan en
cada fila; `inventory`, `money`, `equipment` y las columnas `state_*` en cada fila que nombra a un
jugador (los eventos las toman de la última muestra de posición del jugador).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | También rellena |
|---|---|---|---|
| `position` | el jugador | el jugador (los pies) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (en la mano), `place`, y todo el estado del jugador (las columnas desde `flash` en adelante) - también en el tiempo de congelación |
| `kill` | el asesino | dónde estaba el asesino | `other` (víctima), `weapon`, `headshot`, `opening`, `traded` (una eliminación de venganza), `noscope`, `attackerBlind`, `place` |
| `death` | la víctima | donde cayó la víctima | `other` (asesino; vacío para el mundo), `weapon`, `headshot`, `opening`, `traded` (vengada), `noscope`, `attackerBlind`, `place` |
| `hurt` | la víctima | donde fue alcanzada la víctima | `other` (atacante), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - también los golpes a compañeros y del mundo |
| `shot` | el tirador | desde donde se disparó | `weapon`, `place`, `detail` (el relato del juego sobre las balas) |
| `slash` | el jugador | donde se dio un tajo con el cuchillo | `weapon` = `Knife` |
| `grenade` | el lanzador | la granada en vuelo, en cada muestra de los jugadores y donde se detuvo | `weapon` (la granada), `entity` |
| `throw` | el lanzador | desde donde se lanzó la granada | `weapon` (la granada), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | el lanzador | donde estalló | `weapon`, `throwerPlace` (el lugar del lanzador en ese momento); `place` queda vacío |
| `blind` | el jugador cegado | donde estaba | `other` (quien lo cegó), `duration`, `weapon` = `Flashbang`, `entity`, `place` - también los compañeros cegados |
| `plant` | el colocador | donde colocó | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | el desactivador | donde desactivó | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | cada jugador que jugó la ronda | donde estaba el jugador por última vez | `won`, `earn_round_cs2` (lo que la ronda les pagó: la subida del dinero del bando hasta el siguiente tiempo de congelación cuando las reglas lo permiten, si no, lo que digan las reglas), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | el colocador (con su ID de Steam), bando `T`, el equipo que colocó | la posición de la colocación | `weapon` = `C4 Explosive`, `place` (el del colocador en la colocación: donde quedó la bomba); su tiempo es cuando explotó la bomba |
| `chat` | quien envía | donde estaba | `text` |
| cada otro evento del juego sobre un jugador, con el nombre del juego: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | el jugador | donde estaba (los eventos de una granada: donde estaba la granada) | `weapon` (de un objeto), `entity`, `detail` (cada campo del evento) |

Qué entra y qué no:

- Las filas **position** son jugadores vivos de un bando, fuera del tiempo de congelación y del
  calentamiento, cada `--every` ticks (ocho por segundo por defecto).
- Las filas **kill** son solo eliminaciones de un enemigo - sin compañeros abatidos, suicidios ni muertes
  a manos del mundo. Las filas **death** son todas las muertes, también esas.
- Las filas **explode** son cada bomba colocada que llegó a explotar, según el `bomb_exploded` de la demo:
  también en la fase posterior, cuando los T ya habían ganado por eliminación. Una demo sin ese evento
  recibe una para cada ronda ganada por la bomba, al final de la ronda.
- Las filas **hurt** y **blind** son solo entre enemigos.
- **shot** deja fuera cuchillos y la C4; las granadas son filas **throw**.
- **molotov** cubre molotov e incendiarias (el inicio del fuego).
- El daño entre compañeros, los destellos de compañeros y de espectadores, los eventos del tiempo de
  congelación y cualquier cosa entre rondas no están en la tabla.

Un ejemplo trabajado, de la demo sintética de las pruebas (un humo lanzado, una apertura con un disparo
en la cabeza, venganzas):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

La muerte de bob es vengada por la eliminación de ace por parte de ben 1,9 s después (la fila `death` de
bob: traded 1; la fila `kill` de ben: una eliminación de venganza, traded 1); el segundo golpe a bob fue de
137 de daño con 40 de salud, así que cuenta 40.

## Las pistas del pie `heat3d` {#the-heat3d-footer-hints}

El pie Parquet del archivo (metadatos clave/valor del esquema) lleva instrucciones de lectura bajo la
clave **`heat3d`**, un objeto JSON:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Entrada | Dice |
|---|---|
| `version`, `kind` | la versión de las pistas (1) y qué las escribió (`cs2-demo`) |
| `axes.up` | la Z del archivo es hacia arriba |
| `axes.flipY` | invertir la Y del archivo (ver abajo) |
| `axes.scale` | 1: las posiciones se usan tal cual, en unidades del juego |
| `entity.size` | un jugador mide **32 unidades** de ancho - el ancho de un jugador de CS2 - el tamaño con el que la repetición en caja dibuja a uno |
| `columns.x` / `y` / `z` | las columnas de posición |
| `columns.time`, `timeUnit` | `time`, en segundos |
| `columns.personId` | el jugador es la persona |
| `columns.teamId` | el bando es el grupo (así que T y CT, no los nombres de equipo, colorean los grupos) |
| `columns.sessionId` | cada ronda (`roundId`) es una sesión |
| `columns.lookMode` y `dirX`-`dirZ` | la dirección de la mirada es un vector en esas columnas |
| `columns.extra` | las columnas que conservar como filtros, por orden de utilidad |

Un visor que conoce la clave abre el archivo sin tener que configurar nada. Cualquier otro lo ignora.
Para leerlo tú mismo:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Ejes y unidades {#axes-and-units}

Las coordenadas son las propias del juego: **pulgadas** (una unidad del juego; un jugador mide 72
unidades de alto de pie y 32 de ancho), **Z hacia arriba**, y de sistema dextrógiro.

Un visor cuyo mundo tiene Y hacia arriba debe dibujar las (x, y, z) del juego como **(x, z, -y)**: la Z
se convierte en la altura y la Y se niega. Es una rotación, no un espejo. Dibujado como lo haría un mundo
de Z hacia arriba zurdo, como (x, z, y), cada mapa sale reflejado, con el sitio A en el lado equivocado;
`flipY: true` es lo que indican las pistas para evitarlo. La [exportación del mapa](map-export.md) escribe
su geometría ya en el sistema (x, z, -y), en las mismas unidades, así que queda debajo de la tabla sin
ningún ajuste.

Las distancias en el visor se etiquetan en metros; con escala 1 son unidades del juego. Multiplica por
0,0254 para pasar a metros.

## Tamaño {#size}

Las posiciones dominan: unos diez jugadores por 8 muestras por segundo de juego vivo con el `--every 8`
por defecto, menos para jugadores muertos y el tiempo de congelación. Dividir `--every` a la mitad duplica
las posiciones; los eventos no cambian.
