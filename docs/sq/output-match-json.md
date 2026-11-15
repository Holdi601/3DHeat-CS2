---
title: "Dokumenti i ndeshjes"
nav_order: 9
lang: "sq"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Dokumenti i ndeshjes (`<match>.match.json`) {#the-match-document-matchjson}

Një dokument JSON për ndeshje, pranë tabelës së saj: ekipet, rezultati, çdo raund
me rezultatin e tij, ekonominë, vendosjen e bombës, vrasjet, clutch-et dhe mbijetuesit, dhe linja e tabelës së rezultateve
e çdo lojtari. Është ajo që ngarkon skeda Ndeshja e shikuesit 3DHeat.
Kodi: `summary()` në
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
numrat përkufizohen te [Statistikat](statistics.md).

Skedari është UTF-8, me një hapësirë shtrirje, dhe i mban shkronjat jo-ASCII
(emrat e lojtarëve dhe ekipeve) siç janë. Kohët janë sekonda, të rrumbullakosura në tri
dhjetore për raundet dhe dy për vrasjet dhe vendosjen e bombës.

## Dokumenti {#the-document}

| Fusha | Lloji | Çfarë |
|---|---|---|
| `format` | string | gjithmonë `heat3d-cs2-match` - si e njeh lexuesi skedarin |
| `version` | number | `3`. Një dokument version 1 e jep `time` të vendosjes në sekonda ndeshjeje; nga 2 është sekonda brenda raundit, si ajo e një vrasjeje. 3 shton fushat nga `header` e tutje, dhe kohën e ngrirjes te tabela. |
| `match` | string | emri i ndeshjes, siç emërtohen skedarët |
| `map` | string | harta (`de_x`) |
| `demos` | string[] | skedarët e demos nga u ndërtua, vetëm emrat e skedarëve, sipas renditjes së ndeshjes |
| `teams` | string[] | emrat e ekipeve sipas renditjes së shfaqjes (raundi 1: ana T e para) |
| `score` | object | emri i ekipit -> raundet e fituara: rezultati i raundit të fundit |
| `winner` | string ose null | ekipi që fitoi ndeshjen, ku regjistrimi e tregon fundin; null për një regjistrim që ndalon herët, një kohë shtesë pa panelin e fitores, ose një barazim |
| `winnerSource` | string ose null | si dihet `winner`: `winPanel` (paneli i fitores së ndeshjes i lojës), `surrender`, `regulation` (më shumë se gjysma e raundeve rregullore) |
| `rounds` | object[] | çdo raund i plotë, sipas renditjes - [më poshtë](#rounds) |
| `incomplete` | number[] | numrat e raundeve të prera nga fundi i një demoje dhe të lëna jashtë |
| `missing` | number[] | numrat e raundeve para të parit që mbajnë demot: `[1, 2]` kur regjistrimi nis te raundi 3 |
| `halfLength` | number ose null | raundet në një pjesë rregullore, nga ku ndërrohen anët për herë të parë (`12` në formatin me 24 raunde); null kur regjistrimi nuk e tregon ndërrimin |
| `pistolRounds` | number[] | raundet e pistoletave me të cilat numërohet `buy`: raundi 1, dhe raundi pas pjesës kur `halfLength` dihet; kurrë një raund kohe shtesë |
| `players` | object[] | tabela e rezultateve - [më poshtë](#players) |
| `conventions` | object | përkufizimet pas numrave, [më poshtë](#conventions) |
| `header` | object | koka e demos së parë siç e jep parseri: emri i serverit, versioni i patch-it, versioni i demos, harta |
| `profiles` | object | Steam ID -> çfarë mbetet e njëjtë për një lojtar gjatë ndeshjes: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (e fundit e parë) |
| `playerInfo` | object[] | çdo lojtar që listojnë demot, edhe trajnerët dhe komentuesit: Steam ID, emri, numri i ekipit |
| `skins`, `itemDrops` | object[] | skinat e armëve dhe rënia e sendeve, ku i ka demoja (demot e turneve nga transmetimi nuk kanë) |
| `chat` | object[] | çdo rresht bisede në ndeshje: koha, raundi, lojtari, ana, teksti |
| `events` | object[] | çdo ngjarje loje për asnjë lojtar, sipas renditjes së kohës, me të gjitha fushat e saj: sinjalet dhe fazat e raundit, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (cilësimet e serverit siç ndryshuan), kuadrot ndjekëse dhe të fiksuara të regjisorit të kamerës së transmetimit, `cs_win_panel_match`, ... |
| `state` | object[] | gjendja e lojës ku ndryshoi: koha, fusha, vlera - pauzat (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, lojtarët e gjallë, `match_start_time` dhe `round_start_time` të serverit |
| `selfCheck` | object | `completeness`: ku shkoi gjithçka e demos - për emër ngjarjeje, klasë vetie, mesazh rrjeti, kuadër dhe tabelë vargjesh numrat e saj `seen`, `decoded`, `partial`, `raw` dhe `lost`, sidecar-ët e shkruar, `lost` total (0 përveç me `--no-bulk`), vetitë që parseri i liston por nuk mund t'i lexojë (`unreadProps`). Konventa: [Konverterët mbajnë çdo gjë](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); sidecar-ët: seksioni Completeness i README |

## Raundet {#rounds}

| Fusha | Lloji | Çfarë |
|---|---|---|
| `number` | number | raundi, nga 1 |
| `start` | number | sekonda ndeshjeje kur mbaroi koha e ngrirjes |
| `end` | number | sekonda ndeshjeje kur raundi u vendos |
| `until` | number | sekonda ndeshjeje kur nisi raundi tjetër (fundi i fazës after) |
| `winner` | string | `T` ose `CT`; bosh për një barazim |
| `winnerTeam` | string | emri i ekipit të anës fituese; bosh për një barazim |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` ose `other` |
| `score` | object | emri i ekipit -> raundet e fituara pas këtij |
| `sides` | object | emri i ekipit -> `T` / `CT` këtë raund |
| `equipment` | object | ana -> vlera totale e pajisjeve të lojtarëve të saj të gjallë në fundin e ngrirjes, në dollarë |
| `buy` | object | ana -> `pistol`, `eco`, `force` ose `full` |
| `plant` | object ose null | vendosja e bombës: `site` (`A` ose `B`; bosh kur demoja nuk e thotë), `time` (sekonda **brenda raundit**, si ajo e një vrasjeje), `player`, `steamid`, `x`, `y`, `z` (njësi loje), `place` (emri i vendit të vendosësit: ku ndodhet bomba) |
| `survivors` | object | ana -> emrat e lojtarëve fillestarë ende të gjallë kur raundi u vendos, të renditur |
| `clutches` | object[] | secili: `player`, `steamid`, `side`, `against` (armiq të gjallë kur lojtari mbeti i fundit), `won` |
| `kills` | object[] | çdo vdekje e raundit, sipas renditjes - më poshtë |

Si gjenden këto: [Ndërtimi i një ndeshjeje](building-matches.md#rounds);
clutch-et dhe mbijetuesit: [Statistikat](statistics.md#clutches).

### Vrasjet e një raundi {#a-rounds-kills}

Çdo vdekje në raund, edhe faza after:

| Fusha | Lloji | Çfarë |
|---|---|---|
| `time` | number | sekonda **brenda raundit** (që nga fundi i ngrirjes) |
| `attacker`, `attackerSide` | string | vrasësi dhe ana e tij; bosh për botën |
| `victim`, `victimSide` | string | viktima dhe ana e saj |
| `assister` | string ose null | lojtari që asistoi, ose null |
| `flashAssist` | bool | asista ishte me flash |
| `weapon` | string | siç e emërton loja |
| `headshot` | bool | |
| `wallbang` | bool | plumbi kaloi nëpër diçka |
| `throughSmoke` | bool | vrasja ishte nëpër tym |
| `noscope` | bool | një armë me dylbi u gjuajt pa dylbi |
| `attackerBlind` | bool | vrasësi ishte i verbuar nga flash |
| `opening` | bool | vrasja e parë e një armiku në raund |
| `traded` | bool | kjo vdekje u hakmor brenda 5 s |
| `trade` | bool | kjo vrasje hakmori një shok ekipi brenda 5 s |
| `teamkill` | bool | sulmuesi dhe viktima në të njëjtën anë, dy lojtarë të ndryshëm |
| `suicide` | bool | sulmuesi dhe viktima i njëjti lojtar (një granatë e vetë, të themi); nuk është teamkill |
| `after` | bool | vrasja erdhi pasi raundi u vendos |
| `place` | string | ku ishte **viktima** (emri i vendit në hartë) |

## Lojtarët {#players}

Një hyrje për lojtar, sipas emrit të ekipit dhe pastaj më i miri i pari sipas vrasjeve minus
vdekjeve, pastaj vrasjeve:

| Fusha | Lloji | Çfarë |
|---|---|---|
| `name`, `steamid`, `team` | string | kush |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | asiste pa flash dhe me flash |
| `diff` | number | vrasje - vdekje |
| `adr` | number | dëmi mesatar për raund të luajtur, shëndet i humbur |
| `kast` | number | përqindja e raundeve të luajtura me një vrasje, asistë, mbijetesë ose vdekje të hakmorur |
| `headshotPct` | number | përqindja e vrasjeve që ishin goditje në kokë |
| `openingKills`, `openingDeaths` | number | duelet hapëse të fituara dhe të humbura |
| `tradeKills`, `tradedDeaths` | number | vrasje trade; vdekje që u hakmorën |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: raunde me aq vrasje |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | dëmi me HE, molotov, incendiary |
| `enemiesFlashed` | number | armiq të verbuar të paktën 1 s |
| `plants`, `defuses` | number | |
| `teamkills` | number | shokë ekipi të vrarë; vetëvrasjet nuk llogariten |
| `roundsPlayed` | number | raunde të nisura |

Çdo përkufizim: [Statistikat](statistics.md#the-scoreboard-line).

## Konventat {#conventions}

Shkruhen në çdo dokument që lexuesi të dijë çfarë tregojnë numrat pa këtë
faqe:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Një shembull {#an-example}

Nga demoja sintetike me dy raunde e testeve, e shkurtuar (`...` shënon çfarë
është lënë jashtë):

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

Renditja e çelësave brenda `survivors`, `equipment` dhe `buy` nuk është e fiksuar.
