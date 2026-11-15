---
title: Ažuriranja
nav_order: 14
lang: "bs"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Ažuriranja {#updates}

3DHeat CS2 sam se održava aktuelnim iz
[GitHub izdanja](https://github.com/Holdi601/3DHeat-CS2/releases) ovog repozitorija. Kod:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Provjera pri pokretanju {#the-check-at-start-up}

Svako `python -m heat3d_cs2 ...` prvo pita je li izašlo novije izdanje,
prije nego uopće pročita svoje argumente:

1. Instalirana verzija je datoteka `VERSION` u korijenu repozitorija
   (`0` ako se ne može pročitati).
2. Najnovije izdanje traži se od
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, s
   vremenskim ograničenjem od **5 sekundi**. Odgovor se kešira **6 sati** u
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (na sistemima bez
   `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), pa se
   zahtjev šalje najviše svakih šest sati. "Ništa još nije izdano" (HTTP 404)
   kešira se kao odgovor. Bez interneta, uz ograničenje broja zahtjeva, iza proxyja - svaka druga
   greška - alat nastavlja s verzijom koju ima, i ništa se
   ne kešira.
3. Verzije se porede kao brojevi: `v1.2.3` i `1.2.3` su jednake, sve
   poslije `-` ili `+` se ignoriše, dijelovi koji nedostaju računaju se kao 0.

Kad je izašlo novije izdanje, to kaže na toku grešaka:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Na terminalu (i ulaz i tok grešaka su terminali) pita. Enter, `y`, `yes`, `j` ili `ja` ažurira; bilo šta drugo nastavlja nepromijenjeno.
  Nakon ažuriranja **ista komanda se pokreće ponovo**, na novom kodu.
- Bez terminala - zakazano pokretanje, pipe - samo ispiše gdje
  ažurirati i nastavlja: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` isključuje provjeru. Svaka vrijednost osim prazne,
`0`, `false` ili `no` računa se kao uključeno.

## Ažuriranje na zahtjev {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Ovo uvijek pita GitHub (keš se ne koristi). Ispisuje `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, ili
`<new> is out (this is <current>): <url>` a zatim ažurira (osim uz `--check`).
Izlazni kod `1` kad je ažuriranje pokušano i nije uspjelo, inače `0`.

## Kako se ažuriranje primjenjuje {#how-an-update-is-applied}

Zavisi od toga kako je kopija instalirana:

- **Git checkout** (u korijenu postoji `.git` i `git` na `PATH`):
  `git pull --ff-only`. Odbija se dok praćene datoteke imaju lokalne promjene
  ("this checkout has local changes; commit or stash them, then run
  `git pull`"): to je nečiji rad, a ažuriranje ne odlučuje šta
  će biti s njim. Neprićene datoteke ga ne blokiraju.
- **Preuzeta kopija**: izvorna arhiva izdanja (GitHubov zipball) se
  preuzima i raspakuje u privremeni folder - stavke koje bi završile
  izvan njega se preskaču - a njen `VERSION` mora biti verzija koju izdanje
  tvrdi, inače se ništa ne mijenja ("the archive is version X, not Y"). Zatim se njene
  datoteke kopiraju preko foldera. Datoteke koje nisu dio izdanja -
  vaši demoi, izlazi, virtualno okruženje, sve što ste napravili - nikad se
  ne diraju. Python moduli koje izdanje više nema brišu se iz
  vlastitih paketa alata (folderi `heat3d_*`), pa zastarjeli modul ne može
  zasjeniti svoju zamjenu.

Ako ažuriranje ne uspije, poruka se ispisuje i alat radi dalje s verzijom
koju ima.
