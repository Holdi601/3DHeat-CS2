---
title: Leer una demo
nav_order: 5
lang: "es"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Leer una demo {#reading-a-demo}

Lo que se saca de un archivo `.dem`, antes de interpretar nada. Código:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Una demo de CS2 es la grabación del propio servidor (SourceTV): cada jugador, en cada tick, 64 ticks por
segundo (`TICKRATE = 64`). Se lee con [demoparser2](https://github.com/LaihoE/demoparser) en tres llamadas,
y el resultado se guarda tal como llega, en un `RawPart`:

| Campo | Contiene |
|---|---|
| `path` | el archivo |
| `map` | `map_name` de la cabecera de la demo (`de_x`); vacío si la cabecera no tiene ninguno |
| `samples` | una fila por jugador y por tick muestreado: los campos de jugador y de reglas de abajo, más `tick`, `steamid`, `name` |
| `events` | nombre del evento -> sus filas, con los campos de los jugadores prefijados `user_`, `attacker_`, `assister_` como los nombra el analizador |

Nada en `demo.py` decide qué es una ronda ni quién la ganó; eso es [Cómo se arma una partida](building-matches.md).

## Los ticks muestreados {#the-sampled-ticks}

`parse_ticks` pide los ticks `0, N, 2N, ...` hasta 4.000.000 (`LAST_TICK`, muy por encima de cualquier
partida: 17 horas a 64 ticks por segundo), donde *N* es `--every` (por defecto 8). El analizador se detiene
al final de la demo. Cada jugador presente en un tick muestreado da una fila, esté vivo, muerto, mirando o
como entrenador; el filtrado se hace después.

El paso del muestreo importa más allá de la densidad del mapa de calor: el momento en que se decide una
ronda se lee de estas muestras (ver [Cómo se arma una partida](building-matches.md#rounds)), así que los
tiempos de fin de ronda son exactos a un paso (1/8 s por defecto).

### Campos de jugador {#player-fields}

| Propiedad | Se convierte en |
|---|---|
| `X`, `Y`, `Z` | la posición, en unidades del juego (pulgadas), Z hacia arriba. demoparser2 da el origen del jugador, es decir, los pies. |
| `yaw`, `pitch` | la dirección de la mirada (grados), convertida en un vector unitario |
| `health`, `armor_value` | salud, armadura |
| `team_num` | el bando: 2 = T, 3 = CT; cualquier otro valor (espectadores, 0, 1) no es bando |
| `team_clan_name` | el nombre del equipo tal como lo muestra el servidor, usado para nombrar los equipos |
| `active_weapon_name` | el arma en la mano, tal como la nombra el juego (`AK-47`, `Karambit`) |
| `is_alive` | si el jugador está vivo - solo los jugadores vivos se convierten en posiciones |
| `last_place_name` | el nombre de lugar del propio mapa (`BombsiteA`) |
| `balance` | dinero |
| `current_equip_value` | el valor de lo que lleva el jugador |

### Campos de reglas del juego {#game-rules-fields}

Se leen junto a ellos, una vez por fila de jugador (son los mismos para todos en un tick):

| Propiedad | Para qué se usa |
|---|---|
| `game_time` | el reloj del servidor, en segundos |
| `total_rounds_played` | el conteo de rondas, que continúa a través de los archivos de una partida |
| `round_win_status` | quién ganó la ronda recién jugada: 1 empate, 2 T, 3 CT |
| `round_win_reason` | cómo (el `CSRoundEndReason` del juego) |
| `team_rounds_total` | el marcador de cada bando |
| `is_warmup_period` | el calentamiento se deja fuera en todas partes |
| `is_freeze_period` | el tiempo de congelación se deja fuera de las posiciones |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | la prórroga que se juega, 0 en el tiempo reglamentario: las rondas de prórroga no son de pistola (el analizador no tiene un nombre más corto) |

## Los eventos {#the-events}

Cada evento de abajo se lee cuando la demo lo declara (`list_game_events`), con `X`, `Y`, `Z`, `team_num`,
`last_place_name` y `which_bomb_zone` (la zona de bomba en la que está el jugador: 0 ninguna, 1 A, 2 B) para
cada jugador que nombra el evento, y `total_rounds_played` e `is_warmup_period` del juego en ese tick:

| Evento | Se convierte en |
|---|---|
| `player_death` | eliminaciones y muertes; usa `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | daño; usa `dmg_health` (daño causado a la salud), `health` (salud que queda), `weapon` |
| `player_blind` | jugadores cegados; usa `blind_duration` |
| `weapon_fire` | disparos y lanzamientos de granadas; usa `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | dónde estallaron las granadas; usa los propios `x`, `y`, `z` del evento (el evento no tiene nombre de lugar para ese punto, solo el del lanzador) |
| `bomb_planted` | la colocación; usa la `which_bomb_zone` y el lugar del colocador, y `site` (el número de entidad de la zona) |
| `bomb_defused` | la desactivación |
| `bomb_exploded` | cuándo explotó la bomba: el tiempo de la fila `explode` |
| `round_freeze_end` | dónde empieza cada ronda |
| `round_prestart` | dónde termina el tiempo posterior a una ronda decidida |
| `round_announce_match_start` | dónde empieza la partida en vivo |

## Dos hechos sobre las demos que deciden cómo se leen {#two-facts-about-demos-that-decide-how-they-are-read}

- **Una partida puede repartirse entre archivos**, y los nombres de los archivos no dicen su orden. El
  conteo de rondas (`total_rounds_played`) continúa a través de ellos, y normalmente también el reloj del
  servidor, así que las partes se pueden ordenar por lo que contienen.
- **Una grabación puede empezar antes de la partida**: calentamiento, un reinicio, una ronda de cuchillos.
  La partida empieza en el **último** `round_announce_match_start` de un archivo; antes de él todo se deja
  fuera, y el calentamiento se deja fuera en todas partes.
