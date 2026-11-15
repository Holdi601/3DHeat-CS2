---
title: Dokument zápasu
nav_order: 9
lang: "sk"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# Dokument zápasu (`<match>.match.json`) {#the-match-document-matchjson}

Jeden dokument JSON na zápas, vedľa jeho tabuľky: tímy, skóre, každé kolo s
jeho výsledkom, ekonomikou, položením, zabitiami, clutchmi a preživšími a výsledkový
riadok každého hráča. Je to to, čo načítava karta Zápas prehliadača 3DHeat.
Kód: funkcia `summary()` v
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
čísla sú definované na stránke [Štatistika](statistics.md).

Súbor je v UTF-8, odsadený jednou medzerou a zachováva znaky mimo ASCII (mená
hráčov a tímov) tak, ako sú. Časy sú v sekundách, zaokrúhlené na tri desatinné
miesta pri kolách a na dve pri zabitiach a položení.

## Dokument {#the-document}

| Pole | Typ | Čo |
|---|---|---|
| `format` | reťazec | vždy `heat3d-cs2-match` - podľa neho čitateľ súbor spozná |
| `version` | číslo | `3`. Dokument verzie 1 dáva čas položenia `time` v sekundách zápasu; od verzie 2 je to sekundy v kole, ako pri zabití. Verzia 3 pridáva polia od `header` ďalej a čas zmrazenia do tabuľky. |
| `match` | reťazec | názov zápasu, ako sú pomenované súbory |
| `map` | reťazec | mapa (`de_x`) |
| `demos` | reťazec[] | súbory dema, z ktorých bol zostavený, iba názvy súborov, v poradí zápasu |
| `teams` | reťazec[] | názvy tímov v poradí výskytu (kolo 1: najprv strana T) |
| `score` | objekt | názov tímu -> vyhraté kolá: skóre posledného kola |
| `rounds` | objekt[] | každé úplné kolo, v poradí - [nižšie](#rounds) |
| `incomplete` | číslo[] | čísla kôl prerušených koncom dema a vynechaných |
| `missing` | číslo[] | čísla kôl pred prvým, ktoré demá obsahujú: `[1, 2]`, keď nahrávka začína v kole 3 |
| `halfLength` | číslo alebo null | počet kôl v riadnom polčase, od miesta, kde sa strany prvýkrát vymenia (`12` vo formáte 24 kôl); null, keď nahrávka výmenu neukazuje |
| `pistolRounds` | číslo[] | pistolové kolá, podľa ktorých sa počíta `buy`: kolo 1 a kolo po polčase, ak je `halfLength` známe; nikdy kolo predĺženia |
| `players` | objekt[] | výsledková tabuľka - [nižšie](#players) |
| `conventions` | objekt | definície za číslami, [nižšie](#conventions) |
| `header` | objekt | hlavička prvého dema tak, ako ju dáva parser: názov servera, verzia patchu, verzia dema, mapa |
| `profiles` | objekt | Steam ID -> to, čo sa u hráča počas zápasu nemení: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (naposledy videné) |
| `playerInfo` | objekt[] | každý hráč, ktorého demá uvádzajú, vrátane trénerov a komentátorov: Steam ID, meno, číslo tímu |
| `skins`, `itemDrops` | objekt[] | skiny zbraní a pády predmetov, ak ich demo má (turnajové demá z vysielania ich nemajú) |
| `chat` | objekt[] | každý riadok chatu v zápase: čas, kolo, hráč, strana, text |
| `events` | objekt[] | každá herná udalosť, ktorá sa netýka žiadneho hráča, v poradí času, so všetkými poľami: hlásenia a fázy kola, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (nastavenia servera, keď sa menia), záberové režisérske prechody a pevné zábery vysielacej kamery, `cs_win_panel_match`, ... |
| `state` | objekt[] | stav hry, keď sa zmenil: čas, pole, hodnota - časové výpadky (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, živí hráči, `match_start_time` a `round_start_time` servera |
| `selfCheck` | objekt | `completeness`: kam sa dostalo všetko z dema - pre každý názov udalosti, triedu vlastností, sieťovú správu, snímok a tabuľku reťazcov jeho počty `seen`, `decoded`, `partial`, `raw` a `lost`, zapísané pomocné súbory, celkové `lost` (0, pokiaľ nie je `--no-bulk`), vlastnosti, ktoré parser uvádza, ale nedokáže ich prečítať (`unreadProps`). Konvencia: [Konvertory si ponechajú všetko](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); pomocné súbory: sekcia Completeness v README |

## Kolá {#rounds}

| Pole | Typ | Čo |
|---|---|---|
| `number` | číslo | kolo, od 1 |
| `start` | číslo | sekundy zápasu, keď sa skončil čas zmrazenia |
| `end` | číslo | sekundy zápasu, keď bolo kolo rozhodnuté |
| `until` | číslo | sekundy zápasu, keď sa začalo ďalšie kolo (koniec fázy po skončení) |
| `winner` | reťazec | `T` alebo `CT`; prázdne pri remíze |
| `winnerTeam` | reťazec | názov tímu víťaznej strany; prázdne pri remíze |
| `reason` | reťazec | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` alebo `other` |
| `score` | objekt | názov tímu -> vyhraté kolá po tomto |
| `sides` | objekt | názov tímu -> `T` / `CT` v tomto kole |
| `equipment` | objekt | strana -> celková hodnota výbavy jej živých hráčov na konci zmrazenia, v dolároch |
| `buy` | objekt | strana -> `pistol`, `eco`, `force` alebo `full` |
| `plant` | objekt alebo null | položenie bomby: `site` (`A` alebo `B`; prázdne, keď demo nehovorí), `time` (sekundy **v kole**, ako pri zabití), `player`, `steamid`, `x`, `y`, `z` (herné jednotky), `place` (názov miesta kladača: kde ležala bomba) |
| `survivors` | objekt | strana -> mená začiatočných hráčov, ktorí boli nažive, keď sa kolo rozhodlo, zoradené |
| `clutches` | objekt[] | každý: `player`, `steamid`, `side`, `against` (nepriatelia nažive, keď sa hráč stal posledným), `won` |
| `kills` | objekt[] | každá smrť v kole, v poradí - nižšie |

Ako sa tieto zisťujú: [Zostavenie zápasu](building-matches.md#rounds);
clutche a preživší: [Štatistika](statistics.md#clutches).

### Zabitia v kole {#a-rounds-kills}

Každá smrť v kole, vrátane fázy po skončení:

| Pole | Typ | Čo |
|---|---|---|
| `time` | číslo | sekundy **v kole** (od konca zmrazenia) |
| `attacker`, `attackerSide` | reťazec | zabíjač a jeho strana; prázdne pre svet |
| `victim`, `victimSide` | reťazec | obeť a jej strana |
| `assister` | reťazec alebo null | asistujúci hráč, alebo null |
| `flashAssist` | bool | asistencia bola bleskom |
| `weapon` | reťazec | tak, ako ju hra pomenúva |
| `headshot` | bool | |
| `wallbang` | bool | guľka prešla cez niečo |
| `throughSmoke` | bool | zabitie cez dym |
| `noscope` | bool | zameriavaná zbraň vystrelila nezameraná |
| `attackerBlind` | bool | zabíjač bol oslepený |
| `opening` | bool | prvé zabitie nepriateľa v kole |
| `traded` | bool | táto smrť bola odvetená do 5 s |
| `trade` | bool | toto zabitie odvetilo spoluhráča do 5 s |
| `teamkill` | bool | útočník a obeť na tej istej strane, dvaja rôzni hráči |
| `suicide` | bool | útočník a obeť sú ten istý hráč (napríklad vlastný granát); nie tímové zabitie |
| `after` | bool | zabitie prišlo po rozhodnutí kola |
| `place` | reťazec | kde bola **obeť** (názov miesta na mape) |

## Hráči {#players}

Jeden záznam na hráča, zoradené podľa tímu a potom od najlepšieho podľa zabití
mínus smrti, potom zabití:

| Pole | Typ | Čo |
|---|---|---|
| `name`, `steamid`, `team` | reťazec | kto |
| `kills`, `deaths` | číslo | |
| `assists`, `flashAssists` | číslo | asistencie bez a s bleskom |
| `diff` | číslo | zabitia - smrti |
| `adr` | číslo | priemerné poškodenie na odohrané kolo, stratené zdravie |
| `kast` | číslo | percento odohraných kôl s zabitím, asistenciou, prežitím alebo odvetenou smrťou |
| `headshotPct` | číslo | percento zabití, ktoré boli headshotom |
| `openingKills`, `openingDeaths` | číslo | vyhrané a prehraté otváracie dvojboje |
| `tradeKills`, `tradedDeaths` | číslo | odvetné zabitia; smrti, ktoré boli odvetené |
| `multiKills` | objekt | `{"2k": n, "3k": n, "4k": n, "5k": n}`: kolá s toľkými zabitiami |
| `clutches`, `clutchesWon` | číslo | |
| `utilityDamage` | číslo | poškodenie HE, molotovom, zápalnými granátmi |
| `enemiesFlashed` | číslo | nepriatelia oslepení aspoň 1 s |
| `plants`, `defuses` | číslo | |
| `teamkills` | číslo | zabití spoluhráčov; samovraždy sa nepočítajú |
| `roundsPlayed` | číslo | začaté kolá |

Každá definícia: [Štatistika](statistics.md#the-scoreboard-line).

## Konvencie {#conventions}

Zapisujú sa do každého dokumentu, aby čitateľ vedel, čo čísla znamenajú, bez
tejto stránky:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Príklad {#an-example}

Zo syntetického dvojkolového dema z testov, skrátené (`...` označuje, čo sa
vynechalo):

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

Poradie kľúčov v `survivors`, `equipment` a `buy` nie je pevné.
