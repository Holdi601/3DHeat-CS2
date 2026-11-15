---
title: "Toplinska tablica"
nav_order: 8
lang: "hr"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# Toplinska tablica (`<meč>.parquet`) {#the-heatmap-table-parquet}

Jedna Parquet datoteka po meču: položaj svakog živog igrača, uzorkovan, i svaki događaj na mjestu gdje se dogodio, jedan redak za svaki - duga tablica koju preglednik 3DHeat čita kao toplinsku kartu, a bilo što drugo kao običnu tablicu. Kod:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(datoteka),
[`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(redci; vidi [Sastavljanje meča](building-matches.md)).

Datoteka se piše sa Snappy kompresijom u grupama redaka od 256.000 redaka. Redci su sortirani po `time`, pa po `event`. U njoj su samo redci unutar runde (od kraja freeze timea runde do početka sljedeće).

Na sintetičkoj demo snimci iz testova, redci događaja prve runde:

![redci događaja tablice](../assets/img/table-rows.svg)

U `.3dheat` spremniku tablica je član s ulogom `table` ([Jedna datoteka po meču](output-container.md)).

## Stupci {#columns}

Stupci, uvijek ovim redom. Tekstualni stupci su nizovi kodirani rječnikom (`dictionary<int32, string>`) i nikad nisu null: "nema vrijednosti" je prazan niz. Brojčani stupci su null gdje redak nema vrijednost.

| Stupac | Tip | Što |
|---|---|---|
| `match` | niz | ime meča (`alpha-vs-bravo-m1`, ili `...-b` za drugi lanac) |
| `map` | niz | karta, iz zaglavlja demo snimke (`de_x`) |
| `round` | int16 | broj runde, počevši od 1 |
| `roundId` | niz | `<meč> #NN`, broj runde s dvije znamenke (`alpha-vs-bravo-m1 #07`): jedinstven među mečevima; sesija preglednika |
| `phase` | niz | `freeze` u freeze timeu runde (od kraja prethodne runde), `live` dok runda nije odlučena, `after` dok pobjednici love a gubitnici štede |
| `time` | float64 | sekunde od početka meča (živi početak prve datoteke), na jednom satu kroz njegove datoteke |
| `roundTime` | float32 | sekunde od kraja freeze timea ove runde; negativno u freeze timeu |
| `event` | niz | što redak je - vidi [Događaji](#events) |
| `player` | niz | ime igrača (za svaki događaj, koji igrač je rečeno ispod) |
| `steamid` | niz | Steam ID igrača (64-bitni, kao tekst) |
| `side` | niz | `T` ili `CT` u ovoj rundi; prazno kad igrač nije bio ni na jednoj strani |
| `team` | niz | naziv tima igrača (ili `Started T` / `Started CT`); za `explode`, tim koji je postavljao |
| `x`, `y`, `z` | float32 | položaj u koordinatama same igre: inči (jedinice igre), **Z gore**, desnoruko |
| `dirX`, `dirY`, `dirZ` | float32 | kamo igrač gleda, jedinični vektor u istom okviru; samo pozicije |
| `health` | int16 | 0-100; pozicije, a na `hurt` ono što je ostalo nakon pogotka |
| `armor` | int16 | 0-100; pozicije, a na `hurt` ono što je ostalo nakon pogotka |
| `money` | int32 | novac igrača; samo pozicije |
| `equipment` | int32 | vrijednost onoga što igrač nosi; samo pozicije |
| `weapon` | niz | oružje kako ga igra imenuje (`AK-47`, `M4A1-S`, `Knife` za svaki skin noža) |
| `place` | niz | vlastiti naziv mjesta igre na položaju retka (`BombsiteA`, `CTSpawn`); prazno kod detonacija granata: demo ne imenuje mjesto gdje je granata eksplodirala |
| `throwerPlace` | niz | naziv mjesta bacača kad je granata eksplodirala; samo detonacije granata |
| `other` | niz | drugi igrač ubojstva, smrti, pogotka ili bljeska |
| `damage` | float32 | izgubljeno zdravlje; samo `hurt` |
| `duration` | float32 | sekunde slijepila; samo `blind` |
| `headshot` | int8 | 0/1; samo `kill` i `death` |
| `opening` | int8 | 0/1, prvo ubojstvo neprijatelja u rundi; samo `kill` i `death` |
| `traded` | int8 | 0/1. Za `kill`: bilo je ubojstvo razmjenom. Za `death`: smrt je osvećena unutar 5 s. Samo `kill` i `death`. |
| `noscope` | int8 | 0/1, ubojstvo oružjem s optikom ispaljenim bez nje (događaj `noscope`); samo `kill` i `death` |
| `attackerBlind` | int8 | 0/1, ubojica je bio zaslijepljen kad je ubio (događaj `attackerblind`); samo `kill` i `death` |
| `won` | int8 | 0/1, je li strana ovog retka pobijedila rundu; null kad je `side` prazan |
| `buy` | niz | kupovina strane ovog retka u ovoj rundi: `pistol`, `eco`, `force`, `full` |
| `detail` | niz | svako polje događaja koje ostali stupci ne nose, kao JSON objekt (vlastita imena igre): pucanj (`fire_bullets`: ishodište, kutovi, netočnost, raspršenje, indeks trzaja, sjeme...), `dominated`, `revenge`, `attackerinair`, `wipe`... smrti, `defindex` predmeta, ništa za korak |
| `text` | niz | redak chata; samo `chat` |
| `entity` | int32 | entitet granate: let `throw` (redci `grenade`), njezina detonacija i igrači koje je zaslijepila dijele ga |
| `hitgroup` | niz | gdje je metak pogodio (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | izgubljeni oklop; samo `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | gdje je na tijelu metak pogodio, u okviru žrtve u metrima (x naprijed, y gore od stopala, z desno): zraka pucnja (`fire_bullets`, inače oko napadača i pogled) praćena do tijela postavljenog kako je žrtva stajala i čučala, na dio koji imenuje `hitgroup`; samo `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | smjer pucnja u istom okviru; `hitMiss` koliko je daleko (m) zraka promašila imenovani dio (0: kroz njega); `hitFrom` `bullet` ili `aim` |
| `penetrated` | int16 | zidovi kroz koje je ubojiti metak prošao; `kill` i `death` |
| `throughSmoke` | int8 | 0/1, ubijeno kroz dim; `kill` i `death` |
| `distance` | float32 | udaljenost ubojstva kako je igra računa (metri); `kill` i `death` |
| `assister` | niz | tko je asistirao; `kill` i `death` |
| `flash`, `flashAlpha` | float32 | preostale sekunde bljeska, i koliko je bijel; pozicije |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozicije |
| `zoom`, `duck`, `moveType` | | razina zuma optike, koliko je čučnuo (0-1), vrsta kretanja igre; pozicije |
| `spottedBy` | niz | Steam ID-ovi neprijatelja koji vide ovog igrača, odvojeni s `\|`; pozicije |
| `inventory` | niz | sve što igrač nosi, odvojeno s `\|`; pozicije |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | spremnik i rezerva oružja u ruci; pucnji u trenutnom rafalu; pozicije |
| `punchPitch`, `punchYaw` | float32 | udarac nišana od trzaja, stupnjevi; pozicije |
| `ping` | int16 | milisekunde; pozicije |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | vlastiti brojevi rezultata igre za meč do sada; pozicije |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | novac potrošen u ovoj rundi i u cijelom meču; vrijednost opreme kad je runda počela; pozicije |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, stanje igrača u vrijeme retka, uključujući događaje: kaciga, komplet za deaktivaciju, bilo kakav oklop, optika (od igračeve zadnje pozicije do retka), zaslijepljen (unutar `blind` koji ga je pogodio); svaki redak koji imenuje igrača |
| `state_utility` | int16 | granate koje nosi u to vrijeme (iz `inventory`); svaki redak koji imenuje igrača |
| `state_weapon` | niz | oružje u ruci u to vrijeme (na `death`, vlastito žrtvino, dok je `weapon` ubojičino); svaki redak koji imenuje igrača |
| `earn_round_cs2` | int16 | što je runda isplatila: na `round_end` nagrada za pobjedu ili bonus za poraz (s bonusom strane koja je postavljala), na `plant` i `defuse` 300 igrača |

## Događaji {#events}

Koji igrač je u retku, gdje stoji, i koje stupce popunjava. `match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won` i `buy` popunjeni su u svakom retku; `inventory`, `money`, `equipment` i stupci `state_*` u svakom retku koji imenuje igrača (događaji ih uzimaju iz igračeve zadnje uzorkovane pozicije).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Također popunjeno |
|---|---|---|---|
| `position` | igrač | igrač (stopala) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (u ruci), `place`, i cijelo stanje igrača (stupci od `flash` nadalje) - i u freeze timeu |
| `kill` | ubojica | gdje je ubojica stajao | `other` (žrtva), `weapon`, `headshot`, `opening`, `traded` (ubojstvo razmjenom), `noscope`, `attackerBlind`, `place` |
| `death` | žrtva | gdje je žrtva pala | `other` (ubojica; prazno za svijet), `weapon`, `headshot`, `opening`, `traded` (osvećena), `noscope`, `attackerBlind`, `place` |
| `hurt` | žrtva | gdje je žrtva pogođena | `other` (napadač), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - i pogoci suigrača i svijeta |
| `shot` | strijelac | odakle je ispaljen pucanj | `weapon`, `place`, `detail` (igrin prikaz metaka) |
| `slash` | igrač | gdje je zamahnut nož | `weapon` = `Knife` |
| `grenade` | bacač | granata u letu, na uzorkovanju igrača i gdje je stala | `weapon` (granata), `entity` |
| `throw` | bacač | odakle je granata bačena | `weapon` (granata), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | bacač | gdje je eksplodirala | `weapon`, `throwerPlace` (mjesto bacača u tom trenutku); `place` ostaje prazan |
| `blind` | zaslijepljen igrač | gdje je stajao | `other` (bacač bljeska), `duration`, `weapon` = `Flashbang`, `entity`, `place` - i zaslijepljeni suigrači |
| `plant` | postavljač | gdje je postavio | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | deaktivator | gdje je deaktivirao | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | svaki igrač koji je odigrao rundu | gdje je igrač zadnji stajao | `won`, `earn_round_cs2` (što je runda isplatila: porast novca strane do sljedećeg freeze timea gdje pravila to dopuštaju, inače vlastita pravila igre), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | postavljač (s njegovim Steam ID-om), strana `T`, tim koji je postavljao | položaj postavljanja | `weapon` = `C4 Explosive`, `place` (postavljačevo pri postavljanju: gdje je bomba ležala); njegovo vrijeme je kad je bomba eksplodirala |
| `chat` | pošiljatelj | gdje je bio | `text` |
| svaki drugi događaj igre koji se tiče igrača, pod imenom igre: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | igrač | gdje je bio (događaji granate: gdje je bila granata) | `weapon` (predmeta), `entity`, `detail` (svako polje događaja) |

Što je unutra, a što nije:

- Redci **position** su živi igrači na strani, izvan freeze timea i zagrijavanja, svakih `--every` tikova (osam u sekundi zadano).
- Redci **kill** su samo ubojstva od strane neprijatelja - bez teamkilla, samoubojstva ili smrti od svijeta. Redci **death** su svaka smrt, uključujući te.
- Redci **explode** su svaka postavljena bomba koja je eksplodirala, prema `bomb_exploded` iz demo snimke: i u fazi nakon, kad su Ti već pobijedili eliminacijom. Demo bez tog događaja dobiva po jedan za svaku rundu koju je pobijedila bomba, na kraju runde.
- Redci **hurt** i **blind** su samo između neprijatelja.
- **shot** izostavlja noževe i C4; granate su redci **throw**.
- **molotov** pokriva molotove i zapaljive granate (početak vatre).
- Šteta suigrača, bljeskovi suigrača i gledatelja, događaji u freeze timeu i sve između rundi nisu u tablici.

Radni primjer, iz sintetičke demo snimke iz testova (dim bačen, prvo ubojstvo pogotkom u glavu, razmjene):

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

Bobovu smrt osvećuje benovo ubojstvo ace-a 1,9 s kasnije (redak `death` za boba: traded 1; benov redak `kill`: ubojstvo razmjenom, traded 1); drugi pogodak na boba bio je 137 štete na 40 zdravlja, pa se broji kao 40.

## Podnožje `heat3d`: savjeti {#the-heat3d-footer-hints}

Podnožje Parquet datoteke (metapodaci ključ/vrijednost sheme) nosi upute za čitanje pod ključem **`heat3d`**, JSON objektom:

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
| `version`, `kind` | verzija savjeta (1) i što ih je napisalo (`cs2-demo`) |
| `axes.up` | Z datoteke je gore |
| `axes.flipY` | negiraj Y datoteke (vidi dolje) |
| `axes.scale` | 1: pozicije se koriste kakve jesu, u jedinicama igre |
| `entity.size` | igrač je **32 jedinice** širok - širina CS2 igrača - veličina kojom reprodukcija kutije crta jednog |
| `columns.x` / `y` / `z` | stupci položaja |
| `columns.time`, `timeUnit` | `time`, u sekundama |
| `columns.personId` | igrač je osoba |
| `columns.teamId` | strana je grupa (pa T i CT, a ne nazivi timova, boje grupe) |
| `columns.sessionId` | svaka runda (`roundId`) je sesija |
| `columns.lookMode` i `dirX`-`dirZ` | smjer pogleda je vektor u tim stupcima |
| `columns.extra` | stupci koje treba zadržati kao filtre, po redu korisnosti |

Preglednik koji poznaje ključ otvara datoteku bez ičega za postaviti. Svi ostali ga ignoriraju. Da sami pročitate:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Osi i jedinice {#axes-and-units}

Koordinate su igrine vlastite: **inči** (jedna jedinica igre; igrač je 72 jedinice visok kad stoji i 32 široko), **Z gore**, i desnoruke.

Preglednik čiji je svijet Y prema gore mora crtati (x, y, z) igre kao **(x, z, -y)** - Z postaje visina, a Y se negira. To je rotacija, ne zrcaljenje. Crtano kao što se crta lijevoruki svijet Z-gore, kao (x, z, y), svaka karta ispadne zrcaljena, mjesto A na krivoj strani; `flipY: true` je ono što savjeti kažu da se spriječi. [Izvoz karte](map-export.md) piše svoju geometriju već u okviru (x, z, -y), u istim jedinicama, pa leži ispod tablice bez ikakvog podešavanja.

Udaljenosti u pregledniku označene su u metrima; uz mjerilo 1 to su jedinice igre. Pomnožite s 0,0254 za metre.

## Veličina {#size}

Pozicije dominiraju: otprilike deset igrača x 8 uzoraka u sekundi žive igre uz zadani `--every 8`, manje za mrtve igrače i freeze time. Prepolovljavanje `--every` udvostručuje ih; događaji nisu pogođeni.
