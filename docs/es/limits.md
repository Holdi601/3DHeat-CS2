---
title: Límites
nav_order: 13
lang: es
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Límites {#limits}

Lo que supone el convertidor, lo que no maneja y lo que no está verificado. Cada punto viene del código
tal como está ahora.

## Lo que lee {#what-it-reads}

- **Solo archivos `.dem` sin comprimir.** `.dem.zst`, `.dem.bz2`, `.rar` y `.zip` hay que descomprimirlos
  antes. La extensión se reconoce sin distinguir mayúsculas (`.dem`, `.DEM`), en carpetas igual que en
  archivos dados por nombre.
- **Partidas de desactivación de bomba.** Las causas de fin de ronda, la colocación de la bomba y su
  sitio, los tipos de compra y las rondas de pistola son los del modo de desactivación de bomba. Los
  mapas de rehenes, Wingman y otros modos no se tratan de forma especial y no están verificados.
- **Se supone 64 ticks por segundo** (`TICKRATE = 64`) para todo tiempo calculado a partir de ticks;
  los servidores de CS2 van a 64.
- **Se supone una demo del servidor** (SourceTV): tiene a todos los jugadores. No se probó una grabación
  del lado del cliente (demo POV).

## Partidas y rondas {#matches-and-rounds}

- **Los archivos se agrupan por nombre.** Las partes de una misma partida deben compartir nombre salvo
  por un sufijo `-pN` / `_pN`; los archivos de una misma partida con nombres no relacionados se
  convierten en partidas separadas, y los archivos del mismo nombre en carpetas distintas se agrupan
  juntos (y luego se dividen en cadenas si no continúan una de otra).
- **La partida en vivo empieza en el último `round_announce_match_start`** de un archivo. Una ronda de
  cuchillos que no va seguida de ese anuncio se cuenta como una ronda.
- **Los tiempos de fin de ronda son exactos a una muestra** (ticks de `--every`, 1/8 s por defecto),
  porque la decisión se lee del estado del juego muestreado. Un `--every` muy grande puede pasar por
  alto una ventana corta entre el final de una ronda y el inicio de la siguiente, y dejar la ronda fuera
  como incompleta.
- **Empates.** Una ronda empatada (estado de victoria 1, causa 10) se decide sin ganador: `winner` queda
  vacío y ningún bando la gana. No se encontró ningún empate en una demo real con que compararla; se
  comprueba con la sintética.
- **Las rondas cortadas** por el final de un archivo se dejan fuera (`incomplete`), no se adivinan; las
  rondas anteriores a la primera de los archivos se listan como `missing`.
- **Rondas de pistola.** Siguen la duración de la mitad que muestra la grabación: donde los bandos
  cambian de lado por primera vez entre dos rondas reglamentarias consecutivas. Una grabación que no
  muestra ese cambio (empieza después del descanso, termina antes, o falta una ronda a uno de sus
  lados) solo conoce la ronda 1 como ronda de pistola. La prórroga no tiene ninguna.
- **Equipos.** Un equipo es el nombre de clan que más se ve entre sus jugadores. Sin nombres de clan, los
  equipos son `Started T` y `Started CT`. Un jugador que cambia de equipo a mitad de partida conserva un
  solo equipo.

## Eventos {#events}

- **Se lee todo lo que ofrece el analizador**, con estas excepciones: la velocidad de los jugadores (el
  analizador la deriva de las posiciones; no está en la demo), la voz (audio, `parse_voice`) y el
  `weapon_fire` de la bomba (el inicio de una colocación, que tiene `bomb_beginplant`). Los vuelos de
  granada se guardan con el muestreo de los jugadores (`--every`) y en el punto donde se detuvo cada
  granada, no en cada tick.
- **Las filas fuera de una ronda** (calentamiento, una pausa entre el inicio de la partida y el primer
  tiempo de congelación que pasa de dos minutos) se dejan fuera de la tabla; los eventos que no son de
  ningún jugador están todos en `events` del documento de la partida.
- **Las filas de detonación** (`smoke`, `flash`, `he`, `molotov`, `decoy`) no tienen `place`: la demo
  nombra lugares para los jugadores, no para las granadas. El lugar del lanzador en ese momento está en
  `throwerPlace`.
- **El sitio de una colocación** sale de la zona de bomba en la que el juego dice que estaba el
  colocador; si no, del nombre del lugar del colocador; si no, de otra colocación en la misma zona del
  mismo archivo. Si ninguno de estos lo dice, `site` queda vacío.
- **Una muerte a manos del mundo** (una caída, la bomba) no tiene atacante: ni eliminación, ni
  compañero abatido, ni apertura; es solo una muerte.

## Estadísticas {#statistics}

- **Las rondas jugadas** salen de quién tuvo una posición en el primer segundo después del tiempo de
  congelación. Un jugador que se conecta más tarde en una ronda no cuenta como que la jugó (sus
  eliminaciones sí cuentan).
- **Supervivencia para el KAST**: un jugador eliminado en la fase posterior no sobrevivió para el KAST,
  aunque la lista de rondas lo nombre entre los supervivientes.
- **Ambos jugadores de un 1v1** pueden tener un clutch acreditado en una misma ronda; ver
  [Estadísticas](statistics.md#clutches).
- **El daño de utilidad** son las granadas HE, los molotov y las incendiarias; una eliminación o un golpe
  con un destello o un señuelo lanzados no es daño de utilidad.

## Exportación del mapa {#map-export}

- Necesita el juego instalado (o el `.vpk`) y la CLI de Source2Viewer; no descarga nada.
- Exporta solo `world_physics`; los clips y el cielo se dejan fuera por tener `clip` o `sky` en su nombre,
  sin distinguir mayúsculas.
- El suelo se distingue de la estructura solo por la normal de la cara (componente Z de 0,7 o más), así
  que una rampa empinada es estructura y un techo plano es suelo.
- El archivo está en pulgadas, no en metros.

## Memoria y tiempo {#memory-and-time}

- Una partida se mantiene completa en memoria mientras se construye, en un trabajador por partida. Con
  muchos trabajadores y un `--every` pequeño, la memoria se acumula: baja `--jobs` si una máquina se
  queda corta.
- Una partida se escribe solo cuando está construida: primero el `.parquet`, después el `.match.json`.
  Una ejecución detenida entre las dos deja una tabla sin su documento de partida; una partida cuenta
  como escrita solo con ambos, así que la siguiente ejecución la convierte de nuevo. Las partidas que aún
  no han empezado las recoge la siguiente ejecución.
