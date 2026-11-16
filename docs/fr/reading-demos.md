---
title: "Lire une démo"
nav_order: 5
lang: "fr"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Lire une démo {#reading-a-demo}

Ce qui est extrait d'un fichier `.dem`, avant toute interprétation. Code :
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Une démo CS2 est l'enregistrement du serveur lui-même (SourceTV) : chaque joueur, à chaque tick, 64 ticks par seconde (`TICKRATE = 64`). Elle est lue avec
[demoparser2](https://github.com/LaihoE/demoparser) en trois appels, et le résultat est gardé tel quel, dans un `RawPart` :

| Champ | Contient |
|---|---|
| `path` | le fichier |
| `map` | `map_name` de l'en-tête de la démo (`de_x`) ; vide si l'en-tête n'en a pas |
| `samples` | une ligne par joueur et par tick échantillonné : les champs du joueur et des règles ci-dessous, plus `tick`, `steamid`, `name` |
| `events` | nom d'événement -> ses lignes, avec les champs des joueurs préfixés `user_`, `attacker_`, `assister_` comme les nomme l'analyseur |

Rien dans `demo.py` ne décide ce qu'est un round ni qui l'a gagné ; c'est le rôle de [Construire un match](building-matches.md).

## Les ticks échantillonnés {#the-sampled-ticks}

`parse_ticks` est appelé pour les ticks `0, N, 2N, ...` jusqu'à 4 000 000 (`LAST_TICK`, bien au-delà de n'importe quel match - 17 heures à 64 ticks par seconde), où *N* est `--every` (8 par défaut). L'analyseur s'arrête à la fin de la démo. Chaque joueur présent à un tick échantillonné donne une ligne, qu'il soit vivant, mort, spectateur ou coach ; le filtrage se fait plus tard.

Le pas d'échantillonnage compte au-delà de la densité de la carte de chaleur : le moment où un round est décidé se lit sur ces échantillons (voir [Construire un match](building-matches.md#rounds)), donc les heures de fin de round sont précises à un pas près (1/8 s par défaut).

### Champs du joueur {#player-fields}

| Propriété | Devient |
|---|---|
| `X`, `Y`, `Z` | la position, en unités du jeu (pouces), Z vers le haut. demoparser2 donne l'origine du joueur, c'est-à-dire ses pieds. |
| `yaw`, `pitch` | la direction du regard (degrés), transformée en vecteur unitaire |
| `health`, `armor_value` | vie, armure |
| `team_num` | le camp : 2 = T, 3 = CT ; tout autre (spectateurs, 0, 1) n'est pas un camp |
| `team_clan_name` | le nom de l'équipe tel que le serveur l'affiche, utilisé pour nommer les équipes |
| `active_weapon_name` | l'arme tenue, telle que le jeu la nomme (`AK-47`, `Karambit`) |
| `is_alive` | si le joueur est vivant - seuls les joueurs vivants deviennent des positions |
| `last_place_name` | le nom de lieu propre à la carte (`BombsiteA`) |
| `balance` | argent |
| `current_equip_value` | la valeur de ce que le joueur porte |

### Champs des règles de jeu {#game-rules-fields}

Lus en même temps, une fois par ligne de joueur (ils sont identiques pour tous à un tick donné) :

| Propriété | Utilisée pour |
|---|---|
| `game_time` | l'horloge du serveur, en secondes |
| `total_rounds_played` | le compte des rounds, qui se poursuit à travers les fichiers d'un match |
| `round_win_status` | qui a gagné le round qui vient d'être joué : 1 égalité, 2 T, 3 CT |
| `round_win_reason` | comment (le `CSRoundEndReason` du jeu) |
| `team_rounds_total` | le score de chaque camp |
| `is_warmup_period` | l'échauffement est laissé de côté partout |
| `is_freeze_period` | le temps de gel est laissé de côté pour les positions |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | la prolongation en cours, 0 en temps réglementaire : les rounds de prolongation ne sont pas des rounds pistolet (l'analyseur n'a pas de nom plus court) |

## Les événements {#the-events}

Chaque événement ci-dessous est lu quand la démo le déclare (`list_game_events`), avec `X`, `Y`, `Z`, `team_num`, `last_place_name` et `which_bomb_zone` (la zone de bombe où le joueur se tient : 0 aucune, 1 A, 2 B) pour chaque joueur que l'événement nomme, et `total_rounds_played` et `is_warmup_period` du jeu à ce tick :

| Événement | Devient |
|---|---|
| `player_death` | kills et morts ; utilise `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | dégâts ; utilise `dmg_health` (dégâts infligés à la vie), `health` (vie restante), `weapon` |
| `player_blind` | joueurs flashés ; utilise `blind_duration` |
| `weapon_fire` | tirs et lancers de grenades ; utilise `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | où les grenades ont explosé ; utilise les `x`, `y`, `z` propres à l'événement (il n'a pas de nom de lieu pour ce point, seulement celui du lanceur) |
| `bomb_planted` | la pose ; utilise la `which_bomb_zone` et le lieu du poseur, et `site` (le numéro d'entité de la zone) |
| `bomb_defused` | le désamorçage |
| `bomb_exploded` | quand la bombe a explosé : le temps de la ligne `explode` |
| `round_freeze_end` | où chaque round commence |
| `round_prestart` | où le temps après un round décidé se termine |
| `round_announce_match_start` | où le match en direct commence |

## Deux faits sur les démos qui décident de leur lecture {#two-facts-about-demos-that-decide-how-they-are-read}

- **Un match peut être découpé en plusieurs fichiers**, et les noms des fichiers ne disent pas leur ordre. Le compte des rounds (`total_rounds_played`) se poursuit à travers eux, et en général l'horloge du serveur aussi : les fichiers peuvent donc être remis en ordre d'après leur contenu.
- **Un enregistrement peut commencer avant le match** : échauffement, redémarrage, round de couteau. Le match commence au **dernier** `round_announce_match_start` d'un fichier ; avant lui, tout est laissé de côté, et l'échauffement est laissé de côté partout.
