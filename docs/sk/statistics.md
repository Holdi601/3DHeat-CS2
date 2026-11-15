---
title: Štatistika
nav_order: 7
lang: "sk"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Štatistika {#statistics}

Čo každý hráč urobil v zápase a ako prebehlo každé kolo: výsledková tabuľka a
zoznam kôl v [dokumente zápasu](output-match-json.md). Kód:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Všetko sa počíta zo zápasu zostaveného ako na stránke
[Zostavenie zápasu](building-matches.md): jeho záznamy o zabitiach, jeho
poškodenie (stratené zdravie, iba nepriatelia), jeho oslepenia (iba nepriatelia)
a jeho riadky.

![textová výsledková tabuľka syntetického zápasu](../assets/img/scoreboard.svg)

## Konvencie {#the-conventions}

Tam, kde samotná hra číslo nedefinuje, platia tieto definície. Sú tiež zapísané
v každom dokumente zápasu v časti `conventions`.

| Pojem | Definícia |
|---|---|
| **Odveta (trade)** | Smrť je *odvetená*, keď jej zabijaka zabije niekto zo spoluhráčov obete do **5 s**; to zabitie je *odvetné zabitie*. |
| **Otvorenie** | Prvé zabitie nepriateľa v kole, kým je živé. Tímové zabitie, samovražda alebo smrť spôsobená svetom pred ním sa preskočí. |
| **KAST** | Podiel kôl, v ktorých hráč dostal **K**ill (zabitie), **A**ssist (asistencia; asistencia bleskom sa počíta), **S**urvived (prežil) alebo bol **T**raded (odvetený). |
| **Poškodenie** | Skutočne stratené zdravie, iba nepriatelia: zásah 137 poškodenia hlavou na hráča s 40 zdravia je 40. |
| **Clutch** | Byť posledným hráčom živým na strane, keď na nepriateľov ešte stoja; vyhraný, keď strana vyhrá kolo. |
| **Nákup (buy)** | Pre každú stranu podľa priemernej hodnoty výbavy na konci času zmrazenia: prvé kolo každého riadneho polčasu je pistolové kolo (kolo 1 a kolo po polčase, pokiaľ ho zápas odohral); predĺženie ich nemá; potom pod 1 500 $ eco, pod 4 000 $ force, inak full. |

## Kto začal každé kolo {#who-started-each-round}

Niekoľko čísel potrebuje vedieť, kto kolo odohral. **Začínajúci hráči** kola sú
pre každú stranu každý hráč s živým riadkom pozície do jednej sekundy od
najskoršej pozície toho kola (teda v prvej sekunde po konci času zmrazenia).
**Odohrané kolá** hráča sú počet kôl, ktoré začal. Ak hráč nezačal žiadne (nikdy
nemal taký riadok), použije sa namiesto toho počet kôl zápasu, aby sa nedelilo
nulou.

## Riadok výsledkovej tabuľky {#the-scoreboard-line}

Jeden záznam na hráča (pozrite [dokument zápasu](output-match-json.md#players) pre
názvy polí). „Zabitie nepriateľom“ nižšie znamená zabitie s útočníkom, nie
tímové zabitie a nie samovraždu (vlastnú smrť obete).

| Pole | Počíta |
|---|---|
| `kills` | zabitia nepriateľom, z živej aj z fázy po skončení |
| `deaths` | každá smrť: nepriateľom, spoluhráčom, sebou alebo svetom |
| `assists` | zabitia nepriateľom, ktoré tento hráč asistoval bez bleskania (asistujúci nesmie byť zabijak) |
| `flashAssists` | zabitia nepriateľom, ktoré tento hráč asistoval bleskom |
| `diff` | zabitia - smrti |
| `adr` | poškodenie (stratené zdravie, iba nepriatelia, obe fázy) / odohrané kolá, jedno desatinné miesto |
| `kast` | 100 x (kolá so zabitím, asistenciou alebo asistenciou bleskom, prežitím alebo odvetenou smrťou) / odohrané kolá, jedno desatinné miesto. *Prežitie* je: začínajúci hráč kola, ktorý v ňom nezomrel, v žiadnej z fáz. |
| `headshotPct` | 100 x zabitia headshotom / zabitia, jedno desatinné miesto; 0 bez zabití |
| `openingKills`, `openingDeaths` | vyhrané a prehraté otváracie dvojboje |
| `tradeKills` | zabitia, ktoré odvetili smrť spoluhráča |
| `tradedDeaths` | smrti, ktoré boli odvetené |
| `multiKills` | kolá s 2, 3, 4 a 5 zabitiami nepriateľov (`2k`, `3k`, `4k`, `5k`); viac ako päť sa počíta ako `5k`. Počítajú sa obe fázy. |
| `clutches`, `clutchesWon` | odohrané a vyhraté clutche (nižšie) |
| `utilityDamage` | poškodenie HE granátmi, molotovmi a zápalnými granátmi, jedno desatinné miesto |
| `enemiesFlashed` | nepriatelia oslepení aspoň na **1,0 s** bleskmi tohto hráča |
| `plants`, `defuses` | položenia bomby a zneškodnenia (riadky tabuľky) |
| `teamkills` | zabití spoluhráči. Samovražda - útočník a obeť ten istý hráč, napríklad vlastný granát - sa nepočíta: je to iba smrť. |
| `roundsPlayed` | začaté kolá, ako vyššie |

Hráči sú zoradení podľa názvu tímu (abecedne) a v rámci tímu podľa `diff`, potom
podľa `kills`, od najlepšieho.

Poznámky k okrajom:

- Zabitie vo fáze po skončení - víťazi lovia šetriaceho hráča - sa počíta ako
  zabitie, smrť, pre ADR, multizabitia a KAST rovnako ako každé iné.
- Zásahy cez stenu sa počítajú pre hráča interne, ale nezapisujú sa do
  dokumentu zápasu; každé zabitie v zozname kôl hovorí, či bolo takéto.
- Časť *odvetené* v KAST pripisuje obeti odvetenej smrti v tom kole.
- Tímové zabitia a samovraždy pridajú smrť obeti, ale nikomu nepridajú zabitie;
  tímové zabitie pridá do `teamkills` zabijaka, samovražda nikam inam.

## Clutche {#clutches}

Pre každé kolo sa začínajúci hráči oboch strán považujú za živých a živé
zabitia kola sa prejdú v poradí. Po každej smrti sa obeť odstráni a pozrie sa na
každú stranu: strana s presne **jedným** hráčom, a s aspoň jedným nažive
stojacim nepriateľom, je clutch pre tohto hráča **proti** počtu nepriateľov
nažive v tom okamihu. Každý hráč má najviac jeden clutch v kole; je **vyhratý**,
keď jeho strana vyhrala kolo.

Dôsledky definície:

- Clutch môžu mať obe strany v jednom kole. Ak je jedna strana najprv na jednom
  hráčovi (napríklad 1v3) a potom je aj druhá strana zredukovaná na jedného,
  druhý hráč je v svojom vlastnom clutchi 1v1.
- `against` je počet v okamihu, keď sa hráč stal posledným, nie na konci.
- Zabitia z fázy po skončení sa neprechádzajú, takže ani nezačnú clutch, ani ho
  nemenia.

## Preživší {#survivors}

Preživší kola sú za každú stranu jej začínajúci hráči bez tých, ktorí zomreli
počas živej fázy. Hráč zabitý vo fáze po skončení pri love je v zozname kola
stále preživší - ale pre KAST *neprežil*.

## Zoznam kôl {#the-round-list}

Každé kolo v dokumente zápasu nesie svoj výsledok, skóre, strany, ekonomiku,
položenie, preživších, clutche a svoje zabitia v poradí; pozrite
[Dokument zápasu](output-match-json.md#rounds).

## Textová výsledková tabuľka {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` vypíše tieto čísla po tímoch; pozrite
[Príkazy](commands.md#scoreboard---a-match-as-text).
