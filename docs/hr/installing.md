---
title: "Instalacija"
nav_order: 3
lang: "hr"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalacija {#installing}

Nov u naredbeni redak? Prvo pročitajte [Prije nego što počnete](before-you-start.md).

3DHeat CS2 je Python paket koji se pokreće iz vlastite mape. Ništa se ne gradi i nema instalatera; treba mu Python, četiri paketa (plus pytest za testove) i - samo za izvoz karte - Counter-Strike 2 instaliran i Source2Viewerovu verziju za naredbeni redak.

## Preuzimanje koda {#getting-the-code}

Preuzmite arhivu izdanja sa [stranice izdanja](https://github.com/Holdi601/3DHeat-CS2/releases) i raspakirajte je, ili, ako imate Git, klonirajte repozitorij:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Obje vrste kopije mogu se same ažurirati (vidi [Ažuriranja](updates.md)). Instalirana verzija je jedan redak u datoteci `VERSION`.

Pokrećite svaku naredbu iz te mape: `python -m heat3d_cs2` pronalazi paket jer je u trenutnoj mapi. Paket se ne instalira u `site-packages`.

## Python i paketi {#python-and-the-packages}

Python 3.10 ili noviji. Virtualno okruženje drži pakete odvojenima od ostalog. Na Windowsu (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ako PowerShell odbije pokrenuti skriptu, prvo pokrenite `Set-ExecutionPolicy -Scope Process RemoteSigned` (vrijedi samo za taj prozor). Na Linuxu ili macOS-u:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Radi kad `python -m heat3d_cs2 --help` ispiše `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paket | Najmanje | Za što | Licenca |
|---|---|---|---|
| `demoparser2` | 0.42 | čitanje `.dem` datoteka (igrači po tiku, događaji igre) | MIT |
| `pyarrow` | 15 | pisanje Parquet tablice | Apache-2.0 |
| `pandas` | 2.0 | tablice u međuprolazu | BSD-3-Clause |
| `numpy` | 1.24 | računanje nad njima | BSD-3-Clause |
| `pytest` | 8.0 | samo za testove | MIT |

Naredbe `demos` i `scoreboard` ne trebaju ništa drugo.

## Za izvoz karte: Counter-Strike 2 i Source2Viewerov CLI {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` čita kartu iz igre koju imate instaliranu, i dekodira je pomoću **Source2Viewerove naredbene verzije**, zasebnog programa iz projekta
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (licenca MIT). Nije uključen i ne može se instalirati pomoću pip-a.

1. Preuzmite **CLI** verziju za svoj sustav sa
   [izdanja ValveResourceFormata](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   i raspakirajte je bilo gdje.
2. Učinite da se pronalazi, na bilo koji od tri načina. Isprobavaju se ovim redom:
   1. `--source2viewer <putanja do izvršne datoteke>` u naredbenom retku;
   2. varijabla okoline `HEAT3D_SOURCE2VIEWER` postavljena na putanju izvršne datoteke;
   3. izvršna datoteka imena `Source2Viewer-CLI` ili `Source2Viewer-CLI.exe` na `PATH`.

   Kandidat se koristi samo ako putanja postoji. Ako se ništa ne pronađe, naredba se zaustavlja s `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Postavljanje varijable, na primjer:

```bash
# Windows (PowerShell), za trenutnu sesiju
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Gdje se traži CS2 {#where-cs2-is-looked-for}

Karta je `.vpk` arhiva pod mapom igre:
`<Steam biblioteka>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<karta>.vpk`.
Steam biblioteke pronalaze se iz ovih korijena i iz svake `"path"` vrijednosti navedene u `config\libraryfolders.vdf` svakog korijena:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Kad je Steam negdje drugdje, navedite samu mapu CS2 s `--game` (mapu koja sadrži `game\csgo`), ili navedite putanju do `.vpk` umjesto imena karte. Vidi [Izvoz karte](map-export.md).

## Provjera instalacije {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testovi rade na sintetičkoj demo snimci napravljenoj u kodu i ne trebaju demo snimku, igru ni Source2Viewer (vidi [Razvoj](development.md)).

Svako pokretanje `python -m heat3d_cs2` prvo provjerava, najviše svakih šest sati, je li izašlo novije izdanje; postavite `HEAT3D_NO_UPDATE=1` da to isključite (vidi [Ažuriranja](updates.md)).
