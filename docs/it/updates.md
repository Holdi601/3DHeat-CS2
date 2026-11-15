---
title: "Aggiornamenti"
nav_order: 14
lang: "it"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Aggiornamenti {#updates}

3DHeat CS2 si mantiene aggiornato dalle
[release su GitHub](https://github.com/Holdi601/3DHeat-CS2/releases) di questo repository. Codice:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Il controllo all'avvio {#the-check-at-start-up}

Ogni `python -m heat3d_cs2 ...` chiede prima se è uscita una release più recente, prima ancora di leggere i suoi argomenti:

1. La versione installata è il file `VERSION` nella radice del repository (`0` se non può essere letto).
2. La release più recente viene chiesta a
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, con un timeout di **5 secondi**. La risposta viene
   tenuta in cache per **6 ore** in `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (su sistemi senza `LOCALAPPDATA`:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), così la richiesta viene fatta al massimo ogni sei ore. "No release
   yet" (HTTP 404) viene salvato in cache come una risposta. Offline, con limite di richieste superato, dietro un proxy - ogni
   altro errore - lo strumento va avanti con la versione che ha, e non salva nulla in cache.
3. Le versioni vengono confrontate come numeri: `v1.2.3` e `1.2.3` sono uguali, tutto ciò che segue un `-` o un `+` viene
   ignorato, le parti mancanti valgono 0.

Quando è disponibile una release più recente, lo dice sul flusso degli errori:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- In un terminale (sia l'input sia il flusso degli errori sono terminali) chiede. Invio, `y`, `yes`, `j` o `ja` aggiornano; qualunque
  altra risposta prosegue senza modifiche. Dopo un aggiornamento **lo stesso comando viene rieseguito**, sul codice nuovo.
- Senza terminale - un'esecuzione pianificata, una pipe - si limita a stampare dove aggiornare e prosegue:
  `Run python -m heat3d_update in <cartella> to update.`

`HEAT3D_NO_UPDATE=1` disattiva il controllo. Qualunque valore diverso da vuoto, `0`, `false` o `no` significa attivo.

## Aggiornare su richiesta {#updating-on-request}

```bash
python -m heat3d_update            # aggiorna alla release più recente
python -m heat3d_update --check    # dice solo se ce n'è una
```

Questo chiede sempre a GitHub (la cache non viene usata). Stampa `Up to date: <versione>.`,
`No release found (this is <versione>); offline, or nothing published yet.`, oppure `<nuova> is out (this is <attuale>): <url>` e
poi aggiorna (salvo `--check`). Codice di uscita `1` quando un aggiornamento è stato tentato e non è riuscito, `0` altrimenti.

## Come viene applicato un aggiornamento {#how-an-update-is-applied}

Dipende da come è stata installata la copia:

- **Un checkout di git** (c'è un `.git` nella radice e `git` nel `PATH`): `git pull --ff-only`. Viene rifiutato mentre i file tracciati
  hanno modifiche locali ("this checkout has local changes; commit or stash them, then run `git pull`"): sono lavoro di qualcuno, e un
  aggiornamento non decide cosa ne sarà. I file non tracciati non lo bloccano.
- **Una copia scaricata**: l'archivio sorgente della release (lo zipball di GitHub) viene scaricato e decompresso in una cartella
  temporanea - le voci che finirebbero fuori da essa vengono saltate - e il suo `VERSION` deve essere la versione dichiarata dalla
  release, altrimenti non si cambia nulla ("the archive is version X, not Y"). Poi i suoi file vengono copiati sopra la cartella.
  I file che non fanno parte della release - i tuoi demo, gli output, l'ambiente virtuale, tutto ciò che hai creato - non vengono mai
  toccati. I moduli Python che la release non ha più vengono eliminati dai pacchetti dello strumento (le cartelle `heat3d_*`), così
  un modulo vecchio non può fare ombra al suo sostituto.

Se un aggiornamento fallisce, il messaggio viene stampato e lo strumento prosegue con la versione che ha.
