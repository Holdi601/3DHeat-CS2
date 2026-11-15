---
title: "Lämpökarttataulukko (`<match>.parquet`)"
nav_order: 8
lang: "fi"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Lämpökarttataulukko (`<match>.parquet`) {#the-heatmap-table-parquet}

Yksi Parquet-tiedosto per ottelu: jokaisen elossa olevan pelaajan sijainti näytteistettynä
ja jokainen tapahtuma siinä, missä se tapahtui, yksi rivi kumpikin - pitkä taulukko, jonka
3DHeat-katselin lukee lämpökarttana ja muu ohjelma tavallisena taulukkona. Koodi:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(tiedosto), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(rivit; katso [Ottelun rakentaminen](building-matches.md)).

Tiedosto kirjoitetaan Snappy-pakkauksella 256 000 rivin ryhmissä. Rivit lajitellaan
`time`n ja sitten `event`in mukaan. Taulukossa ovat vain rivit erän sisältä (sen freeze timen
lopusta seuraavan erän alkuun).

Testien synteettisessä demossa ensimmäisen erän tapahtumarivit:

![taulukon tapahtumarivit](../assets/img/table-rows.svg)

`.3dheat`-säilössä taulukko on jäsen, jonka rooli on `table`
([Yksi tiedosto per ottelu](output-container.md)).

## Sarakkeet {#columns}

Sarakkeet aina tässä järjestyksessä. Tekstisarakkeet ovat sanakirjakoodattuja merkkijonoja
(`dictionary<int32, string>`) eivätkä koskaan tyhjiä: "ei arvoa" on tyhjä merkkijono.
Numeeriset sarakkeet ovat null, kun rivillä ei ole arvoa.

| Sarake | Tyyppi | Mitä |
|---|---|---|
| `match` | merkkijono | ottelun nimi (`alpha-vs-bravo-m1`, tai `...-b` toiselle ketjulle) |
| `map` | merkkijono | kartta demon otsikosta (`de_x`) |
| `round` | int16 | erän numero, 1-pohjainen |
| `roundId` | merkkijono | `<match> #NN`, erän numero kahdella numerolla (`alpha-vs-bravo-m1 #07`): ainutlaatuinen kaikkien ottelujen yli, katselimen istunto |
| `phase` | merkkijono | `freeze` erän freeze timessä (edellisen erän lopusta), `live` kunnes erä ratkaistaan, `after` kun voittajat metsästävät ja häviäjät säästävät |
| `time` | float64 | sekuntia siitä, kun ottelu alkoi (ensimmäisen tiedoston elävä alku), yhdellä kellolla sen tiedostojen yli |
| `roundTime` | float32 | sekuntia siitä, kun tämän erän freeze time päättyi; negatiivinen freeze timen aikana |
| `event` | merkkijono | mikä rivi on - katso [Tapahtumat](#tapahtumat) |
| `player` | merkkijono | pelaajan nimi (kullekin tapahtumalle kerrotaan alla, mikä pelaaja) |
| `steamid` | merkkijono | pelaajan Steam-ID (64-bittinen, tekstinä) |
| `side` | merkkijono | `T` tai `CT` tässä erässä; tyhjä, kun pelaaja ei ollut millään puolella |
| `team` | merkkijono | pelaajan joukkueen nimi (tai `Started T` / `Started CT`); `explode`:lle asettavan joukkueen nimi |
| `x`, `y`, `z` | float32 | sijainti pelin omissa koordinaateissa: tuumia (pelin yksikköjä), **Z ylös**, oikeakätinen |
| `dirX`, `dirY`, `dirZ` | float32 | mihin pelaaja katsoo, yksikkövektori samassa kehyksessä; vain sijainnit |
| `health` | int16 | 0-100; sijainneissa, ja `hurt`:ssa se, mitä osuman jälkeen jäi |
| `armor` | int16 | 0-100; sijainneissa, ja `hurt`:ssa se, mitä osuman jälkeen jäi |
| `money` | int32 | pelaajan raha; vain sijainnit |
| `equipment` | int32 | sen arvo, mitä pelaaja kantaa; vain sijainnit |
| `weapon` | merkkijono | ase niin kuin peli sen nimeää (`AK-47`, `M4A1-S`, `Knife` kaikille veitsen skineille) |
| `place` | merkkijono | kartan oma paikan nimi rivin sijainnissa (`BombsiteA`, `CTSpawn`); tyhjä kranaattien räjähdyksissä: demo ei nimeä paikkaa sille, minne kranaatti räjähti |
| `throwerPlace` | merkkijono | heittäjän paikan nimi, kun kranaatti räjähti; vain kranaattien räjähdykset |
| `other` | merkkijono | tappoon, kuolemaan, osumaan tai välähdykseen liittyvä toinen pelaaja |
| `damage` | float32 | menetetty terveys; vain `hurt` |
| `duration` | float32 | sokaisun sekunnit; vain `blind` |
| `headshot` | int8 | 0/1; vain `kill` ja `death` |
| `opening` | int8 | 0/1, erän ensimmäinen vihollisen tappo; vain `kill` ja `death` |
| `traded` | int8 | 0/1. `kill`:lle: se oli trade-tappo. `death`:lle: se kostettiin 5 s:n sisällä. Vain `kill` ja `death`. |
| `noscope` | int8 | 0/1, tappo tehtiin tähtäävällä aseella, joka ammuttiin ilman tähtäystä (tapahtuman `noscope`); vain `kill` ja `death` |
| `attackerBlind` | int8 | 0/1, tappaja oli sokaistu, kun hän tappoi (tapahtuman `attackerblind`); vain `kill` ja `death` |
| `won` | int8 | 0/1, voittiko tämän rivin puoli erän; null, kun `side` on tyhjä |
| `matchWon` | int8 | 0/1, voittiko tämän rivin joukkue ottelun; null, kun `team` on tyhjä tai nauhoitus ei näytä loppua (katso ottelun asiakirjan `winner`) |
| `roundEndReason` | merkkijono | miten rivin erä päättyi: `elimination`, `bomb` (pommi räjähti), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | merkkijono | tämän rivin puolen osto tässä erässä: `pistol`, `eco`, `force`, `full` |
| `detail` | merkkijono | kaikki tapahtuman kentät, joita muut sarakkeet eivät kanna, JSON-objektina (pelin omilla nimillä): laukauksen luodit (`fire_bullets`: lähtöpaikka, kulmat, epätarkkuus, leviäminen, rekyylin indeksi, siemen...), kuoleman `dominated`, `revenge`, `attackerinair`, `wipe`..., esineen `defindex`, askelen ei mitään |
| `text` | merkkijono | chat-rivi; vain `chat` |
| `entity` | int32 | kranaatin entiteetti: `throw`-lennon (`grenade`-rivit), sen räjähdyksen ja sokaistujen pelaajien rivit jakavat sen |
| `hitgroup` | merkkijono | mihin luoti osui (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | menetetty panssari; vain `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | mihin kohtaan vartaloa luoti osui, uhrin kehyksessä metreinä (x eteen, y ylös jaloista, z oikealle): laukauksen säde (`fire_bullets`, muuten tappajan silmä ja katse) jäljitettynä vartaloon, joka oli asennossa kuten uhri seisoi ja kyykistyi, siihen osaan, jonka `hitgroup` nimeää; vain `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | laukauksen suunta samassa kehyksessä; `hitMiss` kuinka monta metriä (m) säde meni nimetyn osan ohi (0: osui siihen); `hitFrom` `bullet` tai `aim` |
| `penetrated` | int16 | seinät, joiden läpi tappava luoti meni; `kill` ja `death` |
| `throughSmoke` | int8 | 0/1, tapettu savun läpi; `kill` ja `death` |
| `distance` | float32 | tappoetäisyys niin kuin peli sen laskee (metreinä); `kill` ja `death` |
| `assister` | merkkijono | kuka avusti; `kill` ja `death` |
| `flash`, `flashAlpha` | float32 | välähdyksen jäljellä olevat sekunnit, ja kuinka valkoinen; sijainnit |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; sijainnit |
| `zoom`, `duck`, `moveType` | | tähtäimen zoomitaso, kuinka paljon kyykyssä (0-1), pelin liiketyyppi; sijainnit |
| `spottedBy` | merkkijono | niiden vihollisten Steam-ID:t, jotka näkevät tämän pelaajan, `\|`-erotettuina; sijainnit |
| `inventory` | merkkijono | kaikki, mitä pelaaja kantaa, `\|`-erotettuina; sijainnit |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | kädessä olevan aseen lipas ja varasto; laukaukset nykyisessä purskeessa; sijainnit |
| `punchPitch`, `punchYaw` | float32 | tähtäimen iskun (aim punch) pitch ja yaw, asteina; sijainnit |
| `ping` | int16 | millisekunteja; sijainnit |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | pelin omat tulostaulun luvut ottelulle tähän asti; sijainnit |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | rahaa käytetty tässä erässä ja ottelussa; varustearvo erän alussa; sijainnit |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, pelaajan tila rivin hetkellä, tapahtumat mukaan lukien: kypärä, purkutyökalu, mikä tahansa panssari, tähtäin (pelaajan viimeisestä sijaintinäytteestä rivin hetkeen asti), sokaistu (`blind`-tapahtumassa, joka osui heihin); jokainen rivi, joka nimeää pelaajan |
| `state_utility` | int16 | mukana olevat kranaatit hetkellä (`inventory`:sta); jokainen rivi, joka nimeää pelaajan |
| `state_weapon` | merkkijono | käsissä oleva ase hetkellä (`death`:ssa uhrin oma, kun `weapon` on tappajan); jokainen rivi, joka nimeää pelaajan |
| `earn_round_cs2` | int16 | mitä erä maksoi: `round_end`:ssä voittopalkkio tai tappiobonus (asettavan puolen bonuksella), `plant`:ssa ja `defuse`:ssa pelaajan 300 |

## Tapahtumat {#events}

Mikä pelaaja rivillä on, missä hän seisoo ja mitkä sarakkeet rivi täyttää.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won`, `roundEndReason` ja `buy` täytetään jokaisella rivillä (`matchWon`, kun ottelun voittaja
tiedetään); `inventory`, `money`, `equipment` ja `state_*`-sarakkeet jokaisella rivillä,
joka nimeää pelaajan (tapahtumat ottavat ne pelaajan viimeisestä sijaintinäytteestä).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Myös täytetty |
|---|---|---|---|
| `position` | pelaaja | pelaaja (jalat) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (kädessä), `place`, ja pelaajan koko tila (sarakkeet `flash`:sta alkaen) - myös freeze timen aikana |
| `kill` | tappaja | missä tappaja seisoi | `other` (uhri), `weapon`, `headshot`, `opening`, `traded` (trade-tappo), `noscope`, `attackerBlind`, `place` |
| `death` | uhri | missä uhri kaatui | `other` (tappaja; tyhjä maailmalle), `weapon`, `headshot`, `opening`, `traded` (kostettu), `noscope`, `attackerBlind`, `place` |
| `hurt` | uhri | missä uhri osui | `other` (hyökkääjä), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - myös joukkuetovereiden ja maailman osumat |
| `shot` | ampuja | mistä laukaus ammuttiin | `weapon`, `place`, `detail` (pelin kuvaus luodeista) |
| `slash` | pelaaja | missä veistä heilautettiin | `weapon` = `Knife` |
| `grenade` | heittäjä | lentävä kranaatti, pelaajien näytteistyksellä ja siellä, missä se pysähtyi | `weapon` (kranaatti), `entity` |
| `throw` | heittäjä | mistä kranaatti heitettiin | `weapon` (kranaatti), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | heittäjä | missä se räjähti | `weapon`, `throwerPlace` (heittäjän paikka sillä hetkellä); `place` jää tyhjäksi |
| `blind` | sokaistu pelaaja | missä he seisoivat | `other` (välähdyttäjä), `duration`, `weapon` = `Flashbang`, `entity`, `place` - myös sokaistut joukkuetoverit |
| `plant` | asettaja | missä he asettivat | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | purkaja | missä he purkivat | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | jokainen pelaaja, joka pelasi erän | missä pelaaja viimeksi seisoi | `won`, `earn_round_cs2` (mitä erä maksoi heille: puolen rahan nousu seuraavaan freeze timeen, missä säännöt sen sallivat, muuten säännön oma), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | asettaja (Steam-ID:llään), puoli `T`, asettava joukkue | asetuksen sijainti | `weapon` = `C4 Explosive`, `place` (asettajan paikka asetuksella: missä pommi makasi); sen aika on, kun pommi räjähti |
| `chat` | lähettäjä | missä he olivat | `text` |
| jokainen muu pelitapahtuma pelaajasta pelin omalla nimellä: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | pelaaja | missä he olivat (kranaatin tapahtumille: missä kranaatti oli) | `weapon` (esineen), `entity`, `detail` (kaikki tapahtuman kentät) |

Mitä on mukana ja mitä ei:

- **position**-rivit ovat elossa olevia pelaajia puolella, freeze timen ja warmupin
  ulkopuolella, joka `--every`:n tikki (oletuksena kahdeksan sekunnissa).
- **kill**-rivit ovat vain vihollisen tekemiä tappoja - ei joukkuetappoja, itsemurhia eikä
  kuolemia maailmalle. **death**-rivit ovat jokainen kuolema, nämä mukaan lukien.
- **explode**-rivit ovat jokainen asetettu pommi, joka räjähti, demon `bomb_exploded`-tapahtuman
  mukaan: myös jälkeisessä vaiheessa, kun T:t olivat jo voittaneet eliminoimalla. Demo ilman
  tuota tapahtumaa saa yhden jokaiselle pommin voittamalle erälle, erän lopussa.
- **hurt**- ja **blind**-rivit ovat vain vihollisten välillä.
- **shot** jättää veitset ja C4:n pois; kranaatit ovat **throw**-rivejä.
- **molotov** kattaa molotovit ja incendiaryt (tulen syttyminen).
- Joukkuetovereiden vahinko, joukkuetovereiden ja katsojien välähdykset, freeze timen
  tapahtumat ja kaikki erien välinen eivät ole taulukossa.

Esimerkki, testien synteettisestä demosta (savu heitettiin, päälaukauksella avaava tappo, trade-tappoja):

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

bobin kuoleman kostaa ben, joka tappoi acen 1,9 s myöhemmin (bobin `death`-rivi: traded 1;
benin `kill`-rivi: trade-tappo, traded 1); bobiin tehty toinen osuma oli 137 vahinkoa 40 terveydellä,
joten se lasketaan 40:ksi.

## `heat3d`-alaviitevihjeet {#the-heat3d-footer-hints}

Tiedoston Parquet-alaviitteessä (skeeman avain/arvo -metatiedot) on lukuohjeet avaimen
**`heat3d`** alla, JSON-objektina:

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

| Kohta | Sanoo |
|---|---|
| `version`, `kind` | vihjeiden versio (1) ja mikä ne kirjoitti (`cs2-demo`) |
| `axes.up` | tiedoston Z on ylös |
| `axes.flipY` | käännä tiedoston Y merkki (katso alla) |
| `axes.scale` | 1: sijainnit käytetään sellaisenaan, pelin yksiköissä |
| `entity.size` | pelaaja on **32 yksikköä** leveä - CS2-pelaajan leveys - koko, jonka laatikkotoisto piirtää |
| `columns.x` / `y` / `z` | sijaintisarakkeet |
| `columns.time`, `timeUnit` | `time`, sekunteina |
| `columns.personId` | pelaaja on henkilö |
| `columns.teamId` | puoli on ryhmä (joten T ja CT, eivät joukkueiden nimet, värittävät ryhmät) |
| `columns.sessionId` | jokainen erä (`roundId`) on istunto |
| `columns.lookMode` ja `dirX`-`dirZ` | katsesuunta on vektori noissa sarakkeissa |
| `columns.extra` | sarakkeet, jotka säilytetään suodattimina, hyödyllisyysjärjestyksessä |

Katselin, joka tuntee avaimen, avaa tiedoston ilman mitään asetettavaa. Muut jättävät sen
huomiotta. Lukeaksesi sen itse:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Akselit ja yksiköt {#axes-and-units}

Koordinaatit ovat pelin omat: **tuumia** (yksi pelin yksikkö; pelaaja on 72 yksikköä
pitkä seisoessaan ja 32 leveä), **Z ylös**, ja oikeakätinen.

Katselimen, jonka maailma on Y-ylös, pitää piirtää pelin (x, y, z) muodossa
**(x, z, -y)** - Z muuttuu korkeudeksi ja Y käännetään. Se on kierto, ei peilaus.
Jos piirretään tavalla, jolla vasenkätinen Z-ylös-maailma piirretään, eli (x, z, y),
jokainen kartta tulee peilattuna, A-alue väärälle puolelle; `flipY: true` on se, mitä
vihjeet sanovat estämään tämän. [Kartan vienti](map-export.md) kirjoittaa geometriansa jo
(x, z, -y)-kehyksessä samoissa yksiköissä, joten se on taulukon alla ilman mitään säätöä.

Etäisyydet katselimessa on merkitty metreinä; mittakaavalla 1 ne ovat pelin yksiköitä.
Kerro 0,0254:llä saadaksesi metrit.

## Koko {#size}

Sijainnit hallitsevat: noin kymmenen pelaajaa kertaa 8 näytettä sekunnissa elävästä
pelistä oletuksella `--every 8`, vähemmän kuolleille pelaajille ja freeze timelle. `--every`:n
puolittaminen kaksinkertaistaa ne; tapahtumat eivät muutu.
