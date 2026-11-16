---
title: "Die Heatmap-Tabelle"
nav_order: 8
lang: "de"
source: output-table.md
source_hash: "7f6d90bac0d2"
nav_exclude: true
search_exclude: true
---
# Die Heatmap-Tabelle (`<match>.parquet`) {#the-heatmap-table-parquet}

Eine Parquet-Datei pro Match: die Position jedes lebenden Spielers, abgetastet, und jedes Ereignis an seinem Ort,
jeweils eine Zeile - eine lange Tabelle, die der 3DHeat-Viewer als Heatmap liest, und jedes andere Programm als
gewöhnliche Tabelle. Code:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(die Datei), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(die Zeilen; siehe [Ein Match aufbauen](building-matches.md)).

Die Datei wird mit Snappy-Kompression in Zeilengruppen zu je 256.000 Zeilen geschrieben. Die Zeilen sind nach
`time` sortiert, dann nach `event`. Nur Zeilen innerhalb einer Runde (vom Ende ihrer Freeze-Zeit bis zum Beginn
der nächsten Runde) stehen darin.

Beim synthetischen Demo der Tests die Ereigniszeilen der ersten Runde:

![Ereigniszeilen der Tabelle](../assets/img/table-rows.svg)

In einem `.3dheat`-Container ist die Tabelle das Element mit der Rolle `table`
([Eine Datei pro Match](output-container.md)).

## Spalten {#columns}

Die Spalten, immer in dieser Reihenfolge. Textspalten sind wörterbuchkodierte Strings
(`dictionary<int32, string>`) und nie leer: „kein Wert“ ist ein leerer String. Numerische Spalten sind null, wo eine
Zeile keinen Wert hat.

