---
title: Dokument zápasu
nav_order: 9
lang: "cs"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Dokument zápasu (`<zápas>.match.json`) {#the-match-document-matchjson}

Jeden dokument JSON na zápas, vedle jeho tabulky: týmy, skóre, každé kolo s
jeho výsledkem, ekonomikou, položením bomby, zabitími, clutchi a přeživšími a
výsledková řádka každého hráče. Načítá ho karta Zápas v prohlížeči 3DHeat.
Kód: `summary()` v
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
čísla jsou definovaná na stránce [Statistiky](statistics.md).

Soubor je v UTF-8, odsazený jednou mezerou, a znaky mimo ASCII (jména hráčů a
týmů) si zachovává tak, jak jsou. Časy jsou v sekundách, zaokrouhlené na tři
desetinná místa u kol a na dvě u zabití a položení.

## Dokument {#the-document}

| Pole | Typ | Co |
|---|---|---|
| `format` | řetězec | vždy `heat3d-cs2-match` - podle toho čtenář soubor rozpozná |
| `version` | číslo | `3`. Dokument verze 1 dává čas položení `time` v sekundách zápasu; od verze 2 je to sekund do kola, jako u zabití. Verze 3 přidává pole od `header` dál a čas zmrazení do tabulky. |
| `match` | řetězec | název zápasu, jak se soubory jmenují |
| `map` | řetězec | mapa (`de_x`) |
| `demos` | řetězec[] | soubory dema, ze kterých byl sestaven, jen jména souborů, v pořadí zápasu |
| `teams` | řetězec[] | názvy týmů v pořadí výskytu (kolo 1: nejdřív strana T) |
| `score` | objekt | název týmu -> počet vyhraných kol: skóre posledního kola |
| `rounds` | objekt[] | každé úplné kolo, v pořadí - [níže](#rounds) |
| `incomplete` | číslo[] | čísla kol přerušených koncem dema a vynechaných |
| `missing` | číslo[] | čísla kol před prvním, které dema mají: `[1, 2]`, když záznam začíná u kola 3 |
| `halfLength` | číslo nebo null | počet kol v řádném poločase, od místa, kde se strany poprvé prohodí (`12` ve formátu 24 kol); null, když záznam prohození neukazuje |
| `pistolRounds` | číslo[] | pistolová kola, podle kterých se počítá `buy`: kolo 1 a kolo po poločase, je-li `halfLength` známé; nikdy kolo prodloužení |
| `players` | objekt[] | výsledková tabule - [níže](#players) |
| `conventions` | objekt | definice, na kterých čísla stojí, [níže](#conventions) |
| `header` | objekt | hlavička prvního dema tak, jak ji parser podává: jméno serveru, verze patche, verze dema, mapa |
| `profiles` | objekt | Steam ID -> to, co u hráče zůstává během zápasu stejné: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (naposledy viděné) |
| `playerInfo` | objekt[] | každý hráč, který dema uvádí, včetně trenérů a kasterů: Steam ID, jméno, číslo týmu |
| `skins`, `itemDrops` | objekt[] | skiny zbraní a předměty, když je dema mají (turnajová dema z vysílání nemají žádné) |
| `chat` | objekt[] | každý řádek chatu v zápase: čas, kolo, hráč, strana, text |
| `events` | objekt[] | každá herní událost, která se netýká žádného hráče, v časovém pořadí, se všemi poli: signály kola a fáze, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (nastavení serveru, jak se měnilo), záběry kamery režie vysílání, `cs_win_panel_match`, ... |
| `state` | objekt[] | stav hry tam, kde se změnil: čas, pole, hodnota - časové výstupy (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, hráči naživu, `match_start_time` a `round_start_time` serveru |
| `selfCheck` | objekt | `completeness`: kam se dostalo všechno z dema - pro každý název události, třídu vlastnosti, síťovou zprávu, snímek a tabulku řetězců jejich počty `seen`, `decoded`, `partial`, `raw` a `lost`, zapsané pomocné soubory, celkové `lost` (0, pokud není `--no-bulk`), vlastnosti, které parser vypisuje, ale nedokáže je přečíst (`unreadProps`). Konvence: [Převodníky nic neztrácejí](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); pomocné soubory: oddíl Completeness v README |

## Kola {#rounds}

| Pole | Typ | Co |
|---|---|---|
| `number` | číslo | kolo, od 1 |
| `start` | číslo | sekundy zápasu, když skončilo zmrazení |
| `end` | číslo | sekundy zápasu, když bylo kolo rozhodnuto |
| `until` | číslo | sekundy zápasu, když začalo další kolo (konec fáze po) |
| `winner` | řetězec | `T` nebo `CT`; prázdné u remízy |
| `winnerTeam` | řetězec | název týmu vítězné strany; prázdné u remízy |
| `reason` | řetězec | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` nebo `other` |
| `score` | objekt | název týmu -> počet vyhraných kol po tomto kole |
| `sides` | objekt | název týmu -> `T` / `CT` v tomto kole |
| `equipment` | objekt | strana -> celková hodnota výbavy jejích živých hráčů na konci zmrazení, v dolarech |
| `buy` | objekt | strana -> `pistol`, `eco`, `force` nebo `full` |
| `plant` | objekt nebo null | položení bomby: `site` (`A` nebo `B`; prázdné, když dema neuvádí), `time` (sekundy **do kola**, jako u zabití), `player`, `steamid`, `x`, `y`, `z` (herní jednotky), `place` (název místa plantéra: kde bomba ležela) |
| `survivors` | objekt | strana -> jména výchozích hráčů, kteří byli naživu, když bylo kolo rozhodnuto, seřazená |
| `clutches` | objekt[] | každý: `player`, `steamid`, `side`, `against` (nepřátelé naživu, když se hráč stal posledním), `won` |
| `kills` | objekt[] | každá smrt v kole, v pořadí - níže |

Jak se tyto údaje zjišťují: [Sestavení zápasu](building-matches.md#rounds);
clutchi a přeživší: [Statistiky](statistics.md#clutches).

### Zabití v kole {#a-rounds-kills}

Každá smrt v kole, včetně fáze po:

| Pole | Typ | Co |
|---|---|---|
| `time` | číslo | sekundy **do kola** (od konce zmrazení) |
| `attacker`, `attackerSide` | řetězec | vrah a jeho strana; prázdné pro svět |
| `victim`, `victimSide` | řetězec | oběť a její strana |
| `assister` | řetězec nebo null | asistující hráč, nebo null |
| `flashAssist` | bool | asistence byla zábleskem |
| `weapon` | řetězec | tak, jak ji hra pojmenuje |
| `headshot` | bool | |
| `wallbang` | bool | kulka prošla něčím |
| `throughSmoke` | bool | zabití přes kouř |
| `noscope` | bool | zaměřovaná zbraň vystřelila bez zaměření |
| `attackerBlind` | bool | vrah byl oslepen zábleskem |
| `opening` | bool | první zabití nepřítele v kole |
| `traded` | bool | tato smrt byla pomstěna do 5 s |
| `trade` | bool | toto zabití pomstilo spoluhráče do 5 s |
| `teamkill` | bool | útočník a oběť na téže straně, dva různí hráči |
| `suicide` | bool | útočník a oběť je tentýž hráč (vlastní granát, třeba); není to teamkill |
| `after` | bool | zabití přišlo poté, co bylo kolo rozhodnuto |
| `place` | řetězec | kde byla **oběť** (název místa na mapě) |

## Hráči {#players}

Jeden záznam na hráče, podle názvu týmu a pak od nejlepšího podle zabití
mínus smrti, potom zabití:

| Pole | Typ | Co |
|---|---|---|
| `name`, `steamid`, `team` | řetězec | kdo |
| `kills`, `deaths` | číslo | |
| `assists`, `flashAssists` | číslo | asistence bez záblesku a se zábleskem |
| `diff` | číslo | zabití - smrti |
| `adr` | číslo | průměrné poškození na odehrané kolo, ztracené zdraví |
| `kast` | číslo | procento kol s zabitím, asistencí, přežitím nebo odplacenou smrtí |
| `headshotPct` | číslo | procento zabití, která byla headshoty |
| `openingKills`, `openingDeaths` | číslo | vyhrané a prohrané otevírací souboje |
| `tradeKills`, `tradedDeaths` | číslo | odplatná zabití; smrti, které byly odplaceny |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: kola s tolika zabitími |
| `clutches`, `clutchesWon` | číslo | |
| `utilityDamage` | číslo | poškození HE, molotovem, zápalným granátem |
| `enemiesFlashed` | číslo | nepřátelé oslepení alespoň 1 s |
| `plants`, `defuses` | číslo | |
| `teamkills` | číslo | zabití spoluhráči; sebevraždy se nepočítají |
| `roundsPlayed` | číslo | začatá kola |

Každá definice: [Statistiky](statistics.md#the-scoreboard-line).

## Konvence {#conventions}

Zapisují se do každého dokumentu, aby čtenář věděl, co čísla znamenají, bez
této stránky:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Příklad {#an-example}

Ze syntetického dvoukolového dema z testů, zkráceně (`...` značí vynechané
části):

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

Pořadí klíčů uvnitř `survivors`, `equipment` a `buy` není pevné.
