---
title: Čtení dema
nav_order: 5
lang: "cs"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Čtení dema {#reading-a-demo}

Co se vytáhne z jednoho souboru `.dem`, dřív než se cokoli interpretuje. Kód:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Dema CS2 je záznam samotného serveru (SourceTV): každý hráč, každý takt, 64
taktů za sekundu (`TICKRATE = 64`). Čte se pomocí
[demoparser2](https://github.com/LaihoE/demoparser) ve třech voláních a výsledek
se ponechá tak, jak přichází, v `RawPart`:

| Pole | Obsahuje |
|---|---|
| `path` | soubor |
| `map` | `map_name` z hlavičky dema (`de_x`); prázdné, když hlavička žádný nemá |
| `samples` | jeden řádek na hráče a vzorkovaný takt: hráč a pravidlová pole níže, plus `tick`, `steamid`, `name` |
| `events` | název události -> její řádky, s poli hráčů s předponou `user_`, `attacker_`, `assister_`, jak je parser pojmenovává |

Nic v `demo.py` nerozhoduje, co je kolo, ani kdo ho vyhrál; to je
[Sestavení zápasu](building-matches.md).

## Vzorkované takty {#the-sampled-ticks}

`parse_ticks` se žádá o takty `0, N, 2N, ...` až do 4 000 000 (`LAST_TICK`,
daleko za jakýkoli zápas - 17 hodin při 64 taktech za sekundu), kde *N* je
`--every` (výchozí 8). Parser se zastaví na konci dema. Každý hráč přítomný v
daném vzorkovaném taktu dá jeden řádek, ať žije, je mrtvý, dívá se, nebo je
trenér; filtrování přichází později.

Krok vzorkování důležitý je i nad rámec hustoty teplotní mapy: okamžik, kdy je
kolo rozhodnuto, se čte z těchto vzorků (viz
[Sestavení zápasu](building-matches.md#rounds)), takže časy konců kol jsou přesné
na jeden krok (1/8 s ve výchozím nastavení).

### Pole hráče {#player-fields}

| Vlastnost | Stane se |
|---|---|
| `X`, `Y`, `Z` | pozice v herních jednotkách (palce), Z nahoru. demoparser2 dává počátek hráče, tj. nohy. |
| `yaw`, `pitch` | směr pohledu (stupně), převedený na jednotkový vektor |
| `health`, `armor_value` | zdraví, pancíř |
| `team_num` | strana: 2 = T, 3 = CT; cokoli jiného (diváci, 0, 1) není strana |
| `team_clan_name` | název týmu, jak ho server ukazuje, používá se k pojmenování týmů |
| `active_weapon_name` | držená zbraň, jak ji hra pojmenuje (`AK-47`, `Karambit`) |
| `is_alive` | zda hráč žije - jen živí hráči se stanou pozicemi |
| `last_place_name` | název místa na mapě (`BombsiteA`) |
| `balance` | peníze |
| `current_equip_value` | hodnota toho, co hráč nese |

### Pole pravidel hry {#game-rules-fields}

Čtou se společně, jednou na řádek hráče (pro každého jsou stejná v daném
taktu):

| Vlastnost | K čemu slouží |
|---|---|
| `game_time` | hodiny serveru, v sekundách |
| `total_rounds_played` | počet kol, který pokračuje napříč soubory zápasu |
| `round_win_status` | kdo právě odehrané kolo vyhrál: 1 remíza, 2 T, 3 CT |
| `round_win_reason` | jak (`CSRoundEndReason` hry) |
| `team_rounds_total` | skóre každé strany |
| `is_warmup_period` | rozcvička se všude vynechává |
| `is_freeze_period` | čas zmrazení se z pozic vynechává |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | probíhající prodloužení, 0 v řádné hře: kola prodloužení nejsou pistolová kola (parser pro to nemá kratší název) |

## Události {#the-events}

Každá událost níže se čte, když ji dema deklaruje (`list_game_events`), s
`X`, `Y`, `Z`, `team_num`, `last_place_name` a `which_bomb_zone` (bombová zóna,
ve které hráč stojí: 0 žádná, 1 A, 2 B) pro každého hráče, kterého událost
jmenuje, a `total_rounds_played` a `is_warmup_period` hry v tom taktu:

| Událost | Stane se |
|---|---|
| `player_death` | zabití a smrti; používá `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | poškození; používá `dmg_health` (poškození způsobené zdraví), `health` (zdraví, které zbylo), `weapon` |
| `player_blind` | oslepení hráči; používá `blind_duration` |
| `weapon_fire` | výstřely a hody granátů; používá `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | kde granáty vybuchly; používá vlastní `x`, `y`, `z` události (událost nemá název místa pro ten bod, jen hodícího) |
| `bomb_planted` | položení; používá `which_bomb_zone` a místo plantéra a `site` (číslo entity zóny) |
| `bomb_defused` | deaktivace |
| `bomb_exploded` | kdy bomba vybuchla: čas řádku `explode` |
| `round_freeze_end` | kde každé kolo začíná |
| `round_prestart` | kde končí čas po rozhodnutém kole |
| `round_announce_match_start` | kde začíná živý zápas |

## Dvě fakta o dem, která určují, jak se čtou {#two-facts-about-demos-that-decide-how-they-are-read}

- **Zápas může být rozdělen mezi více souborů** a názvy souborů neříkají jejich
  pořadí. Počet kol (`total_rounds_played`) pokračuje napříč nimi a obvykle
  i herní hodiny serveru, takže části se dají seřadit podle toho, co obsahují.
- **Záznam může začít před zápasem**: rozcvička, restart, kolo nožů. Zápas začíná
  u **posledního** `round_announce_match_start` v souboru; před ním se vše
  vynechá a rozcvička se vynechává všude.
