---
title: "Kampdokumentet"
nav_order: 9
lang: "no"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Kampdokumentet (`<kamp>.match.json`) {#the-match-document-matchjson}

Ett JSON-dokument per kamp, ved siden av tabellen: lag, score, hver runde med sitt resultat,
økonomi, plantinger, drap, clutcher og overlevende, og hver spillers linje i resultattavlen. Det er
det 3DHeat-visningens Kamp-fane laster. Kode: `summary()` i
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py); tallene
er definert under [Statistikk](statistics.md).

Filen er UTF-8, innrykket med ett mellomrom, og beholder ikke-ASCII-tegn (spiller- og lagnavn) slik de
er. Tider er sekunder, avrundet til tre desimaler for runder og to for drap og plantingen.

## Dokumentet {#the-document}

| Felt | Type | Hva |
|---|---|---|
| `format` | streng | alltid `heat3d-cs2-match` - hvordan en leser gjenkjenner filen |
| `version` | tall | `3`. Et version 1-dokument gir en plantings `time` i kampsekunder; fra 2 er det sekunder inn i runden, som for et drap. 3 legger til feltene fra `header` og freeze time i tabellen. |
| `match` | streng | kampnavnet, slik filene er navngitt |
| `map` | streng | kartet (`de_x`) |
| `demos` | streng[] | demofilene den er bygget av, bare filnavn, i kampens rekkefølge |
| `teams` | streng[] | lagnavnene i den rekkefølgen de først dukker opp (runde 1: T-siden først) |
| `score` | objekt | lagnavn -> runder vunnet: den siste rundens score |
| `winner` | streng eller null | laget som vant kampen, der opptaket viser slutten; null for et opptak som stopper tidlig, en forlengelse uten vinnerpanelet, eller uavgjort |
| `winnerSource` | streng eller null | hvordan `winner` er kjent: `winPanel` (spillets vinnerpanel for kampen), `surrender`, `regulation` (mer enn halvparten av de ordinære rundene) |
| `rounds` | objekt[] | hver komplette runde, i rekkefølge - [under](#rounds) |
| `incomplete` | tall[] | rundenumre kuttet av demoens slutt og utelatt |
| `missing` | tall[] | rundenumre før den første demoene har: `[1, 2]` når opptaket starter i runde 3 |
| `halfLength` | tall eller null | runder i en ordinær halvdel, fra der sidene først bytter (`12` i formatet med 24 runder); null når opptaket ikke viser byttet |
| `pistolRounds` | tall[] | pistolrundene `buy` regnes med: runde 1, og runden etter halvdelen når `halfLength` er kjent; aldri en forlengelsesrunde |
| `players` | objekt[] | resultattavlen - [under](#players) |
| `conventions` | objekt | definisjonene bak tallene, [under](#conventions) |
| `header` | objekt | den første demoens header slik parseren gir den: servernavn, patchversjon, demoversjon, kart |
| `profiles` | objekt | Steam-ID -> det som forblir det samme for en spiller gjennom kampen: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (sist sett) |
| `playerInfo` | objekt[] | hver spiller demoene lister, også coacher og casterne: Steam-ID, navn, lagnummer |
| `skins`, `itemDrops` | objekt[] | våpenskinn og gjenstandsdropp, der demoen har dem (turneringsdemoer fra sendingen har ingen) |
| `chat` | objekt[] | hver chatlinje i kampen: tid, runde, spiller, side, tekst |
| `events` | objekt[] | hver spillhendelse om ingen spiller, i tidsrekkefølge, med alle sine felt: rundesignaler og faser, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (serverens innstillinger slik de endret seg), sendingens kameraregissørs jakt- og faste skudd, `cs_win_panel_match`, ... |
| `state` | objekt[] | spillets tilstand der den endret seg: tid, felt, verdi - timeout (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomben (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, spillerne som er i live, serverens `match_start_time` og `round_start_time` |
| `selfCheck` | objekt | `completeness`: hvor alt i demoen gikk - per hendelsesnavn, egenskapsklasse, nettverksmelding, ramme og strengtabell dens `seen`-, `decoded`-, `partial`-, `raw`- og `lost`-tall, sidefilene som ble skrevet, totalt `lost` (0 med mindre `--no-bulk`), egenskapene parseren lister men ikke kan lese (`unreadProps`). Konvensjonen: [Konverterne beholder alt](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); sidefilene: README-filens avsnitt om fullstendighet |

## Runder {#rounds}

| Felt | Type | Hva |
|---|---|---|
| `number` | tall | runden, 1-basert |
| `start` | tall | kampsekunder da freeze time tok slutt |
| `end` | tall | kampsekunder da runden ble avgjort |
| `until` | tall | kampsekunder da neste runde startet (slutten av etter-fasen) |
| `winner` | streng | `T` eller `CT`; tom for uavgjort |
| `winnerTeam` | streng | den vinnende sidens lagnavn; tom for uavgjort |
| `reason` | streng | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` eller `other` |
| `score` | objekt | lagnavn -> runder vunnet etter denne |
| `sides` | objekt | lagnavn -> `T` / `CT` denne runden |
| `equipment` | objekt | side -> total utstyrsverdi for dens levende spillere ved freeze end, i dollar |
| `buy` | objekt | side -> `pistol`, `eco`, `force` eller `full` |
| `plant` | objekt eller null | bombeplantingen: `site` (`A` eller `B`; tom når demoen ikke sier det), `time` (sekunder **inn i runden**, som for et drap), `player`, `steamid`, `x`, `y`, `z` (spillenheter), `place` (planteren sitt stedsnavn: der bomben lå) |
| `survivors` | objekt | side -> navnene på de startende spillerne som fortsatt lever når runden ble avgjort, sortert |
| `clutches` | objekt[] | hver: `player`, `steamid`, `side`, `against` (fiender i live da spilleren ble den siste), `won` |
| `kills` | objekt[] | hvert dødsfall i runden, i rekkefølge - under |

Slik finnes disse: [Bygge en kamp](building-matches.md#rounds);
clutcher og overlevende: [Statistikk](statistics.md#clutches).

### En rundes drap {#a-rounds-kills}

Hvert dødsfall i runden, også etter-fasen:

| Felt | Type | Hva |
|---|---|---|
| `time` | tall | sekunder **inn i runden** (fra freeze end) |
| `attacker`, `attackerSide` | streng | drapsmannen og dens side; tom for verden |
| `victim`, `victimSide` | streng | offeret og dets side |
| `assister` | streng eller null | spilleren som assisterte, eller null |
| `flashAssist` | bool | assisten var en blending |
| `weapon` | streng | slik spillet kaller det |
| `headshot` | bool | |
| `wallbang` | bool | kulen gikk gjennom noe |
| `throughSmoke` | bool | drapet var gjennom røyk |
| `noscope` | bool | et sikteutstyrt våpen ble avfyrt usikte |
| `attackerBlind` | bool | drapsmannen var blendet |
| `opening` | bool | rundens første drap på en fiende |
| `traded` | bool | dette dødsfallet ble hevnet innen 5 s |
| `trade` | bool | dette drapet hevnet en lagkamerat innen 5 s |
| `teamkill` | bool | angriper og offer på samme side, to forskjellige spillere |
| `suicide` | bool | angriper og offer er samme spiller (en egen granat, for eksempel); ikke et lagkameraddrap |
| `after` | bool | drapet kom etter at runden var avgjort |
| `place` | streng | hvor **offeret** var (kartets stedsnavn) |

## Spillere {#players}

Én oppføring per spiller, etter lagnavn og deretter best først etter drap minus
dødsfall, deretter drap:

| Felt | Type | Hva |
|---|---|---|
| `name`, `steamid`, `team` | streng | hvem |
| `kills`, `deaths` | tall | |
| `assists`, `flashAssists` | tall | assister uten og med blending |
| `diff` | tall | drap - dødsfall |
| `adr` | tall | gjennomsnittlig skade per spilt runde, tapt helse |
| `kast` | tall | prosent av rundene spilt med et drap, en assist, overlevelse eller et trade-dødsfall |
| `headshotPct` | tall | prosent av drapene som var hodeskudd |
| `openingKills`, `openingDeaths` | tall | åpningsduellene vunnet og tapt |
| `tradeKills`, `tradedDeaths` | tall | trade-drap; dødsfall som ble tradet |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: runder med så mange drap |
| `clutches`, `clutchesWon` | tall | |
| `utilityDamage` | tall | skade med HE, molotov, brannbombe |
| `enemiesFlashed` | tall | fiender blendet i minst 1 s |
| `plants`, `defuses` | tall | |
| `teamkills` | tall | lagkamerater drept; selvmord telles ikke |
| `roundsPlayed` | tall | runder startet |

Alle definisjoner: [Statistikk](statistics.md#the-scoreboard-line).

## Konvensjoner {#conventions}

Skrevet inn i hvert dokument, slik at en leser vet hva tallene betyr uten denne siden:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Et eksempel {#an-example}

Fra den syntetiske demoen med to runder fra testene, forkortet (`...` markerer det som er utelatt):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

Rekkefølgen av nøklene inne i `survivors`, `equipment` og `buy` er ikke fast.
