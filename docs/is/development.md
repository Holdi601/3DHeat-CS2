---
title: "Þróun"
nav_order: 15
lang: "is"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Þróun {#development}

## Uppbygging {#layout}

| Slóð | Hvað |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: útgáfuathugunin, svo skipanalínan |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | skipanirnar og valkostirnir; að hópa demo-skrár í leiki; vinnuferlasafnið |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | ein demo-skrá gegnum demoparser2 í `RawPart` - [Að lesa demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | hlutar, keðjur, klukkan, lotur, lið, raðir, fellingar, skaði, blindur - [Að smíða leik](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | lotuyfirlit, stigataflan, leikjaskjalið, textastigataflan - [Tölfræði](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet-taflan með `heat3d`-ábendingum sínum, og JSON - [Hitakortstaflan](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | að finna CS2 og Source2Viewer, árekstrarnetið í hnitakerfi skoðarans - [Kortaútflutningur](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | lágmarks glTF binary lesari og ritari (engin ósk önnur en numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | útgáfuathugunin og uppfærslan - [Uppfærslur](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | prófanirnar og gervi-demo-skráin |
| `VERSION` | útgáfan, ein lína |

Gagnaflæðið:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Notkun úr Python {#using-it-from-python}

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

`Match.kills`, `Match.damage` og `Match.blinds` eru pandas DataFrames með
meira en úttakið ber - staðsetningar og staði árásarmanns og fórnarlambs
fyrir hverja fellingu, `utility` fyrir hvert högg - fyrir þínar eigin greiningar.

## Prófanir {#tests}

```bash
python -m pytest
```

`pytest.ini` keyrir `tests/` hljóðlega. Prófanirnar þurfa enga demo-skrá, engan leik og engan
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
smíðar demo-skrá í höndunum, eins og demoparser2 myndi skila henni - tvær lotur, tveir
leikmenn á hlið (`ace`, `ash` í liði Alpha; `bob`, `ben` í Bravo), nógu
lítið til að hvert svar sé þekkt:

- Lota 1, T vinna með útrýmingu: ace fellir bob með hausskoti (opnunin),
  ben fellir ace 1,9 s síðar (trade: dauði bobs er hefndur), ash
  fellir ben 3,1 s eftir það - einn gegn einum, clutch unnið.
- Lota 2, T vinna með sprengjunni: ash setur sprengju á A, enginn deyr, sprengjan
  springur.

`fixtures.halves` smíðar lengri leik af tómum lotum, liðin á
fyrstu hliðum sínum eða víxluð, með framlengingartalningu leiksins eða án hennar, fyrir
lengd hálfleiks og skammbyssulotur.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
athugar á því: sigurvegara, ástæðu, stöðu og hliðar hverrar lotu; klukkuna
sem byrjar við leikinn; hagkerfi og sprengjusetninguna (tíma hennar inn í lotuna,
stað hennar, sprengjuna springa); að site sprengjusetningar sé alltaf bókstafur eða tómt, aldrei
einingarnúmer; jafntefli ákveðið án sigurvegara; skammbyssulotur frá
því þar sem hliðar skipta, framlenging sleppt, og aðeins lota 1 án skipta;
lið án klanheita (`Started T` / `Started CT`); opnanir, trades og
fána; sjálfsvíg sem er ekki teamkill, og opnunina flutta á fyrstu
fellingu á andstæðingi; `noscope` og `attackerBlind` í töflunni og leikjaskjalinu;
skaða sem tapað líf (60, síðan 40 af 137 á 40 lífi); tölur
stigatöflunnar og KAST; clutch; textastigatöfluna; atburði töflunnar og
hvar þeir eru (sprenging án eigin staðar, stað kastarans í
`throwerPlace`; sprengingin liðs sem setti sprengjuna); að staðsetningar séu lifandi,
merktar og hafi einingarsjónvigra; að skrifaða skráin beri
ábendingar sínar; hluta raðaða hvað sem þeir heita; endurræsta klukku þjóns
sem heldur samt áfram; og tvöfaldar raðir endurheimtar lotu leystar í
þá sem leiðir áfram.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
athugar að demo-skrár í möppum finnist hver sem stafagerð `.dem` er, og að
leikur teljist skrifaður aðeins með bæði töflu sína og leikjaskjal.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
athugar hnitaumbreytingarnar (metrar Source2Viewer í tommur leiksins,
og áfram í hnitakerfi skoðarans, snúningur með ákveði 1), að clip og
himinn séu sleppt hver sem stafagerðin er og yfirborðsheitin, skiptingu jarðar/mannvirkis eftir normal,
og `.glb` skrifaða og lesna aftur.

### Gólfathugunin á raunverulegu korti {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Með báðar breyturnar stilltar keyrir `test_players_stand_on_the_exported_floor` líka:
hún umbreytir demo-skránni, flytur út kort hennar úr uppsetta leiknum, og
athugar að að minnsta kosti 98 % af 300 tilviljanakenndum staðarsýnum hafi jörð undir
sér, með miðgildi hæðar fyrir ofan hana undir 5 einingum
([Kortaútflutningur](map-export.md#the-check-that-the-frame-is-right)).

## Venjur kóðans {#conventions-of-the-code}

- Tímar inni í `match.py` eru leiksekúndur, nema `time` sprengjusetningar,
  sekúndur inn í lotu hennar eins og leikjaskjalið skrifar það; tikk verða aðeins að sekúndum
  gegnum `_Part.at`.
- Hliðar eru `T` / `CT` strengir alls staðar utan hrárra gagna þáttarans
  (`team_num` 2 / 3).
- Nýr töfludálkur fer í `ROW_COLUMNS` (og `NUMERIC` ef hann er töluleg) í
  `match.py`; `output.table` velur Parquet-tegund hans úr mengjunum `INT16`,
  `INT32`, `FLOAT64` og 0/1-fánunum, annars float32.
- Að breyta því sem skoðarinn á að gera við dálk þýðir að breyta `HINTS` í
  `output.py`.

## Leyfi {#licence}

MIT. Pakkar frá þriðja aðila:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demo-skrár og kort eru aldrei hluti af hugbúnaðarsafninu; `.gitignore` þess heldur
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` og þess háttar úti eftir gerð.
