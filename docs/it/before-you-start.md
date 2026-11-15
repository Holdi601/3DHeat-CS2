---
title: Prima di iniziare
nav_order: 2
lang: "it"
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Prima di iniziare {#before-you-start}

Non hai mai usato la riga di comando? Questa pagina ti porta dal nulla a un 3DHeat CS2 funzionante in circa
dieci minuti. Digita i comandi in un *terminale*, una finestra in cui scrivi una riga e premi Invio.

## 1. Installa Python {#install-python}

1. Scarica Python 3.10 o successivo da <https://www.python.org/downloads/>.
2. Esegui il programma di installazione. Nella prima schermata spunta **Add python.exe to PATH**, poi
   clicca su **Install Now**.
3. Verificalo: apri un terminale (passo 3) e digita `python --version`. Dovresti vedere `Python 3.` e un
   numero pari o superiore a 10.

Su Linux o macOS, Python di solito è già installato: usa `python3` dove queste pagine dicono `python`.

## 2. Procurati 3DHeat CS2 {#get-3dheat-cs2}

Scarica lo zip dalla [pagina delle release](https://github.com/Holdi601/3DHeat-CS2/releases) e decomprimilo,
per esempio in `C:\Tools\3DHeat-CS2`. (Se hai Git, anche `git clone` funziona.)

## 3. Apri un terminale in quella cartella {#open-a-terminal-in-that-folder}

- **Windows:** apri la cartella in Esplora file, clicca nella barra degli indirizzi, digita `powershell` e
  premi Invio. Si apre una finestra blu o nera, già in quella cartella.
- **macOS / Linux:** apri *Terminale* e digita `cd ` (con uno spazio), trascina la cartella nella finestra,
  premi Invio.

`cd <cartella>` sposta il terminale in un'altra cartella. Tutti i comandi di queste pagine si digitano nella
cartella dello strumento.

## 4. Installa ciò che serve {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Alla fine dovresti vedere `Successfully installed ...` (oppure `Requirement already satisfied`).

## 5. Verifica che funzioni {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Dovresti vedere: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Come leggere i comandi di queste pagine {#how-to-read-the-commands-on-these-pages}

- Le parole tra `<parentesi angolari>` sono segnaposto: al loro posto scrivi il tuo file o la tua cartella,
  senza le parentesi. `python -m heat3d_cs2 demos <file demo o cartelle> -o out` significa che sostituisci la
  parte tra parentesi.
- Un percorso con spazi va tra virgolette: `"C:\My Games\my file"`.
- Le righe che iniziano con `#` negli esempi sono commenti; non digitarle.
- Il successo appare così: dopo `demos`, una riga `1 match(es), 1 at a time` e poi una riga per partita che
  termina con `lost 0`.

## Errori comuni {#common-errors}

| Vedi | Fai questo |
|---|---|
| `'python' is not recognized` oppure `command not found` | Python non è nel PATH: esegui di nuovo il programma di installazione e spunta **Add python.exe to PATH**, poi apri un nuovo terminale. Su macOS/Linux prova `python3`. |
| `No module named ...` | il passo 4 è stato saltato oppure eseguito in un'altra cartella: fai `cd` nella cartella dello strumento e ripeti. |
| `pip is not recognized` | usa `python -m pip ...` invece di `pip ...`. |
| `No such file or directory` / `can't open file` | il terminale è nella cartella sbagliata, oppure il percorso è scritto male: controllalo, e metti i percorsi con spazi tra virgolette. |
| testo rosso che termina con una riga `error:` | leggi l'ultima riga: dice cosa manca. La pagina [Comandi](commands.md) elenca i messaggi. |
