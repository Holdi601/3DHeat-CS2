---
title: "Le document du match"
nav_order: 9
lang: "fr"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Le document du match (`<match>.match.json`) {#the-match-document-matchjson}

Un document JSON par match, à côté de sa table : les équipes, le score, chaque round avec son résultat, l'économie, la pose, les kills, les clutchs et les survivants, et la ligne de tableau des scores de chaque joueur. C'est ce que charge l'onglet Match de la visionneuse 3DHeat.
Code : `summary()` dans
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) ;
les chiffres sont définis sur [Statistiques](statistics.md).

Le fichier est en UTF-8, indenté d'une espace, et garde les caractères non ASCII (noms de joueurs et d'équipes) tels quels. Les temps sont en secondes, arrondis à trois décimales pour les rounds et à deux pour les kills et la pose.

## Le document {#the-document}

| Champ | Type | Contenu |
|---|---|---|
| `format` | chaîne | toujours `heat3d-cs2-match` - ce qui permet à un lecteur de reconnaître le fichier |
| `version` | nombre | `3`. Un document version 1 donne le `time` d'une pose en secondes de match ; à partir de 2, c'est en secondes dans le round, comme pour un kill. 3 ajoute les champs à partir de `header` et le temps de gel dans la table. |
| `match` | chaîne | le nom du match, tel que les fichiers sont nommés |
| `map` | chaîne | la carte (`de_x`) |
| `demos` | chaîne[] | les fichiers de démo dont il est issu, noms de fichiers seulement, dans l'ordre du match |
| `teams` | chaîne[] | les noms d'équipes dans l'ordre d'apparition (round 1 : le côté T en premier) |
| `score` | objet | nom d'équipe -> rounds gagnés : le score du dernier round |
| `rounds` | objet[] | chaque round complet, dans l'ordre - [ci-dessous](#rounds) |
| `incomplete` | nombre[] | numéros de rounds coupés par la fin d'une démo et laissés de côté |
| `missing` | nombre[] | numéros de rounds avant le premier que contiennent les démos : `[1, 2]` quand l'enregistrement commence au round 3 |
| `halfLength` | nombre ou null | nombre de rounds dans une mi-temps réglementaire, à partir du moment où les camps changent de côté pour la première fois (`12` dans le format à 24 rounds) ; null quand l'enregistrement ne montre pas le changement |
| `pistolRounds` | nombre[] | les rounds pistolet avec lesquels `buy` est compté : le round 1, et le round après la mi-temps quand `halfLength` est connu ; jamais un round de prolongation |
| `players` | objet[] | le tableau des scores - [ci-dessous](#players) |
| `conventions` | objet | les définitions derrière les chiffres, [ci-dessous](#conventions) |
| `header` | objet | l'en-tête de la première démo tel que l'analyseur le donne : nom du serveur, version du patch, version de la démo, carte |
| `profiles` | objet | Steam ID -> ce qui reste identique pour un joueur pendant le match : `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (la dernière vue) |
| `playerInfo` | objet[] | chaque joueur listé par les démos, coachs et casters compris : Steam ID, nom, numéro d'équipe |
| `skins`, `itemDrops` | objet[] | skins d'armes et objets obtenus, quand la démo les a (les démos de tournoi issues de la diffusion n'en ont pas) |
| `chat` | objet[] | chaque ligne de chat du match : temps, round, joueur, camp, texte |
| `events` | objet[] | chaque événement de jeu qui ne concerne aucun joueur, dans l'ordre du temps, avec tous ses champs : bips et phases de round, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (les réglages du serveur quand ils changent), les plans de caméra du réalisateur de diffusion, `cs_win_panel_match`, ... |
| `state` | objet[] | l'état du jeu quand il change : temps, champ, valeur - temps morts (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), la bombe (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, les joueurs vivants, `match_start_time` et `round_start_time` du serveur |
| `selfCheck` | objet | `completeness` : où est allé chaque élément de la démo - pour chaque nom d'événement, classe de propriété, message réseau, image et table de chaînes, ses compteurs `seen`, `decoded`, `partial`, `raw` et `lost`, les fichiers annexes écrits, le total `lost` (0 sauf avec `--no-bulk`), les propriétés que l'analyseur liste mais ne sait pas lire (`unreadProps`). La convention : [Les convertisseurs gardent tout](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) ; les fichiers annexes : la section Complétude du README |

## Rounds {#rounds}

| Champ | Type | Contenu |
|---|---|---|
| `number` | nombre | le round, à partir de 1 |
| `start` | nombre | secondes de match à la fin du temps de gel |
| `end` | nombre | secondes de match quand le round a été décidé |
| `until` | nombre | secondes de match quand le round suivant a commencé (la fin de la phase après) |
| `winner` | chaîne | `T` ou `CT` ; vide pour une égalité |
| `winnerTeam` | chaîne | le nom d'équipe du camp gagnant ; vide pour une égalité |
| `reason` | chaîne | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` ou `other` |
| `score` | objet | nom d'équipe -> rounds gagnés après celui-ci |
| `sides` | objet | nom d'équipe -> `T` / `CT` pour ce round |
| `equipment` | objet | camp -> valeur totale de l'équipement de ses joueurs vivants à la fin du temps de gel, en dollars |
| `buy` | objet | camp -> `pistol`, `eco`, `force` ou `full` |
| `plant` | objet ou null | la pose de la bombe : `site` (`A` ou `B` ; vide quand la démo ne le dit pas), `time` (secondes **dans le round**, comme pour un kill), `player`, `steamid`, `x`, `y`, `z` (unités du jeu), `place` (le nom de lieu du poseur : là où la bombe reposait) |
| `survivors` | objet | camp -> noms des joueurs de départ encore vivants quand le round a été décidé, triés |
| `clutches` | objet[] | chacun : `player`, `steamid`, `side`, `against` (ennemis encore vivants quand le joueur est devenu le dernier), `won` |
| `kills` | objet[] | chaque mort du round, dans l'ordre - ci-dessous |

Comment ces éléments sont trouvés : [Construire un match](building-matches.md#rounds) ;
clutchs et survivants : [Statistiques](statistics.md#clutches).

### Les kills d'un round {#a-rounds-kills}

Chaque mort du round, phase après comprise :

| Champ | Type | Contenu |
|---|---|---|
| `time` | nombre | secondes **dans le round** (depuis la fin du temps de gel) |
| `attacker`, `attackerSide` | chaîne | le tueur et son camp ; vide pour le monde |
| `victim`, `victimSide` | chaîne | la victime et son camp |
| `assister` | chaîne ou null | le joueur qui a assisté, ou null |
| `flashAssist` | booléen | l'assistance était un flash |
| `weapon` | chaîne | telle que le jeu la nomme |
| `headshot` | booléen | |
| `wallbang` | booléen | la balle a traversé quelque chose |
| `throughSmoke` | booléen | le kill a eu lieu à travers une fumée |
| `noscope` | booléen | une arme à lunette a tiré sans lunette |
| `attackerBlind` | booléen | le tueur était aveuglé par un flash |
| `opening` | booléen | le premier kill d'un ennemi du round |
| `traded` | booléen | cette mort a été vengée dans les 5 s |
| `trade` | booléen | ce kill a vengé un coéquipier dans les 5 s |
| `teamkill` | booléen | attaquant et victime du même camp, deux joueurs différents |
| `suicide` | booléen | attaquant et victime sont le même joueur (une grenade à soi, par exemple) ; pas un teamkill |
| `after` | booléen | le kill a eu lieu après la décision du round |
| `place` | chaîne | où se trouvait la **victime** (le nom de lieu de la carte) |

## Joueurs {#players}

Une entrée par joueur, par nom d'équipe, puis du meilleur au moins bon selon kills moins morts, puis kills :

| Champ | Type | Contenu |
|---|---|---|
| `name`, `steamid`, `team` | chaîne | qui |
| `kills`, `deaths` | nombre | |
| `assists`, `flashAssists` | nombre | assistances sans et avec flash |
| `diff` | nombre | kills - morts |
| `adr` | nombre | dégâts moyens par round joué, vie perdue |
| `kast` | nombre | pourcentage de rounds joués avec un kill, une assistance, une survie ou une mort échangée |
| `headshotPct` | nombre | pourcentage de kills qui étaient des headshots |
| `openingKills`, `openingDeaths` | nombre | duels d'ouverture gagnés et perdus |
| `tradeKills`, `tradedDeaths` | nombre | trade kills ; morts échangées |
| `multiKills` | objet | `{"2k": n, "3k": n, "4k": n, "5k": n}` : rounds avec autant de kills |
| `clutches`, `clutchesWon` | nombre | |
| `utilityDamage` | nombre | dégâts avec HE, molotov, incendiaire |
| `enemiesFlashed` | nombre | ennemis aveuglés pendant au moins 1 s |
| `plants`, `defuses` | nombre | |
| `teamkills` | nombre | coéquipiers tués ; les suicides ne comptent pas |
| `roundsPlayed` | nombre | rounds commencés |

Toutes les définitions : [Statistiques](statistics.md#the-scoreboard-line).

## Conventions {#conventions}

Écrites dans chaque document pour qu'un lecteur sache ce que signifient les chiffres sans cette page :

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Un exemple {#an-example}

Tiré de la démo synthétique de deux rounds des tests, raccourci (`...` marque ce qui est omis) :

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

L'ordre des clés dans `survivors`, `equipment` et `buy` n'est pas fixé.
