---
title: Estadísticas
nav_order: 7
lang: es
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Estadísticas {#statistics}

Lo que hizo cada jugador en una partida, y cómo fue cada ronda: el marcador y la lista de rondas del
[documento de la partida](output-match-json.md). Código:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Todo se cuenta a partir de la partida construida como en [Cómo se arma una partida](building-matches.md):
sus registros de eliminación, su daño (salud perdida, solo enemigos), sus cegados (solo enemigos) y sus filas.

![el marcador de texto de una partida sintética](../assets/img/scoreboard.svg)

## Las convenciones {#the-conventions}

Cuando el propio juego no define un número, estas son las definiciones. También están escritas en cada
documento de partida, en `conventions`.

| Término | Definición |
|---|---|
| **Venganza** | Una muerte se considera *vengada* cuando su asesino es eliminado por un compañero de la víctima dentro de **5 s**; esa eliminación es una *eliminación de venganza*. |
| **Apertura** | La primera eliminación de un enemigo en la ronda mientras está en vivo. Una eliminación de compañero, un suicidio o una muerte a manos del mundo antes de ella se pasan por alto. |
| **KAST** | La proporción de rondas en las que un jugador hizo una **K**ill (eliminación), una **A**sistencia (cuenta una asistencia de destello), **S**obrevivió, o fue **T**raded (vengado). |
| **Daño** | Salud realmente perdida, solo de enemigos: un golpe en la cabeza de 137 de daño a un jugador con 40 de salud son 40. |
| **Clutch** | Ser el último jugador vivo de un bando con enemigos aún en pie; se gana cuando el bando gana la ronda. |
| **Compra** | Por bando, a partir del valor medio de equipo al final del tiempo de congelación: la primera ronda de cada mitad reglamentaria es de pistola (la ronda 1, y la ronda posterior a la mitad, mientras la partida la jugó); la prórroga no tiene ninguna; luego menos de 1.500 $ eco, menos de 4.000 $ force, si no full. |

## Quién empezó cada ronda {#who-started-each-round}

Varios números necesitan saber quién jugó una ronda. Los **jugadores iniciales** de una ronda son, por
bando, cada jugador con una fila de posición viva dentro de un segundo de la posición más temprana de esa
ronda (es decir, en el primer segundo después de que terminara el tiempo de congelación). Las **rondas
jugadas** de un jugador son el número de rondas que empezó. Si un jugador no empezó ninguna (nunca tuvo
una fila así), se usa en su lugar el conteo de rondas de la partida, para que no haya división entre cero.

## La línea del marcador {#the-scoreboard-line}

Una entrada por jugador (ver [el documento de la partida](output-match-json.md#players) para los nombres de
los campos). "Eliminación de enemigo" abajo significa una eliminación con atacante, que no es un
compañero abatido ni un suicidio (el propio de la víctima).

| Campo | Cuenta |
|---|---|
| `kills` | eliminaciones de enemigos, de la fase en vivo y de la posterior |
| `deaths` | cada muerte: a manos de enemigos, compañeros, uno mismo o el mundo |
| `assists` | eliminaciones de enemigos que este jugador asistió sin destello (el asistente no puede ser el asesino) |
| `flashAssists` | eliminaciones de enemigos que este jugador asistió con destello |
| `diff` | eliminaciones - muertes |
| `adr` | daño (salud perdida, solo de enemigos, ambas fases) / rondas jugadas, un decimal |
| `kast` | 100 x (rondas con una eliminación, una asistencia o asistencia de destello, supervivencia o muerte vengada) / rondas jugadas, un decimal. *Supervivencia* es: un jugador inicial de la ronda que no murió en ella, en ninguna de las dos fases. |
| `headshotPct` | 100 x eliminaciones en la cabeza / eliminaciones, un decimal; 0 sin eliminaciones |
| `openingKills`, `openingDeaths` | duelos de apertura ganados y perdidos |
| `tradeKills` | eliminaciones que vengaron la muerte de un compañero |
| `tradedDeaths` | muertes que fueron vengadas |
| `multiKills` | rondas con 2, 3, 4 y 5 eliminaciones de enemigos (`2k`, `3k`, `4k`, `5k`); más de cinco cuentan como `5k`. Cuentan ambas fases. |
| `clutches`, `clutchesWon` | clutches jugados y ganados (abajo) |
| `utilityDamage` | daño causado con granadas HE, molotov e incendiarias, un decimal |
| `enemiesFlashed` | enemigos cegados durante **al menos 1,0 s** por los destellos de este jugador |
| `plants`, `defuses` | colocaciones de bomba y desactivaciones (filas de la tabla) |
| `teamkills` | compañeros eliminados. Un suicidio - atacante y víctima el mismo jugador, una granada propia, por ejemplo - no lo es: es solo una muerte. |
| `roundsPlayed` | rondas empezadas, como se dijo antes |

Los jugadores se listan por nombre de equipo (en orden alfabético), y dentro de cada equipo por `diff` y
luego por `kills`, de mejor a peor.

Notas sobre los casos límite:

- Una eliminación en la fase posterior - los ganadores cazando a un jugador que ahorra - cuenta como una
  eliminación, una muerte, para el ADR, las multieliminaciones y el KAST como cualquier otra.
- Los wallbangs se cuentan por jugador internamente, pero no se escriben en el documento de la
  partida; cada eliminación de la lista de rondas dice si fue uno.
- La parte *vengada* del KAST acredita a la víctima de una muerte vengada en esa ronda.
- Las eliminaciones de compañeros y los suicidios suman una muerte a la víctima pero ninguna eliminación a
  nadie; una eliminación de compañero suma a `teamkills` del asesino, un suicidio no suma a nada más.

## Clutches {#clutches}

Para cada ronda, los jugadores iniciales de ambos bandos se toman como vivos, y se recorren en orden las
eliminaciones en vivo de la ronda. Tras cada muerte se quita a la víctima, y se mira cada bando: un bando
con exactamente **un** jugador restante, y al menos un enemigo aún vivo, es un clutch para ese jugador
**contra** el número de enemigos vivos en ese momento. Cada jugador tiene como mucho un clutch por ronda;
se **gana** cuando su bando gana la ronda.

Consecuencias de la definición:

- Los dos bandos pueden tener un clutch en la misma ronda. Si un bando se queda primero con uno (un 1v3,
  por ejemplo) y el otro también se queda con uno después, el segundo jugador está en un clutch 1v1 propio.
- `against` es el recuento cuando el jugador se quedó el último, no al final.
- Las eliminaciones de la fase posterior no se recorren, así que ni empiezan un clutch ni lo cambian.

## Supervivientes {#survivors}

Los **supervivientes** de una ronda son, por bando, sus jugadores iniciales menos todos los que murieron
mientras estaba en vivo. Un jugador eliminado en la fase posterior mientras ahorraba sigue siendo
superviviente en la lista de rondas, pero no *sobrevivió* para el KAST.

## La lista de rondas {#the-round-list}

Cada ronda del documento de la partida lleva su resultado, marcador, bandos, economía, colocación,
supervivientes, clutches y sus eliminaciones en orden; ver
[El documento de la partida](output-match-json.md#rounds).

## El marcador de texto {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` imprime estos números por equipo; ver
[Comandos](commands.md#scoreboard---a-match-as-text).
