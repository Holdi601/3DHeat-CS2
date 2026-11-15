---
title: "Leikjaskjalið"
nav_order: 9
lang: "is"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Leikjaskjalið (`<match>.match.json`) {#the-match-document-matchmatchjson}

Eitt JSON-skjal fyrir hvern leik, við hliðina á töflu hans: lið, staða, hver lota
með niðurstöðu sinni, hagkerfi, sprengjusetningu, fellingum, clutch og eftirlifendum, og
stigatöflulína hvers leikmanns. Það er það sem Leiks-flipi 3DHeat-skoðarans hleður.
Kóði: `summary()` í
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
tölurnar eru skilgreindar á síðunni [Tölfræði](statistics.md).

Skráin er UTF-8, inndregin um eitt bil, og geymir stafi utan ASCII
(nöfn leikmanna og liða) eins og þeir eru. Tímar eru í sekúndum, rúnnaðir í þrjá
aukastafi fyrir lotur og tvo fyrir fellingar og sprengjusetninguna.

## Skjalið {#the-document}

| Reitur | Tegund | Hvað |
|---|---|---|
| `format` | string | alltaf `heat3d-cs2-match` - hvernig lesari þekkir skrána |
| `version` | number | `3`. Skjal í útgáfu 1 gefur `time` sprengjusetningar í leiksekúndum; frá 2 er það sekúndur inn í lotuna, eins og hjá fellingu. 3 bætir við reitunum frá `header` og áfram, og frystitíma í töfluna. |
| `match` | string | leikjanafnið, eins og skrárnar heita |
| `map` | string | kortið (`de_x`) |
| `demos` | string[] | demo-skrárnar sem það var smíðað úr, aðeins skráarnöfn, í röð leiksins |
| `teams` | string[] | liðsheitin í röð birtingar (lota 1: T-hliðin fyrst) |
| `score` | object | liðsheiti -> unnar lotur: staða síðustu lotu |
| `winner` | string or null | liðið sem vann leikinn, þar sem upptakan sýnir endann; null fyrir upptöku sem stöðvast snemma, framlengingu án sigurspjalds, eða jafntefli |
| `winnerSource` | string or null | hvernig `winner` er þekkt: `winPanel` (sigurspjald leiksins), `surrender`, `regulation` (meira en helmingur venjulegra lota) |
| `rounds` | object[] | hver lokið lota, í röð - [hér að neðan](#rounds) |
| `incomplete` | number[] | lotunúmer skorin af við enda demo-skrár og sleppt |
| `missing` | number[] | lotunúmer á undan þeirri fyrstu sem demo-skrárnar geyma: `[1, 2]` þegar upptakan byrjar við lotu 3 |
| `halfLength` | number or null | lotur í venjulegum hálfleik, frá því þar sem hliðar skipta fyrst (`12` í 24 lotna sniðinu); null þegar upptakan sýnir ekki skiptin |
| `pistolRounds` | number[] | skammbyssulloturnar sem `buy` er talið með: lota 1, og lotan eftir hálfleikinn þegar `halfLength` er þekkt; aldrei framlengingarlota |
| `players` | object[] | stigataflan - [hér að neðan](#players) |
| `conventions` | object | skilgreiningarnar á bak við tölurnar, [hér að neðan](#conventions) |
| `header` | object | haus fyrstu demo-skrárinnar eins og þáttarinn gefur hann: heiti þjóns, plásturútgáfa, útgáfa demo-skrár, kort |
| `profiles` | object | Steam ID -> það sem helst eins hjá leikmanni gegnum leikinn: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (það síðast séða) |
| `playerInfo` | object[] | hver leikmaður sem demo-skrárnar telja upp, líka þjálfarar og lýsendur: Steam ID, nafn, liðsnúmer |
| `skins`, `itemDrops` | object[] | vopnaskinn og hlutafall, þar sem demo-skráin hefur þau (mótsdemo-skrár úr útsendingu hafa engin) |
| `chat` | object[] | hver spjalllína í leiknum: tími, lota, leikmaður, hlið, texti |
| `events` | object[] | hver leikatburður sem tengist engum leikmanni, í tímaröð, með öllum reitum sínum: lotuhljóð og fasar, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (stillingar þjónsins eins og þær breyttust), eltingar- og fastar myndavélartökur útsendingarstjórans, `cs_win_panel_match`, ... |
| `state` | object[] | staða leiksins þar sem hún breyttist: tími, reitur, gildi - leikhlé (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), sprengjan (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, leikmenn á lífi, `match_start_time` og `round_start_time` þjónsins |
| `selfCheck` | object | `completeness`: hvert allt úr demo-skránni fór - fyrir hvert atburðarheiti, eiginleikaflokk, netskilaboð, ramma og strengjatöflu fjöldi þess sem var `seen`, `decoded`, `partial`, `raw` og `lost`, hliðarskrárnar skrifaðar, heildarfjöldi `lost` (0 nema `--no-bulk`), eiginleikarnir sem þáttarinn telur upp en getur ekki lesið (`unreadProps`). Venjan: [Converters keep everything](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); hliðarskrárnar: kafli README um Completeness |

## Lotur {#rounds}

| Reitur | Tegund | Hvað |
|---|---|---|
| `number` | number | lotan, frá 1 |
| `start` | number | leiksekúndur þegar frystitíminn endaði |
| `end` | number | leiksekúndur þegar lotan var ákvörðuð |
| `until` | number | leiksekúndur þegar næsta lota byrjaði (endir after-fasans) |
| `winner` | string | `T` eða `CT`; tómt fyrir jafntefli |
| `winnerTeam` | string | liðsheiti sigurhliðarinnar; tómt fyrir jafntefli |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` eða `other` |
| `score` | object | liðsheiti -> unnar lotur eftir þessa |
| `sides` | object | liðsheiti -> `T` / `CT` í þessari lotu |
| `equipment` | object | hlið -> heildarbúnaðarverðmæti lifandi leikmanna hennar við freeze end, í dollurum |
| `buy` | object | hlið -> `pistol`, `eco`, `force` eða `full` |
| `plant` | object or null | sprengjusetningin: `site` (`A` eða `B`; tómt þegar demo-skráin segir það ekki), `time` (sekúndur **inn í lotuna**, eins og hjá fellingu), `player`, `steamid`, `x`, `y`, `z` (leikeiningar), `place` (staðarheiti setjandans: þar sem sprengjan lá) |
| `survivors` | object | hlið -> nöfn upphafsleikmanna sem voru enn á lífi þegar lotan var ákvörðuð, raðað |
| `clutches` | object[] | hver: `player`, `steamid`, `side`, `against` (andstæðingar á lífi þegar leikmaðurinn varð sá síðasti), `won` |
| `kills` | object[] | hvert dauðsfall lotunnar, í röð - hér að neðan |

Hvernig þetta er fundið: [Að smíða leik](building-matches.md#rounds);
clutch og eftirlifendur: [Tölfræði](statistics.md#clutches).

### Fellingar lotu {#a-rounds-kills}

Hvert dauðsfall í lotunni, after-fasinn meðtalinn:

| Reitur | Tegund | Hvað |
|---|---|---|
| `time` | number | sekúndur **inn í lotuna** (frá freeze end) |
| `attacker`, `attackerSide` | string | banamaðurinn og hlið hans; tómt fyrir heiminn |
| `victim`, `victimSide` | string | fórnarlambið og hlið þess |
| `assister` | string or null | aðstoðarleikmaðurinn, eða null |
| `flashAssist` | bool | aðstoðin var blinda |
| `weapon` | string | eins og leikurinn nefnir það |
| `headshot` | bool | |
| `wallbang` | bool | kúlan fór í gegnum eitthvað |
| `throughSmoke` | bool | fellingin var gegnum reyk |
| `noscope` | bool | sjónaukavopni skotið án sjónauka |
| `attackerBlind` | bool | banamaðurinn var blindaður |
| `opening` | bool | fyrsta felling lotunnar á andstæðingi |
| `traded` | bool | þessum dauða var hefnt innan 5 s |
| `trade` | bool | þessi felling hefndi liðsfélaga innan 5 s |
| `teamkill` | bool | árásarmaður og fórnarlamb á sömu hlið, tveir ólíkir leikmenn |
| `suicide` | bool | árásarmaður og fórnarlamb sami leikmaður (eigin handsprengja, til dæmis); ekki teamkill |
| `after` | bool | fellingin kom eftir að lotan var ákvörðuð |
| `place` | string | þar sem **fórnarlambið** var (staðarheiti kortsins) |

## Leikmenn {#players}

Ein færsla fyrir hvern leikmann, eftir liðsheiti og síðan best fyrst eftir fellingum mínus
dauðsföllum, síðan fellingum:

| Reitur | Tegund | Hvað |
|---|---|---|
| `name`, `steamid`, `team` | string | hver |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | aðstoðir án og með blindu |
| `diff` | number | kills - deaths |
| `adr` | number | meðalskaði á spilaða lotu, tapað líf |
| `kast` | number | prósent spilaðra lota með fellingu, aðstoð, að lifa af eða hefnt dauðsfall |
| `headshotPct` | number | prósent fellinga sem voru hausskot |
| `openingKills`, `openingDeaths` | number | opnunareinvígi unnin og töpuð |
| `tradeKills`, `tradedDeaths` | number | trade-fellingar; dauðsföll sem var hefnt |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: lotur með svo mörgum fellingum |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | skaði með HE, molotov, incendiary |
| `enemiesFlashed` | number | andstæðingar blindaðir í að minnsta kosti 1 s |
| `plants`, `defuses` | number | |
| `teamkills` | number | liðsfélagar felldir; sjálfsvíg eru ekki talin |
| `roundsPlayed` | number | lotur byrjaðar |

Allar skilgreiningar: [Tölfræði](statistics.md#the-scoreboard-line).

## Venjur {#conventions}

Skrifað í hvert skjal svo lesari viti hvað tölurnar þýða án
þessarar síðu:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Dæmi {#an-example}

Úr gervi-demo-skránni með tveimur lotum úr prófununum, stytt (`...` sýnir það sem er
sleppt):

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

Röð lykla inni í `survivors`, `equipment` og `buy` er ekki föst.
