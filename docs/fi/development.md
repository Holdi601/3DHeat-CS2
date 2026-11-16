---
title: "Kehitys"
nav_order: 15
lang: "fi"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Kehitys {#development}

## Rakenne {#layout}

| Polku | Mitä |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: julkaisutarkistus, sitten komentorivi |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | komennot ja valinnat; demotiedostojen ryhmittely otteluiksi; työprosessien joukko |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | yksi demotiedosto demoparser2:n kautta `RawPart`-olioksi - [Demon lukeminen](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | osat, ketjut, kello, erät, joukkueet, rivit, tappot, vahinko, sokaisut - [Ottelun rakentaminen](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | erien yhteenvedot, tulostaulu, ottelun asiakirja, tekstitulostaulu - [Tilastot](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | Parquet-taulukko sen `heat3d`-vihjeineen, ja JSON - [Lämpökarttataulukko](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | CS2:n ja Source2Viewerin etsintä, törmäysverkko katselimen koordinaatistoon - [Kartan vienti](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | minimaalinen glTF-binäärin lukija ja kirjoittaja (ei riippuvuutta numpy:n lisäksi) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | julkaisutarkistus ja päivittäjä - [Päivitykset](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testit ja synteettinen demo |
| `VERSION` | versio, yksi rivi |

Tiedonkulku:

```text
.dem files --demo.read_part--> RawPart --match.chains--> [RawPart, ...] per match
          --match.build_match--> Match (rounds, players, teams, rows, kills, damage, blinds)
          --output.write--> <map>/<match>.parquet  (output.table + HINTS)
                            <map>/<match>.match.json (stats.summary)
<map>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Käyttö Pythonista {#using-it-from-python}

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

`Match.kills`, `Match.damage` ja `Match.blinds` ovat pandas-DataFrameja, joissa on
enemmän kuin tulosteissa - tappajan ja uhrin sijainnit ja paikat tapoittain,
osuman kohtaiset `utility`-arvot - omiin analyyseihisi.

## Testit {#tests}

```bash
python -m pytest
```

`pytest.ini` ajaa `tests/`-hakemiston hiljaisesti. Testit eivät tarvitse demoa, peliä
eikä Source2Vieweria: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
rakentaa demon käsin, kuten demoparser2 sen antaisi - kaksi erää, kaksi pelaajaa
puolta kohden (`ace`, `ash` joukkueesta Alpha; `bob`, `ben` joukkueesta Bravo), niin
pieni, että jokainen vastaus on tiedossa:

- Erä 1, T:ien voitto eliminoimalla: ace tappaa bobin päälaukauksella (avaus),
  ben tappaa acen 1,9 s myöhemmin (trade: bobin kuolema on kostettu), ash tappaa
  benin 3,1 s sen jälkeen - yksin yhtä vastaan, clutch voitettu.
- Erä 2, T:ien voitto pommilla: ash asettaa pommin A:lle, kukaan ei kuole, pommi
  räjähtää.

`fixtures.halves` rakentaa pidemmän ottelun tyhjistä eristä, joukkueet alkuperäisillä
tai vaihdetuilla puolilla, pelin jatkoaikalaskurin kanssa tai ilman, puoliajan pituutta
ja pistooli-eriä varten.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
tarkistaa niiden perusteella: kunkin erän voittajan, syyn, tuloksen ja puolet; kellon
alkamisen ottelusta; talouden ja asetuksen (sen aika erässä, paikka, pommin
räjähtäminen); asetuksen kohteen aina kirjaimeksi tai tyhjäksi, ei koskaan
entiteettinumeroksi; tasapelin ilman voittajaa; pistooli-erät sieltä, missä puolet
vaihtuvat, jatkoaika pois lukien, ja vain erä 1 ilman vaihtoa; joukkueet ilman
klaanin nimiä (`Started T` / `Started CT`); avaukset, tradet ja liput; itsemurhan,
joka ei ole joukkuetappo, ja avauksen siirtymisen ensimmäiseen vihollisen tappoon;
`noscope`- ja `attackerBlind`-arvot taulukossa ja ottelun asiakirjassa; vahingon
terveyden menetyksenä (60, sitten 40 137:n osumasta 40 terveydellä); tulostaulun
luvut ja KAST; clutchit; tekstitulostaulun; taulukon tapahtumat ja missä ne ovat
(räjähdys ilman omaa paikkaa, heittäjän paikka `throwerPlace`:ssa; pommin
räjähdys asettavan joukkueen); että sijainnit ovat elävää dataa, nimettyjä ja
yksikkövektoreita katsesuunnalle; että kirjoitettu tiedosto kantaa vihjeensä; että
osat järjestetään nimistään riippumatta; että uudelleenkäynnistetyn palvelimen kello
jatkuu; ja että palautetun erän kaksoisrivit ratkaistaan siihen, joka johtaa
eteenpäin.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
tarkistaa, että kansioiden demot löydetään `.dem`-kirjainkoosta riippumatta, ja että
ottelu lasketaan kirjoitetuksi vain, kun sekä sen taulukko että ottelun asiakirja ovat
olemassa.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
tarkistaa kehysmuunnokset (Source2Viewerin metrit pelin tuumiin, ja siitä katselimen
kehykseen, determinantin 1 kierto), että leikkeet ja taivas jätetään pois
kirjainkoosta riippumatta ja nimetyistä pinnoista, maa- ja rakennejaon normaalin
mukaan, sekä `.glb`-tiedoston kirjoittamisen ja takaisin lukemisen.

### Lattiatarkistus oikealla kartalla {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<a demo> HEAT3D_SOURCE2VIEWER=<the CLI> python -m pytest
```

Kun molemmat muuttujat on asetettu, myös `test_players_stand_on_the_exported_floor`
ajetaan: se muuntaa demon, vie sen kartan asennetusta pelistä ja tarkistaa, että
vähintään 98 % 300:sta satunnaisesta sijaintinäytteestä on maata niiden alla, ja että
keskimääräinen korkeus maan yläpuolella on alle 5 yksikköä
([Kartan vienti](map-export.md#tarkistus-että-kehys-on-oikein)).

## Koodin käytännöt {#conventions-of-the-code}

- Ajat `match.py`:n sisällä ovat ottelun sekunteja, paitsi asetuksen `time`, sekunteja
  erän sisällä, kuten ottelun asiakirja sen kirjoittaa; tikit muuttuvat sekunneiksi vain
  `_Part.at`:n kautta.
- Puolet ovat merkkijonoja `T` / `CT` kaikkialla raakojen jäsennettyjen tietojen
  ulkopuolella (`team_num` 2 / 3).
- Uusi taulukon sarake menee `ROW_COLUMNS`-listaan (ja `NUMERIC`-listaan, jos se on
  numeerinen) tiedostossa `match.py`; `output.table` valitsee sen Parquet-tyypin
  joukoista `INT16`, `INT32`, `FLOAT64` ja 0/1-liput, muuten float32.
- Jos halutaan muuttaa, mitä katselimen pitää tehdä sarakkeelle, täytyy muuttaa
  `HINTS`-arvoja tiedostossa `output.py`.

## Lisenssi {#licence}

MIT. Kolmannen osapuolen paketit:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Demot ja kartat eivät ole koskaan osa repositoriota; sen `.gitignore` pitää
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` ja vastaavat poissa tyypin perusteella.
