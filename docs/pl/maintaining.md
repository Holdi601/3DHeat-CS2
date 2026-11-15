---
title: Utrzymanie tych stron
nav_order: 17
lang: "pl"
source: maintaining.md
source_hash: "7d48fc0b1c7e"
nav_exclude: true
search_exclude: true
---
# Utrzymanie tych stron {#maintaining-these-pages}

Lista kontrolna przy każdym wydaniu. Strony muszą mówić, co robi kod, dobrze czytać się początkującemu, ośmiolatkowi i profesjonaliście oraz istnieć w każdym języku, który obsługuje przeglądarka 3DHeat.

## Lista kontrolna wydania {#release-checklist}

1. **Wygeneruj strony generowane** z kodu:

   ```bash
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Przed zatwierdzeniem to samo z `--check` musi zakończyć się kodem 0:

   ```bash
   python tools/gen_docs_reference.py --check
   ```

2. **Porównaj funkcje od ostatniego wydania.** `VERSION` zawiera wersję; jej tag to `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Każde nowe polecenie, opcja, kolumna, wynik albo zachowanie dostaje wiersz na stronie, która je opisuje, oraz wiersz w `CHANGELOG.md` w sekcji **Docs** z nazwą tej strony.

3. **Niezależny przegląd.** Ktoś, kto nie napisał zmiany, czyta zmienione strony - razem z diagramami i obrazkami - trzy razy: jako początkujący (nigdy nie używał terminala), jako ośmiolatek (czy pierwszy akapit mówi, czym to jest i po co, prostymi słowami?) oraz jako profesjonalista (czy flagi, domyślne wartości i kolumny są dokładnie tym, co robi kod?).

4. **Popraw to, co wykazał przegląd.** Obrazki mają najwyżej około 900 px szerokości, z tekstem co najmniej 12 px, tak jak pokazano; diagramy są generowane z `tools/diagrams/*.json` przez `tools/flow2svg.py`. Przykłady używają tylko zmyślonych nazw (`de_x`, „Demo Valley”, `<mapa>`): nigdy prawdziwej mapy, gracza, identyfikatora meczu ani postaci z prawdziwych plików.

5. **Tłumaczenia.** Każda przetłumaczona strona zapisuje skrót (hash) angielskiego źródła, z którego powstała. Przetłumacz ponownie strony, których źródłowy hash angielski się zmienił, a potem niech każdy język zostanie przejrzany w tych samych trzech ujęciach (zwykłym, początkującego, profesjonalisty), łącznie z podpisami diagramów.

6. **Wypychaj tylko za zgodą właściciela.** Zatwierdzaj lokalnie; właściciel decyduje, kiedy repozytorium staje się publiczne.

## Tłumaczenia: polecenia {#translations-the-commands}

Strona jest tłumaczona na 40 języków przeglądarki 3DHeat: angielski w `docs/`, każdy inny język w `docs/<język>/`, z tymi samymi nazwami plików. `tools/docs_i18n.py` prowadzi ewidencję:

```bash
python tools/docs_i18n.py hashes             # po każdej zmianie angielskiej: zapisz hash każdej strony
python tools/docs_i18n.py svg-strings        # po każdej zmianie obrazka: podpisy do przetłumaczenia
python tools/docs_i18n.py status             # na każdy język: aktualne, nieaktualne, brakujące strony
python tools/docs_i18n.py todo --lang de     # niemieckie strony do (ponownego) przetłumaczenia
python tools/docs_i18n.py svg-build --lang de    # niemieckie obrazki z docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # oznacz niemieckie strony hashem angielskiego źródła
python tools/docs_i18n.py check              # kod 1, gdy hashe lub podpisy są nieaktualne
```

Tłumacz tylko to, co wypisuje `todo`: zachowaj Markdown, linki, kod, nazwy plików i kolumn; przetłumacz tytuły i opisy obrazków; używaj własnych słów przeglądarki 3DHeat na jej przyciski i panele (w `src/i18n/locales/<język>/`). Strony generowane z dokumentacją i obrazki z terminala zostają po angielsku. Na stronie nieaktualne tłumaczenie to mówi i odsyła do angielskiej strony; brakujące tłumaczenie przechodzi na angielski. Menu języków w nagłówku i przekierowanie strony głównej według języka przeglądarki pochodzą z `docs/_includes/`.
