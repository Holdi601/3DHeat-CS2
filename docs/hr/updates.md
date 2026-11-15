---
title: "Ažuriranja"
nav_order: 14
lang: "hr"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Ažuriranja {#updates}

3DHeat CS2 sam drži sebe aktualnim iz [izdanja (releases)](https://github.com/Holdi601/3DHeat-CS2/releases) ovog repozitorija. Kod:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Provjera pri pokretanju {#the-check-at-start-up}

Svako `python -m heat3d_cs2 ...` prvo pita je li izašlo novije izdanje, prije nego što uopće pročita svoje argumente:

1. Instalirana verzija je datoteka `VERSION` u korijenu repozitorija (`0` ako se ne može pročitati).
2. Najnovije izdanje traži se od `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, s **5 sekundi** čekanja. Odgovor se sprema u predmemoriju **6 sati** u `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (na sustavima bez `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), pa se zahtjev šalje najviše svakih šest sati. "Još nema izdanja" (HTTP 404) sprema se u predmemoriju kao i svaki drugi odgovor. Bez mreže, s ograničenjem brzine, iza proxyja - bilo koja druga greška - alat nastavlja s verzijom koju ima, a ništa se ne sprema.
3. Verzije se uspoređuju kao brojevi: `v1.2.3` i `1.2.3` su jednake, sve nakon `-` ili `+` se zanemaruje, nedostajući dijelovi broje se kao 0.

Kad je novije izdanje dostupno, to se ispisuje na kanal za greške:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- U terminalu (ulaz i kanal za greške su terminali) pita. Enter, `y`, `yes`, `j` ili `ja` ažurira; sve drugo nastavlja nepromijenjeno. Nakon ažuriranja **ista naredba se pokreće ponovno**, na novom kodu.
- Bez terminala - zakazano pokretanje, cijev - samo ispisuje gdje se ažurira i nastavlja: `Run python -m heat3d_update in <mapa> to update.`

`HEAT3D_NO_UPDATE=1` isključuje provjeru. Svaka vrijednost osim prazne, `0`, `false` ili `no` znači uključeno.

## Ažuriranje na zahtjev {#updating-on-request}

```bash
python -m heat3d_update            # ažuriraj na najnovije izdanje
python -m heat3d_update --check    # samo reci je li nešto novo izašlo
```

Ovo uvijek pita GitHub (predmemorija se ne koristi). Ispisuje `Up to date: <verzija>.`, `No release found (this is <verzija>); offline, or nothing published yet.`, ili `<nova> is out (this is <trenutna>): <url>` i zatim ažurira (osim uz `--check`). Izlazni kod `1` kad je ažuriranje pokušano i nije uspjelo, inače `0`.

## Kako se ažuriranje primjenjuje {#how-an-update-is-applied}

Ovisi o tome kako je kopija instalirana:

- **Git kopija** (u korijenu postoji `.git` i `git` je na `PATH`-u): `git pull --ff-only`. Odbija se dok praćene datoteke imaju lokalne promjene ("this checkout has local changes; commit or stash them, then run `git pull`"): to je tuđi rad, a ažuriranje ne odlučuje što će se s njim dogoditi. Nepraćene datoteke ne blokiraju ga.
- **Preuzeta kopija**: arhiva izvornog koda izdanja (GitHubov zipball) preuzima se i raspakira u privremenu mapu - unosi koji bi završili izvan nje se preskaču - i njezin `VERSION` mora biti verzija koju izdanje tvrdi, inače se ništa ne mijenja ("the archive is version X, not Y"). Zatim se njezine datoteke kopiraju preko mape. Datoteke koje nisu dio izdanja - vaše demo snimke, izlazi, virtualno okruženje, sve što ste sami napravili - nikad se ne diraju. Python moduli koje izdanje više nema brišu se iz vlastitih paketa alata (mape `heat3d_*`), tako da stari modul ne zasjeni svoju zamjenu.

Ako ažuriranje ne uspije, poruka se ispisuje i alat nastavlja s verzijom koju ima.
