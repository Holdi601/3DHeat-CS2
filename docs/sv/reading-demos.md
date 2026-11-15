---
title: "Läsa en demo"
nav_order: 5
lang: "sv"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Läsa en demo {#reading-a-demo}

Vad som tas ur en `.dem`-fil, innan något tolkas. Kod:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

En CS2-demo är serverns egen inspelning (SourceTV): varje spelare, varje tick, 64 tick per sekund
(`TICKRATE = 64`). Den läses med [demoparser2](https://github.com/LaihoE/demoparser) i tre anrop, och
resultatet behålls så som det kommer, i en `RawPart`:

| Fält | Innehåll |
|---|---|
| `path` | filen |
| `map` | `map_name` från demohuvudet (`de_x`); tomt om huvudet saknar det |
| `samples` | en rad per spelare per samplat tick: spelar- och regelfälten nedan, plus `tick`, `steamid`, `name` |
| `events` | händelsenamn -> dess rader, med spelarnas fält prefixade `user_`, `attacker_`, `assister_` så som parsern namnger dem |

Ingenting i `demo.py` avgör vad en runda är eller vem som vann; det är [Bygga en match](building-matches.md).

## De samplade ticksen {#the-sampled-ticks}

`parse_ticks` begärs för ticks `0, N, 2N, ...` upp till 4 000 000 (`LAST_TICK`, långt bortom någon match -
17 timmar vid 64 tick per sekund), där *N* är `--every` (standard 8). Parsern stannar vid demons slut. Varje
spelare som finns vid ett samplat tick ger en rad, oavsett om den lever, är död, åskådar eller är tränare;
filtrering sker senare.

Samplingssteget betyder mer än tätheten på värmekartan: ögonblicket en runda avgörs läses från dessa sampel
(se [Bygga en match](building-matches.md#rounds)), så rundornas sluttider är exakta till ett steg (1/8 s som
standard).

### Spelarfält {#player-fields}

| Egenskap | Blir |
|---|---|
| `X`, `Y`, `Z` | positionen, i spelets enheter (tum), Z uppåt. demoparser2 ger spelarens ursprung, alltså fötterna. |
| `yaw`, `pitch` | blickriktningen (grader), omvandlad till en enhetsvektor |
| `health`, `armor_value` | hälsa, pansar |
| `team_num` | sidan: 2 = T, 3 = CT; allt annat (åskådare, 0, 1) är ingen sida |
| `team_clan_name` | lagets namn så som servern visar det, används för att namnge lagen |
| `active_weapon_name` | vapnet i handen, så som spelet namnger det (`AK-47`, `Karambit`) |
| `is_alive` | om spelaren lever - bara levande spelare blir positioner |
| `last_place_name` | kartans egna platsnamn (`BombsiteA`) |
| `balance` | pengar |
| `current_equip_value` | värdet av det spelaren bär |

### Regelfält {#game-rules-fields}

Läses tillsammans, en gång per spelarrad (de är desamma för alla vid ett tick):

| Egenskap | Används till |
|---|---|
| `game_time` | serverns klocka, i sekunder |
| `total_rounds_played` | rundräkningen, som fortsätter över en matchs filer |
| `round_win_status` | vem som vann rundan just spelad: 1 oavgjort, 2 T, 3 CT |
| `round_win_reason` | hur (spelets `CSRoundEndReason`) |
| `team_rounds_total` | varje sidas ställning |
| `is_warmup_period` | uppvärmningen utelämnas överallt |
| `is_freeze_period` | freeze time utelämnas ur positionerna |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | den övertid som spelas, 0 i ordinarie tid: övertidsrundor är inga pistolrundor (parsern har inget kortare namn för den) |

## Händelserna {#the-events}

Varje händelse nedan läses när demon deklarerar den (`list_game_events`), med `X`, `Y`, `Z`, `team_num`,
`last_place_name` och `which_bomb_zone` (bombzonen spelaren står i: 0 ingen, 1 A, 2 B) för varje spelare
händelsen namnger, och `total_rounds_played` och `is_warmup_period` för spelet vid det ticket:

| Händelse | Blir |
|---|---|
| `player_death` | kills och deaths; använder `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | skada; använder `dmg_health` (skada på hälsan), `health` (hälsa kvar), `weapon` |
| `player_blind` | bländade spelare; använder `blind_duration` |
| `weapon_fire` | skott och granatkast; använder `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | var granater gick av; använder händelsens egna `x`, `y`, `z` (händelsen har inget platsnamn för den punkten, bara kastarens) |
| `bomb_planted` | planteringen; använder planterarens `which_bomb_zone` och plats, och `site` (zonens entitetsnummer) |
| `bomb_defused` | desarmeringen |
| `bomb_exploded` | när bomben gick av: tiden för `explode`-raden |
| `round_freeze_end` | var varje runda startar |
| `round_prestart` | var tiden efter en avgjord runda slutar |
| `round_announce_match_start` | var den levande matchen startar |

## Två fakta om demos som avgör hur de läses {#two-facts-about-demos-that-decide-how-they-are-read}

- **En match kan delas över filer**, och filernas namn säger inte deras ordning. Rundräkningen
  (`total_rounds_played`) fortsätter över dem, och oftast serverns klocka också, så delarna kan sättas i
  ordning utifrån vad de innehåller.
- **En inspelning kan börja före matchen**: uppvärmning, en omstart, en knivrunda. Matchen startar vid den
  **sista** `round_announce_match_start` i en fil; före den lämnas allt utanför, och uppvärmningen lämnas
  utanför överallt.
