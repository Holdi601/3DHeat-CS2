---
title: "La table de carte de chaleur"
nav_order: 8
lang: fr
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# La table de carte de chaleur (`<match>.parquet`) {#the-heatmap-table-parquet}

Un fichier Parquet par match : la position échantillonnée de chaque joueur vivant, et chaque événement à l'endroit où il s'est produit, une ligne chacun - une longue table que la visionneuse 3DHeat lit comme une carte de chaleur, et que tout autre outil lit comme une table ordinaire. Code :
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(le fichier), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(les lignes ; voir [Construire un match](building-matches.md)).

Le fichier est écrit avec une compression Snappy, en groupes de lignes de 256 000 lignes. Les lignes sont triées par `time`, puis par `event`. Seules les lignes situées dans un round (de la fin de son temps de gel au début du round suivant) figurent dans la table.

Sur la démo synthétique des tests, les lignes d'événements du premier round :

![lignes d'événements de la table](../assets/img/table-rows.svg)

Dans un conteneur `.3dheat`, la table est l'élément de rôle `table` ([Un fichier par match](output-container.md)).

## Colonnes {#columns}

Les colonnes, toujours dans cet ordre. Les colonnes de texte sont des chaînes à dictionnaire (`dictionary<int32, string>`) et ne sont jamais nulles : « pas de valeur » est une chaîne vide. Les colonnes numériques sont nulles là où une ligne n'a pas de valeur.

| Colonne | Type | Contenu |
|---|---|---|
| `match` | chaîne | le nom du match (`alpha-vs-bravo-m1`, ou `...-b` pour une deuxième chaîne) |
| `map` | chaîne | la carte, d'après l'en-tête de la démo (`de_x`) |
| `round` | int16 | le numéro du round, à partir de 1 |
| `roundId` | chaîne | `<match> #NN`, le numéro du round sur deux chiffres (`alpha-vs-bravo-m1 #07`) : unique entre matchs, la session de la visionneuse |
| `phase` | chaîne | `freeze` pendant le temps de gel du round (depuis la fin du round précédent), `live` jusqu'à ce que le round soit décidé, `after` pendant que les gagnants chassent et que les perdants économisent |
| `time` | float64 | secondes depuis le début du match (le début en direct de son premier fichier), sur une horloge unique pour tous ses fichiers |
| `roundTime` | float32 | secondes depuis la fin du temps de gel de ce round ; négatif pendant le temps de gel |
| `event` | chaîne | ce que représente la ligne - voir [Événements](#events) |
| `player` | chaîne | le nom du joueur (pour chaque événement, le joueur est précisé plus bas) |
| `steamid` | chaîne | le Steam ID du joueur (64 bits, en texte) |
| `side` | chaîne | `T` ou `CT` dans ce round ; vide quand le joueur n'était dans aucun camp |
| `team` | chaîne | le nom d'équipe du joueur (ou `Started T` / `Started CT`) ; pour `explode`, l'équipe qui a posé |
| `x`, `y`, `z` | float32 | position dans les propres coordonnées du jeu : pouces (unités du jeu), **Z vers le haut**, repère droitier |
| `dirX`, `dirY`, `dirZ` | float32 | où le joueur regarde, un vecteur unitaire dans le même repère ; positions seulement |
| `health` | int16 | 0-100 ; positions, et sur `hurt` ce qui reste après le coup |
| `armor` | int16 | 0-100 ; positions, et sur `hurt` ce qui reste après le coup |
| `money` | int32 | l'argent du joueur ; positions seulement |
| `equipment` | int32 | la valeur de ce que le joueur porte ; positions seulement |
| `weapon` | chaîne | l'arme telle que le jeu la nomme (`AK-47`, `M4A1-S`, `Knife` pour tous les skins de couteau) |
| `place` | chaîne | le nom de lieu de la carte à la position de la ligne (`BombsiteA`, `CTSpawn`) ; vide pour les détonations de grenades : la démo ne nomme aucun lieu où une grenade a explosé |
| `throwerPlace` | chaîne | le nom de lieu du lanceur quand la grenade a explosé ; détonations de grenades seulement |
| `other` | chaîne | l'autre joueur d'un kill, d'une mort, d'un coup ou d'un flash |
| `damage` | float32 | vie perdue ; `hurt` seulement |
| `duration` | float32 | secondes d'aveuglement ; `blind` seulement |
| `headshot` | int8 | 0/1 ; `kill` et `death` seulement |
| `opening` | int8 | 0/1, le premier kill d'un ennemi du round ; `kill` et `death` seulement |
| `traded` | int8 | 0/1. Pour un `kill` : c'était un trade kill. Pour un `death` : elle a été vengée dans les 5 s. `kill` et `death` seulement. |
| `noscope` | int8 | 0/1, le kill a été fait avec une arme à lunette tirée sans lunette (le `noscope` de l'événement) ; `kill` et `death` seulement |
| `attackerBlind` | int8 | 0/1, le tueur était aveuglé quand il a tué (le `attackerblind` de l'événement) ; `kill` et `death` seulement |
| `won` | int8 | 0/1, si le camp de cette ligne a gagné le round ; nul quand `side` est vide |
| `buy` | chaîne | l'achat du camp de cette ligne pour ce round : `pistol`, `eco`, `force`, `full` |
| `detail` | chaîne | chaque champ de l'événement que les autres colonnes ne portent pas, sous forme d'objet JSON (noms propres au jeu) : les balles d'un tir (`fire_bullets` : origine, angles, imprécision, dispersion, indice de recul, graine...), `dominated`, `revenge`, `attackerinair`, `wipe`... d'une mort, `defindex` d'un objet, rien pour un pas |
| `text` | chaîne | une ligne de chat ; `chat` seulement |
| `entity` | int32 | l'entité de la grenade : le vol d'un `throw` (lignes `grenade`), sa détonation et les joueurs qu'elle a aveuglés la partagent |
| `hitgroup` | chaîne | où la balle a touché (`head`, `chest`, ...) ; `hurt`, `kill`, `death` |
| `armorDamage` | int16 | armure perdue ; `hurt` seulement |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | où sur le corps la balle a touché, dans le repère de la victime en mètres (x vers l'avant, y vers le haut depuis les pieds, z vers la droite) : le rayon du tir (`fire_bullets`, sinon l'œil et la vue de l'attaquant) tracé jusqu'à un corps posé comme la victime se tenait et s'accroupissait, sur la partie que `hitgroup` nomme ; `hurt` seulement |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | la direction du tir dans le même repère ; `hitMiss` à quelle distance (m) le rayon a manqué la partie nommée (0 : à travers) ; `hitFrom` `bullet` ou `aim` |
| `penetrated` | int16 | murs que la balle mortelle a traversés ; `kill` et `death` |
| `throughSmoke` | int8 | 0/1, tué à travers une fumée ; `kill` et `death` |
| `distance` | float32 | la distance du kill telle que le jeu la compte (mètres) ; `kill` et `death` |
| `assister` | chaîne | qui a assisté ; `kill` et `death` |
| `flash`, `flashAlpha` | float32 | secondes de flash restantes, et son intensité ; positions |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1 ; positions |
| `zoom`, `duck`, `moveType` | | le niveau de zoom de la lunette, à quel point le joueur est accroupi (0-1), le type de mouvement du jeu ; positions |
| `spottedBy` | chaîne | les Steam IDs des ennemis qui voient ce joueur, séparés par `\|` ; positions |
| `inventory` | chaîne | tout ce que porte le joueur, séparé par `\|` ; positions |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | le chargeur et la réserve de l'arme tenue ; tirs dans la rafale en cours ; positions |
| `punchPitch`, `punchYaw` | float32 | le recul de visée, en degrés ; positions |
| `ping` | int16 | millisecondes ; positions |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | les compteurs de tableau des scores du jeu pour le match jusqu'ici ; positions |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | argent dépensé dans ce round et dans le match ; valeur d'équipement au début du round ; positions |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, l'état du joueur au temps de la ligne, événements compris : casque, kit de désamorçage, une armure quelconque, lunette (depuis le dernier échantillon de position du joueur jusqu'à la ligne), flashé (dans un `blind` qui l'a touché) ; chaque ligne qui nomme un joueur |
| `state_utility` | int16 | grenades portées à ce moment (d'après `inventory`) ; chaque ligne qui nomme un joueur |
| `state_weapon` | chaîne | l'arme en main à ce moment (sur un `death`, celle de la victime, là où `weapon` est celle du tueur) ; chaque ligne qui nomme un joueur |
| `earn_round_cs2` | int16 | ce que le round a rapporté : sur `round_end`, la récompense de victoire ou le bonus de défaite (avec le bonus du camp qui a posé), sur `plant` et `defuse` les 300 $ du joueur |

## Événements {#events}

Quel joueur une ligne nomme, où elle se situe, et quelles colonnes elle remplit.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won` et `buy` sont remplies sur chaque ligne ; `inventory`, `money`, `equipment` et
les colonnes `state_*` sur chaque ligne qui nomme un joueur (les événements les prennent
au dernier échantillon de position du joueur).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Aussi renseigné |
|---|---|---|---|
| `position` | le joueur | le joueur (pieds) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (tenue), `place`, et tout l'état du joueur (les colonnes à partir de `flash`) - même pendant le temps de gel |
| `kill` | le tueur | où se tenait le tueur | `other` (victime), `weapon`, `headshot`, `opening`, `traded` (un trade kill), `noscope`, `attackerBlind`, `place` |
| `death` | la victime | où la victime est tombée | `other` (tueur ; vide pour le monde), `weapon`, `headshot`, `opening`, `traded` (vengée), `noscope`, `attackerBlind`, `place` |
| `hurt` | la victime | où la victime a été touchée | `other` (attaquant), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - les coups entre coéquipiers et ceux du monde aussi |
| `shot` | le tireur | d'où le coup a été tiré | `weapon`, `place`, `detail` (le compte que le jeu donne des balles) |
| `slash` | le joueur | où le couteau a frappé | `weapon` = `Knife` |
| `grenade` | le lanceur | la grenade en vol, à l'échantillonnage des joueurs et là où elle s'est arrêtée | `weapon` (la grenade), `entity` |
| `throw` | le lanceur | d'où la grenade a été lancée | `weapon` (la grenade), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | le lanceur | où elle a explosé | `weapon`, `throwerPlace` (le lieu du lanceur à cet instant) ; `place` reste vide |
| `blind` | le joueur flashé | où il se tenait | `other` (le flasheur), `duration`, `weapon` = `Flashbang`, `entity`, `place` - les coéquipiers flashés aussi |
| `plant` | le poseur | où il a posé | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | le désamorceur | où il a désamorcé | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | chaque joueur qui a joué le round | où le joueur se tenait en dernier | `won`, `earn_round_cs2` (ce que le round leur a rapporté : la hausse de l'argent du camp jusqu'au prochain temps de gel là où les règles le permettent, sinon celle des règles), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | le poseur (avec son Steam ID), camp `T`, l'équipe qui a posé | la position de la pose | `weapon` = `C4 Explosive`, `place` (celui du poseur au moment de la pose : là où la bombe reposait) ; son temps est celui de l'explosion |
| `chat` | l'expéditeur | où il se trouvait | `text` |
| tout autre événement de jeu qui concerne un joueur, sous le nom du jeu : `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | le joueur | où il se trouvait (pour un événement de grenade : où elle était) | `weapon` (d'un objet), `entity`, `detail` (chaque champ de l'événement) |

Ce qui est dedans et ce qui ne l'est pas :

- Les lignes **position** sont les joueurs vivants d'un camp, hors temps de gel et échauffement, toutes les `--every` ticks (huit par seconde par défaut).
- Les lignes **kill** sont les kills par un ennemi seulement - ni teamkill, ni suicide, ni mort due au monde. Les lignes **death** sont toutes les morts, celles-là comprises.
- Les lignes **explode** sont chaque bombe posée qui a explosé, d'après le `bomb_exploded` de la démo : aussi en phase après, quand les T avaient déjà gagné par élimination. Une démo sans cet événement en reçoit une pour chaque round gagné par la bombe, à la fin du round.
- Les lignes **hurt** et **blind** sont entre ennemis seulement.
- **shot** laisse de côté les couteaux et le C4 ; les grenades sont des lignes **throw**.
- **molotov** couvre les molotovs et les incendiaires (le début du feu).
- Les dégâts entre coéquipiers, les flashs des coéquipiers et des spectateurs, les événements du temps de gel et tout ce qui se passe entre les rounds ne figurent pas dans la table.

Un exemple détaillé, tiré de la démo synthétique des tests (une fumée lancée, un premier kill en headshot, des trades) :

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

La mort de bob est vengée par le kill de ace par ben 1,9 s plus tard (la ligne `death` de bob : traded 1 ; la ligne `kill` de ben : un trade kill, traded 1) ; le second coup sur bob valait 137 dégâts sur 40 points de vie, donc il compte 40.

## Les indications `heat3d` du pied de fichier {#the-heat3d-footer-hints}

Le pied du fichier Parquet (métadonnées de schéma clé/valeur) porte des consignes de lecture sous la clé **`heat3d`**, un objet JSON :

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Entrée | Indique |
|---|---|
| `version`, `kind` | la version des indications (1) et ce qui les a écrites (`cs2-demo`) |
| `axes.up` | le Z du fichier est vers le haut |
| `axes.flipY` | inverser le Y du fichier (voir plus bas) |
| `axes.scale` | 1 : les positions sont utilisées telles quelles, en unités du jeu |
| `entity.size` | un joueur fait **32 unités** de large - la largeur d'un joueur CS2 - la taille qu'un replay en boîtes lui donne |
| `columns.x` / `y` / `z` | les colonnes de position |
| `columns.time`, `timeUnit` | `time`, en secondes |
| `columns.personId` | le joueur est la personne |
| `columns.teamId` | le camp est le groupe (donc T et CT, et non les noms d'équipes, colorent les groupes) |
| `columns.sessionId` | chaque round (`roundId`) est une session |
| `columns.lookMode` et `dirX`-`dirZ` | la direction du regard est un vecteur dans ces colonnes |
| `columns.extra` | les colonnes à garder comme filtres, par ordre d'utilité |

Une visionneuse qui connaît la clé ouvre le fichier sans rien régler. Les autres l'ignorent. Pour la lire vous-même :

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Axes et unités {#axes-and-units}

Les coordonnées sont celles du jeu : **pouces** (une unité du jeu ; un joueur mesure 72 unités debout et 32 de large), **Z vers le haut**, et repère droitier.

Une visionneuse dont le monde a Y vers le haut doit dessiner le (x, y, z) du jeu sous la forme **(x, z, -y)** - Z devient la hauteur et Y est inversé. C'est une rotation, pas un miroir. Dessinée comme un monde gaucher à Z vers le haut, sous la forme (x, z, y), chaque carte sort en miroir, le site A du mauvais côté ; `flipY: true` est ce que les indications demandent pour l'éviter. L'[export de la carte](map-export.md) écrit sa géométrie déjà dans le repère (x, z, -y), dans les mêmes unités, donc elle se place sous la table sans aucun réglage.

Les distances dans la visionneuse sont affichées en mètres ; avec une échelle de 1, ce sont des unités du jeu. Multipliez par 0,0254 pour obtenir des mètres.

## Taille {#size}

Les positions dominent : une dizaine de joueurs fois 8 échantillons par seconde de jeu en direct avec le `--every 8` par défaut, moins pour les joueurs morts et le temps de gel. Diviser `--every` par deux double leur nombre ; les événements ne changent pas.
