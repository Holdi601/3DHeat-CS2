---
title: Deze pagina's onderhouden
nav_order: 17
lang: "nl"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Deze pagina's onderhouden {#maintaining-these-pages}

De checklist voor elke release. De pagina's moeten zeggen wat de code doet, goed leesbaar zijn voor een beginner, een achtjarige en een expert, en bestaan in elke taal die de 3DHeat-viewer ondersteunt.

## Checklist voor elke release {#release-checklist}

1. **De gegenereerde pagina's opnieuw maken** uit de code:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Voor je commit moet hetzelfde met `--check` met code 0 eindigen:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **De functies sinds de vorige release vergelijken.** `VERSION` bevat de versie; de tag daarvan is `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Elke nieuwe opdracht, optie, kolom, uitvoer of gedrag krijgt een regel op de pagina die het beschrijft, en een regel in `CHANGELOG.md` onder **Docs** met de naam van die pagina.

3. **Onafhankelijke beoordeling.** Iemand die de wijziging niet heeft geschreven, leest de gewijzigde pagina's - ook de diagrammen en afbeeldingen - drie keer: als beginner (heeft nog nooit een terminal gebruikt), als achtjarige (zegt de eerste alinea in gewone woorden wat het is en waarom?) en als expert (zijn vlaggen, standaardwaarden en kolommen precies wat de code doet?).

4. **Oplossen wat de beoordeling vond.** Afbeeldingen blijven ongeveer 900 px breed, met tekst van minstens 12 px zoals getoond; diagrammen worden gegenereerd uit `tools/diagrams/*.json` met `tools/flow2svg.py`. Voorbeelden gebruiken alleen verzonnen namen (`de_x`, "Demo Valley", `<map>`): nooit een echte map, speler, wedstrijd-id of getal uit echte bestanden.

5. **Vertalingen.** Elke vertaalde pagina onthoudt de hash van de Engelse bron waarop ze is gebaseerd. Vertaal de pagina's opnieuw waarvan de hash van de Engelse bron is veranderd, en laat daarna elke taal op dezelfde drie manieren nakijken (gewoon, beginner, expert), inclusief de labels van de diagrammen.

6. **Pas pushen na de go van de eigenaar.** Commit lokaal; de eigenaar beslist wanneer het openbaar wordt.

## Vertalingen: de opdrachten {#translations-the-commands}

De site is vertaald in de 40 talen van de 3DHeat-viewer: Engels in `docs/`, elke andere taal in `docs/<lang>/` met dezelfde bestandsnamen. `tools/docs_i18n.py` doet het bijhouden:

```bash
python tools/docs_i18n.py hashes             # na elke Engelse wijziging: de hash van elke pagina vastleggen
python tools/docs_i18n.py svg-strings        # na elke wijziging van een afbeelding: de labels om te vertalen
python tools/docs_i18n.py status             # per taal: actueel, verouderd, ontbrekende pagina's
python tools/docs_i18n.py todo --lang de     # de Duitse pagina's om (opnieuw) te vertalen
python tools/docs_i18n.py svg-build --lang de    # Duitse afbeeldingen uit docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # de Duitse pagina's stempelen met hun Engelse hash
python tools/docs_i18n.py check              # afsluitcode 1 wanneer hashes of labels verouderd zijn
```

Vertaal alleen wat `todo` oplijst: houd Markdown, links, code, bestands- en kolomnamen zoals ze zijn, vertaal titels en beschrijvingen van afbeeldingen, en gebruik de eigen woorden van de 3DHeat-viewer voor zijn knoppen en panelen (in `src/i18n/locales/<lang>/`). Gegenereerde referentiepagina's en terminalafbeeldingen blijven Engels. Op de site zegt een verouderde vertaling dat en linkt naar de Engelse pagina; een ontbrekende valt terug op het Engels. Het taalmenu in de kop en de doorverwijzing op basis van de browsertaal van de startpagina komen uit `docs/_includes/`.
