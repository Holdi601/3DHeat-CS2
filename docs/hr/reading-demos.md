---
title: "Čitanje demo snimke"
nav_order: 5
lang: "hr"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Čitanje demo snimke {#reading-a-demo}

Što se izvlači iz jedne `.dem` datoteke, prije nego se bilo što tumači. Kod:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

CS2 demo snimka je vlastita snimka poslužitelja (SourceTV): svaki igrač, svaki tik, 64 tika u sekundi (`TICKRATE = 64`). Čita se pomoću [demoparser2](https://github.com/LaihoE/demoparser) u tri poziva, a rezultat se čuva kakav dolazi, u `RawPart`:

| Polje | Sadrži |
|---|---|
| `path` | datoteku |
| `map` | `map_name` iz zaglavlja demo snimke (`de_x`); prazno ako ga zaglavlje nema |
| `samples` | jedan redak po igraču po uzorkovanom tiku: polja igrača i pravila ispod, plus `tick`, `steamid`, `name` |
| `events` | ime događaja -> njegovi redci, s poljima igrača prefiksiranim sa `user_`, `attacker_`, `assister_` kako ih parser imenuje |

Ništa u `demo.py` ne odlučuje što je runda ili tko ju je pobijedio; to je [Sastavljanje meča](building-matches.md).

## Uzorkovani tikovi {#the-sampled-ticks}

`parse_ticks` traži tikove `0, N, 2N, ...` do 4.000.000 (`LAST_TICK`, daleko iza svakog meča - 17 sati pri 64 tika u sekundi), gdje je *N* `--every` (zadano 8). Parser staje na kraju demo snimke. Svaki igrač prisutan u uzorkovanom tiku daje jedan redak, bilo živ, mrtav, gledatelj ili trener; filtriranje se radi kasnije.

Korak uzorkovanja važan je i izvan gustoće toplinske karte: trenutak kad se runda odlučuje čita se iz ovih uzoraka (vidi [Sastavljanje meča](building-matches.md#rounds)), pa su vremena završetka rundi točna do jednog koraka (1/8 s zadano).

### Polja igrača {#player-fields}

| Svojstvo | Postaje |
|---|---|
| `X`, `Y`, `Z` | položaj, u jedinicama igre (inči), Z gore. demoparser2 daje ishodište igrača, tj. stopala. |
| `yaw`, `pitch` | smjer pogleda (stupnjevi), pretvoren u jedinični vektor |
| `health`, `armor_value` | zdravlje, oklop |
| `team_num` | strana: 2 = T, 3 = CT; sve drugo (gledatelji, 0, 1) nije strana |
| `team_clan_name` | naziv tima kako ga poslužitelj prikazuje, koristi se za imenovanje timova |
| `active_weapon_name` | oružje u ruci, kako ga igra imenuje (`AK-47`, `Karambit`) |
| `is_alive` | je li igrač živ - samo živi igrači postaju pozicije |
| `last_place_name` | vlastito ime mjesta na karti (`BombsiteA`) |
| `balance` | novac |
| `current_equip_value` | vrijednost onoga što igrač nosi |

### Polja pravila igre {#game-rules-fields}

Čitaju se uz to, jednom po retku igrača (isti su za sve u tiku):

| Svojstvo | Za što se koristi |
|---|---|
| `game_time` | sat poslužitelja, u sekundama |
| `total_rounds_played` | broj rundi, koji se nastavlja kroz datoteke meča |
| `round_win_status` | tko je pobijedio upravo odigranu rundu: 1 neriješeno, 2 T, 3 CT |
| `round_win_reason` | kako (`CSRoundEndReason` igre) |
| `team_rounds_total` | rezultat svake strane |
| `is_warmup_period` | zagrijavanje se svuda izostavlja |
| `is_freeze_period` | freeze time se izostavlja iz pozicija |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | produženje koje se igra, 0 u regularnom dijelu: runde produženja nisu runde s pištoljima (parser nema kraće ime za to) |

## Događaji {#the-events}

Svaki događaj ispod čita se kad ga demo deklarira (`list_game_events`), s `X`, `Y`, `Z`, `team_num`, `last_place_name` i `which_bomb_zone` (zona bombe u kojoj igrač stoji: 0 nijedna, 1 A, 2 B) za svakog igrača koga događaj imenuje, te `total_rounds_played` i `is_warmup_period` igre u tom tiku:

| Događaj | Postaje |
|---|---|
| `player_death` | ubojstva i smrti; koristi `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | šteta; koristi `dmg_health` (šteta nanesena zdravlju), `health` (preostalo zdravlje), `weapon` |
| `player_blind` | zaslijepljeni igrači; koristi `blind_duration` |
| `weapon_fire` | pucnji i bacanja granata; koristi `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | gdje su granate eksplodirale; koristi vlastite `x`, `y`, `z` događaja (događaj nema ime mjesta za tu točku, samo za bacača) |
| `bomb_planted` | postavljanje; koristi `which_bomb_zone` i mjesto postavljača, te `site` (broj entiteta zone) |
| `bomb_defused` | deaktivacija |
| `bomb_exploded` | kad je bomba eksplodirala: vrijeme retka `explode` |
| `round_freeze_end` | gdje svaka runda počinje |
| `round_prestart` | gdje završava vrijeme nakon odlučene runde |
| `round_announce_match_start` | gdje počinje živi meč |

## Dvije činjenice o demo snimkama koje odlučuju kako se čitaju {#two-facts-about-demos-that-decide-how-they-are-read}

- **Meč može biti podijeljen na datoteke**, a imena datoteka ne govore kojim redoslijedom idu. Broj rundi (`total_rounds_played`) se nastavlja kroz njih, i obično i sat poslužitelja, pa se dijelovi mogu poredati prema onome što sadrže.
- **Snimka može početi prije meča**: zagrijavanje, ponovno pokretanje, runda s nožem. Meč počinje na **zadnjem** `round_announce_match_start` u datoteci; prije njega sve se izostavlja, a zagrijavanje se izostavlja svuda.
