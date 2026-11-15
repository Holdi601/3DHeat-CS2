---
title: Statistike
nav_order: 7
lang: "bs"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistike {#statistics}

Šta je svaki igrač uradio u meču, i kako je tekla svaka runda: tabela rezultata i
lista rundi [dokumenta meča](output-match-json.md). Kod:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Sve se računa iz meča izgrađenog kako je opisano u
[Slaganju meča](building-matches.md): njegovih zapisa ubistava, njegove štete (izgubljeno
zdravlje, samo neprijatelji), njegovih zasljepljenja (samo neprijatelji) i njegovih redova.

![tekstualna tabela rezultata sintetičkog meča](../assets/img/scoreboard.svg)

## Konvencije {#the-conventions}

Gdje sama igra ne definiše broj, ovo su definicije.
Upisane su i u svaki dokument meča pod `conventions`.

| Pojam | Definicija |
|---|---|
| **Trade** | Smrt je *traded* kad njenog ubicu ubije neki od žrtvinih saigrača unutar **5 s**; to ubistvo je *trade ubistvo*. |
| **Opening** | Prvo ubistvo neprijatelja u rundi dok je živa. Teamkill, samoubistvo ili smrt od svijeta prije njega preskaču se. |
| **KAST** | Udio rundi u kojima je igrač imao **K**ill (ubistvo), **A**ssist (asistenciju; flash asistencija se računa), **S**urvived (preživio) ili je bio **T**raded (osvećen). |
| **Damage** | Zaista izgubljeno zdravlje, samo neprijatelji: headshot od 137 štete na igraču sa 40 zdravlja je 40. |
| **Clutch** | Biti zadnji živi igrač na strani dok neprijatelji još stoje; dobijen kad strana dobije rundu. |
| **Buy** | Po strani, iz prosječne vrijednosti opreme na kraju freeze vremena: prva runda svakog regularnog poluvremena je pištolj runda (runda 1, i runda poslije poluvremena, ako ju je meč odigrao), produžetak je nema; zatim ispod $1.500 eco, ispod $4.000 force, inače full. |

## Ko je započeo svaku rundu {#who-started-each-round}

Nekoliko brojeva treba znati ko je igrao rundu. **Početni igrači** runde su,
po strani, svaki igrač sa živim redom pozicije unutar jedne sekunde od najranije
pozicije te runde (to jest, u prvoj sekundi nakon završetka freeze vremena).
**Odigrane runde** igrača su broj rundi koje je započeo. Ako igrač nije započeo nijednu
(nikad nije imao takav red), umjesto toga koristi se broj rundi meča, da nijedno
dijeljenje nije nulom.

## Red tabele rezultata {#the-scoreboard-line}

Jedan unos po igraču (imena polja vidi u [dokumentu meča](output-match-json.md#players)).
"Ubistvo neprijatelja" ispod znači ubistvo s napadačem, ne
teamkill, i ne samoubistvo (žrtvino vlastito).

| Polje | Broji |
|---|---|
| `kills` | ubistva neprijatelja, iz žive faze i faze poslije |
| `deaths` | svaka smrt: od neprijatelja, saigrača, samog sebe ili svijeta |
| `assists` | ubistva neprijatelja kojima je ovaj igrač asistirao bez fleša (asistent ne smije biti ubica) |
| `flashAssists` | ubistva neprijatelja kojima je ovaj igrač asistirao flešom |
| `diff` | ubistva - smrti |
| `adr` | šteta (izgubljeno zdravlje, samo neprijatelji, obje faze) / odigrane runde, jedna decimala |
| `kast` | 100 x (runde s ubistvom, asistencijom ili flash asistencijom, preživljavanjem ili osvećenom smrću) / odigrane runde, jedna decimala. *Preživljavanje* je: početni igrač runde koji u njoj nije poginuo, ni u jednoj fazi. |
| `headshotPct` | 100 x headshot ubistva / ubistva, jedna decimala; 0 bez ubistava |
| `openingKills`, `openingDeaths` | dobijeni i izgubljeni opening dvoboji |
| `tradeKills` | ubistva koja su osvetila smrt saigrača |
| `tradedDeaths` | smrti koje su osvećene |
| `multiKills` | runde s 2, 3, 4 i 5 ubistava neprijatelja (`2k`, `3k`, `4k`, `5k`); više od pet računa se kao `5k`. Računaju se obje faze. |
| `clutches`, `clutchesWon` | odigrani i dobijeni clutchevi (ispod) |
| `utilityDamage` | šteta nanesena HE granatama, molotovima i incendiary granatama, jedna decimala |
| `enemiesFlashed` | neprijatelji zasljepljeni **barem 1,0 s** flešovima ovog igrača |
| `plants`, `defuses` | postavljanja i deaktiviranja bombe (redovi tabele) |
| `teamkills` | ubijeni saigrači. Samoubistvo - napadač i žrtva isti igrač, recimo vlastita granata - nije jedno od njih: to je samo smrt. |
| `roundsPlayed` | započete runde, kako je gore |

Igrači su navedeni po imenu tima (abecednim redom), a unutar tima po
`diff`, zatim po `kills`, najbolji prvi.

Napomene o rubnim slučajevima:

- Ubistvo u fazi poslije - pobjednici love igrača koji se spašava - računa se
  kao ubistvo, smrt, za ADR, multi-kills i KAST kao i svako drugo.
- Wallbangovi se interno broje po igraču ali se ne upisuju u
  dokument meča; svako ubistvo u listi rundi kaže je li bio jedan.
- Dio KAST-a *traded* priznaje žrtvi osvećene smrti u toj rundi.
- Teamkillovi i samoubistva dodaju smrt žrtvi ali ne ubistvo nikome;
  teamkill dodaje ubičinom `teamkills`, samoubistvo ništa drugo.

## Clutchevi {#clutches}

Za svaku rundu, početni igrači obje strane uzimaju se kao živi, a
žive runde ubistva prolaze se redom. Nakon svake smrti žrtva se
uklanja, i gleda se svaka strana: strana s tačno **jednim** igračem
preostalim, i barem jednim neprijateljem još živim, je clutch za tog igrača
**protiv** broja neprijatelja živih u tom trenutku. Svaki igrač ima
najviše jedan clutch po rundi; **dobijen** je kad je strana tog igrača dobila
rundu.

Posljedice definicije:

- Obje strane mogu imati clutch u jednoj rundi. Ako je jedna strana prva svedena na jednog
  (recimo 1v3), a zatim i druga strana bude svedena na jednog,
  drugi igrač je u vlastitom 1v1 clutchu.
- `against` je broj kad je igrač postao zadnji, ne na kraju.
- Ubistva iz faze poslije se ne prolaze, pa ne počinju clutch
  niti ga mijenjaju.

## Preživjeli {#survivors}

**Preživjeli** runde su, po strani, njeni početni igrači minus svi
koji su poginuli dok je bila živa. Igrač ubijen u fazi poslije dok se spašava
i dalje je preživjeli u listi rundi - ali nije *preživio* za KAST.

## Lista rundi {#the-round-list}

Svaka runda dokumenta meča nosi svoj rezultat, bodove, strane, ekonomiju, postavljanje bombe,
preživjele, clutcheve i svoja ubistva redom; pogledajte
[Dokument meča](output-match-json.md#rounds).

## Tekstualna tabela rezultata {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` ispisuje ove brojeve po timu;
pogledajte [Komande](commands.md#scoreboard---a-match-as-text).
