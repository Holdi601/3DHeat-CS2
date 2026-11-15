---
title: Een demo lezen
nav_order: 5
lang: "nl"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Een demo lezen {#reading-a-demo}

Wat er uit één `.dem`-bestand wordt gehaald, voordat er iets wordt uitgelegd. Code: [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Een CS2-demo is de eigen opname van de server (SourceTV): elke speler, elk tick, 64 ticks per seconde (`TICKRATE = 64`). Hij wordt gelezen met [demoparser2](https://github.com/LaihoE/demoparser) in drie aanroepen, en het resultaat wordt bewaard zoals het komt, in een `RawPart`:

| Veld | Bevat |
|---|---|
| `path` | het bestand |
| `map` | `map_name` uit de header van de demo (`de_x`); leeg als de header er geen heeft |
| `samples` | één rij per speler per bemonsterd tick: de velden van de speler en van de spelregels hieronder, plus `tick`, `steamid`, `name` |
| `events` | gebeurtenisnaam -> zijn rijen, met de velden van de spelers voorafgegaan door `user_`, `attacker_`, `assister_` zoals de parser ze noemt |

Niets in `demo.py` bepaalt wat een ronde is of wie hem won; dat is [Een wedstrijd opbouwen](building-matches.md).

## De bemonsterde ticks {#the-sampled-ticks}

`parse_ticks` wordt gevraagd om ticks `0, N, 2N, ...` tot 4.000.000 (`LAST_TICK`, ver voorbij elke wedstrijd - 17 uur bij 64 ticks per seconde), waarbij *N* de `--every` is (standaard 8). De parser stopt bij het einde van de demo. Elke speler die aanwezig is op een bemonsterd tick, geeft één rij, of hij nu leeft, dood is, toeschouwer is of coach; het filteren gebeurt later.

De bemonsteringsstap is meer dan de dichtheid van de heatmap: het moment waarop een ronde wordt beslist, wordt uit deze monsters gelezen (zie [Een wedstrijd opbouwen](building-matches.md#rondes)), dus de eindtijden van rondes zijn nauwkeurig tot één stap (standaard 1/8 s).

### Spelervelden {#player-fields}

| Eigenschap | Wordt |
|---|---|
| `X`, `Y`, `Z` | de positie, in de eenheden van de game (inches), Z omhoog. demoparser2 geeft de oorsprong van de speler, dat wil zeggen de voeten. |
| `yaw`, `pitch` | de kijkrichting (graden), omgezet in een eenheidsvector |
| `health`, `armor_value` | gezondheid, pantser |
| `team_num` | de kant: 2 = T, 3 = CT; al het andere (toeschouwers, 0, 1) is geen kant |
| `team_clan_name` | de naam van het team zoals de server die toont, gebruikt om de teams te benoemen |
| `active_weapon_name` | het wapen in de hand, zoals de game het noemt (`AK-47`, `Karambit`) |
| `is_alive` | of de speler leeft - alleen levende spelers worden posities |
| `last_place_name` | de eigen plaatsnaam van de map (`BombsiteA`) |
| `balance` | geld |
| `current_equip_value` | de waarde van wat de speler draagt |

### Spelregelvelden {#game-rules-fields}

Mee gelezen, één keer per spelerrij (ze zijn voor iedereen op een tick gelijk):

| Eigenschap | Gebruikt voor |
|---|---|
| `game_time` | de klok van de server, in seconden |
| `total_rounds_played` | het aantal rondes, dat doorloopt over de bestanden van een wedstrijd heen |
| `round_win_status` | wie de net gespeelde ronde won: 1 gelijkspel, 2 T, 3 CT |
| `round_win_reason` | hoe (de `CSRoundEndReason` van de game) |
| `team_rounds_total` | de score van elke kant |
| `is_warmup_period` | warmup wordt overal weggelaten |
| `is_freeze_period` | freeze time wordt uit de posities weggelaten |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | de overtime die wordt gespeeld, 0 in de reguliere tijd: overtime-rondes zijn geen pistoolrondes (de parser heeft geen kortere naam ervoor) |

## De gebeurtenissen {#the-events}

Elke gebeurtenis hieronder wordt gelezen wanneer de demo haar aankondigt (`list_game_events`), met `X`, `Y`, `Z`, `team_num`, `last_place_name` en `which_bomb_zone` (de bomzone waarin de speler staat: 0 geen, 1 A, 2 B) voor elke speler die de gebeurtenis noemt, en `total_rounds_played` en `is_warmup_period` van het spel op dat tick:

| Gebeurtenis | Wordt |
|---|---|
| `player_death` | kills en doden; gebruikt `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | schade; gebruikt `dmg_health` (aan gezondheid toegebrachte schade), `health` (overgebleven gezondheid), `weapon` |
| `player_blind` | geflitste spelers; gebruikt `blind_duration` |
| `weapon_fire` | schoten en granaatworpen; gebruikt `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | waar granaten afgingen; gebruikt de eigen `x`, `y`, `z` van de gebeurtenis (de gebeurtenis heeft geen plaatsnaam voor dat punt, alleen die van de gooier) |
| `bomb_planted` | de plant; gebruikt de `which_bomb_zone` en plek van de planter, en `site` (het entiteitsnummer van de zone) |
| `bomb_defused` | de defuse |
| `bomb_exploded` | wanneer de bom afging: de tijd van de `explode`-rij |
| `round_freeze_end` | waar elke ronde begint |
| `round_prestart` | waar de tijd na een beslist ronde eindigt |
| `round_announce_match_start` | waar de live-wedstrijd begint |

## Twee feiten over demo's die bepalen hoe ze worden gelezen {#two-facts-about-demos-that-decide-how-they-are-read}

- **Een wedstrijd kan over meerdere bestanden verdeeld zijn**, en de namen van de bestanden zeggen niet in welke volgorde ze horen. Het aantal rondes (`total_rounds_played`) loopt door over de bestanden heen, en meestal ook de klok van de server, dus de delen kunnen worden geordend op wat ze bevatten.
- **Een opname kan beginnen vóór de wedstrijd**: warmup, een herstart, een knife-ronde. De wedstrijd begint bij de **laatste** `round_announce_match_start` in een bestand; ervoor wordt alles weggelaten, en warmup wordt overal weggelaten.
