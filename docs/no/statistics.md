---
title: "Statistikk"
nav_order: 7
lang: "no"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistikk {#statistics}

Hva hver spiller gjorde i en kamp, og hvordan hver runde gikk: resultattavlen og rundelisten i
[kampdokumentet](output-match-json.md). Kode:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Alt telles fra kampen bygget som i [Bygge en kamp](building-matches.md): dens drapsoppføringer, dens
skade (tapt helse, bare fiender), dens blendinger (bare fiender) og dens rader.

![den tekstlige resultattavlen til en syntetisk kamp](../assets/img/scoreboard.svg)

## Konvensjonene {#the-conventions}

Der spillet selv ikke definerer et tall, gjelder disse definisjonene. De er også skrevet inn i hvert
kampdokument under `conventions`.

| Begrep | Definisjon |
|---|---|
| **Trade** | Et dødsfall er *traded* når drapsmannen blir drept av en av offerets lagkamerater innen **5 s**; det drapet er et *trade-drap*. |
| **Åpning** | Rundens første drap på en fiende mens den er live. Et lagkameraddrap, et selvmord eller et dødsfall for verden før det hoppes over. |
| **KAST** | Andelen runder der en spiller fikk et **K**ill, en **A**ssist (en blendingsassist teller), **S**urvived (overlevde), eller ble **T**raded. |
| **Skade** | Helse faktisk tapt, bare fiender: et hodeskudd på 137 skade mot en spiller med 40 helse er 40. |
| **Clutch** | Å være den siste i live på en side med fiender fortsatt oppe; vunnet når siden vinner runden. |
| **Kjøp** | Per side, fra gjennomsnittlig utstyrsverdi ved slutten av freeze time: den første runden i hver ordinære halvdel er en pistolrunde (runde 1, og runden etter halvdelen, så lenge kampen spilte den), forlengelse har ingen; deretter under $1 500 eco, under $4 000 force, ellers full. |

## Hvem som startet hver runde {#who-started-each-round}

Flere tall må vite hvem som spilte en runde. En rundes **startende spillere** er, per side, hver spiller
med en levende posisjonsrad innen ett sekund etter den tidligste posisjonen i den runden (altså i det
første sekundet etter at freeze time tok slutt). En spillers **spilte runder** er antallet runder de
startet. Hvis en spiller ikke startet noen (de hadde aldri en slik rad), brukes kampens rundetall i
stedet, så ingen deling er med null.

## Resultattavlelinjen {#the-scoreboard-line}

Én oppføring per spiller (se [kampdokumentet](output-match-json.md#players) for feltnavnene).
«Fiendedrap» under betyr et drap med en angriper, ikke et lagkameraddrap og ikke et selvmord (spillerens
eget).

| Felt | Teller |
|---|---|
| `kills` | fiendedrap, både i live- og etter-fasen |
| `deaths` | hvert dødsfall: av fiender, lagkamerater, seg selv eller verden |
| `assists` | fiendedrap denne spilleren assisterte uten blending (assistenten må ikke være drapsmannen) |
| `flashAssists` | fiendedrap denne spilleren assisterte med blending |
| `diff` | drap - dødsfall |
| `adr` | skade (tapt helse, bare fiender, begge faser) / spilte runder, én desimal |
| `kast` | 100 x (runder med et drap, en assist eller blendingsassist, overlevelse eller et trade-dødsfall) / spilte runder, én desimal. *Overlevelse* er: en startende spiller i runden som ikke døde i den, i noen av fasene. |
| `headshotPct` | 100 x hodeskuddsdrap / drap, én desimal; 0 uten drap |
| `openingKills`, `openingDeaths` | åpningsduellene vunnet og tapt |
| `tradeKills` | drap som hevnet en lagkamerats dødsfall |
| `tradedDeaths` | dødsfall som ble tradet |
| `multiKills` | runder med 2, 3, 4 og 5 fiendedrap (`2k`, `3k`, `4k`, `5k`); mer enn fem teller som `5k`. Begge faser teller. |
| `clutches`, `clutchesWon` | clutcher spilt og vunnet (under) |
| `utilityDamage` | skade gjort med HE-granater, molotover og brannbomber, én desimal |
| `enemiesFlashed` | fiender blendet i **minst 1,0 s** av denne spillerens blendinger |
| `plants`, `defuses` | bombeplanteringer og desarmeringer (rader i tabellen) |
| `teamkills` | lagkamerater drept. Et selvmord - angriper og offer er samme spiller, en egen granat for eksempel - er ikke ett: det er bare et dødsfall. |
| `roundsPlayed` | runder startet, som over |

Spillere listes etter lagnavn (alfabetisk), og innen et lag etter `diff`, deretter etter `kills`, best
først.

Merknader om kantene:

- Et drap i etter-fasen - vinnerne som jakter en sparende spiller - teller som et drap, et dødsfall, for
  ADR, flerdrap og KAST på samme måte som alle andre.
- Wallbangs telles per spiller internt, men skrives ikke i kampdokumentet; hvert drap i rundelisten sier
  om det var ett.
- KAST-delen *traded* krediterer offeret for et trade-dødsfall i den runden.
- Lagkameraddrap og selvmord gir et dødsfall til offeret, men ikke et drap til noen; et lagkameraddrap gir
  et tillegg til drapsmannens `teamkills`, et selvmord ikke noe annet.

## Clutcher {#clutches}

For hver runde tas de startende spillerne på begge sider som levende, og rundens levende drap gås gjennom
i rekkefølge. Etter hvert dødsfall fjernes offeret, og hver side sjekkes: en side med nøyaktig **én**
spiller igjen, og minst én fiende fortsatt i live, er en clutch for den spilleren **mot** antallet
fiender i live på det øyeblikket. Hver spiller har høyst én clutch per runde; den er **vunnet** når
spillerens side vant runden.

Konsekvenser av definisjonen:

- Begge sider kan ha en clutch i samme runde. Hvis en side først blir nede til én (en 1v3, for eksempel),
  og den andre siden så også blir nede til én, får den andre spilleren en 1v1-clutch for seg selv.
- `against` er telleren da spilleren ble den siste, ikke til slutt.
- Drap i etter-fasen gås ikke gjennom, så de verken starter en clutch eller endrer en.

## Overlevende {#survivors}

En rundes **overlevende** er, per side, dens startende spillere minus alle som døde mens den var live. En
spiller drept i etter-fasen mens de sparte, er fortsatt en overlevende i rundelisten - men overlevde ikke
for KAST.

## Rundelisten {#the-round-list}

Hver runde i kampdokumentet bærer sitt resultat, score, sider, økonomi, plantingen, overlevende, clutcher
og sine drap i rekkefølge; se [kampdokumentet](output-match-json.md#rounds).

## Tekstresultattavlen {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` skriver ut disse tallene per lag; se
[Kommandoer](commands.md#scoreboard---a-match-as-text).
