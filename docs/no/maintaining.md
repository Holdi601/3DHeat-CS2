---
title: "Vedlikehold"
nav_order: 17
lang: "no"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Vedlikehold av disse sidene {#maintaining-these-pages}

Sjekklisten for hver utgivelse. Sidene må si hva koden gjør, lese godt for en nybegynner, en
8-åring og en proff, og finnes på alle språkene 3DHeat-visningen støtter.

## Sjekkliste for utgivelse {#release-checklist}

1. **Generer de genererte sidene** fra koden:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Før committing må det samme med `--check` avslutte med 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Gå gjennom funksjonene siden forrige utgivelse.** `VERSION` holder versjonen; taggen er `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Hver ny kommando, valg, kolonne, utdata eller oppførsel får en linje på siden som dekker den,
   og en linje i `CHANGELOG.md` under **Docs** som nevner siden.

3. **Uavhengig gjennomgang.** Noen som ikke skrev endringen, leser de endrede sidene - diagrammer
   og bilder inkludert - tre ganger: som en nybegynner (har aldri brukt en terminal), som en
   8-åring (sier det første avsnittet hva det er og hvorfor, med enkle ord?) og som en proff (er
   flagg, standarder og kolonner nøyaktig det koden gjør?).

4. **Rett det gjennomgangen fant.** Bilder holder seg omtrent under 900 px brede, med tekst på minst
   12 px slik de vises; diagrammer genereres fra `tools/diagrams/*.json` med `tools/flow2svg.py`.
   Eksempler bruker bare oppdiktede navn (`de_x`, "Demo Valley", `<map>`): aldri et ekte kart, en
   ekte spiller, en ekte kamp-ID eller en figur fra ekte filer.

5. **Oversettelser.** Hver oversatt side registrerer hashen til den engelske kilden den ble laget
   fra. Oversett på nytt de sidene der den engelske kildens hash har endret seg, og få hvert språk
   gjennomgått på samme tre måter (enkelt, nybegynner, proff), inkludert diagramtekstene.

6. **Send bare etter eierens grønne lys.** Commit lokalt; eieren bestemmer når det blir offentlig.

## Oversettelser: kommandoene {#translations-the-commands}

Siden er oversatt til de 40 språkene 3DHeat-visningen støtter: engelsk i `docs/`, hvert annet
språk i `docs/<språk>/` med de samme filnavnene. `tools/docs_i18n.py` gjør bokføringen:

```bash
python tools/docs_i18n.py hashes             # etter enhver engelsk endring: registrer hashen til hver side
python tools/docs_i18n.py svg-strings        # etter enhver bildeendring: tekstene som skal oversettes
python tools/docs_i18n.py status             # per språk: oppdatert, utdatert, manglende sider
python tools/docs_i18n.py todo --lang de     # de tyske sidene som skal (over)oversettes
python tools/docs_i18n.py svg-build --lang de    # tyske bilder fra docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # merk de tyske sidene med deres engelske hash
python tools/docs_i18n.py check              # avslutter med 1 når hasher eller tekster er utdaterte
```

Oversett bare det `todo` lister: behold Markdown, lenker, kode, fil- og kolonnenavn som de er,
oversett titler og bildebeskrivelser, og bruk 3DHeat-visningens egne ord for knapper og paneler
(dens `src/i18n/locales/<språk>/`). Genererte referansesider og terminalbilder forblir engelske.
På nettstedet sier en utdatert oversettelse fra og lenker til den engelske siden; en manglende
faller tilbake til engelsk. Språkmenyen i topptekst og språkomdirigeringen på forsiden kommer fra
`docs/_includes/`.
