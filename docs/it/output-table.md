---
title: "La tabella della mappa di calore"
nav_order: 8
lang: "it"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# La tabella della mappa di calore (`<partita>.parquet`) {#the-heatmap-table-parquet}

Un file Parquet per partita: la posizione di ogni giocatore vivo, campionata, e ogni evento nel punto in cui è avvenuto, una
riga ciascuno - una tabella lunga che il visualizzatore di 3DHeat legge come mappa di calore, e qualunque altro strumento come
una normale tabella. Codice:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) (il file),
[`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) (le righe; vedi
[Costruire una partita](building-matches.md)).

Il file è scritto con compressione Snappy in gruppi di righe da 256.000. Le righe sono ordinate per `time`, poi per `event`.
Vi sono incluse solo le righe dentro un round (dalla fine del suo freeze time fino all'inizio del round successivo).

Sul demo sintetico dei test, le righe di evento del primo round:

![righe di evento della tabella](../assets/img/table-rows.svg)

In un contenitore `.3dheat` la tabella è l'elemento con ruolo `table` ([Un file per partita](output-container.md)).

## Colonne {#columns}

Le colonne, sempre in questo ordine. Le colonne di testo sono stringhe a dizionario (`dictionary<int32, string>`) e non sono
mai nulle: "nessun valore" è una stringa vuota. Le colonne numeriche sono nulle dove una riga non ha un valore.

| Colonna | Tipo | Cosa |
|---|---|---|
| `match` | stringa | il nome della partita (`alpha-vs-bravo-m1`, o `...-b` per una seconda catena) |
| `map` | stringa | la mappa, dall'intestazione del demo (`de_x`) |
| `round` | int16 | il numero del round, a partire da 1 |
| `roundId` | stringa | `<partita> #NN`, il numero del round a due cifre (`alpha-vs-bravo-m1 #07`): unico tra le partite, la sessione del visualizzatore |
| `phase` | stringa | `freeze` nel freeze time del round (dalla fine del round precedente), `live` finché il round non è deciso, `after` mentre chi vince caccia e chi perde risparmia |
| `time` | float64 | secondi dall'inizio della partita (l'inizio live del suo primo file), su un solo orologio tra i suoi file |
| `roundTime` | float32 | secondi dalla fine del freeze time di questo round; negativo nel freeze time |
| `event` | stringa | che cos'è la riga - vedi [Eventi](#events) |
| `player` | stringa | il nome del giocatore (per ogni evento, quale giocatore è indicato sotto) |
| `steamid` | stringa | lo Steam ID del giocatore (64 bit, come testo) |
| `side` | stringa | `T` o `CT` in questo round; vuoto quando il giocatore non era su alcun lato |
| `team` | stringa | il nome della squadra del giocatore (o `Started T` / `Started CT`); per `explode`, la squadra che ha piazzato |
| `x`, `y`, `z` | float32 | posizione nelle coordinate proprie del gioco: pollici (unità di gioco), **Z verso l'alto**, sistema destrorso |
| `dirX`, `dirY`, `dirZ` | float32 | dove guarda il giocatore, un vettore unitario nello stesso sistema; solo posizioni |
| `health` | int16 | 0-100; posizioni, e su `hurt` ciò che è rimasto dopo il colpo |
| `armor` | int16 | 0-100; posizioni, e su `hurt` ciò che è rimasto dopo il colpo |
| `money` | int32 | il denaro del giocatore; solo posizioni |
| `equipment` | int32 | il valore di ciò che il giocatore porta; solo posizioni |
| `weapon` | stringa | l'arma come la chiama il gioco (`AK-47`, `M4A1-S`, `Knife` per ogni skin di coltello) |
| `place` | stringa | il nome del luogo della mappa nella posizione della riga (`BombsiteA`, `CTSpawn`); vuoto sulle esplosioni di granate: il demo non indica alcun luogo per dove è esplosa una granata |
| `throwerPlace` | stringa | il nome del luogo di chi ha lanciato la granata quando è esplosa; solo esplosioni di granate |
| `other` | stringa | l'altro giocatore di un'uccisione, una morte, un colpo o un flash |
| `damage` | float32 | salute persa; solo `hurt` |
| `duration` | float32 | secondi di accecamento; solo `blind` |
| `headshot` | int8 | 0/1; solo `kill` e `death` |
| `opening` | int8 | 0/1, la prima uccisione di un nemico nel round; solo `kill` e `death` |
| `traded` | int8 | 0/1. Per un `kill`: è stata un'uccisione di scambio. Per un `death`: è stata vendicata entro 5 s. Solo `kill` e `death`. |
| `noscope` | int8 | 0/1, l'uccisione è avvenuta con un'arma con mirino sparata senza mirare (il flag `noscope` dell'evento); solo `kill` e `death` |
| `attackerBlind` | int8 | 0/1, l'assassino era stato accecato quando ha ucciso (il flag `attackerblind` dell'evento); solo `kill` e `death` |
| `won` | int8 | 0/1, se il lato di questa riga ha vinto il round; nullo quando `side` è vuoto |
| `matchWon` | int8 | 0/1, se la squadra di questa riga ha vinto la partita; nullo quando `team` è vuoto o la registrazione non mostra la fine (vedi `winner` nel documento partita) |
| `roundEndReason` | stringa | come è finito il round della riga: `elimination`, `bomb` (la bomba è esplosa), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | stringa | il buy del lato di questa riga in questo round: `pistol`, `eco`, `force`, `full` |
| `detail` | stringa | ogni campo dell'evento che le altre colonne non portano, come oggetto JSON (i nomi propri del gioco): i proiettili di un colpo (`fire_bullets`: origine, angoli, inaccuratezza, dispersione, indice di rinculo, seme...), `dominated`, `revenge`, `attackerinair`, `wipe`... di una morte, `defindex` di un oggetto, un passo non ha nulla |
| `text` | stringa | una riga di chat; solo `chat` |
| `entity` | int32 | l'entità della granata: il volo di un `throw` (righe `grenade`), la sua esplosione e i giocatori che ha accecato ne condividono una |
| `hitgroup` | stringa | dove ha colpito il proiettile (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | armatura persa; solo `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | dove sul corpo ha colpito il proiettile, nel sistema della vittima in metri (x in avanti, y in alto dai piedi, z a destra): il raggio del colpo (`fire_bullets`, altrimenti mirino e vista dell'attaccante) tracciato su un corpo posato come stava la vittima, accovacciata o no, fino alla parte che `hitgroup` indica; solo `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | la direzione del colpo nello stesso sistema; `hitMiss` quanto (m) il raggio ha mancato la parte indicata (0: la attraversa); `hitFrom` `bullet` o `aim` |
| `penetrated` | int16 | muri attraversati dal proiettile mortale; `kill` e `death` |
| `throughSmoke` | int8 | 0/1, ucciso attraverso il fumo; `kill` e `death` |
| `distance` | float32 | la distanza dell'uccisione come la conta il gioco (metri); `kill` e `death` |
| `assister` | stringa | chi ha assistito; `kill` e `death` |
| `flash`, `flashAlpha` | float32 | secondi di flash rimasti, e quanto è bianco; posizioni |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; posizioni |
| `zoom`, `duck`, `moveType` | | il livello di zoom del mirino, quanto è accovacciato (0-1), il tipo di movimento del gioco; posizioni |
| `spottedBy` | stringa | gli Steam ID dei nemici che vedono questo giocatore, separati da `\|`; posizioni |
| `inventory` | stringa | tutto ciò che porta il giocatore, separato da `\|`; posizioni |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | il caricatore e la riserva dell'arma in mano; colpi nella raffica corrente; posizioni |
| `punchPitch`, `punchYaw` | float32 | lo scossone di mira del rinculo, in gradi; posizioni |
| `ping` | int16 | millisecondi; posizioni |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | i conteggi del tabellone del gioco per la partita fino a quel momento; posizioni |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | denaro speso in questo round e nella partita; valore dell'equipaggiamento all'inizio del round; posizioni |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, lo stato del giocatore al tempo della riga, eventi compresi: casco, kit di disinnesco, un'armatura qualunque, con mirino (dall'ultimo campione di posizione del giocatore fino alla riga), accecato (dentro un `blind` che lo ha colpito); ogni riga che nomina un giocatore |
| `state_utility` | int16 | granate portate al momento (da `inventory`); ogni riga che nomina un giocatore |
| `state_weapon` | stringa | l'arma in mano al momento (su una `death`, quella della vittima, dove `weapon` è quella dell'assassino); ogni riga che nomina un giocatore |
| `earn_round_cs2` | int16 | quanto ha reso il round: su `round_end` il premio di vittoria o il bonus di sconfitta (con il bonus del lato che ha piazzato), su `plant` e `defuse` i 300 del giocatore |

