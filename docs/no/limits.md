---
title: "Begrensninger"
nav_order: 13
lang: "no"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Begrensninger {#limits}

Hva konverteren forutsetter, hva den ikke håndterer, og hva som ikke er verifisert. Hvert
punkt er hentet fra koden slik den står nå.

## Hva den leser {#what-it-reads}

- **Bare ukomprimerte `.dem`-filer.** `.dem.zst`, `.dem.bz2`, `.rar` og `.zip` må pakkes
  ut først. Filendelsen gjenkjennes uansett bokstavstørrelse (`.dem`, `.DEM`), i mapper
  som for filer gitt med navn.
- **Defusal-kamper.** Grunnene til rundeslutt, bombeplantingen og sonen, kjøpstypene og
  pistolrundene er de for bombedesarmering. Gisselkart, Wingman og andre moduser håndteres
  ikke spesielt og er ikke verifisert.
- **64 tick per sekund** forutsettes (`TICKRATE = 64`) for all tid som regnes ut fra tick;
  CS2-servere går med 64.
- **En demo fra serveren** (SourceTV) forutsettes: den har alle spillerne. En
  klientopptak (POV-demo) er ikke prøvd.

## Kamper og runder {#matches-and-rounds}

- **Filer grupperes på navn.** Delene av én kamp må ha samme navn bortsett fra et `-pN`- /
  `_pN`-suffiks; filer av én kamp under ulike navn blir separate kamper, og filer med samme navn
  i ulike mapper grupperes sammen (og deles så i kjeder hvis de ikke fortsetter hverandre).
- **Den levende kampen starter ved siste `round_announce_match_start`** i en fil. En knivrunde
  som ikke følges av den kunngjøringen, regnes som en runde.
- **Rundeslutt-tider er nøyaktige til én prøve** (`--every` tick, 1/8 s som standard), fordi
  avgjørelsen leses fra samplet spilltilstand. En veldig stor `--every` kan gå glipp av et kort
  vindu mellom en rundes slutt og neste rundes start, og utelate runden som ufullstendig.
- **Uavgjort.** En uavgjort runde (win status 1, grunn 10) er avgjort uten vinner: `winner` er
  tom, og ingen av sidene vant den. Ingen uavgjort runde er møtt i en ekte demo å sjekke mot;
  den er sjekket på den syntetiske.
- **Runder kuttet av** filens slutt utelates (`incomplete`), og gjettes ikke; runder før de første
  i filene listes som `missing`.
- **Pistolrunder** følger halvdelens lengde slik opptaket viser den: der sidene først bytter mellom
  to etterfølgende ordinære runder. Et opptak som ikke viser det byttet (det starter etter
  pausen, eller slutter før den, eller mangler en runde på en av sidene) kjenner bare runde 1 som
  pistolrunde. Forlengelse har ingen.
- **Lag.** Et lag er klannavnet som er sett oftest for dets spillere. Uten klannavn er lagene
  `Started T` og `Started CT`. En spiller som bytter lag midt i kampen, beholder ett lag.

## Hendelser {#events}

- **Alt parseren tilbyr leses**, med disse unntakene: spillernes hastighet (parseren utleder den
  fra posisjoner; den står ikke i demoen), tale (lyd, `parse_voice`), og bombens `weapon_fire`
  (starten på en plantering, som `bomb_beginplant` har). Granatflyvninger beholdes med spillernes
  samplingsrate (`--every`) og der hver granat stoppet, ikke for hvert tick.
- **Rader utenfor en runde** (oppvarming, en pause mellom kampens start og første freeze time
  etter mer enn to minutter) utelates fra tabellen; hendelsene som ikke gjelder noen spiller, står
  alle i kampdokumentets `events`.
- **Detonasjonsrader** (`smoke`, `flash`, `he`, `molotov`, `decoy`) har ikke `place`: demoen
  oppgir steder for spillere, ikke for granater. Kasterens sted i det øyeblikket står i
  `throwerPlace`.
- **Plantingens site** kommer fra bombesonen spilleren sto i ifølge spillet, ellers stedsnavnet
  til planteren, ellers en annen plantering i samme sone i samme fil. Der ingen av disse sier noe,
  er `site` tom.
- **Et dødsfall for verden** (et fall, bomben) har ingen angriper: ingen drap, ingen
  lagkameraddrap, ingen åpning; det er et dødsfall.

## Statistikk {#statistics}

- **Spilte runder** kommer fra hvem som hadde en posisjon i det første sekundet etter freeze
  time. En spiller som kobler seg på senere i en runde, teller ikke som å ha spilt den (drapene
  deres teller likevel).
- **Overlevelse for KAST**: en spiller drept i etter-fasen overlevde ikke for KAST, mens
  rundelisten fortsatt nevner dem blant overlevende.
- **Begge spillerne i en 1v1** kan få en clutch i samme runde; se [Statistikk](statistics.md#clutches).
- **Utility-skade** er HE-granater, molotover og brannbomber; et drap eller treff fra en kastet
  blending eller decoy er ikke utility-skade.

## Karteksport {#map-export}

- Krever at spillet er installert (eller `.vpk`-filen) og Source2Viewers CLI; ingenting lastes ned.
- Eksporterer bare `world_physics`; clip-brett og himmelen utelates etter at navnene deres
  inneholder `clip` eller `sky`, uansett bokstavstørrelse.
- Gulv skilles fra konstruksjon bare etter flatens normal (Z-komponent på 0,7 eller mer), så en
  bratt rampe er konstruksjon, og et flatt tak er gulv.
- Filen er i tommer, ikke meter.

## Minne og tid {#memory-and-time}

- En kamp holdes i minnet helt mens den bygges, i én arbeider per kamp. Med mange arbeidere og et
  lite `--every` legger minnet seg sammen: senk `--jobs` hvis en maskin går tom for minne.
- En kamp skrives først når den er bygget: `.parquet` først, deretter `.match.json`. En kjøring som
  stoppes midt imellom, etterlater en tabell uten sitt kampdokument; en kamp regnes som skrevet
  bare med begge, så neste kjøring konverterer den på nytt. Kamper som ikke er startet, plukkes
  opp av neste kjøring.
