---
title: "Begränsningar"
nav_order: 13
lang: "sv"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Begränsningar {#limits}

Vad konverteraren förutsätter, vad den inte hanterar, och vad som inte är verifierat. Varje
punkt är hämtad från koden så som den ser ut nu.

## Vad den läser {#what-it-reads}

- **Bara okomprimerade `.dem`-filer.** `.dem.zst`, `.dem.bz2`, `.rar` och `.zip` måste packas
  upp först. Ändelsen matchas oavsett versaler (`.dem`, `.DEM`), i mappar så väl som för filer
  som anges med namn.
- **Bombmatcher.** Rundornas slutorsaker, bombplanteringen och dess zon, köpetyperna och
  pistolrundorna är de för bombdesarmering. Gisslankartor, Wingman och andra lägen hanteras
  inte särskilt och är inte verifierade.
- **64 tick per sekund** förutsätts (`TICKRATE = 64`) för all tid som räknas från ticks; CS2-servrar
  går med 64.
- **En demo från servern** (SourceTV) förutsätts: den har alla spelare. En inspelning från klientens
  sida (POV-demo) har inte prövats.

## Matcher och rundor {#matches-and-rounds}

- **Filer grupperas efter namn.** Delarna av en match måste ha samma namn bortsett från ett
  `-pN`- / `_pN`-suffix; filer från en match under orelaterade namn blir separata matcher, och
  filer med samma namn i olika mappar grupperas ihop (och delas sedan upp i kedjor om de inte
  fortsätter varandra).
- **Den levande matchen börjar vid den sista `round_announce_match_start`** i en fil. En knivrunda
  som inte följs av den annonseringen räknas som en runda.
- **Rundornas sluttider är exakta till ett sampel** (`--every` ticks, 1/8 s som standard), eftersom
  avgörandet läses från samplat spelläge. Ett mycket stort `--every` kan missa ett kort fönster
  mellan en runda som slutar och nästa som startar, och lämna ut rundan som ofullständig.
- **Oavgjorda rundor.** En oavgjord runda (win status 1, reason 10) är avgjord utan vinnare:
  `winner` är tomt och ingen sida vann den. Inget oavgjort möttes i en riktig demo att jämföra med;
  det kontrolleras på den syntetiska.
- **Rundor avbrutna** av filens slut utelämnas (`incomplete`), och gissas inte; rundor före de första i
  filerna listas som `missing`.
- **Pistolrundor** följer den halvlekslängd inspelningen visar: där sidorna först byter plats mellan
  två på varandra följande ordinarie rundor. En inspelning som inte visar bytet (den börjar efter
  halvtid, eller slutar före den, eller så saknas en runda på någondera sidan om den) känner bara
  runda 1 som pistolrunda. Övertid har ingen.
- **Lag.** Ett lag är klannamnet som oftast ses för dess spelare. Utan klannamn blir lagen
  `Started T` och `Started CT`. En spelare som byter lag mitt i matchen behåller ett lag.

## Händelser {#events}

- **Allt parsern erbjuder läses**, med dessa undantag: spelarnas hastighet (parsern härleder den
  från positioner; den finns inte i demon), röst (ljud, `parse_voice`), och bombens `weapon_fire`
  (början på en plantering, som `bomb_beginplant` har). Granatflygningar sparas vid spelarnas
  sampling (`--every`) och där varje granat stannade, inte vid varje tick.
- **Rader utanför en runda** (uppvärmning, en paus mellan matchens start och första freeze time
  efter mer än två minuter) utelämnas ur tabellen; händelser som inte gäller någon spelare finns
  alla i matchdokumentets `events`.
- **Detonationsrader** (`smoke`, `flash`, `he`, `molotov`, `decoy`) har ingen `place`: demon anger
  platser för spelare, inte för granater. Kastarens plats i det ögonblicket finns i `throwerPlace`.
- **Planteringens zon** kommer från bombzonen spelet säger att planteraren stod i, annars
  planterarens platsnamn, annars en annan plantering i samma zon i samma fil. Där ingen av dem anger
  något är `site` tomt.
- **En död för världen** (ett fall, bomben) har ingen attacker: ingen kill, ingen teamkill, ingen
  öppning; det är en död.

## Statistik {#statistics}

- **Spelade rundor** kommer från vilka som hade en position under den första sekunden efter freeze
  time. En spelare som ansluter senare i en runda räknas inte som att de spelat den (deras kills
  räknas ändå).
- **Överlevnad för KAST**: en spelare som dödades i efterfasen överlevde inte för KAST, medan
  rundlistan fortfarande nämner dem bland överlevarna.
- **Båda spelarna i en 1v1** kan få en clutch var i samma runda; se [Statistik](statistics.md#clutches).
- **Utrustningsskada** är HE-granater, molotovs och incendiaries; en kill eller träff med en kastad
  flash eller decoy är inte utrustningsskada.

## Kartexport {#map-export}

- Kräver att spelet är installerat (eller `.vpk`-filen) och Source2Viewers CLI; ingenting laddas ner.
- Exporterar bara `world_physics`; clip-volymer och himlen utelämnas genom att deras namn innehåller
  `clip` eller `sky`, oavsett versaler.
- Mark skiljs från konstruktion enbart på ytans normal (Z-komponenten 0,7 eller mer), så en brant
  rampa är konstruktion och ett platt tak är mark.
- Filen är i tum, inte meter.

## Minne och tid {#memory-and-time}

- En match hålls i minnet hel medan den byggs, i en arbetsprocess per match. Med många
  arbetsprocesser och ett litet `--every` lägger sig minnet ihop: sänk `--jobs` om en dator får ont om
  minne.
- En match skrivs först när den byggs: `.parquet` först, sedan `.match.json`. En körning som stoppas
  mitt emellan lämnar en tabell utan sitt matchdokument; en match räknas som skriven bara med båda, så
  nästa körning konverterar den igen. Matcher som ännu inte startat plockas helt enkelt upp av nästa
  körning.
