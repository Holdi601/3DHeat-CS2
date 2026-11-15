---
title: "Mirëmbajtja"
nav_order: 17
lang: "sq"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Mirëmbajtja e këtyre faqeve {#maintaining-these-pages}

Lista e kontrollit për çdo botim. Faqet duhet të thonë çfarë bën kodi, të lexohen mirë për një fillestar, një
8-vjeçar dhe një profesionist, dhe të ekzistojnë në çdo gjuhë që mbështet shikuesi 3DHeat.

## Lista e kontrollit të botimit {#release-checklist}

1. **Rigjenero faqet e gjeneruara** nga kodi:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Para commit-it, e njëjta gjë me `--check` duhet të dalë me 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Krahaso veçoritë që nga botimi i fundit.** `VERSION` mban versionin; etiketa e tij është `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Çdo komandë, opsion, kolonë, dalje ose sjellje e re merr një rresht në faqen që e mbulon, dhe një
   rresht te `CHANGELOG.md` nën **Docs** që e emërton atë faqe.

3. **Shqyrtim i pavarur.** Dikush që nuk e shkroi ndryshimin i lexon faqet e ndryshuara - diagramet dhe
   fotot të përfshira - tri herë: si fillestar (nuk ka përdorur kurrë Terminal), si 8-vjeçar (a thotë
   paragrafi i parë çfarë është dhe pse, me fjalë të thjeshta?) dhe si profesionist (a janë flamujt, parazgjedhjet dhe
   kolonat saktësisht ç'bën kodi?).

4. **Rregullo çfarë gjeti shqyrtimi.** Fotot qëndrojnë më së shumti rreth 900 px të gjera me tekst prej të paktën 12 px
   siç shfaqen; diagramet gjenerohen nga `tools/diagrams/*.json` me `tools/flow2svg.py`. Shembujt përdorin
   vetëm emra të shpikur (`de_x`, "Demo Valley", `<map>`): kurrë një hartë, lojtar, id ndeshjeje apo shifër
   e vërtetë nga skedarë të vërtetë.

5. **Përkthimet.** Çdo faqe e përkthyer regjistron hash-in e burimit anglisht nga i cili u bë.
   Ripërktheji faqet hash-i i burimit anglisht i të cilave ndryshoi, pastaj shqyrto çdo gjuhë në të njëjtat
   tri mënyra (e thjeshtë, fillestar, profesionist), përfshirë etiketat e diagrameve.

6. **Shtyj vetëm pas lejes së pronarit.** Bëj commit lokalisht; pronari vendos kur del publikisht.

## Përkthimet: komandat {#translations-the-commands}

Faqja përkthehet në 40 gjuhët e shikuesit 3DHeat: anglisht te `docs/`, çdo gjuhë tjetër
te `docs/<lang>/` me të njëjtat emra skedarësh. `tools/docs_i18n.py` mban evidencën:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Përkthe vetëm çfarë liston `todo`: mbaj Markdown, lidhjet, kodin, emrat e skedarëve dhe kolonave siç janë,
përkthe titujt dhe përshkrimet e fotove, dhe përdor fjalët e vetë shikuesit 3DHeat për butonat
dhe panelet e tij (`src/i18n/locales/<lang>/`). Faqet e referencës së gjeneruara dhe fotot e terminalit mbeten
në anglisht. Në faqe, një përkthim i vjetruar e thotë këtë dhe lidh faqen angleze; një që mungon
kthehet te anglishtja. Menyja e gjuhës në krye dhe ridrejtimi i faqes kryesore sipas gjuhës së shfletuesit
vijnë nga `docs/_includes/`.
