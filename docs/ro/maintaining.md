---
title: Întreținerea acestor pagini
nav_order: 17
lang: "ro"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Întreținerea acestor pagini {#maintaining-these-pages}

Lista de verificare pentru fiecare lansare. Paginile trebuie să spună ce face codul, să se
citească bine pentru un începător, un copil de opt ani și un profesionist, și să existe în
fiecare limbă pe care o susține vizualizatorul 3DHeat.

## Lista de verificare pentru lansare {#release-checklist}

1. **Regenerează paginile generate** din cod:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Înainte de commit, același lucru cu `--check` trebuie să iasă cu codul 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Compară funcționalitățile de la ultima lansare.** `VERSION` ține versiunea; eticheta sa
   este `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Fiecare comandă, opțiune, coloană, ieșire sau comportament nou primește o linie pe pagina
   care îl acoperă și o linie în `CHANGELOG.md`, la **Docs**, care numește pagina.

3. **Revizuire independentă.** Cineva care nu a scris schimbarea citește paginile modificate -
   inclusiv diagramele și imaginile - de trei ori: ca începător (nu a folosit niciodată un
   terminal), ca un copil de opt ani (prima paragraf spune ce este și de ce, cu cuvinte simple?)
   și ca profesionist (sunt steagurile, valorile implicite și coloanele exact ceea ce face codul?).

4. **Repară ce a găsit revizuirea.** Imaginile rămân de cel mult aproximativ 900 px lățime, cu
   text de cel puțin 12 px așa cum apare; diagramele sunt generate din `tools/diagrams/*.json`
   cu `tools/flow2svg.py`. Exemplele folosesc doar nume inventate (`de_x`, "Demo Valley",
   `<map>`): niciodată o hartă reală, un jucător real, un id de meci real sau o cifră din
   fișiere reale.

5. **Traduceri.** Fiecare pagină tradusă înregistrează hash-ul sursei engleze din care a fost
   făcută. Retraduce paginile a căror hash al sursei engleze s-a schimbat, apoi fă ca fiecare
   limbă să fie revizuită în aceleași trei moduri (simplu, începător, profesionist), inclusiv
   etichetele diagramelor.

6. **Trimite (push) doar cu acordul proprietarului.** Fă commit local; proprietarul decide când
   devine public.

## Traducerile: comenzile {#translations-the-commands}

Site-ul este tradus în cele 40 de limbi ale vizualizatorului 3DHeat: engleza în `docs/`, fiecare
altă limbă în `docs/<lang>/`, cu aceleași nume de fișiere. `tools/docs_i18n.py` face evidența:

```bash
python tools/docs_i18n.py hashes             # după orice schimbare în engleză: notează hash-ul fiecărei pagini
python tools/docs_i18n.py svg-strings        # după orice schimbare de imagine: etichetele de tradus
python tools/docs_i18n.py status             # pe limbă: pagini actuale, învechite, lipsă
python tools/docs_i18n.py todo --lang de     # paginile în germană de (re)tradus
python tools/docs_i18n.py svg-build --lang de    # imaginile în germană din docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marchează paginile în germană cu hash-ul lor englez
python tools/docs_i18n.py check              # iese cu 1 când hash-urile sau etichetele sunt vechi
```

Tradu doar ce listează `todo`: păstrează Markdown-ul, linkurile, codul, numele fișierelor și
ale coloanelor așa cum sunt, tradu titlurile și descrierile imaginilor, și folosește cuvintele
proprii ale vizualizatorului 3DHeat pentru butoanele și panourile sale (din
`src/i18n/locales/<lang>/`). Paginile de referință generate și imaginile din terminal rămân în
engleză. Pe site, o traducere învechită spune asta și trimite la pagina în engleză; una
lipsă revine la engleză. Meniul de limbă din antet și redirecționarea automată după limba
browserului de pe pagina principală vin din `docs/_includes/`.
