---
title: Citirea unui demo
nav_order: 5
lang: "ro"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Citirea unui demo {#reading-a-demo}

Ce se scoate dintr-un fișier `.dem`, înainte ca orice să fie interpretat. Cod:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Un demo CS2 este înregistrarea făcută de server (SourceTV): fiecare jucător, la fiecare tick,
64 de tick-uri pe secundă (`TICKRATE = 64`). Este citit cu
[demoparser2](https://github.com/LaihoE/demoparser) în trei apeluri, iar rezultatul este
păstrat așa cum vine, într-un `RawPart`:

| Câmp | Conține |
|---|---|
| `path` | fișierul |
| `map` | `map_name` din antetul demo-ului (`de_x`); gol dacă antetul nu are |
| `samples` | un rând pentru fiecare jucător la fiecare tick eșantionat: câmpurile jucătorului și ale regulilor de mai jos, plus `tick`, `steamid`, `name` |
| `events` | numele evenimentului -> rândurile sale, cu câmpurile jucătorilor prefixate cu `user_`, `attacker_`, `assister_` cum le numește parserul |

Nimic din `demo.py` nu decide ce este o rundă sau cine a câștigat; asta este
[Cum se construiește un meci](building-matches.md).

## Tick-urile eșantionate {#the-sampled-ticks}

`parse_ticks` este rugat pentru tick-urile `0, N, 2N, ...` până la 4.000.000 (`LAST_TICK`,
mult peste orice meci - 17 ore la 64 de tick-uri pe secundă), unde *N* este `--every`
(implicit 8). Parserul se oprește la sfârșitul demo-ului. Fiecare jucător prezent la un tick
eșantionat dă un rând, fie că este în viață, mort, spectator sau antrenor; filtrarea se face mai târziu.

Pasul de eșantionare contează mai mult decât densitatea hărții termice: momentul în care o
rundă este decisă se citește din aceste eșantioane (vezi
[Cum se construiește un meci](building-matches.md#rounds)), deci timpii de sfârșit ai rundelor
sunt exacți până la un pas (1/8 s implicit).

### Câmpurile jucătorului {#player-fields}

| Proprietate | Devine |
|---|---|
| `X`, `Y`, `Z` | poziția, în unitățile jocului (inchi), Z în sus. demoparser2 dă originea jucătorului, adică picioarele. |
| `yaw`, `pitch` | direcția privirii (grade), transformată într-un vector unitar |
| `health`, `armor_value` | sănătatea, armura |
| `team_num` | partea: 2 = T, 3 = CT; orice altceva (spectatori, 0, 1) nu este parte |
| `team_clan_name` | numele echipei așa cum îl arată serverul, folosit pentru a numi echipele |
| `active_weapon_name` | arma ținută, așa cum o numește jocul (`AK-47`, `Karambit`) |
| `is_alive` | dacă jucătorul este în viață - doar jucătorii în viață devin poziții |
| `last_place_name` | numele locului de pe hartă (`BombsiteA`) |
| `balance` | banii |
| `current_equip_value` | valoarea a ceea ce duce jucătorul |

### Câmpurile regulilor jocului {#game-rules-fields}

Citite împreună cu acestea, o dată pentru fiecare rând de jucător (sunt aceleași pentru
toată lumea la un tick):

| Proprietate | Folosit pentru |
|---|---|
| `game_time` | ceasul serverului, în secunde |
| `total_rounds_played` | numărul rundelor, care continuă peste fișierele unui meci |
| `round_win_status` | cine a câștigat runda tocmai jucată: 1 egalitate, 2 T, 3 CT |
| `round_win_reason` | cum (`CSRoundEndReason` al jocului) |
| `team_rounds_total` | scorul fiecărei părți |
| `is_warmup_period` | încălzirea este lăsată afară peste tot |
| `is_freeze_period` | timpul de îngheț este lăsat afară din poziții |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | prelungirea care se joacă, 0 în regulament: rundele de prelungire nu sunt runde de pistol (parserul nu are un nume mai scurt) |

## Evenimentele {#the-events}

Fiecare eveniment de mai jos este citit când demo-ul îl declară (`list_game_events`), cu
`X`, `Y`, `Z`, `team_num`, `last_place_name` și `which_bomb_zone` (zona bombei în care
stă jucătorul: 0 niciuna, 1 A, 2 B) pentru fiecare jucător numit de eveniment, și
`total_rounds_played` și `is_warmup_period` ale jocului la acel tick:

| Eveniment | Devine |
|---|---|
| `player_death` | eliminări și morți; folosește `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | daune; folosește `dmg_health` (daune asupra sănătății), `health` (sănătatea rămasă), `weapon` |
| `player_blind` | jucători orbiți de flash; folosește `blind_duration` |
| `weapon_fire` | focuri și aruncări de grenade; folosește `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | unde au explodat grenadele; folosesc `x`, `y`, `z` proprii ale evenimentului (evenimentul nu are nume de loc pentru acel punct, doar pentru aruncător) |
| `bomb_planted` | plantarea; folosește `which_bomb_zone` și locul plantatorului și `site` (numărul de entitate al zonei) |
| `bomb_defused` | dezamorsarea |
| `bomb_exploded` | când a explodat bomba: timpul rândului `explode` |
| `round_freeze_end` | unde începe fiecare rundă |
| `round_prestart` | unde se termină timpul de după o rundă decisă |
| `round_announce_match_start` | unde începe meciul live |

## Două fapte despre demo-uri care decid cum sunt citite {#two-facts-about-demos-that-decide-how-they-are-read}

- **Un meci poate fi împărțit pe mai multe fișiere**, iar numele fișierelor nu spun ordinea
  lor. Numărul rundelor (`total_rounds_played`) continuă peste ele, și de obicei și ceasul
  serverului, deci părțile pot fi puse în ordine după ce conțin.
- **O înregistrare poate începe înainte de meci**: încălzire, o repornire, o rundă cu cuțitul.
  Meciul începe la **ultimul** `round_announce_match_start` dintr-un fișier; înainte de el
  totul este lăsat afară, iar încălzirea este lăsată afară peste tot.
