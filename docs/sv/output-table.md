---
title: "Värmekartetabellen"
nav_order: 8
lang: "sv"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Värmekartetabellen (`<match>.parquet`) {#the-heatmap-table-parquet}

En Parquet-fil per match: varje levande spelares position, samplad, och varje händelse där den
inträffade, en rad vardera - en lång tabell som 3DHeat-visaren läser som en värmekarta, och allt annat
som en vanlig tabell. Kod:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(filen), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(raderna; se [Bygga en match](building-matches.md)).

Filen skrivs med Snappy-komprimering i radgrupper om 256 000 rader. Raderna sorteras efter `time`, och
sedan efter `event`. Bara rader inom en runda (från slutet av dess freeze time till nästa rundas start)
finns med.

På den syntetiska demon i testerna, händelseraderna för första rundan:

![händelseraderna i tabellen](../assets/img/table-rows.svg)

I en `.3dheat`-behållare är tabellen medlemmen med rollen `table`
([En fil per match](output-container.md)).

## Kolumner {#columns}

Kolumnerna, alltid i denna ordning. Textkolumner är ordbokskodade strängar
(`dictionary<int32, string>`) och är aldrig null: "inget värde" är en tom sträng. Numeriska kolumner är
null där en rad saknar värde.

| Kolumn | Typ | Vad |
|---|---|---|
| `match` | sträng | matchnamnet (`alpha-vs-bravo-m1`, eller `...-b` för en andra kedja) |
| `map` | sträng | kartan, från demohuvudet (`de_x`) |
| `round` | int16 | rundnumret, 1-baserat |
| `roundId` | sträng | `<match> #NN`, rundnumret med två siffror (`alpha-vs-bravo-m1 #07`): unikt över matcher, visarens session |
| `phase` | sträng | `freeze` i rundans freeze time (från föregående rundas slut), `live` tills rundan avgörs, `after` medan vinnarna jagar och förlorarna sparar |
| `time` | float64 | sekunder sedan matchen startade (den första filens levande start), på en gemensam klocka över dess filer |
| `roundTime` | float32 | sekunder sedan denna rundas freeze time tog slut; negativt i freeze time |
| `event` | sträng | vad raden är - se [Händelser](#events) |
| `player` | sträng | spelarens namn (för varje händelse, vilken spelare som avses anges nedan) |
| `steamid` | sträng | spelarens Steam-ID (64-bitars, som text) |
| `side` | sträng | `T` eller `CT` i denna runda; tomt när spelaren var på ingen sida |
| `team` | sträng | spelarens lagnamn (eller `Started T` / `Started CT`); för `explode`, det planterande laget |
| `x`, `y`, `z` | float32 | position i spelets egna koordinater: tum (spelenheter), **Z uppåt**, högerhänt |
| `dirX`, `dirY`, `dirZ` | float32 | vart spelaren tittar, en enhetsvektor i samma koordinatsystem; bara positioner |
| `health` | int16 | 0-100; positioner, och på `hurt` vad som var kvar efter träffen |
| `armor` | int16 | 0-100; positioner, och på `hurt` vad som var kvar efter träffen |
| `money` | int32 | spelarens pengar; bara positioner |
| `equipment` | int32 | värdet av det spelaren bär; bara positioner |
| `weapon` | sträng | vapnet så som spelet namnger det (`AK-47`, `M4A1-S`, `Knife` för alla kniv-skins) |
| `place` | sträng | kartans egna platsnamn vid radens position (`BombsiteA`, `CTSpawn`); tomt vid granatdetonationer: demon anger ingen plats för var en granat gick av |
| `throwerPlace` | sträng | kastarens platsnamn när granaten gick av; bara granatdetonationer |
| `other` | sträng | den andra spelaren i en kill, död, träff eller blindning |
| `damage` | float32 | förlorad hälsa; bara `hurt` |
| `duration` | float32 | sekunder blindad; bara `blind` |
| `headshot` | int8 | 0/1; bara `kill` och `death` |
| `opening` | int8 | 0/1, rundans första kill av en fiende; bara `kill` och `death` |
| `traded` | int8 | 0/1. För en `kill`: det var en trade-kill. För en `death`: det hämnades inom 5 s. Bara `kill` och `death`. |
| `noscope` | int8 | 0/1, killen gjordes med ett vapen med kikare avfyrat utan kikare (händelsens `noscope`); bara `kill` och `death` |
| `attackerBlind` | int8 | 0/1, mördaren var bländad när den dödade (händelsens `attackerblind`); bara `kill` och `death` |
| `won` | int8 | 0/1, om denna rads sida vann rundan; null när `side` är tomt |
| `matchWon` | int8 | 0/1, om denna rads lag vann matchen; null när `team` är tomt eller inspelningen inte visar slutet (se matchdokumentets `winner`) |
| `roundEndReason` | sträng | hur radens runda slutade: `elimination`, `bomb` (bomben gick av), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | sträng | radens sidas köp den rundan: `pistol`, `eco`, `force`, `full` |
| `detail` | sträng | varje fält i händelsen som de andra kolumnerna inte bär, som ett JSON-objekt (spelets egna namn): ett skotts kulor (`fire_bullets`: ursprung, vinklar, osäkerhet, spridning, rekylindex, seed ...), ett dödsfalls `dominated`, `revenge`, `attackerinair`, `wipe` ..., ett föremåls `defindex`, ett steg har inget |
| `text` | sträng | en chattrad; bara `chat` |
| `entity` | int32 | granatens entitet: en `throw`s flygning (`grenade`-rader), dess detonation och spelarna den bländade delar den |
| `hitgroup` | sträng | var kulan träffade (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | förlorat pansar; bara `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | var på kroppen kulan träffade, i offrets koordinatsystem i meter (x framåt, y upp från fötterna, z till höger): skottets stråle (`fire_bullets`, annars angriparens öga och vy) spårad till en kropp posad som offret stod och satt, till den del `hitgroup` anger; bara `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | skottets riktning i samma koordinatsystem; `hitMiss` hur långt (m) strålen passerade den namngivna delen (0: genom den); `hitFrom` `bullet` eller `aim` |
| `penetrated` | int16 | väggar dödskulan gick igenom; `kill` och `death` |
| `throughSmoke` | int8 | 0/1, dödad genom rök; `kill` och `death` |
| `distance` | float32 | killens avstånd så som spelet räknar det (meter); `kill` och `death` |
| `assister` | sträng | vem som assisterade; `kill` och `death` |
| `flash`, `flashAlpha` | float32 | sekunder kvar av flashen, och hur vit den är; positioner |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; positioner |
| `zoom`, `duck`, `moveType` | | kikarens zoomnivå, hur långt ihopkrupen (0-1), spelets rörelsetyp; positioner |
| `spottedBy` | sträng | Steam-ID:na på de fiender som ser denna spelare, separerade med `\|`; positioner |
| `inventory` | sträng | allt spelaren bär, separerat med `\|`; positioner |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | det hållna vapnets magasin och reserv; skott i den pågående salvan; positioner |
| `punchPitch`, `punchYaw` | float32 | rekylens sikte-slag, grader; positioner |
| `ping` | int16 | millisekunder; positioner |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | spelets egna resultattavleräkningar för matchen hittills; positioner |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | pengar använda denna runda och i matchen; utrustningsvärde när rundan började; positioner |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, spelarens tillstånd vid radens tid, händelser inräknade: hjälm, desarmeringsverktyg, något pansar, kikare (från spelarens senaste positionssampel fram till raden), flashad (inom en `blind` som träffade dem); varje rad som namnger en spelare |
| `state_utility` | int16 | antal granater som bärs vid tiden (från `inventory`); varje rad som namnger en spelare |
| `state_weapon` | sträng | vapnet i handen vid tiden (vid en `death`, offrets eget, där `weapon` är mördarens); varje rad som namnger en spelare |
| `earn_round_cs2` | int16 | vad rundan gav: på `round_end` vinstbeloningen eller förlustbonusen (med den planterande sidans bonus), på `plant` och `defuse` spelarens 300 |

## Händelser {#events}

Vilken spelare en rad anger, var den står, och vilka kolumner den fyller.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won`, `roundEndReason` och
`buy` fylls på varje rad (`matchWon` där matchens vinnare är känd); `inventory`, `money`, `equipment` och
kolumnerna `state_*` på varje rad som namnger en spelare (händelser tar dem från spelarens senaste
positionssampel).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Fylls också |
|---|---|---|---|
| `position` | spelaren | spelaren (fötterna) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (hållet), `place` och spelarens hela tillstånd (kolumnerna från `flash` och framåt) - även i freeze time |
| `kill` | mördaren | där mördaren stod | `other` (offret), `weapon`, `headshot`, `opening`, `traded` (en trade-kill), `noscope`, `attackerBlind`, `place` |
| `death` | offret | där offret föll | `other` (mördaren; tomt för världen), `weapon`, `headshot`, `opening`, `traded` (hämnad), `noscope`, `attackerBlind`, `place` |
| `hurt` | offret | där offret träffades | `other` (angriparen), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - lagkamraters och världens träffar också |
| `shot` | skytten | där skottet avlossades | `weapon`, `place`, `detail` (spelets redogörelse för kulorna) |
| `slash` | spelaren | där en kniv svingades | `weapon` = `Knife` |
| `grenade` | kastaren | granaten i flykt, vid spelarnas sampling och där den stannade | `weapon` (granaten), `entity` |
| `throw` | kastaren | där granaten kastades från | `weapon` (granaten), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | kastaren | där den gick av | `weapon`, `throwerPlace` (kastarens plats i det ögonblicket); `place` förblir tomt |
| `blind` | spelaren som flashades | där de stod | `other` (den som flashade), `duration`, `weapon` = `Flashbang`, `entity`, `place` - lagkamrater som flashades också |
| `plant` | planteraren | där de planterade | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | desarmeraren | där de desarmerade | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | varje spelare som deltog i rundan | där spelaren senast stod | `won`, `earn_round_cs2` (vad rundan gav dem: höjningen av sidans pengar till nästa freeze time där reglerna tillåter det, annars reglernas egen), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | planteraren (med sitt Steam-ID), sidan `T`, det planterande laget | planteringens position | `weapon` = `C4 Explosive`, `place` (planterarens vid planteringen: där bomben låg); dess tid är när bomben gick av |
| `chat` | avsändaren | där de var | `text` |
| varje annan spelhändelse om en spelare, under spelets namn: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | spelaren | där de var (en granats händelser: där den var) | `weapon` (ett föremåls), `entity`, `detail` (varje fält i händelsen) |

Vad som finns med och inte:

- **position**-rader är levande spelare på en sida, utanför freeze time och uppvärmning, var `--every`:e
  tick (åtta per sekund som standard).
- **kill**-rader är kills av en fiende enbart - ingen teamkill, inget suicide och inget dödsfall för
  världen. **death**-rader är varje dödsfall, de där inräknade.
- **explode**-rader är varje planterad bomb som gick av, enligt demons `bomb_exploded`: även i
  efterfasen, när Ts redan vunnit genom eliminering. En demo utan den händelsen får en för varje runda
  som vunnits av bomben, vid rundans slut.
- **hurt**- och **blind**-rader är endast mellan fiender.
- **shot** utelämnar knivar och C4; granater är **throw**-rader.
- **molotov** omfattar molotovs och incendiaries (elden som startar).
- Lagkamraters skada, lagkamraters flashar och åskådares, händelser under freeze time och allt mellan
  rundor finns inte i tabellen.

Ett arbetat exempel, från den syntetiska demon i testerna (en rök kastad, ett huvudskott som öppnar, trades):

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

bobs död hämnas av bens kill på ace 1,9 s senare (bobs `death`-rad: traded 1; bens `kill`-rad: en
trade-kill, traded 1); den andra träffen på bob var 137 skada på 40 hälsa, så den räknas som 40.

## `heat3d`-tipsen i sidfoten {#the-heat3d-footer-hints}

Filens Parquet-sidfot (metadata för schema och nyckel/värde) bär läsinstruktioner under nyckeln **`heat3d`**,
ett JSON-objekt:

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

| Post | Säger |
|---|---|
| `version`, `kind` | tipsens version (1) och vad som skrev dem (`cs2-demo`) |
| `axes.up` | filens Z är uppåt |
| `axes.flipY` | negera filens Y (se nedan) |
| `axes.scale` | 1: positionerna används som de är, i spelenheter |
| `entity.size` | en spelare är **32 enheter** bred - CS2-spelarens bredd - den storlek en lådrepresentation ritar en |
| `columns.x` / `y` / `z` | positionskolumnerna |
| `columns.time`, `timeUnit` | `time`, i sekunder |
| `columns.personId` | spelaren är personen |
| `columns.teamId` | sidan är gruppen (så det är T och CT, inte lagnamnen, som färgar grupperna) |
| `columns.sessionId` | varje runda (`roundId`) är en session |
| `columns.lookMode` och `dirX`-`dirZ` | blickriktningen är en vektor i de kolumnerna |
| `columns.extra` | kolumnerna att behålla som filter, i nyttoordning |

En visare som känner till nyckeln öppnar filen utan att något behöver ställas in. Andra ignorerar den.
För att läsa den själv:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Axlar och enheter {#axes-and-units}

Koordinaterna är spelets egna: **tum** (en spelenhet; en spelare är 72 enheter lång när hon står och 32
bred), **Z uppåt**, och högerhänt.

En visare vars värld har Y uppåt måste rita spelets (x, y, z) som **(x, z, -y)** - Z blir höjden och Y
negeras. Det är en rotation, inte en spegling. Ritas det som en vänsterhänt Z-uppåt-värld, som (x, z, y),
blir varje karta spegelvänd, A-platsen på fel sida; `flipY: true` är vad tipsen säger för att förhindra
det. [Kartexporten](map-export.md) skriver sin geometri redan i koordinatsystemet (x, z, -y), i samma
enheter, så den ligger under tabellen utan någon justering.

Avstånd i visaren märks i meter; med skala 1 är de spelenheter. Multiplicera med 0,0254 för meter.

## Storlek {#size}

Positionerna dominerar: ungefär tio spelare gånger 8 sampel per sekund av levande spel vid standardvärdet
`--every 8`, mindre för döda spelare och i freeze time. Halvering av `--every` fördubblar dem; händelser
påverkas inte.
