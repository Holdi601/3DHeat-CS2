---
title: "Sivujen ylläpito"
nav_order: 17
lang: "fi"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Näiden sivujen ylläpito {#maintaining-these-pages}

Jokaisen julkaisun tarkistuslista. Sivujen pitää kertoa, mitä koodi tekee, olla
luettavia aloittelijalle, kahdeksanvuotiaalle ja ammattilaiselle, ja olla olemassa
jokaisella kielellä, jota 3DHeat-katselin tukee.

## Julkaisun tarkistuslista {#release-checklist}

1. **Luo generoidut sivut uudelleen** koodista:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Ennen commitointia sama `--check`-valinnalla täytyy päättyä koodilla 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Vertaa ominaisuuksia edelliseen julkaisuun.** `VERSION` pitää versiota; sen tagi on `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Jokaiselle uudelle komennolle, valinnalle, sarakkeelle, tulosteelle tai toiminnalle
   tulee rivi sivulle, joka sen kattaa, ja rivi tiedostoon `CHANGELOG.md` kohtaan **Docs**,
   jossa nimetään tuo sivu.

3. **Riippumaton tarkistus.** Joku, joka ei kirjoittanut muutosta, lukee muutetut sivut
   kolme kertaa - kaaviot ja kuvat mukaan lukien: aloittelijana (ei ole koskaan käyttänyt
   terminaalia), kahdeksanvuotiaana (sanooko ensimmäinen kappale, mitä se on ja miksi,
   selkeillä sanoilla?) ja ammattilaisena (ovatko liput, oletukset ja sarakkeet täsmälleen
   sitä, mitä koodi tekee?).

4. **Korjaa, mitä tarkistus löysi.** Kuvat pysyvät noin 900 px leveinä, tekstin koko vähintään
   12 px kuten näytetty; kaaviot generoidaan tiedostoista `tools/diagrams/*.json` työkalulla
   `tools/flow2svg.py`. Esimerkeissä käytetään vain keksittyjä nimiä (`de_x`, "Demo Valley",
   `<map>`): ei koskaan oikeaa karttaa, pelaajaa, ottelutunnusta tai hahmoa oikeista tiedostoista.

5. **Käännökset.** Jokainen käännetty sivu tallentaa sen englanninkielisen lähdesivun
   tiivisteen, josta se tehtiin. Käännä uudelleen ne sivut, joiden englanninkielisen lähteen
   tiiviste on muuttunut, ja anna jokaisen kielen tarkistaa samoin kolmella tavalla (selkeä,
   aloittelija, ammattilainen), kaaviotarrat mukaan lukien.

6. **Työnnä vain omistajan luvalla.** Tee commit paikallisesti; omistaja päättää, milloin
   se julkaistaan.

## Käännökset: komennot {#translations-the-commands}

Sivusto on käännetty 3DHeat-katselimen 40 kielelle: englanti kansiossa `docs/`, kukin muu
kieli kansiossa `docs/<lang>/` samoilla tiedostonimillä. `tools/docs_i18n.py` hoitaa kirjanpidon:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Käännä vain se, minkä `todo` listaa: säilytä Markdown, linkit, koodi sekä tiedosto- ja
sarakenimet sellaisinaan, käännä otsikot ja kuvien selitteet, ja käytä 3DHeat-katselimen
omia sanoja sen painikkeille ja paneeleille (sen `src/i18n/locales/<lang>/`). Generoidut
viiteaivot ja terminaalikuvat pysyvät englanniksi. Sivustolla vanhentunut käännös kertoo
sen ja linkittää englanninkieliseen sivuun; puuttuva käännös näyttää englanniksi. Kielivalikko
otsikossa ja selaimen kielen mukainen uudelleenohjaus etusivulla tulevat kansiosta `docs/_includes/`.
