---
title: "Az oldalak karbantartása"
nav_order: 17
lang: "hu"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Az oldalak karbantartása {#maintaining-these-pages}

Ez a minden kiadásra szóló ellenőrzőlista. Az oldalaknak meg kell mondaniuk, mit csinál a kód, jól kell olvasniuk kezdőnek,
egy 8 évesnek és a profinak, és a 3DHeat megjelenítő minden támogatott nyelvén létezniük kell.

## Kiadási ellenőrzőlista {#release-checklist}

1. **Generáld újra a generált oldalakat** a kódból:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   A commit előtt ugyanez a `--check` kapcsolóval kilépési kóddal 0-val kell véget érjen:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Vesd össze az utolsó kiadás óta történt funkciókat.** A `VERSION` tartalmazza a verziót; a címkéje `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Minden új parancsot, kapcsolót, oszlopot vagy viselkedést kap egy sort azon az oldalon, amely lefedi, és egy sort a
   `CHANGELOG.md` **Docs** részében, az oldal nevével.

3. **Független átnézés.** Valaki, aki nem írta a változtatást, háromszor olvassa el a megváltozott oldalakat - az ábrákkal
   és képekkel együtt: kezdőként (sosem használt terminált), 8 évesként (az első bekezdés elmondja-e egyszerű szavakkal,
   mi ez és miért?), és profiként (a kapcsolók, alapértékek és oszlopok pontosan azt csinálják-e, amit a kód?).

4. **Javítsd, amit az átnézés talált.** A képek legfeljebb mintegy 900 px szélesek, a szöveg legalább 12 px-es marad, úgy,
   ahogy látszik; az ábrákat a `tools/diagrams/*.json` fájlokból generáljuk a `tools/flow2svg.py`-val. A példákban csak
   kitalált nevek szerepelhetnek (`de_x`, "Demo Valley", `<map>`): sosem valódi pálya, játékos, meccsazonosító vagy
   valódi fájlokból származó szám.

5. **Fordítások.** Minden lefordított oldal rögzíti annak az angol forrásnak a hash-ét, amelyből készült. Fordítsd újra
   azokat az oldalakat, amelyeknek az angol forrás hash-e megváltozott, majd minden nyelvet ugyanúgy átnézetni a három
   szempont szerint (egyszerű, kezdő, profi), az ábrák feliratait is beleértve.

6. **Csak a tulajdonos jóváhagyásával tolj.** Commitolj helyben; a tulajdonos dönti el, mikor lesz nyilvános.

## Fordítások: a parancsok {#translations-the-commands}

Az oldal a 3DHeat megjelenítő 40 nyelvére van fordítva: az angol a `docs/`-ban van, minden más nyelv a `docs/<lang>/`
mappában, ugyanazokkal a fájlnevekkel. A `tools/docs_i18n.py` végzi a nyilvántartást:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Csak azt fordítsd, amit a `todo` listáz: a Markdownt, a hivatkozásokat, a kódot, a fájl- és oszlopneveket hagyd úgy,
ahogy vannak; a címeket és a képleírásokat fordítsd; a megjelenítő gombjainak és paneljeinek a saját szavait használd
(a `src/i18n/locales/<lang>/` mappából). A generált referenciaoldalak és a terminálképek angolok maradnak. A webhelyen
egy elavult fordítás ezt megmondja, és az angol oldalra linkel; a hiányzó oldal visszaesik az angolra. A fejléc
nyelvmenüjét és a főoldal böngészőnyelv-átirányítását a `docs/_includes/` adja.
