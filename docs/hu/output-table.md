---
title: "A hőtérképes táblázat"
nav_order: 8
lang: "hu"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# A hőtérképes táblázat (`<match>.parquet`) {#the-heatmap-table}

Egy Parquet-fájl meccsenként: minden élő játékos pozíciója mintavételezve, és minden esemény ott, ahol történt, soronként
egy - egy hosszú táblázat, amelyet a 3DHeat megjelenítő hőtérképként olvas, bármi másként pedig közönséges táblázatként. Kód:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(a fájl), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(a sorok; lásd [Meccs felépítése](building-matches.md)).

A fájl Snappy-tömörítéssel íródik, 256 000 soros sorcsoportokban. A sorok `time` szerint vannak rendezve, azon belül
`event` szerint. Csak az a sor kerül bele, amely egy körön belül van (a kör freeze time-ának végétől a következő kör
kezdetéig).

A teszt szintetikus demóján az első kör eseménysorai:

![eseménysorok a táblázatban](../assets/img/table-rows.svg)

Egy `.3dheat` konténerben a táblázat az a tag, amelynek szerepe `table` ([Egy fájl meccsenként](output-container.md)).

## Oszlopok {#columns}

Az oszlopok mindig ebben a sorrendben vannak. A szöveges oszlopok szótáras kódolású szövegek
(`dictionary<int32, string>`), és sosem nullák: az "nincs érték" egy üres szöveg. A számszerű oszlopok null-ak, ahol egy
sornak nincs értéke.

