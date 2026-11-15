---
title: Instalación
nav_order: 3
lang: "es"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalación {#installing}

¿Nuevo en la línea de comandos? Lee primero [Antes de empezar](before-you-start.md).

3DHeat CS2 es un paquete de Python que se ejecuta desde su propia carpeta. No hay nada que compilar ni
instalador; necesita Python, cuatro paquetes (más pytest para las pruebas) y, solo para la exportación
del mapa, Counter-Strike 2 instalado y la versión de línea de comandos de Source2Viewer.

## Obtener el código {#getting-the-code}

Descarga un archivo de una versión desde la
[página de versiones](https://github.com/Holdi601/3DHeat-CS2/releases) y descomprímelo, o, si tienes
Git, clona el repositorio:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Ambos tipos de copia pueden actualizarse solas (ver [Actualizaciones](updates.md)). La versión
instalada es la línea única del archivo `VERSION`.

Ejecuta todos los comandos desde esa carpeta: `python -m heat3d_cs2` encuentra el paquete porque está
en la carpeta actual. El paquete no se instala en `site-packages`.

## Python y los paquetes {#python-and-the-packages}

Python 3.10 o posterior. Un entorno virtual mantiene los paquetes aparte de todo lo demás. En Windows
(PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell se niega a ejecutar el script, ejecuta primero
`Set-ExecutionPolicy -Scope Process RemoteSigned` (solo dura en esa ventana). En Linux o macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funciona cuando `python -m heat3d_cs2 --help` imprime `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paquete | Mínimo | Para qué se usa | Licencia |
|---|---|---|---|
| `demoparser2` | 0.42 | leer archivos `.dem` (jugadores por tick, eventos del juego) | MIT |
| `pyarrow` | 15 | escribir la tabla Parquet | Apache-2.0 |
| `pandas` | 2.0 | las tablas intermedias | BSD-3-Clause |
| `numpy` | 1.24 | operaciones aritméticas sobre ellas | BSD-3-Clause |
| `pytest` | 8.0 | solo las pruebas | MIT |

Los comandos `demos` y `scoreboard` no necesitan nada más.

## Para la exportación del mapa: Counter-Strike 2 y la CLI de Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` lee el mapa del juego que tienes instalado y lo decodifica con la **línea de
comandos de Source2Viewer**, un programa aparte del proyecto
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (con licencia MIT).
No viene incluido y no se puede instalar con pip.

1. Descarga la versión **CLI** para tu sistema desde
   [las versiones de ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   y descomprímela donde quieras.
2. Haz que se pueda encontrar, de una de tres formas. Se prueban en este orden:
   1. `--source2viewer <ruta al ejecutable>` en la línea de comandos;
   2. la variable de entorno `HEAT3D_SOURCE2VIEWER` con la ruta del ejecutable;
   3. un ejecutable llamado `Source2Viewer-CLI` o `Source2Viewer-CLI.exe` en `PATH`.

   Un candidato se usa solo si su ruta existe. Si no se encuentra ninguno, el comando se detiene con
   `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set
   HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Definir la variable, por ejemplo:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Dónde se busca CS2 {#where-cs2-is-looked-for}

El mapa es un archivo `.vpk` dentro de la carpeta del juego:
`<biblioteca de Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<mapa>.vpk`.
Las bibliotecas de Steam se encuentran desde estas raíces, y desde cada `"path"` que aparece en el
`config\libraryfolders.vdf` de cada raíz:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Cuando Steam está en otro sitio, pasa la carpeta de CS2 con `--game` (la carpeta que contiene
`game\csgo`), o pasa la ruta del `.vpk` en lugar del nombre del mapa. Ver [Exportar el mapa](map-export.md).

## Comprobar la instalación {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Las pruebas se ejecutan sobre una demo sintética construida en código y no necesitan demo, juego ni
Source2Viewer (ver [Desarrollo](development.md)).

Cada inicio de `python -m heat3d_cs2` comprueba primero, como mucho cada seis horas, si hay una versión
más nueva; define `HEAT3D_NO_UPDATE=1` para desactivarlo (ver [Actualizaciones](updates.md)).
