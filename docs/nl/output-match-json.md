---
title: Het matchdocument
nav_order: 9
lang: "nl"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Het matchdocument (`<match>.match.json`) {#the-match-document-matchjson}

Één JSON-document per wedstrijd, naast zijn tabel: teams, score, elke ronde met zijn resultaat, economie, plant, kills, clutches en overlevenden, en de scoreboardregel van elke speler. Het is wat het tabblad Match van de 3DHeat-viewer laadt. Code: `summary()` in [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py); de getallen zijn gedefinieerd op [Statistieken](statistics.md).

Het bestand is UTF-8, met één spatie inspringing, en behoudt niet-ASCII-tekens (namen van spelers en teams) zoals ze zijn. Tijden staan in seconden, afgerond op drie decimalen voor rondes en twee voor kills en de plant.

## Het document {#the-document}

| Veld | Type | Wat |
|---|---|---|
| `format` | tekst | altijd `heat3d-cs2-match` - waaraan een lezer het bestand herkent |
| `version` | getal | `3`. Een document van versie 1 geeft de `time` van een plant in matchseconden; vanaf 2 is het seconden in de ronde, zoals bij een kill. 3 voegt de velden vanaf `header` toe, en freeze time aan de tabel. |
| `match` | tekst | de matchnaam, zoals de bestanden heten |
| `map` | tekst | de map (`de_x`) |
| `demos` | tekst[] | de demobestanden waaruit hij is opgebouwd, alleen bestandsnamen, in matchvolgorde |
| `teams` | tekst[] | de teamnamen in volgorde van verschijnen (ronde 1: de T-kant eerst) |
| `score` | object | teamnaam -> gewonnen rondes: de score van de laatste ronde |
| `rounds` | object[] | elke volledige ronde, in volgorde - [hieronder](#rondes) |
| `incomplete` | getal[] | rondenummers die door het einde van een demo zijn afgebroken en weggelaten |
| `missing` | getal[] | rondenummers vóór de eerste die de demo's bevatten: `[1, 2]` wanneer de opname begint bij ronde 3 |
| `halfLength` | getal of null | rondes in een reguliere helft, vanaf waar de kanten voor het eerst wisselen (`12` in het formaat van 24 rondes); null wanneer de opname de wissel niet toont |
| `pistolRounds` | getal[] | de pistoolrondes waarmee de `buy` wordt geteld: ronde 1, en de ronde na de helft wanneer `halfLength` bekend is; nooit een overtime-ronde |
| `players` | object[] | het scorebord - [hieronder](#spelers) |
| `conventions` | object | de definities achter de getallen, [hieronder](#conventies) |
| `header` | object | de header van de eerste demo zoals de parser hem geeft: servernaam, patchversie, demoversie, map |
| `profiles` | object | Steam-ID -> wat voor een speler gedurende de wedstrijd gelijk blijft: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (laatst gezien) |
| `playerInfo` | object[] | elke speler die de demo's noemen, ook coaches en casters: Steam-ID, naam, teamnummer |
| `skins`, `itemDrops` | object[] | wapenskins en itemdrops, waar de demo ze heeft (toernooidemo's uit de uitzending hebben er geen) |
| `chat` | object[] | elke chatregel in de wedstrijd: tijd, ronde, speler, kant, tekst |
| `events` | object[] | elke spelgebeurtenis die over geen speler gaat, in tijdsvolgorde, met al zijn velden: rondesignalen en -fasen, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (de instellingen van de server zoals ze veranderden), de cameraregie van de uitzending met volgcamera- en vaste shots, `cs_win_panel_match`, ... |
| `state` | object[] | de spelstatus waar die veranderde: tijd, veld, waarde - time-outs (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), de bom (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, de levende spelers, de `match_start_time` en `round_start_time` van de server |
| `selfCheck` | object | `completeness`: waar alles van de demo naartoe is gegaan - per gebeurtenisnaam, eigenschapsklasse, netwerkbericht, frame en stringtabel de tellingen `seen`, `decoded`, `partial`, `raw` en `lost`, de geschreven zijbestanden, het totaal `lost` (0 tenzij `--no-bulk`), de eigenschappen die de parser noemt maar niet kan lezen (`unreadProps`). De conventie: [Converters bewaren alles](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); de zijbestanden: het gedeelte Completeness in de README |

## Rondes {#rounds}

| Veld | Type | Wat |
|---|---|---|
| `number` | getal | de ronde, 1-gebaseerd |
| `start` | getal | matchseconden wanneer de freeze time eindigde |
| `end` | getal | matchseconden wanneer de ronde was beslist |
| `until` | getal | matchseconden wanneer de volgende ronde begon (het einde van de after-fase) |
| `winner` | tekst | `T` of `CT`; leeg bij een gelijkspel |
| `winnerTeam` | tekst | de teamnaam van de winnende kant; leeg bij een gelijkspel |
| `reason` | tekst | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` of `other` |
| `score` | object | teamnaam -> gewonnen rondes na deze |
| `sides` | object | teamnaam -> `T` / `CT` in deze ronde |
| `equipment` | object | kant -> totale waarde van de uitrusting van haar levende spelers bij freeze end, in dollars |
| `buy` | object | kant -> `pistol`, `eco`, `force` of `full` |
| `plant` | object of null | de bomplant: `site` (`A` of `B`; leeg wanneer de demo het niet zegt), `time` (seconden **in de ronde**, zoals bij een kill), `player`, `steamid`, `x`, `y`, `z` (game-eenheden), `place` (de plaatsnaam van de planter: waar de bom lag) |
| `survivors` | object | kant -> namen van de startende spelers die nog leefden toen de ronde was beslist, gesorteerd |
| `clutches` | object[] | elk: `player`, `steamid`, `side`, `against` (vijanden die nog leefden toen de speler de laatste werd), `won` |
| `kills` | object[] | elke dood van de ronde, in volgorde - hieronder |

Hoe deze worden gevonden: [Een wedstrijd opbouwen](building-matches.md#rondes); clutches en overlevenden: [Statistieken](statistics.md#clutches).

### De kills van een ronde {#a-rounds-kills}

Elke dood in de ronde, ook die in de after-fase:

| Veld | Type | Wat |
|---|---|---|
| `time` | getal | seconden **in de ronde** (sinds freeze end) |
| `attacker`, `attackerSide` | tekst | de killer en zijn kant; leeg bij de wereld |
| `victim`, `victimSide` | tekst | het slachtoffer en zijn kant |
| `assister` | tekst of null | de assisterende speler, of null |
| `flashAssist` | bool | de assist was een flits |
| `weapon` | tekst | zoals de game het noemt |
| `headshot` | bool | |
| `wallbang` | bool | de kogel ging door iets heen |
| `throughSmoke` | bool | de kill was door rook |
| `noscope` | bool | een wapen met kijker is afgevuurd zonder kijker |
| `attackerBlind` | bool | de killer was geflitst |
| `opening` | bool | de eerste kill van een vijand in de ronde |
| `traded` | bool | deze dood is binnen 5 s gewroken |
| `trade` | bool | deze kill heeft binnen 5 s een teamgenoot gewroken |
| `teamkill` | bool | aanvaller en slachtoffer aan dezelfde kant, twee verschillende spelers |
| `suicide` | bool | aanvaller en slachtoffer zijn dezelfde speler (bijvoorbeeld een eigen granaat); geen teamkill |
| `after` | bool | de kill kwam nadat de ronde was beslist |
| `place` | tekst | waar het **slachtoffer** was (de plaatsnaam van de map) |

## Spelers {#players}

Eén item per speler, per team, en dan de beste eerst op kills min deaths, dan kills:

| Veld | Type | Wat |
|---|---|---|
| `name`, `steamid`, `team` | tekst | wie |
| `kills`, `deaths` | getal | |
| `assists`, `flashAssists` | getal | assists zonder en met een flits |
| `diff` | getal | kills - deaths |
| `adr` | getal | gemiddelde schade per gespeelde ronde, verloren gezondheid |
| `kast` | getal | procent van de gespeelde rondes met een kill, assist, overleving of gewroken dood |
| `headshotPct` | getal | procent van de kills die headshots waren |
| `openingKills`, `openingDeaths` | getal | gewonnen en verloren openingsduels |
| `tradeKills`, `tradedDeaths` | getal | trade-kills; doden die zijn gewroken |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: rondes met zoveel kills |
| `clutches`, `clutchesWon` | getal | |
| `utilityDamage` | getal | schade met HE, molotov, incendiary |
| `enemiesFlashed` | getal | vijanden die minstens 1 s verblind zijn |
| `plants`, `defuses` | getal | |
| `teamkills` | getal | teamgenoten gedood; suïcides tellen niet mee |
| `roundsPlayed` | getal | gestarte rondes |

Elke definitie: [Statistieken](statistics.md#de-scoreboardregel).

## Conventies {#conventions}

In elk document geschreven, zodat een lezer weet wat de getallen betekenen zonder deze pagina:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Een voorbeeld {#an-example}

Uit de synthetische demo met twee rondes uit de tests, ingekort (`...` markeert wat is weggelaten):

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

De volgorde van de sleutels binnen `survivors`, `equipment` en `buy` ligt niet vast.
