---
title: Tabelul hărții termice
nav_order: 8
lang: "ro"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Tabelul hărții termice (`<meci>.parquet`) {#the-heatmap-table-parquet}

Un fișier Parquet pentru fiecare meci: poziția fiecărui jucător în viață, eșantionată, și
fiecare eveniment în momentul în care s-a produs, câte un rând fiecare - un tabel lung pe
care vizualizatorul 3DHeat îl citește ca hartă termică, iar orice altceva îl citește ca tabel
obișnuit. Cod: [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(fișierul), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(rândurile; vezi [Cum se construiește un meci](building-matches.md)).

Fișierul este scris cu compresie Snappy, în grupuri de rânduri de câte 256.000 de rânduri.
Rândurile sunt sortate după `time`, apoi după `event`. Doar rândurile din interiorul unei
runde (de la sfârșitul timpului de îngheț al ei până la începutul următoarei runde) sunt în el.

Pe demo-ul sintetic din teste, rândurile de eveniment ale primei runde:

![rândurile de eveniment din tabel](../assets/img/table-rows.svg)

Într-un container `.3dheat`, tabelul este membrul cu rolul `table`
([Un fișier pentru fiecare meci](output-container.md)).

## Coloane {#columns}

Coloanele, mereu în această ordine. Coloanele de text sunt șiruri codificate prin dicționar
(`dictionary<int32, string>`) și nu sunt niciodată nule: „nicio valoare” înseamnă un șir gol.
Coloanele numerice sunt nule acolo unde un rând nu are o valoare.

| Coloană | Tip | Ce este |
|---|---|---|
| `match` | șir | numele meciului (`alpha-vs-bravo-m1`, sau `...-b` pentru un al doilea lanț) |
| `map` | șir | harta, din antetul demo-ului (`de_x`) |
| `round` | int16 | numărul rundei, de la 1 |
| `roundId` | șir | `<match> #NN`, numărul rundei în două cifre (`alpha-vs-bravo-m1 #07`): unic între meciuri, sesiunea vizualizatorului |
| `phase` | șir | `freeze` în timpul de îngheț al rundei (de la sfârșitul rundei precedente), `live` până când runda este decisă, `after` cât timp câștigătorii vânează și cei care pierd economisesc |
| `time` | float64 | secunde de la începutul meciului (începutul live al primului său fișier), pe un singur ceas peste fișierele sale |
| `roundTime` | float32 | secunde de la sfârșitul timpului de îngheț al acestei runde; negativ în timpul de îngheț |
| `event` | șir | ce este rândul - vezi [Evenimente](#events) |
| `player` | șir | numele jucătorului (pentru fiecare eveniment, care jucător este spus mai jos) |
| `steamid` | șir | ID-ul Steam al jucătorului (64 de biți, ca text) |
| `side` | șir | `T` sau `CT` în această rundă; gol când jucătorul nu era de nicio parte |
| `team` | șir | numele echipei jucătorului (sau `Started T` / `Started CT`); pentru `explode`, echipa care a plantat |
| `x`, `y`, `z` | float32 | poziția în coordonatele proprii ale jocului: inchi (unități de joc), **Z în sus**, sistem drept |
| `dirX`, `dirY`, `dirZ` | float32 | unde privește jucătorul, un vector unitar în același sistem; doar pentru poziții |
| `health` | int16 | 0-100; pentru poziții, iar la `hurt` ce a rămas după lovitură |
| `armor` | int16 | 0-100; pentru poziții, iar la `hurt` ce a rămas după lovitură |
| `money` | int32 | banii jucătorului; doar pentru poziții |
| `equipment` | int32 | valoarea a ceea ce duce jucătorul; doar pentru poziții |
| `weapon` | șir | arma așa cum o numește jocul (`AK-47`, `M4A1-S`, `Knife` pentru orice skin de cuțit) |
| `place` | șir | numele locului de pe hartă la poziția rândului (`BombsiteA`, `CTSpawn`); gol la detonările grenadelor: demo-ul nu numește niciun loc pentru unde a explodat o grenadă |
| `throwerPlace` | șir | numele locului aruncătorului când a explodat grenada; doar detonări de grenade |
| `other` | șir | celălalt jucător al unei eliminări, morți, lovituri sau orbiri |
| `damage` | float32 | sănătate pierdută; doar `hurt` |
| `duration` | float32 | secunde de orbire; doar `blind` |
| `headshot` | int8 | 0/1; doar `kill` și `death` |
| `opening` | int8 | 0/1, prima eliminare a unui inamic din rundă; doar `kill` și `death` |
| `traded` | int8 | 0/1. Pentru un `kill`: a fost o eliminare de răzbunare. Pentru un `death`: a fost răzbunată în 5 s. Doar `kill` și `death`. |
| `noscope` | int8 | 0/1, eliminarea s-a făcut cu o armă cu lunetă trasă fără lunetă (`noscope` al evenimentului); doar `kill` și `death` |
| `attackerBlind` | int8 | 0/1, ucigașul era orbit când a eliminat (`attackerblind` al evenimentului); doar `kill` și `death` |
| `won` | int8 | 0/1, dacă partea acestui rând a câștigat runda; nul când `side` este gol |
| `matchWon` | int8 | 0/1, dacă echipa acestui rând a câștigat meciul; nul când `team` este gol sau înregistrarea nu arată sfârșitul (vezi `winner` din documentul meciului) |
| `roundEndReason` | șir | cum s-a încheiat runda rândului: `elimination`, `bomb` (bomba a explodat), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | șir | cumpărarea părții acestui rând în această rundă: `pistol`, `eco`, `force`, `full` |
| `detail` | șir | fiecare câmp al evenimentului pe care nu-l duc celelalte coloane, ca obiect JSON (numele jocului): gloanțele unui foc (`fire_bullets`: origine, unghiuri, inexactitate, împrăștiere, indicele reculului, seed...), `dominated`, `revenge`, `attackerinair`, `wipe` ale unei morți..., `defindex` al unui obiect, nimic pentru un pas |
| `text` | șir | o linie de chat; doar `chat` |
| `entity` | int32 | entitatea grenadei: zborul unui `throw` (rânduri `grenade`), detonarea sa și jucătorii pe care i-a orbit o împart |
| `hitgroup` | șir | unde a lovit glonțul (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | armură pierdută; doar `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | unde pe corp a lovit glonțul, în sistemul de referință al victimei, în metri (x înainte, y în sus de la picioare, z la dreapta): raza focului (`fire_bullets`, altfel ochiul și privirea atacatorului) trasată până la un corp pozat ca victima stătea și s-a ghemuit, pe partea pe care o numește `hitgroup`; doar `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | direcția focului în același sistem; `hitMiss` cât de departe (m) a trecut raza pe lângă partea numită (0: prin ea); `hitFrom` `bullet` sau `aim` |
| `penetrated` | int16 | pereții prin care a trecut glonțul ucigaș; `kill` și `death` |
| `throughSmoke` | int8 | 0/1, ucis prin fum; `kill` și `death` |
| `distance` | float32 | distanța eliminării, cum o numără jocul (metri); `kill` și `death` |
| `assister` | șir | cine a asistat; `kill` și `death` |
| `flash`, `flashAlpha` | float32 | secunde de flash rămase și cât de alb; poziții |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; poziții |
| `zoom`, `duck`, `moveType` | | nivelul de zoom al lunetei, cât de ghemuit (0-1), tipul de mișcare al jocului; poziții |
| `spottedBy` | șir | ID-urile Steam ale inamicilor care văd acest jucător, separate prin `\|`; poziții |
| `inventory` | șir | tot ce duce jucătorul, separat prin `\|`; poziții |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | încărcătura și rezerva armei ținute; focurile din rafala curentă; poziții |
| `punchPitch`, `punchYaw` | float32 | lovitura de recul a țintei, în grade; poziții |
| `ping` | int16 | milisecunde; poziții |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | numărările tabelului de scor al jocului pentru meciul de până acum; poziții |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | banii cheltuiți în această rundă și în meci; valoarea echipamentului la începutul rundei; poziții |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, starea jucătorului la timpul rândului, evenimentele incluse: cască, kit de dezamorsare, orice armură, cu lunetă (de la ultimul eșantion de poziție al jucătorului până la rând), orbit (în interiorul unui `blind` care l-a lovit); fiecare rând care numește un jucător |
| `state_utility` | int16 | grenade purtate la timpul rândului (din `inventory`); fiecare rând care numește un jucător |
| `state_weapon` | șir | arma din mână la timpul rândului (la un `death`, a victimei, unde `weapon` este a ucigașului); fiecare rând care numește un jucător |
| `earn_round_cs2` | int16 | ce a plătit runda: la `round_end` recompensa de câștig sau bonusul de pierdere (cu bonusul părții care a plantat), la `plant` și `defuse` cei 300 ai jucătorului |

## Evenimente {#events}

Ce jucător numește un rând, unde se află și ce coloane completează.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won`, `roundEndReason` și `buy` sunt completate pe fiecare rând (`matchWon` acolo unde
se cunoaște câștigătorul meciului); `inventory`, `money`, `equipment` și coloanele `state_*`
pe fiecare rând care numește un jucător (evenimentele le iau de la ultimul eșantion de
poziție al jucătorului).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Completate și | 
|---|---|---|---|
| `position` | jucătorul | jucătorul (picioarele) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (ținută), `place`, și întreaga stare a jucătorului (coloanele de la `flash` încolo) - chiar și în timpul înghețului |
| `kill` | ucigașul | unde a stat ucigașul | `other` (victima), `weapon`, `headshot`, `opening`, `traded` (o eliminare de răzbunare), `noscope`, `attackerBlind`, `place` |
| `death` | victima | unde a căzut victima | `other` (ucigașul; gol pentru lume), `weapon`, `headshot`, `opening`, `traded` (răzbunată), `noscope`, `attackerBlind`, `place` |
| `hurt` | victima | unde a fost lovită victima | `other` (atacatorul), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - și loviturile coechipierilor și ale lumii |
| `shot` | trăgătorul | de unde a fost tras | `weapon`, `place`, `detail` (relatarea jocului despre gloanțe) |
| `slash` | jucătorul | unde a fost lovit cu cuțitul | `weapon` = `Knife` |
| `grenade` | aruncătorul | grenada în zbor, la eșantionarea jucătorilor și unde s-a oprit | `weapon` (grenada), `entity` |
| `throw` | aruncătorul | de unde a fost aruncată grenada | `weapon` (grenada), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | aruncătorul | unde a explodat | `weapon`, `throwerPlace` (locul aruncătorului în acel moment); `place` rămâne gol |
| `blind` | jucătorul orbit | unde stătea | `other` (cel care a aruncat flash-ul), `duration`, `weapon` = `Flashbang`, `entity`, `place` - și coechipierii orbiți |
| `plant` | plantatorul | unde a plantat | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | dezamorsatorul | unde a dezamorsat | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | fiecare jucător care a jucat runda | unde stătea ultima dată jucătorul | `won`, `earn_round_cs2` (ce i-a plătit runda: creșterea banilor părții până la următorul timp de îngheț, acolo unde regulile o permit, altfel ce spun regulile), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | plantatorul (cu ID-ul său Steam), partea `T`, echipa care a plantat | poziția plantării | `weapon` = `C4 Explosive`, `place` (al plantatorului la plantare: unde stătea bomba); timpul său este când a explodat bomba |
| `chat` | expeditorul | unde se afla | `text` |
| fiecare alt eveniment de joc despre un jucător, sub numele jocului: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | jucătorul | unde se afla (evenimentele unei grenade: unde era grenada) | `weapon` (al unui obiect), `entity`, `detail` (fiecare câmp al evenimentului) |

Ce este înăuntru și ce nu:

- Rândurile **position** sunt jucătorii în viață de pe o parte, în afara timpului de îngheț
  și a încălzirii, la fiecare `--every` tick-uri (opt pe secundă implicit).
- Rândurile **kill** sunt eliminări făcute doar de un inamic - fără teamkill, sinucidere sau
  moarte provocată de lume. Rândurile **death** sunt fiecare moarte, inclusiv acestea.
- Rândurile **explode** sunt fiecare bombă plantată care a explodat, după `bomb_exploded` al
  demo-ului: și în faza după, când Ts câștigaseră deja prin eliminare. Un demo fără acel
  eveniment primește câte unul pentru fiecare rundă câștigată de bombă, la sfârșitul rundei.
- Rândurile **hurt** și **blind** sunt doar între inamici.
- **shot** lasă afară cuțitele și C4; grenadele sunt rânduri **throw**.
- **molotov** acoperă molotovele și incendiarele (începutul focului).
- Daunele coechipierilor, flash-urile coechipierilor și ale spectatorilor, evenimentele din
  timpul înghețului și orice între runde nu sunt în tabel.

Un exemplu lucrat, din demo-ul sintetic din teste (un fum aruncat, o eliminare de deschidere
cu lovitură în cap, răzbunări):

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

Moartea lui bob este răzbunată de eliminarea lui ace de către ben, cu 1,9 s mai târziu (rândul
`death` al lui bob: traded 1; rândul `kill` al lui ben: o eliminare de răzbunare, traded 1);
a doua lovitură asupra lui bob a fost 137 de daune pe 40 de sănătate, deci numără 40.

## Sugestiile din subsolul `heat3d` {#the-heat3d-footer-hints}

Subsolul Parquet al fișierului (metadatele de schemă cheie/valoare) poartă instrucțiuni de
citire sub cheia **`heat3d`**, un obiect JSON:

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

| Intrare | Spune |
|---|---|
| `version`, `kind` | versiunea sugestiilor (1) și ce le-a scris (`cs2-demo`) |
| `axes.up` | Z al fișierului este în sus |
| `axes.flipY` | neagă Y-ul fișierului (vezi mai jos) |
| `axes.scale` | 1: pozițiile sunt folosite așa cum sunt, în unități de joc |
| `entity.size` | un jucător are **32 de unități** lățime - lățimea jucătorului CS2 - mărimea pe care o desenează un replay în cutie |
| `columns.x` / `y` / `z` | coloanele de poziție |
| `columns.time`, `timeUnit` | `time`, în secunde |
| `columns.personId` | jucătorul este persoana |
| `columns.teamId` | partea este grupul (deci T și CT, nu numele echipelor, colorează grupurile) |
| `columns.sessionId` | fiecare rundă (`roundId`) este o sesiune |
| `columns.lookMode` și `dirX`-`dirZ` | direcția privirii este un vector în acele coloane |
| `columns.extra` | coloanele de păstrat ca filtre, în ordinea utilității |

Un vizualizator care cunoaște cheia deschide fișierul fără să setezi nimic. Orice altceva
ignoră cheia. Ca să o citești singur:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Axe și unități {#axes-and-units}

Coordonatele sunt ale jocului: **inchi** (o unitate de joc; un jucător are 72 de unități
înalt când stă drept și 32 lățime), **Z în sus**, sistem drept.

Un vizualizator a cărui lume are Y în sus trebuie să deseneze (x, y, z) ale jocului ca
**(x, z, -y)** - Z devine înălțimea, iar Y este negat. Asta este o rotație, nu o oglindire.
Desenat ca într-o lume cu Z în sus și sistem stâng, adică (x, z, y), fiecare hartă iese
oglindită, cu site-ul A pe partea greșită; `flipY: true` este ceea ce spun sugestiile ca să
prevină asta. [Exportul hărții](map-export.md) scrie geometria deja în sistemul (x, z, -y), în
aceleași unități, deci se află sub tabel fără nicio ajustare.

Distanțele din vizualizator sunt etichetate în metri; cu scara 1 sunt unități de joc. Înmulțește
cu 0,0254 pentru metri.

## Dimensiune {#size}

Pozițiile domină: cam zece jucători x 8 eșantioane pe secundă de joc live, la `--every 8`
implicit, mai puțin pentru jucătorii morți și timpul de îngheț. Înjumătățirea lui `--every`
dublează pozițiile; evenimentele nu sunt afectate.
