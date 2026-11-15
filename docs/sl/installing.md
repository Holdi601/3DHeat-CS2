---
title: "Namestitev"
nav_order: 3
lang: "sl"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Namestitev {#installing}

Prvič v ukazni vrstici? Najprej preberite [Preden začneš](before-you-start.md).

3DHeat CS2 je paket za Python, ki se zažene iz svoje mape. Nič ni treba graditi in ni namestitvenega programa; potrebuje
Python, štiri pakete (plus pytest za teste) in – samo za izvoz karte – nameščen Counter-Strike 2 ter ukazno
različico Source2Viewer.

## Pridobitev kode {#getting-the-code}

Prenesi arhiv izdaje s [strani izdaj](https://github.com/Holdi601/3DHeat-CS2/releases) in ga razpakirajte, ali pa,
če imate Git, klonirajte repozitorij:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Obe vrsti kopij se lahko posodobita sami (glejte [Posodobitve](updates.md)). Nameščena različica je ena vrstica v
datoteki `VERSION`.

Vse ukaze zaženite iz te mape: `python -m heat3d_cs2` najde paket, ker je v trenutni mapi. Paket se ne namešča v
`site-packages`.

## Python in paketi {#python-and-the-packages}

Python 3.10 ali novejši. Virtualno okolje ločuje pakete od drugih stvari. V Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Če PowerShell noče zagnati skripte, najprej zaženite `Set-ExecutionPolicy -Scope Process RemoteSigned` (velja samo za
to okno). Na Linuxu ali macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Deluje, ko `python -m heat3d_cs2 --help` izpiše `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Paket | Najmanj | Za kaj | Licenca |
|---|---|---|---|
| `demoparser2` | 0.42 | branje datotek `.dem` (igralci na takt, dogodki igre) | MIT |
| `pyarrow` | 15 | pisanje tabele Parquet | Apache-2.0 |
| `pandas` | 2.0 | vmesne tabele | BSD-3-Clause |
| `numpy` | 1.24 | računanje z njimi | BSD-3-Clause |
| `pytest` | 8.0 | samo za teste | MIT |

Ukaza `demos` in `scoreboard` ne potrebujeta ničesar drugega.

## Za izvoz karte: Counter-Strike 2 in ukazna vrstica Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` prebere karto iz igre, ki jo imate nameščeno, in jo dekodira z **ukazno vrstico Source2Viewer**,
ločenim programom iz projekta [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)
(licenca MIT). Ni priložen in ga ni mogoče namestiti z pip-om.

1. Prenesite gradnjo **CLI** za svoj sistem s
   [strani izdaj ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases) in jo
   razpakirajte kamorkoli.
2. Poskrbite, da jo bo program našel, na enega od treh načinov. Preizkušajo se v tem vrstnem redu:
   1. `--source2viewer <pot do izvršljive datoteke>` v ukazni vrstici;
   2. spremenljivka okolja `HEAT3D_SOURCE2VIEWER` s potjo do izvršljive datoteke;
   3. izvršljiva datoteka z imenom `Source2Viewer-CLI` ali `Source2Viewer-CLI.exe` na `PATH`.

   Kandidat se uporabi samo, če pot obstaja. Če nobenega ni, se ukaz ustavi s sporočilom
   `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set
   HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Nastavitev spremenljivke, na primer:

```bash
# Windows (PowerShell), za trenutno sejo
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Kje se išče CS2 {#where-cs2-is-looked-for}

Karta je arhiv `.vpk` pod mapo igre:
`<knjižnica Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<karta>.vpk`.
Knjižnice Steama se najdejo iz teh korenov in iz vsake `"path"` v `config\libraryfolders.vdf` vsakega korena:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Kadar je Steam drugje, podajtete mapo CS2 sama z `--game` (mapo, ki vsebuje `game\csgo`), ali pa pot do `.vpk` namesto
imena karte. Glejte [Izvoz karte](map-export.md).

## Preverjanje namestitve {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Testi tečejo na sintetičnem demu, zgrajenem v kodi, in ne potrebujejo demo, igre ali Source2Viewer (glejte
[Razvoj](development.md)).

Ob vsakem zagonu `python -m heat3d_cs2` se preveri – največ enkrat na šest ur –, ali je izšla novejša izdaja; z
`HEAT3D_NO_UPDATE=1` to izklopiš (glejte [Posodobitve](updates.md)).