## Eventi {#events}

Quale giocatore nomina una riga, dove si trova, e quali colonne riempie.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won`, `roundEndReason` e `buy` sono riempite in ogni riga (`matchWon` dove è noto il vincitore della partita);
`inventory`, `money`, `equipment` e le colonne `state_*` in ogni riga che nomina un giocatore (gli eventi le prendono dall'ultimo
campione di posizione del giocatore).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Riempie anche |
|---|---|---|---|
| `position` | il giocatore | il giocatore (piedi) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (in mano), `place`, e l'intero stato del giocatore (le colonne da `flash` in poi) - anche nel freeze time |
| `kill` | l'assassino | dove si trovava l'assassino | `other` (vittima), `weapon`, `headshot`, `opening`, `traded` (un'uccisione di scambio), `noscope`, `attackerBlind`, `place` |
| `death` | la vittima | dove è caduta la vittima | `other` (assassino; vuoto per il mondo), `weapon`, `headshot`, `opening`, `traded` (vendicata), `noscope`, `attackerBlind`, `place` |
| `hurt` | la vittima | dove è stata colpita la vittima | `other` (attaccante), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - anche i colpi dei compagni e del mondo |
| `shot` | chi spara | da dove è stato sparato il colpo | `weapon`, `place`, `detail` (il resoconto del gioco sui proiettili) |
| `slash` | il giocatore | dove è stato fatto un fendente di coltello | `weapon` = `Knife` |
| `grenade` | chi ha lanciato | la granata in volo, al campionamento dei giocatori e dove si è fermata | `weapon` (la granata), `entity` |
| `throw` | chi ha lanciato | da dove è stata lanciata la granata | `weapon` (la granata), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | chi ha lanciato | dove è esplosa | `weapon`, `throwerPlace` (il luogo di chi ha lanciato in quel momento); `place` resta vuoto |
| `blind` | il giocatore accecato | dove si trovava | `other` (chi ha lanciato il flash), `duration`, `weapon` = `Flashbang`, `entity`, `place` - anche i compagni accecati |
| `plant` | il piazzatore | dove ha piazzato | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | chi disinnesca | dove ha disinnescato | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | ogni giocatore che ha giocato il round | dove il giocatore si trovava per ultimo | `won`, `earn_round_cs2` (quanto il round ha reso loro: l'aumento del denaro del lato fino al successivo freeze time dove le regole lo consentono, altrimenti quanto dicono le regole), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | il piazzatore (con il suo Steam ID), lato `T`, la squadra che ha piazzato | la posizione del piazzamento | `weapon` = `C4 Explosive`, `place` (quello del piazzatore al momento del piazzamento: dove giaceva la bomba); il suo tempo è quando la bomba è esplosa |
| `chat` | il mittente | dove si trovava | `text` |
| ogni altro evento di gioco che riguarda un giocatore, con il nome del gioco: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | il giocatore | dove si trovava (per gli eventi di una granata: dove era la granata) | `weapon` (di un oggetto), `entity`, `detail` (ogni campo dell'evento) |

Cosa c'è dentro e cosa no:

- Le righe **position** sono i giocatori vivi su un lato, fuori dal freeze time e dal riscaldamento, ogni `--every` tick
  (otto al secondo per impostazione predefinita).
- Le righe **kill** sono solo uccisioni da parte di un nemico - niente compagni uccisi, suicidi o morti causate dal mondo.
  Le righe **death** sono ogni morte, comprese quelle.
- Le righe **explode** sono ogni bomba piazzata che è esplosa, secondo `bomb_exploded` del demo: anche nella fase after, quando
  le T avevano già vinto per eliminazione. Un demo senza quell'evento ne riceve una per ogni round vinto dalla bomba, alla fine del
  round.
- Le righe **hurt** e **blind** sono solo tra nemici.
- **shot** esclude coltelli e C4; le granate sono righe **throw**.
- **molotov** copre molotov e incendiarie (l'innesco del fuoco).
- Il danno ai compagni, i flash ai compagni e agli spettatori, gli eventi nel freeze time e tutto ciò che sta tra i round non sono
  nella tabella.

Un esempio svolto, dal demo sintetico dei test (una granata fumogena lanciata, un'apertura con colpo alla testa, scambi):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

La morte di bob è vendicata dall'uccisione di ace da parte di ben 1,9 s dopo (la riga `death` di bob: traded 1; la riga `kill` di
ben: un'uccisione di scambio, traded 1); il secondo colpo a bob era di 137 danni su 40 di salute, quindi conta 40.

## Gli hint del footer `heat3d` {#the-heat3d-footer-hints}

Il footer Parquet del file (i metadati chiave/valore dello schema) porta le istruzioni di lettura sotto la chiave **`heat3d`**,
un oggetto JSON:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "matchWon", "roundEndReason", "buy", "opening", "team", ...]
  }
}
```

