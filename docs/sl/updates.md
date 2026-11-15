---
title: "Posodobitve"
nav_order: 14
lang: "sl"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Posodobitve {#updates}

3DHeat CS2 se sam ohranja aktualen iz [izdaj na GitHubu](https://github.com/Holdi601/3DHeat-CS2/releases) tega
repozitorija. Koda:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Preverjanje ob zagonu {#the-check-at-start-up}

Vsak `python -m heat3d_cs2 ...` najprej vpraša, ali je izšla novejša izdaja, še preden prebere svoje argumente:

1. Nameščena različica je datoteka `VERSION` v korenu repozitorija (`0`, če je ni mogoče prebrati).
2. Najnovejša izdaja se vpraša na
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, s **5-sekundno** časovno omejitvijo. Odgovor se
   shrani za **6 ur** v `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (kjer `LOCALAPPDATA` ni na voljo:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), tako da se zahteva pošlje največ vsakih šest ur. »Še ni izdaje«
   (HTTP 404) se shrani kot odgovor. Brez povezave, omejen s številom zahtev, za posredniškim strežnikom – katerakoli
   druga napaka – orodje nadaljuje z različico, ki jo ima, in nič se ne shrani.
3. Različice se primerjajo kot številke: `v1.2.3` in `1.2.3` sta enaki, vse za `-` ali `+` se zanemari, manjkajoči deli
   štejejo kot 0.

Ko je izšla novejša izdaja, to pove na izhodnem toku napak:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- V terminalu (vhodni in izhodni tok napak sta terminala) vpraša. Enter, `y`, `yes`, `j` ali `ja` posodobi; karkoli drugega
  nadaljuje nespremenjeno. Po posodobitvi se **isti ukaz zažene znova**, na novi kodi.
- Brez terminala – zagnan po urniku, cev – samo izpiše, kje se posodobi, in nadaljuje:
  `Run python -m heat3d_update in <mapa> to update.`

`HEAT3D_NO_UPDATE=1` preverjanje izklopi. Vsaka vrednost, ki ni prazna, `0`, `false` ali `no`, pomeni vklop.

## Posodobitev na zahtevo {#updating-on-request}

```bash
python -m heat3d_update            # posodobi na najnovejšo izdajo
python -m heat3d_update --check    # samo pove, ali je ena na voljo
```

To vedno vpraša GitHub (predpomnilnik se ne uporabi). Izpiše `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.` ali
`<new> is out (this is <current>): <url>` in nato posodobi (razen pri `--check`). Izhodna koda `1`, ko je bil poskus
posodobitve neuspešen, sicer `0`.

## Kako se posodobitev uveljavi {#how-an-update-is-applied}

Odvisno od tega, kako je bila kopija nameščena:

- **Kopija iz Gita** (v korenu je `.git` in `git` na `PATH`): `git pull --ff-only`. Zavrne se, dokler sledene datoteke
  imajo lokalne spremembe (»this checkout has local changes; commit or stash them, then run `git pull`«): to je nečije
  delo, posodobitev pa ne odloča, kaj se z njim zgodi. Nesledene datoteke posodobitve ne ustavijo.
- **Prenesena kopija**: arhiv izvorne kode izdaje (zipball GitHuba) se prenese in razpakira v začasno mapo – vnosi, ki bi
  pristali zunaj nje, se preskočijo – in njena `VERSION` mora biti različica, ki jo izdaja izdaja, sicer se nič ne
  spremeni (»the archive is version X, not Y«). Nato se njene datoteke prekopirajo čez mapo. Datoteke, ki niso del izdaje –
  vaši demoji, izhodi, virtualno okolje, karkoli ste naredili – se nikoli ne dotaknejo. Python moduli, ki jih izdaja ne
  več ima, se izbrišejo iz paketov orodja (mape `heat3d_*`), da zastareli modul ne zakrije svojega nadomestka.

Če posodobitev spodleti, se sporočilo izpiše in orodje deluje na različici, ki jo ima.
