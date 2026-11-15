---
title: "Mises à jour"
nav_order: 14
lang: fr
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Mises à jour {#updates}

3DHeat CS2 se tient à jour à partir des [versions publiées](https://github.com/Holdi601/3DHeat-CS2/releases) de ce dépôt. Code :
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## La vérification au démarrage {#the-check-at-start-up}

Chaque `python -m heat3d_cs2 ...` demande d'abord si une version plus récente est sortie, avant même de lire ses arguments :

1. La version installée est le fichier `VERSION` à la racine du dépôt (`0` s'il ne peut pas être lu).
2. La version la plus récente est demandée à
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, avec un délai de **5 secondes**. La réponse est mise en cache pendant **6 heures** dans
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (sur les systèmes sans `LOCALAPPDATA` : `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), donc la requête n'est faite qu'au plus toutes les six heures. « Rien de publié » (HTTP 404) est mis en cache comme une réponse. Hors ligne, limité en débit, derrière un proxy - tout autre échec - l'outil continue avec la version qu'il a, et rien n'est mis en cache.
3. Les versions sont comparées comme des nombres : `v1.2.3` et `1.2.3` sont égales, tout ce qui suit un `-` ou un `+` est ignoré, les parties manquantes comptent pour 0.

Quand une version plus récente est sortie, cela est indiqué sur le flux d'erreur :

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Dans un terminal (l'entrée et le flux d'erreur sont tous deux des terminaux), l'outil demande. Entrée, `y`, `yes`, `j` ou `ja` met à jour ; tout le reste continue sans changement. Après une mise à jour, **la même commande s'exécute à nouveau**, sur le nouveau code.
- Sans terminal - une exécution planifiée, un tube - il indique seulement où mettre à jour et continue : `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` désactive la vérification. Toute valeur autre que vide, `0`, `false` ou `no` compte comme activée.

## Mettre à jour sur demande {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Cela interroge toujours GitHub (le cache n'est pas utilisé). Il affiche `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, ou
`<new> is out (this is <current>): <url>`, puis met à jour (sauf avec `--check`).
Code de sortie `1` quand une mise à jour a été tentée et a échoué, `0` sinon.

## Comment une mise à jour est appliquée {#how-an-update-is-applied}

Cela dépend de la façon dont la copie a été installée :

- **Une copie git** (il y a un `.git` à la racine et `git` dans `PATH`) : `git pull --ff-only`. Elle est refusée tant que des fichiers suivis ont des modifications locales (« this checkout has local changes; commit or stash them, then run `git pull` ») : ce sont le travail de quelqu'un, et une mise à jour ne décide pas de leur sort. Les fichiers non suivis ne bloquent pas.
- **Une copie téléchargée** : l'archive source de la version (le zipball de GitHub) est téléchargée et décompressée dans un dossier temporaire - les entrées qui sortiraient de ce dossier sont ignorées - et son `VERSION` doit être la version annoncée par la version, sinon rien ne change (« the archive is version X, not Y »). Ses fichiers sont alors copiés par-dessus le dossier. Les fichiers qui ne font pas partie de la version - vos démos, sorties, environnement virtuel, tout ce que vous avez créé - ne sont jamais touchés. Les modules Python que la version ne contient plus sont supprimés des paquets de l'outil (les dossiers `heat3d_*`), pour qu'un module périmé ne fasse pas d'ombre à son remplaçant.

Si une mise à jour échoue, le message est affiché et l'outil continue avec la version qu'il a.
