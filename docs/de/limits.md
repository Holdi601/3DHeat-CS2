---
title: "Grenzen"
nav_order: 13
lang: "de"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Grenzen {#limits}

Was der Konverter voraussetzt, was er nicht behandelt und was nicht geprüft ist. Jeder Punkt stammt aus
dem Code, so wie er jetzt steht.

## Was er liest {#what-it-reads}

- **Nur unkomprimierte `.dem`-Dateien.** `.dem.zst`, `.dem.bz2`, `.rar` und `.zip` müssen zuerst entpackt
  werden. Die Endung wird in jeder Schreibweise erkannt (`.dem`, `.DEM`), in Ordnern wie bei Dateien, die
  mit Namen angegeben werden.
- **Bombenentschärfungs-Matches.** Die Gründe für das Rundenende, die Bombenlegung und ihren Ort, die
  Buy-Typen und die Pistolenrunden sind die des Bombenmodus. Geiselkarten, Wingman und andere Modi werden
  nicht besonders behandelt und sind nicht geprüft.
- **64 Ticks pro Sekunde** werden für jede Zeit aus Ticks angenommen (`TICKRATE = 64`); CS2-Server laufen mit 64.
- **Ein Demo vom Server** (SourceTV) wird angenommen: es hat jeden Spieler. Eine Aufnahme auf dem Client
  (POV-Demo) wurde nicht probiert.

## Matches und Runden {#matches-and-rounds}

- **Dateien werden nach Namen gruppiert.** Die Teile eines Matches müssen außer einem `-pN`- / `_pN`-Suffix
  denselben Namen haben; Dateien eines Matches unter unverwandten Namen werden zu getrennten Matches, und
  gleichnamige Dateien in verschiedenen Ordnern werden zusammengruppiert (und dann in Ketten geteilt, wenn
  sie nicht aneinander anschließen).
- **Das Live-Match beginnt bei der letzten `round_announce_match_start`** einer Datei. Eine Messer-Runde,
  auf die diese Ankündigung nicht folgt, wird als Runde gezählt.
- **Rundenendzeiten sind auf eine Abtastung genau** (`--every` Ticks, standardmäßig 1/8 s), weil die
  Entscheidung aus abgetastetem Spielzustand gelesen wird. Ein sehr großes `--every` kann ein kurzes
  Fenster zwischen dem Ende einer Runde und dem Start der nächsten übersehen und die Runde als unvollständig
  weglassen.
- **Unentschieden.** Eine unentschiedene Runde (Win-Status 1, Grund 10) ist ohne Gewinner entschieden:
  `winner` ist leer, und keine Seite hat sie gewonnen. In einem echten Demo ist kein Unentschieden
  aufgetreten, an dem man das prüfen könnte; geprüft ist es am synthetischen Demo.
- **Runden, die abgeschnitten werden**, weil eine Datei endet, werden weggelassen (`incomplete`), nicht
  geraten; Runden vor der ersten in den Dateien stehen als `missing`.
- **Pistolenrunden** richten sich nach der Länge der Hälfte, die die Aufnahme zeigt: dort, wo die Seiten
  zwischen zwei aufeinanderfolgenden regulären Runden zum ersten Mal tauschen. Eine Aufnahme, die diesen
  Tausch nicht zeigt (sie beginnt nach der Halbzeit, endet davor, oder eine Runde zu beiden Seiten fehlt),
  kennt nur Runde 1 als Pistolenrunde. Verlängerungen haben keine.
- **Teams.** Ein Team ist der Clan-Name, der für seine Spieler am häufigsten gesehen wurde. Ohne Clan-Namen
  sind die Teams `Started T` und `Started CT`. Ein Spieler, der mitten im Match das Team wechselt, behält
  ein Team.

## Ereignisse {#events}

- **Alles, was der Parser bietet, wird gelesen**, mit diesen Ausnahmen: die Geschwindigkeit der Spieler
  (der Parser leitet sie aus den Positionen ab; sie steht nicht im Demo), die Sprache (Audio,
  `parse_voice`) und der `weapon_fire` der Bombe (der Beginn einer Legung, den `bomb_beginplant` hat).
  Granatenflüge werden in der Abtastung der Spieler (`--every`) und dort festgehalten, wo jede Granate
  stehen blieb, nicht bei jedem Tick.
- **Zeilen außerhalb einer Runde** (Warmup, eine Pause zwischen dem Start des Matches und der ersten
  Freeze-Zeit, wenn sie länger als zwei Minuten ist) fallen aus der Tabelle heraus; die Ereignisse ohne
  Spieler stehen alle in `events` des Match-Dokuments.
- **Detonationszeilen** (`smoke`, `flash`, `he`, `molotov`, `decoy`) haben kein `place`: das Demo nennt Orte
  für Spieler, nicht für Granaten. Der Ort des Werfers in diesem Moment steht in `throwerPlace`.
- **Die Zone der Bombenlegung** kommt aus der Bombenzone, die das Spiel für den Leger angibt; sonst aus dem
  Ortsnamen des Legers; sonst aus einer anderen Legung in derselben Zone in derselben Datei. Sagt keiner
  davon etwas, bleibt `site` leer.
- **Ein Tod durch die Welt** (ein Sturz, die Bombe) hat keinen Angreifer: kein Kill, kein Teamkill, kein
  Opening; es ist ein Tod.

## Statistik {#statistics}

- **Gespielte Runden** ergeben sich daraus, wer in der ersten Sekunde nach Freeze-Zeit eine Position hatte.
  Ein Spieler, der später in der Runde einsteigt, zählt sie nicht als gespielt (seine Kills zählen trotzdem).
- **Überleben für KAST**: ein Spieler, der in der After-Phase getötet wurde, hat für KAST nicht überlebt,
  auch wenn die Rundenliste ihn unter den Überlebenden nennt.
- **Beide Spieler eines 1-gegen-1** können in einer Runde einen Clutch gutgeschrieben bekommen; siehe
  [Statistiken](statistics.md#clutches).
- **Utility-Schaden** sind HE-Granaten, Molotows und Brandgranaten; ein Kill oder Treffer durch eine
  geworfene Blendgranate oder Lockgranate ist kein Utility-Schaden.

## Karten-Export {#map-export}

- Braucht das installierte Spiel (oder die `.vpk`) und die CLI von Source2Viewer; es wird nichts
  heruntergeladen.
- Exportiert nur `world_physics`; Clip-Brushes und der Himmel fallen durch ihre Namen weg, die `clip` oder
  `sky` enthalten, egal in welcher Schreibweise.
- Boden wird von Struktur allein an der Flächennormale unterschieden (Z-Komponente 0,7 oder mehr), also ist
  eine steile Rampe Struktur und ein flaches Dach Boden.
- Die Datei ist in Zoll, nicht in Metern.

## Speicher und Zeit {#memory-and-time}

- Ein Match wird beim Bauen ganz im Speicher gehalten, in einem Arbeiter pro Match. Bei vielen Arbeitern und
  einem kleinen `--every` addiert sich der Speicher: senke `--jobs`, wenn einem Rechner der Speicher ausgeht.
- Ein Match wird erst beim Bauen geschrieben: zuerst die `.parquet`, dann die `.match.json`. Ein Lauf, der
  dazwischen angehalten wird, lässt eine Tabelle ohne ihr Match-Dokument zurück; ein Match gilt nur mit beiden
  als geschrieben, daher wird es beim nächsten Lauf erneut konvertiert. Noch nicht begonnene Matches nimmt
  der nächste Lauf einfach auf.
