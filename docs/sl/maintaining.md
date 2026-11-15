---
title: "Vzdrževanje teh strani"
nav_order: 17
lang: "sl"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Vzdrževanje teh strani {#maintaining-these-pages}

Seznam za vsako izdajo. Strani morajo povedati, kaj koda res počne, morajo biti berljive za začetnika, osemletnika in
strokovnjaka ter obstajati v vsakem jeziku, ki ga podpira pregledovalnik 3DHeat.

## Seznam za izdajo {#release-checklist}

1. **Ustvari generirane strani** iz kode:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Pred potrditvijo mora isto z `--check` končati z 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Primerjaj funkcije od zadnje izdaje.** `VERSION` hrani različico; njena oznaka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Vsak nov ukaz, možnost, stolpec, izhod ali obnašanje dobi vrstico na strani, ki ga pokriva, in vrstico v
   `CHANGELOG.md` pod **Docs**, ki navaja stran.

3. **Neodvisen pregled.** Nekdo, ki spremembe ni napisal, prebere spremenjene strani – vključno z diagrami in
   slikami – trikrat: kot začetnik (še nikoli uporabil terminala), kot osemletnik (ali prvi odstavek pove, kaj je in
   zakaj, z enostavnimi besedami?) in kot strokovnjak (so zastavice, privzete vrednosti in stolpci točno to, kar koda
   počne?).

4. **Popravi, kar pregled najde.** Slike ostanejo široke največ okoli 900 slikovnih točk, z besedilom velikosti vsaj 12 px,
   kakor so prikazane; diagrami se ustvarijo iz `tools/diagrams/*.json` z `tools/flow2svg.py`. Primeri uporabljajo samo
   izmišljena imena (`de_x`, "Demo Valley", `<karta>`): nikoli prave karte, igralca, ID-ja tekme ali figure iz pravih
   datotek.

5. **Prevodi.** Vsaka prevedena stran si zapomni zgoščeno vrednost (hash) angleškega vira, iz katerega je nastala.
   Ponovno prevedite strani, katerih zgoščena vrednost angleškega vira se je spremenila, nato pa naj vsak jezik pregledajo
   na enak trikrat način (preprosto, začetnik, strokovnjak), vključno z oznakami diagramov.

6. **Objavite šele po dovoljenju lastnika.** Potrdite lokalno; lastnik odloči, kdaj gre javno.

## Prevodi: ukazi {#translations-the-commands}

Stran je prevedena v 40 jezikov: angleščina je v `docs/`, vsak drug jezik v `docs/<jezik>/` z
enakimi imeni datotek. `tools/docs_i18n.py` vodi evidenco:

```bash
python tools/docs_i18n.py hashes             # po vsaki spremembi angleščine: zapiši zgoščeno vrednost vsake strani
python tools/docs_i18n.py svg-strings        # po vsaki spremembi slik: napisi za prevod
python tools/docs_i18n.py status             # po jezikih: aktualne, zastarele, manjkajoče strani
python tools/docs_i18n.py todo --lang de     # nemške strani za (ponovni) prevod
python tools/docs_i18n.py svg-build --lang de    # nemške slike iz docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # nemške strani označi z zgoščeno vrednostjo angleščine
python tools/docs_i18n.py check              # izhod 1, ko so zgoščene vrednosti ali oznake zastarele
```

Prevedite samo to, kar izpiše `todo`: ohrani Markdown, povezave, kodo, imena datotek in stolpcev; prevedite naslove in opise
slik ter uporabite lastne besede pregledovalnika 3DHeat za njegove gumbe in plošče (njegov `src/i18n/locales/<jezik>/`).
Generirane referenčne strani in terminalske slike ostanejo v angleščini. Na spletišču zastarel prevod to pove in povezuje
angleško stran; manjkajoč prevod se prikaže v angleščini. Jezikovni meni v glavi in preusmeritev domače strani glede na
jezik brskalnika prihajata iz `docs/_includes/`.
