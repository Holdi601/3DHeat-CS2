---
title: "Документот на натпреварот"
nav_order: 9
lang: "mk"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Документот на натпреварот (`<match>.match.json`) {#the-match-document-matchjson}

Еден JSON документ по натпревар, до неговата табела: тимови, резултат, секоја рунда
со својот исход, економија, поставување, убиства, клачеви и преживеани, и
линијата од табелата со резултати на секој играч. Тоа го вчитува табот
Натпревар на прегледувачот 3DHeat.
Код: `summary()` во
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
броевите се дефинирани на [Статистика](statistics.md).

Датотеката е UTF-8, вовлечена со едно празно место, и ги задржува
не-ASCII знаците (имињата на играчи и тимови) какви што се. Времињата се
секунди, заокружени на три децимали за рундите и две за убиствата и
поставувањето.

## Документот {#the-document}

| Поле | Тип | Што |
|---|---|---|
| `format` | string | секогаш `heat3d-cs2-match` - како читачот ја препознава датотеката |
| `version` | number | `3`. Документ од верзија 1 го дава `time` на поставувањето во секунди на натпреварот; од 2 е во секунди во рундата, како кај убиство. 3 ги додава полињата од `header` натаму, и замрзнатото време во табелата. |
| `match` | string | името на натпреварот, како што се именувани датотеките |
| `map` | string | мапата (`de_x`) |
| `demos` | string[] | датотеките со демо од кои е изграден, само имиња на датотеки, по редослед на натпреварот |
| `teams` | string[] | имињата на тимовите по редослед на појавување (рунда 1: страната T прва) |
| `score` | object | име на тим -> добиени рунди: резултатот од последната рунда |
| `winner` | string or null | тимот што го добил натпреварот, каде што снимката го покажува крајот; null за снимка што запира рано, продолжение без панелот за победа, или нерешено |
| `winnerSource` | string or null | како се знае `winner`: `winPanel` (панелот за победа во натпреварот на играта), `surrender`, `regulation` (повеќе од половина од регуларните рунди) |
| `rounds` | object[] | секоја целосна рунда, по ред - [подолу](#rounds) |
| `incomplete` | number[] | броеви на рунди прекинати од крајот на демо и изоставени |
| `missing` | number[] | броеви на рунди пред првата што ја содржат демоата: `[1, 2]` кога снимката почнува од рунда 3 |
| `halfLength` | number or null | рунди во регуларно полувреме, од таму каде што страните првпат се менуваат (`12` во форматот од 24 рунди); null кога снимката не го покажува менувањето |
| `pistolRounds` | number[] | пиштолските рунди со кои се брои `buy`: рунда 1, и рундата по полувремето кога `halfLength` е познато; никогаш рунда од продолжение |
| `players` | object[] | табелата со резултати - [подолу](#players) |
| `conventions` | object | дефинициите зад броевите, [подолу](#conventions) |
| `header` | object | заглавието на првото демо како што го дава парсерот: име на серверот, верзија на закрпата, верзија на демото, мапа |
| `profiles` | object | Steam ID -> она што останува исто за играчот низ натпреварот: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (последното виденото) |
| `playerInfo` | object[] | секој играч што го листаат демоата, и тренери и коментатори: Steam ID, име, број на тим |
| `skins`, `itemDrops` | object[] | облеки на оружја и испуштени предмети, каде што демото ги има (турнирските демоа од преносот ги немаат) |
| `chat` | object[] | секоја линија од чет во натпреварот: време, рунда, играч, страна, текст |
| `events` | object[] | секој настан на играта што не е за ниту еден играч, по редослед на време, со сите свои полиња: ѕвона и фази на рундите, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (поставките на серверот како што се менувале), рамките на преносниот директор на камера (следење и фиксни), `cs_win_panel_match`, ... |
| `state` | object[] | состојбата на играта таму каде што се променила: време, поле, вредност - тајмаути (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), бомбата (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, живите играчи, `match_start_time` и `round_start_time` на серверот |
| `selfCheck` | object | `completeness`: каде отишло сè од демото - по име на настан, класа на својство, мрежна порака, рамка и табела со низи неговите броеви `seen`, `decoded`, `partial`, `raw` и `lost`, запишаните придружни датотеки, вкупното `lost` (0 освен со `--no-bulk`), својствата што парсерот ги листа но не може да ги чита (`unreadProps`). Конвенцијата: [Converters keep everything](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); придружните датотеки: делот Completeness во README |

## Рунди {#rounds}

| Поле | Тип | Што |
|---|---|---|
| `number` | number | рундата, од 1 |
| `start` | number | секунди на натпреварот кога завршило замрзнатото време |
| `end` | number | секунди на натпреварот кога рундата била одлучена |
| `until` | number | секунди на натпреварот кога почнала следната рунда (крајот на after фазата) |
| `winner` | string | `T` или `CT`; празно за нерешено |
| `winnerTeam` | string | името на тимот на победничката страна; празно за нерешено |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` или `other` |
| `score` | object | име на тим -> добиени рунди по оваа |
| `sides` | object | име на тим -> `T` / `CT` во оваа рунда |
| `equipment` | object | страна -> вкупна вредност на опремата на нејзините живи играчи на крајот на замрзнатото време, во долари |
| `buy` | object | страна -> `pistol`, `eco`, `force` или `full` |
| `plant` | object or null | поставувањето на бомбата: `site` (`A` или `B`; празно кога демото не кажува), `time` (секунди **во рундата**, како кај убиство), `player`, `steamid`, `x`, `y`, `z` (единици на играта), `place` (името на местото на поставувачот: каде лежела бомбата) |
| `survivors` | object | страна -> имиња на играчите од почетокот што уште биле живи кога рундата била одлучена, подредени |
| `clutches` | object[] | секој: `player`, `steamid`, `side`, `against` (непријатели живи кога играчот станал последен), `won` |
| `kills` | object[] | секоја смрт од рундата, по ред - подолу |

Како се наоѓаат овие: [Составување на натпревар](building-matches.md#rounds);
клачеви и преживеани: [Статистика](statistics.md#clutches).

### Убиствата на рундата {#a-rounds-kills}

Секоја смрт во рундата, вклучително after фазата:

| Поле | Тип | Што |
|---|---|---|
| `time` | number | секунди **во рундата** (од крајот на замрзнатото време) |
| `attacker`, `attackerSide` | string | убиецот и неговата страна; празно за светот |
| `victim`, `victimSide` | string | жртвата и нејзината страна |
| `assister` | string or null | играчот што асистирал, или null |
| `flashAssist` | bool | асистенцијата била со блесок |
| `weapon` | string | како што го именува играта |
| `headshot` | bool | |
| `wallbang` | bool | куршумот минал низ нешто |
| `throughSmoke` | bool | убиството било низ чад |
| `noscope` | bool | оружје со оптика пукало без оптика |
| `attackerBlind` | bool | убиецот бил заслепен |
| `opening` | bool | првото убиство на непријател во рундата |
| `traded` | bool | оваа смрт била осветена во рок од 5 s |
| `trade` | bool | ова убиство осветило соиграч во рок од 5 s |
| `teamkill` | bool | напаѓачот и жртвата на иста страна, два различни играчи |
| `suicide` | bool | напаѓачот и жртвата се ист играч (на пример, своја граната); не е убиство на свој |
| `after` | bool | убиството се случило откако рундата била одлучена |
| `place` | string | каде била **жртвата** (името на местото на мапата) |

## Играчи {#players}

Еден запис по играч, по име на тим и потоа најдобриот први по убиства минус
смрти, потоа убиства:

| Поле | Тип | Што |
|---|---|---|
| `name`, `steamid`, `team` | string | кој |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | асистенции без и со блесок |
| `diff` | number | убиства - смрти |
| `adr` | number | просечна штета по одиграна рунда, изгубено здравје |
| `kast` | number | процент од одиграните рунди со убиство, асистенција, преживување или разменета смрт |
| `headshotPct` | number | процент од убиствата што биле хедшот |
| `openingKills`, `openingDeaths` | number | добиени и изгубени отворачки дуели |
| `tradeKills`, `tradedDeaths` | number | убиства-размени; смрти што биле разменети |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: рунди со толку убиства |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | штета со HE, молотов, запалива |
| `enemiesFlashed` | number | непријатели заслепени најмалку 1 s |
| `plants`, `defuses` | number | |
| `teamkills` | number | убиени соиграчи; самоубиствата не се бројат |
| `roundsPlayed` | number | започнати рунди |

Секоја дефиниција: [Статистика](statistics.md#the-scoreboard-line).

## Конвенции {#conventions}

Запишани во секој документ за читачот да знае што значат броевите без оваа
страница:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Пример {#an-example}

Од синтетичкото демо од две рунди од тестовите, скратено (`...` означува она
што е изоставено):

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

Редоследот на клучевите внатре во `survivors`, `equipment` и `buy` не е фиксиран.
