---
title: "Varmekarttabellen"
nav_order: 8
lang: "no"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Varmekarttabellen (`<kamp>.parquet`) {#the-heatmap-table-parquet}

Én Parquet-fil per kamp: hver levende spillers posisjon, samplet, og hver hendelse der den
skjedde, én rad hver - en lang tabell som 3DHeat-visningen leser som et varmekart, og alt annet som
en vanlig tabell. Kode:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(filen), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(radene; se [Bygge en kamp](building-matches.md)).

Filen skrives med Snappy-komprimering i radgrupper på 256 000 rader. Radene sorteres etter `time`,
deretter etter `event`. Bare rader innenfor en runde (fra slutten av rundens freeze time til neste
rundes start) er med.

På den syntetiske demoen fra testene, hendelsesradene i den første runden:

![hendelsesrader i tabellen](../assets/img/table-rows.svg)

I en `.3dheat`-beholder er tabellen elementet med rollen `table`
([En fil per kamp](output-container.md)).

## Kolonner {#columns}

Kolonnene, alltid i denne rekkefølgen. Tekstkolonner er ordbokskodede strenger
(`dictionary<int32, string>`) og er aldri null: «ingen verdi» er en tom streng. Numeriske kolonner er
null der en rad ikke har noen verdi.

| Kolonne | Type | Hva |
|---|---|---|
| `match` | streng | kampnavnet (`alpha-vs-bravo-m1`, eller `...-b` for en andre kjede) |
| `map` | streng | kartet, fra demoens header (`de_x`) |
| `round` | int16 | rundenummeret, 1-basert |
| `roundId` | streng | `<kamp> #NN`, rundenummeret med to siffer (`alpha-vs-bravo-m1 #07`): unikt på tvers av kamper, visningens økt |
| `phase` | streng | `freeze` i rundens freeze time (fra forrige rundes slutt), `live` til runden er avgjort, `after` mens vinnerne jakter og taperne sparer |
| `time` | float64 | sekunder siden kampen startet (livestarten i dens første fil), på én klokke på tvers av filene |
| `roundTime` | float32 | sekunder siden denne rundens freeze time tok slutt; negativ i freeze time |
| `event` | streng | hva raden er - se [Hendelser](#events) |
| `player` | streng | spillerens navn (for hver hendelse, hvilken spiller som nevnes, står under) |
| `steamid` | streng | spillerens Steam-ID (64-bit, som tekst) |
| `side` | streng | `T` eller `CT` denne runden; tom når spilleren ikke var på noen side |
| `team` | streng | spillerens lagnavn (eller `Started T` / `Started CT`); for `explode`, plantende lag |
| `x`, `y`, `z` | float32 | posisjon i spillets egne koordinater: tommer (spillenheter), **Z opp**, høyrehåndsregel |
| `dirX`, `dirY`, `dirZ` | float32 | hvor spilleren ser, en enhetsvektor i samme koordinatsystem; bare posisjoner |
| `health` | int16 | 0-100; posisjoner, og på `hurt` det som var igjen etter treffet |
| `armor` | int16 | 0-100; posisjoner, og på `hurt` det som var igjen etter treffet |
| `money` | int32 | spillerens penger; bare posisjoner |
| `equipment` | int32 | verdien av det spilleren bærer; bare posisjoner |
| `weapon` | streng | våpenet slik spillet kaller det (`AK-47`, `M4A1-S`, `Knife` for alle knivskinn) |
| `place` | streng | kartets eget stedsnavn på radens posisjon (`BombsiteA`, `CTSpawn`); tom ved granatdetonasjoner: demoen oppgir ikke noe sted for hvor en granat gikk av |
| `throwerPlace` | streng | kasterens stedsnavn da granaten gikk av; bare granatdetonasjoner |
| `other` | streng | den andre spilleren i et drap, dødsfall, treff eller blending |
| `damage` | float32 | tapt helse; bare `hurt` |
| `duration` | float32 | sekunder blendet; bare `blind` |
| `headshot` | int8 | 0/1; bare `kill` og `death` |
| `opening` | int8 | 0/1, rundens første drap på en fiende; bare `kill` og `death` |
| `traded` | int8 | 0/1. For en `kill`: det var et trade-drap. For en `death`: det ble hevnet innen 5 s. Bare `kill` og `death`. |
| `noscope` | int8 | 0/1, drapet var med et sikteutstyrt våpen avfyrt usikte (hendelsens `noscope`); bare `kill` og `death` |
| `attackerBlind` | int8 | 0/1, drapsmannen var blendet da de drepte (hendelsens `attackerblind`); bare `kill` og `death` |
| `won` | int8 | 0/1, om radens side vant runden; null når `side` er tom |
| `matchWon` | int8 | 0/1, om radens lag vant kampen; null når `team` er tom eller opptaket ikke viser slutten (se kampdokumentets `winner`) |
| `roundEndReason` | streng | hvordan radens runde endte: `elimination`, `bomb` (bomben gikk av), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | streng | radens sides kjøp denne runden: `pistol`, `eco`, `force`, `full` |
| `detail` | streng | hvert felt i hendelsen som de andre kolonnene ikke bærer, som et JSON-objekt (spillets egne navn): et skudds kuler (`fire_bullets`: opprinnelse, vinkler, unøyaktighet, spredning, rekylindeks, seed ...), et dødsfalls `dominated`, `revenge`, `attackerinair`, `wipe` ..., en gjenstands `defindex`, et fotsteg har ingenting |
| `text` | streng | en chatlinje; bare `chat` |
| `entity` | int32 | granatens entitet: en `throw`s flyvning (`grenade`-rader), dens detonasjon og spillerne den blendet deler den |
| `hitgroup` | streng | hvor kulen traff (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | tapt rustning; bare `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | hvor på kroppen kulen traff, i offerets koordinatsystem i meter (x forover, y opp fra føttene, z til høyre): skuddets stråle (`fire_bullets`, ellers angriperens øye og sikte) sporet til en kropp stilt slik offeret sto og bøyde seg, ned til delen `hitgroup` nevner; bare `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | skuddets retning i samme koordinatsystem; `hitMiss` hvor langt (m) strålen gikk forbi den nevnte delen (0: gjennom den); `hitFrom` `bullet` eller `aim` |
| `penetrated` | int16 | vegger drapskulen gikk gjennom; `kill` og `death` |
| `throughSmoke` | int8 | 0/1, drept gjennom røyk; `kill` og `death` |
| `distance` | float32 | drapets avstand slik spillet regner den (meter); `kill` og `death` |
| `assister` | streng | hvem som assisterte; `kill` og `death` |
| `flash`, `flashAlpha` | float32 | sekunder igjen av blendingen, og hvor hvit den er; posisjoner |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; posisjoner |
| `zoom`, `duck`, `moveType` | | zoomnivået på sikteutstyret, hvor langt som er bøyd (0-1), spillets bevegelsestype; posisjoner |
| `spottedBy` | streng | Steam-ID-ene til fiendene som ser denne spilleren, skilt med `\|`; posisjoner |
| `inventory` | streng | alt spilleren bærer, skilt med `\|`; posisjoner |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | det holdte våpenets magasin og reserve; skudd i det nåværende skuddsettet; posisjoner |
| `punchPitch`, `punchYaw` | float32 | rekylens sikte-støt, i grader; posisjoner |
| `ping` | int16 | millisekunder; posisjoner |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | spillets egne resultattavletall for kampen så langt; posisjoner |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | penger brukt denne runden og i kampen; utstyrsverdi da runden startet; posisjoner |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, spillerens tilstand på radens tid, hendelser inkludert: hjelm, desarmeringsverktøy, noe rustning, sikte (fra spillerens siste posisjonsprøve opp til raden), blendet (inne i en `blind` som traff dem); hver rad som nevner en spiller |
| `state_utility` | int16 | granater båret på tiden (fra `inventory`); hver rad som nevner en spiller |
| `state_weapon` | streng | våpenet i hånden på tiden (på en `death`, offerets eget, der `weapon` er drapsmannens); hver rad som nevner en spiller |
| `earn_round_cs2` | int16 | hva runden betalte: på `round_end` seiersbelønningen eller tapsbonusen (med den plantende sidens bonus), på `plant` og `defuse` spillerens 300 |

## Hendelser {#events}

Hvilken spiller en rad nevner, hvor den står, og hvilke kolonner den fyller.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won`, `roundEndReason`
og `buy` fylles på hver rad (`matchWon` der kampens vinner er kjent); `inventory`, `money`,
`equipment` og `state_*`-kolonnene på hver rad som nevner en spiller (hendelser henter dem fra
spillerens siste posisjonsprøve).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Fylles også |
|---|---|---|---|
| `position` | spilleren | spilleren (føttene) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (holdt), `place`, og spillerens hele tilstand (kolonnene fra `flash` og utover) - også i freeze time |
| `kill` | drapsmannen | der drapsmannen sto | `other` (offeret), `weapon`, `headshot`, `opening`, `traded` (et trade-drap), `noscope`, `attackerBlind`, `place` |
| `death` | offeret | der offeret falt | `other` (drapsmannen; tom for verden), `weapon`, `headshot`, `opening`, `traded` (hevnet), `noscope`, `attackerBlind`, `place` |
| `hurt` | offeret | der offeret ble truffet | `other` (angriperen), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - lagkameraters og verdens treff også |
| `shot` | skytteren | der skuddet ble avfyrt | `weapon`, `place`, `detail` (spillets beretning om kulene) |
| `slash` | spilleren | der en kniv ble svingt | `weapon` = `Knife` |
| `grenade` | kasteren | granaten i flukt, ved spillernes samplingsrate og der den stoppet | `weapon` (granaten), `entity` |
| `throw` | kasteren | der granaten ble kastet fra | `weapon` (granaten), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | kasteren | der den gikk av | `weapon`, `throwerPlace` (kasterens sted i det øyeblikket); `place` står tom |
| `blind` | spilleren som ble blendet | der de sto | `other` (blenderen), `duration`, `weapon` = `Flashbang`, `entity`, `place` - lagkamerater som ble blendet også |
| `plant` | planteren | der de plantet | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | desarmereren | der de desarmerte | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | hver spiller som spilte runden | der spilleren sist sto | `won`, `earn_round_cs2` (hva runden betalte dem: økningen i sidens penger til neste freeze time der reglene tillater det, ellers reglenes egen), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | planteren (med sin Steam-ID), side `T`, det plantende laget | plantingens posisjon | `weapon` = `C4 Explosive`, `place` (planterens ved plantingen: der bomben lå); tiden er når bomben gikk av |
| `chat` | avsenderen | der de var | `text` |
| hver annen spillhendelse om en spiller, under spillets navn: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | spilleren | der de var (en granats hendelser: der den var) | `weapon` (en gjenstands), `entity`, `detail` (hvert felt i hendelsen) |

Hva som er med og ikke:

- **position**-rader er levende spillere på en side, utenfor freeze time og oppvarming, hver
  `--every` tick (åtte per sekund som standard).
- **kill**-rader er bare drap av en fiende - ikke lagkameraddrap, selvmord eller dødsfall for
  verden. **death**-rader er alle dødsfall, også disse.
- **explode**-rader er hver plantet bombe som gikk av, etter demoens `bomb_exploded`: også i
  etter-fasen, når T allerede hadde vunnet ved eliminering. En demo uten den hendelsen får én for
  hver runde vunnet av bomben, ved rundens slutt.
- **hurt**- og **blind**-rader er bare mellom fiender.
- **shot** utelater kniver og C4; granater er **throw**-rader.
- **molotov** dekker molotover og brannbomber (ilden som starter).
- Lagkameraters skade, blendinger av lagkamerater og tilskuere, hendelser i freeze time og alt
  mellom runder er ikke i tabellen.

Et utført eksempel, fra den syntetiske demoen i testene (en røykgranat kastet, et hodeskudd som
åpningsdrap, trader):

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

bobs dødsfall blir hevnet av bens drap av ace 1,9 s senere (bobs `death`-rad: traded 1; bens
`kill`-rad: et trade-drap, traded 1); det andre treffet på bob var 137 skade på 40 helse, så det
teller 40.

## `heat3d`-hintene i fotsporet {#the-heat3d-footer-hints}

Filens Parquet-fotspor (skjemaets nøkkel/verdi-metadata) bærer leseinstruksjoner under nøkkelen
**`heat3d`**, et JSON-objekt:

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

| Oppføring | Sier |
|---|---|
| `version`, `kind` | hintenes versjon (1) og hva som skrev dem (`cs2-demo`) |
| `axes.up` | filens Z er opp |
| `axes.flipY` | negér filens Y (se under) |
| `axes.scale` | 1: posisjoner brukes som de er, i spillenheter |
| `entity.size` | en spiller er **32 enheter** på tvers - bredden til en CS2-spiller - størrelsen en boksavspilling tegner en for |
| `columns.x` / `y` / `z` | posisjonskolonnene |
| `columns.time`, `timeUnit` | `time`, i sekunder |
| `columns.personId` | spilleren er personen |
| `columns.teamId` | siden er gruppen (så T og CT, ikke lagnavnene, farger gruppene) |
| `columns.sessionId` | hver runde (`roundId`) er en økt |
| `columns.lookMode` og `dirX`-`dirZ` | sikteretningen er en vektor i de kolonnene |
| `columns.extra` | kolonnene som skal beholdes som filtre, i rekkefølge etter nytte |

En visning som kjenner nøkkelen, åpner filen uten at du må sette noe. Andre ignorerer den. For å
lese den selv:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Akser og enheter {#axes-and-units}

Koordinatene er spillets egne: **tommer** (én spillenhet; en spiller er 72 enheter høy stående og
32 på tvers), **Z opp**, og høyrehåndsregel.

En visning der verden er Y-opp, må tegne spillets (x, y, z) som **(x, z, -y)** - Z blir høyden og Y
negeres. Det er en rotasjon, ikke en speiling. Tegnes det slik en venstrehåndsverden med Z opp
tegnes, som (x, z, y), kommer hvert kart speilvendt, A-sonen på feil side; `flipY: true` er det
hintene sier for å hindre det. [Eksport av kart](map-export.md) skriver sin geometri allerede i
(x, z, -y)-koordinatsystemet, i de samme enhetene, så den ligger under tabellen uten justering.

Avstander i visningen merkes i meter; med skala 1 er de spillenheter. Gang med 0,0254 for meter.

## Størrelse {#size}

Posisjonene dominerer: omtrent ti spillere ganger 8 prøver per sekund av levende spill ved standard
`--every 8`, mindre for døde spillere og i freeze time. Halvering av `--every` dobler dem; hendelser
påvirkes ikke.
