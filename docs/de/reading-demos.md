---
title: "Ein Demo lesen"
nav_order: 5
lang: "de"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Ein Demo lesen {#reading-a-demo}

Was aus einer `.dem`-Datei herausgeholt wird, bevor irgendetwas gedeutet wird. Code:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Ein CS2-Demo ist die eigene Aufzeichnung des Servers (SourceTV): jeder Spieler, jeder Tick, 64 Ticks pro Sekunde
(`TICKRATE = 64`). Es wird mit [demoparser2](https://github.com/LaihoE/demoparser) in drei Aufrufen gelesen, und das
Ergebnis wird so behalten, wie es kommt, in einem `RawPart`:

| Feld | Enthält |
|---|---|
| `path` | die Datei |
| `map` | `map_name` aus dem Demo-Header (`de_x`); leer, wenn der Header keinen hat |
| `samples` | eine Zeile pro Spieler und abgetastetem Tick: die Spieler- und Regelfelder unten, dazu `tick`, `steamid`, `name` |
| `events` | Ereignisname -> seine Zeilen, mit den Feldern der Spieler als `user_`, `attacker_`, `assister_` vorangestellt, so wie der Parser sie benennt |

Nichts in `demo.py` entscheidet, was eine Runde ist oder wer sie gewonnen hat; das ist
[Ein Match aufbauen](building-matches.md).

## Die abgetasteten Ticks {#the-sampled-ticks}

`parse_ticks` wird nach den Ticks `0, N, 2N, ...` bis 4.000.000 gefragt (`LAST_TICK`, weit über jedes Match hinaus -
17 Stunden bei 64 Ticks pro Sekunde), wobei *N* der Wert von `--every` ist (Standard 8). Der Parser hält am Ende des
Demos an. Jeder Spieler, der bei einem abgetasteten Tick anwesend ist, ergibt eine Zeile, ob lebend, tot, zuschauend
oder als Coach; das Filtern geschieht später.

Der Abtastschritt ist mehr als die Dichte der Heatmap wichtig: Der Moment, in dem eine Runde entschieden ist, wird aus
diesen Abtastungen gelesen (siehe [Ein Match aufbauen](building-matches.md#rounds)), daher sind Rundenendzeiten auf
einen Schritt genau (standardmäßig 1/8 s).

### Spielerfelder {#player-fields}

| Eigenschaft | Wird zu |
|---|---|
| `X`, `Y`, `Z` | die Position in den Einheiten des Spiels (Zoll), Z nach oben. demoparser2 gibt den Ursprung des Spielers, also die Füße. |
| `yaw`, `pitch` | die Blickrichtung (Grad), zu einem Einheitsvektor umgerechnet |
| `health`, `armor_value` | Gesundheit, Rüstung |
| `team_num` | die Seite: 2 = T, 3 = CT; alles andere (Zuschauer, 0, 1) ist keine Seite |
| `team_clan_name` | der Name des Teams, wie der Server ihn zeigt; dient dazu, die Teams zu benennen |
| `active_weapon_name` | die gehaltene Waffe, so wie das Spiel sie benennt (`AK-47`, `Karambit`) |
| `is_alive` | ob der Spieler lebt - nur lebende Spieler werden zu Positionen |
| `last_place_name` | der eigene Ortsname der Karte (`BombsiteA`) |
| `balance` | Geld |
| `current_equip_value` | der Wert dessen, was der Spieler trägt |

### Spielregel-Felder {#game-rules-fields}

Zusätzlich gelesen, einmal pro Spielerzeile (sie sind für alle zu einem Tick gleich):

| Eigenschaft | Verwendet für |
|---|---|
| `game_time` | die Uhr des Servers, in Sekunden |
| `total_rounds_played` | die Rundenzählung, die über die Dateien eines Matches weiterläuft |
| `round_win_status` | wer die eben gespielte Runde gewonnen hat: 1 Unentschieden, 2 T, 3 CT |
| `round_win_reason` | wie (das `CSRoundEndReason` des Spiels) |
| `team_rounds_total` | der Stand jeder Seite |
| `is_warmup_period` | das Warmup wird überall weggelassen |
| `is_freeze_period` | die Freeze-Zeit wird aus den Positionen weggelassen |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | die gespielte Verlängerung, 0 in der regulären Spielzeit: Verlängerungsrunden sind keine Pistolenrunden (der Parser hat keinen kürzeren Namen dafür) |

## Die Ereignisse {#the-events}

Jedes Ereignis unten wird gelesen, wenn das Demo es deklariert (`list_game_events`), mit `X`, `Y`, `Z`, `team_num`,
`last_place_name` und `which_bomb_zone` (die Bombenzone, in der der Spieler steht: 0 keine, 1 A, 2 B) für jeden Spieler,
den das Ereignis nennt, und `total_rounds_played` und `is_warmup_period` des Spiels zu diesem Tick:

| Ereignis | Wird zu |
|---|---|
| `player_death` | Kills und Tode; nutzt `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | Schaden; nutzt `dmg_health` (am Leben verursachter Schaden), `health` (übrige Gesundheit), `weapon` |
| `player_blind` | geblendete Spieler; nutzt `blind_duration` |
| `weapon_fire` | Schüsse und Granatenwürfe; nutzt `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | wo Granaten detonierten; nutzt die eigenen `x`, `y`, `z` des Ereignisses (das Ereignis hat für diesen Punkt keinen Ortsnamen, nur den des Werfers) |
| `bomb_planted` | die Legung; nutzt `which_bomb_zone` und den Ort des Legers sowie `site` (die Entity-Nummer der Zone) |
| `bomb_defused` | die Entschärfung |
| `bomb_exploded` | wann die Bombe explodierte: die Zeit der `explode`-Zeile |
| `round_freeze_end` | wo jede Runde beginnt |
| `round_prestart` | wo die Zeit nach einer entschiedenen Runde endet |
| `round_announce_match_start` | wo das Live-Match beginnt |

## Zwei Tatsachen über Demos, die bestimmen, wie sie gelesen werden {#two-facts-about-demos-that-decide-how-they-are-read}

- **Ein Match kann auf mehrere Dateien verteilt sein**, und die Namen der Dateien sagen nichts über ihre
  Reihenfolge. Die Rundenzählung (`total_rounds_played`) läuft über sie hinweg weiter, und meist auch die Uhr des
  Servers, sodass sich die Teile aus ihrem Inhalt ordnen lassen.
- **Eine Aufnahme kann vor dem Match beginnen**: Warmup, ein Neustart, eine Messer-Runde. Das Match beginnt mit dem
  **letzten** `round_announce_match_start` in einer Datei; davor wird alles weggelassen, und das Warmup wird überall
  weggelassen.
