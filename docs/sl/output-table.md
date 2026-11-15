---
title: "Toplotna tabela"
nav_order: 8
lang: "sl"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# Toplotna tabela (`<tekma>.parquet`) {#the-heatmap-table-matchparquet}

Ena datoteka Parquet na tekmo: položaj vsakega živega igralca, vzorčen, in vsak dogodek tam, kjer se je zgodil – ena
vrstica za vsakega; dolga tabela, ki jo pregledovalnik 3DHeat prebere kot toplotni zemljevid, vse drugo pa kot navadno
tabelo. Koda: [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(datoteka), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(vrstice; glejte [Gradnja tekme](building-matches.md)).

Datoteka je zapisana s stiskanjem Snappy v skupinah vrstic po 256.000 vrstic. Vrstice so urejene po `time`, nato po
`event`. V njej so samo vrstice znotraj runde (od konca zamrznitve runde do začetka naslednje runde).

Na sintetičnem demu iz testov, vrstice dogodkov prve runde:

![vrstice dogodkov v tabeli](../assets/img/table-rows.svg)

V vsebniku `.3dheat` je tabela člen z vlogo `table` ([Ena datoteka na tekmo](output-container.md)).

## Stolpci {#columns}

Stolpci, vedno v tem vrstnem redu. Besedilni stolpci so nizi s slovarskim kodiranjem (`dictionary<int32, string>`) in
nikoli niso prazni: »brez vrednosti« je prazen niz. Številski stolpci so prazni tam, kjer vrstica nima vrednosti.

| Stolpec | Tip | Kaj |
|---|---|---|
| `match` | niz | ime tekme (`alpha-vs-bravo-m1`, ali `...-b` za drugo verigo) |
| `map` | niz | karta iz glave dema (`de_x`) |
| `round` | int16 | številka runde, 1-indeksirana |
| `roundId` | niz | `<tekma> #NN`, številka runde z dvema števkama (`alpha-vs-bravo-m1 #07`): enolična čez vse tekme, seja pregledovalnika |
| `phase` | niz | `freeze` v času zamrznitve runde (od konca prejšnje runde), `live` do odločitve runde, `after`, medtem ko zmagovalci lovijo in poraženci varčujejo |
| `time` | float64 | sekunde od začetka tekme (živega začetka njene prve datoteke), na eni uri čez njene datoteke |
| `roundTime` | float32 | sekunde od konca zamrznitve te runde; negativno v času zamrznitve |
| `event` | niz | kaj vrstica je – glejte [Dogodki](#events) |
| `player` | niz | ime igralca (za vsak dogodek, kateri igralec je, je spodaj) |
| `steamid` | niz | Steam ID igralca (64-bitni, kot besedilo) |
| `side` | niz | `T` ali `CT` v tej rundi; prazno, kadar igralec ni bil na nobeni strani |
| `team` | niz | ime ekipe igralca (ali `Started T` / `Started CT`); za `explode` postavljajoča ekipa |
| `x`, `y`, `z` | float32 | položaj v lastnih koordinatah igre: palci (enote igre), **Z navzgor**, desnosučni |
| `dirX`, `dirY`, `dirZ` | float32 | kam igralec gleda, enotski vektor v istem okvirju; samo za položaje |
| `health` | int16 | 0–100; položaji, in pri `hurt` kar je ostalo po zadetku |
| `armor` | int16 | 0–100; položaji, in pri `hurt` kar je ostalo po zadetku |
| `money` | int32 | denar igralca; samo položaji |
| `equipment` | int32 | vrednost tega, kar igralec nosi; samo položaji |
| `weapon` | niz | orožje, kakor ga imenuje igra (`AK-47`, `M4A1-S`, `Knife` za vsak nož) |
| `place` | niz | ime kraja na karti na položaju vrstice (`BombsiteA`, `CTSpawn`); prazno pri detonacijah granat: demo ne navaja kraja, kjer je granata eksplodirala |
| `throwerPlace` | niz | ime kraja metalca, ko je granata eksplodirala; samo pri detonacijah granat |
| `other` | niz | drugi igralec ubijanja, smrti, zadetka ali oslepitve |
| `damage` | float32 | izgubljeno zdravje; samo `hurt` |
| `duration` | float32 | sekunde oslepljenosti; samo `blind` |
| `headshot` | int8 | 0/1; samo `kill` in `death` |
| `opening` | int8 | 0/1, prvi sovražnikov uboj v rundi; samo `kill` in `death` |
| `traded` | int8 | 0/1. Za `kill`: bil je maščevalni uboj. Za `death`: bila je maščevana v 5 s. Samo `kill` in `death`. |
| `noscope` | int8 | 0/1, ubijanje z optičnim orožjem, izstreljenim brez optike (dogodkov `noscope`); samo `kill` in `death` |
| `attackerBlind` | int8 | 0/1, ubijalec je bil oslepljen, ko je ubil (dogodkov `attackerblind`); samo `kill` in `death` |
| `won` | int8 | 0/1, ali je stran te vrstice zmagala v rundi; null, kadar je `side` prazen |
| `buy` | niz | nakup strani te vrstice v tej rundi: `pistol`, `eco`, `force`, `full` |
| `detail` | niz | vsako polje dogodka, ki ga drugi stolpci ne nosijo, kot objekt JSON (igrina lastna imena): streli krogel (`fire_bullets`: izhodišče, koti, netočnost, razpršitev, indeks odboja, seme ...), `dominated`, `revenge`, `attackerinair`, `wipe` ... pri smrti, `defindex` predmeta, pri koraku nič |
| `text` | niz | vrstica klepeta; samo `chat` |
| `entity` | int32 | entiteta granate: let `throw` (vrstice `grenade`), njena detonacija in igralci, ki jih je oslepila, si jo delijo |
| `hitgroup` | niz | kje je krogla zadela (`head`, `chest` ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | izgubljen oklep; samo `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | kje na telesu je krogla zadela, v okvirju žrtve v metrih (x naprej, y navzgor od tal, z desno): žarek strela (`fire_bullets`, sicer oko in pogled napadalca), sledenje do telesa, postavljenega kot je stala in počepnila žrtev, na del, ki ga navaja `hitgroup`; samo `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | smer strela v istem okvirju; `hitMiss` kako daleč (m) je žarek šel mimo imenovanega dela (0: skozi njega); `hitFrom` `bullet` ali `aim` |
| `penetrated` | int16 | stene, skozi katere je šla smrtonosna krogla; `kill` in `death` |
| `throughSmoke` | int8 | 0/1, ubit skozi dim; `kill` in `death` |
| `distance` | float32 | razdalja ubijanja, kakor jo šteje igra (metri); `kill` in `death` |
| `assister` | niz | kdo je asistiral; `kill` in `death` |
| `flash`, `flashAlpha` | float32 | sekunde preostale bliskovke, in kako bela je; položaji |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; položaji |
| `zoom`, `duck`, `moveType` | | stopnja povečave optike, kako globoko počepnjen (0–1), vrsta gibanja igre; položaji |
| `spottedBy` | niz | Steam ID-ji sovražnikov, ki vidijo tega igralca, ločeni z `\|`; položaji |
| `inventory` | niz | vse, kar igralec nosi, ločeno z `\|`; položaji |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | nabojnik in rezerva orožja v roki; streli v trenutnem rafalu; položaji |
| `punchPitch`, `punchYaw` | float32 | udarec odboja pri tarči, stopinje; položaji |
| `ping` | int16 | milisekunde; položaji |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | igrina lastna števila lestvice za tekmo do zdaj; položaji |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | denar, porabljen v tej rundi in v tekmi; vrednost opreme ob začetku runde; položaji |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, stanje igralca ob času vrstice, vključno z dogodki: čelada, komplet za deaktivacijo, kakršenkoli oklep, z optiko (od zadnjega vzorca položaja igralca do vrstice), oslepljen (znotraj `blind`, ki je zadel igralca); vsaka vrstica, ki navaja igralca |
| `state_utility` | int16 | pripomočki (granate), ki jih igralec nosi ob tem času (iz `inventory`); vsaka vrstica, ki navaja igralca |
| `state_weapon` | niz | orožje v roki ob tem času (pri `death` žrtvino lastno, kjer je `weapon` ubijalčevo); vsaka vrstica, ki navaja igralca |
| `earn_round_cs2` | int16 | koliko je runda plačala: pri `round_end` nagrada za zmago ali bonus za poraz (z bonusom postavljajoče strani), pri `plant` in `defuse` igralčevih 300 |

## Dogodki {#events}

Kateri igralec je v vrstici, kje stoji in katere stolpce izpolni.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won` in `buy` so izpolnjeni v vsaki
vrstici; `inventory`, `money`, `equipment` in stolpci `state_*` v vsaki vrstici, ki navaja igralca (dogodki jih
vzamejo iz zadnjega vzorca položaja igralca).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Prav tako izpolnjeno |
|---|---|---|---|
| `position` | igralec | igralec (stopala) | `dirX`–`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (v roki), `place` in celotno stanje igralca (stolpci od `flash` naprej) – tudi v času zamrznitve |
| `kill` | ubijalec | kjer je ubijalec stal | `other` (žrtev), `weapon`, `headshot`, `opening`, `traded` (maščevalni uboj), `noscope`, `attackerBlind`, `place` |
| `death` | žrtev | kjer je žrtev padla | `other` (ubijalec; prazno za svet), `weapon`, `headshot`, `opening`, `traded` (maščevano), `noscope`, `attackerBlind`, `place` |
| `hurt` | žrtev | kjer je bila žrtev zadeta | `other` (napadalec), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` – tudi zadetki soigralcev in sveta |
| `shot` | strelec | kjer je bil izstreljen strel | `weapon`, `place`, `detail` (igrin opis krogel) |
| `slash` | igralec | kjer je bil nož zamahnjen | `weapon` = `Knife` |
| `grenade` | metalec | granata v letu, pri vzorčenju igralcev in tam, kjer je obstala | `weapon` (granata), `entity` |
| `throw` | metalec | kjer je bila granata vržena | `weapon` (granata), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | metalec | kjer je eksplodirala | `weapon`, `throwerPlace` (kraj metalca ob tem času); `place` ostane prazen |
| `blind` | oslepljeni igralec | kjer je stal | `other` (bliskovalec), `duration`, `weapon` = `Flashbang`, `entity`, `place` – oslepljeni so tudi soigralci |
| `plant` | postavljalec | kjer je postavil | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | deaktivator | kjer je deaktiviral | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | vsak igralec, ki je odigral rundo | kjer je igralec nazadnje stal | `won`, `earn_round_cs2` (koliko mu je runda plačala: rast denarja strani do naslednjega časa zamrznitve, kadar pravila to dovolijo, sicer pravila sama), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | postavljalec (z njegovim Steam ID-jem), stran `T`, postavljajoča ekipa | položaj postavitve | `weapon` = `C4 Explosive`, `place` (postavljalčev ob postavitvi: kjer je bomba ležala); njegov čas je, ko je bomba eksplodirala |
| `chat` | pošiljatelj | kjer je bil | `text` |
| vsak drug dogodek igre o igralcu pod imenom igre: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | igralec | kjer je bil (dogodki granate: kjer je bila granata) | `weapon` (predmetov), `entity`, `detail` (vsako polje dogodka) |

Kaj je in česa ni:

- Vrstice **position** so živi igralci na strani, zunaj zamrznitve in ogrevanja, na vsakih `--every` taktov (privzeto
  osem na sekundo).
- Vrstice **kill** so samo uboji sovražnika – brez prijateljskih ubijanj, samomorov ali smrti zaradi sveta. Vrstice
  **death** so vsaka smrt, tudi te.
- Vrstice **explode** so vsaka postavljena bomba, ki je eksplodirala, po demovem `bomb_exploded`: tudi v fazi po koncu,
  kadar so T-ji že zmagali z izločitvijo. Demo brez tega dogodka dobi eno za vsako rundo, ki jo je dobila bomba, ob
  koncu runde.
- Vrstice **hurt** in **blind** so samo med sovražniki.
- **shot** izpusti nože in C4; granate so vrstice **throw**.
- **molotov** zajema molotovke in zažigalne bombe (začetek ognja).
- Škoda soigralcev, bliskovke soigralcev in gledalcev, dogodki med zamrznitvijo in vse med rundami niso v tabeli.

Delovni primer, iz sintetičnega demoja iz testov (vržen dim, prvi uboj z zadetkom v glavo, maščevanja):

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

bobova smrt je maščevana z benovim ubijanjem ace 1,9 s pozneje (bobova vrstica `death`: traded 1; benova vrstica `kill`:
maščevalni uboj, traded 1); drugi zadetek na boba je bil 137 škode na 40 zdravja, zato šteje 40.

## Namigi v nogi `heat3d` {#the-heat3d-footer-hints}

Noga datoteke Parquet (metapodatki sheme ključ/vrednost) nosi navodila za branje pod ključem **`heat3d`**, objekt JSON:

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

| Vnos | Pove |
|---|---|
| `version`, `kind` | različica namigov (1) in kaj jih je zapisalo (`cs2-demo`) |
| `axes.up` | Z datoteke je navzgor |
| `axes.flipY` | negiraj Y datoteke (glejte spodaj) |
| `axes.scale` | 1: položaji se uporabijo, kakršni so, v enotah igre |
| `entity.size` | igralec je širok **32 enot** – širina igralca CS2 – velikost, s katero škatlasta predvajanja narišejo igralca |
| `columns.x` / `y` / `z` | stolpci položajev |
| `columns.time`, `timeUnit` | `time`, v sekundah |
| `columns.personId` | igralec je oseba |
| `columns.teamId` | stran je skupina (torej T in CT, ne imena ekip, barvata skupine) |
| `columns.sessionId` | vsaka runda (`roundId`) je seja |
| `columns.lookMode` in `dirX`–`dirZ` | smer pogleda je vektor v teh stolpcih |
| `columns.extra` | stolpci, ki jih ohranimo kot filtre, po koristnosti |

Pregledovalnik, ki ključ pozna, odpre datoteko brez kakršnih koli nastavitev. Vse drugo ga prezre. Da ga preberete sam:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Osi in enote {#axes-and-units}

Koordinate so igrine lastne: **palci** (ena enota igre; igralec je stoje visok 72 enot in širok 32), **Z navzgor**,
desnosučne.

Pregledovalnik s svetom, kjer je Y navzgor, mora igrin (x, y, z) narisati kot **(x, z, -y)** – Z postane višina, Y je
negiran. To je rotacija, ne zrcaljenje. Narisano kot svet z Z navzgor in levosučnostjo, torej (x, z, y), vsaka karta
pride zrcaljena, mesto A na napačni strani; `flipY: true` je tisto, kar namigi naročijo, da se to prepreči. [Izvoz
karte](map-export.md) zapiše geometrijo že v okvirju (x, z, -y), v istih enotah, zato leži pod tabelo brez kakršnega
koli prilagajanja.

Razdalje v pregledovalniku so označene v metrih; pri merilu 1 so enote igre. Za metre pomnoži z 0,0254.

## Velikost {#size}

Položaji prevladujejo: približno deset igralcev krat 8 vzorcev na sekundo žive igre pri privzetem `--every 8`, manj za
mrtve igralce in čas zamrznitve. Razpolovitev `--every` podvoji njih; dogodki so nespremenjeni.
