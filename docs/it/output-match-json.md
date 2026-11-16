---
title: "Il documento partita"
nav_order: 9
lang: "it"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Il documento partita (`<partita>.match.json`) {#the-match-document-matchjson}

Un documento JSON per partita, accanto alla sua tabella: squadre, punteggio, ogni round con il suo esito, economia,
piazzamento, uccisioni, clutch e sopravvissuti, e la riga del tabellone di ogni giocatore. È ciò che carica la scheda
Partita del visualizzatore di 3DHeat. Codice: `summary()` in
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py); i numeri sono definiti in
[Statistiche](statistics.md).

Il file è UTF-8, indentato di uno spazio, e conserva i caratteri non ASCII (nomi di giocatori e squadre) così come sono. I
tempi sono secondi, arrotondati a tre decimali per i round e a due per le uccisioni e il piazzamento.

## Il documento {#the-document}

| Campo | Tipo | Cosa |
|---|---|---|
| `format` | stringa | sempre `heat3d-cs2-match` - come un lettore riconosce il file |
| `version` | numero | `3`. Un documento di versione 1 dà il `time` di un piazzamento in secondi di partita; dalla 2 è in secondi dentro il round, come per un'uccisione. La 3 aggiunge i campi da `header` in poi, e il freeze time alla tabella. |
| `match` | stringa | il nome della partita, come sono chiamati i file |
| `map` | stringa | la mappa (`de_x`) |
| `demos` | stringa[] | i file demo da cui è stata costruita, solo i nomi dei file, nell'ordine della partita |
| `teams` | stringa[] | i nomi delle squadre in ordine di comparsa (round 1: prima il lato T) |
| `score` | oggetto | nome della squadra -> round vinti: il punteggio dell'ultimo round |
| `winner` | stringa o null | la squadra che ha vinto la partita, dove la registrazione mostra la fine; null per una registrazione che si interrompe presto, un overtime senza il pannello di vittoria, o un pareggio |
| `winnerSource` | stringa o null | come si sa `winner`: `winPanel` (il pannello di vittoria della partita del gioco), `surrender`, `regulation` (più della metà dei round regolamentari) |
| `rounds` | oggetto[] | ogni round completo, in ordine - [sotto](#rounds) |
| `incomplete` | numero[] | numeri di round interrotti dalla fine di un demo ed esclusi |
| `missing` | numero[] | numeri di round prima del primo che i demo contengono: `[1, 2]` quando la registrazione inizia dal round 3 |
| `halfLength` | numero o null | round in una metà regolamentare, dal punto in cui i lati si scambiano per la prima volta (`12` nel formato a 24 round); null quando la registrazione non mostra lo scambio |
| `pistolRounds` | numero[] | i round pistola con cui viene contato il `buy`: il round 1, e il round dopo la metà quando `halfLength` è noto; mai un round di overtime |
| `players` | oggetto[] | il tabellone - [sotto](#players) |
| `conventions` | oggetto | le definizioni dietro i numeri, [sotto](#conventions) |
| `header` | oggetto | l'intestazione del primo demo così come la dà il parser: nome del server, versione della patch, versione del demo, mappa |
| `profiles` | oggetto | Steam ID -> ciò che resta uguale per un giocatore durante la partita: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (l'ultimo visto) |
| `playerInfo` | oggetto[] | ogni giocatore elencato nei demo, anche allenatori e telecronisti: Steam ID, nome, numero di squadra |
| `skins`, `itemDrops` | oggetto[] | skin delle armi e oggetti lasciati cadere, dove il demo li ha (i demo di torneo dalla diretta non ne hanno) |
| `chat` | oggetto[] | ogni riga di chat della partita: tempo, round, giocatore, lato, testo |
| `events` | oggetto[] | ogni evento di gioco che non riguarda alcun giocatore, in ordine di tempo, con tutti i suoi campi: segnali e fasi dei round, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (le impostazioni del server quando cambiano), le inquadrature di chase e fisse del regista della diretta, `cs_win_panel_match`, ... |
| `state` | oggetto[] | lo stato del gioco dove è cambiato: tempo, campo, valore - timeout (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), la bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, i giocatori vivi, `match_start_time` e `round_start_time` del server |
| `selfCheck` | oggetto | `completeness`: dove è finito tutto ciò che c'è nel demo - per nome di evento, classe di proprietà, messaggio di rete, frame e tabella delle stringhe, i conteggi `seen`, `decoded`, `partial`, `raw` e `lost`, i file accessori scritti, il totale `lost` (0 salvo `--no-bulk`), le proprietà che il parser elenca ma non sa leggere (`unreadProps`). La convenzione: [I convertitori conservano tutto](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); i file accessori: la sezione Completezza del README |

## Round {#rounds}

| Campo | Tipo | Cosa |
|---|---|---|
| `number` | numero | il round, a partire da 1 |
| `start` | numero | secondi di partita quando è finito il freeze time |
| `end` | numero | secondi di partita quando il round è stato deciso |
| `until` | numero | secondi di partita quando è iniziato il round successivo (la fine della fase after) |
| `winner` | stringa | `T` o `CT`; vuoto per un pareggio |
| `winnerTeam` | stringa | il nome della squadra del lato vincitore; vuoto per un pareggio |
| `reason` | stringa | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` o `other` |
| `score` | oggetto | nome della squadra -> round vinti dopo questo |
| `sides` | oggetto | nome della squadra -> `T` / `CT` in questo round |
| `equipment` | oggetto | lato -> valore totale dell'equipaggiamento dei suoi giocatori vivi a fine freeze time, in dollari |
| `buy` | oggetto | lato -> `pistol`, `eco`, `force` o `full` |
| `plant` | oggetto o null | il piazzamento della bomba: `site` (`A` o `B`; vuoto quando il demo non lo dice), `time` (secondi **dentro il round**, come per un'uccisione), `player`, `steamid`, `x`, `y`, `z` (unità di gioco), `place` (il nome del luogo del piazzatore: dove giaceva la bomba) |
| `survivors` | oggetto | lato -> nomi dei giocatori iniziali ancora vivi quando il round è stato deciso, in ordine alfabetico |
| `clutches` | oggetto[] | ciascuno: `player`, `steamid`, `side`, `against` (nemici vivi quando il giocatore è diventato l'ultimo), `won` |
| `kills` | oggetto[] | ogni morte del round, in ordine - sotto |

Come vengono trovati: [Costruire una partita](building-matches.md#rounds); clutch e sopravvissuti:
[Statistiche](statistics.md#clutches).

### Le uccisioni di un round {#a-rounds-kills}

Ogni morte del round, compresa la fase after:

| Campo | Tipo | Cosa |
|---|---|---|
| `time` | numero | secondi **dentro il round** (dalla fine del freeze time) |
| `attacker`, `attackerSide` | stringa | l'assassino e il suo lato; vuoto per il mondo |
| `victim`, `victimSide` | stringa | la vittima e il suo lato |
| `assister` | stringa o null | il giocatore che ha assistito, o null |
| `flashAssist` | bool | l'assistenza è stata un flash |
| `weapon` | stringa | come la chiama il gioco |
| `headshot` | bool | |
| `wallbang` | bool | il proiettile ha attraversato qualcosa |
| `throughSmoke` | bool | l'uccisione è avvenuta attraverso il fumo |
| `noscope` | bool | un'arma con mirino ha sparato senza mirare |
| `attackerBlind` | bool | l'assassino era stato accecato |
| `opening` | bool | la prima uccisione di un nemico nel round |
| `traded` | bool | questa morte è stata vendicata entro 5 s |
| `trade` | bool | questa uccisione ha vendicato un compagno entro 5 s |
| `teamkill` | bool | attaccante e vittima sullo stesso lato, due giocatori diversi |
| `suicide` | bool | attaccante e vittima sono lo stesso giocatore (una granata propria, per esempio); non è un compagno ucciso |
| `after` | bool | l'uccisione è avvenuta dopo che il round era stato deciso |
| `place` | stringa | dove si trovava la **vittima** (il nome del luogo sulla mappa) |

## Giocatori {#players}

Una voce per giocatore, per nome di squadra e poi dal migliore per uccisioni meno morti, poi uccisioni:

| Campo | Tipo | Cosa |
|---|---|---|
| `name`, `steamid`, `team` | stringa | chi |
| `kills`, `deaths` | numero | |
| `assists`, `flashAssists` | numero | assistenze senza e con un flash |
| `diff` | numero | uccisioni - morti |
| `adr` | numero | danno medio per round giocato, salute persa |
| `kast` | numero | percentuale dei round giocati con un'uccisione, un'assistenza, una sopravvivenza o una morte scambiata |
| `headshotPct` | numero | percentuale delle uccisioni che sono colpi alla testa |
| `openingKills`, `openingDeaths` | numero | duelli di apertura vinti e persi |
| `tradeKills`, `tradedDeaths` | numero | uccisioni di scambio; morti che sono state scambiate |
| `multiKills` | oggetto | `{"2k": n, "3k": n, "4k": n, "5k": n}`: round con quel numero di uccisioni |
| `clutches`, `clutchesWon` | numero | |
| `utilityDamage` | numero | danno con HE, molotov, incendiarie |
| `enemiesFlashed` | numero | nemici accecati per almeno 1 s |
| `plants`, `defuses` | numero | |
| `teamkills` | numero | compagni uccisi; i suicidi non contano |
| `roundsPlayed` | numero | round iniziati |

Ogni definizione: [Statistiche](statistics.md#the-scoreboard-line).

## Convenzioni {#conventions}

Scritte in ogni documento perché chi legge sappia cosa significano i numeri senza questa pagina:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Un esempio {#an-example}

Dal demo sintetico di due round dei test, accorciato (`...` indica ciò che è stato omesso):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

L'ordine delle chiavi dentro `survivors`, `equipment` e `buy` non è fisso.
