---
title: "A meccsdokumentum"
nav_order: 9
lang: "hu"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# A meccsdokumentum (`<match>.match.json`) {#the-match-document}

Meccsenként egy JSON-dokumentum, a táblázata mellett: csapatok, állás, minden kör az eredményével, a gazdaság, a lerakás,
az ölések, a klucsok és a túlélők, és minden játékos eredménytáblasora. Ezt tölti be a 3DHeat megjelenítő **Meccs** fülén.
Kód: a `summary()` a
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) fájlban; a számok
meghatározását a [Statisztika](statistics.md) oldal adja.

A fájl UTF-8, egy szóközzel behúzva, és a nem ASCII karaktereket (játékos- és csapatneveket) úgy tartja meg, ahogy vannak.
Az idő másodperc: a köröknél háromjegyre, a gyilkosságoknál és a lerakásnál kettőre kerekítve.

## A dokumentum {#the-document}

| Mező | Típus | Mi |
|---|---|---|
| `format` | string | mindig `heat3d-cs2-match` - ebből ismeri fel az olvasó a fájlt |
| `version` | number | `3`. Az 1-es verziójú dokumentum egy lerakás `time`-ját meccsmásodpercben adja meg; a 2-estől a körbe eltelt másodpercekben, ahogy a gyilkosságoknál. A 3 a `header`-től kezdve új mezőket ad hozzá, és a freeze time-ot a táblázathoz. |
| `match` | string | a meccs neve, ahogy a fájlok nevezve vannak |
| `map` | string | a pálya (`de_x`) |
| `demos` | string[] | a demófájlok, amelyekből épült, csak a fájlnevek, a meccs sorrendjében |
| `teams` | string[] | a csapatnevek a megjelenés sorrendjében (1. kör: a T-oldal előbb) |
| `score` | object | csapatnév -> megnyert körök: az utolsó kör állása |
| `winner` | string vagy null | a meccset megnyerő csapat, ahol a felvétel mutatja a végét; null egy korán megálló felvételnél, egy győzelmi panel nélküli hosszabbításnál vagy döntetlennél |
| `winnerSource` | string vagy null | honnan tudjuk a `winner`-t: `winPanel` (a játék meccsgyőzelmi panelje), `surrender`, `regulation` (a szabályos körök több mint fele) |
| `rounds` | object[] | minden teljes kör, sorrendben - [lent](#rounds) |
| `incomplete` | number[] | a demó végén megszakadt és kihagyott körök sorszámai |
| `missing` | number[] | a sorszámok az első, a demókban lévő kör előtt: `[1, 2]`, ha a felvétel a 3. körnél indul |
| `halfLength` | number vagy null | egy szabályos félidő körei, attól, ahol az oldalak először cserélnek (`12` a 24 körös formátumban); null, ha a felvétel nem mutatja a cserét |
| `pistolRounds` | number[] | azok a pisztolykörök, amelyekkel a `buy` számolódik: az 1. kör, és a félidő utáni kör, ha a `halfLength` ismert; sosem hosszabbítási kör |
| `players` | object[] | az eredménytábla - [lent](#players) |
| `conventions` | object | a számok mögötti meghatározások, [lent](#conventions) |
| `header` | object | az első demó fejléce, ahogy a parser adja: szerver neve, javítás-verziója, demóverzió, pálya |
| `profiles` | object | Steam-azonosító -> ami egy játékosnál a meccs alatt végig ugyanaz marad: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (az utoljára látott) |
| `playerInfo` | object[] | minden játékos, akit a demók felsorolnak, az edzők és a kasztereket is: Steam-azonosító, név, csapatszám |
| `skins`, `itemDrops` | object[] | fegyverskinek és tárgydobások, ahol a demó tartalmazza (a közvetítésből készült versenydemókban nincs) |
| `chat` | object[] | a meccs minden chat-sora: idő, kör, játékos, oldal, szöveg |
| `events` | object[] | minden játékesemény, amely nem köthető játékoshoz, időrendben, minden mezőjével: körjelzések és fázisok, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (a szerver beállításai, ahogy változtak), a közvetítő kamera-rendező követő és fix felvételei, `cs_win_panel_match`, ... |
| `state` | object[] | a játék állapota, ahol változott: idő, mező, érték - időkérések (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), a bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, az élő játékosok, a szerver `match_start_time` és `round_start_time` |
| `selfCheck` | object | `completeness`: hová ment a demó minden része - eseménynév, tulajdonságosztály, hálózati üzenet, képkocka és string-tábla szerint a `seen`, `decoded`, `partial`, `raw` és `lost` számok, a megírt kísérőfájlok, az összes `lost` (0, hacsak nincs `--no-bulk`), és azok a tulajdonságok, amelyeket a parser felsorol, de nem tud olvasni (`unreadProps`). A konvenció: [A konvertálók mindent megtartanak](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); a kísérőfájlok: a README Teljesség része |

## Körök {#rounds}

| Mező | Típus | Mi |
|---|---|---|
| `number` | number | a kör, 1-alapú |
| `start` | number | meccsmásodpercek, amikor a freeze time véget ért |
| `end` | number | meccsmásodpercek, amikor a kör eldőlt |
| `until` | number | meccsmásodpercek, amikor a következő kör kezdődött (az utána fázis vége) |
| `winner` | string | `T` vagy `CT`; döntetlennél üres |
| `winnerTeam` | string | a győztes oldal csapatneve; döntetlennél üres |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` vagy `other` |
| `score` | object | csapatnév -> megnyert körök ez után |
| `sides` | object | csapatnév -> `T` / `CT` ebben a körben |
| `equipment` | object | oldal -> az élő játékosai összes felszerelési értéke a freeze end-nél, dollárban |
| `buy` | object | oldal -> `pistol`, `eco`, `force` vagy `full` |
| `plant` | object vagy null | a bomba lerakása: `site` (`A` vagy `B`; üres, ha a demó nem mondja meg), `time` (másodpercek **a körbe**, ahogy a gyilkosságnál), `player`, `steamid`, `x`, `y`, `z` (játékegységek), `place` (a lerakó helynéve: ahol a bomba feküdt) |
| `survivors` | object | oldal -> a kezdő játékosok neveinek listája, akik még éltek, amikor a kör eldőlt, betűrendben |
| `clutches` | object[] | minden: `player`, `steamid`, `side`, `against` (az ellenségek száma, akik még éltek, amikor a játékos az utolsó lett), `won` |
| `kills` | object[] | a kör minden halála, sorrendben - lent |

Hogyan találjuk meg ezeket: [Meccs felépítése](building-matches.md#rounds); a klucsok és a túlélők:
[Statisztika](statistics.md#clutches).

### Egy kör gyilkosságai {#a-rounds-kills}

A körben minden halál, a utána fázist is beleértve:

| Mező | Típus | Mi |
|---|---|---|
| `time` | number | másodpercek **a körbe** (a freeze end óta) |
| `attacker`, `attackerSide` | string | a gyilkos és az oldala; a világnál üres |
| `victim`, `victimSide` | string | az áldozat és az oldala |
| `assister` | string vagy null | az asszisztáló játékos, vagy null |
| `flashAssist` | bool | az asszisztálás villanás volt |
| `weapon` | string | ahogy a játék nevezi |
| `headshot` | bool | |
| `wallbang` | bool | a golyó átment valamin |
| `throughSmoke` | bool | a gyilkosság füstön át történt |
| `noscope` | bool | egy távcsöves fegyver távcső nélkül lőtt |
| `attackerBlind` | bool | a gyilkos meg volt villanva |
| `opening` | bool | a kör első gyilkossága egy ellenségen |
| `traded` | bool | ezt a halált 5 másodpercen belül megbosszulták |
| `trade` | bool | ez a gyilkosság 5 másodpercen belül megbosszult egy csapattársat |
| `teamkill` | bool | a támadó és az áldozat ugyanazon az oldalon, két különböző játékos |
| `suicide` | bool | a támadó és az áldozat ugyanaz a játékos (például a saját gránátja); nem csapattárs-ölés |
| `after` | bool | a gyilkosság azután történt, hogy a kör eldőlt |
| `place` | string | hol volt az **áldozat** (a pálya helynéve) |

## Játékosok {#players}

Játékosonként egy bejegyzés, csapatnév szerint, majd a gyilkosság mínusz halál, majd a gyilkosság szerint, a legjobb elöl:

| Mező | Típus | Mi |
|---|---|---|
| `name`, `steamid`, `team` | string | ki |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | asszisztok villanás nélkül és villanással |
| `diff` | number | gyilkosság - halál |
| `adr` | number | átlagos sebzés lejátszott körönként, elvesztett életerő |
| `kast` | number | a lejátszott körök százaléka, amelyekben volt gyilkosság, asszisztálás, túlélés vagy megbosszult halál |
| `headshotPct` | number | a gyilkosságok százaléka, amelyek fejlövések voltak |
| `openingKills`, `openingDeaths` | number | megnyert és elvesztett nyitó párharcok |
| `tradeKills`, `tradedDeaths` | number | trade-gyilkosságok; megbosszult halálok |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: hány körben volt ennyi gyilkossága |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | HE-val, molotovval, incendiary-vel okozott sebzés |
| `enemiesFlashed` | number | legalább 1 másodpercig megvakított ellenségek |
| `plants`, `defuses` | number | |
| `teamkills` | number | megölt csapattársak; az öngyilkosságok nem számítanak |
| `roundsPlayed` | number | elkezdett körök |

Minden meghatározás: [Statisztika](statistics.md#the-scoreboard-line).

## Konvenciók {#conventions}

Minden dokumentumba beleírva, hogy az olvasó e oldal nélkül is tudja, mit jelentenek a számok:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Példa {#an-example}

A teszt szintetikus, két körös demójából, rövidítve (a `...` jelzi, mit hagytunk ki):

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

A `survivors`, `equipment` és `buy` kulcsainak sorrendje nincs rögzítve.
