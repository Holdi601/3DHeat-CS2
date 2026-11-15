---
title: Actualizaciones
nav_order: 14
lang: "es"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Actualizaciones {#updates}

3DHeat CS2 se mantiene al día desde las
[versiones de GitHub](https://github.com/Holdi601/3DHeat-CS2/releases) de este repositorio. Código:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## La comprobación al arrancar {#the-check-at-start-up}

Cada `python -m heat3d_cs2 ...` pregunta primero si hay una versión más nueva, antes incluso de leer sus
argumentos:

1. La versión instalada es el archivo `VERSION` en la raíz del repositorio (`0` si no se puede leer).
2. La versión más reciente se pide a
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, con un **tiempo de espera de 5
   segundos**. La respuesta se guarda en caché durante **6 horas** en
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (en sistemas sin `LOCALAPPDATA`:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), así que la petición se hace como mucho cada seis horas.
   "Ninguna versión publicada" (HTTP 404) se guarda en caché como una respuesta más. Sin conexión, con
   límite de peticiones, detrás de un proxy - cualquier otro fallo - la herramienta sigue con la versión que
   tiene, y no se guarda nada en caché.
3. Las versiones se comparan como números: `v1.2.3` y `1.2.3` son iguales; lo que va después de un `-` o un
   `+` se ignora; las partes que faltan cuentan como 0.

Cuando hay una versión nueva, lo indica en el flujo de errores:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- En una terminal (tanto la entrada como el flujo de errores son terminales) pregunta. Enter, `y`, `yes`,
  `j` o `ja` actualizan; cualquier otra cosa sigue sin cambios. Tras una actualización, **el mismo comando se
  vuelve a ejecutar**, con el código nuevo.
- Sin terminal - una ejecución programada, una tubería - solo imprime dónde actualizar y sigue:
  `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` desactiva la comprobación. Cualquier valor distinto de vacío, `0`, `false` o `no`
cuenta como activado.

## Actualizar bajo petición {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Esto siempre pregunta a GitHub (no se usa la caché). Imprime `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, o
`<new> is out (this is <current>): <url>` y luego actualiza (salvo con `--check`). Código de salida `1`
cuando se intentó una actualización y falló, `0` en otro caso.

## Cómo se aplica una actualización {#how-an-update-is-applied}

Depende de cómo se instaló la copia:

- **Una copia de Git** (hay un `.git` en la raíz y `git` en `PATH`): `git pull --ff-only`. Se rechaza mientras
  los archivos con seguimiento tengan cambios locales ("this checkout has local changes; commit or stash them,
  then run `git pull`"): son trabajo de alguien, y una actualización no decide qué pasa con ellos. Los archivos
  sin seguimiento no bloquean.
- **Una copia descargada**: el archivo de código fuente de la versión (el zipball de GitHub) se descarga y se
  descomprime en una carpeta temporal - las entradas que caerían fuera de ella se omiten - y su `VERSION` debe
  ser la versión que dice la versión, o no se cambia nada ("the archive is version X, not Y"). Después, sus
  archivos se copian sobre la carpeta. Los archivos que no forman parte de la versión - tus demos, salidas,
  entorno virtual, cualquier cosa que hayas hecho - nunca se tocan. Los módulos de Python que la versión ya no
  tiene se borran de los paquetes propios de la herramienta (las carpetas `heat3d_*`), para que un módulo viejo
  no tape a su sustituto.

Si una actualización falla, el mensaje se imprime y la herramienta sigue con la versión que tiene.
