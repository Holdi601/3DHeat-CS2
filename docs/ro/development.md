---
title: Dezvoltare
nav_order: 15
lang: "ro"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Dezvoltare {#development}

## Structura {#layout}

| Cale | Ce este |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: verificarea versiunii, apoi linia de comandă |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | verbele și opțiunile; gruparea fișierelor demo în meciuri; pool-ul de lucrători |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | un fișier demo prin demoparser2 într-un `RawPart` - [Citirea unui demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | părțile, lanțurile, ceasul, rundele, echipele, rândurile, eliminările, daunele, orbirile - [Cum se construiește un meci](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | rezumatele rundelor, tabelul de scor, documentul de meci, tabelul de scor text - [Statistici](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | tabelul Parquet cu sugestiile sale `heat3d`, și JSON-ul - [Tabelul hărții termice](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | găsirea CS2 și a Source2Viewer, plasa de coliziune în sistemul vizualizatorului - [Exportul hărții](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | un cititor și scriitor minimal de glTF binar (fără altă dependență decât numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | verificarea versiunii și actualizatorul - [Actualizări](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testele și demo-ul sintetic |
| `VERSION` | versiunea, o singură linie |

Fluxul datelor:

```text
fișiere .dem --demo.read_part--> RawPart --match.chains--> [RawPart, ...] pe meci
          --match.build_match--> Match (runde, jucători, echipe, rânduri, eliminări, daune, orbiri)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --CLI Source2Viewer--> .glb cu physics world --mapexport.parts_from--> glb.write
```

### Utilizarea din Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # tabelul hărții termice ca DataFrame pandas
    kills = match.kills        # un rând pentru fiecare moarte, cu fiecare indicator
    doc = summary(match)       # documentul .match.json ca dicționar
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` și `Match.blinds` sunt DataFrame-uri pandas cu mai mult decât
conțin rezultatele - poziția și locul atacatorului și ale victimei pentru fiecare
eliminare, `utility` pentru fiecare lovitură - pentru analize proprii.

## Teste {#tests}

```bash
python -m pytest
```

`pytest.ini` rulează `tests/` discret. Testele nu au nevoie de niciun demo, de joc sau de
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
construiește manual un demo, așa cum l-ar da demoparser2 - două runde, doi jucători pe
parte (`ace`, `ash` din echipa Alpha; `bob`, `ben` din Bravo), suficient de mic încât
fiecare răspuns să fie cunoscut:

- Runda 1, o victorie T prin eliminare: ace îl elimină pe bob cu o lovitură în cap
  (deschiderea), ben îl elimină pe ace la 1,9 s după aceea (o răzbunare: moartea lui bob
  este răzbunată), ash îl elimină pe ben la 3,1 s după aceea - singur împotriva unuia, un
  clutch câștigat.
- Runda 2, o victorie T prin bombă: ash plantează pe A, nimeni nu moare, bomba explodează.

`fixtures.halves` construiește un meci mai lung, de runde goale, cu echipele pe prima lor
parte sau schimbate, cu numărul de prelungiri al jocului sau fără, pentru lungimea reprizei
și rundele de pistol.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
verifică pe el: câștigătorul, motivul, scorul și părțile fiecărei runde; ceasul care
pornește de la meci; economia și plantarea (timpul său în rundă, locul său, explozia
bombei); o literă sau nimic pentru site-ul unei plantări, niciodată un număr de entitate;
o egalitate decisă fără câștigător; rundele de pistol de la schimbarea părților,
prelungirile lăsate deoparte, și doar runda 1 fără schimbare; echipe fără nume de clan
(`Started T` / `Started CT`); deschideri, răzbunări și indicatori; o sinucidere care nu
este teamkill, și deschiderea trecută la prima eliminare de inamic; `noscope` și
`attackerBlind` în tabel și în documentul meciului; daunele ca sănătate pierdută (60, apoi
40 dintr-un 137 pe 40 de sănătate); cifrele tabelului de scor și KAST; clutch-urile;
tabelul de scor text; evenimentele tabelului și locurile lor (o detonare fără loc propriu,
al aruncătorului în `throwerPlace`; explozia în echipa care a plantat); că pozițiile sunt
live, etichetate și au vectori de privire unitari; că fișierul scris poartă sugestiile sale;
că părțile sunt puse în ordine oricare ar fi numele lor; un ceas de server repornit care
totuși continuă; și rândurile duplicate ale unei runde restaurate rezolvate către cel care
duce mai departe.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
verifică că demo-urile din foldere sunt găsite oricare ar fi scrierea `.dem`, și că un meci
contează ca scris doar cu tabelul și documentul său de meci.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
verifică conversiile de sistem de coordonate (metrii Source2Viewer în inchi ai jocului, și
apoi în sistemul vizualizatorului, o rotație cu determinantul 1), că clipurile și cerul sunt
lăsate deoparte oricare ar fi majusculele și suprafețele numite, împărțirea pe sol/structură
după normală, și un `.glb` scris și citit înapoi.

### Verificarea podelei pe o hartă reală {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<un demo> HEAT3D_SOURCE2VIEWER=<CLI-ul> python -m pytest
```

Cu ambele variabile setate, rulează și `test_players_stand_on_the_exported_floor`: convertește
demo-ul, exportă harta din jocul instalat și verifică faptul că cel puțin 98 % din 300 de
eșantioane aleatoare de poziție au sol dedesubt, cu o înălțime mediană deasupra lui sub
5 unități ([Exportul hărții](map-export.md#the-check-that-the-frame-is-right)).

## Convenții ale codului {#conventions-of-the-code}

- Timpii din `match.py` sunt secunde de meci, cu excepția `time` al unei plantări, secunde
  în interiorul rundei așa cum le scrie documentul meciului; tick-urile devin secunde doar
  prin `_Part.at`.
- Părțile sunt șiruri `T` / `CT` peste tot în afara datelor brute ale parserului
  (`team_num` 2 / 3).
- O coloană nouă de tabel intră în `ROW_COLUMNS` (și în `NUMERIC` dacă este numerică) din
  `match.py`; `output.table` alege tipul său Parquet din seturile `INT16`, `INT32`,
  `FLOAT64` și indicatorii 0/1, float32 în rest.
- Schimbarea a ceea ce ar trebui să facă vizualizatorul cu o coloană înseamnă schimbarea
  `HINTS` din `output.py`.

## Licență {#licence}

MIT. Pachetele terțe: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demo-urile și hărțile nu fac niciodată parte din depozit; `.gitignore` ține afară
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` și asemenea după tip.
