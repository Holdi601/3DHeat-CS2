---
title: "Päivitykset"
nav_order: 14
lang: "fi"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Päivitykset {#updates}

3DHeat CS2 pitää itsensä ajan tasalla tämän repositorion
[GitHub-julkaisuista](https://github.com/Holdi601/3DHeat-CS2/releases). Koodi:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Tarkistus käynnistyksessä {#the-check-at-start-up}

Jokainen `python -m heat3d_cs2 ...` kysyy ensin, onko uudempi julkaisu ilmestynyt, ennen kuin
se edes lukee argumenttejaan:

1. Asennettu versio on tiedosto `VERSION` repositorion juuressa (`0`, jos sitä ei voi lukea).
2. Uusin julkaisu kysytään osoitteesta
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, **5 sekunnin**
   aikarajalla. Vastaus tallennetaan välimuistiin **6 tunniksi** tiedostoon
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (järjestelmissä ilman `LOCALAPPDATA`:a:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), joten pyyntö tehdään enintään kuuden tunnin
   välein. "Ei vielä julkaistu" (HTTP 404) tallennetaan välimuistiin kuten mikä tahansa vastaus.
   Offline-tilassa, pyyntörajan yli, välityspalvelimen takana - mikä tahansa muu virhe - työkalu
   jatkaa sillä versiolla, joka sillä on, eikä mitään tallenneta välimuistiin.
3. Versiot verrataan lukuina: `v1.2.3` ja `1.2.3` ovat samat, kaikki `-`:n tai `+`:n jälkeen
   ohitetaan, puuttuvat osat lasketaan nollaksi.

Kun uudempi julkaisu on ilmestynyt, siitä ilmoitetaan virhevirrassa:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Terminaalissa (sekä syöte että virhevirta ovat terminaaleja) kysytään. Enter, `y`, `yes`, `j` tai
  `ja` päivittää; mikä tahansa muu jatkaa muuttumattomana. Päivityksen jälkeen **sama komento
  ajetaan uudelleen**, uudella koodilla.
- Ilman terminaalia - ajastettu ajo, putki - se vain tulostaa, mistä päivittää, ja jatkaa:
  `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` kytkee tarkistuksen pois. Mikä tahansa arvo muu kuin tyhjä, `0`, `false` tai
`no` on päällä.

## Päivitys pyynnöstä {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Tämä kysyy aina GitHubilta (välimuistia ei käytetä). Se tulostaa `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, tai
`<new> is out (this is <current>): <url>` ja päivittää sitten (ellei `--check`).
Poistumiskoodi `1`, kun päivitys yritettiin ja epäonnistui, muuten `0`.

## Miten päivitys tehdään {#how-an-update-is-applied}

Se riippuu siitä, miten kopio asennettiin:

- **Git-kopio** (juuressa on `.git` ja `git` on `PATH`:issa): `git pull --ff-only`. Se hylätään, kun
  seurattuihin tiedostoihin on paikallisia muutoksia ("this checkout has local changes; commit or
  stash them, then run `git pull`"): ne ovat jonkun työtä, eikä päivitys päätä, mitä niille tapahtuu.
  Seuraamattomat tiedostot eivät estä sitä.
- **Ladattu kopio**: julkaisun lähdearkisto (GitHubin zipball) ladataan ja puretaan väliaikaiseen
  kansioon - sellaiset kohteet, jotka osuisivat sen ulkopuolelle, ohitetaan - ja sen `VERSION`:n
  täytyy olla se versio, jonka julkaisu väittää, tai mitään ei muuteta ("the archive is version X,
  not Y"). Sitten sen tiedostot kopioidaan kansion päälle. Tiedostot, jotka eivät kuulu julkaisuun -
  demosi, tulosteet, virtuaaliympäristö, kaikki, minkä teit - eivät koskaan muutu. Pythonin moduulit,
  joita julkaisussa ei enää ole, poistetaan työkalun omista paketeista (`heat3d_*`-kansiot), jotta
  vanha moduuli ei peitä sen korvaajaa.

Jos päivitys epäonnistuu, viesti tulostetaan ja työkalu ajaa sillä versiolla, joka sillä on.
