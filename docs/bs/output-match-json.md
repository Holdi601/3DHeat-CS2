---
title: Dokument meča
nav_order: 9
lang: "bs"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Dokument meča (`<match>.match.json`) {#the-match-document-matchjson}

Jedan JSON dokument po meču, pored njegove tabele: timovi, rezultat, svaka runda
s rezultatom, ekonomijom, postavljanjem bombe, ubistvima, clutchevima i preživjelima, i red
tabele rezultata svakog igrača. To je ono što učitava kartica Meč preglednika 3DHeat.
Kod: `summary()` u
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
brojevi su definisani na stranici [Statistike](statistics.md).

Datoteka je UTF-8, uvučena za jedan razmak, i čuva ne-ASCII znakove
(imena igrača i timova) kakvi jesu. Vremena su sekunde, zaokružena na tri
decimale za runde i dvije za ubistva i postavljanje bombe.

## Dokument {#the-document}

| Polje | Tip | Šta |
|---|---|---|
| `format` | string | uvijek `heat3d-cs2-match` - kako čitač prepoznaje datoteku |
| `version` | number | `3`. Dokument verzije 1 daje `time` postavljanja u sekundama meča; od 2 to su sekunde u rundi, kao kod ubistva. 3 dodaje polja od `header` nadalje, i freeze vrijeme u tabeli. |
| `match` | string | ime meča, kako su datoteke imenovane |
| `map` | string | mapa (`de_x`) |
| `demos` | string[] | demo datoteke iz kojih je izgrađen, samo imena datoteka, redom meča |
| `teams` | string[] | imena timova redom pojavljivanja (runda 1: T strana prva) |
| `score` | object | ime tima -> dobijene runde: rezultat zadnje runde |
| `rounds` | object[] | svaka potpuna runda, redom - [ispod](#rounds) |
| `incomplete` | number[] | brojevi rundi prekinutih krajem demoa i izostavljenih |
| `missing` | number[] | brojevi rundi prije prve koju demoi sadrže: `[1, 2]` kad snimak počinje u rundi 3 |
| `halfLength` | number ili null | runde u regularnom poluvremenu, iz mjesta gdje se strane prvi put zamijene (`12` u formatu od 24 runde); null kad snimak ne pokazuje zamjenu |
| `pistolRounds` | number[] | pištolj runde s kojima se računa `buy`: runda 1, i runda poslije poluvremena kad je `halfLength` poznat; nikad runda produžetka |
| `players` | object[] | tabela rezultata - [ispod](#players) |
| `conventions` | object | definicije iza brojeva, [ispod](#conventions) |
| `header` | object | zaglavlje prvog demoa kako ga parser daje: ime servera, verzija patcha, verzija demoa, mapa |
| `profiles` | object | Steam ID -> ono što ostaje isto za igrača kroz meč: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (zadnje viđeno) |
| `playerInfo` | object[] | svaki igrač koga demoi navode, i treneri i komentatori: Steam ID, ime, broj tima |
| `skins`, `itemDrops` | object[] | skinovi oružja i dropovi predmeta, gdje ih demo ima (turnirski demoi s prijenosa ih nemaju) |
| `chat` | object[] | svaki red četa u meču: vrijeme, runda, igrač, strana, tekst |
| `events` | object[] | svaki događaj igre koji ne vezuje nijednog igrača, redom vremena, sa svim njegovim poljima: zvučni signali i faze runde, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (postavke servera kako su se mijenjale), potjere i fiksni kadrovi direktora kamere prijenosa, `cs_win_panel_match`, ... |
| `state` | object[] | stanje igre gdje se promijenilo: vrijeme, polje, vrijednost - timeouti (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, živi igrači, serverov `match_start_time` i `round_start_time` |
| `selfCheck` | object | `completeness`: kamo je otišlo sve iz demoa - po imenu događaja, klasi svojstva, mrežnoj poruci, okviru i tabeli stringova njegovi brojevi `seen`, `decoded`, `partial`, `raw` i `lost`, napisane pomoćne datoteke, ukupno `lost` (0 osim uz `--no-bulk`), svojstva koja parser navodi ali ne može čitati (`unreadProps`). Konvencija: [Konverteri čuvaju sve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); pomoćne datoteke: odjeljak Completeness u README-u |

## Runde {#rounds}

| Polje | Tip | Šta |
|---|---|---|
| `number` | number | runda, od 1 |
| `start` | number | sekunde meča kad je freeze vrijeme završilo |
| `end` | number | sekunde meča kad je runda odlučena |
| `until` | number | sekunde meča kad je sljedeća runda počela (kraj faze poslije) |
| `winner` | string | `T` ili `CT`; prazno za neriješeno |
| `winnerTeam` | string | ime tima pobjedničke strane; prazno za neriješeno |
| `reason` | string | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` ili `other` |
| `score` | object | ime tima -> dobijene runde nakon ove |
| `sides` | object | ime tima -> `T` / `CT` u ovoj rundi |
| `equipment` | object | strana -> ukupna vrijednost opreme njenih živih igrača na freeze endu, u dolarima |
| `buy` | object | strana -> `pistol`, `eco`, `force` ili `full` |
| `plant` | object ili null | postavljanje bombe: `site` (`A` ili `B`; prazno kad demo ne kaže), `time` (sekunde **u rundi**, kao kod ubistva), `player`, `steamid`, `x`, `y`, `z` (igrine jedinice), `place` (naziv mjesta postavljača: gdje je bomba ležala) |
| `survivors` | object | strana -> imena početnih igrača koji su još bili živi kad je runda odlučena, sortirano |
| `clutches` | object[] | svaki: `player`, `steamid`, `side`, `against` (neprijatelji živi kad je igrač postao zadnji), `won` |
| `kills` | object[] | svaka smrt runde, redom - ispod |

Kako se ovo nalazi: [Slaganje meča](building-matches.md#rounds);
clutchevi i preživjeli: [Statistike](statistics.md#clutches).

### Ubistva runde {#a-rounds-kills}

Svaka smrt u rundi, uključujući fazu poslije:

| Polje | Tip | Šta |
|---|---|---|
| `time` | number | sekunde **u rundi** (od freeze enda) |
| `attacker`, `attackerSide` | string | ubica i njegova strana; prazno za svijet |
| `victim`, `victimSide` | string | žrtva i njena strana |
| `assister` | string ili null | igrač koji je asistirao, ili null |
| `flashAssist` | bool | asistencija je bila flešom |
| `weapon` | string | kako ga igra imenuje |
| `headshot` | bool | |
| `wallbang` | bool | metak je prošao kroz nešto |
| `throughSmoke` | bool | ubistvo kroz dim |
| `noscope` | bool | optičko oružje ispaljeno bez optike |
| `attackerBlind` | bool | ubica je bio zasljepljen |
| `opening` | bool | prvo ubistvo neprijatelja u rundi |
| `traded` | bool | ova smrt je osvećena unutar 5 s |
| `trade` | bool | ovo ubistvo je osvetilo saigrača unutar 5 s |
| `teamkill` | bool | napadač i žrtva na istoj strani, dva različita igrača |
| `suicide` | bool | napadač i žrtva isti igrač (recimo vlastita granata); nije teamkill |
| `after` | bool | ubistvo je došlo nakon što je runda odlučena |
| `place` | string | gdje je bila **žrtva** (naziv mjesta na mapi) |

## Igrači {#players}

Jedan unos po igraču, po imenu tima, a zatim najbolji prvi po ubistvima minus
smrti, zatim ubistvima:

| Polje | Tip | Šta |
|---|---|---|
| `name`, `steamid`, `team` | string | ko |
| `kills`, `deaths` | number | |
| `assists`, `flashAssists` | number | asistencije bez i s flešom |
| `diff` | number | ubistva - smrti |
| `adr` | number | prosječna šteta po odigranoj rundi, izgubljeno zdravlje |
| `kast` | number | postotak odigranih rundi s ubistvom, asistencijom, preživljavanjem ili osvećenom smrću |
| `headshotPct` | number | postotak ubistava koja su bila headshotovi |
| `openingKills`, `openingDeaths` | number | dobijeni i izgubljeni opening dvoboji |
| `tradeKills`, `tradedDeaths` | number | trade ubistva; smrti koje su osvećene |
| `multiKills` | object | `{"2k": n, "3k": n, "4k": n, "5k": n}`: runde s toliko ubistava |
| `clutches`, `clutchesWon` | number | |
| `utilityDamage` | number | šteta s HE, molotovom, incendiary |
| `enemiesFlashed` | number | neprijatelji zasljepljeni barem 1 s |
| `plants`, `defuses` | number | |
| `teamkills` | number | ubijeni saigrači; samoubistva se ne računaju |
| `roundsPlayed` | number | započete runde |

Svaka definicija: [Statistike](statistics.md#the-scoreboard-line).

## Konvencije {#conventions}

Upisane u svaki dokument da čitač zna šta brojevi znače bez
ove stranice:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Primjer {#an-example}

Iz sintetičkog demoa od dvije runde iz testova, skraćeno (`...` označava ono što
je izostavljeno):

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
