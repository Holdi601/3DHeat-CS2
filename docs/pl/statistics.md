---
title: Statystyki
nav_order: 7
lang: "pl"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statystyki {#statistics}

Co zrobił każdy gracz w meczu i jak przebiegała każda runda: tablica wyników i lista rund [dokumentu meczu](output-match-json.md). Kod:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Wszystko liczy się z meczu zbudowanego tak, jak opisano w [Budowanie meczu](building-matches.md): z jego rekordów zabójstw, obrażeń (stracone zdrowie, tylko wrogowie), oślepień (tylko wrogowie) i wierszy.

![tekstowa tablica wyników syntetycznego meczu](../assets/img/scoreboard.svg)

## Konwencje {#the-conventions}

Tam, gdzie sama gra nie definiuje liczby, obowiązują te definicje. Są też zapisane w każdym dokumencie meczu, w polu `conventions`.

| Pojęcie | Definicja |
|---|---|
| **Trade** (wymiana) | Śmierć jest *wymieniona* (traded), gdy jej zabójca zostaje zabity przez jednego z kolegów ofiary w ciągu **5 s**; to zabójstwo to *zabójstwo wymiany* (trade kill). |
| **Opening** (otwarcie) | Pierwsze zabójstwo wroga w rundzie, gdy jest ona żywa. Teamkill, samobójstwo albo śmierć od świata przed nim są pomijane. |
| **KAST** | Udział rund, w których gracz miał **K**ill (zabójstwo), **A**ssist (asystę, także asystę z błysku), **S**urvived (przetrwał) albo został **T**raded (jego śmierć została pomszczona). |
| **Damage** (obrażenia) | Zdrowie faktycznie stracone, tylko wrogowie: strzał w głowę za 137 obrażeń w graczu z 40 zdrowia to 40. |
| **Clutch** | Bycie ostatnim żywym graczem swojej strony, gdy wrogowie wciąż żyją; wygrany, gdy strona wygrywa rundę. |
| **Buy** (zakup) | Dla każdej strony, ze średniej wartości wyposażenia na końcu czasu zamrożenia: pierwsza runda każdej regulaminowej połowy to runda pistoletowa (runda 1 i runda po połowie, o ile mecz ją rozegrał); dogrywka nie ma jej wcale; potem poniżej 1500 $ eco, poniżej 4000 $ force, w przeciwnym razie full. |

## Kto zaczął każdą rundę {#who-started-each-round}

Kilka liczb wymaga wiedzy, kto grał rundę. **Gracze startowi** rundy to, dla każdej strony, każdy gracz z żywym wierszem pozycji w ciągu sekundy od najwcześniejszej pozycji tej rundy (czyli w pierwszej sekundzie po końcu czasu zamrożenia). **Rozegrane rundy** gracza to liczba rund, które zaczął. Jeśli gracz nie zaczął żadnej (nigdy nie miał takiego wiersza), używana jest zamiast tego liczba rund meczu, żeby nie dzielić przez zero.

## Wiersz tablicy wyników {#the-scoreboard-line}

Jeden wpis na gracza (zob. [dokument meczu](output-match-json.md#players) po nazwy pól). „Zabójstwo wroga” poniżej oznacza zabójstwo z atakującym, nie teamkill i nie samobójstwo (własna śmierć).

| Pole | Liczy |
|---|---|
| `kills` | zabójstwa wrogów, z fazy żywej i po |
| `deaths` | każda śmierć: przez wrogów, kolegów, siebie albo świat |
| `assists` | zabójstwa wrogów, którym ten gracz asystował bez błysku (asystujący nie może być zabójcą) |
| `flashAssists` | zabójstwa wrogów, którym ten gracz asystował błyskiem |
| `diff` | zabójstwa - śmierci |
| `adr` | obrażenia (stracone zdrowie, tylko wrogowie, obie fazy) / rozegrane rundy, z jednym miejscem po przecinku |
| `kast` | 100 x (rundy z zabójstwem, asystą lub asystą z błysku, przetrwaniem albo wymienioną śmiercią) / rozegrane rundy, z jednym miejscem po przecinku. *Przetrwanie* to: gracz startowy rundy, który w niej nie zginął, w żadnej fazie. |
| `headshotPct` | 100 x zabójstwa w głowę / zabójstwa, z jednym miejscem po przecinku; 0 bez zabójstw |
| `openingKills`, `openingDeaths` | wygrane i przegrane pojedynki otwierające |
| `tradeKills` | zabójstwa, które wymieniły śmierć kolegi |
| `tradedDeaths` | śmierci, które zostały wymienione |
| `multiKills` | rundy z 2, 3, 4 i 5 zabójstwami wrogów (`2k`, `3k`, `4k`, `5k`); więcej niż pięć liczy się jako `5k`. Liczą się obie fazy. |
| `clutches`, `clutchesWon` | rozegrane i wygrane clutche (poniżej) |
| `utilityDamage` | obrażenia zadane granatami HE, molotovami i zapalającymi, z jednym miejscem po przecinku |
| `enemiesFlashed` | wrogowie oślepieni przez błyski tego gracza co najmniej na **1,0 s** |
| `plants`, `defuses` | podłożenia i rozbrojenia bomby (wiersze tabeli) |
| `teamkills` | zabici koledzy. Samobójstwo - atakujący i ofiara to ten sam gracz, np. własny granat - nie jest nim: to tylko śmierć. |
| `roundsPlayed` | rozpoczęte rundy, jak wyżej |

Gracze są wymienieni według nazwy drużyny (alfabetycznie), a w drużynie według `diff`, potem według `kills`, od najlepszego.

Uwagi o brzegach:

- Zabójstwo w fazie po - zwycięzcy polujący na oszczędzającego się gracza - liczy się jako zabójstwo, śmierć, dla ADR, wielu zabójstw i KAST, tak jak każde inne.
- Wallbangi są liczone dla każdego gracza wewnętrznie, ale nie są zapisywane w dokumencie meczu; każde zabójstwo na liście rund mówi, czy było wallbangiem.
- Część *wymieniona* w KAST zalicza ofierze wymienionej śmierci w tej rundzie.
- Teamkille i samobójstwa dodają śmierć ofierze, ale nikomu nie dodają zabójstwa; teamkill dodaje do `teamkills` zabójcy, a samobójstwo do niczego innego.

## Clutche {#clutches}

Dla każdej rundy gracze startowi obu stron są traktowani jako żywi, a żywe zabójstwa rundy są przechodzone po kolei. Po każdej śmierci ofiara jest usuwana i sprawdzana jest każda strona: strona, na której został dokładnie **jeden** gracz, a co najmniej jeden wróg wciąż żyje, daje clutch temu graczowi **przeciwko** liczbie wrogów żyjących w tym momencie. Każdy gracz ma co najwyżej jeden clutch w rundzie; jest **wygrany**, gdy strona tego gracza wygrała rundę.

Konsekwencje tej definicji:

- Obie strony mogą mieć clutch w jednej rundzie. Jeśli jedna strona spadnie najpierw do jednego (np. 1v3), a potem druga strona też zostanie sprowadzona do jednego, drugi gracz ma własny clutch 1v1.
- `against` to liczba w chwili, gdy gracz został ostatnim, a nie na końcu.
- Zabójstwa fazy po nie są przechodzone, więc ani nie zaczynają clutcha, ani go nie zmieniają.

## Ocaleli {#survivors}

**Ocaleli** rundy to, dla każdej strony, jej gracze startowi minus wszyscy, którzy zginęli, gdy runda była żywa. Gracz zabity w fazie po podczas oszczędzania wciąż jest ocalałym na liście rund - ale nie *przetrwał* dla KAST.

## Lista rund {#the-round-list}

Każda runda w dokumencie meczu niesie swój wynik, wynik punktowy, strony, ekonomię, podłożenie, ocalałych, clutche i zabójstwa po kolei; zob.
[Dokument meczu](output-match-json.md#rounds).

## Tekstowa tablica wyników {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <mecz.json>` wypisuje te liczby dla każdej drużyny; zob.
[Polecenia](commands.md#scoreboard---a-match-as-text).
