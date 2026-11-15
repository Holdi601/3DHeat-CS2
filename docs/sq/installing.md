---
title: "Instalimi"
nav_order: 3
lang: "sq"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalimi {#installing}

Je i ri te rreshti i komandave? Lexo më parë [Para se të fillosh](before-you-start.md).

3DHeat CS2 është një paketë Python që xhirohet nga dosja e vet. Nuk ka asgjë për
ndërtuar dhe asnjë instalues; kërkon Python, katër paketa (plus pytest për testet), dhe - vetëm për eksportin
e hartës - Counter-Strike 2 të instaluar dhe ndërtimin e Source2Viewer për rreshtin e komandave.

## Marrja e kodit {#getting-the-code}

Shkarko një arkivë botimi nga
[faqja e botimeve](https://github.com/Holdi601/3DHeat-CS2/releases) dhe shpaketoje,
ose, nëse ke Git, klono depon:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Të dy llojet e kopjes mund ta përditësojnë veten (shih [Përditësimet](updates.md)). Versioni
i instaluar është rreshti i vetëm në skedarin `VERSION`.

Xhiro çdo komandë nga ajo dosje: `python -m heat3d_cs2` e gjen paketën
sepse është në dosjen aktuale. Paketa nuk instalohet në
`site-packages`.

## Python dhe paketat {#python-and-the-packages}

Python 3.10 ose më i ri. Një mjedis virtual i mban paketat larg
çdo gjëje tjetër. Në Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nëse PowerShell refuzon ta xhirojë skriptin, xhiro më parë
`Set-ExecutionPolicy -Scope Process RemoteSigned` (vlen vetëm për atë
dritare). Në Linux ose macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funksionon kur `python -m heat3d_cs2 --help` printon `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paketa | Minimumi | Përdoret për | Licenca |
|---|---|---|---|
| `demoparser2` | 0.42 | leximin e skedarëve `.dem` (lojtarët për tick, ngjarjet e lojës) | MIT |
| `pyarrow` | 15 | shkrimin e tabelës Parquet | Apache-2.0 |
| `pandas` | 2.0 | tabelat ndërmjet | BSD-3-Clause |
| `numpy` | 1.24 | aritmetikën mbi to | BSD-3-Clause |
| `pytest` | 8.0 | vetëm testet | MIT |

Komandat `demos` dhe `scoreboard` nuk kërkojnë asgjë tjetër.

## Për eksportin e hartës: Counter-Strike 2 dhe CLI i Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` e lexon hartën nga loja që ke të instaluar, dhe
e dekodon me **rreshtin e komandave të Source2Viewer**, një program më vete nga projekti
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(me licencë MIT). Nuk vjen i përfshirë dhe nuk instalohet me pip.

1. Shkarko ndërtimin **CLI** për sistemin tënd nga
   [botimet e ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   dhe shpaketoje kudo.
2. Bëje të gjendshëm, në një nga tri mënyrat. Provohen sipas këtij rendi:
   1. `--source2viewer <path to the executable>` në rreshtin e komandave;
   2. variabla e mjedisit `HEAT3D_SOURCE2VIEWER` e vendosur te shtegu i skedarit ekzekutues;
   3. një skedar ekzekutues me emrin `Source2Viewer-CLI` ose `Source2Viewer-CLI.exe` në `PATH`.

   Një kandidat përdoret vetëm nëse shtegu ekziston. Nëse nuk gjendet asnjë, komanda
   ndalon me `Source2Viewer-CLI not found: download the command line build for
   your system from https://github.com/ValveResourceFormat/ValveResourceFormat/releases,
   then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Vendosja e variablës, për shembull:

```bash
# Windows (PowerShell), for the current session
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Ku kërkohet CS2 {#where-cs2-is-looked-for}

Harta është një arkivë `.vpk` nën dosjen e lojës:
`<Steam library>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<map>.vpk`.
Bibliotekat e Steam gjenden nga këto rrënjë, dhe nga çdo `"path"` i listuar
në `config\libraryfolders.vdf` të secilës rrënjë:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Kur Steam është diku tjetër, jep vetë dosjen e CS2 me `--game` (dosja
që përmban `game\csgo`), ose jep shtegun e `.vpk` në vend të emrit të hartës.
Shih [Eksporti i hartës](map-export.md).

## Kontrollimi i instalimit {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testet xhirohen mbi një demo sintetike të ndërtuar në kod dhe nuk kërkojnë demo, lojë apo
Source2Viewer (shih [Zhvillimi](development.md)).

Çdo nisje e `python -m heat3d_cs2` kontrollon së pari, çdo gjashtë orë më së shumti,
nëse ka dalë një botim më i ri; vendos `HEAT3D_NO_UPDATE=1` për ta fikur
(shih [Përditësimet](updates.md)).
