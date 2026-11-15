---
title: "Lese en demo"
nav_order: 5
lang: "no"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Lese en demo {#reading-a-demo}

Hva som hentes ut av én `.dem`-fil, før noe tolkes. Kode:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

En CS2-demo er serverens egen opptak (SourceTV): hver spiller, hvert tick, 64 tick per sekund
(`TICKRATE = 64`). Den leses med [demoparser2](https://github.com/LaihoE/demoparser) i tre kall, og
resultatet beholdes slik det kommer, i en `RawPart`:

| Felt | Holder |
|---|---|
| `path` | filen |
| `map` | `map_name` fra demoens header (`de_x`); tom hvis headeren ikke har den |
| `samples` | én rad per spiller per samplet tick: spiller- og regelfeltene under, pluss `tick`, `steamid`, `name` |
| `events` | hendelsesnavn -> dets rader, med spillernes felt prefikset `user_`, `attacker_`, `assister_` slik parseren navngir dem |

Ingenting i `demo.py` avgjør hva en runde er eller hvem som vant; det er [Bygge en kamp](building-matches.md).

## De samplede tickene {#the-sampled-ticks}

`parse_ticks` bes om tickene `0, N, 2N, ...` opp til 4 000 000 (`LAST_TICK`, langt forbi enhver kamp -
17 timer ved 64 tick per sekund), der *N* er `--every` (standard 8). Parseren stopper ved demoens
slutt. Hver spiller til stede på et samplet tick gir én rad, enten levende, død, tilskuer eller coach;
filtrering skjer senere.

Samplingstakten betyr mer enn tetthet på varmekartet: øyeblikket en runde avgjøres, leses fra disse
prøvene (se [Bygge en kamp](building-matches.md#rounds)), så rundeslutt-tider er nøyaktige til ett
steg (1/8 s som standard).

### Spillerfelt {#player-fields}

| Egenskap | Blir |
|---|---|
| `X`, `Y`, `Z` | posisjonen, i spillets enheter (tommer), Z opp. demoparser2 gir spillerens origin, altså føttene. |
| `yaw`, `pitch` | sikteretningen (grader), gjort om til en enhetsvektor |
| `health`, `armor_value` | helse, rustning |
| `team_num` | siden: 2 = T, 3 = CT; alt annet (tilskuere, 0, 1) er ingen side |
| `team_clan_name` | lagets navn slik serveren viser det, brukt til å navngi lagene |
| `active_weapon_name` | våpenet i hånden, slik spillet kaller det (`AK-47`, `Karambit`) |
| `is_alive` | om spilleren er i live - bare levende spillere blir posisjoner |
| `last_place_name` | kartets eget stedsnavn (`BombsiteA`) |
| `balance` | penger |
| `current_equip_value` | verdien av det spilleren bærer |

### Regelfelt i spillet {#game-rules-fields}

Leses sammen med, én gang per spillerrad (de er like for alle på et tick):

| Egenskap | Brukes til |
|---|---|
| `game_time` | serverens klokke, i sekunder |
| `total_rounds_played` | rundetellingen, som fortsetter over en kamps filer |
| `round_win_status` | hvem som vant runden nettopp spilt: 1 uavgjort, 2 T, 3 CT |
| `round_win_reason` | hvordan (spillets `CSRoundEndReason`) |
| `team_rounds_total` | hver sides score |
| `is_warmup_period` | oppvarming utelates overalt |
| `is_freeze_period` | freeze time utelates fra posisjonene |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | forlengelsen som spilles, 0 i ordinær spilletid: forlengelsesrunder er ingen pistolrunder (parseren har ikke et kortere navn for den) |

## Hendelsene {#the-events}

Hver hendelse under leses når demoen erklærer den (`list_game_events`), med `X`, `Y`, `Z`, `team_num`,
`last_place_name` og `which_bomb_zone` (bombesonen spilleren står i: 0 ingen, 1 A, 2 B) for hver spiller
hendelsen nevner, og `total_rounds_played` og `is_warmup_period` for spillet på det ticket:

| Hendelse | Blir |
|---|---|
| `player_death` | drap og dødsfall; bruker `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | skade; bruker `dmg_health` (skade gjort mot helse), `health` (helse igjen), `weapon` |
| `player_blind` | blendede spillere; bruker `blind_duration` |
| `weapon_fire` | skudd og granatkast; bruker `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | hvor granater gikk av; bruker hendelsens egne `x`, `y`, `z` (hendelsen har ikke et stedsnavn for det punktet, bare kasterens) |
| `bomb_planted` | plantingen; bruker planterens `which_bomb_zone` og sted, og `site` (sonens entitetsnummer) |
| `bomb_defused` | desarmeringen |
| `bomb_exploded` | når bomben gikk av: tiden for `explode`-raden |
| `round_freeze_end` | der hver runde starter |
| `round_prestart` | der tiden etter en avgjort runde slutter |
| `round_announce_match_start` | der den levende kampen starter |

## To fakta om demoer som avgjør hvordan de leses {#two-facts-about-demos-that-decide-how-they-are-read}

- **En kamp kan være delt over flere filer**, og filenes navn sier ikke rekkefølgen deres. Rundetellingen
  (`total_rounds_played`) fortsetter over dem, og vanligvis serverens klokke også, så delene kan settes i
  rekkefølge ut fra det de inneholder.
- **Et opptak kan starte før kampen**: oppvarming, en omstart, en knivrunde. Kampen starter ved **siste**
  `round_announce_match_start` i en fil; før den utelates alt, og oppvarming utelates overalt.
