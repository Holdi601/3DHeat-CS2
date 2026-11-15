---
title: "Limiti"
nav_order: 13
lang: "it"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Limiti {#limits}

Cosa presuppone il convertitore, cosa non gestisce e cosa non è verificato. Ogni punto deriva dal codice così com'è.

## Cosa legge {#what-it-reads}

- **Solo file `.dem` non compressi.** `.dem.zst`, `.dem.bz2`, `.rar` e `.zip` devono essere decompressi prima.
  L'estensione viene riconosciuta in qualunque maiuscolo o minuscolo (`.dem`, `.DEM`), nelle cartelle come per i
  file indicati per nome.
- **Partite di defusal.** I motivi di fine round, il piazzamento della bomba e il sito, i tipi di buy e i round
  pistola sono quelli della modalità di disinnesco della bomba. Le mappe con ostaggi, Wingman e le altre modalità non
  vengono gestite in modo speciale e non sono verificate.
- **64 tick al secondo** sono presupposti (`TICKRATE = 64`) per ogni tempo calcolato dai tick; i server di CS2 girano
  a 64.
- Si presuppone un **demo dal server** (SourceTV): contiene ogni giocatore. Una registrazione lato client (demo POV)
  non è stata provata.

## Partite e round {#matches-and-rounds}

- **I file vengono raggruppati per nome.** Le parti di una stessa partita devono avere lo stesso nome a parte un suffisso
  `-pN` / `_pN`; i file di una partita con nomi non collegati diventano partite separate, e file con lo stesso nome in
  cartelle diverse vengono raggruppati insieme (poi divisi in catene se non continuano l'uno dall'altro).
- **La partita live inizia all'ultimo `round_announce_match_start`** di un file. Un round di coltello non seguito da
  quell'annuncio viene contato come un round.
- **La fine di ogni round è precisa a un campione** (`--every` tick, 1/8 s per impostazione predefinita), perché la
  decisione viene letta dallo stato di gioco campionato. Un `--every` molto grande può perdere una breve finestra tra la
  fine di un round e l'inizio del successivo, ed escludere il round come incompleto.
- **Pareggi.** Un round pareggiato (stato di vittoria 1, motivo 10) è deciso senza vincitore: `winner` è vuoto e nessuno
  dei due lati lo ha vinto. Non è stato incontrato alcun pareggio in un demo reale per verificarlo; è verificato su
  quello sintetico.
- **I round interrotti** dalla fine di un file vengono esclusi (`incomplete`), non indovinati; i round prima del primo
  nei file vengono elencati come `missing`.
- **I round pistola** seguono la durata della metà che la registrazione mostra: dove i lati si scambiano per la prima
  volta tra due round regolamentari consecutivi. Una registrazione che non mostra quello scambio (inizia dopo l'intervallo,
  finisce prima, o manca un round da una parte o dall'altra) conosce solo il round 1 come round pistola. L'overtime non ne
  ha.
- **Squadre.** Una squadra è il nome di clan visto più spesso tra i suoi giocatori. Senza nomi di clan le squadre sono
  `Started T` e `Started CT`. Un giocatore che cambia squadra a metà partita mantiene una sola squadra.

## Eventi {#events}

- **Viene letto tutto ciò che il parser offre**, con queste eccezioni: la velocità dei giocatori (il parser la ricava dalle
  posizioni; non è nel demo), la voce (audio, `parse_voice`), e il `weapon_fire` della bomba (l'inizio di un piazzamento,
  che `bomb_beginplant` ha già). Le traiettorie delle granate vengono conservate al campionamento dei giocatori
  (`--every`) e dove ogni granata si è fermata, non a ogni tick.
- **Le righe fuori da un round** (riscaldamento, una pausa tra l'inizio della partita e il primo freeze time oltre i due
  minuti) vengono escluse dalla tabella; gli eventi che non riguardano alcun giocatore sono tutti nel campo `events` del
  documento partita.
- **Le righe di esplosione** (`smoke`, `flash`, `he`, `molotov`, `decoy`) non hanno `place`: il demo indica i luoghi per i
  giocatori, non per le granate. Il luogo di chi ha lanciato in quel momento è in `throwerPlace`.
- **Il sito di un piazzamento** viene dalla zona della bomba in cui il gioco dice che stava il piazzatore, altrimenti dal
  nome del luogo del piazzatore, altrimenti da un altro piazzamento nella stessa zona dello stesso file. Dove nessuno di
  questi lo dice, `site` è vuoto.
- **Una morte causata dal mondo** (una caduta, la bomba) non ha un attaccante: nessuna uccisione, nessun compagno ucciso,
  nessuna apertura; è una morte.

## Statistiche {#statistics}

- **I round giocati** derivano da chi aveva una posizione nel primo secondo dopo il freeze time. Un giocatore che si
  collega più tardi in un round non conta come se lo avesse giocato (le sue uccisioni contano comunque).
- **Sopravvivenza per KAST**: un giocatore ucciso nella fase after non è sopravvissuto ai fini di KAST, mentre l'elenco dei
  round lo nomina ancora tra i sopravvissuti.
- **Entrambi i giocatori di un 1v1** possono essere accreditati di un clutch nello stesso round; vedi
  [Statistiche](statistics.md#clutches).
- **Il danno da utility** sono le granate HE, i molotov e le incendiarie; un'uccisione o un colpo causato da un flash o da
  un decoy lanciato non è danno da utility.

## Esportazione della mappa {#map-export}

- Richiede il gioco installato (o il `.vpk`) e la CLI di Source2Viewer; non scarica nulla.
- Esporta solo `world_physics`; i clip brush e il cielo vengono esclusi perché il loro nome contiene `clip` o `sky`, in
  qualunque maiuscolo o minuscolo.
- Il terreno si distingue dalla struttura solo dalla normale della faccia (componente Z 0,7 o più), quindi una rampa ripida
  è struttura e un tetto piatto è terreno.
- Il file è in pollici, non in metri.

## Memoria e tempo {#memory-and-time}

- Una partita viene tenuta in memoria per intero mentre viene costruita, in un lavoro per partita. Con molti lavori e un
  `--every` piccolo, la memoria si somma: abbassa `--jobs` se una macchina è a corto di memoria.
- Una partita viene scritta solo quando è costruita: prima il `.parquet`, poi il `.match.json`. Una corsa interrotta nel
  mezzo lascia una tabella senza il suo documento partita; una partita conta come scritta solo con entrambi, quindi la
  successiva la converte di nuovo. Le partite non ancora iniziate vengono semplicemente prese dalla corsa successiva.
