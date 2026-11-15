---
title: Statistiky
nav_order: 7
lang: "cs"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistiky {#statistics}

Co kdo z hráčů v zápase udělal a jak každé kolo proběhlo: výsledková tabule a
seznam kol [dokumentu zápasu](output-match-json.md). Kód:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Všechno se počítá z zápasu sestaveného jak je popsáno na stránce
[Sestavení zápasu](building-matches.md): jeho záznamy zabití, jeho poškození
(ztracené zdraví, jen nepřátelé), jeho oslepení (jen nepřátelé) a jeho řádky.

![textová výsledková tabule syntetického zápasu](../assets/img/scoreboard.svg)

## Definice {#the-conventions}

Kde samotná hra číslo nedefinuje, platí tyto definice. Jsou také zapsané do
každého dokumentu zápasu pod `conventions`.

| Pojem | Definice |
|---|---|
| **Odplata (trade)** | Smrt je *odplacena*, když jejího vraha zabije některý spoluhráč oběti do **5 s**; to zabití je *odplatné zabití*. |
| **Otevření** | První zabití nepřítele v kole, zatímco je živé. Týmové zabití, sebevražda nebo smrt způsobená světu před ním se přeskočí. |
| **KAST** | Podíl kol, v nichž hráč dal **K**ill (zabití), měl **A**sistenci (asistence zábleskem se počítá), **S**urvived (přežil), nebo byl **T**raded (odplacen). |
| **Poškození** | Skutečně ztracené zdraví, jen nepřátelé: zásah 137 poškození headshotem na hráče se 40 zdraví je 40. |
| **Clutch** | Být posledním živým hráčem na straně, když ještě stojí nepřátelé; vyhraný, když jeho strana kolo vyhraje. |
| **Nákup (buy)** | Pro každou stranu podle průměrné hodnoty výbavy na konci zmrazení: první kolo každého řádného poločasu je pistolové kolo (kolo 1 a kolo po poločase, pokud zápas tak hrál), prodloužení žádné nemá; pak pod 1 500 $ eco, pod 4 000 $ force, jinak full. |

## Kdo začal každé kolo {#who-started-each-round}

Několik čísel potřebuje vědět, kdo kolo odehrál. **Výchozí hráči** kola jsou
pro každou stranu každý hráč s živým řádkem pozice do jedné sekundy od nejdřívější
pozice toho kola (tedy v první sekundě po konci zmrazení). **Odehraná kola**
hráče je počet kol, která začal. Nezačal-li žádné (neměl takový řádek), použije
se místo něj počet kol zápasu, aby nikde nedocházelo k dělení nulou.

## Řádek výsledkové tabule {#the-scoreboard-line}

Jeden záznam na hráče (pole dokumentu zápasu viz [dokument zápasu](output-match-json.md#players)).
„Zabití nepřítelem“ níže znamená zabití s útočníkem, ne týmové zabití a ne
sebevraždu (vlastní smrt oběti).

| Pole | Počítá |
|---|---|
| `kills` | zabití nepřítelem, z živé i z fáze po |
| `deaths` | každá smrt: nepřítelem, spoluhráčem, sebou nebo světem |
| `assists` | zabití nepřítelem, která tento hráč asistoval bez záblesku (asistující nesmí být vrah) |
| `flashAssists` | zabití nepřítelem, která tento hráč asistoval zábleskem |
| `diff` | zabití - smrti |
| `adr` | poškození (ztracené zdraví, jen nepřátelé, obě fáze) / odehraná kola, jedno desetinné místo |
| `kast` | 100 x (kola se zabitím, asistencí nebo zábleskovou asistencí, přežitím nebo odplacenou smrtí) / odehraná kola, jedno desetinné místo. *Přežití* je: výchozí hráč kola, který v něm nezemřel, v žádné fázi. |
| `headshotPct` | 100 x zabití headshotem / zabití, jedno desetinné místo; 0 bez zabití |
| `openingKills`, `openingDeaths` | vyhrané a prohrané otevírací souboje |
| `tradeKills` | zabití, která pomstila smrt spoluhráče |
| `tradedDeaths` | smrti, které byly odplaceny |
| `multiKills` | kola s 2, 3, 4 a 5 zabitími nepřítele (`2k`, `3k`, `4k`, `5k`); více než pět se počítá jako `5k`. Počítají se obě fáze. |
| `clutches`, `clutchesWon` | odehrané a vyhrané clutche (níže) |
| `utilityDamage` | poškození způsobené granáty HE, molotovy a zápalnými granáty, jedno desetinné místo |
| `enemiesFlashed` | nepřátelé oslepení alespoň **1,0 s** zábleskem tohoto hráče |
| `plants`, `defuses` | položení bomby a deaktivace (řádky tabulky) |
| `teamkills` | zabití spoluhráči. Sebevražda - útočník a oběť je tentýž hráč, třeba vlastní granát - není teamkill: je to jen smrt. |
| `roundsPlayed` | začatá kola, jak je uvedeno výše |

Hráči jsou seřazeni podle názvu týmu (abecedně) a v rámci týmu podle `diff`,
pak podle `kills`, nejlepší první.

Poznámky k okrajům:

- Zabití ve fázi po - vítězové lovící šetřícího hráče - se počítá jako zabití,
  smrt, pro ADR, vícenásobná zabití i KAST stejně jako každé jiné.
- Zabití skrz zeď se počítají interně u každého hráče, ale do dokumentu zápasu se
  nezapisují; každé zabití v seznamu kola říká, zda bylo takové.
- Část *odplacen* v KAST připisuje oběti odplacené smrti v tom kole.
- Týmová zabití a sebevraždy přičtou smrt oběti, ale nikomu žádné zabití;
  týmové zabití přidá do `teamkills` vraha, sebevražda nikam jinam.

## Clutche {#clutches}

Pro každé kolo se výchozí hráči obou stran berou jako živí a procházejí se
živá zabití kola v pořadí. Po každé smrti se oběť odebere a podívá se na každou
stranu: strana, na které zbývá přesně **jeden** hráč a alespoň jeden nepřítel
stojí, je clutch pro tohoto hráče **proti** počtu nepřátel naživu v tom okamžiku.
Každý hráč má nejvýš jeden clutch v kole; je **vyhraný**, když jeho strana kolo
vyhrála.

Důsledky definice:

- Obě strany mohou mít clutch v jednom kole. Když je strana první zredukována
  na jednoho (třeba 1v3) a pak je i druhá strana zredukována na jednoho, druhý
  hráč má vlastní clutch 1v1.
- `against` je počet v okamžiku, kdy se hráč stal posledním, ne na konci.
- Zabití ve fázi po se neprocházejí, takže nezačnou clutch ani ho nemění.

## Přeživší {#survivors}

**Přeživší** kola jsou pro každou stranu její výchozí hráči bez těch, kdo zemřeli
během živé fáze. Hráč zabitý ve fázi po při šetření je v seznamu kola pořád
přeživším - ale pro KAST nepřežil.

## Seznam kol {#the-round-list}

Každé kolo v dokumentu zápasu nese svůj výsledek, skóre, strany, ekonomiku,
položení, přeživší, clutche a zabití v pořadí; viz
[Dokument zápasu](output-match-json.md#rounds).

## Textová výsledková tabule {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` vypíše tato čísla pro každý tým;
viz [Příkazy](commands.md#scoreboard---a-match-as-text).
