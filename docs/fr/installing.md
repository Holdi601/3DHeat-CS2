---
title: "Installation"
nav_order: 3
lang: fr
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installation {#installing}

Vous débutez avec la ligne de commande ? Lisez d'abord [Avant de commencer](before-you-start.md).

3DHeat CS2 est un paquet Python qui se lance depuis son propre dossier. Rien à compiler et pas de programme d'installation ; il faut Python, quatre paquets (plus pytest pour les tests), et - seulement pour l'export de la carte - Counter-Strike 2 installé et la version en ligne de commande de Source2Viewer.

## Obtenir le code {#getting-the-code}

Téléchargez une archive de version depuis la
[page des versions](https://github.com/Holdi601/3DHeat-CS2/releases) et décompressez-la, ou, si vous avez Git, clonez le dépôt :

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Les deux types de copie peuvent se mettre à jour elles-mêmes (voir [Mises à jour](updates.md)). La version installée est la ligne unique du fichier `VERSION`.

Lancez chaque commande depuis ce dossier : `python -m heat3d_cs2` trouve le paquet parce qu'il se trouve dans le répertoire courant. Le paquet n'est pas installé dans `site-packages`.

## Python et les paquets {#python-and-the-packages}

Python 3.10 ou plus récent. Un environnement virtuel tient les paquets à l'écart du reste. Sous Windows (PowerShell) :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell refuse d'exécuter le script, lancez d'abord
`Set-ExecutionPolicy -Scope Process RemoteSigned` (cela ne vaut que pour cette fenêtre). Sous Linux ou macOS :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tout fonctionne quand `python -m heat3d_cs2 --help` affiche `usage: heat3d_cs2 ...`.

`requirements.txt` :

| Paquet | Minimum | Utilisé pour | Licence |
|---|---|---|---|
| `demoparser2` | 0.42 | lecture des fichiers `.dem` (joueurs par tick, événements de jeu) | MIT |
| `pyarrow` | 15 | écriture de la table Parquet | Apache-2.0 |
| `pandas` | 2.0 | les tables intermédiaires | BSD-3-Clause |
| `numpy` | 1.24 | le calcul sur celles-ci | BSD-3-Clause |
| `pytest` | 8.0 | les tests seulement | MIT |

Les commandes `demos` et `scoreboard` n'ont besoin de rien d'autre.

## Pour l'export de la carte : Counter-Strike 2 et l'interface en ligne de commande de Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` lit la carte depuis le jeu que vous avez installé, et la décode avec la **ligne de commande de Source2Viewer**, un programme distinct du projet
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (licence MIT). Il n'est pas fourni avec l'outil et ne s'installe pas avec pip.

1. Téléchargez la version **CLI** pour votre système depuis
   [les versions de ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   et décompressez-la où vous voulez.
2. Indiquez où la trouver, de trois façons. Elles sont essayées dans cet ordre :
   1. `--source2viewer <chemin de l'exécutable>` sur la ligne de commande ;
   2. la variable d'environnement `HEAT3D_SOURCE2VIEWER` définie avec le chemin de l'exécutable ;
   3. un exécutable nommé `Source2Viewer-CLI` ou `Source2Viewer-CLI.exe` dans `PATH`.

   Un candidat n'est utilisé que si son chemin existe. Si rien n'est trouvé, la commande s'arrête avec
   `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Exemple de définition de la variable :

```bash
# Windows (PowerShell), pour la session en cours
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Où CS2 est cherché {#where-cs2-is-looked-for}

La carte est une archive `.vpk` dans le dossier du jeu :
`<bibliothèque Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<carte>.vpk`.
Les bibliothèques Steam sont trouvées à partir de ces racines, et de chaque `"path"` listé dans le fichier `config\libraryfolders.vdf` de chaque racine :

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Quand Steam est ailleurs, indiquez le dossier de CS2 lui-même avec `--game` (le dossier qui contient `game\csgo`), ou donnez le chemin du `.vpk` à la place du nom de la carte. Voir [Export de la carte](map-export.md).

## Vérifier l'installation {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Les tests tournent sur une démo synthétique construite dans le code et n'ont besoin ni de démo, ni du jeu, ni de Source2Viewer (voir [Développement](development.md)).

À chaque lancement de `python -m heat3d_cs2`, une vérification a lieu, au plus toutes les six heures, pour savoir si une version plus récente est sortie ; définissez `HEAT3D_NO_UPDATE=1` pour la désactiver (voir [Mises à jour](updates.md)).
