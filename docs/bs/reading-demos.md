---
title: Čitanje demoa
nav_order: 5
lang: "bs"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Čitanje demoa {#reading-a-demo}

Šta se izvlači iz jedne `.dem` datoteke, prije nego se išta protumači. Kod:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

CS2 demo je serverov vlastiti snimak (SourceTV): svaki igrač, svaki
tik, 64 tika u sekundi (`TICKRATE = 64`). Čita se pomoću
[demoparser2](https://github.com/LaihoE/demoparser) u tri poziva, a
rezultat se čuva onako kako dođe, u `RawPart`:

| Polje | Sadrži |
|---|---|
| `path` | datoteku |
| `map` | `map_name` iz zaglavlja demoa (`de_x`); prazno ako ga zaglavlje nema |
| `samples` | jedan red po igraču po uzorkovanom tiku: polja igrača i pravila ispod, plus `tick`, `steamid`, `name` |
| `events` | ime događaja -> njegovi redovi, s poljima igrača s prefiksima `user_`, `attacker_`, `assister_` kako ih parser imenuje |

Ništa u `demo.py` ne odlučuje šta je runda ili ko je pobijedio; to je
[Slaganje meča](building-matches.md).

## Uzorkovani tikovi {#the-sampled-ticks}

Od `parse_ticks` traže se tikovi `0, N, 2N, ...` do 4.000.000 (`LAST_TICK`,
daleko iza svakog meča - 17 sati pri 64 tika u sekundi), gdje je *N* `--every`
(zadano 8). Parser staje na kraju demoa. Svaki igrač prisutan u
uzorkovanom tiku daje jedan red, bio živ, mrtav, posmatrač ili trener;
filtriranje se radi kasnije.

Korak uzorkovanja bitan je izvan gustoće toplotne mape: trenutak kad je runda
odlučena čita se iz ovih uzoraka (pogledajte
[Slaganje meča](building-matches.md#rounds)), pa su vremena kraja runde
tačna na jedan korak (zadano 1/8 s).

### Polja igrača {#player-fields}

| Svojstvo | Postaje |
|---|---|
| `X`, `Y`, `Z` | pozicija, u igrinim jedinicama (inči), Z prema gore. demoparser2 daje ishodište igrača, tj. stopala. |
| `yaw`, `pitch` | smjer pogleda (stepeni), pretvoren u jedinični vektor |
| `health`, `armor_value` | zdravlje, oklop |
| `team_num` | strana: 2 = T, 3 = CT; sve ostalo (posmatrači, 0, 1) nije strana |
| `team_clan_name` | ime tima kako ga server prikazuje, koristi se za imenovanje timova |
| `active_weapon_name` | držano oružje, kako ga igra imenuje (`AK-47`, `Karambit`) |
| `is_alive` | je li igrač živ - samo živi igrači postaju pozicije |
| `last_place_name` | mapin vlastiti naziv mjesta (`BombsiteA`) |
| `balance` | novac |
| `current_equip_value` | vrijednost onoga što igrač nosi |

### Polja pravila igre {#game-rules-fields}

Čitaju se uz njih, jednom po redu igrača (isti su za sve u jednom tiku):

| Svojstvo | Koristi se za |
|---|---|
| `game_time` | serverov sat, u sekundama |
| `total_rounds_played` | broj rundi, koji se nastavlja preko datoteka meča |
| `round_win_status` | ko je dobio upravo odigranu rundu: 1 neriješeno, 2 T, 3 CT |
| `round_win_reason` | kako (igrin `CSRoundEndReason`) |
| `team_rounds_total` | rezultat svake strane |
| `is_warmup_period` | zagrijavanje se svugdje izostavlja |
| `is_freeze_period` | freeze vrijeme se izostavlja iz pozicija |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | produžetak koji se igra, 0 u regularnom dijelu: runde produžetka nisu pištolj runde (parser nema kraće ime za to) |

## Događaji {#the-events}

Svaki događaj ispod čita se kad ga demo deklariše (`list_game_events`), s
`X`, `Y`, `Z`, `team_num`, `last_place_name` i `which_bomb_zone` (zona bombe
u kojoj igrač stoji: 0 nijedna, 1 A, 2 B) za svakog igrača koje
događaj imenuje, te `total_rounds_played` i `is_warmup_period` igre u tom
tiku:

| Događaj | Postaje |
|---|---|
| `player_death` | ubistva i smrti; koristi `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | šteta; koristi `dmg_health` (šteta nanesena zdravlju), `health` (preostalo zdravlje), `weapon` |
| `player_blind` | zasljepljeni igrači; koristi `blind_duration` |
| `weapon_fire` | pucnji i bacanja granata; koristi `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | gdje su granate eksplodirale; koristi vlastite `x`, `y`, `z` događaja (događaj nema naziv mjesta za tu tačku, samo bacačev) |
| `bomb_planted` | postavljanje bombe; koristi postavljačev `which_bomb_zone` i mjesto, te `site` (broj entiteta zone) |
| `bomb_defused` | deaktiviranje |
| `bomb_exploded` | kad je bomba eksplodirala: vrijeme reda `explode` |
| `round_freeze_end` | gdje svaka runda počinje |
| `round_prestart` | gdje završava vrijeme poslije odlučene runde |
| `round_announce_match_start` | gdje živi meč počinje |

## Dvije činjenice o demoima koje određuju kako se čitaju {#two-facts-about-demos-that-decide-how-they-are-read}

- **Meč može biti podijeljen na datoteke**, a imena datoteka ne govore
  njihov redoslijed. Broj rundi (`total_rounds_played`) nastavlja se preko
  njih, a obično i serverov sat, pa se dijelovi mogu poredati iz
  onoga što sadrže.
- **Snimak može početi prije meča**: zagrijavanje, restart, knife
  runda. Meč počinje na **zadnjem** `round_announce_match_start` u
  datoteci; sve prije njega se izostavlja, a zagrijavanje se izostavlja svugdje.
