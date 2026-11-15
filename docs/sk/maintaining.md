---
title: Údržba týchto stránok
nav_order: 17
lang: "sk"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Údržba týchto stránok {#maintaining-these-pages}

Kontrolný zoznam pre každé vydanie. Stránky musia hovoriť, čo kód naozaj robí,
dobre sa čítať pre začiatočníka, osemročné dieťa aj pre profesionála, a existovať
v každom jazyku, ktorý podporuje prehliadač 3DHeat.

## Kontrolný zoznam vydania {#release-checklist}

1. **Vygenerujte znovu generované stránky** z kódu:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Pred commitom musí byť to isté s `--check` s návratovým kódom 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Porovnajte funkcie od posledného vydania.** `VERSION` drží verziu; jej
   značka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Každý nový príkaz, možnosť, stĺpec, výstup alebo správanie dostane riadok na
   stránke, ktorá ho pokrýva, a riadok v `CHANGELOG.md` pod **Docs** s názvom
   stránky.

3. **Nezávislá kontrola.** Niekto, kto zmenu nenapísal, prečíta zmenené stránky -
   vrátane diagramov a obrázkov - trikrát: ako začiatočník (nikdy nepoužil
   terminál), ako osemročné dieťa (hovorí prvý odsek, čo to je a prečo, jednoduchými
   slovami?) a ako profesionál (sú príznaky, predvolené hodnoty a stĺpce presne
   také, aké kód robí?).

4. **Opravte, čo kontrola zistila.** Obrázky zostanú najviac okolo 900 px
   široké s textom aspoň 12 px, ako sú zobrazené; diagramy sa generujú z
   `tools/diagrams/*.json` nástrojom `tools/flow2svg.py`. Príklady používajú iba
   vymyslené názvy (`de_x`, "Demo Valley", `<map>`): nikdy skutočnú mapu,
   hráča, identifikátor zápasu ani údaj zo skutočných súborov.

5. **Preklady.** Každá preložená stránka zaznamená hash anglického zdroja, z
   ktorého vznikla. Znovu preložte stránky, ktorých hash anglického zdroja sa
   zmenil, a potom každý jazyk nechajte skontrolovať rovnakými tromi spôsobmi
   (jednoducho, pre začiatočníka, pre profesionála), vrátane popisov diagramov.

6. **Odoslať len so súhlasom vlastníka.** Commitujte lokálne; vlastník rozhodne,
   kedy sa to zverejní.

## Preklady: príkazy {#translations-the-commands}

Stránky sa prekladajú do 40 jazykov prehliadača 3DHeat: angličtina v `docs/`,
každý ďalší jazyk v `docs/<lang>/` s rovnakými názvami súborov. `tools/docs_i18n.py`
robí evidenciu:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prekladajte iba to, čo `todo` uvádza: ponechajte Markdown, odkazy, kód, názvy
súborov a stĺpcov tak, ako sú; prekladajte nadpisy a popisy obrázkov; a na
tlačidlá a panely prehliadača 3DHeat používajte jeho vlastné slová (jeho
`src/i18n/locales/<lang>/`). Generované referenčné stránky a obrázky terminálu
zostávajú v angličtine. Na webe preložená stránka, ktorá je zastaraná, to
povie a odkáže na anglickú stránku; chýbajúca stránka sa zobrazí v angličtine. Jazykové
menu hlavičky a presmerovanie domovskej stránky podľa jazyka prehliadača pochádzajú
z `docs/_includes/`.
