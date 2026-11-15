---
title: "Diese Seiten pflegen"
nav_order: 17
lang: de
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Diese Seiten pflegen {#maintaining-these-pages}

Die Checkliste für jedes Release. Die Seiten müssen sagen, was der Code tut, für Anfänger und Achtjährige
gut lesbar sein und in jeder Sprache existieren, die der 3DHeat-Viewer unterstützt.

## Release-Checkliste {#release-checklist}

1. **Die erzeugten Seiten aus dem Code neu erzeugen:**

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Vor dem Committen muss dasselbe mit `--check` mit Exit-Code 0 enden:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Die Funktionen seit dem letzten Release vergleichen.** `VERSION` enthält die Version; ihr Tag ist `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Jeder neue Befehl, jede Option, Spalte, Ausgabe oder jedes Verhalten bekommt eine Zeile auf der Seite, die
   es abdeckt, und eine Zeile in `CHANGELOG.md` unter **Docs**, die die Seite nennt.

3. **Unabhängige Prüfung.** Jemand, der die Änderung nicht geschrieben hat, liest die geänderten Seiten -
   Diagramme und Bilder eingeschlossen - dreimal: als Anfänger (hat nie ein Terminal benutzt), als Achtjähriger
   (sagt der erste Absatz in einfachen Worten, was es ist und warum?) und als Profi (sind Flags, Standardwerte
   und Spalten genau das, was der Code tut?).

4. **Behebe, was die Prüfung gefunden hat.** Bilder bleiben etwa 900 px breit, mit Text von mindestens 12 px
   wie gezeigt; Diagramme werden aus `tools/diagrams/*.json` mit `tools/flow2svg.py` erzeugt. Beispiele
   verwenden nur erfundene Namen (`de_x`, "Demo Valley", `<map>`): nie eine echte Karte, einen echten Spieler,
   eine echte Match-ID oder eine Figur aus echten Dateien.

5. **Übersetzungen.** Jede übersetzte Seite hält den Hash der englischen Quelle fest, aus der sie entstanden ist.
   Übersetze die Seiten neu, deren englischer Quell-Hash sich geändert hat, und lass danach jede Sprache auf die
   gleichen drei Arten prüfen (einfach, Anfänger, Profi), einschließlich der Beschriftungen der Diagramme.

6. **Erst nach dem Go des Besitzers pushen.** Committe lokal; der Besitzer entscheidet, wann es öffentlich wird.

## Übersetzungen: die Befehle {#translations-the-commands}

Die Seite wird in die 40 Sprachen des 3DHeat-Viewers übersetzt: Englisch in `docs/`, jede andere Sprache in
`docs/<lang>/` mit denselben Dateinamen. `tools/docs_i18n.py` erledigt die Buchführung:

```bash
python tools/docs_i18n.py hashes             # nach jeder englischen Änderung: den Hash jeder Seite festhalten
python tools/docs_i18n.py svg-strings        # nach jeder Bildänderung: die zu übersetzenden Beschriftungen
python tools/docs_i18n.py status             # pro Sprache: aktuell, veraltet, fehlende Seiten
python tools/docs_i18n.py todo --lang de     # die deutschen Seiten, die (neu) übersetzt werden müssen
python tools/docs_i18n.py svg-build --lang de    # deutsche Bilder aus docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # die deutschen Seiten mit ihrem englischen Hash stempeln
python tools/docs_i18n.py check              # Exit-Code 1, wenn Hashes oder Beschriftungen veraltet sind
```

Übersetze nur, was `todo` auflistet: Markdown, Links, Code, Datei- und Spaltennamen bleiben, wie sie sind;
Titel und Bildbeschreibungen werden übersetzt, und für Schaltflächen und Panels verwendet man die eigenen
Wörter des 3DHeat-Viewers (aus `src/i18n/locales/<lang>/`). Erzeugte Referenzseiten und Terminal-Bilder bleiben
englisch. Auf der Seite zeigt eine veraltete Übersetzung das an und verlinkt die englische Seite; fehlt eine,
fällt die Seite auf Englisch zurück. Das Sprachmenü im Kopf und die Weiterleitung der Startseite nach der
Browser-Sprache kommen aus `docs/_includes/`.