| Oszlop | Típus | Mi |
|---|---|---|
| `match` | string | a meccs neve (`alpha-vs-bravo-m1`, vagy `...-b` egy második láncnál) |
| `map` | string | a pálya, a demó fejlécéből (`de_x`) |
| `round` | int16 | a kör száma, 1-alapú |
| `roundId` | string | `<match> #NN`, a kör száma két számjeggyel (`alpha-vs-bravo-m1 #07`): meccsek között egyedi, a megjelenítő munkamenete |
| `phase` | string | `freeze` a kör freeze time-ában (az előző kör végétől), `live` amíg a kör el nem dől, `after` amíg a győztesek vadásznak és a vesztesek takarékoskodnak |
| `time` | float64 | másodpercek a meccs kezdete óta (az első fájl élő kezdete), egy közös órán a fájljai között |
| `roundTime` | float32 | másodpercek, mióta a kör freeze time-ja véget ért; negatív a freeze time-ban |
| `event` | string | mi a sor - lásd [Események](#events) |
| `player` | string | a játékos neve (minden eseménynél az alábbi szerint, melyik játékos) |
| `steamid` | string | a játékos Steam-azonosítója (64 bites, szövegként) |
| `side` | string | `T` vagy `CT` ebben a körben; üres, ha a játékos nem volt oldalon |
| `team` | string | a játékos csapatneve (vagy `Started T` / `Started CT`); az `explode`-nál a lerakó csapat |
| `x`, `y`, `z` | float32 | pozíció a játék saját koordinátáiban: hüvelyk (játékegység), **Z felfelé**, jobbsodrású |
| `dirX`, `dirY`, `dirZ` | float32 | ahová a játékos néz, egységvektor ugyanabban a koordinátarendszerben; csak pozícióknál |
| `health` | int16 | 0-100; pozícióknál, és `hurt`-nél az, ami a találat után maradt |
| `armor` | int16 | 0-100; pozícióknál, és `hurt`-nél az, ami a találat után maradt |
| `money` | int32 | a játékos pénze; csak pozícióknál |
| `equipment` | int32 | a játékos által hordott felszerelés értéke; csak pozícióknál |
| `weapon` | string | a fegyver, ahogy a játék nevezi (`AK-47`, `M4A1-S`, `Knife` minden késskinre) |
| `place` | string | a pálya saját helynéve a sor pozíciójánál (`BombsiteA`, `CTSpawn`); üres a gránátrobbanásoknál: a demó nem mond helyet annak, hol robbant fel a gránát |
| `throwerPlace` | string | a dobó helynéve, amikor a gránát felrobbant; csak gránátrobbanásoknál |
| `other` | string | a gyilkosság, halál, találat vagy villanás másik játékosa |
| `damage` | float32 | elvesztett életerő; csak `hurt`-nél |
| `duration` | float32 | a vakítás másodpercben; csak `blind`-nál |
| `headshot` | int8 | 0/1; csak `kill` és `death`-nél |
| `opening` | int8 | 0/1, a kör első gyilkossága egy ellenségen; csak `kill` és `death`-nél |
| `traded` | int8 | 0/1. `kill`-nél: trade-gyilkosság volt. `death`-nél: 5 másodpercen belül megbosszulták. Csak `kill` és `death`-nél. |
| `noscope` | int8 | 0/1, a gyilkosság távcsöves fegyverrel történt távcső nélkül (az esemény `noscope`-ja); csak `kill` és `death`-nél |
| `attackerBlind` | int8 | 0/1, a gyilkos meg volt villanva, amikor megölt (az esemény `attackerblind`-ja); csak `kill` és `death`-nél |
| `won` | int8 | 0/1, megnyerte-e a sor oldala a kört; null, ha a `side` üres |
| `matchWon` | int8 | 0/1, megnyerte-e a sor csapata a meccset; null, ha a `team` üres, vagy a felvétel nem mutatja a végét (lásd a meccsdokumentum `winner`-ét) |
| `roundEndReason` | string | hogyan ért véget a sor köre: `elimination`, `bomb` (a bomba felrobbant), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | string | a sor oldalának vásárlása abban a körben: `pistol`, `eco`, `force`, `full` |
| `detail` | string | az esemény minden mezője, amelyet a többi oszlop nem visz, JSON-objektumként (a játék saját nevein): egy lövés golyói (`fire_bullets`: kiindulás, szögek, pontatlanság, szórás, visszarúgás-index, mag...), egy halál `dominated`, `revenge`, `attackerinair`, `wipe`... mezői, egy tárgy `defindex`-e, egy lépés semmije |
| `text` | string | egy chat-sor; csak `chat`-nél |
| `entity` | int32 | a gránát entitása: egy `throw` repülése (`grenade` sorok), a robbanása és az általa megvakított játékosok ugyanazt használják |
| `hitgroup` | string | hol talált a golyó (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | elvesztett páncél; csak `hurt`-nél |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | hol talált a golyó a test felületén, az áldozat koordinátarendszerében méterben (x előre, y a talptól felfelé, z jobbra): a lövés sugara (`fire_bullets`, különben a támadó szeme és nézete), visszavezetve egy testre, amelyet úgy pózolunk, ahogy az áldozat állt és guggolt, arra a részre, amelyet a `hitgroup` nevez; csak `hurt`-nél |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | a lövés iránya ugyanabban a koordinátarendszerben; a `hitMiss` megmondja, mennyivel (m) ment a sugár a megnevezett rész mellett (0: átment rajta); a `hitFrom` `bullet` vagy `aim` |
| `penetrated` | int16 | a falak, amelyeken a gyilkos golyó átment; `kill` és `death` |
| `throughSmoke` | int8 | 0/1, füstön át ölt; `kill` és `death` |
| `distance` | float32 | a gyilkosság távolsága, ahogy a játék számolja (méter); `kill` és `death` |
| `assister` | string | ki asszisztált; `kill` és `death` |
| `flash`, `flashAlpha` | float32 | a villanás hátralévő másodpercei, és mennyire fehér; pozíciók |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozíciók |
| `zoom`, `duck`, `moveType` | | a távcső nagyítási szintje, mennyire guggol (0-1), a játék mozgástípusa; pozíciók |
| `spottedBy` | string | azoknak az ellenségeknek a Steam-azonosítói, akik látják ezt a játékost, `\|`-vel elválasztva; pozíciók |
| `inventory` | string | minden, amit a játékos hord, `\|`-vel elválasztva; pozíciók |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | a kézben tartott fegyver tára és tartaléka; az aktuális sorozat lövései; pozíciók |
| `punchPitch`, `punchYaw` | float32 | a visszarúgás célzás-lökése, fokban; pozíciók |
| `ping` | int16 | ezredmásodpercben; pozíciók |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | a játék saját eredménytábla-számai a meccsre eddig; pozíciók |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | a körben és a meccsen elköltött pénz; a felszerelési érték, amikor a kör kezdődött; pozíciók |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, a játékos állapota a sor idejénél, az események is beleértve: sisak, bontókészlet, bármilyen páncél, távcsöves (a játékos utolsó pozíció-mintájától a sorig), villantott (egy őket érintő `blind` alatt); minden sornál, amely játékost nevez meg |
| `state_utility` | int16 | az idő szerint hordott gránátok (a `inventory`-ból); minden sornál, amely játékost nevez meg |
| `state_weapon` | string | az idő szerint kézben tartott fegyver (halálnál az áldozaté, ahol a `weapon` a gyilkosé); minden sornál, amely játékost nevez meg |
| `earn_round_cs2` | int16 | mennyit fizetett a kör: a `round_end`-nél a győzelmi jutalom vagy a vesztes-bónusz (a lerakó oldal bónuszával), a `plant` és `defuse`-nál a játékos 300-a |

## Események {#events}

Melyik játékost nevezi meg egy sor, hol áll, és melyik oszlopokat tölti ki.
A `match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won`, `roundEndReason` és `buy` minden sorban
ki van töltve (a `matchWon` ott, ahol a meccs győztese ismert); az `inventory`, `money`, `equipment` és a `state_*`
oszlopok minden játékost megnevező sorban (az események a játékos utolsó pozíció-mintájából veszik).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Még kitöltve |
|---|---|---|---|
| `position` | a játékos | a játékos (a talpa) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (kézben), `place`, és a játékos teljes állapota (a `flash`-tól kezdődő oszlopok) - a freeze time-ban is |
| `kill` | a gyilkos | ahol a gyilkos állt | `other` (áldozat), `weapon`, `headshot`, `opening`, `traded` (trade-gyilkosság), `noscope`, `attackerBlind`, `place` |
| `death` | az áldozat | ahol az áldozat elesett | `other` (gyilkos; üres a világnál), `weapon`, `headshot`, `opening`, `traded` (megbosszulva), `noscope`, `attackerBlind`, `place` |
| `hurt` | az áldozat | ahol az áldozatot eltalálták | `other` (támadó), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - a csapattársak és a világ találatai is |
| `shot` | a lövő | ahonnan a lövést leadták | `weapon`, `place`, `detail` (a játék beszámolója a golyókról) |
| `slash` | a játékos | ahol a kést lendítették | `weapon` = `Knife` |
| `grenade` | a dobó | a repülő gránát, a játékosok mintavételezésénél és ott, ahol megállt | `weapon` (a gránát), `entity` |
| `throw` | a dobó | ahonnan a gránátot dobták | `weapon` (a gránát), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | a dobó | ahol felrobbant | `weapon`, `throwerPlace` (a dobó helye abban a pillanatban); a `place` üres marad |
| `blind` | a megvakított játékos | ahol álltak | `other` (a villantó), `duration`, `weapon` = `Flashbang`, `entity`, `place` - a megvakított csapattársak is |
| `plant` | a lerakó | ahol lerakták | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | a hatástalanító | ahol hatástalanították | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | minden játékos, aki játszotta a kört | ahol a játékos utoljára állt | `won`, `earn_round_cs2` (mennyit fizetett neki a kör: az oldal pénzének emelkedése a következő freeze time-ig, ahol a szabályok engedik, különben a szabályok saját összege), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | a lerakó (a Steam-azonosítójával), `T` oldal, a lerakó csapat | a lerakás pozíciója | `weapon` = `C4 Explosive`, `place` (a lerakó helye a lerakásnál: ahol a bomba feküdt); az ideje az, amikor a bomba felrobbant |
| `chat` | a küldő | ahol volt | `text` |
| minden más játékos-esemény a játék nevén: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | a játékos | ahol volt (egy gránát eseményeinél: ahol a gránát volt) | `weapon` (egy tárgyé), `entity`, `detail` (az esemény minden mezője) |

Mi benne van, és mi nincs:

- A **position** sorok az élő, oldalon lévő játékosok, freeze time-on és bemelegítésen kívül, minden `--every` tickenként
  (alapértelmezetten másodpercenként nyolc).
- A **kill** sorok csak az ellenség által okozott gyilkosságok - nincs csapattárs-ölés, öngyilkosság vagy a világnak okozott
  halál. A **death** sorok minden halál, azok is.
- Az **explode** sorok minden felrobbant lerakott bombáról szólnak, a demó `bomb_exploded` eseménye szerint: az utána fázisban
  is, ha a T-k már eliminálással nyertek. Egy olyan demó, amelyben nincs ez az esemény, minden bomba által nyert körre
  kap egyet, a kör végénél.
- A **hurt** és **blind** sorok csak ellenségek között vannak.
- A **shot** kihagyja a késeket és a C4-et; a gránátok a **throw** sorok.
- A **molotov** a molotovokat és az incendiary-ket fedi (a tűz kezdete).
- A csapattársak sebzése, a csapattársak és a nézők villanásai, a freeze time-os események és a körök közötti dolgok nincsenek
  a táblázatban.

Egy példa a teszt szintetikus demójából (egy füstgránát dobása, egy fejlövéses nyitógyilkosság, trade-ek):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

bob halálát ben 1,9 másodperccel később megbosszulja, azzal, hogy megöli acet (bob `death` sora: traded 1; ben `kill` sora:
trade-gyilkosság, traded 1); bobon a második találat 137 sebzés volt 40 életerőn, így 40-et számít.

## A `heat3d` lábléc-tippek {#the-heat3d-footer-hints}

A fájl Parquet-lábléce (a séma kulcs/érték metaadatai) olvasási utasításokat hordoz a **`heat3d`** kulcs alatt, egy JSON-
objektumban:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "matchWon", "roundEndReason", "buy", "opening", "team", ...]
  }
}
```

| Bejegyzés | Mit mond |
|---|---|
| `version`, `kind` | a tippek verziója (1) és az, ami írta (`cs2-demo`) |
| `axes.up` | a fájl Z-je felfelé mutat |
| `axes.flipY` | a fájl Y-ját negálni kell (lásd lent) |
| `axes.scale` | 1: a pozíciókat úgy használjuk, ahogy vannak, játékegységekben |
| `entity.size` | egy játékos **32 egység** széles - a CS2-játékos szélessége -, ekkora rajzol egy dobozos visszajátszás |
| `columns.x` / `y` / `z` | a pozíció-oszlopok |
| `columns.time`, `timeUnit` | a `time`, másodpercben |
| `columns.personId` | a játékos a személy |
| `columns.teamId` | az oldal a csoport (tehát a T és a CT, nem a csapatnevek színezik a csoportokat) |
| `columns.sessionId` | minden kör (`roundId`) egy munkamenet |
| `columns.lookMode` és `dirX`-`dirZ` | a nézési irány vektor azokban az oszlopokban |
| `columns.extra` | a szűrőként megtartandó oszlopok, a hasznosságuk sorrendjében |

Az a megjelenítő, amely ismeri a kulcsot, beállítás nélkül megnyitja a fájlt. Minden más figyelmen kívül hagyja. Hogy magad
olvasd:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Tengelyek és egységek {#axes-and-units}

A koordináták a játék saját koordinátái: **hüvelyk** (egy játékegység; egy játékos állva 72 egység magas, és 32 széles),
**Z felfelé**, és jobbsodrásúak.

Egy megjelenítő, amelynek a világa Y-felfelé van, a játék (x, y, z) pontjait **(x, z, -y)** alakban rajzolja - a Z lesz a
magasság, az Y negálva. Ez forgatás, nem tükrözés. Ha úgy rajzolnánk, ahogy egy balkezes, Z-felfelé világ rajzolódik, (x, z, y)
alakban, minden pálya tükrözve jönne ki, az A-bombazóna a rossz oldalon; a `flipY: true` az, amit a tippek azért mondanak,
hogy ezt megakadályozzák. A [pályaexport](map-export.md) a geometriáját már az (x, z, -y) koordinátarendszerben írja, ugyanazokban
az egységekben, így a táblázat alá esik, bármilyen igazítás nélkül.

A megjelenítőben a távolságok méterben vannak feliratozva; 1-es skálánál játékegységek. Méterre 0,0254-gyel szorozz.

## Méret {#size}

A pozíciók dominálnak: nagyjából tíz játékos x 8 minta másodpercenként az élő játékban, az alapértelmezett `--every 8`
mellett, kevesebb a halott játékosoknál és a freeze time-ban. A `--every` felezése a pozíciókat megduplázza; az események
nem változnak.
