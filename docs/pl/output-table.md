---
title: Tabela mapy cieplnej
nav_order: 8
lang: "pl"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# Tabela mapy cieplnej (`<mecz>.parquet`) {#the-heatmap-table-parquet}

Jeden plik Parquet na mecz: pozycja każdego żywego gracza, próbkowana, i każde zdarzenie w miejscu, w którym zaszło - jeden wiersz na każde. To długa tabela, którą przeglądarka 3DHeat czyta jako mapę cieplną, a każde inne narzędzie jako zwykłą tabelę. Kod:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(plik), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(wiersze; zob. [Budowanie meczu](building-matches.md)).

Plik jest zapisywany z kompresją Snappy w grupach wierszy po 256 000 wierszy. Wiersze są posortowane według `time`, a potem według `event`. W tabeli są tylko wiersze wewnątrz rundy (od końca jej czasu zamrożenia do początku następnej rundy).

Na syntetycznym demie z testów wiersze zdarzeń pierwszej rundy:

![wiersze zdarzeń w tabeli](../assets/img/table-rows.svg)

W kontenerze `.3dheat` tabela to element o roli `table` ([Jeden plik na mecz](output-container.md)).

## Kolumny {#columns}

Kolumny, zawsze w tej kolejności. Kolumny tekstowe to ciągi ze słownikiem (`dictionary<int32, string>`) i nigdy nie są puste: „brak wartości” to pusty ciąg. Kolumny liczbowe są puste tam, gdzie wiersz nie ma wartości.

