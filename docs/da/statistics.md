---
title: "Statistik"
nav_order: 7
lang: "da"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistik {#statistics}

Hvad hver spiller gjorde i en kamp, og hvordan hver runde gik: scoreboardet og rundelisten i
[kampdokumentet](output-match-json.md). Kode:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Alt bliver talt ud fra kampen, bygget som på
[Sådan bygges en kamp](building-matches.md): dens kill-poster, dens skade (mistede liv, kun fjender), dens blændinger (kun fjender) og dens rækker.

![den tekstlige scoreboard for en syntetisk kamp](../assets/img/scoreboard.svg)

## Definitionerne {#the-conventions}

Hvor spillet selv ikke definerer et tal, er disse definitionerne. De bliver også skrevet ind i hvert kampdokument under `conventions`.

| Begreb | Definition |
|---|---|
| **Trade** | Et dødsfald er *hævnet* (traded), når dens dræber bliver dræbt af en af offerets holdkammerater inden for **5 s**; den kill er en *trade-kill*. |
| **Åbning** | Rundens første kill af en fjende, mens den er live. Et teamkill, et selvmord eller et dødsfald til verdenen før den bliver sprunget over. |
| **KAST** | Andelen af runder, hvor en spiller fik en **K**ill, en **A**ssist (en blænder-assist tæller), **S**urvived (overlevede) eller blev **T**raded (hævnet). |
| **Skade** | Liv der faktisk er mistet, kun fjender: et hovedskud på 137 skade mod en spiller med 40 liv er 40. |
| **Clutch** | At være den sidste spiller i live på en side, med fjender stadig oppe; vundet, når siden vinder runden. |
| **Køb** | Pr. side, ud fra gennemsnitligt udstyr ved freeze-tidens slutning: den første runde i hver ordinære halvleg er en pistolrunde (runde 1, og runden efter halvlegen, så længe kampen spillede den), overtid har ingen; derefter under $1.500 eco, under $4.000 force, ellers full. |

## Hvem startede hver runde {#who-started-each-round}

Flere tal skal vide, hvem der spillede en runde. En runde's **startende spillere** er, pr. side, hver spiller med en levende positionsrække inden for et sekund af rundens tidligste position (altså i det første sekund efter freeze-tiden sluttede). En spillers **spillede runder** er antallet af runder, de startede. Hvis en spiller ikke startede nogen (de havde ingen sådan række), bliver kampens rundetal brugt i stedet, så der aldrig er en division med nul.

## Scoreboard-linjen {#the-scoreboard-line}

Én post pr. spiller (se [kampdokumentet](output-match-json.md#players) for feltnavnene). "Fjende-kill" nedenfor betyder en kill med en angriber, ikke et teamkill og ikke et selvmord (offerets eget).

| Felt | Tæller |
|---|---|
| `kills` | fjende-kills, både i live- og efter-fasen |
| `deaths` | hvert dødsfald: af fjender, holdkammerater, sig selv eller verdenen |
| `assists` | fjende-kills, denne spiller assisterede uden blænder (assisteren må ikke være dræberen) |
| `flashAssists` | fjende-kills, denne spiller assisterede med en blænder |
| `diff` | kills - døde |
| `adr` | skade (mistede liv, kun fjender, begge faser) / spillede runder, én decimal |
| `kast` | 100 x (runder med en kill, en assist eller blænder-assist, overlevelse eller en hævnet død) / spillede runder, én decimal. *Overlevelse* er: en startende spiller i runden, der ikke døde i den, i begge faser. |
| `headshotPct` | 100 x hovedskudskills / kills, én decimal; 0 uden kills |
| `openingKills`, `openingDeaths` | åbningsdueller vundet og tabt |
| `tradeKills` | kills, der hævnede en holdkammerats død |
| `tradedDeaths` | dødsfald, der blev hævnet |
| `multiKills` | runder med 2, 3, 4 og 5 fjende-kills (`2k`, `3k`, `4k`, `5k`); mere end fem tæller som `5k`. Begge faser tæller. |
| `clutches`, `clutchesWon` | clutches spillet og vundet (nedenfor) |
| `utilityDamage` | skade gjort med HE-granater, molotovs og incendiaries, én decimal |
| `enemiesFlashed` | fjender blændet i **mindst 1,0 s** af denne spillers blændere |
| `plants`, `defuses` | bombeplantninger og desarmeringer (rækker i tabellen) |
| `teamkills` | holdkammerater dræbt. Et selvmord - angriber og offer den samme spiller, en egen granat for eksempel - tæller ikke: det er kun et dødsfald. |
| `roundsPlayed` | runder startet, som ovenfor |

Spillere står på listen efter holdnavn (alfabetisk), og inden for et hold efter
`diff`, derefter `kills`, bedst først.

Bemærkninger om kanterne:

- En kill i efter-fasen - vinderne, der jager en sparende spiller - tæller som en kill, et dødsfald, for ADR, multi-kills og KAST ligesom enhver anden.
- Wallbangs bliver talt pr. spiller internt, men ikke skrevet i kampdokumentet; hver kill i rundelisten siger, om den var en.
- KAST-delen *traded* krediterer offeret for et hævnet dødsfald i den runde.
- Teamkills og selvmord lægger et dødsfald til offeret, men ingen kill til nogen; et teamkill lægger til dræberens `teamkills`, et selvmord til intet andet.

## Clutches {#clutches}

For hver runde bliver de startende spillere på begge sider taget som levende, og rundens live-kills bliver gennemgået i rækkefølge. Efter hvert dødsfald bliver offeret fjernet, og hver side bliver set efter: en side med præcis **én** spiller tilbage, og mindst én fjende stadig i live, er en clutch for den spiller **mod** det antal fjender, der er i live på det øjeblik. Hver spiller har højst én clutch pr. runde; den er **vundet**, når spillerens side vinder runden.

Konsekvenser af definitionen:

- Begge sider kan have en clutch i samme runde. Hvis en side først bliver nede på én (en 1v3, for eksempel), og den anden side så også bliver nede på én, er den anden spiller i en 1v1-clutch for sig selv.
- `against` er tallet, da spilleren blev den sidste, ikke ved slutningen.
- Kills i efter-fasen bliver ikke gennemgået, så de hverken starter en clutch eller ændrer en.

## Overlevende {#survivors}

En rundes **overlevende** er, pr. side, dens startende spillere minus alle, der døde, mens den var live. En spiller, der bliver dræbt i efter-fasen, mens de sparer, er stadig en overlevende i rundelisten - men overlevede ikke til KAST.

## Rundelisten {#the-round-list}

Hver runde i kampdokumentet bærer sit resultat, score, sider, økonomi, plantning, overlevende, clutches og sine kills i rækkefølge; se
[Kampdokumentet](output-match-json.md#rounds).

## Tekst-scoreboardet {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` udskriver disse tal pr. hold;
se [Kommandoer](commands.md#scoreboard---a-match-as-text).
