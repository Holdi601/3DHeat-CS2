---
title: "Документ меча"
nav_order: 9
lang: "sr"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Документ меча (`<match>.match.json`) {#the-match-document-matchjson}

Један JSON документ по мечу, поред његове табеле: тимови, резултат, свака рунда с њеним исходом, економија, постављање, убиства, клачеви и преживели, и табела резултата сваког играча. То је оно што картица Меч прегледача 3DHeat учитава. Код: `summary()` у [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py); бројеви су дефинисани на [Статистика](statistics.md).

Фајл је у UTF-8, увучен једним размаком, и чува не-ASCII знакове (имена играча и тимова) онакве какви јесу. Времена су секунде, заокружена на три децимале за рунде и на две за убиства и постављање.

## Документ {#the-document}

| Поље | Тип | Шта |
|---|---|---|
| `format` | стринг | увек `heat3d-cs2-match` - по чему читач препознаје фајл |
| `version` | број | `3`. Документ верзије 1 даје `time` постављања у секундама меча; од 2 то су секунде у рунди, као код убиства. 3 додаје поља од `header` и замрзавање у табелу. |
| `match` | стринг | име меча, како су датотеке именоване |
| `map` | стринг | мапа (`de_x`) |
| `demos` | string[] | демо-датотеке од којих је направљен, само називи фајлова, редом меча |
| `teams` | string[] | називи тимова по редоследу појављивања (рунда 1: страна T прва) |
| `score` | објекат | назив тима -> освојене рунде: резултат последње рунде |
| `winner` | стринг или null | тим који је победио меч, где снимак показује крај; null за снимак који се рано завршава, продужетак без панела победе, или нерешено |
| `winnerSource` | стринг или null | како је познат `winner`: `winPanel` (игрин панел победе у мечу), `surrender`, `regulation` (више од половине редовних рунди) |
| `rounds` | object[] | свака комплетна рунда, по редоследу - [испод](#рунде) |
| `incomplete` | number[] | бројеви рунди које је прекинуо крај демоа и које су изостављене |
| `missing` | number[] | бројеви рунди пре прве коју демои садрже: `[1, 2]` кад снимак почиње у рунди 3 |
| `halfLength` | number или null | рунде у редовном полувремену, од места где се стране први пут замене (`12` у формату од 24 рунде); null кад снимак не показује замену |
| `pistolRounds` | number[] | пистол-рунде с којима се рачуна `buy`: рунда 1, и рунда после половине кад је `halfLength` познат; никад рунда продужетка |
| `players` | object[] | табела резултата - [испод](#играчи) |
| `conventions` | објекат | дефиниције иза бројева, [испод](#конвенције) |
| `header` | објекат | заглавље првог демоа како га даје парсер: назив сервера, верзија патча, верзија демоа, мапа |
| `profiles` | објекат | Steam ID -> оно што се за играча не мења током меча: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (последње виђено) |
| `playerInfo` | object[] | сваки играч којег демои наводе, укључујући тренере и кастере: Steam ID, име, број тима |
| `skins`, `itemDrops` | object[] | скинови оружја и испадања предмета, где их демо има (турнирски демои из преноса их немају) |
| `chat` | object[] | сваки ред ћаскања у мечу: време, рунда, играч, страна, текст |
| `events` | object[] | сваки догађај игре који није ни о једном играчу, по времену, са свим својим пољима: сигнали рунди и фазе, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (подешавања сервера кад су се мењала), режисерове ударе камере при преносу, `cs_win_panel_match`, ... |
| `state` | object[] | стање игре где се променило: време, поље, вредност - тајмаути (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), бомба (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, играчи који су живи, и серверови `match_start_time` и `round_start_time` |
| `selfCheck` | објекат | `completeness`: где је отишло све из демоа - по називу догађаја, класи својстава, мрежној поруци, оквиру и табели стрингова, бројеви `seen`, `decoded`, `partial`, `raw` и `lost`, написане пратеће датотеке, укупно `lost` (0 осим уз `--no-bulk`), и својства која парсер наводи а не може да прочита (`unreadProps`). Конвенција: [Конвертори чувају све](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); пратеће датотеке: одељак Completeness у README-у |

## Рунде {#rounds}

| Поље | Тип | Шта |
|---|---|---|
| `number` | number | рунда, од 1 |
| `start` | number | секунде меча кад је завршено замрзавање |
| `end` | number | секунде меча кад је рунда одлучена |
| `until` | number | секунде меча кад је почела следећа рунда (крај после фазе) |
| `winner` | стринг | `T` или `CT`; празно за нерешено |
| `winnerTeam` | стринг | назив тима победничке стране; празно за нерешено |
| `reason` | стринг | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` или `other` |
| `score` | објекат | назив тима -> освојене рунде после ове |
| `sides` | објекат | назив тима -> `T` / `CT` ове рунде |
| `equipment` | објекат | страна -> укупна вредност опреме њених живих играча на крају замрзавања, у доларима |
| `buy` | објекат | страна -> `pistol`, `eco`, `force` или `full` |
| `plant` | објекат или null | постављање бомбе: `site` (`A` или `B`; празно кад демо то не каже), `time` (секунде **у рунди**, као код убиства), `player`, `steamid`, `x`, `y`, `z` (јединице игре), `place` (назив места постављача: где је бомба лежала) |
| `survivors` | објекат | страна -> називи почетних играча који су још били живи кад је рунда одлучена, сортирани |
| `clutches` | object[] | сваки: `player`, `steamid`, `side`, `against` (непријатељи живи кад је играч постао последњи), `won` |
| `kills` | object[] | свака смрт у рунди, по редоследу - испод |

Како се ово налази: [Како се прави меч](building-matches.md#рунде); клачеви и преживели: [Статистика](statistics.md#клачеви).

### Убиства у рунди {#a-rounds-kills}

Свака смрт у рунди, укључујући после фазе:

| Поље | Тип | Шта |
|---|---|---|
| `time` | number | секунде **у рунди** (од краја замрзавања) |
| `attacker`, `attackerSide` | стринг | убица и његова страна; празно за свет |
| `victim`, `victimSide` | стринг | жртва и њена страна |
| `assister` | стринг или null | играч који је асистирао, или null |
| `flashAssist` | bool | асистенција је била блицем |
| `weapon` | стринг | како га игра именује |
| `headshot` | bool | |
| `wallbang` | bool | метак је прошао кроз нешто |
| `throughSmoke` | bool | убиство је кроз дим |
| `noscope` | bool | оружје са нишаном је испаљено без нишана |
| `attackerBlind` | bool | убица је био ослепљен блицем |
| `opening` | bool | прво убиство непријатеља у рунди |
| `traded` | bool | ова смрт је осветљена у року од 5 s |
| `trade` | bool | ово убиство је осветлило саиграча у року од 5 s |
| `teamkill` | bool | нападач и жртва на истој страни, два различита играча |
| `suicide` | bool | нападач и жртва исти играч (нпр. сопствени бацач); није тимско убиство |
| `after` | bool | убиство је дошло после одлуке о рунди |
| `place` | стринг | где је била **жртва** (назив места на мапи) |

## Играчи {#players}

Један унос по играчу, по називу тима, па најбољи први по убиствима минус смрти, па по убиствима:

| Поље | Тип | Шта |
|---|---|---|
| `name`, `steamid`, `team` | стринг | ко |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | асистенције без и са блицем |
| `diff` | number | убиства - смрти |
| `adr` | number | просечна штета по одиграној рунди, изгубљено здравље |
| `kast` | number | проценат рунди са убиством, асистенцијом, преживљавањем или осветљеном смрћу |
| `headshotPct` | number | проценат убистава која су била у главу |
| `openingKills`, `openingDeaths` | number | добијени и изгубљени отварајући дуели |
| `tradeKills`, `tradedDeaths` | number | убиства која су осветлила саиграча; смрти које су осветљене |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: рунде с толико убистава |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | штета HE бацачима, молотовом, запаљивом бомбом |
| `enemiesFlashed` | number | непријатељи ослепљени најмање 1 s |
| `plants`, `defuses` | number | |
| `teamkills` | number | саиграчи убијени; самоубиства се не броје |
| `roundsPlayed` | number | почете рунде |

Свака дефиниција: [Статистика](statistics.md#ред-табеле-резултата).

## Конвенције {#conventions}

Уписане у сваки документ да читалац зна шта бројеви значе без ове странице:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Пример {#an-example}

Из синтетичког демоа са две рунде из тестова, скраћено (`...` означава оно што је изостављено):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

Редослед кључева унутар `survivors`, `equipment` и `buy` није фиксиран.