| Kolumna | Typ | Co to jest |
|---|---|---|
| `match` | tekst | nazwa meczu (`alpha-vs-bravo-m1`, albo `...-b` dla drugiego łańcucha) |
| `map` | tekst | mapa z nagłówka dema (`de_x`) |
| `round` | int16 | numer rundy, od 1 |
| `roundId` | tekst | `<mecz> #NN`, numer rundy w dwóch cyfrach (`alpha-vs-bravo-m1 #07`): unikalny między meczami, sesja widoku |
| `phase` | tekst | `freeze` w czasie zamrożenia rundy (od końca poprzedniej rundy), `live` aż do rozstrzygnięcia rundy, `after`, gdy zwycięzcy polują, a przegrani oszczędzają |
| `time` | float64 | sekundy od startu meczu (żywego startu jego pierwszego pliku), na jednym zegarze dla jego plików |
| `roundTime` | float32 | sekundy od końca czasu zamrożenia tej rundy; ujemne w czasie zamrożenia |
| `event` | tekst | czym jest wiersz - zob. [Zdarzenia](#events) |
| `player` | tekst | nazwa gracza (przy każdym zdarzeniu, który gracz - opisano niżej) |
| `steamid` | tekst | Steam ID gracza (64-bitowe, jako tekst) |
| `side` | tekst | `T` albo `CT` w tej rundzie; puste, gdy gracz nie był po żadnej stronie |
| `team` | tekst | nazwa drużyny gracza (albo `Started T` / `Started CT`); przy `explode` drużyna podkładająca |
| `x`, `y`, `z` | float32 | pozycja we własnych współrzędnych gry: cale (jednostki gry), **Z w górę**, układ prawoskrętny |
| `dirX`, `dirY`, `dirZ` | float32 | dokąd patrzy gracz, wektor jednostkowy w tym samym układzie; tylko pozycje |
| `health` | int16 | 0-100; w pozycjach, a przy `hurt` - ile zostało po trafieniu |
| `armor` | int16 | 0-100; w pozycjach, a przy `hurt` - ile zostało po trafieniu |
| `money` | int32 | pieniądze gracza; tylko pozycje |
| `equipment` | int32 | wartość tego, co gracz niesie; tylko pozycje |
| `weapon` | tekst | broń tak, jak nazywa ją gra (`AK-47`, `M4A1-S`, `Knife` dla każdej skórki noża) |
| `place` | tekst | nazwa miejsca na mapie w pozycji wiersza (`BombsiteA`, `CTSpawn`); puste przy detonacjach granatów: dema nie podają miejsca, w którym wybuchł granat |
| `throwerPlace` | tekst | nazwa miejsca rzucającego, gdy granat wybuchł; tylko detonacje granatów |
| `other` | tekst | drugi gracz zabójstwa, śmierci, trafienia albo błysku |
| `damage` | float32 | stracone zdrowie; tylko `hurt` |
| `duration` | float32 | sekundy oślepienia; tylko `blind` |
| `headshot` | int8 | 0/1; tylko `kill` i `death` |
| `opening` | int8 | 0/1, pierwsze zabójstwo wroga w rundzie; tylko `kill` i `death` |
| `traded` | int8 | 0/1. Dla `kill`: to było zabójstwo wymiany. Dla `death`: została pomszczona w ciągu 5 s. Tylko `kill` i `death`. |
| `noscope` | int8 | 0/1, zabójstwo bronią z celownikiem wystrzeloną bez celowania (zdarzenie `noscope`); tylko `kill` i `death` |
| `attackerBlind` | int8 | 0/1, zabójca był oślepiony, gdy zabijał (zdarzenie `attackerblind`); tylko `kill` i `death` |
| `won` | int8 | 0/1, czy strona tego wiersza wygrała rundę; puste, gdy `side` jest puste |
| `buy` | tekst | zakup strony tego wiersza w tej rundzie: `pistol`, `eco`, `force`, `full` |
| `detail` | tekst | każde pole zdarzenia, którego nie niosą inne kolumny, jako obiekt JSON (nazwy z gry): strzał to kule (`fire_bullets`: początek, kąty, niecelność, rozrzut, indeks odrzutu, ziarno...), `dominated`, `revenge`, `attackerinair`, `wipe` śmierci, `defindex` przedmiotu, a krok nie ma nic |
| `text` | tekst | linia czatu; tylko `chat` |
| `entity` | int32 | encja granatu: lot `throw` (wiersze `grenade`), jego detonacja i gracze, których oślepił, mają wspólną |
| `hitgroup` | tekst | gdzie trafiła kula (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | stracony pancerz; tylko `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | miejsce trafienia na ciele, w układzie ofiary, w metrach (x do przodu, y w górę od stóp, z w prawo): promień strzału (`fire_bullets`, inaczej oko atakującego i widok) prześledzony do ciała ustawionego tak, jak stała i kucała ofiara, na część nazwaną przez `hitgroup`; tylko `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | kierunek strzału w tym samym układzie; `hitMiss` o ile (m) promień minął nazwaną część (0: przez nią); `hitFrom` `bullet` albo `aim` |
| `penetrated` | int16 | ściany, przez które przeszła zabójcza kula; `kill` i `death` |
| `throughSmoke` | int8 | 0/1, zabicie przez dym; `kill` i `death` |
| `distance` | float32 | odległość zabójstwa, tak jak liczy ją gra (metry); `kill` i `death` |
| `assister` | tekst | kto asystował; `kill` i `death` |
| `flash`, `flashAlpha` | float32 | sekundy pozostałego błysku i jak biały; pozycje |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozycje |
| `zoom`, `duck`, `moveType` | | poziom przybliżenia celownika, jak bardzo kuca (0-1), typ ruchu gry; pozycje |
| `spottedBy` | tekst | Steam ID wrogów, którzy widzą tego gracza, oddzielone `\|`; pozycje |
| `inventory` | tekst | wszystko, co gracz niesie, oddzielone `\|`; pozycje |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | magazynek i zapas trzymanej broni; strzały w bieżącej serii; pozycje |
| `punchPitch`, `punchYaw` | float32 | odrzut celowania, w stopniach; pozycje |
| `ping` | int16 | milisekundy; pozycje |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | liczniki tablicy wyników gry za mecz do tej pory; pozycje |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | pieniądze wydane w tej rundzie i w meczu; wartość wyposażenia na starcie rundy; pozycje |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, stan gracza w czasie wiersza, z uwzględnieniem zdarzeń: hełm, zestaw do rozbrajania, jakikolwiek pancerz, celowanie (od ostatniej próbki pozycji gracza do wiersza), oślepienie (w trakcie `blind`, które w nich trafiło); każdy wiersz z nazwanym graczem |
| `state_utility` | int16 | granaty niesione w tej chwili (z `inventory`); każdy wiersz z nazwanym graczem |
| `state_weapon` | tekst | broń w ręku w tej chwili (przy `death` - własna ofiary, gdzie `weapon` to broń zabójcy); każdy wiersz z nazwanym graczem |
| `earn_round_cs2` | int16 | ile runda wypłaciła: przy `round_end` nagroda za wygraną albo premia za przegraną (z premią drużyny podkładającej), przy `plant` i `defuse` 300 gracza |

## Zdarzenia {#events}

Który gracz jest w wierszu, gdzie stoi i które kolumny wypełnia.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won` i `buy` są wypełnione w każdym wierszu; `inventory`, `money`, `equipment` i
kolumny `state_*` w każdym wierszu z nazwanym graczem (zdarzenia biorą je z ostatniej próbki pozycji gracza).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Także wypełnione |
|---|---|---|---|
| `position` | gracz | gracz (stopy) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (trzymana), `place` i cały stan gracza (kolumny od `flash` wzwyż) - także w czasie zamrożenia |
| `kill` | zabójca | gdzie stał zabójca | `other` (ofiara), `weapon`, `headshot`, `opening`, `traded` (zabójstwo wymiany), `noscope`, `attackerBlind`, `place` |
| `death` | ofiara | gdzie upadła ofiara | `other` (zabójca; puste dla świata), `weapon`, `headshot`, `opening`, `traded` (pomszczona), `noscope`, `attackerBlind`, `place` |
| `hurt` | ofiara | gdzie została trafiona | `other` (atakujący), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - także trafienia kolegów i świata |
| `shot` | strzelający | skąd oddano strzał | `weapon`, `place`, `detail` (relacja gry o kulach) |
| `slash` | gracz | gdzie zamachnięto się nożem | `weapon` = `Knife` |
| `grenade` | rzucający | granat w locie, w próbkowaniu graczy i tam, gdzie się zatrzymał | `weapon` (granat), `entity` |
| `throw` | rzucający | skąd rzucono granat | `weapon` (granat), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | rzucający | gdzie wybuchł | `weapon`, `throwerPlace` (miejsce rzucającego w tym momencie); `place` pozostaje puste |
| `blind` | oślepiony gracz | gdzie stał | `other` (oślepiający), `duration`, `weapon` = `Flashbang`, `entity`, `place` - także oślepieni koledzy |
| `plant` | podkładający | gdzie podłożył | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | rozbrajający | gdzie rozbroił | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | każdy gracz, który grał rundę | gdzie gracz stał ostatnio | `won`, `earn_round_cs2` (co runda im wypłaciła: wzrost pieniędzy strony do następnego czasu zamrożenia, gdy zasady na to pozwalają, a w przeciwnym razie wartość wynikająca z zasad), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | podkładający (wraz z jego Steam ID), strona `T`, drużyna podkładająca | pozycja podłożenia | `weapon` = `C4 Explosive`, `place` (podkładającego w chwili podłożenia: gdzie leżała bomba); czas to chwila wybuchu bomby |
| `chat` | nadawca | gdzie był | `text` |
| każde inne zdarzenie gry dotyczące gracza, pod nazwą z gry: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect` i inne | gracz | gdzie był (zdarzenia granatu: gdzie był granat) | `weapon` (przedmiotu), `entity`, `detail` (każde pole zdarzenia) |

Co jest w tabeli, a czego nie ma:

- Wiersze **position** to żywi gracze po jednej stronie, poza czasem zamrożenia i rozgrzewką, co `--every` ticków (domyślnie osiem na sekundę).
- Wiersze **kill** to tylko zabójstwa przez wroga - bez teamkilla, samobójstwa i śmierci od świata. Wiersze **death** to każda śmierć, także te.
- Wiersze **explode** to każda podłożona bomba, która wybuchła, według `bomb_exploded` dema: także w fazie po, gdy T już wygrali przez eliminację. Dema bez tego zdarzenia dostają jeden dla każdej rundy wygranej przez bombę, na końcu rundy.
- Wiersze **hurt** i **blind** są tylko między wrogami.
- **shot** pomija noże i C4; granaty to wiersze **throw**.
- **molotov** obejmuje molotovy i zapalające (zapłon ognia).
- Obrażenia od drużyny, błyski kolegów i widzów, zdarzenia w czasie zamrożenia oraz wszystko między rundami nie są w tabeli.

Przykład, z syntetycznego dema z testów (rzucony dym, otwierające zabójstwo w głowę, wymiany):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

Śmierć bob'a zostaje pomszczona przez zabójstwo ace'a przez bena 1,9 s później (wiersz `death` bob'a: traded 1; wiersz `kill` bena: zabójstwo wymiany, traded 1); drugie trafienie w bob'a to 137 obrażeń przy 40 zdrowiu, więc liczy się jako 40.

## Podpowiedzi stopki `heat3d` {#the-heat3d-footer-hints}

Stopka Parquet pliku (metadane klucz/wartość schematu) niesie instrukcje odczytu pod kluczem **`heat3d`**, obiektem JSON:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Wpis | Mówi |
|---|---|
| `version`, `kind` | wersja podpowiedzi (1) i to, co je zapisało (`cs2-demo`) |
| `axes.up` | Z pliku jest w górę |
| `axes.flipY` | zaneguj Y pliku (zob. niżej) |
| `axes.scale` | 1: pozycje są używane tak, jak są, w jednostkach gry |
| `entity.size` | gracz ma **32 jednostki** szerokości - szerokość gracza CS2 - tyle, ile rysuje pudełkowa powtórka |
| `columns.x` / `y` / `z` | kolumny pozycji |
| `columns.time`, `timeUnit` | `time`, w sekundach |
| `columns.personId` | gracz to osoba |
| `columns.teamId` | strona to grupa (więc T i CT, a nie nazwy drużyn, nadają kolory grupom) |
| `columns.sessionId` | każda runda (`roundId`) to sesja |
| `columns.lookMode` i `dirX`-`dirZ` | kierunek patrzenia to wektor w tych kolumnach |
| `columns.extra` | kolumny do zachowania jako filtry, w kolejności przydatności |

Widok, który zna ten klucz, otwiera plik bez żadnych ustawień. Inne narzędzia go ignorują. Żeby odczytać go samodzielnie:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Osie i jednostki {#axes-and-units}

Współrzędne są własne dla gry: **cale** (jedna jednostka gry; gracz ma 72 jednostki wzrostu, stojąc, i 32 szerokości), **Z w górę**, układ prawoskrętny.

Widok, którego świat ma Y w górę, musi rysować (x, y, z) gry jako **(x, z, -y)** - Z staje się wysokością, a Y jest odwrócone. To obrót, a nie odbicie lustrzane. Narysowane tak, jak rysuje się świat lewoskrętny z Z w górę, jako (x, z, y), każda mapa wychodzi odbita lustrzanie, a strona A jest po złej stronie; `flipY: true` to to, co podpowiedzi każą ustawić, by temu zapobiec. [Eksport mapy](map-export.md) zapisuje swoją geometrię już w układzie (x, z, -y), w tych samych jednostkach, więc leży pod tabelą bez żadnej korekty.

Odległości w widoku są podpisane w metrach; przy skali 1 to jednostki gry. Pomnóż przez 0,0254, by otrzymać metry.

## Rozmiar {#size}

Dominują pozycje: około dziesięciu graczy razy 8 próbek na sekundę żywej gry przy domyślnym `--every 8`, mniej dla martwych graczy i w czasie zamrożenia. Podwojenie `--every` zmniejsza je o połowę; zdarzenia się nie zmieniają.
