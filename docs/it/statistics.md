---
title: "Statistiche"
nav_order: 7
lang: "it"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistiche {#statistics}

Cosa ha fatto ogni giocatore in una partita, e come è andato ogni round: il tabellone e l'elenco dei round del
[documento partita](output-match-json.md). Codice:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Tutto è contato dalla partita costruita come in [Costruire una partita](building-matches.md): i suoi record di uccisione, i
suoi danni (salute persa, solo nemici), i suoi accecamenti (solo nemici) e le sue righe.

![il tabellone di testo di una partita sintetica](../assets/img/scoreboard.svg)

## Le convenzioni {#the-conventions}

Dove il gioco stesso non definisce un numero, queste sono le definizioni. Sono anche scritte in ogni documento partita sotto
`conventions`.

| Termine | Definizione |
|---|---|
| **Scambio** | Una morte è *scambiata* quando il suo assassino viene ucciso da un compagno della vittima entro **5 s**; quella uccisione è un'*uccisione di scambio*. |
| **Apertura** | La prima uccisione di un nemico nel round mentre è live. Un compagno ucciso, un suicidio o una morte causata dal mondo prima di essa vengono saltati. |
| **KAST** | La quota di round in cui un giocatore ha fatto una **K**ill (uccisione), una **A**ssistenza (conta anche l'assistenza a un flash), è **S**opravvissuto, o è stato **T**raded (scambiato). |
| **Danno** | Salute realmente persa, solo nemici: un colpo alla testa da 137 danni su un giocatore con 40 di salute vale 40. |
| **Clutch** | Essere l'ultimo giocatore vivo di un lato con ancora nemici in piedi; vinto quando il lato vince il round. |
| **Buy** | Per lato, dal valore medio dell'equipaggiamento a fine freeze time: il primo round di ogni metà regolamentare è un round pistola (il round 1, e il round dopo la metà, purché la partita li abbia giocati), l'overtime non ne ha; poi sotto $1.500 eco, sotto $4.000 force, altrimenti full. |

## Chi ha iniziato ogni round {#who-started-each-round}

Molti numeri richiedono di sapere chi ha giocato un round. I **giocatori iniziali** di un round sono, per lato, ogni giocatore con
una riga di posizione viva entro un secondo dalla posizione più antica di quel round (cioè nel primo secondo dopo la fine del
freeze time). I **round giocati** di un giocatore sono i round che ha iniziato. Se un giocatore non ne ha iniziato nessuno (non
aveva mai una riga del genere), si usa invece il numero di round della partita, così che nessuna divisione sia per zero.

## La riga del tabellone {#the-scoreboard-line}

Una voce per giocatore (vedi [il documento partita](output-match-json.md#players) per i nomi dei campi). "Uccisione di nemico"
qui sotto significa un'uccisione con un attaccante, non un compagno ucciso e non un suicidio (la propria morte).

| Campo | Conta |
|---|---|
| `kills` | uccisioni di nemici, della fase live e della fase after |
| `deaths` | ogni morte: da nemici, compagni, da sé o dal mondo |
| `assists` | uccisioni di nemici che questo giocatore ha assistito senza flash (chi assiste non deve essere l'assassino) |
| `flashAssists` | uccisioni di nemici che questo giocatore ha assistito con un flash |
| `diff` | uccisioni - morti |
| `adr` | danno (salute persa, solo nemici, entrambe le fasi) / round giocati, un decimale |
| `kast` | 100 x (round con un'uccisione, un'assistenza o un'assistenza con flash, una sopravvivenza o una morte scambiata) / round giocati, un decimale. *Sopravvivenza* è: un giocatore iniziale del round che non è morto in esso, in nessuna delle due fasi. |
| `headshotPct` | 100 x uccisioni alla testa / uccisioni, un decimale; 0 senza uccisioni |
| `openingKills`, `openingDeaths` | duelli di apertura vinti e persi |
| `tradeKills` | uccisioni che hanno scambiato la morte di un compagno |
| `tradedDeaths` | morti che sono state scambiate |
| `multiKills` | round con 2, 3, 4 e 5 uccisioni di nemici (`2k`, `3k`, `4k`, `5k`); più di cinque conta come `5k`. Contano entrambe le fasi. |
| `clutches`, `clutchesWon` | clutch giocati e vinti (sotto) |
| `utilityDamage` | danno inflitto con granate HE, molotov e incendiarie, un decimale |
| `enemiesFlashed` | nemici accecati per **almeno 1,0 s** dai flash di questo giocatore |
| `plants`, `defuses` | piazzamenti e disinneschi di bomba (righe della tabella) |
| `teamkills` | compagni uccisi. Un suicidio - attaccante e vittima lo stesso giocatore, una granata propria per esempio - non lo è: è solo una morte. |
| `roundsPlayed` | round iniziati, come sopra |

I giocatori sono elencati per nome di squadra (in ordine alfabetico), e dentro una squadra per `diff`, poi per `kills`, il migliore per primo.

Note sui casi limite:

- Un'uccisione nella fase after - chi vince a caccia di un giocatore che risparmia - conta come un'uccisione, una morte, per ADR,
  uccisioni multiple e KAST come qualunque altra.
- Gli wallbang sono contati internamente per giocatore ma non scritti nel documento partita; ogni uccisione nell'elenco del round
  dice se lo era.
- La parte *scambiata* di KAST accredita la vittima di una morte scambiata in quel round.
- Le uccisioni di compagni e i suicidi aggiungono una morte alla vittima ma nessuna uccisione a nessuno; un'uccisione di compagno
  aggiunge a `teamkills` dell'assassino, un suicidio non aggiunge a nient'altro.

## Clutch {#clutches}

Per ogni round, i giocatori iniziali di entrambi i lati sono considerati vivi, e le uccisioni live del round vengono percorse in
ordine. Dopo ogni morte la vittima viene tolta, e ogni lato viene controllato: un lato con esattamente **un** giocatore rimasto, e
almeno un nemico ancora vivo, dà un clutch a quel giocatore **contro** il numero di nemici vivi in quel momento. Ogni giocatore ha al
massimo un clutch per round; è **vinto** quando il lato di quel giocatore ha vinto il round.

Conseguenze della definizione:

- Entrambi i lati possono avere un clutch nello stesso round. Se un lato scende a uno per primo (un 1v3, per esempio) e anche l'altro
  viene ridotto a uno, il secondo giocatore è in un clutch 1v1 tutto suo.
- `against` è il conteggio quando il giocatore è diventato l'ultimo, non alla fine.
- Le uccisioni della fase after non vengono percorse, quindi né iniziano un clutch né ne cambiano uno.

## Sopravvissuti {#survivors}

I **sopravvissuti** di un round sono, per lato, i suoi giocatori iniziali meno chiunque sia morto mentre era live. Un giocatore ucciso
nella fase after mentre risparmiava è ancora un sopravvissuto nell'elenco dei round - ma non è *sopravvissuto* ai fini di KAST.

## L'elenco dei round {#the-round-list}

Ogni round del documento partita riporta il suo esito, punteggio, lati, economia, piazzamento, sopravvissuti, clutch e le sue
uccisioni in ordine; vedi [Il documento partita](output-match-json.md#rounds).

## Il tabellone di testo {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` stampa questi numeri per squadra; vedi
[Comandi](commands.md#scoreboard---a-match-as-text).
