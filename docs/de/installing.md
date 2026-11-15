---
title: "Installation"
nav_order: 3
lang: de
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installation {#installing}

Neu in der Kommandozeile? Lies zuerst [Bevor du anfängst](before-you-start.md).

3DHeat CS2 ist ein Python-Paket, das aus seinem eigenen Ordner gestartet wird. Es gibt nichts zu bauen
und kein Installationsprogramm; es braucht Python, vier Pakete (plus pytest für die Tests) und - nur für
den Karten-Export - Counter-Strike 2, installiert, und die Kommandozeilen-Version von Source2Viewer.

## Den Code holen {#getting-the-code}

Lade ein Release-Archiv von der [Releases-Seite](https://github.com/Holdi601/3DHeat-CS2/releases)
herunter und entpacke es, oder, wenn du Git hast, klone das Repository:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Beide Arten von Kopie können sich selbst aktualisieren (siehe [Updates](updates.md)). Die installierte
Version ist die eine Zeile in der Datei `VERSION`.

Führe jeden Befehl aus diesem Ordner aus: `python -m heat3d_cs2` findet das Paket, weil es im aktuellen
Ordner liegt. Das Paket wird nicht in `site-packages` installiert.

## Python und die Pakete {#python-and-the-packages}

Python 3.10 oder neuer. Eine virtuelle Umgebung hält die Pakete von allem anderen getrennt. Unter
Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Wenn PowerShell das Skript nicht ausführen will, führe zuerst
`Set-ExecutionPolicy -Scope Process RemoteSigned` aus (es gilt nur für dieses Fenster). Unter Linux oder
macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Es funktioniert, wenn `python -m heat3d_cs2 --help` `usage: heat3d_cs2 ...` ausgibt.

`requirements.txt`:

| Paket | Mindestversion | Wofür | Lizenz |
|---|---|---|---|
| `demoparser2` | 0.42 | das Lesen der `.dem`-Dateien (Spieler pro Tick, Spielereignisse) | MIT |
| `pyarrow` | 15 | das Schreiben der Parquet-Tabelle | Apache-2.0 |
| `pandas` | 2.0 | die Tabellen dazwischen | BSD-3-Clause |
| `numpy` | 1.24 | das Rechnen damit | BSD-3-Clause |
| `pytest` | 8.0 | nur die Tests | MIT |

Die Befehle `demos` und `scoreboard` brauchen nichts weiter.

## Für den Karten-Export: Counter-Strike 2 und die CLI von Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` liest die Karte aus dem Spiel, das du installiert hast, und dekodiert sie mit
der **Kommandozeile von Source2Viewer**, einem eigenen Programm aus dem Projekt
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (MIT-lizenziert). Es ist
nicht mitgeliefert und lässt sich nicht mit pip installieren.

1. Lade den **CLI**-Build für dein System von
   [den ValveResourceFormat-Releases](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   herunter und entpacke ihn, wo du willst.
2. Mache ihn auffindbar, auf einem von drei Wegen. Sie werden in dieser Reihenfolge probiert:
   1. `--source2viewer <Pfad zur ausführbaren Datei>` in der Befehlszeile;
   2. die Umgebungsvariable `HEAT3D_SOURCE2VIEWER` mit dem Pfad der ausführbaren Datei;
   3. eine ausführbare Datei namens `Source2Viewer-CLI` oder `Source2Viewer-CLI.exe` im `PATH`.

   Ein Kandidat wird nur genommen, wenn sein Pfad existiert. Wird keiner gefunden, bricht der Befehl ab
   mit `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set
   HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Die Variable setzen, zum Beispiel:

```bash
# Windows (PowerShell), für die aktuelle Sitzung
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Wo nach CS2 gesucht wird {#where-cs2-is-looked-for}

Die Karte ist ein `.vpk`-Archiv im Ordner des Spiels:
`<Steam-Bibliothek>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<Karte>.vpk`.
Die Steam-Bibliotheken werden von diesen Wurzeln aus gefunden, und von jedem `"path"`, der in der
`config\libraryfolders.vdf` jeder Wurzel steht:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Liegt Steam woanders, gib den CS2-Ordner selbst mit `--game` an (den Ordner, der `game\csgo` enthält),
oder gib den Pfad der `.vpk` statt des Kartennamens an. Siehe [Karten-Export](map-export.md).

## Prüfen, ob die Installation stimmt {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Die Tests laufen mit einem synthetischen Demo, das im Code gebaut wird, und brauchen kein Demo, kein
Spiel und keine Source2Viewer (siehe [Entwicklung](development.md)).

Jeder Start von `python -m heat3d_cs2` prüft zuerst, höchstens alle sechs Stunden, ob ein neueres Release
erschienen ist; mit `HEAT3D_NO_UPDATE=1` schaltest du das ab (siehe [Updates](updates.md)).
