---
title: Odczyt dema
nav_order: 5
lang: "pl"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Odczyt dema {#reading-a-demo}

Co wyjmuje się z jednego pliku `.dem`, zanim cokolwiek zostanie zinterpretowane. Kod:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Dema CS2 to nagranie serwera (SourceTV): każdy gracz, w każdym ticku, 64 ticki na sekundę (`TICKRATE = 64`). Są czytane przez
[demoparser2](https://github.com/LaihoE/demoparser) w trzech wywołaniach, a wynik zachowywany jest taki, jaki przyszedł, w `RawPart`:

| Pole | Zawiera |
|---|---|
| `path` | plik |
| `map` | `map_name` z nagłówka dema (`de_x`); puste, jeśli nagłówek go nie ma |
| `samples` | jeden wiersz na gracza na próbkowany tick: poniższe pola graczy i zasad gry, plus `tick`, `steamid`, `name` |
| `events` | nazwa zdarzenia -> jego wiersze, z polami graczy z prefiksami `user_`, `attacker_`, `assister_`, tak jak nazywa je parser |

Nic w `demo.py` nie decyduje, czym jest runda ani kto ją wygrał; to należy do [Budowanie meczu](building-matches.md).

## Próbkowane ticki {#the-sampled-ticks}

`parse_ticks` jest proszony o ticki `0, N, 2N, ...` aż do 4 000 000 (`LAST_TICK`, daleko poza jakimkolwiek meczem - 17 godzin przy 64 tickach na sekundę), gdzie *N* to `--every` (domyślnie 8). Parser zatrzymuje się na końcu dema. Każdy gracz obecny w próbkowanym ticku daje jeden wiersz, czy żywy, martwy, obserwujący czy trener; filtrowanie odbywa się później.

Krok próbkowania liczy się bardziej niż gęstość mapy cieplnej: moment rozstrzygnięcia rundy odczytywany jest z tych próbek (zob. [Budowanie meczu](building-matches.md#rounds)), więc czasy końca rund są dokładne co jeden krok (domyślnie 1/8 s).

### Pola graczy {#player-fields}

| Właściwość | Staje się |
|---|---|
| `X`, `Y`, `Z` | pozycja, w jednostkach gry (calach), Z w górę. demoparser2 podaje punkt gracza, czyli stopy. |
| `yaw`, `pitch` | kierunek patrzenia (stopnie), zamieniony na wektor jednostkowy |
| `health`, `armor_value` | zdrowie, pancerz |
| `team_num` | strona: 2 = T, 3 = CT; cokolwiek innego (widzowie, 0, 1) to brak strony |
| `team_clan_name` | nazwa drużyny, tak jak pokazuje ją serwer; używana do nazwania drużyn |
| `active_weapon_name` | trzymana broń, tak jak nazywa ją gra (`AK-47`, `Karambit`) |
| `is_alive` | czy gracz żyje - tylko żywi gracze stają się pozycjami |
| `last_place_name` | nazwa miejsca na mapie, tak jak podaje ją mapa (`BombsiteA`) |
| `balance` | pieniądze |
| `current_equip_value` | wartość tego, co gracz niesie |

### Pola zasad gry {#game-rules-fields}

Odczytywane równolegle, raz na wiersz gracza (są takie same dla wszystkich w danym ticku):

| Właściwość | Do czego |
|---|---|
| `game_time` | zegar serwera, w sekundach |
| `total_rounds_played` | liczba rund, która przechodzi przez pliki meczu |
| `round_win_status` | kto wygrał właśnie rozegraną rundę: 1 remis, 2 T, 3 CT |
| `round_win_reason` | jak (`CSRoundEndReason` gry) |
| `team_rounds_total` | wynik każdej strony |
| `is_warmup_period` | rozgrzewka jest wszędzie pomijana |
| `is_freeze_period` | czas zamrożenia jest pomijany w pozycjach |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | rozgrywana dogrywka, 0 w regulaminie: rundy dogrywki nie są rundami pistoletowymi (parser nie ma krótszej nazwy) |

## Zdarzenia {#the-events}

Każde zdarzenie poniżej jest odczytywane, gdy dema je deklaruje (`list_game_events`), z `X`, `Y`, `Z`, `team_num`, `last_place_name` i `which_bomb_zone` (strefa bomby, w której stoi gracz: 0 brak, 1 A, 2 B) dla każdego gracza, którego zdarzenie wymienia, oraz `total_rounds_played` i `is_warmup_period` gry w tym ticku:

| Zdarzenie | Staje się |
|---|---|
| `player_death` | zabójstwa i śmierci; używa `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | obrażenia; używa `dmg_health` (zadane obrażenia zdrowia), `health` (zdrowie, które zostało), `weapon` |
| `player_blind` | oślepieni gracze; używa `blind_duration` |
| `weapon_fire` | strzały i rzuty granatów; używa `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | gdzie wybuchły granaty; używa własnych `x`, `y`, `z` zdarzenia (zdarzenie nie ma nazwy miejsca dla tego punktu, tylko dla rzucającego) |
| `bomb_planted` | podłożenie; używa `which_bomb_zone` i miejsca podkładającego oraz `site` (numer encji strefy) |
| `bomb_defused` | rozbrojenie |
| `bomb_exploded` | kiedy bomba wybuchła: czas wiersza `explode` |
| `round_freeze_end` | gdzie zaczyna się każda runda |
| `round_prestart` | gdzie kończy się czas po rozstrzygniętej rundzie |
| `round_announce_match_start` | gdzie zaczyna się żywy mecz |

## Dwa fakty o demach, które decydują o sposobie ich czytania {#two-facts-about-demos-that-decide-how-they-are-read}

- **Mecz może być podzielony na pliki**, a nazwy plików nie mówią o ich kolejności. Liczba rund (`total_rounds_played`) przechodzi przez nie, zwykle także zegar serwera, więc części można ustawić według tego, co zawierają.
- **Nagranie może zacząć się przed meczem**: rozgrzewka, restart, runda na noże. Mecz zaczyna się od **ostatniego** `round_announce_match_start` w pliku; przed nim wszystko jest pomijane, a rozgrzewka jest pomijana wszędzie.
