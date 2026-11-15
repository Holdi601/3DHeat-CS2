---
title: Tabela toplotne mape
nav_order: 8
lang: "bs"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# Tabela toplotne mape (`<match>.parquet`) {#the-heatmap-table-parquet}

Jedna Parquet datoteka po meču: pozicija svakog živog igrača, uzorkovana, i svaki
događaj gdje se desio, po jedan red - duga tabela koju preglednik 3DHeat čita
kao toplotnu mapu, a sve ostalo kao običnu tabelu. Kod:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(datoteka), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(redovi; pogledajte [Slaganje meča](building-matches.md)).

Datoteka se piše sa Snappy kompresijom u grupama redova od 256.000 redova.
Redovi su sortirani po `time`, zatim po `event`. U njoj su samo redovi unutar runde (od
kraja njenog freeze vremena do početka sljedeće runde).

Na sintetičkom demou iz testova, redovi događaja prve runde:

![redovi događaja tabele](../assets/img/table-rows.svg)

U `.3dheat` kontejneru tabela je član s ulogom `table`
([Jedna datoteka po meču](output-container.md)).

## Kolone {#columns}

Kolone, uvijek ovim redom. Tekstualne kolone su stringovi kodirani rječnikom
(`dictionary<int32, string>`) i nikad nisu null: "nema vrijednosti" je prazan
string. Numeričke kolone su null gdje red nema vrijednost.

