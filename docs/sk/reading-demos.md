---
title: Čítanie dema
nav_order: 5
lang: "sk"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Čítanie dema {#reading-a-demo}

Čo sa vyberie z jedného súboru `.dem`, skôr než sa čokoľvek interpretuje. Kód:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Demo CS2 je nahrávka servera (SourceTV): každý hráč, každý tik, 64 tikov za
sekundu (`TICKRATE = 64`). Číta sa pomocou
[demoparser2](https://github.com/LaihoE/demoparser) v troch volaniach a výsledok
sa ponechá tak, ako prichádza, v `RawPart`:

| Pole | Obsahuje |
|---|---|
| `path` | súbor |
| `map` | `map_name` z hlavičky dema (`de_x`); prázdne, ak hlavička žiadne nemá |
| `samples` | jeden riadok na hráča a vzorkovaný tik: polia hráča a pravidiel nižšie, plus `tick`, `steamid`, `name` |
| `events` | názov udalosti -> jej riadky, s poľami hráčov s predponami `user_`, `attacker_`, `assister_`, ako ich parser pomenúva |

Nič v `demo.py` nerozhoduje, čo je kolo, ani kto ho vyhral; to je
[Zostavenie zápasu](building-matches.md).

## Vzorkované tiky {#the-sampled-ticks}

`parse_ticks` sa žiada o tiky `0, N, 2N, ...` až do 4 000 000 (`LAST_TICK`,
ďaleko za každý zápas - 17 hodín pri 64 tikoch za sekundu), kde *N* je `--every`
(predvolene 8). Parser sa zastaví na konci dema. Každý hráč prítomný vo
vzorkovanom tiku dá jeden riadok, či je živý, mŕtvy, divák alebo tréner;
filtrovanie sa deje neskôr.

Krok vzorkovania má význam nielen pre hustotu heatmapy: okamih rozhodnutia kola
sa číta z týchto vzoriek (pozrite [Zostavenie zápasu](building-matches.md#rounds)),
takže časy konca kôl sú presné na jeden krok (1/8 s pri predvolenom nastavení).

### Polia hráča {#player-fields}

| Vlastnosť | Stane sa z nej |
|---|---|
| `X`, `Y`, `Z` | pozícia v herných jednotkách (palce), Z nahor. demoparser2 dáva začiatok hráča, teda chodidlá. |
| `yaw`, `pitch` | smer pohľadu (stupne), prevedený na jednotkový vektor |
| `health`, `armor_value` | zdravie, pancier |
| `team_num` | strana: 2 = T, 3 = CT; čokoľvek iné (diváci, 0, 1) nie je strana |
| `team_clan_name` | názov tímu tak, ako ho ukazuje server, používa sa na pomenovanie tímov |
| `active_weapon_name` | držaná zbraň, tak ako ju hra pomenúva (`AK-47`, `Karambit`) |
| `is_alive` | či hráč žije - na pozície sa menia iba živí hráči |
| `last_place_name` | vlastný názov miesta mapy (`BombsiteA`) |
| `balance` | peniaze |
| `current_equip_value` | hodnota toho, čo hráč nesie |

### Polia herných pravidiel {#game-rules-fields}

Čítajú sa spolu, raz na riadok hráča (sú pre všetkých rovnaké v tiku):

| Vlastnosť | Na čo sa používa |
|---|---|
| `game_time` | hodiny servera, v sekundách |
| `total_rounds_played` | počet kôl, ktorý pokračuje naprieč súbormi zápasu |
| `round_win_status` | kto vyhral práve odohrané kolo: 1 remíza, 2 T, 3 CT |
| `round_win_reason` | ako (`CSRoundEndReason` hry) |
| `team_rounds_total` | skóre každej strany |
| `is_warmup_period` | rozcvička sa všade vynecháva |
| `is_freeze_period` | čas zmrazenia sa vynecháva z pozícií |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | predĺženie, ktoré sa hrá; 0 v riadnom hraní: kolá predĺženia nie sú pistolové kolá (parser pre to nemá kratší názov) |

## Udalosti {#the-events}

Každá udalosť nižšie sa číta, keď ju demo deklaruje (`list_game_events`), s
`X`, `Y`, `Z`, `team_num`, `last_place_name` a `which_bomb_zone` (bombová zóna, v
ktorej hráč stojí: 0 žiadna, 1 A, 2 B) pre každého hráča, ktorého udalosť
pomenúva, a `total_rounds_played` a `is_warmup_period` hry v tom tiku:

| Udalosť | Stane sa z nej |
|---|---|
| `player_death` | zabitia a smrti; používa `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | poškodenie; používa `dmg_health` (poškodenie zdravia), `health` (zostávajúce zdravie), `weapon` |
| `player_blind` | oslepení hráči; používa `blind_duration` |
| `weapon_fire` | výstrely a hody granátov; používa `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | kde granáty vybuchli; používa vlastné `x`, `y`, `z` udalosti (udalosť nemá názov miesta pre ten bod, iba pre hádzajúceho) |
| `bomb_planted` | položenie; používa `which_bomb_zone` a miesto kladača a `site` (číslo entity zóny) |
| `bomb_defused` | zneškodnenie |
| `bomb_exploded` | kedy bomba vybuchla: čas riadku `explode` |
| `round_freeze_end` | kde každé kolo začína |
| `round_prestart` | kde končí čas po rozhodnutom kole |
| `round_announce_match_start` | kde sa začína živý zápas |

## Dve fakty o demách, ktoré určujú, ako sa čítajú {#two-facts-about-demos-that-decide-how-they-are-read}

- **Zápas sa môže rozdeliť na viac súborov** a názvy súborov nehovoria o ich
  poradí. Počet kôl (`total_rounds_played`) pokračuje naprieč nimi a zvyčajne aj
  hodiny servera, takže časti sa dajú zoradiť podľa toho, čo obsahujú.
- **Nahrávka sa môže začať pred zápasom**: rozcvička, reštart, nožové kolo.
  Zápas sa začína pri **poslednej** udalosti `round_announce_match_start` v
  súbore; pred ňou sa všetko vynecháva a rozcvička sa vynecháva všade.
