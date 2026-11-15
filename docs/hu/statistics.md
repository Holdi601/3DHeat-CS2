---
title: "Statisztika"
nav_order: 7
lang: "hu"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statisztika {#statistics}

Mit csinált egy játékos a meccsen, és hogyan ment minden kör: az eredménytábla és a körlista a
[meccsdokumentumban](output-match-json.md). Kód:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Minden abból számolódik, ahogy a [Meccs felépítése](building-matches.md) oldalon felépül a meccs: a gyilkossági
rekordjaiból, a sebzéséből (az elvesztett életerő, csak ellenségek), a vakításaiból (csak ellenségek) és a sorainak
összességéből.

![egy szintetikus meccs szöveges eredménytáblája](../assets/img/scoreboard.svg)

## A konvenciók {#the-conventions}

Ahol maga a játék nem határoz meg egy számot, ezek a meghatározások. Minden meccsdokumentumban is benne vannak a
`conventions` alatt.

| Fogalom | Meghatározás |
|---|---|
| **Trade** | Egy halált *megbosszultnak* (traded) nevezünk, ha a gyilkosát az áldozat egyik csapattársa megöli **5 s**-on belül; ez a gyilkosság a *trade-gyilkosság*. |
| **Nyitó** | A kör első gyilkossága egy ellenségen, amíg az élő. Egy csapattárs-ölés, egy öngyilkosság vagy egy halál a világnak ezt megelőzően kimarad. |
| **KAST** | Azoknak a köröknek az aránya, amelyekben a játékos **K**-t ölt (gyilkosság), **A**-t asszisztál (a villantási asszisztálás is számít), **S**-t túlél (survived), vagy **T**-t megbosszulják (traded). |
| **Sebzés** | Ténylegesen elvesztett életerő, csak ellenségek: egy 137-es fejlövés 40 életerejű játékosnál 40. |
| **Klucs** (clutch) | Az utolsó élő játékos az oldalán úgy, hogy még ellenségek állnak; megnyerve, ha az oldala nyeri a kört. |
| **Vásárlás** (buy) | Oldalanként, a freeze time végi átlagos felszerelési érték alapján: a szabályos félidő első köre pisztolykör (az 1. kör, és a félidő utáni kör, amennyiben a meccs játszotta), a hosszabbításnak nincs; utána $1500 alatt eco, $4000 alatt force, egyébként full. |

## Kik kezdték az egyes köröket {#who-started-each-round}

Néhány szám tudni akarja, ki játszotta a kört. Egy kör **kezdő játékosai** oldalanként mindazok, akiknek a kör
legkorábbi pozíciójától számított egy másodpercen belül élő pozíciósora van (vagyis a freeze time vége utáni első
másodpercben). Egy játékos **lejátszott köreinek** száma azoknak a köröknek a száma, amelyeket elkezdett. Ha egy játékos egyet
sem kezdett (nem volt ilyen sora), a meccs körszámát használjuk, hogy ne legyen nullával osztás.

## Az eredménytábla-sor {#the-scoreboard-line}

Játékosonként egy bejegyzés (a mezőneveket lásd: [a meccsdokumentum](output-match-json.md#players)). Az alábbi
"ellenséges gyilkosság" olyan gyilkosságot jelent, amelynek van támadója, nem csapattárs-ölés, és nem öngyilkosság (az
áldozat saját maga).

| Mező | Mit számol |
|---|---|
| `kills` | ellenséges gyilkosságok, az élő és az utána fázisban is |
| `deaths` | minden halál: ellenségtől, csapattárstól, saját magától vagy a világtól |
| `assists` | ellenséges gyilkosságok, amelyeket ez a játékos villantás nélkül asszisztált (az asszisztáló nem lehet a gyilkos) |
| `flashAssists` | ellenséges gyilkosságok, amelyeket ez a játékos villantással asszisztált |
| `diff` | gyilkosság - halál |
| `adr` | sebzés (elvesztett életerő, csak ellenségek, mindkét fázisban) / lejátszott körök, egy tizedesjegy |
| `kast` | 100 x (azoknak a köröknek a száma, amelyekben volt gyilkosság, asszisztálás vagy villantási asszisztálás, túlélés vagy megbosszult halál) / lejátszott körök, egy tizedesjegy. *Túlélés*: a kör egy kezdő játékosa, aki nem halt meg benne, bármelyik fázisban. |
| `headshotPct` | 100 x fejlövéses gyilkosságok / gyilkosságok, egy tizedesjegy; 0, ha nincs gyilkosság |
| `openingKills`, `openingDeaths` | megnyert és elvesztett nyitó párharcok |
| `tradeKills` | gyilkosságok, amelyek egy csapattárs halálát megbosszulták |
| `tradedDeaths` | megbosszult halálok |
| `multiKills` | azoknak a köröknek a száma, amelyekben 2, 3, 4 és 5 ellenséges gyilkosság volt (`2k`, `3k`, `4k`, `5k`); az ötnél több az `5k`. Mindkét fázis számít. |
| `clutches`, `clutchesWon` | játszott és megnyert klucsok (lent) |
| `utilityDamage` | HE-gránátokkal, molotovval és incendiary-vel okozott sebzés, egy tizedesjegy |
| `enemiesFlashed` | ellenségek, akiket ennek a játékosnak a villanásai legalább **1,0 s**-ig megvakítottak |
| `plants`, `defuses` | bomba-lerakások és hatástalanítások (a táblázat sorai) |
| `teamkills` | megölt csapattársak. Az öngyilkosság - a támadó és az áldozat ugyanaz a játékos, mondjuk a saját gránátja - nem ilyen: csak egy halál. |
| `roundsPlayed` | elkezdett körök, ahogy fent |

A játékosok csapatnév szerint vannak felsorolva (ábécé szerint), a csapatukon belül a `diff`, majd a `kills` szerint, a
legjobb elöl.

A széleken:

- Egy gyilkosság az utána fázisban - amikor a győztesek vadásszák a menekülő játékost - ugyanúgy gyilkosság és halál a
  ADR-nál, többes gyilkosságnál és a KAST-nál, mint bármely más.
- A falon át lövéseket játékosonként belül számoljuk, de nem írjuk a meccsdokumentumba; a körlista minden gyilkossága
  megmondja, hogy volt-e ilyen.
- A KAST *megbosszult* része azt a játékost jóváírja, akinek a megbosszult halála volt abban a körben.
- A csapattárs-ölések és az öngyilkosságok halált adnak az áldozatnak, de senkinek nem adnak gyilkosságot; egy
  csapattárs-ölés a gyilkos `teamkills`-ét növeli, egy öngyilkosság semmi mást nem.

## Klucsok {#clutches}

Minden körben a két oldal kezdő játékosait élőnek vesszük, és a kör élő gyilkosságait sorrendben bejárjuk. Minden halál
után eltávolítjuk az áldozatot, és minden oldalt megnézünk: az az oldal, amelyen pontosan **egy** játékos maradt, és
legalább egy ellenség még áll, az a játékos klucsa **az ellenség ellen**, azok számával, akik abban a pillanatban élnek.
Minden játékosnak legfeljebb egy klucsa van körönként; akkor **nyert**, ha az oldala megnyerte a kört.

A meghatározásból következik:

- Mindkét oldalnak lehet klucsa egy körben. Ha az egyik oldal előbb marad egyre (mondjuk egy 1v3), és a másik oldal is
  egyre csökken, a második játékos saját 1v1-es klucsban van.
- Az `against` az az érték, amikor a játékos az utolsó lett, nem a kör végén.
- Az utána fázis gyilkosságait nem járjuk be, így nem indítanak klucsot, és nem változtatnak egyen sem.

## Túlélők {#survivors}

Egy kör **túlélői** oldalanként a kezdő játékosai, mínusz mindazok, akik az élő alatt haltak meg. Az utána fázisban megölt
játékos, aki mentés közben halt meg, a körlistában továbbra is túlélő - de a KAST szempontjából nem élte túl.

## A körlista {#the-round-list}

A meccsdokumentum minden körének van az eredménye, állása, oldalai, gazdasága, lerakása, túlélői, klucsai és gyilkosságai
sorrendben; lásd [A meccsdokumentum](output-match-json.md#rounds).

## A szöveges eredménytábla {#the-text-scoreboard}

A `python -m heat3d_cs2 scoreboard <match.json>` ezeket a számokat írja ki csapatonként; lásd
[Parancsok](commands.md#scoreboard---a-match-as-text).
