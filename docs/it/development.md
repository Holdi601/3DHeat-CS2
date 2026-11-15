---
title: "Sviluppo"
nav_order: 15
lang: "it"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Sviluppo {#development}

## Struttura {#layout}

| Percorso | Cosa |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: prima il controllo della versione, poi la riga di comando |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | i verbi e le opzioni; il raggruppamento dei file demo in partite; il pool di lavoro |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | un file demo attraverso demoparser2 in un `RawPart` - [Leggere un demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | parti, catene, cronometro, round, squadre, righe, uccisioni, danni, accecamenti - [Costruire una partita](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | riepiloghi dei round, il tabellone, il documento partita, il tabellone di testo - [Statistiche](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | la tabella Parquet con i suoi suggerimenti `heat3d`, e il JSON - [La tabella della mappa di calore](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | ricerca di CS2 e Source2Viewer, la mesh di collisione nel sistema del visualizzatore - [Esportazione della mappa](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | un lettore e scrittore minimale di glTF binario (nessuna dipendenza oltre numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | il controllo della versione e l'aggiornatore - [Aggiornamenti](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | i test e il demo sintetico |
| `VERSION` | la versione, su una riga |

Il flusso dei dati:

```text
file .dem --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per partita
          --match.build_match--> Match (round, giocatori, squadre, righe, uccisioni, danni, accecamenti)
          --output.write--> <mappa>/<partita>.parquet  (output.table + HINTS)
                            <mappa>/<partita>.match.json (stats.summary)
<mappa>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Uso da Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # la tabella della mappa di calore come DataFrame di pandas
    kills = match.kills        # una riga per morte, con ogni flag
    doc = summary(match)       # il documento .match.json come dizionario
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` e `Match.blinds` sono DataFrame di pandas con più di quanto contengano gli output -
posizioni e luoghi di attaccante e vittima per uccisione, `utility` per ogni colpo - per analisi proprie.

## Test {#tests}

```bash
python -m pytest
```

`pytest.ini` esegue `tests/` in modo silenzioso. I test non richiedono né un demo, né il gioco, né Source2Viewer:
[`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) costruisce a mano un demo,
come lo darebbe demoparser2 - due round, due giocatori per lato (`ace`, `ash` della squadra Alpha; `bob`, `ben` di
Bravo), abbastanza piccolo da conoscere ogni risposta:

- Round 1, vittoria della T per eliminazione: ace uccide bob con un colpo alla testa (l'apertura), ben uccide ace 1,9 s
  dopo (uno scambio: la morte di bob è vendicata), ash uccide ben 3,1 s dopo - da solo contro uno, un clutch vinto.
- Round 2, vittoria della T per la bomba: ash piazza su A, nessuno muore, la bomba esplode.

`fixtures.halves` costruisce una partita più lunga di round vuoti, con le squadre sui loro primi lati o scambiate, con il
conteggio di overtime del gioco o senza, per la durata della metà e i round pistola.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) verifica su di esso:
vincitore, motivo, punteggio e lati di ogni round; il cronometro che parte dalla partita; economia e piazzamento (il suo
tempo nel round, il suo luogo, l'esplosione della bomba); il sito di un piazzamento sempre una lettera o vuoto, mai un
numero di entità; un pareggio deciso senza vincitore; i round pistola dal punto in cui i lati si scambiano, l'overtime
escluso, e solo il round 1 senza scambio; squadre senza nomi di clan (`Started T` / `Started CT`); aperture, scambi e
flag; un suicidio che non è un compagno ucciso, e l'apertura passata al primo nemico ucciso; `noscope` e `attackerBlind`
nella tabella e nel documento partita; i danni come salute persa (60, poi 40 di un colpo da 137 su 40 di salute); i numeri
del tabellone e KAST; i clutch; il tabellone di testo; gli eventi della tabella e dove si trovano (un'esplosione senza un
luogo proprio, quello di chi ha lanciato in `throwerPlace`; l'esplosione attribuita alla squadra che ha piazzato); che le
posizioni siano live, etichettate e con vettori di sguardo unitari; che il file scritto porti i suoi suggerimenti; che le
parti siano messe in ordine qualunque siano i loro nomi; un orologio del server riavviato che prosegue comunque; e le righe
duplicate di un round ripristinato risolte in quella che prosegue.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) verifica che i demo nelle
cartelle vengano trovati qualunque sia il maiuscolo o minuscolo di `.dem`, e che una partita conti come scritta solo con
sia la sua tabella sia il suo documento partita.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) verifica le
conversioni di sistema (i metri di Source2Viewer in pollici del gioco, e poi nel sistema del visualizzatore, una rotazione
con determinante 1), che clip e cielo vengano esclusi qualunque sia il maiuscolo o minuscolo e i nomi delle superfici, la
divisione terreno/struttura per normale, e un `.glb` scritto e riletto.

### Il controllo del pavimento su una mappa reale {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<un demo> HEAT3D_SOURCE2VIEWER=<la CLI> python -m pytest
```

Con entrambe le variabili impostate viene eseguito anche `test_players_stand_on_the_exported_floor`: converte il demo,
esporta la mappa dal gioco installato, e verifica che almeno il 98% di 300 campioni casuali di posizione abbia terreno
sotto di sé, con un'altezza mediana sopra di esso inferiore a 5 unità ([Esportazione della mappa](map-export.md#the-check-that-the-frame-is-right)).

## Convenzioni del codice {#conventions-of-the-code}

- I tempi dentro `match.py` sono secondi di partita, tranne il `time` di un piazzamento, secondi dentro il suo round come
  lo scrive il documento partita; i tick diventano secondi solo tramite `_Part.at`.
- I lati sono stringhe `T` / `CT` ovunque fuori dai dati grezzi del parser (`team_num` 2 / 3).
- Una nuova colonna della tabella va in `ROW_COLUMNS` (e in `NUMERIC` se è numerica) in `match.py`; `output.table` sceglie
  il suo tipo Parquet dagli insiemi `INT16`, `INT32`, `FLOAT64` e i flag 0/1, altrimenti float32.
- Cambiare ciò che il visualizzatore deve fare con una colonna significa cambiare `HINTS` in `output.py`.

## Licenza {#licence}

MIT. Pacchetti di terze parti e ciò che i giochi richiedono:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
I demo e le mappe non fanno mai parte del repository; il suo `.gitignore` tiene fuori per tipo `*.dem`, `*.parquet`,
`*.match.json`, `*.glb` e simili.
