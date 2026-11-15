---
title: Správa těchto stránek
nav_order: 17
lang: "cs"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Správa těchto stránek {#maintaining-these-pages}

Kontrolní seznam pro každé vydání. Stránky musí říkat, co kód dělá, číst se
dobře pro začátečníka, osmileté dítě i profesionála, a existovat v každém
jazyce, který prohlížeč 3DHeat podporuje.

## Kontrolní seznam vydání {#release-checklist}

1. **Znovu vygenerujte vygenerované stránky** z kódu:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Před zápisem do repozitáře musí totéž s `--check` skončit s kódem 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Porovnejte funkce od posledního vydání.** `VERSION` drží verzi; její značka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Každý nový příkaz, volba, sloupec, výstup nebo chování dostane řádek na
   stránce, která ho pokrývá, a řádek v `CHANGELOG.md` pod **Docs** s názvem
   stránky.

3. **Nezávislá kontrola.** Někdo, kdo změnu nenapsal, přečte změněné stránky -
   včetně diagramů a obrázků - třikrát: jako začátečník (nikdy nepoužil
   terminál), jako osmileté dítě (říká první odstavec, co to je a proč, prostými
   slovy?) a jako profesionál (jsou příznaky, výchozí hodnoty a sloupce přesně
   tím, co kód dělá?).

4. **Opravte, co kontrola našla.** Obrázky zůstávají nejvýš zhruba 900 px široké
   s textem alespoň 12 px, jak je zobrazeno; diagramy se generují z
   `tools/diagrams/*.json` nástrojem `tools/flow2svg.py`. Příklady používají jen
   vymyšlená jména (`de_x`, „Demo Valley“, `<map>`): nikdy skutečnou mapu, hráče,
   id zápasu nebo postavu ze skutečných souborů.

5. **Překlady.** Každá přeložená stránka zaznamenává hash anglického zdroje, ze
   kterého vznikla. Znovu přeložte stránky, jejichž hash anglického zdroje se
   změnil, a nechte každý jazyk zkontrolovat stejnými třemi způsoby (prostě,
   pro začátečníka, pro profesionála), včetně popisků diagramů.

6. **Zveřejnit jen se souhlasem vlastníka.** Potvrďte místně; vlastník rozhodne,
   kdy se to zveřejní.

## Překlady: příkazy {#translations-the-commands}

Stránky se překládají do 40 jazyků prohlížeče 3DHeat: angličtina je v `docs/`,
každý další jazyk v `docs/<lang>/` se stejnými názvy souborů. `tools/docs_i18n.py`
vede evidenci:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Překládejte jen to, co `todo` uvádí: markdown, odkazy, kód, názvy souborů a
sloupců ponechte beze změny, přeložte nadpisy a popisy obrázků a pro tlačítka a
panely prohlížeče 3DHeat používejte jeho vlastní slova (jeho
`src/i18n/locales/<lang>/`). Vygenerované referenční stránky a obrázky terminálu
zůstávají anglicky. Na webu zastaralý překlad to řekne a odkáže na anglickou
stránku; chybějící se nahradí angličtinou. Jazykové menu v záhlaví a přesměrování
domovské stránky podle jazyka prohlížeče pocházejí z `docs/_includes/`.
