---
title: "Opdateringer"
nav_order: 14
lang: "da"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Opdateringer {#updates}

3DHeat CS2 holder sig selv opdateret fra dette repositoriums
[GitHub-udgivelser](https://github.com/Holdi601/3DHeat-CS2/releases). Kode:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Tjekket ved opstart {#the-check-at-start-up}

Hver `python -m heat3d_cs2 ...` spørger først, om der er kommet en nyere udgivelse,
før den overhovedet læser sine argumenter:

1. Den installerede version er filen `VERSION` i repositoriets rod (`0`, hvis den ikke kan læses).
2. Den nyeste udgivelse bliver spurgt hos
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, med en timeout på **5 sekunder**. Svaret bliver cachet i **6 timer** i
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (på systemer uden `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), så forespørgslen højst bliver sendt hver sjette time. "Ingen udgivelse endnu" (HTTP 404) bliver cachet ligesom et svar. Offline, rate-limiteret, bag en proxy - enhver anden fejl - fortsætter værktøjet med den version, det har, og intet bliver cachet.
3. Versioner bliver sammenlignet som tal: `v1.2.3` og `1.2.3` er ens, alt efter et `-` eller `+` bliver ignoreret, manglende dele tæller som 0.

Når en nyere udgivelse er kommet, siger det det på fejlstrømmen:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- I en terminal (både input- og fejlstrømmen er terminaler) spørger den. Enter, `y`, `yes`, `j` eller `ja` opdaterer; alt andet fortsætter uændret. Efter en opdatering **kører den samme kommando igen**, på den nye kode.
- Uden en terminal - en planlagt kørsel, en pipe - skriver den kun, hvor man opdaterer, og fortsætter: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` slår tjekket fra. Enhver værdi, der ikke er tom, `0`, `false` eller `no`, tæller som til.

## Opdatering efter anmodning {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Dette spørger altid GitHub (cachen bliver ikke brugt). Den skriver `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, eller
`<new> is out (this is <current>): <url>` og opdaterer derefter (medmindre `--check`).
Exitkode `1`, når en opdatering blev forsøgt og fejlede, ellers `0`.

## Sådan bliver en opdatering udført {#how-an-update-is-applied}

Det afhænger af, hvordan kopien blev installeret:

- **Et git-checkout** (der er en `.git` i roden, og `git` på `PATH`): `git pull --ff-only`. Det bliver afvist, mens sporede filer har lokale ændringer ("this checkout has local changes; commit or stash them, then run `git pull`"): det er nogens arbejde, og en opdatering bestemmer ikke, hvad der sker med det. Usporede filer blokerer ikke.
- **En downloadet kopi**: udgivelsens kildearkiv (GitHubs zipball) bliver downloadet og pakket ud i en midlertidig mappe - poster, der ville havne uden for den, springes over - og dens `VERSION` skal være den version, udgivelsen hævder, ellers bliver intet ændret ("the archive is version X, not Y"). Derefter bliver dens filer kopieret over mappen. Filer, der ikke er en del af udgivelsen - dine demoer, output, det virtuelle miljø, alt du har lavet - bliver aldrig rørt. Python-moduler, som udgivelsen ikke længere har, bliver slettet fra værktøjets egne pakker (`heat3d_*`-mapperne), så et forældet modul ikke kan skygge for sin afløser.

Hvis en opdatering fejler, bliver beskeden udskrevet, og værktøjet kører på den version, det har.
