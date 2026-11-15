---
title: "Das Match-Dokument"
nav_order: 9
lang: de
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Das Match-Dokument (`<match>.match.json`) {#the-match-document-matchjson}

Ein JSON-Dokument pro Match, neben seiner Tabelle: Teams, Ergebnis, jede Runde mit ihrem Ergebnis, Wirtschaft,
Bombenlegung, Kills, Clutches und Überlebende und die Scoreboard-Zeile jedes Spielers. Es ist das, was der
Match-Tab des 3DHeat-Viewers lädt. Code: `summary()` in
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py); die Zahlen sind auf
[Statistiken](statistics.md) definiert.

Die Datei ist UTF-8, mit einem Leerzeichen eingerückt, und behält Nicht-ASCII-Zeichen (Spieler- und Teamnamen) so,
wie sie sind. Zeiten sind Sekunden, auf drei Nachkommastellen gerundet für Runden und auf zwei für Kills und die
Bombenlegung.

## Das Dokument {#the-document}

| Feld | Typ | Was |
|---|---|---|
| `format` | string | immer `heat3d-cs2-match` - woran ein Leser die Datei erkennt |
| `version` | number | `3`. Ein Dokument der Version 1 gibt die `time` einer Bombenlegung in Match-Sekunden an; ab 2 in Sekunden in der Runde, wie bei einem Kill. 3 fügt die Felder ab `header` hinzu und die Freeze-Zeit zur Tabelle. |
| `match` | string | der Match-Name, so wie die Dateien heißen |
| `map` | string | die Karte (`de_x`) |
| `demos` | string[] | die Demo-Dateien, aus denen es gebaut wurde, nur Dateinamen, in Match-Reihenfolge |
| `teams` | string[] | die Teamnamen in der Reihenfolge des ersten Auftretens (Runde 1: zuerst die T-Seite) |
| `score` | object | Teamname -> gewonnene Runden: der Stand der letzten Runde |
| `rounds` | object[] | jede vollständige Runde, in Reihenfolge - [unten](#rounds) |
| `incomplete` | number[] | Rundennummern, die am Ende eines Demos abgeschnitten und weggelassen wurden |
| `missing` | number[] | Rundennummern vor der ersten, die die Demos enthalten: `[1, 2]`, wenn die Aufnahme mit Runde 3 beginnt |
| `halfLength` | number oder null | Runden in einer regulären Hälfte, ab dem ersten Seitentausch (`12` im Format mit 24 Runden); null, wenn die Aufnahme den Tausch nicht zeigt |
| `pistolRounds` | number[] | die Pistolenrunden, mit denen der `buy` gezählt wird: Runde 1 und die Runde nach der Hälfte, wenn `halfLength` bekannt ist; nie eine Verlängerungsrunde |
| `players` | object[] | das Scoreboard - [unten](#players) |
| `conventions` | object | die Definitionen hinter den Zahlen, [unten](#conventions) |
| `header` | object | der Header des ersten Demos, so wie der Parser ihn gibt: Servername, Patch-Version, Demo-Version, Karte |
| `profiles` | object | Steam-ID -> was für einen Spieler während des Matches gleich bleibt: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (das zuletzt Gesehene) |
| `playerInfo` | object[] | jeder Spieler, den die Demos auflisten, auch Coaches und Caster: Steam-ID, Name, Teamnummer |
| `skins`, `itemDrops` | object[] | Waffen-Skins und Item-Drops, wo das Demo sie hat (Turnier-Demos aus der Übertragung haben keine) |
| `chat` | object[] | jede Chatzeile des Matches: Zeit, Runde, Spieler, Seite, Text |
| `events` | object[] | jedes Spielereignis ohne Spieler, in Zeitfolge, mit allen seinen Feldern: Rundentöne und Phasen, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (die Einstellungen des Servers, wie sie sich änderten), die Chase- und Fixed-Kameraeinstellungen des Übertragungsregisseurs, `cs_win_panel_match`, ... |
| `state` | object[] | der Spielzustand, wo er sich änderte: Zeit, Feld, Wert - Auszeiten (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), die Bombe (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, die lebenden Spieler, die `match_start_time` und `round_start_time` des Servers |
| `selfCheck` | object | `completeness`: wohin alles aus dem Demo ging - je Ereignisname, Eigenschaftsklasse, Netzwerknachricht, Frame und Stringtabelle die Zählungen `seen`, `decoded`, `partial`, `raw` und `lost`, die geschriebenen Beiwerk-Dateien, das gesamte `lost` (0, außer bei `--no-bulk`), die Eigenschaften, die der Parser auflistet, aber nicht lesen kann (`unreadProps`). Die Konvention: [Konverter behalten alles](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); die Beiwerk-Dateien: der Abschnitt Vollständigkeit der README |

## Runden {#rounds}

| Feld | Typ | Was |
|---|---|---|
| `number` | number | die Runde, ab 1 |
| `start` | number | Match-Sekunden, als die Freeze-Zeit endete |
| `end` | number | Match-Sekunden, als die Runde entschieden wurde |
| `until` | number | Match-Sekunden, als die nächste Runde begann (das Ende der After-Phase) |
| `winner` | string | `T` oder `CT`; leer bei einem Unentschieden |
| `winnerTeam` | string | der Teamname der gewinnenden Seite; leer bei einem Unentschieden |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` oder `other` |
| `score` | object | Teamname -> gewonnene Runden nach dieser |
| `sides` | object | Teamname -> `T` / `CT` in dieser Runde |
| `equipment` | object | Seite -> Gesamtausrüstungswert ihrer lebenden Spieler beim Freeze-Ende, in Dollar |
| `buy` | object | Seite -> `pistol`, `eco`, `force` oder `full` |
| `plant` | object oder null | die Bombenlegung: `site` (`A` oder `B`; leer, wenn das Demo es nicht angibt), `time` (Sekunden **in der Runde**, wie bei einem Kill), `player`, `steamid`, `x`, `y`, `z` (Spieleinheiten), `place` (der Ortsname des Legers: wo die Bombe lag) |
| `survivors` | object | Seite -> Namen der Startspieler, die beim Entscheiden der Runde noch lebten, sortiert |
| `clutches` | object[] | je: `player`, `steamid`, `side`, `against` (Gegner, die noch lebten, als der Spieler der letzte wurde), `won` |
| `kills` | object[] | jeder Tod der Runde, in Reihenfolge - unten |

Wie diese gefunden werden: [Ein Match aufbauen](building-matches.md#rounds); Clutches und Überlebende:
[Statistiken](statistics.md#clutches).

### Die Kills einer Runde {#a-rounds-kills}

Jeder Tod in der Runde, auch in der After-Phase:

| Feld | Typ | Was |
|---|---|---|
| `time` | number | Sekunden **in der Runde** (seit dem Freeze-Ende) |
| `attacker`, `attackerSide` | string | der Killer und seine Seite; leer für die Welt |
| `victim`, `victimSide` | string | das Opfer und seine Seite |
| `assister` | string oder null | der assistierende Spieler oder null |
| `flashAssist` | bool | der Assist war eine Blendung |
| `weapon` | string | so, wie das Spiel sie benennt |
| `headshot` | bool | |
| `wallbang` | bool | die Kugel ging durch etwas hindurch |
| `throughSmoke` | bool | der Kill ging durch Rauch |
| `noscope` | bool | eine Zielfernrohr-Waffe schoss ohne Zielfernrohr |
| `attackerBlind` | bool | der Killer war geblendet |
| `opening` | bool | der erste Kill eines Gegners in der Runde |
| `traded` | bool | dieser Tod wurde innerhalb von 5 s gerächt |
| `trade` | bool | dieser Kill hat innerhalb von 5 s einen Teamkameraden gerächt |
| `teamkill` | bool | Angreifer und Opfer auf derselben Seite, zwei verschiedene Spieler |
| `suicide` | bool | Angreifer und Opfer derselbe Spieler (etwa eine eigene Granate); kein Teamkill |
| `after` | bool | der Kill kam, nachdem die Runde entschieden war |
| `place` | string | wo das **Opfer** war (der Ortsname der Karte) |

## Spieler {#players}

Ein Eintrag pro Spieler, nach Teamname und dann die besten zuerst nach Kills minus Tode, dann Kills:

| Feld | Typ | Was |
|---|---|---|
| `name`, `steamid`, `team` | string | wer |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | Assists ohne und mit Blendung |
| `diff` | number | Kills - Tode |
| `adr` | number | durchschnittlicher Schaden pro gespielter Runde, verlorene Gesundheit |
| `kast` | number | Prozent der gespielten Runden mit einem Kill, einem Assist, einem Überleben oder einem getradeten Tod |
| `headshotPct` | number | Prozent der Kills, die Kopftreffer waren |
| `openingKills`, `openingDeaths` | number | gewonnene und verlorene Opening-Duelle |
| `tradeKills`, `tradedDeaths` | number | Trade-Kills; Tode, die getradet wurden |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: Runden mit so vielen Kills |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | Schaden mit HE, Molotow, Brandgranate |
| `enemiesFlashed` | number | Gegner, die mindestens 1 s geblendet wurden |
| `plants`, `defuses` | number | |
| `teamkills` | number | getötete Teamkameraden; Suizide zählen nicht |
| `roundsPlayed` | number | begonnene Runden |

Jede Definition: [Statistiken](statistics.md#the-scoreboard-line).

## Konventionen {#conventions}

Steht in jedem Dokument, damit ein Leser ohne diese Seite weiß, was die Zahlen bedeuten:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Ein Beispiel {#an-example}

Aus dem synthetischen Demo mit zwei Runden aus den Tests, gekürzt (`...` markiert, was weggelassen ist):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

Die Reihenfolge der Schlüssel in `survivors`, `equipment` und `buy` ist nicht festgelegt.
