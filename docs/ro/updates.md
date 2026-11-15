---
title: Actualizări
nav_order: 14
lang: "ro"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Actualizări {#updates}

3DHeat CS2 se ține la zi singur, din [lansările GitHub](https://github.com/Holdi601/3DHeat-CS2/releases)
ale acestui depozit. Cod:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Verificarea la pornire {#the-check-at-start-up}

La fiecare `python -m heat3d_cs2 ...` se verifică mai întâi dacă a apărut o lansare mai nouă,
înainte chiar de a citi argumentele:

1. Versiunea instalată este fișierul `VERSION` din rădăcina depozitului (`0` dacă nu poate fi citit).
2. Cea mai nouă lansare este cerută de la
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, cu un timeout de
   **5 secunde**. Răspunsul este ținut în cache **6 ore** în
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (pe sistemele fără `LOCALAPPDATA`:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), deci cererea se face cel mult la șase ore.
   „Nicio lansare încă” (HTTP 404) se ține în cache ca un răspuns. Fără conexiune, limitat ca
   rată, în spatele unui proxy - orice altă eroare - instrumentul merge mai departe cu versiunea
   pe care o are, iar nimic nu se pune în cache.
3. Versiunile sunt comparate ca numere: `v1.2.3` și `1.2.3` sunt egale, orice după un `-` sau
   `+` este ignorat, părțile lipsă contează ca 0.

Când o lansare mai nouă este disponibilă, se spune asta pe fluxul de erori:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- La un terminal (atât intrarea, cât și fluxul de erori sunt terminale) întreabă. Enter, `y`,
  `yes`, `j` sau `ja` actualizează; orice altceva merge mai departe neschimbat. După o
  actualizare, **aceeași comandă rulează din nou**, pe codul nou.
- Fără terminal - o rulare programată, o conductă - doar afișează unde să actualizezi și merge
  mai departe: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` oprește verificarea. Orice valoare în afara celor goale, `0`, `false` sau
`no` înseamnă pornit.

## Actualizarea la cerere {#updating-on-request}

```bash
python -m heat3d_update            # actualizează la cea mai nouă lansare
python -m heat3d_update --check    # spune doar dacă există una nouă
```

Asta întreabă mereu GitHub (cache-ul nu este folosit). Afișează `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, sau
`<new> is out (this is <current>): <url>` și apoi actualizează (dacă nu este `--check`).
Codul de ieșire `1` când o actualizare a fost încercată și a eșuat, `0` în rest.

## Cum se aplică o actualizare {#how-an-update-is-applied}

Depinde de cum a fost instalată copia:

- **O copie git** (există un `.git` în rădăcină și `git` în `PATH`): `git pull --ff-only`.
  Este refuzată cât timp fișierele urmărite au modificări locale ("this checkout has local
  changes; commit or stash them, then run `git pull`"): acelea sunt munca cuiva, iar o
  actualizare nu decide ce se întâmplă cu ele. Fișierele neurmărite nu o blochează.
- **O copie descărcată**: arhiva sursă a lansării (zipball-ul GitHub) este descărcată și
  dezarhivată într-un folder temporar - intrările care ar ajunge în afara lui sunt sărite - iar
  `VERSION` ei trebuie să fie versiunea pe care o pretinde lansarea, altfel nu se schimbă nimic
  ("the archive is version X, not Y"). Apoi fișierele ei sunt copiate peste folder. Fișierele
  care nu fac parte din lansare - demo-urile tale, rezultatele, mediul virtual, orice ai făcut
  tu - nu sunt atinse niciodată. Modulele Python pe care lansarea nu le mai are sunt șterse din
  pachetele instrumentului (folderele `heat3d_*`), ca un modul vechi să nu umbrească înlocuitorul.

Dacă o actualizare eșuează, mesajul este afișat, iar instrumentul rulează pe versiunea pe care
o are.
