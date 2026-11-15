---
title: Statistieken
nav_order: 7
lang: "nl"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistieken {#statistics}

Wat elke speler in een wedstrijd deed, en hoe elke ronde verliep: het scorebord en de rondelijst van het [matchdocument](output-match-json.md). Code: [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py). Alles wordt geteld uit de wedstrijd zoals die is opgebouwd in [Een wedstrijd opbouwen](building-matches.md): de killrecords, de schade (verloren gezondheid, alleen vijanden), de verblindingen (alleen vijanden) en de rijen.

![de tekstuele scorebord van een synthetische wedstrijd](../assets/img/scoreboard.svg)

## De conventies {#the-conventions}

Waar het spel zelf een getal niet definieert, gelden deze definities. Ze staan ook in elk matchdocument onder `conventions`.

| Term | Definitie |
|---|---|
| **Trade** | Een dood is *getradet* wanneer zijn killer binnen **5 s** door een teamgenoot van het slachtoffer wordt gedood; die kill is een *trade-kill*. |
| **Opening** | De eerste kill van een vijand in de ronde terwijl die live is. Een teamkill, een suïcide of een dood door de wereld ervoor wordt overgeslagen. |
| **KAST** | Het aandeel van de rondes waarin een speler een **K**ill had, een **A**ssist (een flitsassist telt mee), **S**urvived (overleefde) of **T**raded (getradet) werd. |
| **Schade** | Gezondheid die daadwerkelijk verloren is, alleen vijanden: een headshot van 137 schade op een speler met 40 gezondheid is 40. |
| **Clutch** | De laatste levende speler van een kant, terwijl er nog vijanden in leven zijn; gewonnen wanneer die kant de ronde wint. |
| **Buy** | Per kant, uit de gemiddelde waarde van de uitrusting aan het einde van de freeze time: de eerste ronde van elke reguliere helft is een pistoolronde (ronde 1, en de ronde na de helft, zolang de wedstrijd die speelde); overtime heeft er geen; daarna onder $1.500 eco, onder $4.000 force, anders full. |

## Wie een ronde begon {#who-started-each-round}

Sommige getallen hangen af van wie een ronde speelde. De **startende spelers** van een ronde zijn, per kant, elke speler met een levende positierij binnen één seconde na de vroegste positie van die ronde (dat wil zeggen, in de eerste seconde na het einde van de freeze time). Het aantal **gespeelde rondes** van een speler is het aantal rondes dat hij begon. Heeft een speler er geen begonnen (hij had nooit zo'n rij), dan wordt in plaats daarvan het rondetal van de wedstrijd gebruikt, zodat er niet door nul wordt gedeeld.

## De scoreboardregel {#the-scoreboard-line}

Één item per speler (zie [het matchdocument](output-match-json.md#spelers) voor de veldnamen). "Kill van een vijand" hieronder is een kill met een aanvaller, geen teamkill en geen suïcide (de eigen dood van het slachtoffer).

| Veld | Telt |
|---|---|
| `kills` | kills van vijanden, uit de live- en de after-fase |
| `deaths` | elke dood: door vijanden, teamgenoten, zichzelf of de wereld |
| `assists` | kills van vijanden die deze speler zonder flits assisteerde (de assisterende speler mag niet de killer zijn) |
| `flashAssists` | kills van vijanden die deze speler met een flits assisteerde |
| `diff` | kills - deaths |
| `adr` | schade (verloren gezondheid, alleen vijanden, beide fasen) / gespeelde rondes, één decimaal |
| `kast` | 100 x (rondes met een kill, een assist of flitsassist, overleving of een getradete dood) / gespeelde rondes, één decimaal. *Overleving* is: een startende speler van de ronde die er niet in stierf, in beide fasen. |
| `headshotPct` | 100 x headshotkills / kills, één decimaal; 0 zonder kills |
| `openingKills`, `openingDeaths` | gewonnen en verloren openingsduels |
| `tradeKills` | kills die de dood van een teamgenoot wraakten |
| `tradedDeaths` | doden die zijn getradet |
| `multiKills` | rondes met 2, 3, 4 en 5 kills van vijanden (`2k`, `3k`, `4k`, `5k`); meer dan vijf telt als `5k`. Beide fasen tellen mee. |
| `clutches`, `clutchesWon` | gespeelde en gewonnen clutches (hieronder) |
| `utilityDamage` | schade met HE-granaten, molotovs en incendiaries, één decimaal |
| `enemiesFlashed` | vijanden die door de flitsen van deze speler minstens **1,0 s** verblind waren |
| `plants`, `defuses` | bomplanten en defusies (rijen van de tabel) |
| `teamkills` | gedode teamgenoten. Een suïcide - aanvaller en slachtoffer dezelfde speler, bijvoorbeeld een eigen granaat - telt niet mee: het is alleen een dood. |
| `roundsPlayed` | gestarte rondes, zoals hierboven |

Spelers staan per teamnaam (alfabetisch), en binnen een team op `diff`, dan op `kills`, beste eerst.

Opmerkingen over de randen:

- Een kill in de after-fase - de winnaars die een sparende speler opjagen - telt als kill, als dood, voor ADR, multikills en KAST net als elke andere.
- Wallbangs worden per speler intern geteld, maar niet in het matchdocument geschreven; elke kill in de rondelijst zegt of hij er een was.
- Het *getradet*-deel van KAST krediteert het slachtoffer van een getradete dood in die ronde.
- Teamkills en suïcides tellen een dood op bij het slachtoffer, maar geen kill bij iemand; een teamkill telt op bij de `teamkills` van de killer, een suïcide bij niets anders.

## Clutches {#clutches}

Voor elke ronde worden de startende spelers van beide kanten als levend beschouwd, en de live-kills van de ronde worden in volgorde doorlopen. Na elke dood wordt het slachtoffer verwijderd, en elke kant wordt bekeken: een kant met precies **één** speler over, en minstens één vijand nog in leven, is een clutch voor die speler **tegen** het aantal vijanden dat op dat moment in leven is. Elke speler heeft hooguit één clutch per ronde; hij is **gewonnen** wanneer de kant van die speler de ronde won.

Gevolgen van de definitie:

- Beide kanten kunnen in één ronde een clutch hebben. Als de ene kant eerst tot één speler wordt teruggebracht (een 1v3, bijvoorbeeld) en de andere kant daarna ook tot één, dan heeft de tweede speler een eigen 1v1-clutch.
- `against` is het aantal toen de speler de laatste werd, niet aan het eind.
- Kills van de after-fase worden niet doorlopen, dus ze starten geen clutch en veranderen er geen.

## Overlevenden {#survivors}

De **overlevenden** van een ronde zijn, per kant, de startende spelers min iedereen die tijdens de live-fase stierf. Een speler die in de after-fase sterft terwijl hij spaart, is in de rondelijst nog steeds een overlevende - maar hij heeft voor KAST niet *overleefd*.

## De rondelijst {#the-round-list}

Elke ronde van het matchdocument bevat zijn resultaat, score, kanten, economie, plant, overlevenden, clutches en zijn kills in volgorde; zie [Het matchdocument](output-match-json.md#rondes).

## Het tekstscorebord {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` drukt deze getallen per team af; zie [Commando's](commands.md#scoreboard---een-wedstrijd-als-tekst).
