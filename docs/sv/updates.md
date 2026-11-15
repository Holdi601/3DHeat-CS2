---
title: "Uppdateringar"
nav_order: 14
lang: "sv"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Uppdateringar {#updates}

3DHeat CS2 håller sig aktuellt via det här förrådets
[GitHub-utgivningar](https://github.com/Holdi601/3DHeat-CS2/releases). Kod:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Kollen vid start {#the-check-at-start-up}

Varje `python -m heat3d_cs2 ...` frågar först om en nyare utgåva finns, innan den ens läser sina argument:

1. Den installerade versionen är filen `VERSION` i förrådets rot (`0` om den inte kan läsas).
2. Den senaste utgåvan efterfrågas hos
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, med en tidsgräns på **5 sekunder**.
   Svaret sparas i **6 timmar** i `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (på system utan
   `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), så att begäran görs högst var sjätte
   timme. "Ingen utgåva ännu" (HTTP 404) sparas som ett svar. Offline, begränsad av antalet anrop, bakom en
   proxy - vilket annat fel som helst - fortsätter verktyget med den version det har, och inget sparas.
3. Versioner jämförs som tal: `v1.2.3` och `1.2.3` är lika, allt efter ett `-` eller `+` ignoreras, saknade
   delar räknas som 0.

När en nyare utgåva finns säger det på felströmmen:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- I en terminal (både indata- och felströmmen är terminaler) frågar den. Enter, `y`, `yes`, `j` eller `ja`
  uppdaterar; allt annat fortsätter oförändrat. Efter en uppdatering **körs samma kommando igen**, på den
  nya koden.
- Utan terminal - en schemalagd körning, en pipe - skriver den bara var man uppdaterar och fortsätter:
  `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` stänger av kollen. Varje värde utom tomt, `0`, `false` eller `no` räknas som på.

## Uppdatera på begäran {#updating-on-request}

```bash
python -m heat3d_update            # uppdatera till den senaste utgåvan
python -m heat3d_update --check    # säg bara om en finns
```

Det här frågar alltid GitHub (sparningen används inte). Det skriver ut `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, eller
`<new> is out (this is <current>): <url>` och uppdaterar sedan (om inte `--check`). Avslutskod `1` när en
uppdatering försökts och misslyckades, annars `0`.

## Hur en uppdatering görs {#how-an-update-is-applied}

Det beror på hur kopian installerades:

- **En git-kopia** (det finns en `.git` i roten och `git` på `PATH`): `git pull --ff-only`. Det vägras medan
  spårade filer har lokala ändringar ("this checkout has local changes; commit or stash them, then run
  `git pull`"): det är någons arbete, och en uppdatering bestämmer inte vad som händer med det. Ospårade filer
  stoppar inte den.
- **En nedladdad kopia**: utgivningens källarkiv (GitHubs zipball) laddas ner och packas upp i en tillfällig
  mapp - poster som skulle hamna utanför den hoppas över - och dess `VERSION` måste vara den version
  utgivningen anger, annars ändras ingenting ("the archive is version X, not Y"). Sedan kopieras dess filer
  över mappen. Filer som inte ingår i utgivningen - dina demos, utdata, din virtuella miljö, allt du gjort -
  rörs aldrig. Python-moduler som utgivningen inte längre har tas bort ur verktygets egna paket (mapparna
  `heat3d_*`), så att en gammal modul inte kan skymma sin ersättning.

Om en uppdatering misslyckas skrivs meddelandet ut och verktyget kör på den version det har.
