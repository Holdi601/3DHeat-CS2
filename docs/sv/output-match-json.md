---
title: "Matchdokumentet"
nav_order: 9
lang: "sv"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Matchdokumentet (`<match>.match.json`) {#the-match-document-matchjson}

Ett JSON-dokument per match, bredvid dess tabell: lag, ställning, varje runda med sitt resultat,
ekonomi, plantering, kills, clutchar och överlevare, och varje spelares resultattavleslinje. Det är
vad 3DHeat-visarens flik Match läser in. Kod: `summary()` i
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
siffrorna definieras på [Statistik](statistics.md).

Filen är UTF-8, indragen med ett mellanslag, och behåller tecken utanför ASCII (spelar- och lagnamn)
som de är. Tider är sekunder, avrundade till tre decimaler för rundor och två för kills och
plantering.

## Dokumentet {#the-document}

| Fält | Typ | Vad |
|---|---|---|
| `format` | sträng | alltid `heat3d-cs2-match` - så att en läsare känner igen filen |
| `version` | tal | `3`. Ett version 1-dokument anger en plantering `time` i matchsekunder; från 2 är det sekunder in i rundan, som för en kill. 3 lägger till fälten från `header` och freeze time i tabellen. |
| `match` | sträng | matchnamnet, så som filerna heter |
| `map` | sträng | kartan (`de_x`) |
| `demos` | sträng[] | demofilerna den byggdes av, bara filnamn, i matchordning |
| `teams` | sträng[] | lagnamnen i ordning efter första förekomst (runda 1: T-sidan först) |
| `score` | objekt | lagnamn -> vunna rundor: den sista rundans ställning |
| `winner` | sträng eller null | laget som vann matchen, där inspelningen visar slutet; null för en inspelning som stannar tidigt, en övertid utan vinstpanelen, eller oavgjort |
| `winnerSource` | sträng eller null | hur `winner` är känt: `winPanel` (spelets vinstpanel för matchen), `surrender` (kapitulation), `regulation` (mer än hälften av de ordinarie rundorna) |
| `rounds` | objekt[] | varje komplett runda, i ordning - [nedan](#rounds) |
| `incomplete` | tal[] | rundnummer som avbröts av demons slut och utelämnades |
| `missing` | tal[] | rundnummer före den första som demonerna innehåller: `[1, 2]` när inspelningen startar i runda 3 |
| `halfLength` | tal eller null | rundor i en ordinarie halvlek, från där sidorna först byter plats (`12` i 24-rundorsformatet); null när inspelningen inte visar bytet |
| `pistolRounds` | tal[] | pistolrundorna som `buy` räknas med: runda 1, och rundan efter halvleken när `halfLength` är känt; aldrig en övertidsrunda |
| `players` | objekt[] | resultattavlan - [nedan](#players) |
| `conventions` | objekt | definitionerna bakom siffrorna, [nedan](#conventions) |
| `header` | objekt | den första demons huvud så som parsern ger det: servernamn, patchversion, demoversion, karta |
| `profiles` | objekt | Steam-ID -> det som är oförändrat för en spelare genom matchen: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (senast sedd) |
| `playerInfo` | objekt[] | varje spelare demonerna listar, tränare och kommentatorer med: Steam-ID, namn, lagnummer |
| `skins`, `itemDrops` | objekt[] | vapenskins och föremålsdroppar, där demon har dem (turneringsdemos från sändningen har inga) |
| `chat` | objekt[] | varje chattrad i matchen: tid, runda, spelare, sida, text |
| `events` | objekt[] | varje spelhändelse som inte gäller någon spelare, i tidsordning, med alla sina fält: rundsignaler och faser, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (serverns inställningar när de ändrades), sändningskamerans regi med jakt- och fasta skott, `cs_win_panel_match`, ... |
| `state` | objekt[] | spelets tillstånd där det ändrades: tid, fält, värde - timeouts (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomben (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, de levande spelarna, serverns `match_start_time` och `round_start_time` |
| `selfCheck` | objekt | `completeness`: vart all information i demon tog vägen - per händelsenamn, egenskapsklass, nätverksmeddelande, bildruta och strängtabell dess räknare `seen`, `decoded`, `partial`, `raw` och `lost`, de skrivna sidofilerna, det totala `lost` (0 om inte `--no-bulk`), och de egenskaper parsern listar men inte kan läsa (`unreadProps`). Konventionen: [Konverterare behåller allt](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); sidofilerna: READMEns avsnitt om fullständighet |

## Rundor {#rounds}

| Fält | Typ | Vad |
|---|---|---|
| `number` | tal | rundan, 1-baserad |
| `start` | tal | matchsekunder när freeze time tog slut |
| `end` | tal | matchsekunder när rundan avgjordes |
| `until` | tal | matchsekunder när nästa runda startade (slutet på efterfasen) |
| `winner` | sträng | `T` eller `CT`; tomt vid oavgjort |
| `winnerTeam` | sträng | den vinnande sidans lagnamn; tomt vid oavgjort |
| `reason` | sträng | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` eller `other` |
| `score` | objekt | lagnamn -> vunna rundor efter denna |
| `sides` | objekt | lagnamn -> `T` / `CT` i denna runda |
| `equipment` | objekt | sida -> totalt utrustningsvärde för dess levande spelare vid freeze end, i dollar |
| `buy` | objekt | sida -> `pistol`, `eco`, `force` eller `full` |
| `plant` | objekt eller null | bombplanteringen: `site` (`A` eller `B`; tomt när demon inte anger det), `time` (sekunder **in i rundan**, som för en kill), `player`, `steamid`, `x`, `y`, `z` (spelenheter), `place` (planterarens platsnamn: där bomben låg) |
| `survivors` | objekt | sida -> namnen på de startande spelare som fortfarande levde när rundan avgjordes, sorterade |
| `clutches` | objekt[] | var och en: `player`, `steamid`, `side`, `against` (fiender levande när spelaren blev den sista), `won` |
| `kills` | objekt[] | varje dödsfall i rundan, i ordning - nedan |

Hur de hittas: [Bygga en match](building-matches.md#rounds);
clutchar och överlevare: [Statistik](statistics.md#clutches).

### Rundans kills {#a-rounds-kills}

Varje dödsfall i rundan, efterfasen inräknad:

| Fält | Typ | Vad |
|---|---|---|
| `time` | tal | sekunder **in i rundan** (sedan freeze end) |
| `attacker`, `attackerSide` | sträng | mördaren och dess sida; tomt för världen |
| `victim`, `victimSide` | sträng | offret och dess sida |
| `assister` | sträng eller null | den assisterande spelaren, eller null |
| `flashAssist` | bool | assisten var en flash |
| `weapon` | sträng | så som spelet namnger det |
| `headshot` | bool | |
| `wallbang` | bool | kulan gick igenom något |
| `throughSmoke` | bool | killen skedde genom rök |
| `noscope` | bool | ett vapen med kikare avfyrades utan att kikaren användes |
| `attackerBlind` | bool | mördaren var bländad av en flash |
| `opening` | bool | rundans första kill av en fiende |
| `traded` | bool | detta dödsfall hämnades inom 5 s |
| `trade` | bool | denna kill hämnade en lagkamrat inom 5 s |
| `teamkill` | bool | attacker och victim på samma sida, två olika spelare |
| `suicide` | bool | attacker och victim är samma spelare (en egen granat, till exempel); inte en teamkill |
| `after` | bool | killen kom efter att rundan avgjordes |
| `place` | sträng | var **offret** var (kartans platsnamn) |

## Spelare {#players}

En post per spelare, efter lag och sedan bäst först efter kills minus deaths, sedan kills:

| Fält | Typ | Vad |
|---|---|---|
| `name`, `steamid`, `team` | sträng | vem |
| `kills`, `deaths` | tal | |
| `assists`, `flashAssists` | tal | assists utan och med flash |
| `diff` | tal | kills - deaths |
| `adr` | tal | genomsnittlig skada per spelad runda, förlorad hälsa |
| `kast` | tal | procent av de spelade rundorna med en kill, assist, överlevnad eller trade-död |
| `headshotPct` | tal | procent av kills som var huvudskott |
| `openingKills`, `openingDeaths` | tal | öppningsduellerna vunna och förlorade |
| `tradeKills`, `tradedDeaths` | tal | trade-kills; dödsfall som hämnades |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: rundor med så många kills |
| `clutches`, `clutchesWon` | tal | |
| `utilityDamage` | tal | skada med HE, molotov, incendiary |
| `enemiesFlashed` | tal | fiender bländade minst 1 s |
| `plants`, `defuses` | tal | |
| `teamkills` | tal | lagkamrater dödade; suicide räknas inte |
| `roundsPlayed` | tal | rundor startade |

Varje definition: [Statistik](statistics.md#the-scoreboard-line).

## Konventioner {#conventions}

Skrivna in i varje dokument, så att en läsare vet vad siffrorna betyder utan den här sidan:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Ett exempel {#an-example}

Från den syntetiska tvårundersdemon i testerna, förkortat (`...` markerar det som utelämnats):

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

Ordningen på nycklarna i `survivors`, `equipment` och `buy` är inte fast.
