---
title: "Installazione"
nav_order: 3
lang: "it"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Installazione {#installing}

Nuovo alla riga di comando? Leggi prima [Prima di iniziare](before-you-start.md).

3DHeat CS2 è un pacchetto Python eseguito dalla sua cartella. Non c'è nulla da compilare e nessun programma di
installazione; servono Python, quattro pacchetti (più pytest per i test) e - solo per l'esportazione della mappa -
Counter-Strike 2 installato e la build a riga di comando di Source2Viewer.

## Ottenere il codice {#getting-the-code}

Scarica un archivio di release dalla
[pagina delle release](https://github.com/Holdi601/3DHeat-CS2/releases) e decomprimilo, oppure, se hai Git, clona il
repository:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Entrambi i tipi di copia possono aggiornarsi da soli (vedi [Aggiornamenti](updates.md)). La versione installata è la
riga contenuta nel file `VERSION`.

Esegui ogni comando da quella cartella: `python -m heat3d_cs2` trova il pacchetto perché si trova nella cartella
corrente. Il pacchetto non viene installato in `site-packages`.

## Python e i pacchetti {#python-and-the-packages}

Python 3.10 o successivo. Un ambiente virtuale tiene i pacchetti separati da tutto il resto. Su Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se PowerShell rifiuta di eseguire lo script, esegui prima
`Set-ExecutionPolicy -Scope Process RemoteSigned` (vale solo per quella finestra). Su Linux o macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funziona quando `python -m heat3d_cs2 --help` stampa `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pacchetto | Minimo | Serve a | Licenza |
|---|---|---|---|
| `demoparser2` | 0.42 | leggere i file `.dem` (giocatori per tick, eventi di gioco) | MIT |
| `pyarrow` | 15 | scrivere la tabella Parquet | Apache-2.0 |
| `pandas` | 2.0 | le tabelle intermedie | BSD-3-Clause |
| `numpy` | 1.24 | i calcoli su di esse | BSD-3-Clause |
| `pytest` | 8.0 | solo i test | MIT |

I comandi `demos` e `scoreboard` non richiedono altro.

## Per l'esportazione della mappa: Counter-Strike 2 e la CLI di Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` legge la mappa dal gioco che hai installato, e la decodifica con la **riga di comando di
Source2Viewer**, un programma separato del progetto
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (licenza MIT). Non è incluso e non si
può installare con pip.

1. Scarica la build **CLI** per il tuo sistema dalle
   [release di ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases) e decomprimila
   dove preferisci.
2. Fai in modo che venga trovata, in uno di tre modi. Vengono provati in questo ordine:
   1. `--source2viewer <percorso dell'eseguibile>` sulla riga di comando;
   2. la variabile d'ambiente `HEAT3D_SOURCE2VIEWER` impostata con il percorso dell'eseguibile;
   3. un eseguibile chiamato `Source2Viewer-CLI` o `Source2Viewer-CLI.exe` nel `PATH`.

   Un candidato viene usato solo se il suo percorso esiste. Se non se ne trova nessuno, il comando si ferma con
   `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set HEAT3D_SOURCE2VIEWER,
   or pass --source2viewer`.

Impostare la variabile, per esempio:

```bash
# Windows (PowerShell), per la sessione corrente
$env:HEAT3D_SOURCE2VIEWER = "C:\Tools\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/tools/Source2Viewer-CLI
```

### Dove viene cercato CS2 {#where-cs2-is-looked-for}

La mappa è un archivio `.vpk` nella cartella del gioco:
`<libreria Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<mappa>.vpk`.
Le librerie di Steam vengono trovate partendo da queste radici, e da ogni `"path"` elencato nel file
`config\libraryfolders.vdf` di ciascuna radice:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Quando Steam si trova altrove, passa la cartella di CS2 stessa con `--game` (la cartella che contiene `game\csgo`), oppure
passa il percorso del `.vpk` invece del nome della mappa. Vedi [Esportazione della mappa](map-export.md).

## Verificare l'installazione {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

I test girano su un demo sintetico costruito nel codice e non richiedono né demo, né gioco, né Source2Viewer (vedi
[Sviluppo](development.md)).

Ogni avvio di `python -m heat3d_cs2` controlla prima, al massimo ogni sei ore, se è uscita una release più recente; imposta
`HEAT3D_NO_UPDATE=1` per disattivarlo (vedi [Aggiornamenti](updates.md)).