| Kolona | Tip | Šta |
|---|---|---|
| `match` | string | ime meča (`alpha-vs-bravo-m1`, ili `...-b` za drugi lanac) |
| `map` | string | mapa, iz zaglavlja demoa (`de_x`) |
| `round` | int16 | broj runde, od 1 |
| `roundId` | string | `<match> #NN`, broj runde u dvije cifre (`alpha-vs-bravo-m1 #07`): jedinstven preko mečeva, sesija preglednika |
| `phase` | string | `freeze` u freeze vremenu runde (od kraja prethodne runde), `live` dok runda nije odlučena, `after` dok pobjednici love a gubitnici spašavaju |
| `time` | float64 | sekunde od početka meča (živi početak njegove prve datoteke), na jednom satu preko njegovih datoteka |
| `roundTime` | float32 | sekunde od kraja freeze vremena ove runde; negativno u freeze vremenu |
| `event` | string | šta je red - pogledajte [Događaji](#events) |
| `player` | string | ime igrača (za svaki događaj, koji je igrač ispod rečeno) |
| `steamid` | string | Steam ID igrača (64-bitni, kao tekst) |
| `side` | string | `T` ili `CT` u ovoj rundi; prazno kad igrač nije bio ni na jednoj strani |
| `team` | string | ime tima igrača (ili `Started T` / `Started CT`); za `explode`, tim koji postavlja |
| `x`, `y`, `z` | float32 | pozicija u igrinim koordinatama: inči (igrine jedinice), **Z prema gore**, desnoruki |
| `dirX`, `dirY`, `dirZ` | float32 | kamo igrač gleda, jedinični vektor u istom koordinatnom sistemu; samo pozicije |
| `health` | int16 | 0-100; pozicije, a kod `hurt` ono što je ostalo poslije pogotka |
| `armor` | int16 | 0-100; pozicije, a kod `hurt` ono što je ostalo poslije pogotka |
| `money` | int32 | novac igrača; samo pozicije |
| `equipment` | int32 | vrijednost onoga što igrač nosi; samo pozicije |
| `weapon` | string | oružje kako ga igra imenuje (`AK-47`, `M4A1-S`, `Knife` za svaki skin noža) |
| `place` | string | mapin vlastiti naziv mjesta na poziciji reda (`BombsiteA`, `CTSpawn`); prazno kod detonacija granata: demo ne imenuje mjesto gdje je granata eksplodirala |
| `throwerPlace` | string | naziv mjesta bacača kad je granata eksplodirala; samo detonacije granata |
| `other` | string | drugi igrač ubistva, smrti, pogotka ili flaša |
| `damage` | float32 | izgubljeno zdravlje; samo `hurt` |
| `duration` | float32 | sekunde zasljepljenja; samo `blind` |
| `headshot` | int8 | 0/1; samo `kill` i `death` |
| `opening` | int8 | 0/1, prvo ubistvo neprijatelja u rundi; samo `kill` i `death` |
| `traded` | int8 | 0/1. Za `kill`: bilo je trade ubistvo. Za `death`: osvećena je unutar 5 s. Samo `kill` i `death`. |
| `noscope` | int8 | 0/1, ubistvo optičkim oružjem ispaljenim bez optike (`noscope` događaja); samo `kill` i `death` |
| `attackerBlind` | int8 | 0/1, ubica je bio zasljepljen kad je ubio (`attackerblind` događaja); samo `kill` i `death` |
| `won` | int8 | 0/1, je li strana ovog reda dobila rundu; null kad je `side` prazan |
| `buy` | string | kupovina strane ovog reda u ovoj rundi: `pistol`, `eco`, `force`, `full` |
| `detail` | string | svako polje događaja koje ostale kolone ne nose, kao JSON objekat (igrina vlastita imena): meci pucnja (`fire_bullets`: ishodište, uglovi, nepreciznost, rasipanje, indeks trzaja, seed...), `dominated`, `revenge`, `attackerinair`, `wipe` smrti..., `defindex` predmeta, ništa za korak |
| `text` | string | red četa; samo `chat` |
| `entity` | int32 | entitet granate: let `throw`-a (redovi `grenade`), njegova detonacija i igrači koje je zasljepila dijele ga |
| `hitgroup` | string | gdje je metak pogodio (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | izgubljeni oklop; samo `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | gdje na tijelu je metak pogodio, u koordinatnom sistemu žrtve u metrima (x naprijed, y gore od stopala, z desno): zraka pucnja (`fire_bullets`, inače oko i pogled napadača) praćena do tijela u pozi u kojoj je žrtva stajala i čučala, do dijela koji imenuje `hitgroup`; samo `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | smjer pucnja u istom koordinatnom sistemu; `hitMiss` koliko daleko (m) je zraka prošla pored imenovanog dijela (0: kroz njega); `hitFrom` `bullet` ili `aim` |
| `penetrated` | int16 | zidovi kroz koje je prošao metak koji ubija; `kill` i `death` |
| `throughSmoke` | int8 | 0/1, ubijen kroz dim; `kill` i `death` |
| `distance` | float32 | udaljenost ubistva kako je igra računa (metri); `kill` i `death` |
| `assister` | string | ko je asistirao; `kill` i `death` |
| `flash`, `flashAlpha` | float32 | preostale sekunde fleša i koliko je bijel; pozicije |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozicije |
| `zoom`, `duck`, `moveType` | | nivo zooma optike, koliko je čučnuo (0-1), igrin tip kretanja; pozicije |
| `spottedBy` | string | Steam ID-evi neprijatelja koji vide ovog igrača, odvojeni sa `\|`; pozicije |
| `inventory` | string | sve što igrač nosi, odvojeno sa `\|`; pozicije |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | okvir i rezerva držanog oružja; pucnji u trenutnoj rafali; pozicije |
| `punchPitch`, `punchYaw` | float32 | aim punch trzaja, stepeni; pozicije |
| `ping` | int16 | milisekunde; pozicije |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | igrini vlastiti brojevi tabele rezultata za meč do sada; pozicije |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | novac potrošen u ovoj rundi i u meču; vrijednost opreme kad je runda počela; pozicije |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, stanje igrača u vrijeme reda, događaji uključeni: kaciga, set za deaktiviranje, bilo koji oklop, s optikom (od zadnjeg uzorka pozicije igrača do reda), zasljepljen (unutar `blind` koji ga je pogodio); svaki red koji imenuje igrača |
| `state_utility` | int16 | granate koje nosi u to vrijeme (iz `inventory`); svaki red koji imenuje igrača |
| `state_weapon` | string | oružje u ruci u to vrijeme (kod `death`, žrtvino vlastito, dok je `weapon` ubičino); svaki red koji imenuje igrača |
| `earn_round_cs2` | int16 | šta je runda isplatila: kod `round_end` nagrada za pobjedu ili bonus za poraz (s bonusom strane koja postavlja), kod `plant` i `defuse` 300 igrača |

## Događaji {#events}

Koji igrač je imenovan u redu, gdje stoji, i koje kolone red popunjava.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won` i `buy` popunjeni su u svakom redu; `inventory`, `money`, `equipment` i
kolone `state_*` u svakom redu koji imenuje igrača (događaji ih uzimaju iz
zadnjeg uzorka pozicije igrača).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Također popunjeno |
|---|---|---|---|
| `position` | igrač | igrač (stopala) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (držano), `place`, i cijelo stanje igrača (kolone od `flash` nadalje) - i u freeze vremenu |
| `kill` | ubica | gdje je ubica stajao | `other` (žrtva), `weapon`, `headshot`, `opening`, `traded` (trade ubistvo), `noscope`, `attackerBlind`, `place` |
| `death` | žrtva | gdje je žrtva pala | `other` (ubica; prazno za svijet), `weapon`, `headshot`, `opening`, `traded` (osvećena), `noscope`, `attackerBlind`, `place` |
| `hurt` | žrtva | gdje je žrtva pogođena | `other` (napadač), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - i pogoci saigrača i svijeta |
| `shot` | strijelac | odakle je pucano | `weapon`, `place`, `detail` (igrin opis metaka) |
| `slash` | igrač | gdje je nož zamahnut | `weapon` = `Knife` |
| `grenade` | bacač | granata u letu, pri uzorkovanju igrača i gdje se zaustavila | `weapon` (granata), `entity` |
| `throw` | bacač | odakle je granata bačena | `weapon` (granata), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | bacač | gdje je eksplodirala | `weapon`, `throwerPlace` (mjesto bacača u tom trenutku); `place` ostaje prazan |
| `blind` | zasljepljeni igrač | gdje je stajao | `other` (flešer), `duration`, `weapon` = `Flashbang`, `entity`, `place` - i zasljepljeni saigrači |
| `plant` | postavljač | gdje je postavio | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | deaktivator | gdje je deaktivirao | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | svaki igrač koji je odigrao rundu | gdje je igrač zadnji put stajao | `won`, `earn_round_cs2` (šta im je runda isplatila: porast novca strane do sljedećeg freeze vremena gdje pravila dopuštaju, inače vlastiti iznos pravila), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | postavljač (s njegovim Steam ID-em), strana `T`, tim koji postavlja | pozicija postavljanja | `weapon` = `C4 Explosive`, `place` (postavljačevo pri postavljanju: gdje je bomba ležala); njegovo vrijeme je kad je bomba eksplodirala |
| `chat` | pošiljalac | gdje je bio | `text` |
| svaki drugi događaj igre o igraču, pod igrinim imenom: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | igrač | gdje je bio (događaji granate: gdje je bila) | `weapon` (predmeta), `entity`, `detail` (svako polje događaja) |

Šta je unutra a šta nije:

- redovi **position** su živi igrači na nekoj strani, izvan freeze vremena i
  zagrijavanja, svakih `--every` tikova (zadano osam u sekundi).
- redovi **kill** su samo ubistva od neprijatelja - nema teamkilla, samoubistva ni smrti od
  svijeta. Redovi **death** su svaka smrt, i te uključene.
- redovi **explode** su svaka postavljena bomba koja je eksplodirala, prema demovom
  `bomb_exploded`: i u fazi poslije, kad su T-ovi već pobijedili
  eliminacijom. Demo bez tog događaja dobija jedan za svaku rundu dobijenu
  bombom, na kraju runde.
- redovi **hurt** i **blind** su samo među neprijateljima.
- **shot** izostavlja noževe i C4; granate su redovi **throw**.
- **molotov** pokriva molotove i incendiary (početak vatre).
- Šteta saigračima, flešovi saigrača i posmatrača, događaji u freeze vremenu
  i sve između rundi nisu u tabeli.

Radni primjer, iz sintetičkog demoa iz testova (bačen dim, opening
ubistvo headshotom, trade-ovi):

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

Bobovu smrt osvećuje benovo ubistvo acea 1,9 s kasnije (bobov red `death`:
traded 1; benov red `kill`: trade ubistvo, traded 1); drugi pogodak na boba bio je
137 štete na 40 zdravlja, pa se računa 40.

## Napomene `heat3d` u podnožju {#the-heat3d-footer-hints}

Parquet podnožje datoteke (key/value metapodaci sheme) nosi upute za čitanje
pod ključem **`heat3d`**, JSON objekat:

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

| Unos | Kaže |
|---|---|
| `version`, `kind` | verzija napomena (1) i šta ih je napisalo (`cs2-demo`) |
| `axes.up` | Z datoteke je prema gore |
| `axes.flipY` | negirajte Y datoteke (pogledajte ispod) |
| `axes.scale` | 1: pozicije se koriste kakve jesu, u igrinim jedinicama |
| `entity.size` | igrač je **32 jedinice** širok - širina CS2 igrača - veličina kojom ga crta replay s kutijama |
| `columns.x` / `y` / `z` | kolone pozicije |
| `columns.time`, `timeUnit` | `time`, u sekundama |
| `columns.personId` | igrač je osoba |
| `columns.teamId` | strana je grupa (pa T i CT, a ne imena timova, boje grupe) |
| `columns.sessionId` | svaka runda (`roundId`) je sesija |
| `columns.lookMode` i `dirX`-`dirZ` | smjer pogleda je vektor u tim kolonama |
| `columns.extra` | kolone koje se čuvaju kao filteri, redom korisnosti |

Preglednik koji zna ključ otvara datoteku bez ičeg za postaviti. Sve ostalo
ga ignoriše. Da ga pročitate sami:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Ose i jedinice {#axes-and-units}

Koordinate su igrine vlastite: **inči** (jedna igrina jedinica; igrač je visok 72
jedinice stojeći i širok 32), **Z prema gore**, desnoruke.

Preglednik čiji je svijet Y-gore mora nacrtati igrino (x, y, z) kao
**(x, z, -y)** - Z postaje visina a Y se negira. To je rotacija,
ne zrcaljenje. Nacrtano kako se crta ljevoruki Z-gore svijet, kao (x, z, y), svaka
mapa ispadne zrcaljena, A site na pogrešnoj strani; `flipY: true` je ono što
napomene kažu da to spriječi. [Izvoz mape](map-export.md) piše svoju geometriju
već u koordinatnom sistemu (x, z, -y), u istim jedinicama, pa leži ispod
tabele bez ikakvog podešavanja.

Udaljenosti u pregledniku označene su u metrima; sa skalom 1 to su
igrine jedinice. Pomnožite s 0,0254 za metre.

## Veličina {#size}

Pozicije dominiraju: oko deset igrača x 8 uzoraka u sekundi žive igre pri
zadanom `--every 8`, manje za mrtve igrače i freeze vrijeme. Prepolovljenje
`--every` ih udvostručuje; događaji nisu pogođeni.
