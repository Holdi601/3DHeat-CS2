---
title: "Demon lukeminen"
nav_order: 5
lang: "fi"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Demon lukeminen {#reading-a-demo}

Mitä yhdestä `.dem`-tiedostosta otetaan talteen ennen kuin mitään tulkitaan. Koodi:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

CS2-demo on palvelimen oma nauhoitus (SourceTV): jokainen pelaaja, jokainen tikki, 64 tikkiä
sekunnissa (`TICKRATE = 64`). Sen lukee
[demoparser2](https://github.com/LaihoE/demoparser) kolmella kutsulla, ja tulos säilytetään
sellaisenaan `RawPart`-oliossa:

| Kenttä | Sisältää |
|---|---|
| `path` | tiedosto |
| `map` | `map_name` demon otsikosta (`de_x`); tyhjä, jos otsikossa ei ole sitä |
| `samples` | yksi rivi per pelaaja per näytteistetty tikki: alla olevat pelaaja- ja sääntökentät, sekä `tick`, `steamid`, `name` |
| `events` | tapahtuman nimi -> sen rivit, pelaajien kentät etuliitteinä `user_`, `attacker_`, `assister_`, kuten jäsentäjä ne nimeää |

Mikään `demo.py`:ssä ei päätä, mikä erä on tai kuka voitti; se on
[Ottelun rakentaminen](building-matches.md).

## Näytteistetyt tikit {#the-sampled-ticks}

`parse_ticks` pyydetään tikeille `0, N, 2N, ...` asti 4 000 000:aan (`LAST_TICK`, kaukana
minkään ottelun yli - 17 tuntia 64 tikillä sekunnissa), missä *N* on `--every` (oletus 8).
Jäsentäjä pysähtyy demon loppuun. Jokainen näytteistetyllä tikillä läsnä oleva pelaaja antaa
yhden rivin, olipa hän elossa, kuollut, katsomassa tai valmentaja; suodatus tehdään myöhemmin.

Näytteistysaskel on tärkeä lämpökartan tiheyttä pidemmälle: hetki, jolloin erä ratkeaa, luetaan
näistä näytteistä (katso [Ottelun rakentaminen](building-matches.md#erat)), joten erän
loppuajat ovat tarkkoja yhden askeleen verran (1/8 s oletuksena).

### Pelaajan kentät {#player-fields}

| Ominaisuus | Muuttuu |
|---|---|
| `X`, `Y`, `Z` | sijainti pelin yksiköissä (tuumia), Z ylös. demoparser2 antaa pelaajan origon, eli jalat. |
| `yaw`, `pitch` | katsesuunta (asteina), muutettuna yksikkövektoriksi |
| `health`, `armor_value` | terveys, panssari |
| `team_num` | puoli: 2 = T, 3 = CT; mikä tahansa muu (katsojat, 0, 1) ei ole puolta |
| `team_clan_name` | joukkueen nimi niin kuin palvelin sen näyttää; käytetään joukkueiden nimeämiseen |
| `active_weapon_name` | kädessä oleva ase, niin kuin peli sen nimeää (`AK-47`, `Karambit`) |
| `is_alive` | onko pelaaja elossa - vain elävät pelaajat tulevat sijainneiksi |
| `last_place_name` | kartan oma paikan nimi (`BombsiteA`) |
| `balance` | raha |
| `current_equip_value` | sen arvo, mitä pelaaja kantaa |

### Sääntökentät {#game-rules-fields}

Luetaan rinnalla, kerran pelaajarivillä (ne ovat samat kaikille tikillä):

| Ominaisuus | Käyttö |
|---|---|
| `game_time` | palvelimen kello sekunteina |
| `total_rounds_played` | erälaskuri, joka jatkuu ottelun tiedostojen yli |
| `round_win_status` | kuka voitti juuri pelatun erän: 1 tasapeli, 2 T, 3 CT |
| `round_win_reason` | miten (pelin `CSRoundEndReason`) |
| `team_rounds_total` | kunkin puolen tulos |
| `is_warmup_period` | warmup jätetään pois kaikkialta |
| `is_freeze_period` | freeze time jätetään pois sijainneista |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | pelattava jatkoaika, 0 säännöllisessä pelissä: jatkoajan erät eivät ole pistooli-eriä (jäsentäjällä ei ole lyhyempää nimeä sille) |

## Tapahtumat {#the-events}

Jokainen alla oleva tapahtuma luetaan, kun demo ilmoittaa sen (`list_game_events`), ja kanssa
`X`, `Y`, `Z`, `team_num`, `last_place_name` ja `which_bomb_zone` (pommialue, jolla pelaaja
seisoo: 0 ei mikään, 1 A, 2 B) jokaiselle pelaajalle, jonka tapahtuma nimeää, sekä
`total_rounds_played` ja `is_warmup_period` pelin tilasta sillä tikillä:

| Tapahtuma | Muuttuu |
|---|---|
| `player_death` | tapot ja kuolemat; käyttää kenttiä `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | vahinko; käyttää kenttiä `dmg_health` (terveydelle tehty vahinko), `health` (jäljellä oleva terveys), `weapon` |
| `player_blind` | sokaistut pelaajat; käyttää kenttää `blind_duration` |
| `weapon_fire` | laukaukset ja kranaattiheitot; käyttää kenttää `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | missä kranaatit räjähtivät; käyttää tapahtuman omia kenttiä `x`, `y`, `z` (tapahtumalla ei ole paikan nimeä sille pisteelle, vain heittäjän) |
| `bomb_planted` | asetus; käyttää asettajan `which_bomb_zone`-arvoa ja paikkaa sekä `site`-kenttää (alueen entiteettinumero) |
| `bomb_defused` | purku |
| `bomb_exploded` | milloin pommi räjähti: `explode`-rivin aika |
| `round_freeze_end` | mistä kukin erä alkaa |
| `round_prestart` | mihin ratkaistun erän jälkeinen aika päättyy |
| `round_announce_match_start` | mistä elävä ottelu alkaa |

## Kaksi demojen ominaisuutta, jotka päättävät, miten ne luetaan {#two-facts-about-demos-that-decide-how-they-are-read}

- **Ottelu voi jakautua useaan tiedostoon**, eikä tiedostojen nimet kerro niiden
  järjestystä. Erälaskuri (`total_rounds_played`) jatkuu niiden yli, ja yleensä myös palvelimen
  kello, joten osat voidaan järjestää sen perusteella, mitä ne sisältävät.
- **Nauhoitus voi alkaa ennen ottelua**: warmup, uudelleenkäynnistys, veitsierä. Ottelu alkaa
  tiedoston **viimeisestä** `round_announce_match_start`-tapahtumasta; sitä ennen kaikki
  jätetään pois, ja warmup jätetään pois kaikkialta.
