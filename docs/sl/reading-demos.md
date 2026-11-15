---
title: "Branje dema"
nav_order: 5
lang: "sl"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Branje dema {#reading-a-demo}

Kaj se vzame iz ene datoteke `.dem`, preden se karkoli razlaga. Koda:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Demo CS2 je posnetek strežnika (SourceTV): vsi igralci, na vsakem taktu, 64 taktov na sekundo (`TICKRATE = 64`). Prebere
ga [demoparser2](https://github.com/LaihoE/demoparser) v treh klicih, rezultat pa se ohrani, kakršen je, v `RawPart`:

| Polje | Vsebuje |
|---|---|
| `path` | datoteko |
| `map` | `map_name` iz glave dema (`de_x`); prazno, če glava nima imena |
| `samples` | po ena vrstica na igralca na vzorčen takt: polja igralca in pravil spodaj, plus `tick`, `steamid`, `name` |
| `events` | ime dogodka -> njegove vrstice, s polji igralcev, ki so predpona `user_`, `attacker_`, `assister_`, kakor jih poimenuje razčlenjevalnik |

Nič v `demo.py` ne odloča, kaj je runda ali kdo jo je dobil; to je [Gradnja tekme](building-matches.md).

## Vzorčeni takti {#the-sampled-ticks}

`parse_ticks` se prosi za takte `0, N, 2N, ...` do 4.000.000 (`LAST_TICK`, daleč čez vsako tekmo – 17 ur pri 64 taktih na
sekundo), kjer je *N* `--every` (privzeto 8). Razčlenjevalnik se ustavi ob koncu dema. Vsak igralec, prisoten ob
vzorčenem taktu, da eno vrstico – živ, mrtev, gledalec ali trener; filtriranje pride pozneje.

Korak vzorčenja pomembneje od gostote toplotnega zemljevida: trenutek, ko je runda odločena, je prebran iz teh vzorcev
(glejte [Gradnja tekme](building-matches.md#rounds)), zato so časi koncev rund natančni do enega koraka (1/8 s privzeto).

### Polja igralca {#player-fields}

| Lastnost | Postane |
|---|---|
| `X`, `Y`, `Z` | položaj v igrinih enotah (palcih), Z navzgor. demoparser2 da izhodišče igralca, to je stopala. |
| `yaw`, `pitch` | smer pogleda (stopinje), pretvorjena v enotski vektor |
| `health`, `armor_value` | zdravje, oklep |
| `team_num` | stran: 2 = T, 3 = CT; karkoli drugega (gledalci, 0, 1) ni stran |
| `team_clan_name` | ime ekipe, kakor ga prikaže strežnik; uporabi se za poimenovanje ekip |
| `active_weapon_name` | orožje v roki, kakor ga igra imenuje (`AK-47`, `Karambit`) |
| `is_alive` | ali je igralec živ – samo živi igralci postanejo položaji |
| `last_place_name` | ime kraja na karti (`BombsiteA`) |
| `balance` | denar |
| `current_equip_value` | vrednost tega, kar igralec nosi |

### Polja pravil igre {#game-rules-fields}

Berejo se vzporedno, enkrat na vrstico igralca (za vse so enaka ob istem taktu):

| Lastnost | Za kaj |
|---|---|
| `game_time` | ura strežnika, v sekundah |
| `total_rounds_played` | število rund, ki teče čez datoteke tekme |
| `round_win_status` | kdo je pravkar odigrano rundo dobil: 1 remi, 2 T, 3 CT |
| `round_win_reason` | kako (`CSRoundEndReason` igre) |
| `team_rounds_total` | rezultat vsake strani |
| `is_warmup_period` | ogrevanje se povsod izpusti |
| `is_freeze_period` | čas zamrznitve se izpusti iz položajev |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | igrano podaljšanje, 0 v rednem igranju: runde podaljška niso pištolske (razčlenjevalnik nima krajšega imena) |

## Dogodki {#the-events}

Vsak dogodek spodaj se prebere, ko ga demo napove (`list_game_events`), z `X`, `Y`, `Z`, `team_num`, `last_place_name` in
`which_bomb_zone` (bombno območje, na katerem igralec stoji: 0 nobeno, 1 A, 2 B) za vsakega igralca, ki ga dogodek
navaja, ter `total_rounds_played` in `is_warmup_period` igre ob tem taktu:

| Dogodek | Postane |
|---|---|
| `player_death` | uboji in smrti; uporablja `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | škoda; uporablja `dmg_health` (škoda na zdravje), `health` (ostalo zdravje), `weapon` |
| `player_blind` | oslepljeni igralci; uporablja `blind_duration` |
| `weapon_fire` | streli in meti granat; uporablja `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | kje so granate eksplodirale; uporablja lastne `x`, `y`, `z` dogodka (dogodek nima imena kraja za to točko, samo metalčevega) |
| `bomb_planted` | postavitev; uporablja `which_bomb_zone` in kraj postavljalca ter `site` (številka entitete območja) |
| `bomb_defused` | deaktivacija |
| `bomb_exploded` | kdaj je bomba eksplodirala: čas vrstice `explode` |
| `round_freeze_end` | kje se začne vsaka runda |
| `round_prestart` | kje se konča čas po odločeni rundi |
| `round_announce_match_start` | kje se začne živa tekma |

## Dve dejstvi o demih, ki določata, kako se berejo {#two-facts-about-demos-that-decide-how-they-are-read}

- **Tekma je lahko razdeljena na več datotek**, imena datotek pa ne povedo njihovega vrstnega reda. Število rund
  (`total_rounds_played`) teče čez njih, ponavadi tudi strežnikova ura, zato se deli lahko uredijo po tem, kar vsebujejo.
- **Posnetek se lahko začne pred tekmo**: ogrevanje, ponovni zagon, nož-runda. Tekma se začne pri **zadnjem**
  `round_announce_match_start` v datoteki; pred njim se vse izpusti, ogrevanje pa se izpusti povsod.
