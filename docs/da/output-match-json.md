---
title: "Kampdokumentet"
nav_order: 9
lang: "da"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Kampdokumentet (`<match>.match.json`) {#the-match-document-matchjson}

Ét JSON-dokument pr. kamp, ved siden af dens tabel: hold, score, hver runde med dens resultat, økonomi, plantning, kills, clutches og overlevende, og hver spillers scoreboard-linje. Det er det, 3DHeat-visningens Kamp-fane indlæser. Kode: `summary()` i
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
tallene er defineret på [Statistik](statistics.md).

Filen er UTF-8, indrykket med ét mellemrum, og den beholder ikke-ASCII-tegn (spiller- og holdnavne) som de er. Tider er sekunder, afrundet til tre decimaler for runder og to for kills og plantningen.

## Dokumentet {#the-document}

| Felt | Type | Hvad |
|---|---|---|
| `format` | streng | altid `heat3d-cs2-match` - sådan genkender en læser filen |
| `version` | tal | `3`. Et version 1-dokument giver en plantnings `time` i kampsekunder; fra 2 er det sekunder inde i runden, som en kills. 3 tilføjer felterne fra `header` og frem, og freeze-tid til tabellen. |
| `match` | streng | kampnavnet, som filerne er navngivet |
| `map` | streng | kortet (`de_x`) |
| `demos` | streng[] | demo-filerne den er bygget af, kun filnavne, i kampens rækkefølge |
| `teams` | streng[] | holdnavnene i den rækkefølge, de optræder (runde 1: T-siden først) |
| `score` | objekt | holdnavn -> runder vundet: den sidste runds score |
| `winner` | streng eller null | det hold, der vandt kampen, hvor optagelsen viser slutningen; null for en optagelse, der stopper tidligt, en overtid uden vinderpanelet, eller et uafgjort |
| `winnerSource` | streng eller null | hvordan `winner` er kendt: `winPanel` (spillets vinderpanel for kampen), `surrender`, `regulation` (mere end halvdelen af de ordinære runder) |
| `rounds` | objekt[] | hver komplet runde, i rækkefølge - [nedenfor](#rounds) |
| `incomplete` | tal[] | rundenumre, en demos ende afbrød, og som er udeladt |
| `missing` | tal[] | rundenumre før den første, demoerne indeholder: `[1, 2]`, når optagelsen starter i runde 3 |
| `halfLength` | tal eller null | runder i en ordinær halvleg, fra hvor siderne først bytter (`12` i 24-runde-formatet); null, når optagelsen ikke viser byttet |
| `pistolRounds` | tal[] | pistolrunderne, `buy` tælles med: runde 1, og runden efter halvlegen, når `halfLength` er kendt; aldrig en overtidsrunde |
| `players` | objekt[] | scoreboardet - [nedenfor](#players) |
| `conventions` | objekt | definitionerne bag tallene, [nedenfor](#conventions) |
| `header` | objekt | den første demos header, som parseren giver den: servernavn, patchversion, demoversion, kort |
| `profiles` | objekt | Steam-ID -> det, der forbliver det samme for en spiller gennem kampen: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (sidst set) |
| `playerInfo` | objekt[] | hver spiller demoerne lister, også coaches og casters: Steam-ID, navn, holdnummer |
| `skins`, `itemDrops` | objekt[] | våbenskins og item-drops, hvor demoen har dem (turneringsdemoer fra transmissionen har ingen) |
| `chat` | objekt[] | hver chatlinje i kampen: tid, runde, spiller, side, tekst |
| `events` | objekt[] | hver spilhændelse om ingen spiller, i tidsrækkefølge, med alle sine felter: rundebip og faser, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (serverens indstillinger, efterhånden som de ændrer sig), transmissionskameraets chase- og faste skud, `cs_win_panel_match`, ... |
| `state` | objekt[] | spillets tilstand, hvor den ændrede sig: tid, felt, værdi - timeouts (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomben (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, de levende spillere, serverens `match_start_time` og `round_start_time` |
| `selfCheck` | objekt | `completeness`: hvor alt i demoen gik hen - pr. hændelsesnavn, egenskabsklasse, netværksbesked, frame og strengtabel dens tællere `seen`, `decoded`, `partial`, `raw` og `lost`, de skrevne sidecars, den samlede `lost` (0, medmindre `--no-bulk`), og de egenskaber, parseren lister, men ikke kan læse (`unreadProps`). Konventionen: [Konvertere beholder alt](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); sidecarsne: README'ens afsnit om fuldstændighed |

## Runder {#rounds}

| Felt | Type | Hvad |
|---|---|---|
| `number` | tal | runden, 1-baseret |
| `start` | tal | kampsekunder, da freeze-tiden sluttede |
| `end` | tal | kampsekunder, da runden blev afgjort |
| `until` | tal | kampsekunder, da den næste runde startede (slutningen af efter-fasen) |
| `winner` | streng | `T` eller `CT`; tom ved et uafgjort |
| `winnerTeam` | streng | den vindende sides holdnavn; tom ved et uafgjort |
| `reason` | streng | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` eller `other` |
| `score` | objekt | holdnavn -> runder vundet efter denne |
| `sides` | objekt | holdnavn -> `T` / `CT` i denne runde |
| `equipment` | objekt | side -> samlet udstyrsværdi for dens levende spillere ved freeze end, i dollars |
| `buy` | objekt | side -> `pistol`, `eco`, `force` eller `full` |
| `plant` | objekt eller null | bombeplantningen: `site` (`A` eller `B`; tom, når demoen ikke siger det), `time` (sekunder **inde i runden**, som en kills), `player`, `steamid`, `x`, `y`, `z` (spilenheder), `place` (planterens stednavn: hvor bomben lå) |
| `survivors` | objekt | side -> navne på de startende spillere, der stadig var i live, da runden blev afgjort, sorteret |
| `clutches` | objekt[] | hver: `player`, `steamid`, `side`, `against` (fjender i live, da spilleren blev den sidste), `won` |
| `kills` | objekt[] | hvert dødsfald i runden, i rækkefølge - nedenfor |

Sådan bliver de fundet: [Sådan bygges en kamp](building-matches.md#rounds);
clutches og overlevende: [Statistik](statistics.md#clutches).

### En rundes kills {#a-rounds-kills}

Hvert dødsfald i runden, også i efter-fasen:

| Felt | Type | Hvad |
|---|---|---|
| `time` | tal | sekunder **inde i runden** (siden freeze end) |
| `attacker`, `attackerSide` | streng | dræberen og dens side; tom for verdenen |
| `victim`, `victimSide` | streng | offeret og dets side |
| `assister` | streng eller null | den assisterende spiller, eller null |
| `flashAssist` | bool | assisten var en blænder |
| `weapon` | streng | som spillet navngiver det |
| `headshot` | bool | |
| `wallbang` | bool | kuglen gik igennem noget |
| `throughSmoke` | bool | kill'en var gennem røg |
| `noscope` | bool | et skudt våben med scope blev affyret uden scope |
| `attackerBlind` | bool | dræberen var blændet |
| `opening` | bool | rundens første kill af en fjende |
| `traded` | bool | dette dødsfald blev hævnet inden for 5 s |
| `trade` | bool | denne kill hævnede en holdkammerat inden for 5 s |
| `teamkill` | bool | angriber og offer på samme side, to forskellige spillere |
| `suicide` | bool | angriber og offer er den samme spiller (en egen granat, for eksempel); ikke et teamkill |
| `after` | bool | kill'en kom, efter runden var afgjort |
| `place` | streng | hvor **offeret** var (kortets stednavn) |

## Spillere {#players}

Én post pr. spiller, efter hold og derefter bedst først efter kills minus døde, derefter kills:

| Felt | Type | Hvad |
|---|---|---|
| `name`, `steamid`, `team` | streng | hvem |
| `kills`, `deaths` | tal | |
| `assists`, `flashAssists` | tal | assists uden og med en blænder |
| `diff` | tal | kills - døde |
| `adr` | tal | gennemsnitlig skade pr. spillet runde, mistede liv |
| `kast` | tal | procent af de spillede runder med en kill, en assist, en overlevelse eller en hævnet død |
| `headshotPct` | tal | procent af kills, der var hovedskud |
| `openingKills`, `openingDeaths` | tal | åbningsdueller vundet og tabt |
| `tradeKills`, `tradedDeaths` | tal | trade-kills; dødsfald, der blev hævnet |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: runder med så mange kills |
| `clutches`, `clutchesWon` | tal | |
| `utilityDamage` | tal | skade med HE, molotov, incendiary |
| `enemiesFlashed` | tal | fjender blændet i mindst 1 s |
| `plants`, `defuses` | tal | |
| `teamkills` | tal | holdkammerater dræbt; selvmord tæller ikke med |
| `roundsPlayed` | tal | runder startet |

Hver definition: [Statistik](statistics.md#the-scoreboard-line).

## Konventioner {#conventions}

Skrevet ind i hvert dokument, så en læser ved, hvad tallene betyder, uden denne side:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Et eksempel {#an-example}

Fra den syntetiske demo med to runder fra testene, forkortet (`...` markerer det, der er udeladt):

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

Rækkefølgen af nøgler inde i `survivors`, `equipment` og `buy` er ikke fast.
