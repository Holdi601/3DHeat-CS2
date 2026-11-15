---
title: "Vedligeholdelse af siderne"
nav_order: 17
lang: "da"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Vedligeholdelse af siderne {#maintaining-these-pages}

Tjeklisten for hver udgivelse. Siderne skal sige, hvad koden gør, læses godt for en
begynder, en 8-årig og en professionel, og findes på alle de sprog, 3DHeat-visningen understøtter.

## Udgivelsestjeklisten {#release-checklist}

1. **Generér de genererede sider** ud fra koden:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Før du committer, skal det samme med `--check` slutte med 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Gennemgå ændringerne siden sidste udgivelse.** `VERSION` holder versionen; dens tag er `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Hver ny kommando, valg, kolonne, udskrift eller adfærd får en linje på den side, der dækker den, og en
   linje i `CHANGELOG.md` under **Docs**, der nævner siden.

3. **Uafhængig gennemlæsning.** Én, der ikke skrev ændringen, læser de ændrede sider - diagrammer og billeder med - tre gange: som en begynder (har aldrig brugt en terminal), som en 8-årig (siger det første afsnit, hvad det er og hvorfor, med almindelige ord?) og som en professionel (er flag, standarder og kolonner præcis, hvad koden gør?).

4. **Ret det, gennemlæsningen fandt.** Billeder bliver ved omkring 900 px i bredden med tekst på mindst 12 px, som vist; diagrammer bliver genereret fra `tools/diagrams/*.json` med `tools/flow2svg.py`. Eksempler bruger kun opdigtede navne (`de_x`, "Demo Valley", `<map>`): aldrig et rigtigt kort, en rigtig spiller, et rigtigt kamp-id eller en figur fra rigtige filer.

5. **Oversættelser.** Hver oversat side registrerer hashen af den engelske kilde, den blev lavet ud fra. Oversæt igen de sider, hvis engelske kildehash er ændret, og lad så hvert sprog blive gennemgået på samme tre måder (almindeligt, begynder, professionel), inklusive diagrammets labels.

6. **Push først efter ejerens grønne lys.** Commit lokalt; ejeren bestemmer, hvornår det bliver offentligt.

## Oversættelser: kommandoerne {#translations-the-commands}

Siden er oversat til de 40 sprog, 3DHeat-visningen understøtter: engelsk i `docs/`, hvert andet
sprog i `docs/<lang>/` med de samme filnavne. `tools/docs_i18n.py` står for bogholderiet:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Oversæt kun det, `todo` lister: behold Markdown, links, kode, fil- og kolonnenavne, som de er; oversæt titler og billedbeskrivelser, og brug 3DHeat-visningens egne ord for dens knapper
og paneler (dens `src/i18n/locales/<lang>/`). Genererede referencesider og terminalbilleder bliver engelske. På siden viser en forældet oversættelse det og linker til den engelske side; en manglende falder tilbage til engelsk. Sprogmenuen i sidehovedet og browsersprog-omdirigeringen på forsiden kommer fra `docs/_includes/`.
