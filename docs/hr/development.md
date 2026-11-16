---
title: "Razvoj"
nav_order: 15
lang: "hr"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

## Raspored {#layout}

| Putanja | Što je |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: provjera izdanja, pa naredbeni redak |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | naredbe i opcije; grupiranje demo datoteka u mečeve; skup radnika |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | jedna demo datoteka kroz demoparser2 u `RawPart` - [Čitanje demo snimke](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | dijelovi, lanci, sat, runde, timovi, redci, ubojstva, šteta, slijepila - [Sastavljanje meča](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | sažeci rundi, rezultatna tablica, dokument meča, tekstualna rezultatna tablica - [Statistika](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet tablica s `heat3d` savjetima, i JSON - [Toplinska tablica](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | pronalaženje CS2 i Source2Viewera, kolizijska mreža u okviru pregledniku - [Izvoz karte](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | minimalni čitač i pisac glTF binarnog formata (bez ovisnosti osim numpyja) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | provjera izdanja i ažuriranje - [Ažuriranja](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testovi i sintetička demo snimka |
| `VERSION` | verzija, jedan redak |

Tok podataka:

```text
.dem datoteke --demo.read_part--> RawPart --match.chains--> [RawPart, ...] po mečevima
          --match.build_match--> Match (runde, igrači, timovi, redci, ubojstva, šteta, slijepila)
          --output.write--> <karta>/<meč>.parquet  (output.table + HINTS)
                            <karta>/<meč>.match.json (stats.summary)
<karta>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Korištenje iz Pythona {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # toplinska tablica kao pandas DataFrame
    kills = match.kills        # jedan redak po smrti, sa svim zastavicama
    doc = summary(match)       # dokument .match.json kao rječnik
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` i `Match.blinds` su pandas DataFrame-ovi s više podataka nego što izlazi nose - položaji i mjesta napadača i žrtve po ubojstvu, `utility` po pogotku - za vaše vlastite analize.

## Testovi {#tests}

```bash
python -m pytest
```

`pytest.ini` pokreće `tests/` tiho. Testovima ne treba nijedna demo snimka, igra ni Source2Viewer:
[`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
ručno gradi demo snimku, kako bi je dao demoparser2 - dvije runde, po dva igrača sa svake strane (`ace`, `ash` iz tima Alpha; `bob`, `ben` iz Bravo), dovoljno malu da je svaki odgovor poznat:

- Runda 1, pobjeda T eliminacijom: ace ubije bob-a pogotkom u glavu (prvo ubojstvo), ben ubije ace-a 1,9 s kasnije (razmjena: bob-ova smrt je razmijenjena), ash ubije ben-a 3,1 s nakon toga - sam protiv jednog, osvojen clutch.
- Runda 2, pobjeda T bombom: ash postavlja bombu na A, nitko ne umire, bomba eksplodira.

`fixtures.halves` gradi dulji meč od praznih rundi, timovi na prvim stranama ili zamijenjeni, s brojem produžetka igre ili bez njega, za duljinu poluvremena i runde s pištoljima.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
provjerava na njoj: pobjednika, razlog, rezultat i strane svake runde; sat koji počinje s mečem; ekonomiju i postavljanje (vrijeme u rundi, mjesto, eksploziju bombe); da je mjesto postavljanja uvijek slovo ili prazno, nikad broj entiteta; neriješenu rundu bez pobjednika; runde s pištoljima od mjesta gdje se strane zamijene, bez produženja, i samo runda 1 bez zamjene; timove bez naziva klubova (`Started T` / `Started CT`); prva ubojstva, razmjene i zastavice; samoubojstvo koje nije teamkill, i prvo ubojstvo prebačeno na prvo ubojstvo neprijatelja; `noscope` i `attackerBlind` u tablici i dokumentu meča; štetu kao izgubljeno zdravlje (60, pa 40 od 137 na 40 zdravlja); brojeve tablice rezultata i KAST; clutcheve; tekstualnu rezultatnu tablicu; događaje tablice i gdje su (detonacija bez vlastitog mjesta, mjesto bacača u `throwerPlace`; eksplozija je tima koji je postavio); da su pozicije žive, označene i da imaju jedinične vektore pogleda; da zapisana datoteka nosi svoje savjete; dijelove poredane bez obzira na imena; ponovno pokrenuti sat poslužitelja koji i dalje slijedi; te dupli redci vraćene runde riješeni u onaj koji vodi dalje.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
provjerava da se demo snimke u mapama pronalaze bez obzira na veličinu slova u `.dem`, i da se meč smatra zapisanim samo s obje svoje datoteke, tablicom i dokumentom meča.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
provjerava pretvorbe okvira (metri Source2Vieweru u igrine inče, a dalje u okvir preglednika, rotacija s determinantom 1), da su clip i sky elementi izostavljeni bez obzira na veličinu slova i imena ploha, podjelu na tlo i strukturu po normali i da se `.glb` zapiše i ponovno pročita.

### Provjera poda na stvarnoj karti {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<demo snimka> HEAT3D_SOURCE2VIEWER=<CLI> python -m pytest
```

Kad su obje varijable postavljene, pokreće se i `test_players_stand_on_the_exported_floor`: pretvara demo snimku, izvozi njezinu kartu iz instalirane igre i provjerava da je pod pod najmanje 98 % od 300 nasumičnih uzoraka pozicija, a srednja visina iznad poda manja od 5 jedinica ([Izvoz karte](map-export.md#the-check-that-the-frame-is-right)).

## Konvencije koda {#conventions-of-the-code}

- Vremena unutar `match.py` su sekunde meča, osim `time` postavljanja, sekunde u rundi kako ih piše dokument meča; tikovi postaju sekunde tek kroz `_Part.at`.
- Strane su nizovi `T` / `CT` svuda izvan sirovih podataka parsera (`team_num` 2 / 3).
- Novi stupac tablice ide u `ROW_COLUMNS` (i u `NUMERIC` ako je numerički) u `match.py`; `output.table` bira svoj Parquet tip iz skupova `INT16`, `INT32`, `FLOAT64` i zastavica 0/1, inače float32.
- Promjena onoga što preglednik treba raditi sa stupcem znači promjenu `HINTS` u `output.py`.

## Licenca {#licence}

MIT. Paketi trećih strana: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demo snimke i karte nikad nisu dio repozitorija; njegov `.gitignore` po vrsti drži `*.dem`, `*.parquet`, `*.match.json`, `*.glb` i slične datoteke van.
