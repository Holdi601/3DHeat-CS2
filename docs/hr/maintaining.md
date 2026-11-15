---
title: "Održavanje ovih stranica"
nav_order: 17
lang: "hr"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Održavanje ovih stranica {#maintaining-these-pages}

Popis za svako izdanje. Stranice moraju reći što kod radi, dobro se čitati za početnika, za osmogodišnjaka i za stručnjaka, i postojati na svakom jeziku koji podržava preglednik 3DHeat.

## Popis za izdanje {#release-checklist}

1. **Ponovno generirajte generirane stranice** iz koda:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Prije commita, isto s `--check` mora završiti s 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Usporedite značajke od zadnjeg izdanja.** `VERSION` drži verziju; njezina oznaka je `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Svaka nova naredba, opcija, stupac, izlaz ili ponašanje dobiva redak na stranici koja ga pokriva, i redak u `CHANGELOG.md` pod **Docs** koji imenuje tu stranicu.

3. **Neovisni pregled.** Netko tko nije napisao promjenu čita promijenjene stranice - uključujući dijagrame i slike - triput: kao početnik (nikad nije koristio Terminal), kao osmogodišnjak (kaže li prvi odlomak jasno što je i zašto, običnim riječima?) i kao stručnjak (odgovaraju li zastavice, zadane vrijednosti i stupci točno onome što kod radi).

4. **Popravite što je pregled našao.** Slike ostaju široke najviše oko 900 px s tekstom od barem 12 px kako je prikazan; dijagrami se generiraju iz `tools/diagrams/*.json` pomoću `tools/flow2svg.py`. Primjeri koriste samo izmišljena imena (`de_x`, "Demo Valley", `<karta>`): nikad pravu kartu, igrača, ID meča ili lik iz stvarnih datoteka.

5. **Prijevodi.** Svaka prevedena stranica bilježi hash engleskog izvora iz kojeg je nastala. Ponovno prevedite stranice čiji se hash engleskog izvora promijenio, pa neka svaki jezik pregleda na isti triput način (običan, početnički, stručni), uključujući oznake dijagrama.

6. **Objavljujte tek nakon vlasnikova odobrenja.** Commitajte lokalno; vlasnik odlučuje kada ide javno.

## Prijevodi: naredbe {#translations-the-commands}

Stranica se prevodi na 40 jezika koje podržava preglednik 3DHeat: engleski je u `docs/`, svaki drugi jezik u `docs/<jezik>/` s istim imenima datoteka. `tools/docs_i18n.py` vodi evidenciju:

```bash
python tools/docs_i18n.py hashes             # nakon svake promjene engleskog: zabilježi hash svake stranice
python tools/docs_i18n.py svg-strings        # nakon svake promjene slika: oznake za prijevod
python tools/docs_i18n.py status             # po jeziku: aktualne, zastarjele i nedostajuće stranice
python tools/docs_i18n.py todo --lang de     # njemačke stranice za (ponovni) prijevod
python tools/docs_i18n.py svg-build --lang de    # njemačke slike iz docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # označi njemačke stranice hashom engleskog izvora
python tools/docs_i18n.py check              # izlazni kod 1 kad su hashevi ili oznake zastarjeli
```

Prevodite samo ono što `todo` navodi: zadržite Markdown, poveznice, kod, imena datoteka i stupaca kakvi jesu; prevedite naslove i opise slika; i koristite vlastite riječi preglednika 3DHeat za njegove gumbe i panele (`src/i18n/locales/<jezik>/`). Generirane referentne stranice i slike terminala ostaju na engleskom. Na stranici zastarjeli prijevod to kaže i povezuje englesku stranicu; nedostajući prijevod se vraća na engleski. Izbornik jezika u zaglavlju i preusmjeravanje početne stranice prema jeziku pregledniku dolaze iz `docs/_includes/`.
