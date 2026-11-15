---
title: "Begrænsninger"
nav_order: 13
lang: "da"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Begrænsninger {#limits}

Hvad konverteren går ud fra, hvad den ikke håndterer, og hvad der ikke er verificeret. Hvert punkt
kommer fra koden, sådan som den står nu.

## Hvad den læser {#what-it-reads}

- **Kun ukomprimerede `.dem`-filer.** `.dem.zst`, `.dem.bz2`, `.rar` og `.zip` skal pakkes ud først. Endelsen bliver matchet uanset store eller små bogstaver (`.dem`, `.DEM`), i mapper som for filer, der er givet med navn.
- **Defusal-kampe.** Rundernes slutårsager, bombeplantningen og dens sted, købstyperne og pistolrunderne er dem fra bomb defusal. Gidselkort, Wingman og andre spilletilstande bliver ikke håndteret særligt og er ikke verificeret.
- **64 tick i sekundet** antages (`TICKRATE = 64`) for al tid, der regnes ud fra ticks; CS2-servere kører med 64.
- **En demo fra serveren** (SourceTV) antages: den har alle spillere. En klientsideoptagelse (POV-demo) er ikke prøvet.

## Kampe og runder {#matches-and-rounds}

- **Filer bliver grupperet efter navn.** Delene af én kamp skal have samme navn bortset fra et `-pN` / `_pN`-suffiks; filer af én kamp under urelaterede navne bliver til separate kampe, og filer med samme navn i forskellige mapper bliver grupperet sammen (og derefter delt i kæder, hvis de ikke fortsætter hinanden).
- **Live-kampen starter ved den sidste `round_announce_match_start`** i en fil. En knivrunde, der ikke efterfølges af den annoncering, bliver talt som en runde.
- **Rundernes sluttider er nøjagtige til ét sample** (`--every` tick, 1/8 s som standard), fordi afgørelsen bliver læst fra samplede spiltilstande. Et meget stort `--every` kan misse et kort vindue mellem en rundes slutning og næste runde's start og lade runden ligge som ufuldstændig.
- **Uafgjorte.** En uafgjort runde (win status 1, reason 10) er afgjort uden vinder: `winner` er tom, og ingen af siderne vandt den. Der blev ikke mødt et uafgjort i en rigtig demo at tjekke det mod; det er tjekket på den syntetiske.
- **Runder afbrudt** af en fils ende bliver udeladt (`incomplete`) og ikke gættet; runder før den første i filerne står som `missing`.
- **Pistolrunder** følger halvlegens længde, som optagelsen viser: hvor siderne først bytter mellem to følgende ordinære runder. En optagelse, der ikke viser det byt (den starter efter halvtid, eller slutter før det, eller en runde på hver side af det mangler), kender kun runde 1 som pistolrunde. Overtid har ingen.
- **Hold.** Et hold er klannavnet, der oftest er set for dets spillere. Uden klannavne er holdene `Started T` og `Started CT`. En spiller, der skifter hold midt i kampen, beholder ét hold.

## Hændelser {#events}

- **Alt, parseren tilbyder, bliver læst**, med disse undtagelser: spillernes hastighed (parseren udleder den fra positioner; den er ikke i demoen), stemme (lyd, `parse_voice`) og bombens `weapon_fire` (begyndelsen på en plantning, som `bomb_beginplant` har). Granaters flyvninger bliver gemt med spillernes sampling (`--every`) og der, hvor hver granat stoppede, ikke for hvert tick.
- **Rækker uden for en runde** (opvarmning, en pause mellem kampens start og første freeze-tid over to minutter) bliver udeladt fra tabellen; hændelser om ingen spiller er alle i kampdokumentets `events`.
- **Detonationsrækker** (`smoke`, `flash`, `he`, `molotov`, `decoy`) har intet `place`: demoen navngiver steder for spillere, ikke for granater. Kasterens sted på det tidspunkt er i `throwerPlace`.
- **Plantningens site** kommer fra bombezonen, som spillet siger, planteren stod i, ellers planterens stednavn, ellers en anden plantning i samme zone i samme fil. Hvor ingen af disse siger noget, er `site` tom.
- **Et dødsfald til verdenen** (et fald, bomben) har ingen angriber: ingen kill, intet teamkill, ingen åbning; det er et dødsfald.

## Statistik {#statistics}

- **Spillede runder** kommer fra, hvem der havde en position i det første sekund efter freeze-tid. En spiller, der forbinder senere i en runde, tæller ikke som at have spillet den (deres kills tæller stadig).
- **Overlevelse til KAST**: en spiller, der bliver dræbt i efter-fasen, overlevede ikke til KAST, selv om rundelisten stadig nævner dem blandt overlevende.
- **Begge spillere i en 1v1** kan få en clutch i samme runde; se [Statistik](statistics.md#clutches).
- **Utility-skade** er HE-granater, molotovs og incendiaries; en kill eller et hit med en kastet blænder eller decoy er ikke utility-skade.

## Kortudtræk {#map-export}

- Kræver at spillet er installeret (eller `.vpk`-filen) og Source2Viewers CLI; intet bliver hentet.
- Eksporterer kun `world_physics`; clip-brushes og himlen bliver udeladt efter deres navne, der indeholder `clip` eller `sky`, uanset store eller små bogstaver.
- Gulv bliver skilt fra struktur alene ud fra flade-normalen (Z-komponent 0,7 eller mere), så en stejl rampe er struktur, og et fladt tag er gulv.
- Filen er i tommer, ikke meter.

## Hukommelse og tid {#memory-and-time}

- En kamp bliver holdt i hukommelsen hel, mens den bygges, i én arbejder pr. kamp. Med mange arbejdere og et lille `--every` lægger hukommelsen sig sammen: sænk `--jobs`, hvis en maskine løber tør.
- En kamp bliver kun skrevet, når den er bygget: `.parquet` først, derefter `.match.json`. En kørsel, der stoppes imellem, efterlader en tabel uden sit kampdokument; en kamp tæller kun som skrevet med begge, så den næste kørsel konverterer den igen. Kampe, der ikke er startet endnu, bliver bare samlet op af den næste kørsel.
