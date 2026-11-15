---
title: Održavanje
nav_order: 17
lang: "bs"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Održavanje ovih stranica {#maintaining-these-pages}

Kontrolna lista za svako izdanje. Stranice moraju govoriti šta kod radi, čitati se dobro za početnika,
osmogodišnjaka i profesionalca, i postojati na svakom jeziku koji preglednik 3DHeat podržava.

## Kontrolna lista izdanja {#release-checklist}

1. **Ponovo generirajte generirane stranice** iz koda:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Prije commita, isto s `--check` mora izaći s 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Usporedite mogućnosti od zadnjeg izdanja.** `VERSION` drži verziju; njen tag je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Svaka nova komanda, opcija, kolona, izlaz ili ponašanje dobija red na stranici koja ga pokriva, i
   red u `CHANGELOG.md` pod **Docs** koji imenuje tu stranicu.

3. **Nezavisan pregled.** Neko ko nije napisao promjenu čita izmijenjene stranice - uključujući dijagrame i
   slike - tri puta: kao početnik (nikad nije koristio terminal), kao osmogodišnjak (govori li
   prvi odlomak šta je to i zašto, jednostavnim riječima?) i kao profesionalac (jesu li zastavice, zadane vrijednosti i
   kolone tačno ono što kod radi?).

4. **Popravite ono što je pregled našao.** Slike ostaju najviše oko 900 px široke s tekstom od najmanje 12 px
   kako se prikazuju; dijagrami se generišu iz `tools/diagrams/*.json` pomoću `tools/flow2svg.py`. Primjeri koriste
   samo izmišljena imena (`de_x`, "Demo Valley", `<map>`): nikad stvarnu mapu, igrača, id meča ili broj
   iz stvarnih datoteka.

5. **Prijevodi.** Svaka prevedena stranica bilježi hash engleskog izvora iz kojeg je napravljena.
   Ponovo prevedi stranice čiji se hash engleskog izvora promijenio, zatim svaki jezik pregledaj na isti
   tri načina (jednostavno, početnik, profesionalac), uključujući oznake dijagrama.

6. **Šaljite tek nakon odobrenja vlasnika.** Napravite commit lokalno; vlasnik odlučuje kad ide javno.

## Prijevodi: komande {#translations-the-commands}

Sajt je preveden na 40 jezika preglednika 3DHeat: engleski u `docs/`, svaki drugi
jezik u `docs/<lang>/` s istim imenima datoteka. `tools/docs_i18n.py` vodi evidenciju:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prevodi samo ono što `todo` navodi: Markdown, linkove, kod, imena datoteka i kolona ostavite kakvi jesu,
prevedite naslove i opise slika, a za dugmad i panele koristite vlastite riječi preglednika 3DHeat
(njegov `src/i18n/locales/<lang>/`). Generisane referentne stranice i slike terminala ostaju
engleske. Na sajtu zastarjeli prijevod to kaže i povezuje englesku stranicu; prijevod koji nedostaje
vraća se na engleski. Jezični meni u zaglavlju i preusmjeravanje početne stranice na jezik preglednika
dolaze iz `docs/_includes/`.
