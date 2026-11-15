---
title: De heatmaptabel
nav_order: 8
lang: "nl"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# De heatmaptabel (`<match>.parquet`) {#the-heatmap-table-parquet}

Eén Parquet-bestand per wedstrijd: de positie van elke levende speler, bemonsterd, en elke gebeurtenis waar die plaatsvond, elk één rij - een lange tabel die de 3DHeat-viewer leest als heatmap, en al het andere als een gewone tabel. Code: [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) (het bestand), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) (de rijen; zie [Een wedstrijd opbouwen](building-matches.md)).

Het bestand wordt geschreven met Snappy-compressie, in rijgroepen van 256.000 rijen. De rijen zijn gesorteerd op `time`, daarna op `event`. Alleen rijen binnen een ronde (van het einde van de freeze time van die ronde tot het begin van de volgende ronde) staan erin.

Op de synthetische demo uit de tests, de gebeurtenisrijen van de eerste ronde:

![gebeurtenisrijen van de tabel](../assets/img/table-rows.svg)

In een `.3dheat`-container is de tabel het item met de rol `table` ([Eén bestand per match](output-container.md)).

## Kolommen {#columns}

De kolommen, altijd in deze volgorde. Tekstkolommen zijn woordenboekgecodeerde tekenreeksen (`dictionary<int32, string>`) en zijn nooit leeg: "geen waarde" is een lege tekenreeks. Numerieke kolommen zijn null waar een rij geen waarde heeft.

