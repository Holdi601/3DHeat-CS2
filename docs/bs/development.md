---
title: Razvoj
nav_order: 15
lang: "bs"
source: development.md
source_hash: "bcc524eebb27"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

## Raspored {#layout}

| Putanja | Šta |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: provjera izdanja, zatim komandna linija |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | glagoli i opcije; grupisanje demo datoteka u mečeve; skup radnika |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | jedna demo datoteka kroz demoparser2 u `RawPart` - [Čitanje demoa](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | dijelovi, lanci, sat, runde, timovi, redovi, ubistva, šteta, zasljepljenja - [Slaganje meča](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | sažeci rundi, tabela rezultata, dokument meča, tekstualna tabela rezultata - [Statistike](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet tabela sa svojim `heat3d` napomenama, i JSON - [Tabela toplotne mape](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | pronalaženje CS2 i Source2Viewer, mreža kolizije u koordinatni sistem preglednika - [Izvoz mape](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | minimalni čitač i pisač glTF binarnog formata (bez zavisnosti osim numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | provjera izdanja i ažurirač - [Ažuriranja](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testovi i sintetički demo |
| `VERSION` | verzija, jedan red |

Tok podataka:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
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
    rows = match.rows          # the heatmap table as a pandas DataFrame
    kills = match.kills        # one row per death, with every flag
    doc = summary(match)       # the .match.json document as a dict
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` i `Match.blinds` su pandas DataFrame-ovi s
više nego što izlazi nose - pozicije i mjesta napadača i žrtve po
ubistvu, `utility` po pogotku - za vaše vlastite analize.

## Testovi {#tests}

```bash
python -m pytest
```

`pytest.ini` pokreće `tests/` tiho. Testovi ne trebaju ni demo, ni igru, ni
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
ručno gradi demo, onako kako bi ga dao demoparser2 - dvije runde, dva
igrača po strani (`ace`, `ash` tima Alpha; `bob`, `ben` tima Bravo), dovoljno
mali da je svaki odgovor poznat:

- Runda 1, T pobjeda eliminacijom: ace ubija boba headshotom (opening),
  ben ubija acea 1,9 s kasnije (trade: bobova smrt je traded), ash
  ubija bena 3,1 s poslije toga - sam protiv jednog, dobijen clutch.
- Runda 2, T pobjeda bombom: ash postavlja na A, niko ne pogine, bomba
  eksplodira.

`fixtures.halves` gradi duži meč praznih rundi, timovi na svojim
prvim stranama ili zamijenjeni, s igrinim brojačem produžetka ili bez njega, za
dužinu poluvremena i pištolj runde.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
na tome provjerava: pobjednika, razlog, rezultat i strane svake runde; sat koji
počinje s mečom; ekonomiju i postavljanje bombe (njegovo vrijeme u rundi, njegovo
mjesto, eksploziju bombe); da je site postavljanja uvijek slovo ili prazno, nikad
broj entiteta; neriješeno odlučeno bez pobjednika; pištolj runde od
mjesta gdje se strane zamijene, produžetak izostavljen, i samo rundu 1 bez zamjene;
timove bez naziva klanova (`Started T` / `Started CT`); openinge, trade-ove i
zastavice; samoubistvo koje nije teamkill, i opening prenesen na prvo
ubistvo neprijatelja; `noscope` i `attackerBlind` u tabeli i dokumentu meča;
štetu kao izgubljeno zdravlje (60, zatim 40 od 137 na 40 zdravlja); brojeve
tabele rezultata i KAST; clutcheve; tekstualnu tabelu rezultata; događaje tabele i
gdje su (detonacija bez vlastitog mjesta, bacačevo mjesto u
`throwerPlace`; eksplozija tima koji postavlja); da su pozicije žive,
označene i imaju jedinične vektore pogleda; da napisana datoteka nosi svoje
napomene; dijelove poredane bez obzira na njihova imena; restartovan serverov
sat koji ipak slijedi dalje; i duplirane redove vraćene runde riješene u onaj
koji vodi dalje.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
provjerava da se demoi u folderima nalaze bez obzira na veličinu slova `.dem`, i da
se meč računa kao napisan samo s tabelom i dokumentom meča.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
provjerava pretvorbe koordinatnih sistema (Source2Viewerovi metri u igrine inče,
i dalje u koordinatni sistem preglednika, rotacija s determinantom 1), da su clipovi i
nebo izostavljeni bez obzira na veličinu slova i imenovane površine, podjelu na tlo/strukturu po normali,
i `.glb` napisan i pročitan natrag.

### Provjera poda na stvarnoj mapi {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Kad su obje varijable postavljene, pokreće se i
`test_players_stand_on_the_exported_floor`: pretvara demo, izvozi njegovu mapu iz instalirane igre, i
provjerava da barem 98 % od 300 nasumičnih uzoraka pozicije ima tlo ispod sebe,
a da je medijan visine iznad njega ispod 5 jedinica
([Izvoz mape](map-export.md#the-check-that-the-frame-is-right)).

## Konvencije koda {#conventions-of-the-code}

- Vremena unutar `match.py` su sekunde meča, osim `time` postavljanja bombe,
  sekundi u rundi kako ih piše dokument meča; tikovi postaju sekunde samo
  kroz `_Part.at`.
- Strane su stringovi `T` / `CT` svugdje izvan sirovih podataka parsera
  (`team_num` 2 / 3).
- Nova kolona tabele ide u `ROW_COLUMNS` (i `NUMERIC` ako je numerička) u
  `match.py`; `output.table` bira svoj Parquet tip iz skupova `INT16`,
  `INT32`, `FLOAT64` i 0/1 zastavica, inače float32.
- Promjena onoga što preglednik treba raditi s kolonom znači promjenu `HINTS` u
  `output.py`.

## Licenca {#licence}

MIT. Paketi trećih strana i ono na šta igre obavezuju:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demoi i mape nikad nisu dio repozitorija; njegov `.gitignore` drži
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` i slično vani po tipu.
