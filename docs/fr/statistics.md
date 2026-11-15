---
title: "Statistiques"
nav_order: 7
lang: "fr"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistiques {#statistics}

Ce que chaque joueur a fait dans un match, et comment chaque round s'est passé : le tableau des scores et la liste des rounds du [document du match](output-match-json.md). Code :
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Tout est compté à partir du match construit comme dans [Construire un match](building-matches.md) : ses enregistrements de kills, ses dégâts (vie perdue, ennemis seulement), ses aveuglements (ennemis seulement) et ses lignes.

![le tableau des scores en texte d'un match synthétique](../assets/img/scoreboard.svg)

## Les conventions {#the-conventions}

Quand le jeu lui-même ne définit pas un chiffre, voici les définitions. Elles sont aussi écrites dans chaque document de match, sous `conventions`.

| Terme | Définition |
|---|---|
| **Trade** | Une mort est *échangée* (traded) quand son tueur est tué par un coéquipier de la victime dans les **5 s** ; ce kill est un *trade kill*. |
| **Ouverture** | Le premier kill d'un ennemi du round pendant qu'il est en direct. Un teamkill, un suicide ou une mort due au monde qui précède est ignoré. |
| **KAST** | La part des rounds où un joueur a fait un **K**ill, une **A**ssistance (une assistance au flash compte), a **S**urvécu, ou a été **T**raded (échangé). |
| **Dégâts** | Vie réellement perdue, ennemis seulement : un headshot de 137 dégâts sur un joueur à 40 points de vie vaut 40. |
| **Clutch** | Être le dernier joueur vivant de son camp alors que des ennemis sont encore debout ; gagné quand le camp gagne le round. |
| **Achat** | Par camp, d'après la valeur moyenne d'équipement à la fin du temps de gel : le premier round de chaque mi-temps réglementaire est un round pistolet (le round 1, et le round qui suit la mi-temps, tant que le match l'a joué) ; la prolongation n'en a pas ; ensuite moins de 1 500 $ eco, moins de 4 000 $ force, sinon full. |

## Qui a commencé chaque round {#who-started-each-round}

Plusieurs chiffres demandent de savoir qui a joué un round. Les **joueurs de départ** d'un round sont, par camp, chaque joueur ayant une ligne de position vivante dans la seconde qui suit la position la plus ancienne de ce round (c'est-à-dire dans la première seconde après la fin du temps de gel). Les **rounds joués** d'un joueur sont le nombre de rounds qu'il a commencés. S'il n'en a commencé aucun (il n'a jamais eu une telle ligne), le nombre de rounds du match est utilisé à la place, pour qu'aucune division ne soit par zéro.

## La ligne de tableau des scores {#the-scoreboard-line}

Une entrée par joueur (voir [le document du match](output-match-json.md#players) pour les noms des champs). « Kill ennemi » ci-dessous désigne un kill avec un attaquant, qui n'est ni un teamkill ni un suicide (la mort de la victime elle-même).

| Champ | Compte |
|---|---|
| `kills` | kills ennemis, de la phase en direct et de la phase après |
| `deaths` | chaque mort : par des ennemis, des coéquipiers, soi-même ou le monde |
| `assists` | kills ennemis que ce joueur a assistés sans flash (l'assistant ne doit pas être le tueur) |
| `flashAssists` | kills ennemis que ce joueur a assistés avec un flash |
| `diff` | kills - morts |
| `adr` | dégâts (vie perdue, ennemis seulement, les deux phases) / rounds joués, à une décimale |
| `kast` | 100 x (rounds avec un kill, une assistance ou une assistance au flash, une survie ou une mort échangée) / rounds joués, à une décimale. *Survie* : être un joueur de départ du round qui n'est pas mort pendant celui-ci, dans l'une ou l'autre phase. |
| `headshotPct` | 100 x kills en headshot / kills, à une décimale ; 0 sans kill |
| `openingKills`, `openingDeaths` | duels d'ouverture gagnés et perdus |
| `tradeKills` | kills qui ont vengé la mort d'un coéquipier |
| `tradedDeaths` | morts qui ont été échangées |
| `multiKills` | rounds avec 2, 3, 4 et 5 kills ennemis (`2k`, `3k`, `4k`, `5k`) ; plus de cinq compte comme `5k`. Les deux phases comptent. |
| `clutches`, `clutchesWon` | clutchs joués et gagnés (ci-dessous) |
| `utilityDamage` | dégâts faits avec les grenades HE, molotovs et incendiaires, à une décimale |
| `enemiesFlashed` | ennemis aveuglés pendant **au moins 1,0 s** par les flashs de ce joueur |
| `plants`, `defuses` | poses et désamorçages de bombe (lignes de la table) |
| `teamkills` | coéquipiers tués. Un suicide - attaquant et victime sont le même joueur, une grenade à soi par exemple - n'en est pas un : ce n'est qu'une mort. |
| `roundsPlayed` | rounds commencés, comme ci-dessus |

Les joueurs sont listés par nom d'équipe (ordre alphabétique), et dans une équipe par `diff`, puis par `kills`, du meilleur au moins bon.

Remarques sur les cas limites :

- Un kill pendant la phase après - les gagnants chassant un joueur qui économise - compte comme un kill, une mort, pour l'ADR, les multi-kills et le KAST, comme n'importe quel autre.
- Les wallbangs sont comptés par joueur en interne, mais ne sont pas écrits dans le document du match ; chaque kill de la liste des rounds indique s'il en était un.
- La partie *échangé* du KAST crédite la victime d'une mort échangée dans ce round.
- Les teamkills et les suicides ajoutent une mort à la victime mais aucun kill à personne ; un teamkill ajoute à `teamkills` du tueur, un suicide n'ajoute rien d'autre.

## Clutchs {#clutches}

Pour chaque round, les joueurs de départ des deux camps sont considérés comme vivants, et les kills en direct du round sont parcourus dans l'ordre. Après chaque mort, la victime est retirée, et chaque camp est examiné : un camp qui ne compte plus qu'**un** joueur, et qui a encore au moins un ennemi debout, donne un clutch à ce joueur **contre** le nombre d'ennemis encore vivants à cet instant. Chaque joueur a au plus un clutch par round ; il est **gagné** quand le camp de ce joueur gagne le round.

Conséquences de la définition :

- Les deux camps peuvent avoir un clutch dans un même round. Si un camp tombe d'abord à un joueur (un 1v3, par exemple) et que l'autre camp est ensuite lui aussi réduit à un, le second joueur est en clutch 1v1 de son côté.
- `against` est le compte au moment où le joueur est devenu le dernier, et non à la fin.
- Les kills de la phase après ne sont pas parcourus : ils ne démarrent ni ne modifient aucun clutch.

## Survivants {#survivors}

Les **survivants** d'un round sont, par camp, ses joueurs de départ moins tous ceux qui sont morts pendant qu'il était en direct. Un joueur tué pendant la phase après, en économisant, reste un survivant dans la liste des rounds - mais n'a pas *survécu* pour le KAST.

## La liste des rounds {#the-round-list}

Chaque round du document du match porte son résultat, son score, ses camps, son économie, sa pose, ses survivants, ses clutchs et ses kills dans l'ordre ; voir [Le document du match](output-match-json.md#rounds).

## Le tableau des scores en texte {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` affiche ces chiffres par équipe ; voir [Commandes](commands.md#scoreboard---a-match-as-text).
