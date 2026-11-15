---
title: "Statistika"
nav_order: 7
lang: "hr"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistika {#statistics}

Što je svaki igrač napravio u meču i kako je svaka runda prošla: rezultatna tablica i popis rundi u [dokumentu meča](output-match-json.md). Kod:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Sve se broji iz meča izgrađenog kako je opisano na [Sastavljanje meča](building-matches.md): njegovi zapisi ubojstava, njegova šteta (izgubljeno zdravlje, samo neprijatelji), njegova slijepila (samo neprijatelji) i njegovi redci.

![tekstualna rezultatna tablica sintetičkog meča](../assets/img/scoreboard.svg)

## Konvencije {#the-conventions}

Gdje sama igra ne definira broj, ovo su definicije. Upisane su i u svaki dokument meča, pod `conventions`.

| Pojam | Definicija |
|---|---|
| **Razmjena (trade)** | Smrt je *razmijenjena* kad njezinu ubojicu ubije jedan od žrtvinih suigrača unutar **5 s**; to ubojstvo je *ubojstvo razmjenom*. |
| **Prvo ubojstvo (opening)** | Prvo ubojstvo neprijatelja u rundi dok je živa. Teamkill, samoubojstvo ili smrt od svijeta prije njega se preskače. |
| **KAST** | Udio rundi u kojima je igrač imao **K**ill (ubojstvo), **A**ssist (asistenciju; asistencija bljeskom se računa), **S**urvived (preživio) ili je bio **T**raded (razmijenjen). |
| **Šteta (Damage)** | Zdravlje stvarno izgubljeno, samo neprijatelji: pogodak u glavu od 137 štete na igraču s 40 zdravlja je 40. |
| **Clutch** | Biti zadnji živi igrač na strani dok su neprijatelji još stajali; osvojen kad strana pobijedi rundu. |
| **Kupovina (Buy)** | Po strani, iz prosječne vrijednosti opreme na kraju freeze timea: prva runda svakog regularnog poluvremena je runda s pištoljima (runda 1, i runda nakon poluvremena, ako ju je meč odigrao); produženje ih nema; zatim ispod 1.500 $ eco, ispod 4.000 $ force, inače full. |

## Tko je počeo svaku rundu {#who-started-each-round}

Nekoliko brojeva treba znati tko je odigrao rundu. **Početni igrači** runde su, po strani, svaki igrač s živim retkom položaja unutar jedne sekunde od najranijeg položaja te runde (to jest, u prvoj sekundi nakon što je freeze time završio). **Odigrane runde** igrača je broj rundi koje je započeo. Ako nije započeo nijednu (nikad nije imao takav redak), koristi se broj rundi meča, kako se ne bi dijelilo nulom.

## Redak rezultatne tablice {#the-scoreboard-line}

Jedan unos po igraču (vidi [dokument meča](output-match-json.md#players) za imena polja). "Neprijateljsko ubojstvo" dolje je ubojstvo s napadačem, a ne teamkill, i ne samoubojstvo (žrtvino vlastito).

| Polje | Broji |
|---|---|
| `kills` | neprijateljska ubojstva, iz žive i iz faze nakon |
| `deaths` | svaka smrt: od neprijatelja, suigrača, sebe ili svijeta |
| `assists` | neprijateljska ubojstva koja je ovaj igrač asistirao bez bljeska (asistent ne smije biti ubojica) |
| `flashAssists` | neprijateljska ubojstva koja je ovaj igrač asistirao bljeskom |
| `diff` | kills - deaths |
| `adr` | šteta (izgubljeno zdravlje, samo neprijatelji, obje faze) / odigrane runde, jedna decimala |
| `kast` | 100 x (runde s ubojstvom, asistencijom ili asistencijom bljeskom, preživljavanjem ili razmijenjenom smrću) / odigrane runde, jedna decimala. *Preživljavanje* je: početni igrač runde koji nije umro u njoj, u bilo kojoj fazi. |
| `headshotPct` | 100 x ubojstva u glavu / ubojstva, jedna decimala; 0 bez ubojstava |
| `openingKills`, `openingDeaths` | prvi dvoboji dobiveni i izgubljeni |
| `tradeKills` | ubojstva koja su razmijenila smrt suigrača |
| `tradedDeaths` | smrti koje su razmijenjene |
| `multiKills` | runde s 2, 3, 4 i 5 neprijateljskih ubojstava (`2k`, `3k`, `4k`, `5k`); više od pet broji se kao `5k`. Obje faze se računaju. |
| `clutches`, `clutchesWon` | odigrani i osvojeni clutchevi (dolje) |
| `utilityDamage` | šteta nanesena HE granatama, molotovima i zapaljivim granatama, jedna decimala |
| `enemiesFlashed` | neprijatelji zaslijepljeni najmanje **1,0 s** bljeskovima ovog igrača |
| `plants`, `defuses` | postavljanja bombi i deaktivacije (retci tablice) |
| `teamkills` | ubijeni suigrači. Samoubojstvo - napadač i žrtva isti igrač, npr. vlastita granata - nije to: samo je smrt. |
| `roundsPlayed` | započete runde, kako je gore opisano |

Igrači su navedeni po nazivu tima (abecedno), a unutar tima po `diff`, pa po `kills`, najbolji prvi.

Napomene o rubovima:

- Ubojstvo u fazi nakon - pobjednici love igrača koji štedi - broji se kao ubojstvo, smrt, za ADR, višestruka ubojstva i KAST kao i svako drugo.
- Pogoci u zid broje se interno po igraču, ali se ne zapisuju u dokument meča; svako ubojstvo u popisu rundi kaže je li bilo takvo.
- Dio *razmijenjen* u KAST-u pripisuje se žrtvi razmijenjene smrti u toj rundi.
- Teamkillovi i samoubojstva dodaju smrt žrtvi, ali nikome ne dodaju ubojstvo; teamkill dodaje `teamkills` ubojici, a samoubojstvo ni na što drugo.

## Clutchevi {#clutches}

Za svaku rundu, početni igrači obje strane uzimaju se kao živi, pa se prolazi kroz žive ubojstva runde redom. Nakon svake smrti žrtva se uklanja, i gleda se svaka strana: strana s točno **jednim** igračem koji je ostao, i s barem jednim neprijateljem još živim, je clutch za tog igrača **protiv** broja neprijatelja živih u tom trenutku. Svaki igrač ima najviše jedan clutch po rundi; **osvojen** je kad je strana tog igrača pobijedila rundu.

Posljedice ove definicije:

- Obje strane mogu imati clutch u istoj rundi. Ako strana prvo padne na jednog (npr. 1v3), a druga strana se također svede na jednog, drugi igrač je u vlastitom clutchu 1v1.
- `against` je broj kad je igrač postao zadnji, a ne na kraju.
- Ubojstva iz faze nakon se ne prolaze, pa ne pokreću clutch niti ga mijenjaju.

## Preživjeli {#survivors}

**Preživjeli** runde su, po strani, njezini početni igrači minus svi koji su umrli dok je bila živa. Igrač ubijen u fazi nakon dok štedi i dalje je preživjeli u popisu rundi - ali nije *preživio* za KAST.

## Popis rundi {#the-round-list}

Svaka runda u dokumentu meča nosi svoj rezultat, rezultat tablice, strane, ekonomiju, postavljanje, preživjele, clutcheve i svoja ubojstva redom; vidi [Dokument meča](output-match-json.md#rounds).

## Tekstualna rezultatna tablica {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <meč.json>` ispisuje ove brojeve po timu; vidi [Naredbe](commands.md#scoreboard---a-match-as-text).
