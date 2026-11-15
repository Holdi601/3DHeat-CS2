---
title: "Dokument tekme"
nav_order: 9
lang: "sl"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Dokument tekme (`<tekma>.match.json`) {#the-match-document-matchmatchjson}

En dokument JSON na tekmo, poleg njene tabele: ekipe, rezultat, vsaka runda z njenim izidom, ekonomijo, postavitvijo,
ubijanji, clutchi in preživelimi ter vrstica lestvice vsakega igralca. Pregledovalnik 3DHeat ga naloži v zavihku
Tekma. Koda: funkcija `summary()` v
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py); števila so definirana na
strani [Statistika](statistics.md).

Datoteka je v UTF-8, zamaknjena za en presledek, in ohranja znake, ki niso ASCII (imena igralcev in ekip), takšne, kot so.
Časi so v sekundah, zaokroženi na tri decimalke pri rundah in na dve pri ubijanjih in postavitvah.

## Dokument {#the-document}

| Polje | Tip | Kaj |
|---|---|---|
| `format` | niz | vedno `heat3d-cs2-match` – po tem bralnik prepozna datoteko |
| `version` | število | `3`. Dokument različice 1 da `time` postavitve v sekundah tekme; od 2 naprej so to sekunde v rundi, kot pri uboju. 3 doda polja od `header` naprej in zamrznitev v tabelo. |
| `match` | niz | ime tekme, kakor so datoteke poimenovane |
| `map` | niz | karta (`de_x`) |
| `demos` | niz[] | datoteke demo, iz katerih je zgrajena, samo imena datotek, po vrstnem redu tekme |
| `teams` | niz[] | imena ekip v vrstnem redu pojavitve (runda 1: stran T najprej) |
| `score` | objekt | ime ekipe -> število dobljenih rund: rezultat zadnje runde |
| `rounds` | objekt[] | vsaka dokončana runda, po vrsti – [spodaj](#rounds) |
| `incomplete` | število[] | številke rund, ki jih je prekinil konec dema, in so izpuščene |
| `missing` | število[] | številke rund pred prvo, ki jo imajo dema: `[1, 2]`, ko se posnetek začne pri rundi 3 |
| `halfLength` | število ali null | število rund v rednem polčasu, od mesta, kjer se strani prvič zamenjata (`12` v formatu 24 rund); null, kadar posnetek zamenjave ne kaže |
| `pistolRounds` | število[] | pištolske runde, s katerimi se šteje `buy`: runda 1 in runda po polčasu, kadar je `halfLength` znan; nikoli runda podaljška |
| `players` | objekt[] | lestvica – [spodaj](#players) |
| `conventions` | objekt | definicije za števila, [spodaj](#conventions) |
| `header` | objekt | glava prvega dema, kakor jo poda razčlenjevalnik: ime strežnika, različica popravka, različica demoja, karta |
| `profiles` | objekt | Steam ID -> kar se za igralca med tekmo ne spremeni: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (zadnje videno) |
| `playerInfo` | objekt[] | vsak igralec, naveden v demih, tudi trenerji in kasterji: Steam ID, ime, številka ekipe |
| `skins`, `itemDrops` | objekt[] | barve orožij in predmeti iz padcev, kjer jih demo ima (turnirski demoji iz prenosa jih nimajo) |
| `chat` | objekt[] | vsaka vrstica klepeta na tekmi: čas, runda, igralec, stran, besedilo |
| `events` | objekt[] | vsak dogodek igre, ki se ne tiče nobenega igralca, po času, z vsemi polji: zvoki in fazi runde, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (nastavitve strežnika, kakor so se spremenile), pogonski posnetki kamere prenosa (zasledovanje in fiksni posnetki), `cs_win_panel_match`, ... |
| `state` | objekt[] | stanje igre, kjer se je spremenilo: čas, polje, vrednost – časovne zahteve (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, živi igralci, strežnikov `match_start_time` in `round_start_time` |
| `selfCheck` | objekt | `completeness`: kam je šlo vse iz dema – po imenu dogodka, razredu lastnosti, omrežnem sporočilu, okvirju in vnosu tabele nizov njihove števce `seen`, `decoded`, `partial`, `raw` in `lost`, zapisane spremljevalne datoteke, skupni `lost` (0, razen pri `--no-bulk`), lastnosti, ki jih razčlenjevalnik našteje, a jih ne more prebrati (`unreadProps`). Konvencija: [Pretvorniki ohranijo vse](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); spremljevalne datoteke: razdelek Completeness v README-ju |

## Runde {#rounds}

| Polje | Tip | Kaj |
|---|---|---|
| `number` | število | runda, 1-indeksirana |
| `start` | število | sekunde tekme, ko se je končala zamrznitev |
| `end` | število | sekunde tekme, ko je bila runda odločena |
| `until` | število | sekunde tekme, ko se je začela naslednja runda (konec faze po) |
| `winner` | niz | `T` ali `CT`; prazno za remi |
| `winnerTeam` | niz | ime ekipe zmagovalne strani; prazno za remi |
| `reason` | niz | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` ali `other` |
| `score` | objekt | ime ekipe -> število dobljenih rund po tej |
| `sides` | objekt | ime ekipe -> `T` / `CT` v tej rundi |
| `equipment` | objekt | stran -> skupna vrednost opreme njenih živih igralcev ob koncu zamrznitve, v dolarjih |
| `buy` | objekt | stran -> `pistol`, `eco`, `force` ali `full` |
| `plant` | objekt ali null | postavitev bombe: `site` (`A` ali `B`; prazno, kadar demo tega ne pove), `time` (sekunde **v rundi**, kot pri uboju), `player`, `steamid`, `x`, `y`, `z` (enote igre), `place` (ime kraja postavljalca: kjer je bomba ležala) |
| `survivors` | objekt | stran -> imena začetnih igralcev, ki so bili še živi, ko je bila runda odločena, urejeno |
| `clutches` | objekt[] | vsak: `player`, `steamid`, `side`, `against` (sovražniki živi, ko je igralec postal zadnji), `won` |
| `kills` | objekt[] | vsaka smrt v rundi, po vrsti – spodaj |

Kako se to najde: [Gradnja tekme](building-matches.md#rounds); clutchi in preživeli: [Statistika](statistics.md#clutches).

### Uboji v rundi {#a-rounds-kills}

Vsaka smrt v rundi, vključno s fazo po koncu:

| Polje | Tip | Kaj |
|---|---|---|
| `time` | število | sekunde **v rundi** (od konca zamrznitve) |
| `attacker`, `attackerSide` | niz | ubijalec in njegova stran; prazno za svet |
| `victim`, `victimSide` | niz | žrtev in njena stran |
| `assister` | niz ali null | igralec, ki je asistiral, ali null |
| `flashAssist` | bool | asistenca je bila z bliskovko |
| `weapon` | niz | kakor ga imenuje igra |
| `headshot` | bool | |
| `wallbang` | bool | krogla je šla skozi nekaj |
| `throughSmoke` | bool | ubijanje je bilo skozi dim |
| `noscope` | bool | orožje z optiko izstreljeno brez nje |
| `attackerBlind` | bool | ubijalec je bil oslepljen |
| `opening` | bool | prvi sovražnikov uboj v rundi |
| `traded` | bool | ta smrt je bila maščevana v 5 s |
| `trade` | bool | ta uboj je maščeval soigralca v 5 s |
| `teamkill` | bool | napadalec in žrtev na isti strani, dva različna igralca |
| `suicide` | bool | napadalec in žrtev sta isti igralec (na primer lastna granata); ni prijateljski uboj |
| `after` | bool | uboj je prišel po tem, ko je bila runda odločena |
| `place` | niz | kje je bila **žrtev** (ime kraja na karti) |

## Igralci {#players}

En vnos na igralca, po ekipi, nato najboljši najprej po ubojih minus smrtih, nato po ubojih:

| Polje | Tip | Kaj |
|---|---|---|
| `name`, `steamid`, `team` | niz | kdo |
| `kills`, `deaths` | število | |
| `assists`, `flashAssists` | število | asistence brez in z bliskovko |
| `diff` | število | uboji - smrti |
| `adr` | število | povprečna škoda na odigrano rundo, izgubljeno zdravje |
| `kast` | število | odstotek odigranih rund z ubojem, asistenco, preživetjem ali maščevano smrtjo |
| `headshotPct` | število | odstotek ubojev, ki so bili zadetki v glavo |
| `openingKills`, `openingDeaths` | število | dvoboji prvega ubijanja, dobljeni in izgubljeni |
| `tradeKills`, `tradedDeaths` | število | maščevalni uboji; smrti, ki so bile maščevane |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: runde s toliko uboji |
| `clutches`, `clutchesWon` | število | |
| `utilityDamage` | število | škoda s HE, molotovko, zažigalno bombo |
| `enemiesFlashed` | število | sovražniki, oslepljeni vsaj 1 s |
| `plants`, `defuses` | število | |
| `teamkills` | število | ubiti soigralci; samomori se ne štejejo |
| `roundsPlayed` | število | začete runde |

Vsaka definicija: [Statistika](statistics.md#the-scoreboard-line).

## Konvencije {#conventions}

Zapisano v vsak dokument, da bralec ve, kaj števila pomenijo, tudi brez te strani:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Primer {#an-example}

Iz sintetičnega demoja z dvema rundama iz testov, skrajšano (`...` označuje izpuščeno):

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

Vrstni red ključev v `survivors`, `equipment` in `buy` ni fiksen.
