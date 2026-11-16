---
title: "Razvoj"
nav_order: 15
lang: "sl"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

## Postavitev {#layout}

| Pot | Kaj |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: najprej preverjanje izdaje, nato ukazna vrstica |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | ukazi in možnosti; združevanje datotek demo v tekme; bazen delavcev |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | ena datoteka demo skozi demoparser2 v `RawPart` – [Branje dema](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | deli, verige, ura, runde, ekipe, vrstice, uboji, škoda, oslepitve – [Gradnja tekme](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | povzetki rund, lestvica, dokument tekme, besedilna lestvica – [Statistika](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | tabela Parquet z njenimi namigi `heat3d` in JSON – [Toplotna tabela](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | iskanje CS2 in Source2Viewer, mreža trkov v okvirju pregledovalnika – [Izvoz karte](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | najpreprostejši bralnik in pisalnik binarnega glTF (brez odvisnosti razen numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | preverjanje izdaje in posodabljanje – [Posodobitve](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testi in sintetični demo |
| `VERSION` | različica, ena vrstica |

Tok podatkov:

```text
.dem datoteke --demo.read_part--> RawPart --match.chains--> [RawPart, ...] na tekmo
          --match.build_match--> Match (runde, igralci, ekipe, vrstice, uboji, škoda, oslepitve)
          --output.write--> <karta>/<tekma>.parquet  (output.table + HINTS)
                            <karta>/<tekma>.match.json (stats.summary)
<karta>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Uporaba iz Pythona {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # toplotna tabela kot pandas DataFrame
    kills = match.kills        # en vrstica na smrt, z vsemi zastavicami
    doc = summary(match)       # dokument .match.json kot slovar
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` in `Match.blinds` so pandas DataFrame z več podatki, kot jih nosijo izhodi – položaji
napadalca in žrtve ter kraji za vsak uboj, škoda za vsak zadetek po `utility` – za lastne analize.

## Testi {#tests}

```bash
python -m pytest
```

`pytest.ini` zažene `tests/` tiho. Testi ne potrebujejo demo, igre ali Source2Viewer:
[`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py) zgradi demo ročno, kot bi ga
dal demoparser2 – dve rundi, dva igralca na stran (`ace`, `ash` iz ekipe Alpha; `bob`, `ben` iz Bravo), dovolj majhen,
da je vsak odgovor znan:

- Runda 1, zmaga T z izločitvijo: ace ubije bob z zadetkom v glavo (prvi uboj), ben ubije ace 1,9 s pozneje (maščevalni
  uboj: smrt bob je maščevana), ash ubije bena 3,1 s po tem – sam proti enemu, osvojen clutch.
- Runda 2, zmaga T z bombo: ash postavi bombo na A, nihče ne umre, bomba eksplodira.

`fixtures.halves` zgradi daljšo tekmo praznih rund, ekipe na začetnih straneh ali zamenjane, s številom podaljškov igre
ali brez njega, za dolžino polčasa in pištolske runde.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py) preveri na njem: zmagovalca,
vzrok, rezultat in strani vsake runde; uro, ki se začne s tekmo; ekonomijo in postavitev (njen čas v rundi, njen kraj,
eksplozijo bombe); da je postavitvena stran vedno črka ali prazna, nikoli številka entitete; remi, odločen brez
zmagovalca; pištolske runde od mesta zamenjave strani, podaljški izvzeti, in samo runda 1 brez zamenjave; ekipe brez
klanskih imen (`Started T` / `Started CT`); prve uboje, maščevanja in zastavice; samomor, ki ni prijateljski uboj, in
prvi uboj, prenesen na prvi sovražnikov uboj; `noscope` in `attackerBlind` v tabeli in dokumentu tekme; škodo kot
izgubljeno zdravje (60, nato 40 od zadetka 137 na 40 zdravja); številke lestvice in KAST; clutche; besedilno lestvico;
dogodke tabele in kje so (detonacija brez svojega kraja, metalčev kraj v `throwerPlace`; eksplozija je
postavljajoče ekipe); da so položaji živi, označeni in imajo enotske vektorje pogleda; da zapisana datoteka nosi svoje
namige; da so deli urejeni ne glede na imena; ponovno zagnan strežnikov čas, ki še vedno sledi; in da se podvojene
vrstice obnovljene runde razrešijo v tisto, ki vodi naprej.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) preveri, da se demoji v mapah
najdejo, ne glede na velikost črk v `.dem`, in da se tekma šteje kot zapisana šele z obema, tabelo in dokumentom tekme.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py) preveri pretvorbe
okvirja (Source2Viewerjevi metri v igrine palce in naprej v okvir pregledovalnika, rotacijo z determinanto 1), da so
clipi in nebo izpuščeni ne glede na velikost črk in imena površin, delitev na tla/konstrukcijo po normali, in da se
`.glb` zapiše in znova prebere.

### Preverjanje tal na pravi karti {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<demo> HEAT3D_SOURCE2VIEWER=<CLI> python -m pytest
```

Ko sta obe spremenljivki nastavljeni, teče tudi `test_players_stand_on_the_exported_floor`: pretvori demo, izvozi
karto iz nameščene igre in preveri, da ima vsaj 98 % od 300 naključnih vzorcev položaja pod seboj tla, z mediano
višino nad njimi pod 5 enotami ([Izvoz karte](map-export.md#the-check-that-the-frame-is-right)).

## Konvencije kode {#conventions-of-the-code}

- Časi znotraj `match.py` so sekunde tekme, razen `time` postavitve, sekunde v rundi, kakor ga piše dokument tekme;
  takti postanejo sekunde samo prek `_Part.at`.
- Strani so nizi `T` / `CT` povsod zunaj surovih podatkov razčlenjevalnika (`team_num` 2 / 3).
- Nov stolpec tabele gre v `ROW_COLUMNS` (in `NUMERIC`, če je številski) v `match.py`; `output.table` izbere njegov tip
  Parquet iz množic `INT16`, `INT32`, `FLOAT64` in zastavic 0/1; sicer float32.
- Če naj pregledovalnik s stolpcem nekaj drugega počne, je treba spremeniti `HINTS` v `output.py`.

## Licenca {#licence}

MIT. Paketi tretjih oseb:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demoji in karte nikoli niso del repozitorija; njegov `.gitignore` z vrsto izključi `*.dem`, `*.parquet`,
`*.match.json`, `*.glb` in podobne datoteke.
