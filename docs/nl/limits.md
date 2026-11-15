---
title: Beperkingen
nav_order: 13
lang: "nl"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Beperkingen {#limits}

Wat de converter aanneemt, wat hij niet afhandelt, en wat niet is geverifieerd. Elk punt komt uit de code zoals hij nu is.

## Wat er wordt gelezen {#what-it-reads}

- **Alleen niet-gecomprimeerde `.dem`-bestanden.** `.dem.zst`, `.dem.bz2`, `.rar` en `.zip` moeten eerst worden uitgepakt. De extensie wordt in elke schrijfwijze herkend (`.dem`, `.DEM`), ook in mappen, net als bij bestanden die je bij naam opgeeft.
- **Defusal-wedstrijden.** De redenen van het einde van een ronde, de bomplant en site, de buy-typen en de pistoolrondes zijn die van bomb defusal. Gijzelaarskaarten, Wingman en andere modi worden niet speciaal behandeld en zijn niet geverifieerd.
- **64 ticks per seconde** wordt aangenomen (`TICKRATE = 64`) voor elke tijd die uit ticks wordt berekend; CS2-servers draaien op 64.
- **Een demo van de server** (SourceTV) wordt aangenomen: die heeft elke speler. Een opname aan de clientkant (POV-demo) is niet getest.

## Wedstrijden en rondes {#matches-and-rounds}

- **Bestanden worden op naam gegroepeerd.** De delen van één wedstrijd moeten dezelfde naam delen, afgezien van een achtervoegsel `-pN` / `_pN`; bestanden van één wedstrijd onder niet-verwante namen worden aparte wedstrijden, en bestanden met dezelfde naam in verschillende mappen worden samen gegroepeerd (en daarna in ketens gesplitst als ze niet op elkaar aansluiten).
- **De live-wedstrijd begint bij de laatste `round_announce_match_start`** in een bestand. Een knife-ronde die niet door die aankondiging wordt gevolgd, telt als ronde.
- **Eindtijden van rondes zijn nauwkeurig tot één monster** (`--every` ticks, standaard 1/8 s), omdat de beslissing wordt gelezen uit bemonsterde spelstatus. Een heel grote `--every` kan een kort venster tussen het einde van een ronde en het begin van de volgende missen, waardoor de ronde als onvolledig wegvalt.
- **Gelijkspel.** Een gelijkspelronde (winstatus 1, reden 10) is beslist zonder winnaar: `winner` is leeg en geen van beide kanten won hem. In een echte demo is nog geen gelijkspel tegengekomen om dit tegen te controleren; het is gecontroleerd op de synthetische demo.
- **Rondes die zijn afgebroken** door het einde van een bestand worden weggelaten (`incomplete`), niet geraden; rondes vóór de eerste in de bestanden staan als `missing`.
- **Pistoolrondes** volgen de lengte van de helft die de opname toont: waar de kanten voor het eerst wisselen tussen twee opeenvolgende reguliere rondes. Een opname die die wissel niet toont (hij begint na de rust, of eindigt ervoor, of er ontbreekt een ronde aan weerszijden ervan), kent alleen ronde 1 als pistoolronde. Overtime heeft er geen.
- **Teams.** Een team is de clannaam die het vaakst voor zijn spelers is gezien. Zonder clannamen zijn de teams `Started T` en `Started CT`. Een speler die midden in de wedstrijd van team wisselt, houdt één team.

## Gebeurtenissen {#events}

- **Alles wat de parser aanbiedt wordt gelezen**, met deze uitzonderingen: de snelheid van de spelers (de parser leidt die af uit posities; ze staat niet in de demo), spraak (audio, `parse_voice`), en de `weapon_fire` van de bom (het begin van een plant, die `bomb_beginplant` al heeft). Granaatvluchten worden bewaard op de bemonstering van de spelers (`--every`) en op de plek waar elke granaat stopte, niet op elk tick.
- **Rijen buiten een ronde** (warmup, een pauze tussen het begin van de wedstrijd en de eerste freeze time na meer dan twee minuten) vallen weg uit de tabel; de gebeurtenissen die over geen speler gaan staan allemaal in de `events` van het matchdocument.
- **Ontploffingsrijen** (`smoke`, `flash`, `he`, `molotov`, `decoy`) hebben geen `place`: de demo noemt plekken voor spelers, niet voor granaten. De plek van de gooier op dat moment staat in `throwerPlace`.
- **De site van een plant** komt van de bomzone waarin de game zegt dat de planter stond, anders de plaatsnaam van de planter, anders een andere plant in dezelfde zone in hetzelfde bestand. Als geen van deze iets zegt, is `site` leeg.
- **Een dood door de wereld** (een val, de bom) heeft geen aanvaller: geen kill, geen teamkill, geen opening; het is een dood.

## Statistieken {#statistics}

- **Gespeelde rondes** komen van wie een positie had in de eerste seconde na freeze time. Een speler die later in een ronde verbindt, telt die ronde niet als gespeeld (zijn kills tellen wel).
- **Overleving voor KAST**: een speler die in de after-fase is gedood, heeft niet overleefd voor KAST, terwijl de rondelijst hem nog steeds onder de overlevenden noemt.
- **Beide spelers van een 1v1** kunnen in één ronde een clutch krijgen; zie [Statistieken](statistics.md#clutches).
- **Utility-schade** is HE-granaten, molotovs en incendiaries; een kill of treffer door een gegooide flits of decoy is geen utility-schade.

## Kaartexport {#map-export}

- Heeft het geïnstalleerde spel (of het `.vpk`) en de Source2Viewer-CLI nodig; er wordt niets gedownload.
- Exporteert alleen `world_physics`; clip brushes en de lucht vallen weg omdat hun namen `clip` of `sky` bevatten, in elke schrijfwijze.
- Grond wordt van structuur onderscheiden door alleen de normaal van het vlak (Z-component 0,7 of meer), dus een steile helling is structuur en een plat dak is grond.
- Het bestand is in inches, niet in meters.

## Geheugen en tijd {#memory-and-time}

- Een wedstrijd wordt tijdens het opbouwen helemaal in het geheugen gehouden, in één werker per wedstrijd. Bij veel werkers en een kleine `--every` loopt het geheugen op: verlaag `--jobs` als een machine te weinig heeft.
- Een wedstrijd wordt pas geschreven wanneer hij is opgebouwd: eerst de `.parquet`, dan de `.match.json`. Een run die daartussen stopt, laat een tabel achter zonder haar matchdocument; een wedstrijd telt alleen als geschreven met beide, dus de volgende run zet hem opnieuw om. Wedstrijden die nog niet zijn begonnen, worden door de volgende run gewoon opgepikt.
