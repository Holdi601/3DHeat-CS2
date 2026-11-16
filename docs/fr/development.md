---
title: "Développement"
nav_order: 15
lang: "fr"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Développement {#development}

## Structure {#layout}

| Chemin | Contenu |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2` : la vérification de version, puis la ligne de commande |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | les verbes et les options ; le regroupement des fichiers de démo en matchs ; le pool de travailleurs |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | un fichier de démo passé dans demoparser2 pour en faire un `RawPart` - [Lire une démo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | parties, chaînes, horloge, manches, équipes, lignes, éliminations, dégâts, aveuglements - [Construire un match](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | résumés de manche, tableau des scores, document de match, tableau des scores en texte - [Statistiques](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | la table Parquet avec ses indications `heat3d`, et le JSON - [La table de carte de chaleur](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | recherche de CS2 et de Source2Viewer, le maillage de collision dans le repère du visualiseur - [Export de la carte](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | un lecteur et un écrivain minimaux de glTF binaire (aucune dépendance au-delà de numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | la vérification de version et la mise à jour - [Mises à jour](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | les tests et la démo synthétique |
| `VERSION` | la version, sur une ligne |

Le flux des données :

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Utilisation depuis Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # the heatmap table as a pandas DataFrame
    kills = match.kills        # one row per death, with every flag
    doc = summary(match)       # the .match.json document as a dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` et `Match.blinds` sont des DataFrame pandas qui contiennent plus que ce que portent les sorties : positions et lieux de l'attaquant et de la victime pour chaque élimination, `utility` pour chaque coup - pour vos propres analyses.

## Tests {#tests}

```bash
python -m pytest
```

`pytest.ini` lance `tests/` en mode silencieux. Les tests n'ont besoin ni de démo, ni du jeu, ni de Source2Viewer : [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) construit à la main une démo, telle que demoparser2 la donnerait - deux manches, deux joueurs par camp (`ace`, `ash` de l'équipe Alpha ; `bob`, `ben` de Bravo), assez petite pour que chaque réponse soit connue :

- Manche 1, victoire des T par élimination : ace tue bob d'un headshot (l'ouverture), ben tue ace 1,9 s plus tard (un trade : la mort de bob est échangée), ash tue ben 3,1 s après - seul contre un, un clutch gagné.
- Manche 2, victoire des T par la bombe : ash pose sur A, personne ne meurt, la bombe explose.

`fixtures.halves` construit un match plus long fait de manches vides, les équipes sur leur premier côté ou échangées, avec le compteur de prolongation du jeu ou sans, pour la durée de la mi-temps et les manches pistolet.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) vérifie dessus : le gagnant, la raison, le score et les camps de chaque manche ; l'horloge qui part du match ; l'économie et la pose (son temps dans la manche, son lieu, l'explosion de la bombe) ; un site de pose toujours une lettre ou vide, jamais un numéro d'entité ; une manche à égalité décidée sans gagnant ; les manches pistolet à partir du changement de côté, la prolongation exclue, et seule la manche 1 sans changement ; les équipes sans noms de clan (`Started T` / `Started CT`) ; les ouvertures, les trades et les drapeaux ; un suicide qui n'est pas un teamkill, et l'ouverture transmise au première élimination d'ennemi ; `noscope` et `attackerBlind` dans la table et dans le document de match ; les dégâts comme vie perdue (60, puis 40 d'un 137 sur 40 points de vie) ; les chiffres du tableau des scores et le KAST ; les clutchs ; le tableau des scores en texte ; les événements de la table et leur emplacement (une détonation sans lieu propre, celui du lanceur dans `throwerPlace` ; l'explosion dans le camp qui a posé) ; que les positions sont en direct, étiquetées et ont des vecteurs de regard unitaires ; que le fichier écrit porte ses indications ; des parties mises en ordre quels que soient leurs noms ; une horloge de serveur redémarrée qui continue malgré tout ; et les lignes en double d'une manche restaurée résolues vers celle qui mène plus loin.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) vérifie que les démos dans des dossiers sont trouvées quelle que soit la casse de `.dem`, et qu'un match ne compte comme écrit que si sa table et son document de match le sont tous deux.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) vérifie les conversions de repère (les mètres de Source2Viewer vers les pouces du jeu, puis vers le repère du visualiseur, une rotation de déterminant 1), que les clips et le ciel sont retirés quelle que soit la casse et les surfaces nommées, la séparation sol / structure par la normale, et qu'un `.glb` écrit se relit à l'identique.

### La vérification du sol sur une vraie carte {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<une démo> HEAT3D_SOURCE2VIEWER=<l'interface CLI> python -m pytest
```

Quand les deux variables sont définies, `test_players_stand_on_the_exported_floor` s'exécute aussi : il convertit la démo, exporte sa carte depuis le jeu installé, et vérifie qu'au moins 98 % de 300 échantillons de position aléatoires ont du sol sous eux, avec une hauteur médiane au-dessus de ce sol inférieure à 5 unités ([Export de la carte](map-export.md#the-check-that-the-frame-is-right)).

## Conventions du code {#conventions-of-the-code}

- Les temps dans `match.py` sont des secondes de match, sauf le `time` d'une pose, en secondes dans sa manche, comme l'écrit le document de match ; les ticks ne deviennent des secondes que par `_Part.at`.
- Les camps sont des chaînes `T` / `CT` partout en dehors des données brutes de l'analyseur (`team_num` 2 / 3).
- Une nouvelle colonne de table va dans `ROW_COLUMNS` (et dans `NUMERIC` si elle est numérique) dans `match.py` ; `output.table` choisit son type Parquet d'après les ensembles `INT16`, `INT32`, `FLOAT64` et les drapeaux 0/1, float32 sinon.
- Changer ce que le visualiseur doit faire d'une colonne revient à changer `HINTS` dans `output.py`.

## Licence {#licence}

MIT. Paquets tiers et obligations imposées par les jeux : [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Les démos et les cartes ne font jamais partie du dépôt ; son `.gitignore` exclut `*.dem`, `*.parquet`, `*.match.json`, `*.glb` et les fichiers semblables par type.
