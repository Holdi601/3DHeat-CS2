---
title: "Документът на мача"
nav_order: 9
lang: "bg"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Документът на мача (`<match>.match.json`) {#the-match-document-matchjson}

Един JSON документ на мач, до неговата таблица: отбори, резултат, всеки рунд с неговия изход, икономика, поставяне, убийства, clutch-ове и оцелели, и редът на таблото на всеки играч. Това е, което зарежда визуализаторът в раздела Мач.
Код: `summary()` в
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
числата са определени в [Статистика](statistics.md).

Файлът е в UTF-8, с отстъп от един интервал, и запазва не-ASCII знаците (имената на играчите и отборите) както са. Времената са в секунди, закръглени до три знака за рундове и до два за убийства и поставяне.

## Документът {#the-document}

| Поле | Тип | Какво е |
|---|---|---|
| `format` | низ | винаги `heat3d-cs2-match` - така четецът разпознава файла |
| `version` | число | `3`. Документ от версия 1 дава `time` на поставянето в секунди на мача; от 2 нататък е в секунди в рунда, както на убийство. 3 добавя полетата от `header` нататък и freeze time към таблицата. |
| `match` | низ | името на мача, както са наименувани файловете |
| `map` | низ | картата (`de_x`) |
| `demos` | низ[] | файловете с демо, от които е сглобен, само имената на файловете, в ред на мача |
| `teams` | низ[] | имената на отборите в реда на появяване (рунд 1: първо страна T) |
| `score` | обект | име на отбор -> спечелени рундове: резултатът на последния рунд |
| `winner` | низ или null | отборът, спечелил мача, където записът показва края; null за запис, който спира рано, овертайм без панела за победа, или равенство |
| `winnerSource` | низ или null | как е известен `winner`: `winPanel` (панелът за победа на играта), `surrender` (предаване), `regulation` (повече от половината редовни рундове) |
| `rounds` | обект[] | всеки пълен рунд, по ред - [по-долу](#рундове) |
| `incomplete` | число[] | номера на рундове, прекъснати от края на демо и пропуснати |
| `missing` | число[] | номера на рундове преди първия, който демата съдържат: `[1, 2]`, когато записът започва от рунд 3 |
| `halfLength` | число или null | рундове в едно редовно полувреме, от мястото, където страните за първи път си сменят местата (`12` в 24-рундовия формат); null, когато записът не показва смяната |
| `pistolRounds` | число[] | пистолните рундове, с които се брои `buy`: рунд 1 и рундът след полувремето, когато `halfLength` е известно; никога овертайм рунд |
| `players` | обект[] | таблото - [по-долу](#играчи) |
| `conventions` | обект | определенията зад числата, [по-долу](#конвенции) |
| `header` | обект | заглавието на първото демо, както го дава парсерът: име на сървъра, версия на пача, версия на демото, карта |
| `profiles` | обект | Steam ID -> какво остава същото за играча през целия мач: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (последно видяно) |
| `playerInfo` | обект[] | всеки играч, който демата изброяват, включително треньори и коментатори: Steam ID, име, номер на отбора |
| `skins`, `itemDrops` | обект[] | скинове на оръжия и падащи предмети, където демото ги има (турнирните демота от излъчването нямат) |
| `chat` | обект[] | всеки ред от чата в мача: време, рунд, играч, страна, текст |
| `events` | обект[] | всяко игрово събитие, което не е свързано с никой играч, по време, с всичките му полета: сигнали и фази на рунда, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (настройките на сървъра, както са се променяли), режисьорските кадри на излъчването - преследване и фиксирани кадри, `cs_win_panel_match`, ... |
| `state` | обект[] | състоянието на играта, където се е променило: време, поле, стойност - прекъсвания (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), бомбата (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, играчите в живо състояние, `match_start_time` и `round_start_time` на сървъра |
| `selfCheck` | обект | `completeness`: къде е отишло всичко от демото - по име на събитие, клас на свойство, мрежово съобщение, кадър и таблица на низове - техните броеве `seen`, `decoded`, `partial`, `raw` и `lost`, записаните помощни файлове, общият `lost` (0, освен при `--no-bulk`), свойствата, които парсерът изброява, но не може да прочете (`unreadProps`). Конвенцията: [Конверторите запазват всичко](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); помощните файлове: раздел Completeness в README |

## Рундове {#rounds}

| Поле | Тип | Какво е |
|---|---|---|
| `number` | число | рундът, от 1 |
| `start` | число | секунди на мача, когато е свършило freeze time |
| `end` | число | секунди на мача, когато рундът е решен |
| `until` | число | секунди на мача, когато е започнал следващият рунд (краят на след фазата) |
| `winner` | низ | `T` или `CT`; празно при равенство |
| `winnerTeam` | низ | името на отбора на победилата страна; празно при равенство |
| `reason` | низ | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` или `other` |
| `score` | обект | име на отбор -> спечелени рундове след този |
| `sides` | обект | име на отбор -> `T` / `CT` в този рунд |
| `equipment` | обект | страна -> общата стойност на екипировката на живите ѝ играчи в freeze end, в долари |
| `buy` | обект | страна -> `pistol`, `eco`, `force` или `full` |
| `plant` | обект или null | поставянето на бомбата: `site` (`A` или `B`; празно, когато демото не казва), `time` (секунди **в рунда**, както на убийство), `player`, `steamid`, `x`, `y`, `z` (игрови единици), `place` (името на мястото на поставящия: където е лежала бомбата) |
| `survivors` | обект | страна -> имената на началните играчи, които са още живи, когато рундът е решен, подредени |
| `clutches` | обект[] | всеки: `player`, `steamid`, `side`, `against` (враговете живи, когато играчът е станал последният), `won` |
| `kills` | обект[] | всяка смърт в рунда, по ред - по-долу |

Как се намират: [Изграждане на мач](building-matches.md#рундове);
clutch-ове и оцелели: [Статистика](statistics.md#clutch-ове).

### Убийствата в рунд {#a-rounds-kills}

Всяка смърт в рунда, включително в след фазата:

| Поле | Тип | Какво е |
|---|---|---|
| `time` | число | секунди **в рунда** (от freeze end) |
| `attacker`, `attackerSide` | низ | убиецът и неговата страна; празно за света |
| `victim`, `victimSide` | низ | жертвата и нейната страна |
| `assister` | низ или null | асистиращият играч, или null |
| `flashAssist` | bool | асистенцията е била за ослепяване |
| `weapon` | низ | както го назовава играта |
| `headshot` | bool | |
| `wallbang` | bool | куршумът е минал през нещо |
| `throughSmoke` | bool | убийството е през дим |
| `noscope` | bool | оръжие с прицел е стреляло без прицел |
| `attackerBlind` | bool | убиецът е бил заслепен |
| `opening` | bool | първото убийство на враг в рунда |
| `traded` | bool | тази смърт е отмъстена в рамките на 5 s |
| `trade` | bool | това убийство е отмъстило съотборник в рамките на 5 s |
| `teamkill` | bool | атакуващият и жертвата са на една страна, двама различни играча |
| `suicide` | bool | атакуващият и жертвата са един и същ играч (например собствена граната); не е teamkill |
| `after` | bool | убийството е дошло, след като рундът е бил решен |
| `place` | низ | където е била **жертвата** (името на мястото на картата) |

## Играчи {#players}

По един запис на играч, по име на отбор и после най-добрите първи по убийства минус смъртни случаи, после по убийства:

| Поле | Тип | Какво е |
|---|---|---|
| `name`, `steamid`, `team` | низ | кой |
| `kills`, `deaths` | число | |
| `assists`, `flashAssists` | число | асистенции без и за ослепяване |
| `diff` | число | убийства - смъртни случаи |
| `adr` | число | средни щети на изигран рунд, загубено здраве |
| `kast` | число | процент от изиграните рундове с убийство, асистенция, оцеляване или разменена смърт |
| `headshotPct` | число | процент от убийствата, които са в главата |
| `openingKills`, `openingDeaths` | число | спечелени и загубени първи дуели |
| `tradeKills`, `tradedDeaths` | число | убийства в размяна; смъртни случаи, които са разменени |
| `multiKills` | обект | `{"2k": n, "3k": n, "4k": n, "5k": n}`: рундове с толкова убийства |
| `clutches`, `clutchesWon` | число | |
| `utilityDamage` | число | щети с HE, молотов, запалителна |
| `enemiesFlashed` | число | врагове, заслепени поне 1 s |
| `plants`, `defuses` | число | |
| `teamkills` | число | убити съотборници; самоубийствата не се броят |
| `roundsPlayed` | число | започнати рундове |

Всяко определение: [Статистика](statistics.md#редът-на-таблото).

## Конвенции {#conventions}

Записани във всеки документ, за да знае четецът какво означават числата, без тази страница:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Пример {#an-example}

От синтетичното демо с два рунда от тестовете, съкратено (`...` означава пропуснатото):

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

Редът на ключовете в `survivors`, `equipment` и `buy` не е фиксиран.
