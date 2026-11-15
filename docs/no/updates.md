---
title: "Oppdateringer"
nav_order: 14
lang: "no"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Oppdateringer {#updates}

3DHeat CS2 holder seg oppdatert fra dette repositoriets
[utgivelser på GitHub](https://github.com/Holdi601/3DHeat-CS2/releases). Kode:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Sjekken ved oppstart {#the-check-at-start-up}

Hver `python -m heat3d_cs2 ...` spør først om en nyere utgivelse finnes, før den i det hele tatt leser
argumentene sine:

1. Den installerte versjonen er filen `VERSION` i repositoriets rot (`0` hvis den ikke kan leses).
2. Den nyeste utgivelsen spørres hos
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, med en tidsgrense på **5 sekunder**.
   Svaret lagres i hurtigbufferen i **6 timer** i `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json`
   (på systemer uten `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), så forespørselen
   gjøres høyst hvert sjette timer. «Ingen utgitt ennå» (HTTP 404) lagres som et svar. Frakoblet,
   hastighetsbegrenset, bak en proxy - hvilken som helst annen feil - fortsetter verktøyet med versjonen
   det har, og ingenting lagres.
3. Versjoner sammenlignes som tall: `v1.2.3` og `1.2.3` er like, alt etter et `-` eller `+` ignoreres,
   manglende deler telles som 0.

Når en nyere utgivelse finnes, sier det det på feilstrømmen:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- I en terminal (både inn- og feilstrømmen er terminaler) spør den. Enter, `y`, `yes`, `j` eller `ja`
  oppdaterer; alt annet fortsetter uendret. Etter en oppdatering **kjøres den samme kommandoen på nytt**,
  med den nye koden.
- Uten terminal - en planlagt kjøring, en pipe - skriver den bare hvor du oppdaterer, og fortsetter:
  `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` slår av sjekken. Enhver verdi annet enn tom, `0`, `false` eller `no` regnes som på.

## Oppdatere på forespørsel {#updating-on-request}

```bash
python -m heat3d_update            # oppdater til den nyeste utgivelsen
python -m heat3d_update --check    # bare si om en finnes
```

Dette spør alltid GitHub (hurtigbufferen brukes ikke). Den skriver ut `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, eller
`<new> is out (this is <current>): <url>` og oppdaterer deretter (med mindre `--check`).
Avslutningskode `1` når en oppdatering ble forsøkt og mislyktes, `0` ellers.

## Slik brukes en oppdatering {#how-an-update-is-applied}

Det avhenger av hvordan kopien ble installert:

- **En git-kopi** (det finnes en `.git` i roten, og `git` på `PATH`): `git pull --ff-only`. Den nektes så
  lenge sporede filer har lokale endringer («this checkout has local changes; commit or stash them, then
  run `git pull`»): det er noens arbeid, og en oppdatering bestemmer ikke hva som skjer med dem. Ikke-sporede
  filer hindrer den ikke.
- **En nedlastet kopi**: utgivelsens kildearkiv (GitHubs zipball) lastes ned og pakkes ut i en midlertidig
  mappe - oppføringer som ville havnet utenfor den, hoppes over - og dens `VERSION` må være versjonen
  utgivelsen oppgir, ellers endres ingenting («the archive is version X, not Y»). Deretter kopieres filene
  over mappen. Filer som ikke er del av utgivelsen - demoene dine, utdata, det virtuelle miljøet, alt du
  har laget - røres aldri. Python-moduler som utgivelsen ikke lenger har, slettes fra verktøyets egne pakker
  (`heat3d_*`-mappene), så en utdatert modul ikke kan skygge for erstatningen.

Mislykkes en oppdatering, skrives meldingen ut, og verktøyet kjører på versjonen det har.
