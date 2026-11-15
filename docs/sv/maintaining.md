---
title: "Underhåll av sidorna"
nav_order: 17
lang: "sv"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Underhåll av sidorna {#maintaining-these-pages}

Checklistan för varje utgåva. Sidorna måste säga vad koden gör, läsas bra för en nybörjare, en
8-åring och en proffs, och finnas på alla språk som 3DHeat-visaren stöder.

## Checklista för utgivning {#release-checklist}

1. **Generera om de genererade sidorna** från koden:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Innan du committar måste samma sak med `--check` avslutas med 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Jämför funktionerna sedan förra utgivningen.** `VERSION` innehåller versionen; dess tagg är `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Varje nytt kommando, alternativ, kolumn, utdata eller beteende får en rad på sidan som täcker det,
   och en rad i `CHANGELOG.md` under **Docs** som anger sidan.

3. **Oberoende granskning.** Någon som inte skrev ändringen läser de ändrade sidorna tre gånger -
   bilder och diagram inräknade: som nybörjare (har aldrig använt en terminal), som 8-åring (säger
   det första stycket vad det är och varför, med enkla ord?) och som proffs (är flaggor, standardvärden
   och kolumner exakt vad koden gör?).

4. **Åtgärda det granskningen hittade.** Bilder är högst cirka 900 px breda med text på minst 12 px
   så som de visas; diagram genereras från `tools/diagrams/*.json` med `tools/flow2svg.py`. Exempel
   använder bara påhittade namn (`de_x`, "Demo Valley", `<map>`): aldrig en riktig karta, spelare,
   match-id eller figur från riktiga filer.

5. **Översättningar.** Varje översatt sida registrerar hashen för den engelska källan den gjordes
   av. Översätt om de sidor vars engelska källhash ändrats, och låt varje språk granskas på samma tre
   sätt (enkelt, nybörjare, proffs), inklusive diagrammens etiketter.

6. **Publicera bara efter ägarens klartecken.** Committa lokalt; ägaren bestämmer när det blir offentligt.

## Översättningar: kommandona {#translations-the-commands}

Sajten är översatt till de 40 språk som 3DHeat-visaren stöder: engelska i `docs/`, varje annat språk i
`docs/<språk>/` med samma filnamn. `tools/docs_i18n.py` sköter bokföringen:

```bash
python tools/docs_i18n.py hashes             # efter varje engelsk ändring: registrera varje sidas hash
python tools/docs_i18n.py svg-strings        # efter varje bildändring: etiketterna att översätta
python tools/docs_i18n.py status             # per språk: aktuella, inaktuella och saknade sidor
python tools/docs_i18n.py todo --lang de     # de tyska sidorna att (över)översätta
python tools/docs_i18n.py svg-build --lang de    # tyska bilder från docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # märk de tyska sidorna med deras engelska hash
python tools/docs_i18n.py check              # avslutar med 1 när hashar eller etiketter är inaktuella
```

Översätt bara det `todo` listar: behåll Markdown, länkar, kod, fil- och kolumnnamn som de är, och
översätt titlar och bildbeskrivningar, och använd 3DHeat-visarens egna ord för dess knappar och
paneler (dess `src/i18n/locales/<språk>/`). Genererade referenssidor och terminalbilder förblir
engelska. På sajten säger en inaktuell översättning det och länkar till den engelska sidan; en saknad
sida faller tillbaka på engelska. Språkmenyn i sidhuvudet och startsidans omdirigering efter
webbläsarens språk kommer från `docs/_includes/`.
