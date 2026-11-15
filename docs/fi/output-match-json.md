---
title: "Ottelun asiakirja (`<match>.match.json`)"
nav_order: 9
lang: "fi"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Ottelun asiakirja (`<match>.match.json`) {#the-match-document-matchjson}

Yksi JSON-asiakirja per ottelu, lähellä sen taulukkoa: joukkueet, tulos, jokainen erä
tuloksineen, talous, asetus, tappot, clutchit ja selviytyjät sekä jokaisen pelaajan
tulostaulun rivi. Sen lataa 3DHeat-katselimen **Ottelu**-välilehti.
Koodi: `summary()` tiedostossa
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
luvut on määritelty sivulla [Tilastot](statistics.md).

Tiedosto on UTF-8, sisennetty yhdellä välilyönnillä, ja se säilyttää ei-ASCII-merkit
(pelaajien ja joukkueiden nimet) sellaisinaan. Ajat ovat sekunteja: erät pyöristetään
kolmeen desimaaliin, tapot ja asetus kahteen.

## Asiakirja {#the-document}

| Kenttä | Tyyppi | Mitä |
|---|---|---|
| `format` | merkkijono | aina `heat3d-cs2-match` - sillä lukija tunnistaa tiedoston |
| `version` | numero | `3`. Version 1 asiakirja antaa asetuksen `time`-arvon otteluin sekunteina; versiosta 2 lähtien se on sekunteina erän sisällä, kuten tapon. 3 lisää kentät kohdasta `header` alkaen ja freeze timen taulukkoon. |
| `match` | merkkijono | ottelun nimi, kuten tiedostot on nimetty |
| `map` | merkkijono | kartta (`de_x`) |
| `demos` | merkkijonotaulukko | demotiedostot, joista se rakennettiin, vain tiedostonimet, ottelun järjestyksessä |
| `teams` | merkkijonotaulukko | joukkueiden nimet ilmestymisjärjestyksessä (erä 1: T-puoli ensin) |
| `score` | objekti | joukkueen nimi -> voitetut erät: viimeisen erän tulos |
| `winner` | merkkijono tai null | ottelun voittanut joukkue, jos nauhoitus näyttää lopun; null nauhoitukselle, joka loppuu kesken, jatkoajalle ilman voittopaneelia tai tasapelille |
| `winnerSource` | merkkijono tai null | miten `winner` tiedetään: `winPanel` (pelin ottelun voittopaneeli), `surrender`, `regulation` (yli puolet säännöllisten erien voitoista) |
| `rounds` | objektitaulukko | jokainen valmis erä järjestyksessä - [alla](#erat) |
| `incomplete` | lukutaulukko | erien numerot, jotka demon loppu katkaisi ja jätti pois |
| `missing` | lukutaulukko | erien numerot ennen ensimmäistä, jonka demot sisältävät: `[1, 2]`, kun nauhoitus alkaa erästä 3 |
| `halfLength` | numero tai null | säännöllisen puoliajan erät siitä, missä puolet ensin vaihtuvat (`12` 24 erän formaatissa); null, kun nauhoitus ei näytä vaihtoa |
| `pistolRounds` | lukutaulukko | pistooli-erät, joilla `buy` lasketaan: erä 1, ja puoliajan jälkeinen erä, kun `halfLength` tiedetään; ei koskaan jatkoajan erää |
| `players` | objektitaulukko | tulostaulu - [alla](#pelaajat) |
| `conventions` | objekti | lukujen takana olevat määritelmät, [alla](#sopimukset) |
| `header` | objekti | ensimmäisen demon otsikko sellaisena kuin jäsentäjä sen antaa: palvelimen nimi, päivitysversio, demoversio, kartta |
| `profiles` | objekti | Steam-ID -> se, mikä pysyy samana pelaajalle koko ottelun ajan: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (viimeksi nähty) |
| `playerInfo` | objektitaulukko | jokainen demojen listaama pelaaja, myös valmentajat ja kommentaattorit: Steam-ID, nimi, joukkuenumero |
| `skins`, `itemDrops` | objektitaulukko | asekuoret ja esinepudotukset, jos demossa on niitä (turnausdemoissa lähetyksestä niitä ei ole) |
| `chat` | objektitaulukko | jokainen chat-rivi ottelussa: aika, erä, pelaaja, puoli, teksti |
| `events` | objektitaulukko | jokainen pelitapahtuma, joka ei koske yhtäkään pelaajaa, aikajärjestyksessä, kaikki kentät mukana: erän äänimerkit ja vaiheet, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (palvelimen asetukset muutosten mukaan), lähetyksen kameran ohjaajan takaa-ajo- ja kiinteät kuvat, `cs_win_panel_match`, ... |
| `state` | objektitaulukko | pelin tila siellä, missä se muuttui: aika, kenttä, arvo - aikalisät (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), pommi (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, elossa olevat pelaajat, palvelimen `match_start_time` ja `round_start_time` |
| `selfCheck` | objekti | `completeness`: mihin kaikki demon tieto meni - jokaisen tapahtumanimen, ominaisuusluokan, verkkoviestin, kehyksen ja merkkijonotaulun kohdalla `seen`, `decoded`, `partial`, `raw` ja `lost` -määrät, kirjoitetut sivutiedostot, kokonais-`lost` (0, ellei `--no-bulk`), ja ominaisuudet, jotka jäsentäjä listaa mutta ei voi lukea (`unreadProps`). Sopimus: [Muuntajat säilyttävät kaiken](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); sivutiedostot: README:n osio Completeness |

## Erät {#rounds}

| Kenttä | Tyyppi | Mitä |
|---|---|---|
| `number` | numero | erä, 1-pohjainen |
| `start` | numero | ottelun sekunnit, kun freeze time päättyi |
| `end` | numero | ottelun sekunnit, kun erä ratkaistiin |
| `until` | numero | ottelun sekunnit, kun seuraava erä alkoi (jälkeisen vaiheen loppu) |
| `winner` | merkkijono | `T` tai `CT`; tyhjä tasapelissä |
| `winnerTeam` | merkkijono | voittaneen puolen joukkueen nimi; tyhjä tasapelissä |
| `reason` | merkkijono | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` tai `other` |
| `score` | objekti | joukkueen nimi -> tämän erän jälkeen voitetut erät |
| `sides` | objekti | joukkueen nimi -> `T` / `CT` tässä erässä |
| `equipment` | objekti | puoli -> sen elossa olevien pelaajien varustuksen kokonaisarvo freeze endissä, dollareina |
| `buy` | objekti | puoli -> `pistol`, `eco`, `force` tai `full` |
| `plant` | objekti tai null | pommin asetus: `site` (`A` tai `B`; tyhjä, kun demo ei kerro), `time` (sekuntia **erän sisällä**, kuten tapossa), `player`, `steamid`, `x`, `y`, `z` (pelin yksiköt), `place` (asettajan paikan nimi: missä pommi makasi) |
| `survivors` | objekti | puoli -> aloittavien pelaajien, jotka olivat yhä hengissä erän ratkaisussa, nimet, aakkosjärjestyksessä |
| `clutches` | objektitaulukko | kukin: `player`, `steamid`, `side`, `against` (vihollisia elossa, kun pelaaja jäi viimeiseksi), `won` |
| `kills` | objektitaulukko | jokainen erän kuolema järjestyksessä - alla |

Miten nämä löydetään: [Ottelun rakentaminen](building-matches.md#erat);
clutchit ja selviytyjät: [Tilastot](statistics.md#clutchit).

### Erän tapot {#a-rounds-kills}

Jokainen kuolema erässä, jälkeinen vaihe mukaan lukien:

| Kenttä | Tyyppi | Mitä |
|---|---|---|
| `time` | numero | sekuntia **erän sisällä** (freeze endistä) |
| `attacker`, `attackerSide` | merkkijono | tappaja ja hänen puolensa; tyhjä maailmalle |
| `victim`, `victimSide` | merkkijono | uhri ja hänen puolensa |
| `assister` | merkkijono tai null | avustanut pelaaja, tai null |
| `flashAssist` | bool | avustus oli välähdys |
| `weapon` | merkkijono | niin kuin peli sen nimeää |
| `headshot` | bool | |
| `wallbang` | bool | luoti meni jonkin läpi |
| `throughSmoke` | bool | tappo savun läpi |
| `noscope` | bool | tähtäävä ase ammuttiin ilman tähtäystä |
| `attackerBlind` | bool | tappaja oli sokaistu |
| `opening` | bool | erän ensimmäinen vihollisen tappo |
| `traded` | bool | tämä kuolema kostettiin 5 s:n sisällä |
| `trade` | bool | tämä tappo kosti joukkuetoverin 5 s:n sisällä |
| `teamkill` | bool | tappaja ja uhri samalla puolella, kaksi eri pelaajaa |
| `suicide` | bool | tappaja ja uhri sama pelaaja (esimerkiksi oma kranaatti); ei joukkuetappo |
| `after` | bool | tappo tapahtui sen jälkeen, kun erä oli ratkaistu |
| `place` | merkkijono | missä **uhri** oli (kartan paikan nimi) |

## Pelaajat {#players}

Yksi merkintä per pelaaja, joukkueen nimen mukaan ja sitten parhain ensin tappojen
miinus kuolemien, sitten tappojen mukaan:

| Kenttä | Tyyppi | Mitä |
|---|---|---|
| `name`, `steamid`, `team` | merkkijono | kuka |
| `kills`, `deaths` | numero | |
| `assists`, `flashAssists` | numero | avustukset ilman ja välähdyksellä |
| `diff` | numero | tappoja miinus kuolemia |
| `adr` | numero | keskimääräinen vahinko pelattua erää kohden, menetetty terveys |
| `kast` | numero | prosenttia pelatuista eristä, joissa oli tappo, avustus, selviytyminen tai kostettu kuolema |
| `headshotPct` | numero | prosenttia tapoista, jotka olivat päälaukauksia |
| `openingKills`, `openingDeaths` | numero | voitetut ja hävityt avausduellit |
| `tradeKills`, `tradedDeaths` | numero | trade-tapot; kuolemat, jotka kostettiin |
| `multiKills` | objekti | `{"2k": n, "3k": n, "4k": n, "5k": n}`: erät, joissa oli niin monta tappoa |
| `clutches`, `clutchesWon` | numero | |
| `utilityDamage` | numero | vahinko HE:llä, molotovilla, incendiaryllä |
| `enemiesFlashed` | numero | vihollisia sokaistu vähintään 1 s |
| `plants`, `defuses` | numero | |
| `teamkills` | numero | joukkuetovereita tapettu; itsemurhia ei lasketa |
| `roundsPlayed` | numero | aloitetut erät |

Jokainen määritelmä: [Tilastot](statistics.md#tulostaulun-rivi).

## Sopimukset {#conventions}

Kirjoitettu jokaiseen asiakirjaan, jotta lukija tietää, mitä luvut tarkoittavat ilman
tätä sivua:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Esimerkki {#an-example}

Testien synteettisestä kahden erän demosta, lyhennettynä (`...` merkitsee jätettyä):

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

Avaimien järjestystä kohdissa `survivors`, `equipment` ja `buy` ei ole kiinnitetty.
