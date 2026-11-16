---
title: El documento de la partida
nav_order: 9
lang: "es"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# El documento de la partida (`<partida>.match.json`) {#the-match-document-matchjson}

Un documento JSON por partida, junto a su tabla: equipos, marcador, cada ronda con su resultado, economía,
colocación, eliminaciones, clutches y supervivientes, y la línea del marcador de cada jugador. Es lo que
carga la pestaña Partida del visor de mapas de calor de 3DHeat.
Código: `summary()` en
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
los números se definen en [Estadísticas](statistics.md).

El archivo es UTF-8, con sangría de un espacio, y conserva los caracteres no ASCII (nombres de jugadores
y de equipos) tal como son. Los tiempos son segundos, redondeados a tres decimales para las rondas y a
dos para las eliminaciones y la colocación.

## El documento {#the-document}

| Campo | Tipo | Qué |
|---|---|---|
| `format` | cadena | siempre `heat3d-cs2-match` - cómo reconoce un lector el archivo |
| `version` | número | `3`. Un documento de versión 1 da el `time` de una colocación en segundos de partida; desde la 2 es en segundos dentro de la ronda, como el de una eliminación. La 3 añade los campos desde `header` en adelante, y el tiempo de congelación a la tabla. |
| `match` | cadena | el nombre de la partida, tal como se llaman los archivos |
| `map` | cadena | el mapa (`de_x`) |
| `demos` | cadena[] | los archivos de demo de los que se construyó, solo nombres de archivo, en orden de partida |
| `teams` | cadena[] | los nombres de equipo por orden de aparición (ronda 1: primero el bando T) |
| `score` | objeto | nombre de equipo -> rondas ganadas: el marcador de la última ronda |
| `winner` | cadena o null | el equipo que ganó la partida, cuando la grabación muestra el final; null para una grabación que se corta antes, una prórroga sin el panel de victoria, o un empate |
| `winnerSource` | cadena o null | cómo se sabe `winner`: `winPanel` (el panel de victoria de la partida del juego), `surrender`, `regulation` (más de la mitad de las rondas reglamentarias) |
| `rounds` | objeto[] | cada ronda completa, en orden - [abajo](#rounds) |
| `incomplete` | número[] | números de ronda cortados por el final de una demo y dejados fuera |
| `missing` | número[] | números de ronda anteriores a la primera que tienen las demos: `[1, 2]` cuando la grabación empieza en la ronda 3 |
| `halfLength` | número o null | rondas en una mitad reglamentaria, desde donde los bandos cambian de lado por primera vez (`12` en el formato de 24 rondas); null cuando la grabación no muestra el cambio |
| `pistolRounds` | número[] | las rondas de pistola con las que se cuenta la `buy`: la ronda 1, y la ronda posterior a la mitad cuando se conoce `halfLength`; nunca una ronda de prórroga |
| `players` | objeto[] | el marcador - [abajo](#players) |
| `conventions` | objeto | las definiciones detrás de los números, [abajo](#conventions) |
| `header` | objeto | la cabecera de la primera demo tal como la da el analizador: nombre del servidor, versión del parche, versión de la demo, mapa |
| `profiles` | objeto | ID de Steam -> lo que se mantiene igual para un jugador durante la partida: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (el último visto) |
| `playerInfo` | objeto[] | cada jugador que listan las demos, también entrenadores y comentaristas: ID de Steam, nombre, número de equipo |
| `skins`, `itemDrops` | objeto[] | skins de armas y objetos soltados, cuando la demo los tiene (las demos de torneo de la retransmisión no los tienen) |
| `chat` | objeto[] | cada línea de chat de la partida: tiempo, ronda, jugador, bando, texto |
| `events` | objeto[] | cada evento del juego que no es de ningún jugador, en orden de tiempo, con todos sus campos: avisos y fases de ronda, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (la configuración del servidor según cambia), las tomas de chase y fijas del director de cámara de la retransmisión, `cs_win_panel_match`, ... |
| `state` | objeto[] | el estado del juego donde cambió: tiempo, campo, valor - tiempos muertos (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), la bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, los jugadores vivos, `match_start_time` y `round_start_time` del servidor |
| `selfCheck` | objeto | `completeness`: a dónde fue todo lo de la demo - por nombre de evento, clase de propiedad, mensaje de red, fotograma y tabla de cadenas, sus recuentos `seen`, `decoded`, `partial`, `raw` y `lost`, los archivos auxiliares escritos, el total `lost` (0 salvo con `--no-bulk`), las propiedades que el analizador lista pero no puede leer (`unreadProps`). La convención: [Los convertidores lo guardan todo](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); los archivos auxiliares: la sección de integridad del README |

## Rondas {#rounds}

| Campo | Tipo | Qué |
|---|---|---|
| `number` | número | la ronda, desde 1 |
| `start` | número | segundos de partida cuando terminó el tiempo de congelación |
| `end` | número | segundos de partida cuando se decidió la ronda |
| `until` | número | segundos de partida cuando empezó la siguiente ronda (el final de la fase posterior) |
| `winner` | cadena | `T` o `CT`; vacío en un empate |
| `winnerTeam` | cadena | el nombre de equipo del bando ganador; vacío en un empate |
| `reason` | cadena | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` u `other` |
| `score` | objeto | nombre de equipo -> rondas ganadas después de esta |
| `sides` | objeto | nombre de equipo -> `T` / `CT` en esta ronda |
| `equipment` | objeto | bando -> valor total de equipo de sus jugadores vivos en el freeze end, en dólares |
| `buy` | objeto | bando -> `pistol`, `eco`, `force` o `full` |
| `plant` | objeto o null | la colocación de la bomba: `site` (`A` o `B`; vacío cuando la demo no lo dice), `time` (segundos **dentro de la ronda**, como el de una eliminación), `player`, `steamid`, `x`, `y`, `z` (unidades del juego), `place` (el nombre del lugar del colocador: donde quedó la bomba) |
| `survivors` | objeto | bando -> nombres de los jugadores iniciales que seguían vivos cuando se decidió la ronda, ordenados |
| `clutches` | objeto[] | cada uno: `player`, `steamid`, `side`, `against` (enemigos vivos cuando el jugador quedó el último), `won` |
| `kills` | objeto[] | cada muerte de la ronda, en orden - abajo |

Cómo se encuentran: [Cómo se arma una partida](building-matches.md#rounds);
clutches y supervivientes: [Estadísticas](statistics.md#clutches).

### Las eliminaciones de una ronda {#a-rounds-kills}

Cada muerte de la ronda, incluida la fase posterior:

| Campo | Tipo | Qué |
|---|---|---|
| `time` | número | segundos **dentro de la ronda** (desde el freeze end) |
| `attacker`, `attackerSide` | cadena | el asesino y su bando; vacío para el mundo |
| `victim`, `victimSide` | cadena | la víctima y su bando |
| `assister` | cadena o null | el jugador que asistió, o null |
| `flashAssist` | bool | la asistencia fue un destello |
| `weapon` | cadena | tal como la nombra el juego |
| `headshot` | bool | |
| `wallbang` | bool | la bala atravesó algo |
| `throughSmoke` | bool | la eliminación fue a través del humo |
| `noscope` | bool | un arma con mira disparó sin mira |
| `attackerBlind` | bool | el asesino estaba cegado |
| `opening` | bool | la primera eliminación de un enemigo en la ronda |
| `traded` | bool | esta muerte fue vengada dentro de 5 s |
| `trade` | bool | esta eliminación vengó a un compañero dentro de 5 s |
| `teamkill` | bool | atacante y víctima en el mismo bando, dos jugadores distintos |
| `suicide` | bool | atacante y víctima son el mismo jugador (una granada propia, por ejemplo); no es una eliminación de compañero |
| `after` | bool | la eliminación llegó después de que se decidiera la ronda |
| `place` | cadena | dónde estaba la **víctima** (el nombre de lugar del mapa) |

## Jugadores {#players}

Una entrada por jugador, por nombre de equipo y luego de mejor a peor según eliminaciones menos muertes,
y después eliminaciones:

| Campo | Tipo | Qué |
|---|---|---|
| `name`, `steamid`, `team` | cadena | quién |
| `kills`, `deaths` | número | |
| `assists`, `flashAssists` | número | asistencias sin destello y con destello |
| `diff` | número | eliminaciones - muertes |
| `adr` | número | daño medio por ronda jugada, salud perdida |
| `kast` | número | porcentaje de rondas jugadas con una eliminación, una asistencia, una supervivencia o una muerte vengada |
| `headshotPct` | número | porcentaje de eliminaciones que fueron en la cabeza |
| `openingKills`, `openingDeaths` | número | duelos de apertura ganados y perdidos |
| `tradeKills`, `tradedDeaths` | número | eliminaciones de venganza; muertes que fueron vengadas |
| `multiKills` | objeto | `{"2k": n, "3k": n, "4k": n, "5k": n}`: rondas con esa cantidad de eliminaciones |
| `clutches`, `clutchesWon` | número | |
| `utilityDamage` | número | daño con HE, molotov, incendiaria |
| `enemiesFlashed` | número | enemigos cegados al menos 1 s |
| `plants`, `defuses` | número | |
| `teamkills` | número | compañeros eliminados; los suicidios no cuentan |
| `roundsPlayed` | número | rondas empezadas |

Cada definición: [Estadísticas](statistics.md#the-scoreboard-line).

## Convenciones {#conventions}

Escritas en cada documento para que quien lo lea sepa lo que significan los números sin esta página:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Un ejemplo {#an-example}

De la demo sintética de dos rondas de las pruebas, acortado (`...` marca lo que se deja fuera):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

El orden de las claves dentro de `survivors`, `equipment` y `buy` no está fijado.