| Kolom | Type | Wat |
|---|---|---|
| `match` | tekst | de matchnaam (`alpha-vs-bravo-m1`, of `...-b` voor een tweede keten) |
| `map` | tekst | de map, uit de header van de demo (`de_x`) |
| `round` | int16 | het rondenummer, 1-gebaseerd |
| `roundId` | tekst | `<match> #NN`, het rondenummer in twee cijfers (`alpha-vs-bravo-m1 #07`): uniek over wedstrijden heen, de sessie van de viewer |
| `phase` | tekst | `freeze` in de freeze time van de ronde (vanaf het einde van de vorige ronde), `live` tot de ronde is beslist, `after` terwijl de winnaars jagen en de verliezers sparen |
| `time` | float64 | seconden sinds de wedstrijd begon (het live-begin van zijn eerste bestand), op één klok over zijn bestanden heen |
| `roundTime` | float32 | seconden sinds de freeze time van deze ronde eindigde; negatief in freeze time |
| `event` | tekst | wat de rij is - zie [Gebeurtenissen](#gebeurtenissen) |
| `player` | tekst | de naam van de speler (bij elke gebeurtenis, welke speler hieronder staat) |
| `steamid` | tekst | de Steam-ID van de speler (64-bit, als tekst) |
| `side` | tekst | `T` of `CT` in deze ronde; leeg wanneer de speler aan geen kant stond |
| `team` | tekst | de teamnaam van de speler (of `Started T` / `Started CT`); voor `explode`, het planterende team |
| `x`, `y`, `z` | float32 | positie in de eigen coördinaten van de game: inches (game-eenheden), **Z omhoog**, rechtshandig |
| `dirX`, `dirY`, `dirZ` | float32 | waar de speler naar kijkt, een eenheidsvector in hetzelfde assenstelsel; alleen posities |
| `health` | int16 | 0-100; posities, en bij `hurt` wat er na de treffer over was |
| `armor` | int16 | 0-100; posities, en bij `hurt` wat er na de treffer over was |
| `money` | int32 | het geld van de speler; alleen posities |
| `equipment` | int32 | de waarde van wat de speler draagt; alleen posities |
| `weapon` | tekst | het wapen zoals de game het noemt (`AK-47`, `M4A1-S`, `Knife` voor elk mes) |
| `place` | tekst | de eigen plaatsnaam van de map op de positie van de rij (`BombsiteA`, `CTSpawn`); leeg bij ontploffingen van granaten: de demo noemt geen plek voor waar een granaat afging |
| `throwerPlace` | tekst | de plaatsnaam van de gooier toen de granaat afging; alleen bij ontploffingen van granaten |
| `other` | tekst | de andere speler van een kill, dood, treffer of flits |
| `damage` | float32 | verloren gezondheid; alleen `hurt` |
| `duration` | float32 | seconden verblind; alleen `blind` |
| `headshot` | int8 | 0/1; alleen `kill` en `death` |
| `opening` | int8 | 0/1, de eerste kill van een vijand in de ronde; alleen `kill` en `death` |
| `traded` | int8 | 0/1. Voor een `kill`: het was een trade-kill. Voor een `death`: het is binnen 5 s gewroken. Alleen `kill` en `death`. |
| `noscope` | int8 | 0/1, de kill was met een wapen met kijker zonder kijker afgevuurd (de `noscope` van de gebeurtenis); alleen `kill` en `death` |
| `attackerBlind` | int8 | 0/1, de killer was geflitst toen hij kilde (de `attackerblind` van de gebeurtenis); alleen `kill` en `death` |
| `won` | int8 | 0/1, of de kant van deze rij de ronde won; null wanneer `side` leeg is |
| `buy` | tekst | de buy van de kant van deze rij in deze ronde: `pistol`, `eco`, `force`, `full` |
| `detail` | tekst | elk veld van de gebeurtenis dat de andere kolommen niet hebben, als JSON-object (de eigen namen van de game): de kogels van een schot (`fire_bullets`: oorsprong, hoeken, onnauwkeurigheid, spreiding, recoilindex, seed...), de `dominated`, `revenge`, `attackerinair`, `wipe`... van een dood, de `defindex` van een item, en bij een voetstap niets |
| `text` | tekst | een chatregel; alleen `chat` |
| `entity` | int32 | de entiteit van de granaat: de vlucht van een `throw` (`grenade`-rijen), zijn ontploffing en de spelers die hij heeft verblind delen hem |
| `hitgroup` | tekst | waar de kogel raakte (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | verloren pantser; alleen `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | waar op het lichaam de kogel raakte, in het assenstelsel van het slachtoffer in meters (x vooruit, y omhoog vanaf de voeten, z rechts): de straal van het schot (`fire_bullets`, anders het oog en de kijkrichting van de aanvaller) getraceerd naar een lichaam dat stond zoals het slachtoffer stond en hurkte, op het deel dat `hitgroup` noemt; alleen `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | de richting van het schot in hetzelfde assenstelsel; `hitMiss` hoe ver (m) de straal het genoemde deel miste (0: er doorheen); `hitFrom` `bullet` of `aim` |
| `penetrated` | int16 | muren die de dodelijke kogel doorboorde; `kill` en `death` |
| `throughSmoke` | int8 | 0/1, gedood door rook heen; `kill` en `death` |
| `distance` | float32 | de afstand van de kill, zoals de game die telt (meters); `kill` en `death` |
| `assister` | tekst | wie assisteerde; `kill` en `death` |
| `flash`, `flashAlpha` | float32 | seconden flits die nog over zijn, en hoe wit; posities |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; posities |
| `zoom`, `duck`, `moveType` | | het zoomniveau van de kijker, hoe ver gehurkt (0-1), het bewegingstype van de game; posities |
| `spottedBy` | tekst | de Steam-ID's van de vijanden die deze speler zien, gescheiden door `\|`; posities |
| `inventory` | tekst | alles wat de speler draagt, gescheiden door `\|`; posities |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | het magazijn en de reserve van het wapen in de hand; schoten in de huidige salvo; posities |
| `punchPitch`, `punchYaw` | float32 | de aim punch van de terugslag, in graden; posities |
| `ping` | int16 | milliseconden; posities |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | de eigen scoreboardtellingen van de game voor de wedstrijd tot nu toe; posities |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | geld uitgegeven in deze ronde en in de wedstrijd; waarde van de uitrusting toen de ronde begon; posities |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, de staat van de speler op het tijdstip van de rij, gebeurtenissen inbegrepen: helm, defusekit, enig pantser, gekeken door kijker (vanaf het laatste positiemonster van de speler tot de rij), geflitst (binnen een `blind` die hem trof); elke rij die een speler noemt |
| `state_utility` | int16 | granaten bij zich op dat tijdstip (uit `inventory`); elke rij die een speler noemt |
| `state_weapon` | tekst | het wapen in de hand op dat tijdstip (bij een `death` dat van het slachtoffer zelf, waar `weapon` dat van de killer is); elke rij die een speler noemt |
| `earn_round_cs2` | int16 | wat de ronde uitbetaalde: bij `round_end` de winstbeloning of het verliesbonus (met de bonus van de plantende kant), bij `plant` en `defuse` de 300 van de speler |

## Gebeurtenissen {#events}

Welke speler een rij noemt, waar die staat, en welke kolommen die vullen. `match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won` en `buy` zijn op elke rij ingevuld; `inventory`, `money`, `equipment` en de `state_*`-kolommen op elke rij die een speler noemt (gebeurtenissen nemen die over van het laatste positiemonster van de speler).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Ook ingevuld |
|---|---|---|---|
| `position` | de speler | de speler (voeten) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (in de hand), `place`, en de volledige staat van de speler (de kolommen vanaf `flash`) - ook in freeze time |
| `kill` | de killer | waar de killer stond | `other` (slachtoffer), `weapon`, `headshot`, `opening`, `traded` (een trade-kill), `noscope`, `attackerBlind`, `place` |
| `death` | het slachtoffer | waar het slachtoffer viel | `other` (killer; leeg voor de wereld), `weapon`, `headshot`, `opening`, `traded` (gewroken), `noscope`, `attackerBlind`, `place` |
| `hurt` | het slachtoffer | waar het slachtoffer werd geraakt | `other` (aanvaller), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - ook de treffers van teamgenoten en van de wereld |
| `shot` | de schutter | waar het schot werd afgevuurd | `weapon`, `place`, `detail` (het verslag van de game over de kogels) |
| `slash` | de speler | waar met een mes werd gezwaaid | `weapon` = `Knife` |
| `grenade` | de gooier | de granaat in de lucht, op de bemonstering van de spelers en waar hij stopte | `weapon` (de granaat), `entity` |
| `throw` | de gooier | waar de granaat vandaan werd gegooid | `weapon` (de granaat), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | de gooier | waar hij afging | `weapon`, `throwerPlace` (de plek van de gooier op dat moment); `place` blijft leeg |
| `blind` | de geflitste speler | waar hij stond | `other` (flitser), `duration`, `weapon` = `Flashbang`, `entity`, `place` - ook geflitste teamgenoten |
| `plant` | de planter | waar hij plantte | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | de defuser | waar hij defuseerde | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | elke speler die de ronde speelde | waar de speler laatst stond | `won`, `earn_round_cs2` (wat de ronde hen uitbetaalde: de stijging van het geld van de kant tot de volgende freeze time waar de regels dat toelaten, anders de eigen regels), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | de planter (met zijn Steam-ID), kant `T`, het planterende team | de positie van de plant | `weapon` = `C4 Explosive`, `place` (die van de planter bij de plant: waar de bom lag); zijn tijd is wanneer de bom afging |
| `chat` | de afzender | waar hij was | `text` |
| elke andere spelgebeurtenis over een speler, onder de naam van de game: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | de speler | waar hij was (de gebeurtenis van een granaat: waar die was) | `weapon` (van een item), `entity`, `detail` (elk veld van de gebeurtenis) |

Wat erin zit en wat niet:

- **position**-rijen zijn levende spelers aan een kant, buiten freeze time en warmup, elke `--every` ticks (standaard acht per seconde).
- **kill**-rijen zijn alleen kills door een vijand - geen teamkill, suïcide of dood door de wereld. **death**-rijen zijn elke dood, die erbij inbegrepen.
- **explode**-rijen zijn elke geplante bom die afging, volgens de `bomb_exploded` van de demo: ook in de after-fase, wanneer de T's al door eliminatie hadden gewonnen. Een demo zonder die gebeurtenis krijgt er één voor elke ronde die door de bom is gewonnen, op het einde van de ronde.
- **hurt**- en **blind**-rijen zijn alleen tussen vijanden.
- **shot** laat messen en de C4 weg; granaten zijn **throw**-rijen.
- **molotov** dekt molotovs en incendiaries (het begin van het vuur).
- Schade van teamgenoten, flitsen van teamgenoten en toeschouwers, gebeurtenissen in freeze time en alles tussen rondes staan niet in de tabel.

Een uitgewerkt voorbeeld, uit de synthetische demo van de tests (een rookgranaat gegooid, een openingskill met headshot, trades):

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

Ben doodt ace 1,9 s nadat ace bob doodde; zo wordt bobs dood gewroken (de `death`-rij van bob: traded 1; de `kill`-rij van ben: een trade-kill, traded 1); de tweede treffer op bob was 137 schade op 40 gezondheid, dus telt hij als 40.

## De `heat3d`-voetnoothints {#the-heat3d-footer-hints}

Het Parquet-voetstuk van het bestand (de sleutel/waarde-metadata van het schema) draagt leesinstructies onder de sleutel **`heat3d`**, een JSON-object:

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
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Onderdeel | Zegt |
|---|---|
| `version`, `kind` | de versie van de hints (1) en wat ze schreef (`cs2-demo`) |
| `axes.up` | het Z van het bestand is omhoog |
| `axes.flipY` | keer de Y van het bestand om (zie hieronder) |
| `axes.scale` | 1: posities worden gebruikt zoals ze zijn, in game-eenheden |
| `entity.size` | een speler is **32 eenheden** breed - de breedte van een CS2-speler - de maat waarmee een boxreplay er een tekent |
| `columns.x` / `y` / `z` | de positiekolommen |
| `columns.time`, `timeUnit` | `time`, in seconden |
| `columns.personId` | de speler is de persoon |
| `columns.teamId` | de kant is de groep (dus T en CT, niet de teamnamen, kleuren de groepen) |
| `columns.sessionId` | elke ronde (`roundId`) is een sessie |
| `columns.lookMode` en `dirX`-`dirZ` | de kijkrichting is een vector in die kolommen |
| `columns.extra` | de kolommen om als filter te bewaren, in volgorde van nut |

Een viewer die de sleutel kent, opent het bestand zonder iets in te stellen. Al het andere negeert hem. Om hem zelf te lezen:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Assen en eenheden {#axes-and-units}

De coördinaten zijn die van de game zelf: **inches** (één game-eenheid; een speler is 72 eenheden hoog staand en 32 breed), **Z omhoog**, en rechtshandig.

Een viewer waarvan de wereld Y-omhoog is, moet de (x, y, z) van de game tekenen als **(x, z, -y)** - Z wordt de hoogte en Y wordt omgekeerd. Dat is een rotatie, geen spiegeling. Getekend zoals een linkshandige Z-omhoog-wereld dat doet, als (x, z, y), komt elke map gespiegeld uit, de A-site aan de verkeerde kant; `flipY: true` is wat de hints zeggen om dat te voorkomen. De [kaartexport](map-export.md) schrijft zijn geometrie al in het assenstelsel (x, z, -y), in dezelfde eenheden, dus die ligt zonder aanpassing onder de tabel.

Afstanden in de viewer worden in meters aangegeven; met een schaal van 1 zijn het game-eenheden. Vermenigvuldig met 0,0254 voor meters.

## Grootte {#size}

Posities domineren: ongeveer tien spelers x 8 monsters per seconde van levend spel bij de standaard `--every 8`, minder voor dode spelers en in freeze time. Een halvering van `--every` verdubbelt ze; gebeurtenissen worden er niet door beïnvloed.
