---
title: Rozwój
nav_order: 15
lang: "pl"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Rozwój {#development}

## Układ {#layout}

| Ścieżka | Co to jest |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: sprawdzenie wydania, potem wiersz poleceń |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | polecenia i opcje; grupowanie plików dema w mecze; pula procesów roboczych |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | jeden plik dema przez demoparser2 do `RawPart` - [Odczyt dema](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | części, łańcuchy, zegar, rundy, drużyny, wiersze, zabójstwa, obrażenia, oślepienia - [Budowanie meczu](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | podsumowania rund, tablica wyników, dokument meczu, tekstowa tablica wyników - [Statystyki](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | tabela Parquet z jej podpowiedziami `heat3d` oraz JSON - [Tabela mapy cieplnej](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | znajdowanie CS2 i Source2Viewer, siatka kolizji w układzie widoku - [Eksport mapy](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | minimalny czytnik i zapisywacz glTF binary (bez zależności poza numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | sprawdzanie wydania i aktualizator - [Aktualizacje](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | testy i syntetyczne dema |
| `VERSION` | wersja, jedna linia |

Przepływ danych:

```text
pliki .dem --demo.read_part--> RawPart --match.chains--> [RawPart, ...] na mecz
          --match.build_match--> Match (rundy, gracze, drużyny, wiersze, zabójstwa, obrażenia, oślepienia)
          --output.write--> <mapa>/<mecz>.parquet  (output.table + HINTS)
                            <mapa>/<mecz>.match.json (stats.summary)
<mapa>.vpk --Source2Viewer CLI--> world_physics .glb --mapexport.parts_from--> glb.write
```

### Użycie z Pythona {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # tabela mapy cieplnej jako DataFrame pandas
    kills = match.kills        # jeden wiersz na śmierć, ze wszystkimi flagami
    doc = summary(match)       # dokument .match.json jako słownik
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` i `Match.blinds` to DataFrame-y pandas z większą zawartością, niż mają wyniki - pozycje atakującego i ofiary oraz miejsca przy każdym zabójstwie, obrażenia z granatów na trafienie - do własnych analiz.

## Testy {#tests}

```bash
python -m pytest
```

`pytest.ini` uruchamia `tests/` po cichu. Testy nie potrzebują dema, gry ani Source2Viewer:
[`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
buduje dema ręcznie, tak jak zrobiłby to demoparser2: dwie rundy, dwóch graczy na stronę (`ace`, `ash` z drużyny Alpha; `bob`, `ben` z Bravo), na tyle małe, że każda odpowiedź jest znana:

- Runda 1, wygrana T przez eliminację: ace zabija bob'a strzałem w głowę (otwarcie), ben zabija ace'a 1,9 s później (wymiana: śmierć bob'a jest pomszczona), ash zabija bena 3,1 s po tym - sam przeciwko jednemu, wygrany clutch.
- Runda 2, wygrana T przez bombę: ash podkłada na A, nikt nie ginie, bomba wybucha.

`fixtures.halves` buduje dłuższy mecz z pustych rund, drużyny na początkowych stronach albo zamienione, z licznikiem dogrywki gry albo bez, do długości połowy i rund pistoletowych.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
sprawdza na nim: zwycięzcę, przyczynę, wynik i strony każdej rundy; zegar startujący od meczu; ekonomię i podłożenie (jego czas w rundzie, miejsce, wybuch bomby); że strona podłożenia to zawsze litera albo pusto, nigdy numer encji; remis rozstrzygnięty bez zwycięzcy; rundy pistoletowe od miejsca zamiany stron, z pominiętą dogrywką i tylko rundą 1 bez zamiany; drużyny bez nazw klanów (`Started T` / `Started CT`); otwarcia, wymiany i flagi; samobójstwo, które nie jest teamkillem, i otwarcie przechodzące na pierwsze zabójstwo wroga; `noscope` i `attackerBlind` w tabeli i dokumencie meczu; obrażenia jako stracone zdrowie (60, potem 40 z 137 przy 40 zdrowia); liczby tablicy wyników i KAST; clutche; tekstową tablicę wyników; zdarzenia tabeli i ich miejsca (detonacja bez własnego miejsca, miejsce rzucającego w `throwerPlace`; wybuch po stronie podkładającej); że pozycje są żywe, opisane i mają wektory patrzenia o długości jednostkowej; że zapisany plik ma swoje podpowiedzi; że części są ustawiane w kolejności, czymkolwiek by się nazywały; że zrestartowany zegar serwera nadal kontynuuje; i że zduplikowane wiersze przywróconej rundy są rozstrzygane na ten, który prowadzi dalej.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py)
sprawdza, że dema w folderach są znajdowane bez względu na wielkość liter w `.dem`, oraz że mecz liczy się jako zapisany dopiero wtedy, gdy ma swoją tabelę i dokument meczu.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
sprawdza przeliczenia układu (metry Source2Viewer na cale gry, a dalej na układ widoku, obrót o wyznaczniku 1), że clipy i niebo są pomijane bez względu na wielkość liter i nazwy powierzchni, podział na podłoże i konstrukcję według normalnej oraz że `.glb` jest zapisany i odczytany z powrotem.

### Test podłogi na prawdziwej mapie {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<jakieś demo> HEAT3D_SOURCE2VIEWER=<CLI> python -m pytest
```

Gdy obie zmienne są ustawione, uruchamia się także `test_players_stand_on_the_exported_floor`: konwertuje demo, eksportuje jego mapę z zainstalowanej gry i sprawdza, czy co najmniej 98 % z 300 losowych próbek pozycji ma pod sobą podłoże, a mediana wysokości nad nim jest mniejsza niż 5 jednostek ([Eksport mapy](map-export.md#the-check-that-the-frame-is-right)).

## Konwencje kodu {#conventions-of-the-code}

- Czasy w `match.py` to sekundy meczu, z wyjątkiem `time` podłożenia: sekundy od początku jego rundy, tak jak zapisuje je dokument meczu. Ticki zamieniają się w sekundy dopiero przez `_Part.at`.
- Strony to łańcuchy `T` / `CT` wszędzie poza surowymi danymi parsera (`team_num` 2 / 3).
- Nowa kolumna tabeli idzie do `ROW_COLUMNS` (a jeśli jest liczbowa, to do `NUMERIC`) w `match.py`; `output.table` wybiera jej typ Parquet z zestawów `INT16`, `INT32`, `FLOAT64` i flag 0/1, a w przeciwnym razie float32.
- Zmiana tego, co widok ma robić z kolumną, oznacza zmianę `HINTS` w `output.py`.

## Licencja {#licence}

MIT. Pakiety zewnętrzne:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
Dema i mapy nigdy nie są częścią repozytorium; jego `.gitignore` wyklucza po typie `*.dem`, `*.parquet`, `*.match.json`, `*.glb` i podobne.
