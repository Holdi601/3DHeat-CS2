---
title: "Statistiken"
nav_order: 7
lang: de
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistiken {#statistics}

Was jeder Spieler in einem Match getan hat und wie jede Runde verlief: das Scoreboard und die Rundenliste des
[Match-Dokuments](output-match-json.md). Code:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Alles wird aus dem Match gezählt, so wie es unter [Ein Match aufbauen](building-matches.md) gebaut wird: seine
Kill-Datensätze, sein Schaden (verlorene Gesundheit, nur Gegner), seine Blendungen (nur Gegner) und seine Zeilen.

![das Text-Scoreboard eines synthetischen Matches](../assets/img/scoreboard.svg)

## Die Konventionen {#the-conventions}

Wo das Spiel selbst eine Zahl nicht definiert, gelten diese Definitionen. Sie stehen auch in jedem Match-Dokument
unter `conventions`.

| Begriff | Definition |
|---|---|
| **Trade** | Ein Tod ist *getradet*, wenn sein Killer innerhalb von **5 s** von einem Teamkameraden des Opfers getötet wird; dieser Kill ist ein *Trade-Kill*. |
| **Opening** | Der erste Kill eines Gegners in der Runde, solange sie live ist. Ein Teamkill, ein Suizid oder ein Tod durch die Welt davor wird übergangen. |
| **KAST** | Der Anteil der Runden, in denen ein Spieler einen **K**ill hatte, einen **A**ssist (ein Flash-Assist zählt), **S**urvived (überlebte) oder **T**raded (getradet wurde). |
| **Schaden** | Die tatsächlich verlorene Gesundheit, nur Gegner: ein Kopftreffer mit 137 Schaden auf einen Spieler mit 40 Gesundheit ist 40. |
| **Clutch** | Der letzte lebende Spieler einer Seite, wenn noch Gegner stehen; gewonnen, wenn seine Seite die Runde gewinnt. |
| **Buy** | Pro Seite, aus dem durchschnittlichen Ausrüstungswert am Ende der Freeze-Zeit: die erste Runde jeder regulären Hälfte ist eine Pistolenrunde (Runde 1 und die Runde nach der Hälfte, solange das Match sie gespielt hat); die Verlängerung hat keine; darüber hinaus unter 1.500 $ Eco, unter 4.000 $ Force, sonst Full. |

## Wer jede Runde begonnen hat {#who-started-each-round}

Mehrere Zahlen müssen wissen, wer eine Runde gespielt hat. Die **Startspieler** einer Runde sind, pro Seite, jeder
Spieler mit einer lebenden Positionszeile innerhalb einer Sekunde nach der frühesten Position dieser Runde (also in der
ersten Sekunde nach dem Ende der Freeze-Zeit). Die **gespielten Runden** eines Spielers ist die Anzahl der Runden, die
er begonnen hat. Hat ein Spieler keine begonnen (er hatte nie eine solche Zeile), wird stattdessen die Rundenzahl des
Matches genommen, damit nicht durch null geteilt wird.

## Die Scoreboard-Zeile {#the-scoreboard-line}

Ein Eintrag pro Spieler (die Feldnamen stehen im [Match-Dokument](output-match-json.md#players)). „Gegner-Kill“ meint
unten einen Kill mit Angreifer, der weder Teamkill noch Suizid (des Opfers selbst) ist.

| Feld | Zählt |
|---|---|
| `kills` | Gegner-Kills, aus der Live- und der After-Phase |
| `deaths` | jeder Tod: durch Gegner, Teamkameraden, sich selbst oder die Welt |
| `assists` | Gegner-Kills, die dieser Spieler ohne Blendung assistiert hat (der Assistierende darf nicht der Killer sein) |
| `flashAssists` | Gegner-Kills, die dieser Spieler mit einer Blendung assistiert hat |
| `diff` | Kills - Tode |
| `adr` | Schaden (verlorene Gesundheit, nur Gegner, beide Phasen) / gespielte Runden, eine Nachkommastelle |
| `kast` | 100 x (Runden mit einem Kill, einem Assist oder Flash-Assist, Überleben oder einem getradeten Tod) / gespielte Runden, eine Nachkommastelle. *Überleben* heißt: ein Startspieler der Runde, der in ihr nicht starb, in welcher Phase auch immer. |
| `headshotPct` | 100 x Kopftreffer-Kills / Kills, eine Nachkommastelle; 0 ohne Kills |
| `openingKills`, `openingDeaths` | gewonnene und verlorene Opening-Duelle |
| `tradeKills` | Kills, die den Tod eines Teamkameraden gerächt haben |
| `tradedDeaths` | Tode, die getradet wurden |
| `multiKills` | Runden mit 2, 3, 4 und 5 Gegner-Kills (`2k`, `3k`, `4k`, `5k`); mehr als fünf zählt als `5k`. Beide Phasen zählen. |
| `clutches`, `clutchesWon` | gespielte und gewonnene Clutches (unten) |
| `utilityDamage` | Schaden mit HE-Granaten, Molotows und Brandgranaten, eine Nachkommastelle |
| `enemiesFlashed` | Gegner, die durch Blendungen dieses Spielers mindestens **1,0 s** geblendet wurden |
| `plants`, `defuses` | Bombenlegungen und Entschärfungen (Zeilen der Tabelle) |
| `teamkills` | getötete Teamkameraden. Ein Suizid - Angreifer und Opfer derselbe Spieler, etwa durch eine eigene Granate - zählt nicht: er ist nur ein Tod. |
| `roundsPlayed` | begonnene Runden, wie oben |

Spieler sind nach Teamname aufgelistet (alphabetisch), und innerhalb eines Teams nach `diff`, dann nach `kills`, die
besten zuerst.

Hinweise zu den Rändern:

- Ein Kill in der After-Phase - die Gewinner, die einen sparenden Spieler jagen - zählt als Kill, als Tod, für ADR,
  Multi-Kills und KAST wie jeder andere.
- Wallbangs werden intern pro Spieler gezählt, aber nicht ins Match-Dokument geschrieben; jeder Kill in der
  Rundenliste sagt, ob es einer war.
- Der Trade-Teil von KAST wird dem Opfer eines getradeten Todes in dieser Runde gutgeschrieben.
- Teamkills und Suizide fügen dem Opfer einen Tod, aber niemandem einen Kill hinzu; ein Teamkill fügt dem Killer
  etwas zu `teamkills` hinzu, ein Suizid nichts anderem.

## Clutches {#clutches}

Für jede Runde gelten die Startspieler beider Seiten als lebend, und die Live-Kills der Runde werden in Reihenfolge
durchlaufen. Nach jedem Tod wird das Opfer entfernt, und jede Seite wird angesehen: Eine Seite mit genau **einem**
verbliebenen Spieler und mindestens einem noch lebenden Gegner ist ein Clutch für diesen Spieler **gegen** die Anzahl
der Gegner, die in diesem Moment leben. Jeder Spieler hat höchstens einen Clutch pro Runde; er ist **gewonnen**, wenn
die Seite dieses Spielers die Runde gewinnt.

Folgen dieser Definition:

- Beide Seiten können in einer Runde einen Clutch haben. Ist eine Seite zuerst auf einen reduziert (etwa ein 1 gegen 3)
  und wird dann auch die andere Seite auf einen gebracht, ist der zweite Spieler in einem eigenen 1-gegen-1-Clutch.
- `against` ist die Zahl, als der Spieler der letzte wurde, nicht die am Ende.
- Kills der After-Phase werden nicht durchlaufen; sie beginnen keinen Clutch und ändern keinen.

## Überlebende {#survivors}

Die **Überlebenden** einer Runde sind pro Seite ihre Startspieler, abzüglich aller, die während des Live-Teils starben.
Ein Spieler, der in der After-Phase beim Sparen getötet wurde, ist in der Rundenliste noch ein Überlebender - hat aber
für KAST nicht *überlebt*.

## Die Rundenliste {#the-round-list}

Jede Runde des Match-Dokuments trägt ihr Ergebnis, Stand, Seiten, Wirtschaft, Bombenlegung, Überlebende, Clutches und
ihre Kills in Reihenfolge; siehe [Das Match-Dokument](output-match-json.md#rounds).

## Das Text-Scoreboard {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` gibt diese Zahlen pro Team aus; siehe
[Befehle](commands.md#scoreboard---a-match-as-text).
