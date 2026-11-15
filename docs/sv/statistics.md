---
title: "Statistik"
nav_order: 7
lang: "sv"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistik {#statistics}

Vad varje spelare gjorde i en match, och hur varje runda gick: resultattavlan och rundlistan i
[matchdokumentet](output-match-json.md). Kod:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Allt räknas från matchen så som den byggs på [Bygga en match](building-matches.md): dess killposter, dess
skada (förlorad hälsa, endast fiender), dess blindningar (endast fiender) och dess rader.

![den textbaserade resultattavlan för en syntetisk match](../assets/img/scoreboard.svg)

## Konventionerna {#the-conventions}

Där spelet självt inte definierar ett tal är det här definitionerna. De skrivs också in i varje
matchdokument under `conventions`.

| Term | Definition |
|---|---|
| **Trade** | Ett dödsfall är *traded* när dess mördare dödas av någon av offrets lagkamrater inom **5 s**; den killen är en *trade-kill*. |
| **Opening** | Rundans första kill av en fiende medan den är levande. En teamkill, ett suicide eller ett dödsfall för världen före den hoppas över. |
| **KAST** | Andelen rundor där en spelare fick en **K**ill, en **A**ssist (en flashassist räknas), **S**urvived (överlevde), eller blev **T**raded. |
| **Damage** | Hälsa som faktiskt förlorades, endast fiender: en huvudträff på 137 skada mot en spelare med 40 hälsa är 40. |
| **Clutch** | Att vara den sista spelaren kvar levande på en sida när fiender fortfarande står; vunnen när sidan vinner rundan. |
| **Buy** | Per sida, från genomsnittligt utrustningsvärde vid slutet av freeze time: första rundan i varje ordinarie halvlek är en pistolrunda (runda 1, och rundan efter halvleken, så länge matchen spelade den); övertid har ingen; sedan under 1 500 $ eco, under 4 000 $ force, annars full. |

## Vilka som började varje runda {#who-started-each-round}

Flera tal behöver veta vem som spelade en runda. En rundas **startande spelare** är, per sida, varje
spelare med en levande positionsrad inom en sekund från rundans tidigaste position (det vill säga under
den första sekunden efter att freeze time tog slut). En spelares **spelade rundor** är antalet rundor de
startade. Startade en spelare inga (de hade aldrig en sådan rad), används i stället matchens rundantal,
så att ingen division med noll sker.

## Resultattavleraden {#the-scoreboard-line}

En post per spelare (se [matchdokumentet](output-match-json.md#players) för fältnamnen). "Fiendekill" nedan
betyder en kill med en attacker, inte en teamkill, och inte ett suicide (offrets eget).

| Fält | Räknar |
|---|---|
| `kills` | fiendekills, både i den levande fasen och i efterfasen |
| `deaths` | varje dödsfall: av fiender, lagkamrater, sig själv eller världen |
| `assists` | fiendekills som spelaren assisterade utan flash (assistenten får inte vara mördaren) |
| `flashAssists` | fiendekills som spelaren assisterade med en flash |
| `diff` | kills - deaths |
| `adr` | skada (förlorad hälsa, endast fiender, båda faserna) / spelade rundor, en decimal |
| `kast` | 100 x (rundor med en kill, en assist eller flashassist, överlevnad eller en trade-död) / spelade rundor, en decimal. *Överlevnad* är: en startande spelare i rundan som inte dog i den, i någon av faserna. |
| `headshotPct` | 100 x huvudskottskills / kills, en decimal; 0 utan kills |
| `openingKills`, `openingDeaths` | öppningsduellerna vunna och förlorade |
| `tradeKills` | kills som hämnade en lagkamrats död |
| `tradedDeaths` | dödsfall som hämnades |
| `multiKills` | rundor med 2, 3, 4 och 5 fiendekills (`2k`, `3k`, `4k`, `5k`); fler än fem räknas som `5k`. Båda faserna räknas. |
| `clutches`, `clutchesWon` | clutchar spelade och vunna (nedan) |
| `utilityDamage` | skada med HE-granater, molotovs och incendiaries, en decimal |
| `enemiesFlashed` | fiender blindade i **minst 1,0 s** av denna spelares flashar |
| `plants`, `defuses` | bombplanteringar och desarmeringar (rader i tabellen) |
| `teamkills` | lagkamrater dödade. Ett suicide - mördare och offer samma spelare, en egen granat till exempel - räknas inte som det: det är bara ett dödsfall. |
| `roundsPlayed` | startade rundor, som ovan |

Spelarna listas efter lag (i alfabetisk ordning), och inom ett lag efter `diff`, sedan `kills`, bäst först.

Noteringar om kanterna:

- En kill i efterfasen - vinnarna som jagar en sparande spelare - räknas som en kill, ett dödsfall, för
  ADR, multikills och KAST precis som andra.
- Wallbangs räknas per spelare internt men skrivs inte i matchdokumentet; varje kill i rundlistan säger om
  den var en.
- Den *traded*-delen av KAST krediterar offret för ett hämnat dödsfall i den rundan.
- Teamkills och suicide lägger ett dödsfall på offret men ingen kill på någon; en teamkill lägger till
  mördarens `teamkills`, ett suicide ingenting annat.

## Clutchar {#clutches}

För varje runda behandlas de startande spelarna på båda sidor som levande, och rundans levande kills går
igenom i ordning. Efter varje dödsfall tas offret bort, och varje sida granskas: en sida med exakt **en**
spelare kvar, och minst en fiende fortfarande levande, är en clutch för den spelaren **mot** så många
fiender som lever i det ögonblicket. Varje spelare har högst en clutch per runda; den är **vunnen** när
spelarens sida vann rundan.

Följder av definitionen:

- Båda sidor kan ha en clutch i samma runda. Om en sida först är nere på en (en 1v3, till exempel) och den
  andra sidan sedan också nedbringas till en, är den andra spelaren i en egen 1v1-clutch.
- `against` är antalet när spelaren blev den sista, inte vid rundans slut.
- Kills i efterfasen går inte igenom, så de varken startar en clutch eller ändrar en.

## Överlevare {#survivors}

En rundas **överlevare** är, per sida, dess startande spelare minus alla som dog medan den var levande. En
spelare som dödades i efterfasen medan den sparade är fortfarande en överlevare i rundlistan - men överlevde
inte för KAST.

## Rundlistan {#the-round-list}

Varje runda i matchdokumentet bär sitt resultat, sin ställning, sina sidor, sin ekonomi, sin plantering,
sina överlevare, sina clutchar och sina kills i ordning; se
[Matchdokumentet](output-match-json.md#rounds).

## Den textbaserade resultattavlan {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` skriver ut dessa tal per lag; se
[Kommandon](commands.md#scoreboard---a-match-as-text).
