---
title: Dokument meczu
nav_order: 9
lang: "pl"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Dokument meczu (`<mecz>.match.json`) {#the-match-document-matchjson}

Jeden dokument JSON na mecz, obok jego tabeli: drużyny, wynik, każda runda z jej wynikiem, ekonomia, podłożenie, zabójstwa, clutche i ocaleli oraz wiersz tablicy wyników każdego gracza. To ten dokument ładuje karta Mecz przeglądarki 3DHeat.
Kod: `summary()` w
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
liczby są zdefiniowane na stronie [Statystyki](statistics.md).

Plik jest w UTF-8, z wcięciem jedną spacją, i zachowuje znaki spoza ASCII (nazwy graczy i drużyn) bez zmian. Czasy są w sekundach, zaokrąglone do trzech miejsc po przecinku dla rund oraz do dwóch dla zabójstw i podłożenia.

## Dokument {#the-document}

| Pole | Typ | Co to jest |
|---|---|---|
| `format` | tekst | zawsze `heat3d-cs2-match` - po tym czytnik rozpoznaje plik |
| `version` | liczba | `3`. Dokument w wersji 1 podaje `time` podłożenia w sekundach meczu; od wersji 2 to sekundy od początku rundy, jak przy zabójstwie. Wersja 3 dodaje pola od `header` wzwyż oraz czas zamrożenia do tabeli. |
| `match` | tekst | nazwa meczu, tak jak nazywają się pliki |
| `map` | tekst | mapa (`de_x`) |
| `demos` | tablica tekstów | pliki dem, z których zbudowano mecz, same nazwy plików, w kolejności meczu |
| `teams` | tablica tekstów | nazwy drużyn w kolejności pojawiania się (runda 1: najpierw strona T) |
| `score` | obiekt | nazwa drużyny -> wygrane rundy: wynik z ostatniej rundy |
| `rounds` | tablica obiektów | każda kompletna runda, po kolei - [poniżej](#rounds) |
| `incomplete` | tablica liczb | numery rund przerwanych końcem dema i pominiętych |
| `missing` | tablica liczb | numery rund przed pierwszą, którą mają dema: `[1, 2]`, gdy nagranie zaczyna się od rundy 3 |
| `halfLength` | liczba albo null | liczba rund w regulaminowej połowie, od miejsca, w którym strony po raz pierwszy się zamieniają (`12` w formacie 24 rund); null, gdy nagranie nie pokazuje zamiany |
| `pistolRounds` | tablica liczb | rundy pistoletowe, według których liczony jest `buy`: runda 1 i runda po połowie, gdy `halfLength` jest znane; nigdy runda dogrywki |
| `players` | tablica obiektów | tablica wyników - [poniżej](#players) |
| `conventions` | obiekt | definicje stojące za liczbami, [poniżej](#conventions) |
| `header` | obiekt | nagłówek pierwszego dema tak, jak podaje go parser: nazwa serwera, wersja łatki, wersja dema, mapa |
| `profiles` | obiekt | Steam ID -> to, co u gracza nie zmienia się przez cały mecz: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (ostatnio widziany) |
| `playerInfo` | tablica obiektów | każdy gracz wymieniony w demach, także trenerzy i komentatorzy: Steam ID, nazwa, numer drużyny |
| `skins`, `itemDrops` | tablica obiektów | skórki broni i upuszczone przedmioty, gdy dema je mają (dema turniejowe z transmisji ich nie mają) |
| `chat` | tablica obiektów | każda linia czatu w meczu: czas, runda, gracz, strona, tekst |
| `events` | tablica obiektów | każde zdarzenie gry, które nie dotyczy żadnego gracza, w kolejności czasu, ze wszystkimi polami: sygnały i fazy rund, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (ustawienia serwera w miarę ich zmian), ujęcia kamery reżysera transmisji, `cs_win_panel_match` i inne |
| `state` | tablica obiektów | stan gry tam, gdzie się zmienił: czas, pole, wartość - przerwy (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, żywi gracze, `match_start_time` i `round_start_time` serwera |
| `selfCheck` | obiekt | `completeness`: dokąd trafiło wszystko z dema - dla każdej nazwy zdarzenia, klasy właściwości, wiadomości sieciowej, klatki i tablicy łańcuchów liczby `seen`, `decoded`, `partial`, `raw` i `lost`, zapisane pliki pomocnicze, łączna liczba `lost` (0, chyba że `--no-bulk`), właściwości, które parser wymienia, ale nie potrafi odczytać (`unreadProps`). Zasada: [Konwertery zachowują wszystko](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); pliki pomocnicze: sekcja Kompletność w README |

## Rundy {#rounds}

| Pole | Typ | Co to jest |
|---|---|---|
| `number` | liczba | runda, liczona od 1 |
| `start` | liczba | sekundy meczu, gdy skończył się czas zamrożenia |
| `end` | liczba | sekundy meczu, gdy runda została rozstrzygnięta |
| `until` | liczba | sekundy meczu, gdy zaczęła się następna runda (koniec fazy po) |
| `winner` | tekst | `T` albo `CT`; pusty przy remisie |
| `winnerTeam` | tekst | nazwa drużyny zwycięskiej strony; pusta przy remisie |
| `reason` | tekst | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` albo `other` |
| `score` | obiekt | nazwa drużyny -> rundy wygrane po tej rundzie |
| `sides` | obiekt | nazwa drużyny -> `T` / `CT` w tej rundzie |
| `equipment` | obiekt | strona -> łączna wartość wyposażenia jej żywych graczy na końcu czasu zamrożenia, w dolarach |
| `buy` | obiekt | strona -> `pistol`, `eco`, `force` albo `full` |
| `plant` | obiekt albo null | podłożenie bomby: `site` (`A` lub `B`; puste, gdy dema tego nie mówią), `time` (sekundy **od początku rundy**, jak przy zabójstwie), `player`, `steamid`, `x`, `y`, `z` (jednostki gry), `place` (nazwa miejsca podkładającego: gdzie leżała bomba) |
| `survivors` | obiekt | strona -> nazwy graczy startowych, którzy wciąż żyli, gdy runda została rozstrzygnięta, posortowane |
| `clutches` | tablica obiektów | każdy: `player`, `steamid`, `side`, `against` (wrogowie żyjący, gdy gracz został ostatni), `won` |
| `kills` | tablica obiektów | każda śmierć w rundzie, po kolei - poniżej |

Jak to jest wyliczane: [Budowanie meczu](building-matches.md#rounds);
clutche i ocaleli: [Statystyki](statistics.md#clutches).

### Zabójstwa w rundzie {#a-rounds-kills}

Każda śmierć w rundzie, także w fazie po:

| Pole | Typ | Co to jest |
|---|---|---|
| `time` | liczba | sekundy **od początku rundy** (od końca czasu zamrożenia) |
| `attacker`, `attackerSide` | tekst | zabójca i jego strona; pusty dla świata |
| `victim`, `victimSide` | tekst | ofiara i jej strona |
| `assister` | tekst albo null | gracz, który asystował, albo null |
| `flashAssist` | bool | asysta była błyskiem |
| `weapon` | tekst | tak, jak nazywa ją gra |
| `headshot` | bool | |
| `wallbang` | bool | kula przeszła przez coś |
| `throughSmoke` | bool | zabójstwo przez dym |
| `noscope` | bool | broń z celownikiem wystrzelona bez celowania |
| `attackerBlind` | bool | zabójca był oślepiony |
| `opening` | bool | pierwsze zabójstwo wroga w rundzie |
| `traded` | bool | ta śmierć została pomszczona w ciągu 5 s |
| `trade` | bool | to zabójstwo pomściło kolegę w ciągu 5 s |
| `teamkill` | bool | atakujący i ofiara po tej samej stronie, dwaj różni gracze |
| `suicide` | bool | atakujący i ofiara to ten sam gracz (np. własny granat); nie teamkill |
| `after` | bool | zabójstwo nastąpiło po rozstrzygnięciu rundy |
| `place` | tekst | gdzie była **ofiara** (nazwa miejsca na mapie) |

## Gracze {#players}

Jeden wpis na gracza, pogrupowany według nazwy drużyny, a w drużynie od najlepszego według zabójstw minus śmierci, potem zabójstw:

| Pole | Typ | Co to jest |
|---|---|---|
| `name`, `steamid`, `team` | tekst | kto |
| `kills`, `deaths` | liczba | |
| `assists`, `flashAssists` | liczba | asysty bez błysku i z błyskiem |
| `diff` | liczba | zabójstwa - śmierci |
| `adr` | liczba | średnie obrażenia na rozegraną rundę, stracone zdrowie |
| `kast` | liczba | procent rozegranych rund z zabójstwem, asystą, przetrwaniem albo pomszczoną śmiercią |
| `headshotPct` | liczba | procent zabójstw, które były strzałami w głowę |
| `openingKills`, `openingDeaths` | liczba | wygrane i przegrane pojedynki otwierające |
| `tradeKills`, `tradedDeaths` | liczba | zabójstwa wymiany; śmierci, które zostały pomszczone |
| `multiKills` | obiekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: rundy z tyloma zabójstwami |
| `clutches`, `clutchesWon` | liczba | |
| `utilityDamage` | liczba | obrażenia z HE, molotova, zapalającego |
| `enemiesFlashed` | liczba | wrogowie oślepieni co najmniej na 1 s |
| `plants`, `defuses` | liczba | |
| `teamkills` | liczba | zabici koledzy; samobójstwa się nie liczą |
| `roundsPlayed` | liczba | rozpoczęte rundy |

Każda definicja: [Statystyki](statistics.md#the-scoreboard-line).

## Konwencje {#conventions}

Zapisywane w każdym dokumencie, żeby czytelnik wiedział, co znaczą liczby, bez tej strony:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Przykład {#an-example}

Z syntetycznego dwurundowego dema z testów, skrócony (`...` oznacza pominięte):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

Kolejność kluczy wewnątrz `survivors`, `equipment` i `buy` nie jest ustalona.
