---
title: Instalacija
nav_order: 3
lang: "bs"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalacija {#installing}

Novi ste u komandnoj liniji? Prvo pročitajte [Prije nego počnete](before-you-start.md).

3DHeat CS2 je Python paket koji se pokreće iz vlastitog foldera. Ništa se ne
gradi i nema instalera; treba mu Python, četiri paketa (plus pytest za testove) i - samo za izvoz
mape - instaliran Counter-Strike 2 i komandnolinijska verzija programa Source2Viewer.

## Preuzimanje koda {#getting-the-code}

Preuzmite arhivu izdanja sa
[stranice izdanja](https://github.com/Holdi601/3DHeat-CS2/releases) i raspakujte je,
ili, ako imate Git, klonirajte repozitorij:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Obje vrste kopije mogu se same ažurirati (pogledajte [Ažuriranja](updates.md)).
Instalirana verzija je jedan red u datoteci `VERSION`.

Svaku komandu pokreći iz tog foldera: `python -m heat3d_cs2` pronalazi paket
jer je u trenutnom folderu. Paket se ne instalira u
`site-packages`.

## Python i paketi {#python-and-the-packages}

Python 3.10 ili noviji. Virtualno okruženje drži pakete odvojeno od svega
ostalog. Na Windowsu (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ako PowerShell odbije pokrenuti skriptu, prvo pokrenite
`Set-ExecutionPolicy -Scope Process RemoteSigned` (traje samo za taj
prozor). Na Linuxu ili macOS-u:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Radi kad `python -m heat3d_cs2 --help` ispiše `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paket | Minimum | Za šta se koristi | Licenca |
|---|---|---|---|
| `demoparser2` | 0.42 | čitanje `.dem` datoteka (igrači po tiku, događaji igre) | MIT |
| `pyarrow` | 15 | pisanje Parquet tabele | Apache-2.0 |
| `pandas` | 2.0 | međutabele | BSD-3-Clause |
| `numpy` | 1.24 | aritmetika nad njima | BSD-3-Clause |
| `pytest` | 8.0 | samo testovi | MIT |

Komande `demos` i `scoreboard` ne trebaju ništa drugo.

## Za izvoz mape: Counter-Strike 2 i CLI programa Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` čita mapu iz igre koju imate instaliranu i
dekodira je **komandnom linijom programa Source2Viewer**, zasebnim programom iz
projekta [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(MIT licenca). Nije uključen i ne može se instalirati pomoću pip-a.

1. Preuzmite **CLI** verziju za svoj sistem sa
   [izdanja ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   i raspakujte je bilo gdje.
2. Učinite je pronalazivom, na jedan od tri načina. Isprobavaju se ovim redom:
   1. `--source2viewer <putanja do izvršne datoteke>` u komandnoj liniji;
   2. varijabla okruženja `HEAT3D_SOURCE2VIEWER` postavljena na putanju izvršne datoteke;
   3. izvršna datoteka zvana `Source2Viewer-CLI` ili `Source2Viewer-CLI.exe` na `PATH`.

   Kandidat se koristi samo ako putanja postoji. Ako se nijedan ne nađe,
   komanda staje s `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Postavljanje varijable, na primjer:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Gdje se traži CS2 {#where-cs2-is-looked-for}

Mapa je `.vpk` arhiva unutar foldera igre:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Steam biblioteke se nalaze iz ovih korijena i iz svakog `"path"` navedenog u
`config\libraryfolders.vdf` svakog korijena:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Kad je Steam negdje drugdje, proslijedite sami CS2 folder s `--game` (folder
koji sadrži `game\csgo`), ili proslijedite putanju `.vpk` umjesto imena mape.
Pogledajte [Izvoz mape](map-export.md).

## Provjera instalacije {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testovi rade na sintetičkom demou izgrađenom u kodu i ne trebaju ni demo, ni
igru, ni Source2Viewer (pogledajte [Razvoj](development.md)).

Svako pokretanje `python -m heat3d_cs2` prvo provjerava, najviše svakih šest
sati, je li izašlo novije izdanje; postavite `HEAT3D_NO_UPDATE=1` da to
isključite (pogledajte [Ažuriranja](updates.md)).
