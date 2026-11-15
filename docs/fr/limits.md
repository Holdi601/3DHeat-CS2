---
title: "Limites"
nav_order: 13
lang: fr
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Limites {#limits}

Ce que le convertisseur suppose, ce qu'il ne gère pas et ce qui n'est pas vérifié. Chaque point vient du code tel qu'il est aujourd'hui.

## Ce qu'il lit {#what-it-reads}

- **Fichiers `.dem` non compressés seulement.** `.dem.zst`, `.dem.bz2`, `.rar` et `.zip` doivent être décompressés d'abord. L'extension est reconnue quelle que soit la casse (`.dem`, `.DEM`), dans les dossiers comme pour les fichiers donnés par leur nom.
- **Matchs de désamorçage de bombe.** Les raisons de fin de round, la pose de la bombe et le site, les types d'achat et les rounds pistolet sont ceux du désamorçage de bombe. Les cartes avec otages, Wingman et les autres modes ne sont pas traités à part et ne sont pas vérifiés.
- **64 ticks par seconde** sont supposés (`TICKRATE = 64`) pour tout temps calculé à partir des ticks ; les serveurs CS2 tournent à 64.
- **Une démo prise sur le serveur** (SourceTV) est supposée : elle contient tous les joueurs. Un enregistrement côté client (démo POV) n'a pas été essayé.

## Matchs et rounds {#matches-and-rounds}

- **Les fichiers sont regroupés par nom.** Les parties d'un même match doivent partager un nom, à part le suffixe `-pN` / `_pN` ; les fichiers d'un même match sous des noms sans rapport deviennent des matchs séparés, et des fichiers de même nom dans des dossiers différents sont regroupés ensemble (puis découpés en chaînes s'ils ne se suivent pas).
- **Le match en direct commence au dernier `round_announce_match_start`** d'un fichier. Un round de couteau qui n'est pas suivi de cette annonce est compté comme un round.
- **Les heures de fin de round sont précises à un échantillon près** (`--every` ticks, soit 1/8 s par défaut), parce que la décision est lue dans l'état du jeu échantillonné. Un `--every` très grand peut manquer une courte fenêtre entre la fin d'un round et le début du suivant, et laisser le round de côté comme incomplet.
- **Égalités.** Un round à égalité (statut de victoire 1, raison 10) est décidé sans gagnant : `winner` est vide et aucun camp ne l'a gagné. Aucune égalité n'a été rencontrée dans une vraie démo pour vérifier cela ; c'est vérifié sur la démo synthétique.
- **Les rounds coupés** par la fin d'un fichier sont laissés de côté (`incomplete`), sans être devinés ; les rounds avant le premier des fichiers sont listés comme `missing`.
- **Les rounds pistolet** suivent la durée de mi-temps que montre l'enregistrement : là où les camps changent de côté pour la première fois entre deux rounds réglementaires consécutifs. Un enregistrement qui ne montre pas ce changement (il commence après la mi-temps, ou finit avant, ou un round de part et d'autre est manquant) ne connaît que le round 1 comme round pistolet. La prolongation n'en a pas.
- **Équipes.** Une équipe est le nom de clan vu le plus souvent pour ses joueurs. Sans noms de clan, les équipes sont `Started T` et `Started CT`. Un joueur qui change d'équipe en cours de match garde une seule équipe.

## Événements {#events}

- **Tout ce que l'analyseur propose est lu**, à ces exceptions près : la vitesse des joueurs (l'analyseur la calcule à partir des positions ; elle n'est pas dans la démo), la voix (audio, `parse_voice`), et le `weapon_fire` de la bombe (le début d'une pose, que `bomb_beginplant` porte déjà). Les trajectoires de grenades sont gardées à l'échantillonnage des joueurs (`--every`) et à l'endroit où chaque grenade s'est arrêtée, et non à chaque tick.
- **Les lignes hors round** (échauffement, une pause entre le début du match et le premier freeze time au-delà de deux minutes) sont laissées de côté dans la table ; les événements qui ne concernent aucun joueur figurent tous dans les `events` du document de match.
- **Les lignes de détonation** (`smoke`, `flash`, `he`, `molotov`, `decoy`) n'ont pas de `place` : la démo nomme des lieux pour les joueurs, pas pour les grenades. Le lieu du lanceur à cet instant figure dans `throwerPlace`.
- **Le site de la pose** vient de la zone de bombe où le jeu dit que le poseur se tenait, sinon du nom de lieu du poseur, sinon d'une autre pose dans la même zone dans le même fichier. Si aucune de ces sources ne le dit, `site` est vide.
- **Une mort due au monde** (une chute, la bombe) n'a pas d'attaquant : ni kill, ni teamkill, ni ouverture ; c'est une mort.

## Statistiques {#statistics}

- **Les rounds joués** viennent de qui avait une position dans la première seconde après le temps de gel. Un joueur qui se connecte plus tard dans un round ne compte pas comme l'ayant joué (ses kills comptent toujours).
- **Survie pour le KAST** : un joueur tué pendant la phase après n'a pas survécu pour le KAST, alors que la liste des rounds le cite encore parmi les survivants.
- **Les deux joueurs d'un 1v1** peuvent se voir créditer un clutch dans un même round ; voir [Statistiques](statistics.md#clutches).
- **Les dégâts d'utilitaire** sont ceux des grenades HE, molotovs et incendiaires ; un kill ou un coup par un flash ou un leurre lancé n'est pas un dégât d'utilitaire.

## Export de la carte {#map-export}

- Demande que le jeu soit installé (ou le `.vpk`) et l'interface en ligne de commande de Source2Viewer ; rien n'est téléchargé.
- N'exporte que `world_physics` ; les clips et le ciel sont laissés de côté parce que leur nom contient `clip` ou `sky`, quelle que soit la casse.
- Le sol se distingue de la structure par la seule composante normale de la face (composante Z de 0,7 ou plus) : une rampe raide est une structure et un toit plat est du sol.
- Le fichier est en pouces, et non en mètres.

## Mémoire et temps {#memory-and-time}

- Un match est gardé entièrement en mémoire pendant sa construction, dans un processus de travail par match. Avec beaucoup de travailleurs et un petit `--every`, la mémoire s'additionne : baissez `--jobs` si la machine manque de mémoire.
- Un match n'est écrit qu'une fois construit : d'abord le `.parquet`, puis le `.match.json`. Une exécution arrêtée entre les deux laisse une table sans son document de match ; un match ne compte comme écrit qu'avec les deux, donc la prochaine exécution le reconvertit. Les matchs pas encore commencés sont simplement repris par l'exécution suivante.