| Spalte | Typ | Was |
|---|---|---|
| `match` | string | der Match-Name (`alpha-vs-bravo-m1`, oder `...-b` für eine zweite Kette) |
| `map` | string | die Karte aus dem Demo-Header (`de_x`) |
| `round` | int16 | die Rundennummer, ab 1 |
| `roundId` | string | `<match> #NN`, die Rundennummer zweistellig (`alpha-vs-bravo-m1 #07`): über alle Matches eindeutig, die Session des Viewers |
| `phase` | string | `freeze` in der Freeze-Zeit der Runde (ab dem Ende der vorigen Runde), `live`, bis die Runde entschieden ist, `after`, während die Gewinner jagen und die Verlierer sparen |
| `time` | float64 | Sekunden seit dem Start des Matches (dem Live-Start seiner ersten Datei), auf einer gemeinsamen Uhr über alle seine Dateien |
| `roundTime` | float32 | Sekunden seit dem Ende der Freeze-Zeit dieser Runde; negativ in der Freeze-Zeit |
| `event` | string | was die Zeile ist - siehe [Ereignisse](#events) |
| `player` | string | der Name des Spielers (für jedes Ereignis, welcher Spieler gemeint ist, steht unten) |
| `steamid` | string | die Steam-ID des Spielers (64-bit, als Text) |
| `side` | string | `T` oder `CT` in dieser Runde; leer, wenn der Spieler auf keiner Seite war |
| `team` | string | der Teamname des Spielers (oder `Started T` / `Started CT`); bei `explode` das Team, das die Bombe legte |
| `x`, `y`, `z` | float32 | Position in den eigenen Koordinaten des Spiels: Zoll (Spieleinheiten), **Z nach oben**, rechtshändig |
| `dirX`, `dirY`, `dirZ` | float32 | wohin der Spieler schaut, ein Einheitsvektor im selben Koordinatensystem; nur bei Positionen |
| `health` | int16 | 0-100; bei Positionen, und bei `hurt` das, was nach dem Treffer übrig war |
| `armor` | int16 | 0-100; bei Positionen, und bei `hurt` das, was nach dem Treffer übrig war |
| `money` | int32 | das Geld des Spielers; nur bei Positionen |
| `equipment` | int32 | der Wert dessen, was der Spieler trägt; nur bei Positionen |
| `weapon` | string | die Waffe, so wie das Spiel sie benennt (`AK-47`, `M4A1-S`, `Knife` für jeden Messer-Skin) |
| `place` | string | der eigene Ortsname der Karte an der Position der Zeile (`BombsiteA`, `CTSpawn`); leer bei Granaten-Detonationen: das Demo nennt keinen Ort dafür, wo eine Granate detonierte |
| `throwerPlace` | string | der Ortsname des Werfers, als die Granate detonierte; nur bei Granaten-Detonationen |
| `other` | string | der andere Spieler eines Kills, Todes, Treffers oder einer Blendung |
| `damage` | float32 | verlorene Gesundheit; nur `hurt` |
| `duration` | float32 | Sekunden Blendung; nur `blind` |
| `headshot` | int8 | 0/1; nur `kill` und `death` |
| `opening` | int8 | 0/1, der erste Kill eines Gegners in der Runde; nur `kill` und `death` |
| `traded` | int8 | 0/1. Bei einem `kill`: es war ein Trade-Kill. Bei einem `death`: er wurde innerhalb von 5 s gerächt. Nur `kill` und `death`. |
| `noscope` | int8 | 0/1, der Kill geschah mit einer Zielfernrohr-Waffe, die ohne Zielfernrohr schoss (das `noscope` des Ereignisses); nur `kill` und `death` |
| `attackerBlind` | int8 | 0/1, der Killer war geblendet, als er tötete (das `attackerblind` des Ereignisses); nur `kill` und `death` |
| `won` | int8 | 0/1, ob die Seite dieser Zeile die Runde gewonnen hat; null, wenn `side` leer ist |
| `matchWon` | int8 | 0/1, ob das Team dieser Zeile das Match gewonnen hat; null, wenn `team` leer ist oder die Aufnahme das Ende nicht zeigt (siehe `winner` im Match-Dokument) |
| `roundEndReason` | string | wie die Runde der Zeile endete: `elimination`, `bomb` (die Bombe explodierte), `defuse`, `time`, `surrender`, `draw`, `other` |
| `buy` | string | der Buy der Seite dieser Zeile in dieser Runde: `pistol`, `eco`, `force`, `full` |
| `detail` | string | jedes Feld des Ereignisses, das die anderen Spalten nicht tragen, als JSON-Objekt (die eigenen Namen des Spiels): die Kugeln eines Schusses (`fire_bullets`: Ursprung, Winkel, Ungenauigkeit, Streuung, Rückstoß-Index, Seed ...), `dominated`, `revenge`, `attackerinair`, `wipe` ... eines Todes, `defindex` eines Items; ein Schritt hat nichts |
| `text` | string | eine Chatzeile; nur `chat` |
| `entity` | int32 | die Entity der Granate: der Flug eines `throw` (`grenade`-Zeilen), seine Detonation und die Spieler, die sie blendete, teilen sie |
| `hitgroup` | string | wohin die Kugel traf (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | verlorene Rüstung; nur `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | wohin am Körper die Kugel traf, im Koordinatensystem des Opfers in Metern (x nach vorn, y von den Füßen nach oben, z nach rechts): der Strahl des Schusses (`fire_bullets`, sonst Auge und Blickrichtung des Angreifers), verfolgt bis zu einem Körper in der Haltung, die das Opfer stehend und geduckt hatte, auf den Teil, den `hitgroup` nennt; nur `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | die Richtung des Schusses im selben Koordinatensystem; `hitMiss` wie weit (m) der Strahl am genannten Teil vorbeiging (0: durch ihn hindurch); `hitFrom` `bullet` oder `aim` |
| `penetrated` | int16 | Wände, durch die die tödliche Kugel ging; `kill` und `death` |
| `throughSmoke` | int8 | 0/1, getötet durch Rauch; `kill` und `death` |
| `distance` | float32 | die Entfernung des Kills, wie das Spiel sie zählt (Meter); `kill` und `death` |
| `assister` | string | wer assistierte; `kill` und `death` |
| `flash`, `flashAlpha` | float32 | Sekunden Blendung, die noch übrig sind, und wie weiß sie ist; Positionen |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; Positionen |
| `zoom`, `duck`, `moveType` | | die Zoomstufe des Zielfernrohrs, wie tief geduckt (0-1), der Bewegungstyp des Spiels; Positionen |
| `spottedBy` | string | die Steam-IDs der Gegner, die diesen Spieler sehen, durch `\|` getrennt; Positionen |
| `inventory` | string | alles, was der Spieler trägt, durch `\|` getrennt; Positionen |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | Magazin und Reserve der gehaltenen Waffe; Schüsse im aktuellen Feuerstoß; Positionen |
| `punchPitch`, `punchYaw` | float32 | der Aim-Punch des Rückstoßes, in Grad; Positionen |
| `ping` | int16 | Millisekunden; Positionen |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | die eigenen Scoreboard-Zahlen des Spiels für das Match bis dahin; Positionen |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | Geld, das in dieser Runde und im ganzen Match ausgegeben wurde; Ausrüstungswert, als die Runde begann; Positionen |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, der Zustand des Spielers zur Zeit der Zeile, Ereignisse eingeschlossen: Helm, Entschärfer-Kit, irgendeine Rüstung, Zielfernrohr (von der letzten Positionsabtastung des Spielers bis zur Zeile), geblendet (innerhalb eines `blind`, das ihn traf); jede Zeile, die einen Spieler nennt |
| `state_utility` | int16 | Granaten, die zur Zeit getragen werden (aus `inventory`); jede Zeile, die einen Spieler nennt |
| `state_weapon` | string | die Waffe in der Hand zur Zeit (bei einem `death` die des Opfers, wo `weapon` die des Killers ist); jede Zeile, die einen Spieler nennt |
| `earn_round_cs2` | int16 | was die Runde zahlte: bei `round_end` die Siegprämie oder der Verlustbonus (mit dem Bonus der Seite, die die Bombe legte), bei `plant` und `defuse` die 300 des Spielers |

## Ereignisse {#events}

Welchen Spieler eine Zeile nennt, wo er steht und welche Spalten sie füllt. `match`, `map`, `round`, `roundId`,
`phase`, `time`, `roundTime`, `event`, `won`, `roundEndReason` und `buy` sind in jeder Zeile gefüllt (`matchWon`, wo der
Gewinner des Matches bekannt ist); `inventory`, `money`,
`equipment` und die `state_*`-Spalten in jeder Zeile, die einen Spieler nennt (Ereignisse nehmen sie von der letzten
Positionsabtastung des Spielers).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Außerdem gefüllt |
|---|---|---|---|
| `position` | der Spieler | der Spieler (Füße) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (gehalten), `place`, und der ganze Zustand des Spielers (die Spalten ab `flash`) - auch in der Freeze-Zeit |
| `kill` | der Killer | wo der Killer stand | `other` (Opfer), `weapon`, `headshot`, `opening`, `traded` (ein Trade-Kill), `noscope`, `attackerBlind`, `place` |
| `death` | das Opfer | wo das Opfer fiel | `other` (Killer; leer bei der Welt), `weapon`, `headshot`, `opening`, `traded` (gerächt), `noscope`, `attackerBlind`, `place` |
| `hurt` | das Opfer | wo das Opfer getroffen wurde | `other` (Angreifer), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - auch die Treffer von Teamkameraden und der Welt |
| `shot` | der Schütze | wo der Schuss abgefeuert wurde | `weapon`, `place`, `detail` (die Darstellung der Kugeln durch das Spiel) |
| `slash` | der Spieler | wo mit dem Messer geschlagen wurde | `weapon` = `Knife` |
| `grenade` | der Werfer | die Granate im Flug, bei der Abtastung der Spieler und dort, wo sie stehen blieb | `weapon` (die Granate), `entity` |
| `throw` | der Werfer | wo die Granate geworfen wurde | `weapon` (die Granate), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | der Werfer | wo sie detonierte | `weapon`, `throwerPlace` (der Ort des Werfers in diesem Moment); `place` bleibt leer |
| `blind` | der geblendete Spieler | wo er stand | `other` (der Blender), `duration`, `weapon` = `Flashbang`, `entity`, `place` - auch geblendete Teamkameraden |
| `plant` | der Leger | wo er legte | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | der Entschärfer | wo er entschärfte | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | jeder Spieler, der die Runde spielte | wo der Spieler zuletzt stand | `won`, `earn_round_cs2` (was die Runde ihm zahlte: der Anstieg des Geldes der Seite bis zur nächsten Freeze-Zeit, wo die Regeln es erlauben, sonst die eigenen Regeln), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | der Leger (mit seiner Steam-ID), Seite `T`, das Team, das die Bombe legte | die Position der Legung | `weapon` = `C4 Explosive`, `place` (der des Legers bei der Legung: wo die Bombe lag); seine Zeit ist, wann die Bombe explodierte |
| `chat` | der Absender | wo er war | `text` |
| jedes andere Spielereignis über einen Spieler, unter dem Namen des Spiels: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | der Spieler | wo er war (bei Granatenereignissen: wo die Granate war) | `weapon` (eines Items), `entity`, `detail` (jedes Feld des Ereignisses) |

Was drin ist und was nicht:

- **position**-Zeilen sind lebende Spieler auf einer Seite, außerhalb der Freeze-Zeit und des Warmups, alle
  `--every` Ticks (standardmäßig acht pro Sekunde).
- **kill**-Zeilen sind nur Kills durch einen Gegner - kein Teamkill, Suizid oder Tod durch die Welt. **death**-Zeilen
  sind jeder Tod, diese eingeschlossen.
- **explode**-Zeilen sind jede gelegte Bombe, die explodierte, nach dem `bomb_exploded` des Demos: auch in der
  After-Phase, wenn die Ts bereits durch Eliminierung gewonnen hatten. Ein Demo ohne dieses Ereignis bekommt eine für
  jede durch die Bombe gewonnene Runde, am Ende der Runde.
- **hurt**- und **blind**-Zeilen sind nur zwischen Gegnern.
- **shot** lässt Messer und das C4 weg; Granaten sind **throw**-Zeilen.
- **molotov** umfasst Molotows und Brandgranaten (der beginnende Brand).
- Schaden von Teamkameraden, Blendungen von Teamkameraden und Zuschauern, Ereignisse der Freeze-Zeit und alles
  zwischen den Runden stehen nicht in der Tabelle.

Ein durchgerechnetes Beispiel, aus dem synthetischen Demo der Tests (eine geworfene Rauchgranate, ein Kopftreffer-Opening-Kill, Trades):

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

bobs Tod wird durch Bens Kill an ace 1,9 s später gerächt (bobs `death`-Zeile: traded 1; Bens `kill`-Zeile: ein
Trade-Kill, traded 1); der zweite Treffer auf bob waren 137 Schaden bei 40 Gesundheit, also zählt er 40.

## Die `heat3d`-Hinweise im Footer {#the-heat3d-footer-hints}

Der Parquet-Footer der Datei (Schema-Metadaten) trägt Leseanweisungen unter dem Schlüssel **`heat3d`**, ein JSON-Objekt:

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

| Eintrag | Sagt |
|---|---|
| `version`, `kind` | die Version der Hinweise (1) und was sie geschrieben hat (`cs2-demo`) |
| `axes.up` | das Z der Datei zeigt nach oben |
| `axes.flipY` | das Y der Datei negieren (siehe unten) |
| `axes.scale` | 1: Positionen werden so benutzt, wie sie sind, in Spieleinheiten |
| `entity.size` | ein Spieler ist **32 Einheiten** breit - die Breite eines CS2-Spielers - die Größe, mit der eine Box-Wiedergabe ihn zeichnet |
| `columns.x` / `y` / `z` | die Positionsspalten |
| `columns.time`, `timeUnit` | `time`, in Sekunden |
| `columns.personId` | der Spieler ist die Person |
| `columns.teamId` | die Seite ist die Gruppe (so färben T und CT die Gruppen, nicht die Teamnamen) |
| `columns.sessionId` | jede Runde (`roundId`) ist eine Session |
| `columns.lookMode` und `dirX`-`dirZ` | die Blickrichtung ist ein Vektor in diesen Spalten |
| `columns.extra` | die Spalten, die als Filter bleiben, nach Nützlichkeit geordnet |

Ein Viewer, der den Schlüssel kennt, öffnet die Datei ohne etwas einzustellen. Alles andere ignoriert ihn. Um ihn
selbst zu lesen:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Achsen und Einheiten {#axes-and-units}

Die Koordinaten sind die eigenen des Spiels: **Zoll** (eine Spieleinheit; ein Spieler ist 72 Einheiten hoch im
Stehen und 32 breit), **Z nach oben**, rechtshändig.

Ein Viewer, dessen Welt Y nach oben hat, muss die (x, y, z) des Spiels als **(x, z, -y)** zeichnen - Z wird zur Höhe,
und Y wird negiert. Das ist eine Drehung, keine Spiegelung. Zeichnet man es so, wie eine linkshändige Welt mit Z nach
oben es zeichnet, als (x, z, y), kommt jede Karte gespiegelt heraus, die A-Site auf der falschen Seite; `flipY: true`
ist das, was die Hinweise verlangen, um das zu verhindern. Der [Karten-Export](map-export.md) schreibt seine Geometrie
bereits im Koordinatensystem (x, z, -y), in denselben Einheiten, sodass sie ohne Anpassung unter der Tabelle liegt.

Entfernungen im Viewer sind in Metern beschriftet; bei einem Maßstab von 1 sind es Spieleinheiten. Mit 0,0254
multiplizieren für Meter.

## Größe {#size}

Die Positionen bestimmen die Größe: etwa zehn Spieler mal 8 Abtastungen pro Sekunde lebendes Spiel bei der
Standardeinstellung `--every 8`, weniger für tote Spieler und die Freeze-Zeit. Das Halbieren von `--every` verdoppelt
sie; Ereignisse bleiben unberührt.
