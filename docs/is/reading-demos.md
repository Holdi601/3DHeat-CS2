---
title: "Að lesa demo"
nav_order: 5
lang: "is"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Að lesa demo {#reading-a-demo}

Hvað er tekið úr einni `.dem`-skrá, áður en nokkuð er túlkað. Kóði:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

CS2-demo er eigin upptaka þjónsins (SourceTV): hver leikmaður, hvert
tikk, 64 tikk á sekúndu (`TICKRATE = 64`). Hún er lesin með
[demoparser2](https://github.com/LaihoE/demoparser) í þremur köllum, og
niðurstaðan er geymd eins og hún kemur, í `RawPart`:

| Reitur | Geymir |
|---|---|
| `path` | skrána |
| `map` | `map_name` úr haus demo-skrárinnar (`de_x`); tómt ef haus hefur ekkert |
| `samples` | ein röð fyrir hvern leikmann í hverju sýnatekna tikki: reitir leikmanns og leikreglna hér að neðan, plús `tick`, `steamid`, `name` |
| `events` | atburðarheiti -> raðir þess, með reitum leikmannanna forskeyttum `user_`, `attacker_`, `assister_` eins og þáttarinn nefnir þá |

Ekkert í `demo.py` ákveður hvað lota er eða hver vann; það er
[Að smíða leik](building-matches.md).

## Sýnatekin tikk {#the-sampled-ticks}

`parse_ticks` er beðið um tikk `0, N, 2N, ...` upp að 4.000.000 (`LAST_TICK`,
langt umfram hvaða leik sem er - 17 klukkustundir á 64 tikkum á sekúndu), þar sem *N* er `--every`
(sjálfgefið 8). Þáttarinn stoppar við enda demo-skrárinnar. Hver leikmaður sem er til staðar í
sýnatekna tikkinu gefur eina röð, hvort sem hann er á lífi, dáinn, áhorfandi eða þjálfari;
síun gerist síðar.

Sýnatökubilið skiptir máli umfram þéttleika hitakortsins: augnablikið sem lota
er ákvörðuð er lesið úr þessum sýnum (sjá
[Að smíða leik](building-matches.md#rounds)), svo lokatímar lota eru
nákvæmir upp á eitt bil (1/8 s sjálfgefið).

### Reitir leikmanns {#player-fields}

| Eiginleiki | Verður |
|---|---|
| `X`, `Y`, `Z` | staðan, í einingum leiksins (tommum), Z upp. demoparser2 gefur upphafspunkt leikmannsins, þ.e. fæturna. |
| `yaw`, `pitch` | sjónstefnan (gráður), breytt í einingarvigur |
| `health`, `armor_value` | líf, brynja |
| `team_num` | hliðin: 2 = T, 3 = CT; allt annað (áhorfendur, 0, 1) er engin hlið |
| `team_clan_name` | heiti liðsins eins og þjónninn sýnir það, notað til að nefna liðin |
| `active_weapon_name` | vopnið í hendi, eins og leikurinn nefnir það (`AK-47`, `Karambit`) |
| `is_alive` | hvort leikmaðurinn er á lífi - aðeins lifandi leikmenn verða að staðsetningum |
| `last_place_name` | eigið staðarheiti kortsins (`BombsiteA`) |
| `balance` | peningar |
| `current_equip_value` | verðmæti þess sem leikmaðurinn ber |

### Reitir leikreglna {#game-rules-fields}

Lesnir samhliða, einu sinni fyrir hverja leikmannaröð (þeir eru eins fyrir alla í einu tikki):

| Eiginleiki | Notaður í |
|---|---|
| `game_time` | klukku þjónsins, í sekúndum |
| `total_rounds_played` | lotutalninguna, sem heldur áfram yfir skrár leiks |
| `round_win_status` | hver vann lotuna sem var að ljúka: 1 jafntefli, 2 T, 3 CT |
| `round_win_reason` | hvernig (`CSRoundEndReason` leiksins) |
| `team_rounds_total` | stöðu hverrar hliðar |
| `is_warmup_period` | upphitun er sleppt alls staðar |
| `is_freeze_period` | frystitíma er sleppt úr staðsetningum |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | framlengingin sem er spiluð, 0 í venjulegum leiktíma: framlengingarlotur eru ekki skammbyssulotur (þáttarinn hefur ekkert styttra heiti fyrir það) |

## Atburðirnir {#the-events}

Hver atburður hér að neðan er lesinn þegar demo-skráin lýsir honum yfir (`list_game_events`), með
`X`, `Y`, `Z`, `team_num`, `last_place_name` og `which_bomb_zone` (sprengjusvæðið
sem leikmaðurinn stendur á: 0 ekkert, 1 A, 2 B) fyrir hvern leikmann sem atburðurinn
nefnir, og `total_rounds_played` og `is_warmup_period` leiksins á því
tikki:

| Atburður | Verður |
|---|---|
| `player_death` | fellingar og dauðsföll; notar `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | skaði; notar `dmg_health` (skaði á lífi), `health` (líf eftir), `weapon` |
| `player_blind` | blindaðir leikmenn; notar `blind_duration` |
| `weapon_fire` | skot og köst handsprengna; notar `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | þar sem handsprengjur sprungu; notar eigin `x`, `y`, `z` atburðarins (atburðurinn hefur ekkert staðarheiti fyrir þann punkt, aðeins kastarans) |
| `bomb_planted` | sprengjusetningin; notar `which_bomb_zone` og stað setjandans, og `site` (einingarnúmer svæðisins) |
| `bomb_defused` | aftengingin |
| `bomb_exploded` | hvenær sprengjan sprakk: tími `explode`-raðarinnar |
| `round_freeze_end` | þar sem hver lota byrjar |
| `round_prestart` | þar sem tíminn eftir ákvarðaða lotu endar |
| `round_announce_match_start` | þar sem lifandi leikurinn byrjar |

## Tvær staðreyndir um demo-skrár sem ráða hvernig þær eru lesnar {#two-facts-about-demos-that-decide-how-they-are-read}

- **Leikur getur verið skiptur í margar skrár**, og nöfn skránna segja ekki
  til um röð þeirra. Lotutalningin (`total_rounds_played`) heldur áfram yfir
  þær, og yfirleitt klukka þjónsins líka, svo hægt er að raða hlutunum út frá
  því sem þeir innihalda.
- **Upptaka getur byrjað fyrir leikinn**: upphitun, endurræsing, hnífalota.
  Leikurinn byrjar við **síðasta** `round_announce_match_start` í
  skrá; allt á undan því er sleppt, og upphitun er sleppt alls staðar.
