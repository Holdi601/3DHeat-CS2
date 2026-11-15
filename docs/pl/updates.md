---
title: Aktualizacje
nav_order: 14
lang: "pl"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Aktualizacje {#updates}

3DHeat CS2 utrzymuje się w bieżącej wersji dzięki
[wydaniom na GitHubie](https://github.com/Holdi601/3DHeat-CS2/releases) tego repozytorium. Kod:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Sprawdzenie przy starcie {#the-check-at-start-up}

Każde `python -m heat3d_cs2 ...` najpierw pyta, czy nie ma nowszego wydania, zanim jeszcze odczyta swoje argumenty:

1. Zainstalowana wersja to plik `VERSION` w katalogu głównym repozytorium (`0`, jeśli nie da się go odczytać).
2. Najnowsze wydanie pytane jest pod adresem `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, z limitem czasu **5 s**. Odpowiedź jest zapamiętywana przez **6 godzin** w `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (w systemach bez `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), więc zapytanie jest wysyłane najwyżej co sześć godzin. „Nic nie wydano” (HTTP 404) jest zapamiętywane tak jak każda odpowiedź. Przy braku sieci, limicie zapytań, za proxy - każdym innym błędzie - narzędzie działa dalej z wersją, którą ma, i niczego nie zapamiętuje.
3. Wersje są porównywane jako liczby: `v1.2.3` i `1.2.3` są równe, wszystko po `-` albo `+` jest ignorowane, brakujące części liczą się jako 0.

Gdy jest nowsze wydanie, mówi o tym na strumieniu błędów:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- W terminalu (zarówno wejście, jak i strumień błędów są terminalami) pyta. Enter, `y`, `yes`, `j` albo `ja` aktualizuje; cokolwiek innego działa dalej bez zmian. Po aktualizacji **to samo polecenie uruchamia się ponownie**, na nowym kodzie.
- Bez terminala - zaplanowane uruchomienie, potok - tylko wypisuje, gdzie zaktualizować, i działa dalej: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` wyłącza sprawdzanie. Każda wartość inna niż pusta, `0`, `false` albo `no` oznacza włączone.

## Aktualizacja na żądanie {#updating-on-request}

```bash
python -m heat3d_update            # aktualizuj do najnowszego wydania
python -m heat3d_update --check    # tylko powiedz, czy jest nowe wydanie
```

To zawsze pyta GitHub (pamięć podręczna nie jest używana). Wypisuje `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.` albo
`<new> is out (this is <current>): <url>`, a potem aktualizuje (chyba że `--check`).
Kod wyjścia `1`, gdy próba aktualizacji się nie udała, `0` w pozostałych przypadkach.

## Jak stosowana jest aktualizacja {#how-an-update-is-applied}

Zależy od tego, jak kopia została zainstalowana:

- **Kopia z gita** (w katalogu głównym jest `.git` i `git` jest w `PATH`): `git pull --ff-only`. Jest odrzucana, dopóki śledzone pliki mają lokalne zmiany („this checkout has local changes; commit or stash them, then run `git pull`”): to czyjaś praca, a aktualizacja nie decyduje, co się z nią stanie. Pliki nieśledzone nie blokują.
- **Pobrana kopia**: archiwum źródeł wydania (zipball GitHuba) jest pobierane i rozpakowywane do folderu tymczasowego - wpisy, które wylądowałyby poza nim, są pomijane - a jego `VERSION` musi być wersją, którą deklaruje wydanie, albo nic się nie zmienia („the archive is version X, not Y”). Następnie jego pliki są kopiowane do folderu. Pliki, które nie są częścią wydania - twoje dema, wyniki, środowisko wirtualne, cokolwiek sam zrobiłeś - nigdy nie są ruszane. Moduły Pythona, których wydanie już nie ma, są usuwane z pakietów narzędzia (foldery `heat3d_*`), żeby stary moduł nie przesłonił swojego następcy.

Gdy aktualizacja się nie uda, komunikat jest wypisywany, a narzędzie działa na wersji, którą ma.
