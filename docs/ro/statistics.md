---
title: Statistici
nav_order: 7
lang: "ro"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistici {#statistics}

Ce a făcut fiecare jucător într-un meci și cum a decurs fiecare rundă: tabelul de scor și
lista rundelor din [documentul meciului](output-match-json.md). Cod:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Totul este numărat din meciul construit ca în [Cum se construiește un meci](building-matches.md):
înregistrările sale de eliminare, daunele sale (sănătate pierdută, doar inamici), orbirile
sale (doar inamici) și rândurile sale.

![tabelul de scor text al unui meci sintetic](../assets/img/scoreboard.svg)

## Convențiile {#the-conventions}

Acolo unde jocul însuși nu definește o cifră, acestea sunt definițiile. Sunt scrise și în
fiecare document de meci, la `conventions`.

| Termen | Definiție |
|---|---|
| **Răzbunare** (*trade*) | O moarte este *răzbunată* când ucigașul său este eliminat de unul dintre coechipierii victimei în **5 s**; eliminarea aceea este o *eliminare de răzbunare*. |
| **Deschidere** | Prima eliminare a unui inamic din rundă, cât timp este live. Un teamkill, o sinucidere sau o moarte provocată de lume dinaintea ei sunt ignorate. |
| **KAST** | Procentul rundelor în care un jucător a făcut o **K**ill (eliminare), o **A**ssist (asistență; asistența de flash contează), a **S**upraviețuit sau a fost **T**raded (răzbunat). |
| **Daune** | Sănătatea efectiv pierdută, doar inamici: o lovitură în cap de 137 de daune asupra unui jucător cu 40 de sănătate înseamnă 40. |
| **Clutch** | A fi ultimul jucător în viață de pe o parte, cu inamici încă în picioare; câștigat când partea câștigă runda. |
| **Cumpărare** (*buy*) | Pe parte, din valoarea medie a echipamentului la sfârșitul timpului de îngheț: prima rundă a fiecărei reprize regulamentare este rundă de pistol (runda 1, și runda de după repriză, atâta timp cât meciul a jucat-o); prelungirea nu are niciuna; apoi sub 1.500 $ eco, sub 4.000 $ force, altfel full. |

## Cine a început fiecare rundă {#who-started-each-round}

Mai multe cifre trebuie să știe cine a jucat o rundă. Jucătorii de **start** ai unei runde
sunt, pe fiecare parte, fiecare jucător cu un rând de poziție în viață în interval de o
secundă de cea mai timpurie poziție a rundei (adică în prima secundă după terminarea
timpului de îngheț). **Rundele jucate** ale unui jucător sunt numărul rundelor pe care le-a
început. Dacă un jucător nu a început niciuna (nu a avut un astfel de rând), se folosește
în schimb numărul de runde al meciului, ca să nu existe nicio împărțire la zero.

## Linia de tabel de scor {#the-scoreboard-line}

Câte o intrare pentru fiecare jucător (vezi [documentul meciului](output-match-json.md#players)
pentru numele câmpurilor). „Eliminare de inamic” mai jos înseamnă o eliminare cu un atacator,
nu un teamkill și nu o sinucidere (propria victimă).

| Câmp | Numără |
|---|---|
| `kills` | eliminări de inamici, din faza live și din cea după |
| `deaths` | fiecare moarte: de inamici, de coechipieri, de sine sau de lume |
| `assists` | eliminări de inamici pe care jucătorul le-a asistat fără flash (asistentul nu trebuie să fie ucigașul) |
| `flashAssists` | eliminări de inamici pe care jucătorul le-a asistat cu un flash |
| `diff` | eliminări - morți |
| `adr` | daune (sănătate pierdută, doar inamici, ambele faze) / runde jucate, o zecimală |
| `kast` | 100 x (runde cu o eliminare, o asistență sau asistență de flash, supraviețuire sau o moarte răzbunată) / runde jucate, o zecimală. *Supraviețuirea* înseamnă: un jucător de start al rundei care nu a murit în ea, în niciuna dintre faze. |
| `headshotPct` | 100 x eliminări în cap / eliminări, o zecimală; 0 fără eliminări |
| `openingKills`, `openingDeaths` | dueluri de deschidere câștigate și pierdute |
| `tradeKills` | eliminări care au răzbunat moartea unui coechipier |
| `tradedDeaths` | morți care au fost răzbunate |
| `multiKills` | runde cu 2, 3, 4 și 5 eliminări de inamici (`2k`, `3k`, `4k`, `5k`); mai mult de cinci se numără ca `5k`. Ambele faze se numără. |
| `clutches`, `clutchesWon` | clutch-uri jucate și câștigate (mai jos) |
| `utilityDamage` | daune făcute cu grenade HE, molotov și incendiare, o zecimală |
| `enemiesFlashed` | inamici orbiți timp de **cel puțin 1,0 s** de flash-urile acestui jucător |
| `plants`, `defuses` | plantări și dezamorsări de bombă (rândurile tabelului) |
| `teamkills` | coechipieri uciși. O sinucidere - atacatorul și victima sunt același jucător, o grenadă proprie, de exemplu - nu este una: este doar o moarte. |
| `roundsPlayed` | runde începute, ca mai sus |

Jucătorii sunt listați pe echipă (alfabetic), iar în cadrul unei echipe după `diff`, apoi
după `kills`, cel mai bun întâi.

Note despre margini:

- O eliminare din faza după - câștigătorii vânând un jucător care economisește - se numără
  ca eliminare, moarte, pentru ADR, multi-eliminări și KAST, la fel ca oricare alta.
- Lovitura prin perete este numărată intern pe jucător, dar nu este scrisă în documentul
  meciului; fiecare eliminare din lista rundei spune dacă a fost una.
- Partea *răzbunat* din KAST îi creditează victimei unei morți răzbunate din acea rundă.
- Teamkill-urile și sinuciderile adaugă o moarte victimei, dar nicio eliminare nimănui; un
  teamkill adaugă la `teamkills` al ucigașului, o sinucidere nu adaugă la nimic altceva.

## Clutch-uri {#clutches}

Pentru fiecare rundă, jucătorii de start ai ambelor părți sunt considerați în viață, iar
eliminările live ale rundei sunt parcurse în ordine. După fiecare moarte, victima este
scoasă, iar fiecare parte este privită: o parte cu exact **un** jucător rămas, și cel puțin
un inamic încă în viață, este un clutch pentru acel jucător **împotriva** numărului de
inamici în viață în acel moment. Fiecare jucător are cel mult un clutch pe rundă; este
**câștigat** când partea acelui jucător a câștigat runda.

Consecințele definiției:

- Ambele părți pot avea un clutch în aceeași rundă. Dacă o parte rămâne cu unul primul (un
  1v3, de exemplu) și cealaltă parte este apoi și ea redusă la unul, al doilea jucător este
  într-un clutch 1v1 propriu.
- `against` este numărul când jucătorul a devenit ultimul, nu cel de la sfârșit.
- Eliminările din faza după nu sunt parcurse, deci nu încep un clutch și nu îl schimbă.

## Supraviețuitori {#survivors}

**Supraviețuitorii** unei runde sunt, pe fiecare parte, jucătorii ei de start minus toți cei
care au murit cât timp a fost live. Un jucător ucis în faza după, în timp ce salva, este tot
supraviețuitor în lista rundei - dar nu a *supraviețuit* pentru KAST.

## Lista rundelor {#the-round-list}

Fiecare rundă din documentul meciului poartă rezultatul, scorul, părțile, economia, plantarea,
supraviețuitorii, clutch-urile și eliminările sale în ordine; vezi
[Documentul meciului](output-match-json.md#rounds).

## Tabelul de scor text {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` afișează aceste cifre pe echipă; vezi
[Comenzi](commands.md#scoreboard---a-match-as-text).
