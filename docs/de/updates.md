---
title: "Updates"
nav_order: 14
lang: de
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Updates {#updates}

3DHeat CS2 hält sich aus den [GitHub-Releases](https://github.com/Holdi601/3DHeat-CS2/releases) dieses
Repositorys aktuell. Code:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Die Prüfung beim Start {#the-check-at-start-up}

Jedes `python -m heat3d_cs2 ...` fragt zuerst, ob ein neueres Release erschienen ist, noch bevor es seine Argumente liest:

1. Die installierte Version ist die Datei `VERSION` im Wurzelordner des Repositorys (`0`, wenn sie nicht gelesen
   werden kann).
2. Das neueste Release wird bei
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest` angefragt, mit einem Timeout von **5 Sekunden**.
   Die Antwort wird **6 Stunden** lang in
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` zwischengespeichert (auf Systemen ohne `LOCALAPPDATA`:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), sodass höchstens alle sechs Stunden angefragt wird. „Noch nichts
   veröffentlicht“ (HTTP 404) wird wie eine Antwort zwischengespeichert. Offline, rate-limitiert, hinter einem Proxy -
   bei jedem anderen Fehler arbeitet das Werkzeug mit der Version weiter, die es hat, und nichts wird zwischengespeichert.
3. Versionen werden als Zahlen verglichen: `v1.2.3` und `1.2.3` sind gleich, alles nach einem `-` oder `+` wird
   ignoriert, fehlende Teile zählen als 0.

Ist ein neueres Release erschienen, sagt es das im Fehlerkanal:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- In einem Terminal (sowohl die Eingabe als auch der Fehlerkanal sind Terminals) wird gefragt. Enter, `y`, `yes`, `j`
  oder `ja` aktualisieren; alles andere arbeitet unverändert weiter. Nach einem Update läuft **derselbe Befehl noch
  einmal**, mit dem neuen Code.
- Ohne Terminal - ein geplanter Lauf, eine Pipe - wird nur ausgegeben, wo man aktualisiert, und es wird weitergemacht:
  `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` schaltet die Prüfung ab. Jeder Wert außer leer, `0`, `false` oder `no` gilt als an.

## Auf Wunsch aktualisieren {#updating-on-request}

```bash
python -m heat3d_update            # auf das neueste Release aktualisieren
python -m heat3d_update --check    # nur sagen, ob eines erschienen ist
```

Das fragt immer bei GitHub nach (der Zwischenspeicher wird nicht benutzt). Es gibt aus `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.` oder
`<new> is out (this is <current>): <url>` und aktualisiert dann (außer mit `--check`). Exit-Code `1`, wenn ein Update
versucht wurde und fehlschlug, sonst `0`.

## Wie ein Update angewendet wird {#how-an-update-is-applied}

Es hängt davon ab, wie die Kopie installiert wurde:

- **Ein Git-Checkout** (im Wurzelordner gibt es ein `.git`, und `git` ist im `PATH`): `git pull --ff-only`. Es wird
  abgelehnt, solange verfolgte Dateien lokale Änderungen haben („this checkout has local changes; commit or stash them,
  then run `git pull`“): das ist die Arbeit jemandes, und ein Update entscheidet nicht, was damit passiert. Nicht
  verfolgte Dateien blockieren es nicht.
- **Eine heruntergeladene Kopie**: das Quellarchiv des Releases (das ZIP von GitHub) wird heruntergeladen und in einen
  temporären Ordner entpackt - Einträge, die außerhalb davon landen würden, werden übersprungen -, und seine `VERSION`
  muss die Version sein, die das Release angibt, sonst wird nichts geändert („the archive is version X, not Y“). Dann
  werden seine Dateien über den Ordner kopiert. Dateien, die nicht zum Release gehören - deine Demos, Ausgaben, die
  virtuelle Umgebung, alles, was du selbst gemacht hast - werden nie angefasst. Python-Module, die das Release nicht
  mehr hat, werden aus den eigenen Paketen des Werkzeugs gelöscht (den Ordnern `heat3d_*`), damit ein veraltetes Modul
  seinen Ersatz nicht verdeckt.

Schlägt ein Update fehl, wird die Meldung ausgegeben, und das Werkzeug arbeitet mit der Version weiter, die es hat.
