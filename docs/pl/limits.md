---
title: Ograniczenia
nav_order: 13
lang: "pl"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Ograniczenia {#limits}

Co konwerter zakłada, czego nie obsługuje i czego nie sprawdzono. Każdy punkt pochodzi z kodu w jego obecnym stanie.

## Co czyta {#what-it-reads}

- **Tylko nieskompresowane pliki `.dem`.** `.dem.zst`, `.dem.bz2`, `.rar` i `.zip` trzeba najpierw rozpakować. Rozszerzenie jest dopasowywane bez względu na wielkość liter (`.dem`, `.DEM`), w folderach tak samo jak w plikach podanych z nazwy.
- **Mecze z rozbrajaniem bomby.** Końcowe przyczyny rund, podłożenie i strona bomby, typy zakupu i rundy pistoletowe to te z trybu rozbrajania bomby. Mapy z zakładnikami, Wingman i inne tryby nie są obsługiwane w sposób szczególny i nie są sprawdzone.
- **Zakładane jest 64 ticki na sekundę** (`TICKRATE = 64`) dla każdego czasu wyliczanego z ticków; serwery CS2 działają w 64.
- **Zakładane jest dema z serwera** (SourceTV): ma ono wszystkich graczy. Nagranie po stronie klienta (dema POV) nie zostało wypróbowane.

## Mecze i rundy {#matches-and-rounds}

- **Pliki są grupowane po nazwie.** Części jednego meczu muszą mieć wspólną nazwę, nie licząc sufiksu `-pN` / `_pN`. Pliki jednego meczu o niepowiązanych nazwach stają się osobnymi meczami, a pliki o tej samej nazwie w różnych folderach są grupowane razem (a potem dzielone na łańcuchy, jeśli nie kontynuują jednego po drugim).
- **Żywy mecz zaczyna się od ostatniego `round_announce_match_start`** w pliku. Runda na noże, po której nie następuje to ogłoszenie, jest liczona jako runda.
- **Czasy końca rund są dokładne co do jednej próbki** (`--every` ticków, domyślnie 1/8 s), bo rozstrzygnięcie odczytywane jest z próbkowanego stanu gry. Bardzo duże `--every` może przegapić krótkie okno między końcem rundy a początkiem następnej i zostawić rundę jako niekompletną.
- **Remisy.** Runda zremisowana (status wygranej 1, przyczyna 10) jest rozstrzygnięta bez zwycięzcy: `winner` jest puste i żadna strona jej nie wygrała. W prawdziwym demie nie spotkano remisu, do którego można by to porównać; sprawdzono to na syntetycznym.
- **Rundy przerwane** końcem pliku są pomijane (`incomplete`), a nie zgadywane; rundy przed pierwszą w plikach są wypisane jako `missing`.
- **Rundy pistoletowe** podążają za długością połowy, jaką pokazuje nagranie: tam, gdzie strony po raz pierwszy się zamieniają między dwiema kolejnymi regulaminowymi rundami. Nagranie, które nie pokazuje tej zamiany (zaczyna się po przerwie, kończy przed nią albo brakuje rundy po którejś stronie), zna tylko rundę 1 jako rundę pistoletową. Dogrywka nie ma rund pistoletowych.
- **Drużyny.** Drużyna to nazwa klanu widziana najczęściej u jej graczy. Bez nazw klanów drużyny to `Started T` i `Started CT`. Gracz, który w trakcie meczu zmienia drużynę, zachowuje jedną drużynę.

## Zdarzenia {#events}

- **Czytane jest wszystko, co oferuje parser**, z wyjątkami: prędkość graczy (parser wylicza ją z pozycji; nie ma jej w demie), głos (dźwięk, `parse_voice`) oraz `weapon_fire` bomby (początek podłożenia, który ma `bomb_beginplant`). Trajektorie granatów są zachowywane w próbkowaniu graczy (`--every`) i w miejscu, gdzie każdy granat się zatrzymał, a nie w każdym ticku.
- **Wiersze poza rundą** (rozgrzewka, pauza między startem meczu a pierwszym czasem zamrożenia dłuższą niż dwie minuty) są pomijane w tabeli; zdarzenia, które nie dotyczą żadnego gracza, są w całości w `events` dokumentu meczu.
- **Wiersze detonacji** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nie mają `place`: dema podają miejsca dla graczy, nie dla granatów. Miejsce rzucającego w tym momencie jest w `throwerPlace`.
- **Strona podłożenia** pochodzi ze strefy bomby, w której według gry stał podkładający, albo z nazwy miejsca podkładającego, albo z innego podłożenia w tej samej strefie w tym samym pliku. Gdy żadne z tych nie wskazuje, `site` jest puste.
- **Śmierć od świata** (upadek, bomba) nie ma atakującego: nie ma zabójstwa, teamkilla ani otwarcia; jest tylko śmiercią.

## Statystyki {#statistics}

- **Rozegrane rundy** wynikają z tego, kto miał pozycję w pierwszej sekundzie po końcu czasu zamrożenia. Gracz, który dołącza później w rundzie, nie liczy się jako grający w niej (jego zabójstwa nadal się liczą).
- **Przetrwanie dla KAST**: gracz zabity w fazie po nie przetrwał dla KAST, mimo że lista rund wciąż wymienia go wśród ocalałych.
- **Obaj gracze w 1v1** mogą dostać clutcha w jednej rundzie; zobacz [Statystyki](statistics.md#clutches).
- **Obrażenia z granatów** to granaty HE, molotovy i zapalające; zabójstwo albo trafienie rzuconym błyskiem lub dekoyem nie są obrażeniami z granatów.

## Eksport mapy {#map-export}

- Wymaga zainstalowanej gry (albo pliku `.vpk`) i wiersza poleceń Source2Viewer; nic nie jest pobierane.
- Eksportuje tylko `world_physics`; clipy i niebo są pomijane po nazwach zawierających `clip` lub `sky`, bez względu na wielkość liter.
- Podłoże jest odróżniane od konstrukcji tylko po normalnej ściany (składowa Z 0,7 lub więcej), więc stroma rampa to konstrukcja, a płaski dach to podłoże.
- Plik jest w calach, a nie w metrach.

## Pamięć i czas {#memory-and-time}

- Mecz jest trzymany w pamięci w całości podczas budowania, w jednym procesie roboczym na mecz. Przy wielu procesach i małym `--every` pamięć się sumuje: zmniejsz `--jobs`, jeśli maszynie brakuje pamięci.
- Mecz jest zapisywany dopiero po zbudowaniu: najpierw `.parquet`, potem `.match.json`. Przebieg przerwany pomiędzy zostawia tabelę bez dokumentu meczu; mecz liczy się jako zapisany tylko z obiema częściami, więc następny przebieg konwertuje go ponownie. Mecze jeszcze nie rozpoczęte są po prostu podejmowane przez następny przebieg.
