---
title: "Læsning af en demo"
nav_order: 5
lang: "da"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Læsning af en demo {#reading-a-demo}

Hvad der bliver taget ud af én `.dem`-fil, før noget bliver fortolket. Kode:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

En CS2-demo er serverens egen optagelse (SourceTV): hver spiller, hvert tick, 64 tick i sekundet (`TICKRATE = 64`). Den bliver læst med
[demoparser2](https://github.com/LaihoE/demoparser) i tre kald, og resultatet bliver beholdt, som det kommer, i en `RawPart`:

| Felt | Indeholder |
|---|---|
| `path` | filen |
| `map` | `map_name` fra demo-headeren (`de_x`); tom, hvis headeren ingen har |
| `samples` | én række pr. spiller pr. samplet tick: spiller- og spilregelfelterne nedenfor, plus `tick`, `steamid`, `name` |
| `events` | hændelsesnavn -> dets rækker, med spillernes felter præfikset `user_`, `attacker_`, `assister_`, som parseren navngiver dem |

Intet i `demo.py` afgør, hvad en runde er, eller hvem der vandt; det er [Sådan bygges en kamp](building-matches.md).

## De samplede ticks {#the-sampled-ticks}

`parse_ticks` bliver bedt om ticks `0, N, 2N, ...` op til 4.000.000 (`LAST_TICK`, langt ud over enhver kamp - 17 timer ved 64 tick i sekundet), hvor *N* er `--every` (standard 8). Parseren stopper ved demoens ende. Hver spiller, der er til stede ved et samplet tick, giver én række, uanset om de er i live, døde, tilskuere eller coach; filtreringen sker senere.

Sampling-skridtet betyder mere end heatmapets tæthed: det øjeblik, en runde bliver afgjort, bliver læst ud fra disse samples (se [Sådan bygges en kamp](building-matches.md#rounds)), så rundernes sluttider er nøjagtige til ét skridt (1/8 s som standard).

### Spillerfelter {#player-fields}

| Egenskab | Bliver til |
|---|---|
| `X`, `Y`, `Z` | positionen, i spillets enheder (tommer), Z opad. demoparser2 giver spillerens origin, altså fødderne. |
| `yaw`, `pitch` | kigge-retningen (grader), omdannet til en enhedsvektor |
| `health`, `armor_value` | liv, rustning |
| `team_num` | siden: 2 = T, 3 = CT; alt andet (tilskuere, 0, 1) er ingen side |
| `team_clan_name` | holdets navn, som serveren viser det, brugt til at navngive holdene |
| `active_weapon_name` | våbnet i hånden, som spillet navngiver det (`AK-47`, `Karambit`) |
| `is_alive` | om spilleren er i live - kun levende spillere bliver til positioner |
| `last_place_name` | kortets eget stednavn (`BombsiteA`) |
| `balance` | penge |
| `current_equip_value` | værdien af det, spilleren bærer |

### Spilregelfelter {#game-rules-fields}

Læses sammen med, én gang pr. spillerrække (de er de samme for alle ved et tick):

| Egenskab | Bruges til |
|---|---|
| `game_time` | serverens ur, i sekunder |
| `total_rounds_played` | rundetallet, som fortsætter på tværs af en kamps filer |
| `round_win_status` | hvem der vandt den netop spillede runde: 1 uafgjort, 2 T, 3 CT |
| `round_win_reason` | hvordan (spillets `CSRoundEndReason`) |
| `team_rounds_total` | hver sides score |
| `is_warmup_period` | opvarmning bliver udeladt alle steder |
| `is_freeze_period` | freeze-tid bliver udeladt fra positionerne |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | den overtid, der spilles, 0 i ordinær spilletid: overtidsrunder er ingen pistolrunder (parseren har intet kortere navn for den) |

## Hændelserne {#the-events}

Hver hændelse nedenfor bliver læst, når demoen erklærer den (`list_game_events`), med
`X`, `Y`, `Z`, `team_num`, `last_place_name` og `which_bomb_zone` (den bombezone spilleren står i: 0 ingen, 1 A, 2 B) for hver spiller hændelsen navngiver, og `total_rounds_played` og `is_warmup_period` for spillet på det tick:

| Hændelse | Bliver til |
|---|---|
| `player_death` | kills og dødsfald; bruger `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | skade; bruger `dmg_health` (skade påført liv), `health` (liv tilbage), `weapon` |
| `player_blind` | blændede spillere; bruger `blind_duration` |
| `weapon_fire` | skud og granatkast; bruger `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | hvor granater gik af; bruger hændelsens egne `x`, `y`, `z` (hændelsen har intet stednavn for det punkt, kun kasterens) |
| `bomb_planted` | plantningen; bruger planterens `which_bomb_zone` og sted, og `site` (zonens entity-nummer) |
| `bomb_defused` | desarmeringen |
| `bomb_exploded` | hvornår bomben gik af: tiden for `explode`-rækken |
| `round_freeze_end` | hvor hver runde starter |
| `round_prestart` | hvor tiden efter en afgjort runde slutter |
| `round_announce_match_start` | hvor den live kamp starter |

## To fakta om demoer, der bestemmer, hvordan de læses {#two-facts-about-demos-that-decide-how-they-are-read}

- **En kamp kan være delt over flere filer**, og filernes navne siger ikke deres rækkefølge. Rundetallet (`total_rounds_played`) fortsætter på tværs af dem, og normalt også serverens ur, så delene kan sættes i rækkefølge ud fra deres indhold.
- **En optagelse kan starte før kampen**: opvarmning, en genstart, en knivrunde. Kampen starter ved den **sidste** `round_announce_match_start` i en fil; før den bliver alt udeladt, og opvarmning bliver udeladt alle steder.
