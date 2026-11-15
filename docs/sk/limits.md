---
title: Obmedzenia
nav_order: 13
lang: "sk"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Obmedzenia {#limits}

Čo konvertor predpokladá, čo nerieši a čo nie je overené. Každý bod pochádza z
kódu v jeho aktuálnom stave.

## Čo číta {#what-it-reads}

- **Iba nekomprimované súbory `.dem`.** `.dem.zst`, `.dem.bz2`, `.rar` a
  `.zip` treba najprv rozbaliť. Prípona sa porovnáva bez ohľadu na veľkosť
  písmen (`.dem`, `.DEM`), v priečinkoch rovnako ako pri súboroch zadaných
  menom.
- **Zápasy na defúzie bomby.** Konce kôl, položenie a miesto bomby, typy nákupu
  a pistolové kolá sú tie z defúzie bomby. Mapy s rukojemníkmi, Wingman a iné
  režimy sa nespracúvajú osobitne a nie sú overené.
- **Predpokladá sa 64 tikov za sekundu** (`TICKRATE = 64`) pre každý čas
  počítaný z tikov; servery CS2 bežia na 64.
- **Predpokladá sa demo zo servera** (SourceTV): obsahuje každého hráča.
  Nahrávka na strane klienta (POV demo) sa neskúšala.

## Zápasy a kolá {#matches-and-rounds}

- **Súbory sa zoskupujú podľa názvu.** Časti jedného zápasu musia mať rovnaký
  názov okrem prípony `-pN` / `_pN`; súbory jedného zápasu pod nesúvisiacimi
  názvami sa stanú samostatnými zápasmi a súbory s rovnakým názvom v rôznych
  priečinkoch sa zoskupia spolu (potom sa rozdelia na reťazce, ak na seba
  nenadväzujú).
- **Živý zápas sa začína pri poslednej udalosti `round_announce_match_start`**
  v súbore. Nožové kolo, za ktorým toto oznámenie nenasleduje, sa počíta ako
  kolo.
- **Časy konca kôl sú presné na jednu vzorku** (`--every` tikov, pri predvolenom nastavení 1/8 s), lebo rozhodnutie sa číta zo vzorkovaného
  herného stavu. Veľmi veľké `--every` môže minúť krátke okno medzi koncom
  kola a začiatkom ďalšieho a kolo vynechať ako neúplné.
- **Remízy.** Remízové kolo (stav výhry 1, dôvod 10) sa rozhodne bez víťaza:
  `winner` je prázdne a žiadna strana ho nevyhrala. Remíza v skutočnom deme sa
  nevyskytla, na porovnanie; overuje sa na syntetickom.
- **Kolá prerušené** koncom súboru sa vynechajú (`incomplete`), nehádajú sa;
  kolá pred prvým v súboroch sa uvedú ako `missing`.
- **Pistolové kolá** nasledujú dĺžku polčasu, ktorú ukazuje nahrávka: kde sa
  strany prvýkrát vymenia medzi dvoma po sebe idúcimi riadnymi kolami.
  Nahrávka, ktorá takú výmenu neukazuje (začína po polčase, alebo končí pred
  ňou, alebo chýba kolo na jednej z jej strán), pozná ako pistolové kolo iba
  kolo 1. Predĺženie nemá žiadne.
- **Tímy.** Tím je názov klanu, ktorý sa najčastejšie vidí pri jeho hráčoch.
  Bez názvov klanov sú tímy `Started T` a `Started CT`. Hráč, ktorý uprostred
  zápasu zmení tím, zostane v jednom tíme.

## Udalosti {#events}

- **Číta sa všetko, čo parser ponúka**, s týmito výnimkami: rýchlosť hráčov
  (parser ju odvodzuje z pozícií; v deme nie je), hlas (zvuk, `parse_voice`) a
  `weapon_fire` bomby (začiatok položenia, ktoré má `bomb_beginplant`). Lety
  granátov sa zachovajú pri vzorkovaní hráčov (`--every`) a tam, kde sa granát
  zastavil, nie v každom tiku.
- **Riadky mimo kola** (rozcvička, pauza medzi začiatkom zápasu a prvým časom
  zmrazenia po viac než dvoch minútach) sa z tabuľky vynechajú; udalosti, ktoré
  sa netýkajú žiadneho hráča, sú všetky v `events` dokumentu zápasu.
- **Riadky výbuchov** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nemajú
  `place`: demo pomenúva miesta pre hráčov, nie pre granáty. Miesto hádzajúceho
  v tom okamihu je v `throwerPlace`.
- **Miesto položenia** pochádza z bombovej zóny, v ktorej podľa hry stál
  kladač, inak z názvu miesta kladača, inak z iného položenia na tej istej zóne
  v tom istom súbore. Ak nič z toho nehovorí, `site` je prázdne.
- **Smrť spôsobená svetom** (pád, bomba) nemá útočníka: žiadne zabitie, žiadne
  tímové zabitie, žiadne otvorenie; je to smrť.

## Štatistika {#statistics}

- **Odohrané kolá** pochádzajú od toho, kto mal pozíciu v prvej sekunde po
  zmrazení. Hráč, ktorý sa pripojí neskôr v kole, sa za toho, kto ho odohral,
  nepočíta (jeho zabitia sa rátajú).
- **Prežitie pre KAST:** hráč zabitý vo fáze po skončení nebol pre KAST
  nažive, hoci ho zoznam kôl stále uvádza medzi preživšími.
- **Obaja hráči 1v1** môžu dostať clutch v jednom kole; pozrite
  [Štatistika](statistics.md#clutches).
- **Poškodenie výbušninou** sú granáty HE, molotovy a zápalné granáty; zabitie
  alebo zásah hodeným bleskom alebo návnadou nie je poškodenie výbušninou.

## Export mapy {#map-export}

- Potrebuje nainštalovanú hru (alebo `.vpk`) a CLI Source2Viewer; nič sa
  nesťahuje.
- Exportuje iba `world_physics`; clip a obloha sa vynechajú podľa toho, či ich
  názvy obsahujú `clip` alebo `sky`, bez ohľadu na veľkosť písmen.
- Zem sa od konštrukcie rozlišuje iba podľa normály plochy (zložka Z 0,7 alebo
  viac), takže strmá rampa je konštrukcia a plochá strecha je zem.
- Súbor je v palcoch, nie v metroch.

## Pamäť a čas {#memory-and-time}

- Zápas sa drží v pamäti celý, kým sa zostavuje, v jednom pracovnom procese na
  zápas. Pri mnohých procesoch a malom `--every` pamäť narastá: ak má stroj málo
  pamäte, znížte `--jobs`.
- Zápas sa zapisuje, až keď sa zostaví: najprv `.parquet`, potom `.match.json`.
  Beh zastavený medzi tým zanechá tabuľku bez dokumentu zápasu; zápas sa počíta
  ako zapísaný iba s oboma, takže ďalší beh ho konvertuje znova. Zápasy, ktoré
  ešte nezačali, si ďalší beh jednoducho vezme.
