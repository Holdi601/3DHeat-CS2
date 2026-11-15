---
title: "Leggere un demo"
nav_order: 5
lang: "it"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Leggere un demo {#reading-a-demo}

Cosa si ricava da un singolo file `.dem`, prima che venga interpretato qualcosa. Codice:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Un demo di CS2 è la registrazione del server stesso (SourceTV): ogni giocatore, ogni tick, 64 tick al secondo
(`TICKRATE = 64`). Viene letto con [demoparser2](https://github.com/LaihoE/demoparser) in tre chiamate, e il risultato
viene conservato così com'è, in un `RawPart`:

| Campo | Contiene |
|---|---|
| `path` | il file |
| `map` | `map_name` dall'intestazione del demo (`de_x`); vuoto se l'intestazione non ne ha uno |
| `samples` | una riga per giocatore per tick campionato: i campi del giocatore e delle regole sotto, più `tick`, `steamid`, `name` |
| `events` | nome dell'evento -> le sue righe, con i campi dei giocatori preceduti da `user_`, `attacker_`, `assister_` come li nomina il parser |

Niente in `demo.py` decide cos'è un round o chi ha vinto; questo è compito di [Costruire una partita](building-matches.md).

## I tick campionati {#the-sampled-ticks}

`parse_ticks` viene chiamato per i tick `0, N, 2N, ...` fino a 4.000.000 (`LAST_TICK`, ben oltre qualunque partita - 17 ore a
64 tick al secondo), dove *N* è `--every` (predefinito 8). Il parser si ferma alla fine del demo. Ogni giocatore presente in un
tick campionato dà una riga, che sia vivo, morto, in osservazione o allenatore; il filtro avviene più tardi.

Il passo del campionamento conta anche oltre la densità della mappa di calore: il momento in cui un round viene deciso si legge da
questi campioni (vedi [Costruire una partita](building-matches.md#rounds)), quindi le fini dei round sono precise a un passo
(1/8 s per impostazione predefinita).

### Campi del giocatore {#player-fields}

| Proprietà | Diventa |
|---|---|
| `X`, `Y`, `Z` | la posizione, in unità di gioco (pollici), Z verso l'alto. demoparser2 dà l'origine del giocatore, cioè i piedi. |
| `yaw`, `pitch` | la direzione dello sguardo (gradi), trasformata in un vettore unitario |
| `health`, `armor_value` | salute, armatura |
| `team_num` | il lato: 2 = T, 3 = CT; qualunque altro valore (spettatori, 0, 1) non è un lato |
| `team_clan_name` | il nome della squadra come lo mostra il server, usato per nominare le squadre |
| `active_weapon_name` | l'arma in mano, come la chiama il gioco (`AK-47`, `Karambit`) |
| `is_alive` | se il giocatore è vivo - solo i giocatori vivi diventano posizioni |
| `last_place_name` | il nome del luogo della mappa (`BombsiteA`) |
| `balance` | denaro |
| `current_equip_value` | il valore di ciò che il giocatore porta |

### Campi delle regole di gioco {#game-rules-fields}

Letti insieme, una volta per riga giocatore (sono gli stessi per tutti in un tick):

| Proprietà | Serve a |
|---|---|
| `game_time` | l'orologio del server, in secondi |
| `total_rounds_played` | il conteggio dei round, che prosegue tra i file di una partita |
| `round_win_status` | chi ha vinto il round appena giocato: 1 pareggio, 2 T, 3 CT |
| `round_win_reason` | come (il `CSRoundEndReason` del gioco) |
| `team_rounds_total` | il punteggio di ciascun lato |
| `is_warmup_period` | il riscaldamento viene escluso ovunque |
| `is_freeze_period` | il freeze time viene escluso dalle posizioni |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | l'overtime in corso, 0 in regolamentare: i round di overtime non sono round pistola (il parser non ha un nome più breve) |

## Gli eventi {#the-events}

Ogni evento qui sotto viene letto quando il demo lo dichiara (`list_game_events`), con `X`, `Y`, `Z`, `team_num`,
`last_place_name` e `which_bomb_zone` (la zona della bomba in cui sta il giocatore: 0 nessuna, 1 A, 2 B) per ogni giocatore
che l'evento nomina, e `total_rounds_played` e `is_warmup_period` del gioco a quel tick:

| Evento | Diventa |
|---|---|
| `player_death` | uccisioni e morti; usa `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | danni; usa `dmg_health` (danno inflitto alla salute), `health` (salute rimasta), `weapon` |
| `player_blind` | giocatori accecati dal flash; usa `blind_duration` |
| `weapon_fire` | colpi e lanci di granate; usa `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | dove sono esplose le granate; usa i `x`, `y`, `z` propri dell'evento (l'evento non ha un nome di luogo per quel punto, solo quello di chi ha lanciato) |
| `bomb_planted` | il piazzamento; usa la `which_bomb_zone` e il luogo del piazzatore, e `site` (il numero di entità della zona) |
| `bomb_defused` | il disinnesco |
| `bomb_exploded` | quando è esplosa la bomba: il tempo della riga `explode` |
| `round_freeze_end` | dove inizia ogni round |
| `round_prestart` | dove finisce il tempo dopo un round deciso |
| `round_announce_match_start` | dove inizia la partita live |

## Due fatti sui demo che ne decidono la lettura {#two-facts-about-demos-that-decide-how-they-are-read}

- **Una partita può essere divisa tra più file**, e i nomi dei file non dicono il loro ordine. Il conteggio dei round
  (`total_rounds_played`) prosegue tra di essi, e di solito anche l'orologio del server, quindi le parti si possono mettere in
  ordine da ciò che contengono.
- **Una registrazione può iniziare prima della partita**: riscaldamento, un riavvio, un round di coltello. La partita inizia
  all'**ultimo** `round_announce_match_start` di un file; prima di esso tutto viene escluso, e il riscaldamento viene escluso
  ovunque.
