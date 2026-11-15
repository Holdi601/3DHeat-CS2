---
title: Instalare
nav_order: 3
lang: "ro"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalare {#installing}

Nu ești obișnuit cu linia de comandă? Citește mai întâi [Înainte de a începe](before-you-start.md).

3DHeat CS2 este un pachet Python care rulează din propriul său folder. Nu există nimic de
construit și nici program de instalare; are nevoie de Python, de patru pachete (plus pytest
pentru teste) și - doar pentru exportul hărții - de Counter-Strike 2 instalat și de
versiunea de linie de comandă a Source2Viewer.

## Obținerea codului {#getting-the-code}

Descarcă o arhivă de lansare de pe
[pagina de lansări](https://github.com/Holdi601/3DHeat-CS2/releases) și dezarhiveaz-o,
sau, dacă ai Git, clonează depozitul:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Ambele tipuri de copii se pot actualiza singure (vezi [Actualizări](updates.md)). Versiunea
instalată este linia unică din fișierul `VERSION`.

Rulează fiecare comandă din acest folder: `python -m heat3d_cs2` găsește pachetul pentru că
acesta se află în folderul curent. Pachetul nu este instalat în `site-packages`.

## Python și pachetele {#python-and-the-packages}

Python 3.10 sau mai nou. Un mediu virtual ține pachetele separate de orice altceva. Pe
Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Dacă PowerShell refuză să ruleze scriptul, rulează mai întâi
`Set-ExecutionPolicy -Scope Process RemoteSigned` (durează doar pentru acea fereastră). Pe
Linux sau macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funcționează când `python -m heat3d_cs2 --help` afișează `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pachet | Minim | Folosit pentru | Licență |
|---|---|---|---|
| `demoparser2` | 0.42 | citirea fișierelor `.dem` (jucători pe tick, evenimente de joc) | MIT |
| `pyarrow` | 15 | scrierea tabelului Parquet | Apache-2.0 |
| `pandas` | 2.0 | tabelele intermediare | BSD-3-Clause |
| `numpy` | 1.24 | calculele pe ele | BSD-3-Clause |
| `pytest` | 8.0 | doar testele | MIT |

Comenzile `demos` și `scoreboard` nu au nevoie de nimic altceva.

## Pentru exportul hărții: Counter-Strike 2 și CLI-ul Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` citește harta din jocul pe care l-ai instalat și o decodează cu
**linia de comandă a Source2Viewer**, un program separat de proiectul
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(licență MIT). Nu este inclus și nu poate fi instalat cu pip.

1. Descarcă versiunea **CLI** pentru sistemul tău de la
   [lansările ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   și dezarhiveaz-o oriunde.
2. Fă-l găsibil, în unul din trei feluri. Sunt încercate în această ordine:
   1. `--source2viewer <calea către executabil>` în linia de comandă;
   2. variabila de mediu `HEAT3D_SOURCE2VIEWER` setată la calea executabilului;
   3. un executabil numit `Source2Viewer-CLI` sau `Source2Viewer-CLI.exe` în `PATH`.

   Un candidat este folosit doar dacă calea există. Dacă nu se găsește niciunul, comanda se
   oprește cu `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Setarea variabilei, de exemplu:

```bash
# Windows (PowerShell), pentru sesiunea curentă
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Unde este căutat CS2 {#where-cs2-is-looked-for}

Harta este o arhivă `.vpk` sub folderul jocului:
`<bibliotecă Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Bibliotecile Steam sunt găsite din aceste rădăcini și din fiecare `"path"` listat în
`config\libraryfolders.vdf` al fiecărei rădăcini:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Când Steam este în alt loc, dă folderul CS2 însuși cu `--game` (folderul care conține
`game\csgo`), sau dă calea către `.vpk` în loc de numele hărții. Vezi [Exportul hărții](map-export.md).

## Verificarea instalării {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testele rulează pe un demo sintetic construit în cod și nu au nevoie de niciun demo, joc
sau Source2Viewer (vezi [Dezvoltare](development.md)).

La fiecare pornire a `python -m heat3d_cs2` se verifică mai întâi, cel mult la fiecare șase
ore, dacă a apărut o versiune nouă; setează `HEAT3D_NO_UPDATE=1` ca să oprești asta (vezi
[Actualizări](updates.md)).