| Voce | Dice |
|---|---|
| `version`, `kind` | la versione degli hint (1) e che cosa li ha scritti (`cs2-demo`) |
| `axes.up` | la Z del file è verso l'alto |
| `axes.flipY` | cambia il segno della Y del file (vedi sotto) |
| `axes.scale` | 1: le posizioni si usano così come sono, in unità di gioco |
| `entity.size` | un giocatore è largo **32 unità** - la larghezza del giocatore di CS2 - la dimensione con cui un replay a scatola lo disegna |
| `columns.x` / `y` / `z` | le colonne di posizione |
| `columns.time`, `timeUnit` | `time`, in secondi |
| `columns.personId` | il giocatore è la persona |
| `columns.teamId` | il lato è il gruppo (quindi T e CT, non i nomi delle squadre, colorano i gruppi) |
| `columns.sessionId` | ogni round (`roundId`) è una sessione |
| `columns.lookMode` e `dirX`-`dirZ` | la direzione dello sguardo è un vettore in quelle colonne |
| `columns.extra` | le colonne da tenere come filtri, in ordine di utilità |

Un visualizzatore che conosce la chiave apre il file senza impostare nulla. Gli altri la ignorano. Per leggerla da sé:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Assi e misure {#axes-and-units}

Le coordinate sono quelle proprie del gioco: **pollici** (un'unità di gioco; un giocatore è alto 72 unità in piedi e largo 32),
**Z verso l'alto**, e sistema destrorso.

Un visualizzatore il cui mondo ha Y verso l'alto deve disegnare la (x, y, z) del gioco come **(x, z, -y)** - Z diventa l'altezza
e Y viene negata. È una rotazione, non uno specchio. Disegnata come un mondo con Z verso l'alto e sinistrorso, cioè (x, z, y), ogni
mappa esce specchiata, con il sito A dal lato sbagliato; `flipY: true` è ciò che gli hint dicono per evitarlo. L'[esportazione della mappa](map-export.md) scrive la sua geometria già nel sistema (x, z, -y), nelle stesse unità, quindi sta sotto la
tabella senza alcun aggiustamento.

Le distanze nel visualizzatore sono indicate in metri; con scala 1 sono unità di gioco. Moltiplica per 0,0254 per avere i metri.

## Dimensione {#size}

Dominano le posizioni: circa dieci giocatori x 8 campioni al secondo di gioco live con il valore predefinito `--every 8`, meno per i
giocatori morti e il freeze time. Dimezzare `--every` raddoppia le posizioni; gli eventi non cambiano.
