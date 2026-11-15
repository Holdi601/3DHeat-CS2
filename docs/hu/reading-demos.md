---
title: "Demó beolvasása"
nav_order: 5
lang: "hu"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Demó beolvasása {#reading-a-demo}

Ami egy `.dem` fájlból kikerül, mielőtt bármit értelmeznénk. Kód:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

A CS2-demó a szerver saját felvétele (SourceTV): minden játékos, minden tick, másodpercenként 64 tick (`TICKRATE = 64`).
A [demoparser2](https://github.com/LaihoE/demoparser) három hívással olvassa be, és az eredmény úgy marad meg, ahogy
jön, egy `RawPart`-ban:

| Mező | Tartalma |
|---|---|
| `path` | a fájl |
| `map` | a `map_name` a demó fejlécéből (`de_x`); üres, ha a fejlécben nincs |
| `samples` | egy sor játékosonként és mintavételezett tickenként: az alábbi játékos- és szabálymezők, plusz `tick`, `steamid`, `name` |
| `events` | eseménynév -> a sorai, a játékosok mezőivel, `user_`, `attacker_`, `assister_` előtaggal, ahogy a parser nevezi |

A `demo.py` semmit nem dönt el arról, mi a kör vagy ki nyert; ez a [Meccs felépítése](building-matches.md).

## A mintavételezett tickek {#the-sampled-ticks}

A `parse_ticks` a `0, N, 2N, ...` tickeket kéri, legfeljebb 4 000 000-ig (`LAST_TICK`, ami jóval túl van bármely meccsen -
17 óra 64 tick/másodperc mellett), ahol *N* a `--every` (alapértelmezetten 8). A parser a demó végén áll meg. Minden játékos,
aki egy mintavételezett ticknél jelen van, egy sort ad - élő, halott, néző vagy edző -, a szűrés később történik.

A mintavételezési lépés a hőtérkép sűrűségén túl is számít: a kör eldőlésének pillanata ezekből a mintákból olvasódik (lásd
[Meccs felépítése](building-matches.md#rounds)), így a körök végének ideje egy lépés pontosságú (alapértelmezetten 1/8 s).

### Játékos-mezők {#player-fields}

| Tulajdonság | Ebből lesz |
|---|---|
| `X`, `Y`, `Z` | a pozíció, játékegységekben (hüvelyk), Z felfelé. A demoparser2 a játékos origóját adja, vagyis a talpát. |
| `yaw`, `pitch` | a nézési irány (fokban), egységvektorrá alakítva |
| `health`, `armor_value` | életerő, páncél |
| `team_num` | az oldal: 2 = T, 3 = CT; minden más (nézők, 0, 1) nincs oldalon |
| `team_clan_name` | a csapat neve, ahogy a szerver mutatja; a csapatok elnevezéséhez |
| `active_weapon_name` | a kézben tartott fegyver, ahogy a játék nevezi (`AK-47`, `Karambit`) |
| `is_alive` | él-e a játékos - csak az élő játékosokból lesz pozíció |
| `last_place_name` | a pálya saját helynéve (`BombsiteA`) |
| `balance` | pénz |
| `current_equip_value` | a játékos által hordott felszerelés értéke |

### Játékszabály-mezők {#game-rules-fields}

Mellékesen olvassuk, játékosonként egyszer (mindenkinél ugyanazok egy ticken):

| Tulajdonság | Mire használjuk |
|---|---|
| `game_time` | a szerver órája, másodpercben |
| `total_rounds_played` | a körszámláló, amely a meccs fájljain át folytatódik |
| `round_win_status` | ki nyerte az éppen lejátszott kört: 1 döntetlen, 2 T, 3 CT |
| `round_win_reason` | hogyan (a játék `CSRoundEndReason`-je) |
| `team_rounds_total` | az oldalak állása |
| `is_warmup_period` | a bemelegítés mindenhol ki van hagyva |
| `is_freeze_period` | a freeze time ki van hagyva a pozíciókból |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | a játszott hosszabbítás, 0 a szabályos játékban: a hosszabbítási körök nem pisztolykörök (a parsernek nincs rövidebb neve rá) |

## Az események {#the-events}

Az alábbi események mindegyikét akkor olvassuk be, amikor a demó deklarálja (`list_game_events`), és minden játékosnál,
akit az esemény megnevez, az `X`, `Y`, `Z`, `team_num`, `last_place_name` és `which_bomb_zone` (az a bombazóna, amelyben a
játékos áll: 0 nincs, 1 A, 2 B) mezőkkel, a játék `total_rounds_played` és `is_warmup_period` értékével az adott ticknél:

| Esemény | Ebből lesz |
|---|---|
| `player_death` | gyilkosságok és halálok; a `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` mezőkkel |
| `player_hurt` | sebzés; a `dmg_health` (az életerőben okozott sebzés), `health` (a maradék életerő), `weapon` mezőkkel |
| `player_blind` | megvakított játékosok; a `blind_duration`-nel |
| `weapon_fire` | lövések és gránátdobások; a `weapon`-nel |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | hol robbantak a gránátok; az esemény saját `x`, `y`, `z` mezőjével (az eseménynek nincs helynév ahhoz a ponthoz, csak a dobóé) |
| `bomb_planted` | a lerakás; a lerakó `which_bomb_zone`-jával és helyével, valamint a `site`-tal (a zóna entitásszáma) |
| `bomb_defused` | a hatástalanítás |
| `bomb_exploded` | amikor a bomba felrobbant: a `explode` sor ideje |
| `round_freeze_end` | ahol minden kör kezdődik |
| `round_prestart` | ahol az eldöntött kör utáni idő véget ér |
| `round_announce_match_start` | ahol az élő meccs kezdődik |

## Két tény a demókról, amelyek eldöntik, hogyan olvassuk őket {#two-facts-about-demos-that-decide-how-they-are-read}

- **Egy meccs több fájlra lehet osztva**, és a fájlok nevei nem mondják meg a sorrendjüket. A körszámláló
  (`total_rounds_played`) átível rajtuk, és általában a szerver órája is, így a részek abból rendezhetők, amit
  tartalmaznak.
- **A felvétel a meccs előtt is kezdődhet**: bemelegítés, újraindítás, kés-kör. A meccs a fájl **utolsó**
  `round_announce_match_start`-jánál kezdődik; az előtte lévő mindent kihagyjuk, és a bemelegítés mindenhol kimarad.
