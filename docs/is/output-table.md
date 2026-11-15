---
title: "Hitakortstaflan"
nav_order: 8
lang: "is"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Hitakortstaflan (`<match>.parquet`) {#the-heatmap-table-matchparquet}

Ein Parquet-skrá fyrir hvern leik: staða hvers lifandi leikmanns, sýnatekin, og hver
atburður þar sem hann gerðist, ein röð hver - löng tafla sem 3DHeat-skoðarinn les
sem hitakort, og allt annað sem venjulega töflu. Kóði:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(skráin), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(raðirnar; sjá [Að smíða leik](building-matches.md)).

Skráin er skrifuð með Snappy-þjöppun í raðahópum með 256.000 röðum.
Raðirnar eru raðaðar eftir `time`, síðan eftir `event`. Aðeins raðir innan lotu (frá
lokum frystitíma hennar til upphafs næstu lotu) eru í henni.

Á gervi-demo-skrá prófananna, atburðaraðir fyrstu lotu:

![event rows of the table](../assets/img/table-rows.svg)

Í `.3dheat`-gámi er taflan hlutinn með hlutverkið `table`
([Ein skrá fyrir hvern leik](output-container.md)).

## Dálkar {#columns}

Dálkarnir, alltaf í þessari röð. Textadálkar eru orðabókarkóðaðir strengir
(`dictionary<int32, string>`) og eru aldrei null: „ekkert gildi“ er tómur
strengur. Töludálkar eru null þar sem röð hefur ekkert gildi.

| Dálkur | Tegund | Hvað |
|---|---|---|
| `match` | string | leikjanafnið (`alpha-vs-bravo-m1`, eða `...-b` fyrir aðra keðju) |
| `map` | string | kortið, úr haus demo-skrárinnar (`de_x`) |
| `round` | int16 | lotunúmerið, frá 1 |
| `roundId` | string | `<match> #NN`, lotunúmerið með tveimur tölustöfum (`alpha-vs-bravo-m1 #07`): einstakt yfir leiki, lota (session) skoðarans |
| `phase` | string | `freeze` á frystitíma lotunnar (frá lokum fyrri lotu), `live` þar til lotan er ákvörðuð, `after` á meðan sigurvegararnir veiða og taparar bjarga sér |
| `time` | float64 | sekúndur frá því leikurinn byrjaði (lifandi byrjun fyrstu skrárinnar), á einni klukku yfir skrárnar |
| `roundTime` | float32 | sekúndur frá því frystitími þessarar lotu endaði; neikvætt á frystitíma |
| `event` | string | hvað röðin er - sjá [Atburðir](#events) |
| `player` | string | nafn leikmannsins (fyrir hvern atburð er sagt hér að neðan hvaða leikmaður) |
| `steamid` | string | Steam ID leikmannsins (64 bita, sem texti) |
| `side` | string | `T` eða `CT` í þessari lotu; tómt þegar leikmaðurinn var á engri hlið |
| `team` | string | liðsheiti leikmannsins (eða `Started T` / `Started CT`); fyrir `explode`, liðið sem setti sprengjuna |
| `x`, `y`, `z` | float32 | staða í eigin hnitum leiksins: tommur (leikeiningar), **Z upp**, rétthent |
| `dirX`, `dirY`, `dirZ` | float32 | hvert leikmaðurinn horfir, einingarvigur í sama hnitakerfi; aðeins staðsetningar |
| `health` | int16 | 0-100; staðsetningar, og á `hurt` það sem var eftir eftir höggið |
| `armor` | int16 | 0-100; staðsetningar, og á `hurt` það sem var eftir eftir höggið |
| `money` | int32 | peningar leikmannsins; aðeins staðsetningar |
| `equipment` | int32 | verðmæti þess sem leikmaðurinn ber; aðeins staðsetningar |
| `weapon` | string | vopnið eins og leikurinn nefnir það (`AK-47`, `M4A1-S`, `Knife` fyrir öll hnífaskinn) |
| `place` | string | eigið staðarheiti kortsins á stöðu raðarinnar (`BombsiteA`, `CTSpawn`); tómt á sprengingum handsprengna: demo-skráin nefnir engan stað fyrir hvar handsprengja sprakk |
| `throwerPlace` | string | staðarheiti kastarans þegar handsprengjan sprakk; aðeins sprengingar handsprengna |
| `other` | string | hinn leikmaðurinn í fellingu, dauða, höggi eða blindu |
| `damage` | float32 | tapað líf; aðeins `hurt` |
| `duration` | float32 | sekúndur blindaður; aðeins `blind` |
| `headshot` | int8 | 0/1; aðeins `kill` og `death` |
| `opening` | int8 | 0/1, fyrsta felling lotunnar á andstæðingi; aðeins `kill` og `death` |
| `traded` | int8 | 0/1. Fyrir `kill`: þetta var trade-felling. Fyrir `death`: því var hefnt innan 5 s. Aðeins `kill` og `death`. |
| `noscope` | int8 | 0/1, fellingin var með sjónaukavopni skotnu án sjónauka (`noscope` atburðarins); aðeins `kill` og `death` |
| `attackerBlind` | int8 | 0/1, banamaðurinn var blindaður þegar hann felldi (`attackerblind` atburðarins); aðeins `kill` og `death` |
| `won` | int8 | 0/1, hvort hlið þessarar raðar vann lotuna; null þegar `side` er tómt |
| `matchWon` | int8 | 0/1, hvort lið þessarar raðar vann leikinn; null þegar `team` er tómt eða upptakan sýnir ekki endann (sjá `winner` í leikjaskjalinu) |
| `roundEndReason` | string | hvernig lota raðarinnar endaði: `elimination`, `bomb` (sprengjan sprakk), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | string | kaup hliðar þessarar raðar í þessari lotu: `pistol`, `eco`, `force`, `full` |
| `detail` | string | hver reitur atburðarins sem hinir dálkarnir bera ekki, sem JSON-hlutur (eigin heiti leiksins): kúlur skots (`fire_bullets`: uppruni, hornin, ónákvæmni, dreifing, rekoil-vísitala, fræ...), `dominated`, `revenge`, `attackerinair`, `wipe` dauða..., `defindex` hlutar, ekkert hjá fótataki |
| `text` | string | spjalllína; aðeins `chat` |
| `entity` | int32 | eining handsprengjunnar: flug `throw` (`grenade`-raðir), sprenging hennar og leikmennirnir sem hún blindaði deila henni |
| `hitgroup` | string | hvar kúlan hitti (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | tapuð brynja; aðeins `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | hvar á líkamanum kúlan hitti, í hnitakerfi fórnarlambsins í metrum (x fram, y upp frá fótum, z hægri): geisli skotsins (`fire_bullets`, annars auga og stefna árásarmannsins) rakinn í líkama stilltan eins og fórnarlambið stóð og beygði sig, á hlutann sem `hitgroup` nefnir; aðeins `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | stefna skotsins í sama hnitakerfi; `hitMiss` hve langt (m) geislinn fór fram hjá nefnda hlutanum (0: í gegnum hann); `hitFrom` `bullet` eða `aim` |
| `penetrated` | int16 | veggir sem banakúlan fór í gegnum; `kill` og `death` |
| `throughSmoke` | int8 | 0/1, felldur gegnum reyk; `kill` og `death` |
| `distance` | float32 | fjarlægð fellingarinnar eins og leikurinn telur hana (metrar); `kill` og `death` |
| `assister` | string | hver aðstoðaði; `kill` og `death` |
| `flash`, `flashAlpha` | float32 | sekúndur af blindu eftir, og hve hvít; staðsetningar |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; staðsetningar |
| `zoom`, `duck`, `moveType` | | aðdráttarstig sjónaukans, hve langt beygður (0-1), hreyfitegund leiksins; staðsetningar |
| `spottedBy` | string | Steam ID andstæðinganna sem sjá þennan leikmann, aðskilin með `\|`; staðsetningar |
| `inventory` | string | allt sem leikmaðurinn ber, aðskilið með `\|`; staðsetningar |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | magasín og varabirgðir vopnsins í hendi; skot í núverandi lotu; staðsetningar |
| `punchPitch`, `punchYaw` | float32 | miðunarhögg rekoils, gráður; staðsetningar |
| `ping` | int16 | millisekúndur; staðsetningar |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | eigin stigatöflutölur leiksins fyrir leikinn hingað til; staðsetningar |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | peningar eyddir í þessari lotu og í leiknum; búnaðarverðmæti þegar lotan byrjaði; staðsetningar |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, staða leikmannsins á tíma raðarinnar, atburðir meðtaldir: hjálmur, aftengingarsett, einhver brynja, með sjónauka (frá síðasta staðarsýni leikmannsins fram að röðinni), blindaður (inni í `blind` sem hitti hann); hver röð sem nefnir leikmann |
| `state_utility` | int16 | handsprengjur bornar á tímanum (úr `inventory`); hver röð sem nefnir leikmann |
| `state_weapon` | string | vopnið í hendi á tímanum (á `death` vopn fórnarlambsins sjálfs, þar sem `weapon` er vopn banamannsins); hver röð sem nefnir leikmann |
| `earn_round_cs2` | int16 | það sem lotan gaf: á `round_end` sigurlaunin eða tapbónusinn (með bónus hliðarinnar sem setti sprengjuna), á `plant` og `defuse` 300 leikmannsins |

## Atburðir {#events}

Hvaða leikmann röð nefnir, hvar hann stendur, og hvaða dálka hún fyllir.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won`, `roundEndReason` og `buy` eru fyllt á hverri röð (`matchWon` þar sem sigurvegari leiksins er þekktur); `inventory`, `money`, `equipment` og
`state_*` dálkarnir á hverri röð sem nefnir leikmann (atburðir taka þá úr
síðasta staðarsýni leikmannsins).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Einnig fyllt |
|---|---|---|---|
| `position` | leikmaðurinn | leikmaðurinn (fætur) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (í hendi), `place`, og allt ástand leikmannsins (dálkarnir frá `flash` og áfram) - líka á frystitíma |
| `kill` | banamaðurinn | þar sem banamaðurinn stóð | `other` (fórnarlambið), `weapon`, `headshot`, `opening`, `traded` (trade-felling), `noscope`, `attackerBlind`, `place` |
| `death` | fórnarlambið | þar sem fórnarlambið féll | `other` (banamaðurinn; tómt fyrir heiminn), `weapon`, `headshot`, `opening`, `traded` (hefnt), `noscope`, `attackerBlind`, `place` |
| `hurt` | fórnarlambið | þar sem fórnarlambið var hitt | `other` (árásarmaðurinn), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - högg liðsfélaga og heimsins líka |
| `shot` | skotmaðurinn | þaðan sem skotið var af | `weapon`, `place`, `detail` (frásögn leiksins af kúlunum) |
| `slash` | leikmaðurinn | þar sem hníf var sveiflað | `weapon` = `Knife` |
| `grenade` | kastarinn | handsprengjan á flugi, á sýnatöku leikmannanna og þar sem hún stöðvaðist | `weapon` (handsprengjan), `entity` |
| `throw` | kastarinn | þaðan sem handsprengjunni var kastað | `weapon` (handsprengjan), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | kastarinn | þar sem hún sprakk | `weapon`, `throwerPlace` (staður kastarans á því augnabliki); `place` helst tómt |
| `blind` | leikmaðurinn sem var blindaður | þar sem hann stóð | `other` (blindarinn), `duration`, `weapon` = `Flashbang`, `entity`, `place` - liðsfélagar blindaðir líka |
| `plant` | setjandinn | þar sem hann setti sprengjuna | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | aftengjandinn | þar sem hann aftengdi | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | hver leikmaður sem spilaði lotuna | þar sem leikmaðurinn stóð síðast | `won`, `earn_round_cs2` (það sem lotan gaf honum: hækkun peninga hliðarinnar fram að næsta frystitíma þar sem reglurnar leyfa það, annars eigin gildi reglnanna), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | setjandinn (með Steam ID sitt), hlið `T`, liðið sem setti sprengjuna | staða sprengjusetningarinnar | `weapon` = `C4 Explosive`, `place` (staður setjandans við sprengjusetninguna: þar sem sprengjan lá); tími hennar er þegar sprengjan sprakk |
| `chat` | sendandinn | þar sem hann var | `text` |
| sérhver annar leikatburður um leikmann, undir heiti leiksins: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | leikmaðurinn | þar sem hann var (atburðir handsprengju: þar sem hún var) | `weapon` (hlutar), `entity`, `detail` (hver reitur atburðarins) |

Hvað er með og hvað ekki:

- **position**-raðir eru lifandi leikmenn á hlið, utan frystitíma og
  upphitunar, á hverju `--every`-tikki (átta á sekúndu sjálfgefið).
- **kill**-raðir eru aðeins fellingar af hendi andstæðings - enginn teamkill, sjálfsvíg eða dauði af hendi
  heimsins. **death**-raðir eru öll dauðsföll, þau meðtalin.
- **explode**-raðir eru hver sprengja sem var sett og sprakk, samkvæmt `bomb_exploded`
  demo-skrárinnar: líka í after-fasa, þegar T höfðu þegar unnið með
  útrýmingu. Demo-skrá án þess atburðar fær einn fyrir hverja lotu unna með
  sprengjunni, við lok lotunnar.
- **hurt**- og **blind**-raðir eru aðeins milli andstæðinga.
- **shot** sleppir hnífum og C4; handsprengjur eru **throw**-raðir.
- **molotov** nær yfir molotov og incendiary (eldurinn byrjar).
- Skaði liðsfélaga, blindur liðsfélaga og áhorfenda, atburðir á frystitíma
  og allt milli lota er ekki í töflunni.

Útfært dæmi, úr gervi-demo-skrá prófananna (reykur kastaður,
opnunarfelling með hausskoti, trades):

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

Dauða bobs er hefnt með fellingu bens á ace 1,9 s síðar (`death`-röð bobs:
traded 1; `kill`-röð bens: trade-felling, traded 1); seinna höggið á bob var
137 skaði á 40 lífi, svo það telur 40.

## `heat3d`-ábendingarnar í endanum {#the-heat3d-footer-hints}

Parquet-endir skrárinnar (lýsigögn skema, lykill/gildi) ber lestrarleiðbeiningar
undir lyklinum **`heat3d`**, JSON-hlut:

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

| Færsla | Segir |
|---|---|
| `version`, `kind` | útgáfu ábendinganna (1) og hvað skrifaði þær (`cs2-demo`) |
| `axes.up` | Z skrárinnar er upp |
| `axes.flipY` | neikvæða Y skrárinnar (sjá hér að neðan) |
| `axes.scale` | 1: staðsetningar eru notaðar eins og þær eru, í leikeiningum |
| `entity.size` | leikmaður er **32 einingar** á breidd - breidd CS2-leikmanns - stærðin sem kassaendurspilun teiknar hann í |
| `columns.x` / `y` / `z` | staðsetningardálkarnir |
| `columns.time`, `timeUnit` | `time`, í sekúndum |
| `columns.personId` | leikmaðurinn er persónan |
| `columns.teamId` | hliðin er hópurinn (svo T og CT, ekki liðsheitin, lita hópana) |
| `columns.sessionId` | hver lota (`roundId`) er lota (session) |
| `columns.lookMode` og `dirX`-`dirZ` | sjónstefnan er vigur í þessum dálkum |
| `columns.extra` | dálkarnir til að halda sem síur, í röð notagildis |

Skoðari sem þekkir lykilinn opnar skrána án þess að nokkuð þurfi að stilla. Allt annað
hunsar hann. Til að lesa hann sjálf(ur):

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Ásar og einingar {#axes-and-units}

Hnitin eru eigin hnit leiksins: **tommur** (ein leikeining; leikmaður er 72
einingar á hæð standandi og 32 á breidd), **Z upp**, og rétthent.

Skoðari þar sem heimurinn er Y-upp verður að teikna (x, y, z) leiksins sem
**(x, z, -y)** - Z verður hæðin og Y er neikvætt. Það er snúningur,
ekki speglun. Teiknað eins og vinstrihentur Z-upp heimur er, sem (x, z, y), kemur
hvert kort speglað út, A site á röngum stað; `flipY: true` er það sem
ábendingarnar segja til að koma í veg fyrir það. [Kortaútflutningurinn](map-export.md) skrifar geometríu sína
þegar í (x, z, -y) hnitakerfinu, í sömu einingum, svo hún liggur undir
töflunni án nokkurrar aðlögunar.

Fjarlægðir í skoðaranum eru merktar í metrum; með kvarða 1 eru þær
leikeiningar. Margfaldaðu með 0,0254 fyrir metra.

## Stærð {#size}

Staðsetningar eru mestar: um tíu leikmenn x 8 sýni á sekúndu af lifandi leik á
sjálfgefnu `--every 8`, minna fyrir dauða leikmenn og frystitíma. Að helminga
`--every` tvöfaldar þær; atburðir verða fyrir engum áhrifum.
