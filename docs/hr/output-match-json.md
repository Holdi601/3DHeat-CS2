---
title: "Dokument meča"
nav_order: 9
lang: "hr"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Dokument meča (`<meč>.match.json`) {#the-match-document-matchjson}

Jedan JSON dokument po meču, uz njegovu tablicu: timovi, rezultat, svaka runda s rezultatom, ekonomijom, postavljanjem, ubojstvima, clutchevima i preživjelima, te svaki redak rezultatne tablice svakog igrača. Kartica Meč u pregledniku 3DHeat učitava upravo ovo.
Kod: `summary()` u
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
brojevi su definirani na [Statistika](statistics.md).

Datoteka je UTF-8, uvučena jednim razmakom, i čuva znakove koji nisu ASCII (imena igrača i timova) kakvi jesu. Vremena su u sekundama, zaokružena na tri decimale za runde i dvije za ubojstva i postavljanje.

## Dokument {#the-document}

| Polje | Tip | Što |
|---|---|---|
| `format` | niz | uvijek `heat3d-cs2-match` - po čemu čitatelj prepoznaje datoteku |
| `version` | broj | `3`. Dokument verzije 1 daje `time` postavljanja u sekundama meča; od verzije 2 to su sekunde u rundi, kao kod ubojstva. 3 dodaje polja od `header` nadalje i freeze time u tablicu. |
| `match` | niz | ime meča, kako su datoteke imenovane |
| `map` | niz | karta (`de_x`) |
| `demos` | niz[] | demo datoteke iz kojih je izgrađen, samo imena datoteka, redom meča |
| `teams` | niz[] | imena timova po redu pojavljivanja (runda 1: strana T prva) |
| `score` | objekt | ime tima -> broj pobjeda: rezultat zadnje runde |
| `rounds` | objekt[] | svaka potpuna runda, redom - [dolje](#rounds) |
| `incomplete` | broj[] | brojevi rundi prekinutih krajem demo snimke i izostavljenih |
| `missing` | broj[] | brojevi rundi prije prve koju demo snimke sadrže: `[1, 2]` kad snimka počinje u rundi 3 |
| `halfLength` | broj ili null | broj rundi u regularnom poluvremenu, od mjesta gdje se strane prvi put zamijene (`12` u formatu od 24 runde); null kad snimka ne pokazuje zamjenu |
| `pistolRounds` | broj[] | runde s pištoljima po kojima se broji `buy`: runda 1, i runda nakon poluvremena kad je `halfLength` poznat; nikad runda produženja |
| `players` | objekt[] | rezultatna tablica - [dolje](#players) |
| `conventions` | objekt | definicije iza brojeva, [dolje](#conventions) |
| `header` | objekt | zaglavlje prve demo snimke kako ga parser daje: ime poslužitelja, verzija patcha, verzija dema, karta |
| `profiles` | objekt | Steam ID -> ono što ostaje isto za igrača kroz cijeli meč: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (zadnje viđeno) |
| `playerInfo` | objekt[] | svaki igrač koji demo navodi, i treneri i komentatori: Steam ID, ime, broj tima |
| `skins`, `itemDrops` | objekt[] | skinovi oružja i ispadanja predmeta, gdje ih demo ima (turnirske demo snimke iz prijenosa ih nemaju) |
| `chat` | objekt[] | svaki redak chata u meču: vrijeme, runda, igrač, strana, tekst |
| `events` | objekt[] | svaki događaj igre koji se ne tiče nijednog igrača, po redu vremena, sa svim poljima: oznake rundi i faza, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (postavke poslužitelja kako su se mijenjale), kamera režisera prijenosa s praćenjem i fiksnim snimkama, `cs_win_panel_match`, ... |
| `state` | objekt[] | stanje igre gdje se promijenilo: vrijeme, polje, vrijednost - tajmauti (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, igrači živi, poslužiteljevi `match_start_time` i `round_start_time` |
| `selfCheck` | objekt | `completeness`: kamo je otišlo sve iz demo snimke - po imenu događaja, klasi svojstva, mrežnoj poruci, okviru i tablici nizova njihovi brojevi `seen`, `decoded`, `partial`, `raw` i `lost`, zapisane prateće datoteke, ukupno `lost` (0 osim uz `--no-bulk`), svojstva koja parser navodi ali ne može pročitati (`unreadProps`). Konvencija: [Pretvarači sve zadržavaju](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); prateće datoteke: odjeljak Completeness u README-u |

## Runde {#rounds}

| Polje | Tip | Što |
|---|---|---|
| `number` | broj | runda, počevši od 1 |
| `start` | broj | sekunde meča kad je freeze time završio |
| `end` | broj | sekunde meča kad je runda odlučena |
| `until` | broj | sekunde meča kad je sljedeća runda počela (kraj faze nakon) |
| `winner` | niz | `T` ili `CT`; prazno za neriješeno |
| `winnerTeam` | niz | naziv tima pobjedničke strane; prazno za neriješeno |
| `reason` | niz | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` ili `other` |
| `score` | objekt | ime tima -> broj pobjeda nakon ove runde |
| `sides` | objekt | ime tima -> `T` / `CT` u ovoj rundi |
| `equipment` | objekt | strana -> ukupna vrijednost opreme njezinih živih igrača na freeze endu, u dolarima |
| `buy` | objekt | strana -> `pistol`, `eco`, `force` ili `full` |
| `plant` | objekt ili null | postavljanje bombe: `site` (`A` ili `B`; prazno kad demo to ne kaže), `time` (sekunde **u rundi**, kao kod ubojstva), `player`, `steamid`, `x`, `y`, `z` (jedinice igre), `place` (naziv mjesta postavljača: gdje je bomba ležala) |
| `survivors` | objekt | strana -> imena početnih igrača koji su još bili živi kad je runda odlučena, poredana |
| `clutches` | objekt[] | svaki: `player`, `steamid`, `side`, `against` (neprijatelji živi kad je igrač postao zadnji), `won` |
| `kills` | objekt[] | svaka smrt runde, redom - dolje |

Kako se ovo pronalazi: [Sastavljanje meča](building-matches.md#rounds);
clutchevi i preživjeli: [Statistika](statistics.md#clutches).

### Ubojstva u rundi {#a-rounds-kills}

Svaka smrt u rundi, uključujući fazu nakon:

| Polje | Tip | Što |
|---|---|---|
| `time` | broj | sekunde **u rundi** (od kraja freeze timea) |
| `attacker`, `attackerSide` | niz | ubojica i njegova strana; prazno za svijet |
| `victim`, `victimSide` | niz | žrtva i njezina strana |
| `assister` | niz ili null | igrač koji je asistirao, ili null |
| `flashAssist` | bool | asistencija je bila bljeskom |
| `weapon` | niz | kako ga igra imenuje |
| `headshot` | bool | |
| `wallbang` | bool | metak je prošao kroz nešto |
| `throughSmoke` | bool | ubojstvo je bilo kroz dim |
| `noscope` | bool | oružje s optikom ispaljeno bez nje |
| `attackerBlind` | bool | ubojica je bio zaslijepljen |
| `opening` | bool | prvo ubojstvo neprijatelja u rundi |
| `traded` | bool | ova smrt je osvećena unutar 5 s |
| `trade` | bool | ovo ubojstvo je osvetilo suigrača unutar 5 s |
| `teamkill` | bool | napadač i žrtva na istoj strani, dva različita igrača |
| `suicide` | bool | napadač i žrtva isti igrač (vlastita granata, npr.); nije teamkill |
| `after` | bool | ubojstvo je bilo nakon što je runda odlučena |
| `place` | niz | gdje je bila **žrtva** (naziv mjesta na karti) |

## Igrači {#players}

Jedan unos po igraču, po timu, pa najbolji prvi po ubojstvima minus smrtima, pa po ubojstvima:

| Polje | Tip | Što |
|---|---|---|
| `name`, `steamid`, `team` | niz | tko |
| `kills`, `deaths` | broj | |
| `assists`, `flashAssists` | broj | asistencije bez bljeska i s bljeskom |
| `diff` | broj | ubojstva - smrti |
| `adr` | broj | prosječna šteta po odigranoj rundi, izgubljeno zdravlje |
| `kast` | broj | postotak odigranih rundi s ubojstvom, asistencijom, preživljavanjem ili razmijenjenom smrću |
| `headshotPct` | broj | postotak ubojstava koja su bila u glavu |
| `openingKills`, `openingDeaths` | broj | prvi dvoboji dobiveni i izgubljeni |
| `tradeKills`, `tradedDeaths` | broj | ubojstva razmjenom; smrti koje su razmijenjene |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: runde s toliko ubojstava |
| `clutches`, `clutchesWon` | broj | |
| `utilityDamage` | broj | šteta HE granatama, molotovima, zapaljivima |
| `enemiesFlashed` | broj | neprijatelji zaslijepljeni najmanje 1 s |
| `plants`, `defuses` | broj | |
| `teamkills` | broj | ubijeni suigrači; samoubojstva se ne broje |
| `roundsPlayed` | broj | započete runde |

Svaka definicija: [Statistika](statistics.md#the-scoreboard-line).

## Konvencije {#conventions}

Upisane su u svaki dokument, da čitatelj zna što brojevi znače i bez ove stranice:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Primjer {#an-example}

Iz sintetičke demo snimke s dvije runde iz testova, skraćeno (`...` označava ono što je izostavljeno):

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

Redoslijed ključeva unutar `survivors`, `equipment` i `buy` nije fiksan.
