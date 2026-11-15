---
title: "Heatmap-tabellen"
nav_order: 8
lang: "da"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Heatmap-tabellen (`<match>.parquet`) {#the-heatmap-table-parquet}

Én Parquet-fil pr. kamp: hver levende spillers position, samplet, og hver hændelse der, hvor den skete, én række hver - en lang tabel, som 3DHeat-visningen læser som et heatmap, og alt andet som en almindelig tabel. Kode:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(filen), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(rækkerne; se [Sådan bygges en kamp](building-matches.md)).

Filen bliver skrevet med Snappy-komprimering i rækkegrupper på 256.000 rækker.
Rækkerne er sorteret efter `time`, og derefter efter `event`. Kun rækker inden for en runde (fra enden af dens freeze-tid til næste rundes start) er med.

På testenes syntetiske demo, hændelsesrækkerne i den første runde:

![hændelsesrækker i tabellen](../assets/img/table-rows.svg)

I en `.3dheat`-container er tabellen medlemmet med rollen `table`
([En fil pr. kamp](output-container.md)).

## Kolonner {#columns}

Kolonnerne, altid i denne rækkefølge. Tekstkolonner er ordbogskodede strenge (`dictionary<int32, string>`) og er aldrig tomme (null): "ingen værdi" er en tom streng. Numeriske kolonner er null, hvor en række ingen værdi har.

| Kolonne | Type | Hvad |
|---|---|---|
| `match` | streng | kampnavnet (`alpha-vs-bravo-m1`, eller `...-b` for en anden kæde) |
| `map` | streng | kortet, fra demo-headeren (`de_x`) |
| `round` | int16 | rundenummeret, 1-baseret |
| `roundId` | streng | `<match> #NN`, rundenummeret med to cifre (`alpha-vs-bravo-m1 #07`): unik på tværs af kampe, visningens session |
| `phase` | streng | `freeze` i rundens freeze-tid (fra den forrige rundes slutning), `live` indtil runden er afgjort, `after` mens vinderne jager og taberne sparer |
| `time` | float64 | sekunder siden kampen startede (live-starten af dens første fil), på ét ur på tværs af dens filer |
| `roundTime` | float32 | sekunder siden denne rundes freeze-tid sluttede; negativ i freeze-tid |
| `event` | streng | hvad rækken er - se [Hændelser](#events) |
| `player` | streng | spillerens navn (for hver hændelse, hvilken spiller der står nedenfor) |
| `steamid` | streng | spillerens Steam-ID (64-bit, som tekst) |
| `side` | streng | `T` eller `CT` i denne runde; tom, når spilleren var på ingen side |
| `team` | streng | spillerens holdnavn (eller `Started T` / `Started CT`); for `explode`, det plantende hold |
| `x`, `y`, `z` | float32 | position i spillets egne koordinater: tommer (spilenheder), **Z opad**, højrehåndet |
| `dirX`, `dirY`, `dirZ` | float32 | hvor spilleren kigger, en enhedsvektor i samme koordinatsystem; kun positioner |
| `health` | int16 | 0-100; positioner, og på `hurt` hvad der var tilbage efter hittet |
| `armor` | int16 | 0-100; positioner, og på `hurt` hvad der var tilbage efter hittet |
| `money` | int32 | spillerens penge; kun positioner |
| `equipment` | int32 | værdien af det, spilleren bærer; kun positioner |
| `weapon` | streng | våbnet, som spillet navngiver det (`AK-47`, `M4A1-S`, `Knife` for enhver knivskin) |
| `place` | streng | kortets eget stednavn ved rækkens position (`BombsiteA`, `CTSpawn`); tom ved granatdetonationer: demoen navngiver ikke et sted for, hvor en granat gik af |
| `throwerPlace` | streng | kasterens stednavn, da granaten gik af; kun granatdetonationer |
| `other` | streng | den anden spiller i en kill, et dødsfald, et hit eller en blænding |
| `damage` | float32 | mistede liv; kun `hurt` |
| `duration` | float32 | sekunder blændet; kun `blind` |
| `headshot` | int8 | 0/1; kun `kill` og `death` |
| `opening` | int8 | 0/1, rundens første kill af en fjende; kun `kill` og `death` |
| `traded` | int8 | 0/1. For en `kill`: det var en trade-kill. For en `death`: det blev hævnet inden for 5 s. Kun `kill` og `death`. |
| `noscope` | int8 | 0/1, kill'en var med et våben med scope skudt uden scope (hændelsens `noscope`); kun `kill` og `death` |
| `attackerBlind` | int8 | 0/1, dræberen var blændet, da de dræbte (hændelsens `attackerblind`); kun `kill` og `death` |
| `won` | int8 | 0/1, om rækkens side vandt runden; null, når `side` er tom |
| `matchWon` | int8 | 0/1, om rækkens hold vandt kampen; null, når `team` er tom, eller optagelsen ikke viser slutningen (se kampdokumentets `winner`) |
| `roundEndReason` | streng | hvordan rækkens runde endte: `elimination`, `bomb` (bomben gik af), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | streng | rækkens sides køb den runde: `pistol`, `eco`, `force`, `full` |
| `detail` | streng | hvert felt i hændelsen, som de andre kolonner ikke har, som et JSON-objekt (spillets egne navne): et skuds kugler (`fire_bullets`: origin, angles, inaccuracy, spread, recoil index, seed ...), et dødsfalds `dominated`, `revenge`, `attackerinair`, `wipe` ..., et items `defindex`, et fodtrins intet |
| `text` | streng | en chatlinje; kun `chat` |
| `entity` | int32 | granatens entity: et `throw`s flyvning (`grenade`-rækker), dens detonation og spillerne, den blændede, deler den |
| `hitgroup` | streng | hvor kuglen ramte (`head`, `chest` ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | mistet rustning; kun `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | hvor på kroppen kuglen ramte, i offerets koordinatsystem i meter (x fremad, y op fra fødderne, z til højre): skuddets stråle (`fire_bullets`, ellers angriberens øje og sigte) sporet til en krop stillet, som offeret stod og krumbøjede sig, ud til den del, `hitgroup` navngiver; kun `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | skuddets retning i samme koordinatsystem; `hitMiss` hvor langt (m) strålen gik forbi den navngivne del (0: gennem den); `hitFrom` `bullet` eller `aim` |
| `penetrated` | int16 | vægge dræbende kuglen gik igennem; `kill` og `death` |
| `throughSmoke` | int8 | 0/1, dræbt gennem røg; `kill` og `death` |
| `distance` | float32 | kill'ens afstand, som spillet tæller den (meter); `kill` og `death` |
| `assister` | streng | hvem der assisterede; `kill` og `death` |
| `flash`, `flashAlpha` | float32 | sekunder blænding tilbage, og hvor hvid den er; positioner |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; positioner |
| `zoom`, `duck`, `moveType` | | scopets zoomniveau, hvor langt der er krumbøjet (0-1), spillets bevægelsestype; positioner |
| `spottedBy` | streng | Steam-ID'erne på de fjender, der ser denne spiller, adskilt med `\|`; positioner |
| `inventory` | streng | alt spilleren bærer, adskilt med `\|`; positioner |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | det våben, der holdes: magasin og reserve; skud i den aktuelle serie; positioner |
| `punchPitch`, `punchYaw` | float32 | rekylens sigtepunch, i grader; positioner |
| `ping` | int16 | millisekunder; positioner |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | spillets egne scoreboard-tal for kampen indtil nu; positioner |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | penge brugt i runden og i kampen; udstyrsværdi, da runden startede; positioner |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, spillerens tilstand ved rækkens tid, hændelser medregnet: hjelm, defuse-kit, rustning overhovedet, scope (fra spillerens sidste positionssample op til rækken), blændet (inden for en `blind`, der ramte dem); hver række, der navngiver en spiller |
| `state_utility` | int16 | granater båret på tidspunktet (fra `inventory`); hver række, der navngiver en spiller |
| `state_weapon` | streng | våbnet i hånden på tidspunktet (på en `death`, offerets eget, hvor `weapon` er dræberens); hver række, der navngiver en spiller |
| `earn_round_cs2` | int16 | hvad runden gav: på `round_end` vindingsbelønningen eller tabsbonussen (med den plantende sides bonus), på `plant` og `defuse` spillerens 300 |

## Hændelser {#events}

Hvilken spiller en række navngiver, hvor den står, og hvilke kolonner den udfylder.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won`, `roundEndReason` og `buy` er udfyldt på hver række (`matchWon`, hvor kampens vinder er kendt); `inventory`, `money`, `equipment` og
`state_*`-kolonnerne på hver række, der navngiver en spiller (hændelser henter dem fra
spillerens sidste positionssample).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Også udfyldt |
|---|---|---|---|
| `position` | spilleren | spilleren (fødderne) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (i hånden), `place` og spillerens hele tilstand (kolonnerne fra `flash` og frem) - også i freeze-tid |
| `kill` | dræberen | hvor dræberen stod | `other` (offer), `weapon`, `headshot`, `opening`, `traded` (en trade-kill), `noscope`, `attackerBlind`, `place` |
| `death` | offeret | hvor offeret faldt | `other` (dræber; tom for verdenen), `weapon`, `headshot`, `opening`, `traded` (hævnet), `noscope`, `attackerBlind`, `place` |
| `hurt` | offeret | hvor offeret blev ramt | `other` (angriber), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - holdkammeraters og verdenens hits også |
| `shot` | skytten | hvor skuddet blev affyret fra | `weapon`, `place`, `detail` (spillets beretning om kuglerne) |
| `slash` | spilleren | hvor en kniv blev svinget | `weapon` = `Knife` |
| `grenade` | kasteren | granaten i flugt, ved spillernes sampling og der, hvor den stoppede | `weapon` (granaten), `entity` |
| `throw` | kasteren | hvor granaten blev kastet fra | `weapon` (granaten), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | kasteren | hvor den gik af | `weapon`, `throwerPlace` (kasterens sted på det tidspunkt); `place` bliver tom |
| `blind` | den blændede spiller | hvor de stod | `other` (blenderen), `duration`, `weapon` = `Flashbang`, `entity`, `place` - holdkammerater, der blev blændet, også |
| `plant` | planteren | hvor de plantede | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | desarmeren | hvor de desarmerede | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | hver spiller, der spillede runden | hvor spilleren sidst stod | `won`, `earn_round_cs2` (hvad runden gav dem: stigningen i sidens penge til næste freeze-tid, hvor reglerne tillader det, ellers reglernes egen), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | planteren (med deres Steam-ID), side `T`, det plantende hold | plantningens position | `weapon` = `C4 Explosive`, `place` (planterens, ved plantningen: hvor bomben lå); dens tid er, hvornår bomben gik af |
| `chat` | afsenderen | hvor de var | `text` |
| hver anden spilhændelse om en spiller, under spillets navn: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | spilleren | hvor de var (en granats hændelser: hvor den var) | `weapon` (et items), `entity`, `detail` (hvert felt i hændelsen) |

Hvad der er med, og hvad der ikke er:

- **position**-rækker er levende spillere på en side, uden for freeze-tid og opvarmning, hvert `--every` tick (otte i sekundet som standard).
- **kill**-rækker er kun kills af en fjende - ingen teamkill, selvmord eller dødsfald til verdenen. **death**-rækker er hvert dødsfald, de også.
- **explode**-rækker er hver plantet bombe, der gik af, efter demoens `bomb_exploded`: også i efter-fasen, når Ts allerede havde vundet ved elimination. En demo uden den hændelse får én for hver runde vundet af bomben, ved rundens slutning.
- **hurt**- og **blind**-rækker er kun mellem fjender.
- **shot** udelader knive og C4; granater er **throw**-rækker.
- **molotov** dækker molotovs og incendiaries (ilden, der starter).
- Holdkammeraters skade, blændinger af holdkammerater og tilskuere, hændelser i freeze-tid og alt mellem runder er ikke i tabellen.

Et gennemregnet eksempel fra testenes syntetiske demo (en røg kastet, et hovedskud som åbningskill, trades):

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

bobs dødsfald bliver hævnet af bens kill af ace 1,9 s senere (bobs `death`-række:
traded 1; bens `kill`-række: en trade-kill, traded 1); det andet hit på bob var
137 skade på 40 liv, så det tæller 40.

## `heat3d`-footerens hints {#the-heat3d-footer-hints}

Filens Parquet-footer (skema-nøgle/værdi-metadata) bærer læseinstruktioner under nøglen **`heat3d`**, et JSON-objekt:

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

| Post | Siger |
|---|---|
| `version`, `kind` | hints'ens version (1) og hvad der skrev dem (`cs2-demo`) |
| `axes.up` | filens Z er opad |
| `axes.flipY` | negér filens Y (se nedenfor) |
| `axes.scale` | 1: positioner bliver brugt, som de er, i spilenheder |
| `entity.size` | en spiller er **32 enheder** på tværs - CS2-spillerens bredde - den størrelse, en boksreplay tegner en med |
| `columns.x` / `y` / `z` | positionskolonnerne |
| `columns.time`, `timeUnit` | `time`, i sekunder |
| `columns.personId` | spilleren er personen |
| `columns.teamId` | siden er gruppen (så T og CT, ikke holdnavnene, farver grupperne) |
| `columns.sessionId` | hver runde (`roundId`) er en session |
| `columns.lookMode` og `dirX`-`dirZ` | kigge-retningen er en vektor i de kolonner |
| `columns.extra` | kolonnerne at beholde som filtre, i rækkefølge efter nytte |

En visning, der kender nøglen, åbner filen uden at sætte noget. Andre ignorerer den. For at læse den selv:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Akser og enheder {#axes-and-units}

Koordinaterne er spillets egne: **tommer** (én spilenhed; en spiller er 72 enheder høj stående og 32 på tværs), **Z opad**, og højrehåndet.

En visning, hvis verden er Y-opad, skal tegne spillets (x, y, z) som **(x, z, -y)** - Z bliver højden, og Y bliver negeret. Det er en rotation, ikke en spejling. Tegnes det, som en venstrehåndet Z-opad-verden gør, som (x, z, y), kommer hvert kort spejlvendt ud, A-sitet på den forkerte side; `flipY: true` er det, hintsene siger, for at forhindre det. [Kortudtrækket](map-export.md) skriver sin geometri allerede i (x, z, -y)-koordinatsystemet, i de samme enheder, så den ligger under tabellen uden nogen justering.

Afstande i visningen er mærket i meter; med en skala på 1 er de spilenheder. Gang med 0,0254 for meter.

## Størrelse {#size}

Positionerne dominerer: cirka ti spillere gange 8 samples i sekundet af levende spil ved standard `--every 8`, mindre for døde spillere og freeze-tid. At halvere `--every` fordobler dem; hændelser er uberørt.
