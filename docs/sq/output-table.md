---
title: "Tabela e hartës së nxehtësisë"
nav_order: 8
lang: "sq"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Tabela e hartës së nxehtësisë (`<match>.parquet`) {#the-heatmap-table-parquet}

Një skedar Parquet për ndeshje: pozicioni i çdo lojtari të gjallë, marrë si mostër, dhe çdo
ngjarje ku ndodhi, një rresht secila - një tabelë e gjatë që shikuesi 3DHeat e lexon
si hartë nxehtësie, dhe çdo gjë tjetër si tabelë të zakonshme. Kodi:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(skedari), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(rreshtat; shih [Ndërtimi i një ndeshjeje](building-matches.md)).

Skedari shkruhet me ngjeshje Snappy në grupe rreshtash prej 256,000 rreshtash.
Rreshtat renditen sipas `time`, pastaj sipas `event`. Aty janë vetëm rreshtat brenda një raundi (nga
fundi i kohës së ngrirjes deri në nisjen e raundit tjetër).

Në demon sintetike të testeve, rreshtat e ngjarjeve të raundit të parë:

![rreshtat e ngjarjeve të tabelës](../assets/img/table-rows.svg)

Në një kontejner `.3dheat` tabela është anëtari me rolin `table`
([Një skedar për ndeshje](output-container.md)).

## Kolonat {#columns}

Kolonat, gjithmonë në këtë rend. Kolonat tekst janë vargje të koduara me fjalor
(`dictionary<int32, string>`) dhe nuk janë kurrë null: "pa vlerë" është një varg
bosh. Kolonat numerike janë null ku një rresht nuk ka vlerë.

| Kolona | Lloji | Çfarë |
|---|---|---|
| `match` | string | emri i ndeshjes (`alpha-vs-bravo-m1`, ose `...-b` për një zinxhir të dytë) |
| `map` | string | harta, nga koka e demos (`de_x`) |
| `round` | int16 | numri i raundit, nga 1 |
| `roundId` | string | `<match> #NN`, numri i raundit me dy shifra (`alpha-vs-bravo-m1 #07`): unik nëpër ndeshje, sesioni i shikuesit |
| `phase` | string | `freeze` në kohën e ngrirjes së raundit (nga fundi i raundit të mëparshëm), `live` derisa raundi vendoset, `after` ndërsa fituesit gjuajnë dhe humbësit shpëtojnë pajisjet |
| `time` | float64 | sekonda që nga nisja e ndeshjes (fillimi live i skedarit të parë), në një orë të vetme nëpër skedarët e saj |
| `roundTime` | float32 | sekonda që nga mbarimi i kohës së ngrirjes së këtij raundi; negative në kohën e ngrirjes |
| `event` | string | çfarë është rreshti - shih [Ngjarjet](#events) |
| `player` | string | emri i lojtarit (për çdo ngjarje, cili lojtar thuhet më poshtë) |
| `steamid` | string | Steam ID i lojtarit (64-bit, si tekst) |
| `side` | string | `T` ose `CT` këtë raund; bosh kur lojtari ishte në asnjë anë |
| `team` | string | emri i ekipit të lojtarit (ose `Started T` / `Started CT`); për `explode`, ekipi që vendosi |
| `x`, `y`, `z` | float32 | pozicioni në koordinatat e vetë lojës: inçe (njësi loje), **Z lart**, dorës së djathtë |
| `dirX`, `dirY`, `dirZ` | float32 | ku shikon lojtari, një vektor njësi në të njëjtin sistem; vetëm pozicionet |
| `health` | int16 | 0-100; pozicionet, dhe te `hurt` çfarë mbeti pas goditjes |
| `armor` | int16 | 0-100; pozicionet, dhe te `hurt` çfarë mbeti pas goditjes |
| `money` | int32 | paratë e lojtarit; vetëm pozicionet |
| `equipment` | int32 | vlera e asaj që mbart lojtari; vetëm pozicionet |
| `weapon` | string | arma siç e emërton loja (`AK-47`, `M4A1-S`, `Knife` për çdo skin thike) |
| `place` | string | emri i vendit të hartës në pozicionin e rreshtit (`BombsiteA`, `CTSpawn`); bosh te shpërthimet e granatave: demoja nuk emërton vend për ku shpërtheu një granatë |
| `throwerPlace` | string | emri i vendit të hedhësit kur granata shpërtheu; vetëm shpërthimet e granatave |
| `other` | string | lojtari tjetër i një vrasjeje, vdekjeje, goditjeje ose flash-i |
| `damage` | float32 | shëndeti i humbur; vetëm `hurt` |
| `duration` | float32 | sekonda i verbuar; vetëm `blind` |
| `headshot` | int8 | 0/1; vetëm `kill` dhe `death` |
| `opening` | int8 | 0/1, vrasja e parë e një armiku në raund; vetëm `kill` dhe `death` |
| `traded` | int8 | 0/1. Për një `kill`: ishte vrasje trade. Për një `death`: u hakmor brenda 5 s. Vetëm `kill` dhe `death`. |
| `noscope` | int8 | 0/1, vrasja ishte me një armë me dylbi të gjuajtur pa dylbi (`noscope` i ngjarjes); vetëm `kill` dhe `death` |
| `attackerBlind` | int8 | 0/1, vrasësi ishte i verbuar nga flash kur vrau (`attackerblind` i ngjarjes); vetëm `kill` dhe `death` |
| `won` | int8 | 0/1, nëse ana e këtij rreshti e fitoi raundin; null kur `side` është bosh |
| `matchWon` | int8 | 0/1, nëse ekipi i këtij rreshti e fitoi ndeshjen; null kur `team` është bosh ose regjistrimi nuk e tregon fundin (shih `winner` të dokumentit të ndeshjes) |
| `roundEndReason` | string | si përfundoi raundi i rreshtit: `elimination`, `bomb` (bomba shpërtheu), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | string | blerja e anës së këtij rreshti këtë raund: `pistol`, `eco`, `force`, `full` |
| `detail` | string | çdo fushë e ngjarjes që kolonat e tjera nuk e mbartin, si objekt JSON (emrat e vetë lojës): plumbat e një të shëne (`fire_bullets`: origjina, këndet, pasaktësia, përhapja, indeksi i rikthimit, fara...), `dominated`, `revenge`, `attackerinair`, `wipe`... të një vdekjeje, `defindex` i një sendi, asgjë për një hap |
| `text` | string | një rresht bisede; vetëm `chat` |
| `entity` | int32 | entiteti i granatës: fluturimi i një `throw` (rreshtat `grenade`), shpërthimi i saj dhe lojtarët që verboi e ndajnë |
| `hitgroup` | string | ku goditi plumbi (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | parzmorja e humbur; vetëm `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | ku në trup goditi plumbi, në sistemin e viktimës në metra (x përpara, y lart nga këmbët, z djathtas): rrezja e të shënës (`fire_bullets`, përndryshe syri dhe pamja e sulmuesit) e ndjekur te një trup i pozuar si qëndroi viktima, në këmbë dhe i kërrusur, mbi pjesën që emërton `hitgroup`; vetëm `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | drejtimi i të shënës në të njëjtin sistem; `hitMiss` sa larg (m) e kaloi rrezja pjesën e emërtuar (0: përmes saj); `hitFrom` `bullet` ose `aim` |
| `penetrated` | int16 | muret nëpër të cilët kaloi plumbi vrasës; `kill` dhe `death` |
| `throughSmoke` | int8 | 0/1, vrarë nëpër një tym; `kill` dhe `death` |
| `distance` | float32 | largësia e vrasjes siç e numëron loja (metra); `kill` dhe `death` |
| `assister` | string | kush asistoi; `kill` dhe `death` |
| `flash`, `flashAlpha` | float32 | sekonda flash-i që mbeten, dhe sa i bardhë; pozicionet |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozicionet |
| `zoom`, `duck`, `moveType` | | niveli i zmadhimit të dylbisë, sa i kërrusur (0-1), lloji i lëvizjes së lojës; pozicionet |
| `spottedBy` | string | Steam ID-të e armiqve që e shohin këtë lojtar, të ndara me `\|`; pozicionet |
| `inventory` | string | gjithçka që mbart lojtari, e ndarë me `\|`; pozicionet |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | karikatori dhe rezerva e armës në dorë; të shënat në breshërinë aktuale; pozicionet |
| `punchPitch`, `punchYaw` | float32 | goditja e synimit nga rikthimi, gradë; pozicionet |
| `ping` | int16 | milisekonda; pozicionet |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | numërimet e vetë tabelës së rezultateve të lojës për ndeshjen deri tani; pozicionet |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | paratë e shpenzuara këtë raund dhe në ndeshje; vlera e pajisjeve kur nisi raundi; pozicionet |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, gjendja e lojtarit në kohën e rreshtit, ngjarjet të përfshira: helmetë, kit çaktivizimi, çfarëdo parzmore, me dylbi, i verbuar (brenda një `blind` që e goditi); çdo rresht që emërton një lojtar |
| `state_utility` | int16 | granata të mbartura në atë kohë (nga `inventory`); çdo rresht që emërton një lojtar |
| `state_weapon` | string | arma në dorë në atë kohë (te një `death`, ajo e vetë viktimës, ku `weapon` është e vrasësit); çdo rresht që emërton një lojtar |
| `earn_round_cs2` | int16 | çfarë pagoi raundi: te `round_end` shpërblimi i fitores ose bonusi i humbjes (me bonusin e anës që vendosi), te `plant` dhe `defuse` 300 të lojtarit |

## Ngjarjet {#events}

Cilin lojtar e emërton një rresht, ku qëndron, dhe cilat kolona i plotëson.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won`, `roundEndReason` dhe `buy` plotësohen në çdo rresht (`matchWon` ku fituesi i ndeshjes dihet); `inventory`, `money`, `equipment` dhe
kolonat `state_*` në çdo rresht që emërton një lojtar (ngjarjet i marrin nga
mostra e fundit e pozicionit të lojtarit).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Gjithashtu plotësohen |
|---|---|---|---|
| `position` | lojtari | lojtari (këmbët) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (në dorë), `place`, dhe gjithë gjendja e lojtarit (kolonat nga `flash` e tutje) - edhe në kohën e ngrirjes |
| `kill` | vrasësi | ku qëndronte vrasësi | `other` (viktima), `weapon`, `headshot`, `opening`, `traded` (vrasje trade), `noscope`, `attackerBlind`, `place` |
| `death` | viktima | ku ra viktima | `other` (vrasësi; bosh për botën), `weapon`, `headshot`, `opening`, `traded` (e hakmorur), `noscope`, `attackerBlind`, `place` |
| `hurt` | viktima | ku u godit viktima | `other` (sulmuesi), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - edhe goditjet e shokëve të ekipit dhe të botës |
| `shot` | gjuajtësi | nga ku u gjuajt | `weapon`, `place`, `detail` (përshkrimi i lojës për plumbat) |
| `slash` | lojtari | ku u vrapua një thikë | `weapon` = `Knife` |
| `grenade` | hedhësi | granata në fluturim, me mostrimin e lojtarëve dhe ku ndaloi | `weapon` (granata), `entity` |
| `throw` | hedhësi | nga ku u hodh granata | `weapon` (granata), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | hedhësi | ku shpërtheu | `weapon`, `throwerPlace` (vendi i hedhësit në atë moment); `place` mbetet bosh |
| `blind` | lojtari i verbuar | ku qëndronte | `other` (flashuesi), `duration`, `weapon` = `Flashbang`, `entity`, `place` - edhe shokët e ekipit të verbuar |
| `plant` | vendosësi | ku vendosi | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | çaktivizuesi | ku çaktivizoi | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | çdo lojtar që e luajti raundin | ku qëndroi lojtari për herë të fundit | `won`, `earn_round_cs2` (çfarë i pagoi raundi: rritja e parave të anës deri në kohën tjetër të ngrirjes ku e lejojnë rregullat, përndryshe e rregullave vetë), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | vendosësi (me Steam ID-në e tij), ana `T`, ekipi që vendosi | pozicioni i vendosjes | `weapon` = `C4 Explosive`, `place` (ai i vendosësit gjatë vendosjes: ku ndodhet bomba); koha e tij është kur shpërtheu bomba |
| `chat` | dërguesi | ku ishte | `text` |
| çdo ngjarje tjetër loje për një lojtar, nën emrin e lojës: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | lojtari | ku ishte (për ngjarjet e një granate: ku ishte ajo) | `weapon` (e një sendi), `entity`, `detail` (çdo fushë e ngjarjes) |

Çfarë përfshihet dhe çfarë jo:

- rreshtat **position** janë lojtarë të gjallë në një anë, jashtë kohës së ngrirjes dhe
  ngrohjes, çdo `--every` tick-e (tetë në sekondë si parazgjedhje).
- rreshtat **kill** janë vetëm vrasje nga një armik - jo teamkill, vetëvrasje apo vdekje nga
  bota. Rreshtat **death** janë çdo vdekje, edhe ato.
- rreshtat **explode** janë çdo bombë e vendosur që shpërtheu, sipas `bomb_exploded` të
  demos: edhe në fazën after, kur T-të kishin fituar tashmë me
  eliminim. Një demo pa atë ngjarje merr një për çdo raund të fituar nga
  bomba, në fundin e raundit.
- rreshtat **hurt** dhe **blind** janë vetëm midis armiqve.
- **shot** lë jashtë thikat dhe C4; granatat janë rreshta **throw**.
- **molotov** mbulon molotovët dhe incendiary (nisja e zjarrit).
- Dëmi ndaj shokëve të ekipit, flash-et ndaj shokëve dhe shikuesve, ngjarjet
  e kohës së ngrirjes dhe çdo gjë midis raundeve nuk janë në tabelë.

Një shembull i zgjidhur, nga demoja sintetike e testeve (një tym i hedhur, një
vrasje hapëse me goditje në kokë, trade):

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

Vdekja e bob hakmorret nga vrasja e ace nga ben 1.9 s më vonë (rreshti `death` i bob:
traded 1; rreshti `kill` i ben: vrasje trade, traded 1); goditja e dytë mbi bob ishte
137 dëm mbi 40 shëndet, kështu që llogaritet 40.

## Sugjerimet `heat3d` në fund të skedarit {#the-heat3d-footer-hints}

Fundi i Parquet i skedarit (metadata çelës/vlerë e skemës) mbart udhëzime leximi
nën çelësin **`heat3d`**, një objekt JSON:

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

| Hyrja | Thotë |
|---|---|
| `version`, `kind` | versioni i sugjerimeve (1) dhe ç'i shkroi (`cs2-demo`) |
| `axes.up` | Z e skedarit është lart |
| `axes.flipY` | mohoje Y të skedarit (shih më poshtë) |
| `axes.scale` | 1: pozicionet përdoren siç janë, në njësi loje |
| `entity.size` | një lojtar është **32 njësi** i gjerë - gjerësia e lojtarit të CS2 - madhësia që e vizaton një riprodhim me kuti |
| `columns.x` / `y` / `z` | kolonat e pozicionit |
| `columns.time`, `timeUnit` | `time`, në sekonda |
| `columns.personId` | lojtari është personi |
| `columns.teamId` | ana është grupi (pra T dhe CT, jo emrat e ekipeve, i ngjyrosin grupet) |
| `columns.sessionId` | çdo raund (`roundId`) është një sesion |
| `columns.lookMode` dhe `dirX`-`dirZ` | drejtimi i shikimit është vektor në ato kolona |
| `columns.extra` | kolonat që mbahen si filtra, sipas dobisë |

Një shikues që e njeh çelësin e hap skedarin pa asgjë për të vendosur. Çdo gjë tjetër
e shpërfill. Për ta lexuar vetë:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Boshtet dhe njësitë {#axes-and-units}

Koordinatat janë ato të vetë lojës: **inçe** (një njësi loje; një lojtar është 72
njësi i gjatë në këmbë dhe 32 i gjerë), **Z lart**, dhe dorës së djathtë.

Një shikues bota e të cilit ka Y lart duhet ta vizatojë (x, y, z) të lojës si
**(x, z, -y)** - Z bëhet lartësia dhe Y mohohet. Kjo është rrotullim,
jo pasqyrim. Vizatuar si në një botë me Z lart dorës së majtë, si (x, z, y), çdo
hartë del e pasqyruar, site A në anën e gabuar; `flipY: true` është ajo që thonë
sugjerimet për ta parandaluar. [Eksporti i hartës](map-export.md) e shkruan gjeometrinë e tij
tashmë në sistemin (x, z, -y), në të njëjtat njësi, kështu që shtrihet nën
tabelë pa asnjë rregullim.

Largësitë në shikues etiketohen në metra; me shkallë 1 janë
njësi loje. Shumëzo me 0.0254 për metra.

## Madhësia {#size}

Pozicionet dominojnë: rreth dhjetë lojtarë x 8 mostra në sekondë loje live me
`--every 8` të parazgjedhur, më pak për lojtarët e vdekur dhe kohën e ngrirjes. Përgjysmimi i
`--every` i dyfishon; ngjarjet nuk preken.
