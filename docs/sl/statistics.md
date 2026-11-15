---
title: "Statistika"
nav_order: 7
lang: "sl"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistika {#statistics}

Kaj je naredil vsak igralec na tekmi in kako je šla vsaka runda: lestvica in seznam rund
[dokumenta tekme](output-match-json.md). Koda:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Vse se šteje iz tekme, zgrajene kakor v [Gradnja tekme](building-matches.md): njeni zapisi ubijanj, njena škoda (izgubljeno
zdravje, samo sovražniki), njene oslepitve (samo sovražniki) in njene vrstice.

![besedilna lestvica sintetične tekme](../assets/img/scoreboard.svg)

## Konvencije {#the-conventions}

Kjer igra sama ne določa števila, veljajo te definicije. Zapisane so tudi v vsakem dokumentu tekme pod `conventions`.

| Izraz | Definicija |
|---|---|
| **Maščevanje** | Smrt je *maščevana*, če njen ubijalec v **5 s** pade od roke enega od žrtvinih soigralcev; ta uboj je *maščevalni uboj*. |
| **Prvi uboj** | Prvi sovražnikov uboj v rundi, dokler je živa. Prijateljski uboj, samomor ali smrt zaradi sveta pred njim se preskoči. |
| **KAST** | Delež rund, v katerih je igralec dobil **K**ill (uboj), **A**ssist (asistenca; asistenca z bliskovko šteje), **S**urvived (preživel) ali bil **T**raded (maščevan). |
| **Škoda** | Dejansko izgubljeno zdravje, samo sovražniki: zadetek v glavo s škodo 137 na igralca z 40 zdravja je 40. |
| **Clutch** | Biti zadnji živi igralec na strani, ko so sovražniki še živi; osvojen, kadar stran zmaga v rundi. |
| **Nakup** (`buy`) | Za vsako stran iz povprečne vrednosti opreme ob koncu zamrznitve: prva runda vsakega rednega polčasa je pištolska (runda 1 in runda po polčasu, če jo je tekma odigrala); podaljšek nima pištolske; nato pod 1500 $ eco, pod 4000 $ force, sicer full. |

## Kdo je začel vsako rundo {#who-started-each-round}

Več števil mora vedeti, kdo je igral rundo. Začetni igralci runde so, za vsako stran, vsak igralec z živo vrstico položaja
v eni sekundi od najzgodnejšega položaja te runde (to je v prvi sekundi po koncu zamrznitve). Število **odigranih rund**
igralca je število rund, ki jih je začel. Če igralec ni začel nobene (nikoli ni imel take vrstice), se uporabi število rund
tekme, da ne pride do deljenja z nič.

## Vrstica lestvice {#the-scoreboard-line}

En vnos na igralca (glejte [dokument tekme](output-match-json.md#players) za imena polj). »Uboj« spodaj pomeni uboj
z napadalcem, ne prijateljski uboj in ne samomor (lastna smrt žrtve).

| Polje | Šteje |
|---|---|
| `kills` | uboji sovražnikov, v živi fazi in fazi po koncu |
| `deaths` | vsaka smrt: od sovražnikov, soigralcev, sebe ali sveta |
| `assists` | uboji sovražnikov, ki jih je ta igralec asistiral brez bliskovke (asistent ne sme biti ubijalec) |
| `flashAssists` | uboji sovražnikov, ki jih je ta igralec asistiral z bliskovko |
| `diff` | uboji - smrti |
| `adr` | škoda (izgubljeno zdravje, samo sovražniki, obe fazi) / odigrane runde, ena decimalka |
| `kast` | 100 x (runde z ubojem, asistenco ali asistenco z bliskovko, preživetjem ali maščevano smrtjo) / odigrane runde, ena decimalka. *Preživetje* je: začetni igralec runde, ki v njej ni umrl, v nobeni fazi. |
| `headshotPct` | 100 x uboji v glavo / uboji, ena decimalka; 0, če ni ubojev |
| `openingKills`, `openingDeaths` | dvoboji prvega ubijanja, dobljeni in izgubljeni |
| `tradeKills` | uboji, ki so maščevali smrt soigralca |
| `tradedDeaths` | smrti, ki so bile maščevane |
| `multiKills` | runde z 2, 3, 4 in 5 ubijalci sovražnikov (`2k`, `3k`, `4k`, `5k`); več kot pet se šteje kot `5k`. Štejeta obe fazi. |
| `clutches`, `clutchesWon` | odigrani in osvojeni clutchi (spodaj) |
| `utilityDamage` | škoda z HE granatami, molotovkami in zažigalnimi bombami, ena decimalka |
| `enemiesFlashed` | sovražniki, oslepljeni vsaj **1,0 s** z bliskovkami tega igralca |
| `plants`, `defuses` | postavitve bomb in deaktivacije (vrstice tabele) |
| `teamkills` | ubiti soigralci. Samomor – napadalec in žrtev sta isti igralec, na primer lastna granata – ni tak uboj: je samo smrt. |
| `roundsPlayed` | začete runde, kakor zgoraj |

Igralci so navedeni po imenu ekipe (po abecedi), znotraj ekipe po `diff`, nato po `kills`, najboljši najprej.

Opombe o robovih:

- Uboj v fazi po koncu – zmagovalci lovijo varčujočega igralca – šteje kot uboj, smrt, za ADR, večkratne uboje in KAST
  kot vsak drug.
- Prebojni streli se interno štejejo za igralca, v dokument tekme pa se ne zapišejo; vsak uboj v seznamu rund pove, ali
  je bil tak.
- Del *maščevan* v KAST šteje žrtev maščevane smrti v tisti rundi.
- Prijateljski uboji in samomori dodajo smrt žrtvi, nikomur pa ne dodajo ubojev; prijateljski uboj doda ubijalčevim
  `teamkills`, samomor pa ničemur drugemu.

## Clutchi {#clutches}

Za vsako rundo se začetni igralci obeh strani štejejo kot živi, prek živih ubojev runde pa se gre po vrsti. Po vsaki smrti
se žrtev odstrani in preveri se vsaka stran: stran z natanko **enim** igralcem, in vsaj enim živim sovražnikom, je clutch
za tega igralca **proti** številu sovražnikov, živih v tistem trenutku. Vsak igralec ima največ en clutch na rundo; **osvojen**
je, kadar njegova stran zmaga v rundi.

Posledice definicije:

- Obe strani lahko imata clutch v isti rundi. Če je ena stran najprej padla na enega (na primer 1v3), nato pa je tudi drugi
  padel na enega, je drugi igralec v svojem 1v1 clutchu.
- `against` je število, ko je igralec postal zadnji, ne na koncu.
- Uboji v fazi po koncu se ne prehodijo, zato ne začnejo clutcha in ga ne spremenijo.

## Preživeli {#survivors}

Preživeli runde so za vsako stran njeni začetni igralci minus vsak, ki je umrl, dokler je bila živa. Igralec, ubit v fazi po
koncu med varčevanjem, je še vedno preživel v seznamu rund – vendar ni *preživel* za KAST.

## Seznam rund {#the-round-list}

Vsaka runda v dokumentu tekme nosi svoj izid, rezultat, strani, ekonomijo, postavitev, preživele, clutche in svoje uboje po
vrsti; glejte [Dokument tekme](output-match-json.md#rounds).

## Besedilna lestvica {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <tekma.json>` izpiše ta števila za vsako ekipo; glejte [Ukazi](commands.md#scoreboard---a-match-as-text).
