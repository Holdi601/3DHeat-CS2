---
title: Documentul meciului
nav_order: 9
lang: "ro"
source: output-match-json.md
source_hash: "8f8b6aee7aff"
nav_exclude: true
search_exclude: true
---
# Documentul meciului (`<meci>.match.json`) {#the-match-document-matchjson}

Un document JSON pentru fiecare meci, lângă tabelul său: echipe, scor, fiecare rundă cu
rezultatul ei, economie, plantare, eliminări, clutch-uri și supraviețuitori, și linia de
tabel de scor a fiecărui jucător. Este ceea ce încarcă fila Meci a vizualizatorului 3DHeat.
Cod: `summary()` din
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
cifrele sunt definite pe pagina [Statistici](statistics.md).

Fișierul este UTF-8, indentat cu un spațiu, și păstrează caracterele non-ASCII (numele
jucătorilor și ale echipelor) așa cum sunt. Timpii sunt în secunde, rotunjiți la trei zecimale
pentru runde și la două pentru eliminări și plantare.

## Documentul {#the-document}

| Câmp | Tip | Ce este |
|---|---|---|
| `format` | șir | mereu `heat3d-cs2-match` - cum recunoaște un cititor fișierul |
| `version` | număr | `3`. Un document versiunea 1 dă `time` al unei plantări în secunde de meci; de la 2 este în secunde în interiorul rundei, ca cel al unei eliminări. 3 adaugă câmpurile de la `header` încolo și timpul de îngheț în tabel. |
| `match` | șir | numele meciului, așa cum sunt numite fișierele |
| `map` | șir | harta (`de_x`) |
| `demos` | șir[] | fișierele demo din care a fost construit, doar numele fișierelor, în ordinea meciului |
| `teams` | șir[] | numele echipelor în ordinea apariției (runda 1: partea T întâi) |
| `score` | obiect | numele echipei -> runde câștigate: scorul ultimei runde |
| `winner` | șir sau null | echipa care a câștigat meciul, acolo unde înregistrarea arată sfârșitul; null pentru o înregistrare care se oprește devreme, o prelungire fără panoul de câștig sau o egalitate |
| `winnerSource` | șir sau null | cum se știe `winner`: `winPanel` (panoul de câștig al meciului al jocului), `surrender` (capitulare), `regulation` (mai mult de jumătate din rundele regulamentare) |
| `rounds` | obiect[] | fiecare rundă completă, în ordine - [mai jos](#rounds) |
| `incomplete` | număr[] | numerele rundelor întrerupte de sfârșitul unui demo și lăsate afară |
| `missing` | număr[] | numerele rundelor dinaintea primei pe care demo-urile o țin: `[1, 2]` când înregistrarea începe cu runda 3 |
| `halfLength` | număr sau null | rundele dintr-o repriză regulamentară, de unde taberele schimbă prima dată părțile (`12` în formatul de 24 de runde); null când înregistrarea nu arată schimbarea |
| `pistolRounds` | număr[] | rundele de pistol după care se numără `buy`: runda 1, și runda de după repriză când se cunoaște `halfLength`; niciodată o rundă de prelungire |
| `players` | obiect[] | tabelul de scor - [mai jos](#players) |
| `conventions` | obiect | definițiile din spatele cifrelor, [mai jos](#conventions) |
| `header` | obiect | antetul primului demo, așa cum îl dă parserul: numele serverului, versiunea patch-ului, versiunea demo-ului, harta |
| `profiles` | obiect | ID Steam -> ce rămâne la fel pentru un jucător pe tot meciul: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (ultima văzută) |
| `playerInfo` | obiect[] | fiecare jucător listat de demo-uri, inclusiv antrenorii și comentatorii: ID Steam, nume, numărul echipei |
| `skins`, `itemDrops` | obiect[] | skin-uri de arme și obiecte căzute, acolo unde demo-ul le are (demo-urile de turneu din transmisie nu au) |
| `chat` | obiect[] | fiecare linie de chat din meci: timp, rundă, jucător, parte, text |
| `events` | obiect[] | fiecare eveniment de joc care nu privește niciun jucător, în ordinea timpului, cu toate câmpurile sale: sunetele rundei și fazele, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (setările serverului pe măsură ce s-au schimbat), urmărirea și planurile fixe ale regizorului de cameră al transmisiei, `cs_win_panel_match`, ... |
| `state` | obiect[] | starea jocului acolo unde s-a schimbat: timp, câmp, valoare - timeout-urile (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, jucătorii în viață, `match_start_time` și `round_start_time` ale serverului |
| `selfCheck` | obiect | `completeness`: unde a ajuns totul din demo - pentru fiecare nume de eveniment, clasă de proprietăți, mesaj de rețea, cadru și tabel de șiruri, numărările lor `seen`, `decoded`, `partial`, `raw` și `lost`, fișierele anexe scrise, totalul `lost` (0 decât cu `--no-bulk`), proprietățile pe care parserul le listează dar nu le poate citi (`unreadProps`). Convenția: [Convertoarele păstrează tot](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); fișierele anexe: secțiunea Completeness din README |

## Runde {#rounds}

| Câmp | Tip | Ce este |
|---|---|---|
| `number` | număr | runda, de la 1 |
| `start` | număr | secunde de meci când s-a încheiat timpul de îngheț |
| `end` | număr | secunde de meci când runda a fost decisă |
| `until` | număr | secunde de meci când a început următoarea rundă (sfârșitul fazei după) |
| `winner` | șir | `T` sau `CT`; gol pentru o egalitate |
| `winnerTeam` | șir | numele echipei părții câștigătoare; gol pentru o egalitate |
| `reason` | șir | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` sau `other` |
| `score` | obiect | numele echipei -> runde câștigate după aceasta |
| `sides` | obiect | numele echipei -> `T` / `CT` în această rundă |
| `equipment` | obiect | parte -> valoarea totală a echipamentului jucătorilor săi în viață la sfârșitul timpului de îngheț, în dolari |
| `buy` | obiect | parte -> `pistol`, `eco`, `force` sau `full` |
| `plant` | obiect sau null | plantarea bombei: `site` (`A` sau `B`; gol când demo-ul nu spune), `time` (secunde **în interiorul rundei**, ca al unei eliminări), `player`, `steamid`, `x`, `y`, `z` (unități de joc), `place` (numele locului plantatorului: unde stătea bomba) |
| `survivors` | obiect | parte -> numele jucătorilor de start încă în viață când runda a fost decisă, sortate |
| `clutches` | obiect[] | fiecare: `player`, `steamid`, `side`, `against` (inamici în viață când jucătorul a devenit ultimul), `won` |
| `kills` | obiect[] | fiecare moarte din rundă, în ordine - mai jos |

Cum sunt găsite: [Cum se construiește un meci](building-matches.md#rounds);
clutch-urile și supraviețuitorii: [Statistici](statistics.md#clutches).

### Eliminările unei runde {#a-rounds-kills}

Fiecare moarte din rundă, inclusiv cele din faza după:

| Câmp | Tip | Ce este |
|---|---|---|
| `time` | număr | secunde **în interiorul rundei** (de la sfârșitul timpului de îngheț) |
| `attacker`, `attackerSide` | șir | ucigașul și partea sa; gol pentru lume |
| `victim`, `victimSide` | șir | victima și partea sa |
| `assister` | șir sau null | jucătorul care a asistat, sau null |
| `flashAssist` | bool | asistența a fost un flash |
| `weapon` | șir | așa cum o numește jocul |
| `headshot` | bool | |
| `wallbang` | bool | glonțul a trecut prin ceva |
| `throughSmoke` | bool | eliminarea a fost prin fum |
| `noscope` | bool | o armă cu lunetă a tras fără lunetă |
| `attackerBlind` | bool | ucigașul fusese orbit |
| `opening` | bool | prima eliminare a unui inamic din rundă |
| `traded` | bool | această moarte a fost răzbunată în 5 s |
| `trade` | bool | această eliminare a răzbunat un coechipier în 5 s |
| `teamkill` | bool | atacatorul și victima sunt de aceeași parte, doi jucători diferiți |
| `suicide` | bool | atacatorul și victima sunt același jucător (o grenadă proprie, de exemplu); nu un teamkill |
| `after` | bool | eliminarea a venit după ce runda a fost decisă |
| `place` | șir | unde era **victima** (numele locului de pe hartă) |

## Jucători {#players}

Câte o intrare pentru fiecare jucător, pe echipă și apoi cel mai bun întâi după eliminări
minus morți, apoi după eliminări:

| Câmp | Tip | Ce este |
|---|---|---|
| `name`, `steamid`, `team` | șir | cine |
| `kills`, `deaths` | număr | |
| `assists`, `flashAssists` | număr | asistențe fără și cu flash |
| `diff` | număr | eliminări - morți |
| `adr` | număr | daune medii pe rundă jucată, sănătate pierdută |
| `kast` | număr | procentul rundelor jucate cu o eliminare, o asistență, o supraviețuire sau o moarte răzbunată |
| `headshotPct` | număr | procentul eliminărilor care au fost lovituri în cap |
| `openingKills`, `openingDeaths` | număr | dueluri de deschidere câștigate și pierdute |
| `tradeKills`, `tradedDeaths` | număr | eliminări de răzbunare; morți care au fost răzbunate |
| `multiKills` | obiect | `{"2k": n, "3k": n, "4k": n, "5k": n}`: runde cu atâtea eliminări |
| `clutches`, `clutchesWon` | număr | |
| `utilityDamage` | număr | daune cu HE, molotov, incendiară |
| `enemiesFlashed` | număr | inamici orbiți cel puțin 1 s |
| `plants`, `defuses` | număr | |
| `teamkills` | număr | coechipieri uciși; sinuciderile nu se numără |
| `roundsPlayed` | număr | runde începute |

Fiecare definiție: [Statistici](statistics.md#the-scoreboard-line).

## Convenții {#conventions}

Scrise în fiecare document, ca un cititor să știe ce înseamnă cifrele fără această pagină:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: prima rundă a fiecărei reprize regulamentare (pistolRounds), niciuna în prelungire; altfel, echipament mediu sub 1500 $ eco, sub 4000 $ force, altfel full",
 "damage": "sănătatea efectiv pierdută, doar inamici",
 "kast": "runde cu o eliminare, o asistență (asistențele de flash contează), supraviețuire sau o moarte răzbunată"
}
```

## Un exemplu {#an-example}

Din demo-ul sintetic cu două runde din teste, scurtat (`...` marchează ce este lăsat afară):

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

Ordinea cheilor din `survivors`, `equipment` și `buy` nu este fixă.
