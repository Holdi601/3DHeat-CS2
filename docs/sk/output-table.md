---
title: Tabuľka heatmapy
nav_order: 8
lang: "sk"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# Tabuľka heatmapy (`<match>.parquet`) {#the-heatmap-table-parquet}

Jeden súbor Parquet na zápas: pozícia každého živého hráča, vzorkovaná, a každá
udalosť tam, kde sa stala, jeden riadok na každú - dlhá tabuľka, ktorú prehliadač
3DHeat číta ako heatmapu, a ostatné nástroje ako obyčajnú tabuľku. Kód:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(súbor), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(riadky; pozrite [Zostavenie zápasu](building-matches.md)).

Súbor sa zapisuje s kompresiou Snappy v skupinách riadkov po 256 000 riadkoch.
Riadky sú zoradené podľa `time`, potom podľa `event`. Sú v ňom len riadky vnútri
kola (od konca jeho času zmrazenia po začiatok ďalšieho kola).

Na syntetickom deme z testov riadky udalostí prvého kola:

![riadky udalostí v tabuľke](../assets/img/table-rows.svg)

V kontajneri `.3dheat` je tabuľka členom s rolou `table`
([Jeden súbor na zápas](output-container.md)).

## Stĺpce {#columns}

Stĺpce vždy v tomto poradí. Textové stĺpce sú reťazce kódované slovníkom
(`dictionary<int32, string>`) a nikdy nie sú null: „žiadna hodnota“ je prázdny
reťazec. Číselné stĺpce sú null tam, kde riadok nemá hodnotu.

| Stĺpec | Typ | Čo |
|---|---|---|
| `match` | reťazec | názov zápasu (`alpha-vs-bravo-m1`, alebo `...-b` pre druhý reťazec) |
| `map` | reťazec | mapa z hlavičky dema (`de_x`) |
| `round` | int16 | číslo kola, od 1 |
| `roundId` | reťazec | `<match> #NN`, číslo kola dvoma číslicami (`alpha-vs-bravo-m1 #07`): jedinečné naprieč zápasmi, relácia prehliadača |
| `phase` | reťazec | `freeze` v čase zmrazenia kola (od konca predchádzajúceho kola), `live` až kým sa kolo nerozhodne, `after` kým víťazi hľadajú a porazení zachraňujú |
| `time` | float64 | sekundy od začiatku zápasu (živý začiatok jeho prvého súboru), na jedných hodinách naprieč jeho súbormi |
| `roundTime` | float32 | sekundy od konca času zmrazenia tohto kola; v čase zmrazenia záporné |
| `event` | reťazec | čo riadok je - pozrite [Udalosti](#events) |
| `player` | reťazec | meno hráča (pri každej udalosti, ktorý hráč, je uvedené nižšie) |
| `steamid` | reťazec | Steam ID hráča (64-bitové, ako text) |
| `side` | reťazec | `T` alebo `CT` v tomto kole; prázdne, keď hráč nebol na žiadnej strane |
| `team` | reťazec | názov tímu hráča (alebo `Started T` / `Started CT`); pri `explode` položiaci tím |
| `x`, `y`, `z` | float32 | pozícia v herných súradniciach: palce (herné jednotky), **Z nahor**, pravotočivé |
| `dirX`, `dirY`, `dirZ` | float32 | kam hráč hľadí, jednotkový vektor v tom istom rámci; iba pozície |
| `health` | int16 | 0-100; pozície, a pri `hurt` čo zostalo po zásahu |
| `armor` | int16 | 0-100; pozície, a pri `hurt` čo zostalo po zásahu |
| `money` | int32 | peniaze hráča; iba pozície |
| `equipment` | int32 | hodnota toho, čo hráč nesie; iba pozície |
| `weapon` | reťazec | zbraň tak, ako ju hra pomenúva (`AK-47`, `M4A1-S`, `Knife` pre každý skin noža) |
| `place` | reťazec | vlastný názov miesta mapy na pozícii riadku (`BombsiteA`, `CTSpawn`); prázdne pri výbuchoch granátov: demo nepomenúva miesto, kde granát vybuchol |
| `throwerPlace` | reťazec | názov miesta hádzajúceho, keď granát vybuchol; iba výbuchy granátov |
| `other` | reťazec | druhý hráč zabitia, smrti, zásahu alebo oslepenia |
| `damage` | float32 | stratené zdravie; iba `hurt` |
| `duration` | float32 | sekundy oslepenia; iba `blind` |
| `headshot` | int8 | 0/1; iba `kill` a `death` |
| `opening` | int8 | 0/1, prvé zabitie nepriateľa v kole; iba `kill` a `death` |
| `traded` | int8 | 0/1. Pri `kill`: bolo to odvetné zabitie. Pri `death`: smrť bola odvetená do 5 s. Iba `kill` a `death`. |
| `noscope` | int8 | 0/1, zabitie zameriavanou zbraňou vystrelenou nezameriavanou (udalosťové `noscope`); iba `kill` a `death` |
| `attackerBlind` | int8 | 0/1, zabíjač bol v čase zabitia oslepený (udalosťové `attackerblind`); iba `kill` a `death` |
| `won` | int8 | 0/1, či strana tohto riadku kolo vyhrala; null, keď `side` je prázdne |
| `buy` | reťazec | nákup strany tohto riadku v tom kole: `pistol`, `eco`, `force`, `full` |
| `detail` | reťazec | každé pole udalosti, ktoré ostatné stĺpce nenesú, ako objekt JSON (vlastné názvy hry): výstrel (`fire_bullets`: začiatok, uhly, nepresnosť, rozptyl, index spätného rázu, seed...), `dominated`, `revenge`, `attackerinair`, `wipe` smrti..., `defindex` predmetu; krok nemá nič |
| `text` | reťazec | riadok chatu; iba `chat` |
| `entity` | int32 | entita granátu: let `throw` (riadky `grenade`), jeho výbuch a hráči, ktorých oslepil, zdieľajú ju |
| `hitgroup` | reťazec | kam guľka zasiahla (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | stratený pancier; iba `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | kde na tele guľka zasiahla, v rámci obete v metroch (x dopredu, y nahor od chodidiel, z vpravo): lúč výstrelu (`fire_bullets`, inak oko a pohľad útočníka) vysledovaný na telo postavené tak, ako obeť stála a drepla, na časť, ktorú pomenúva `hitgroup`; iba `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | smer výstrelu v tom istom rámci; `hitMiss` ako ďaleko (m) lúč minul pomenovanú časť (0: prešiel cez ňu); `hitFrom` `bullet` alebo `aim` |
| `penetrated` | int16 | steny, cez ktoré prešla smrtiaca guľka; `kill` a `death` |
| `throughSmoke` | int8 | 0/1, zabitie cez dym; `kill` a `death` |
| `distance` | float32 | vzdialenosť zabitia tak, ako ju hra počíta (metre); `kill` a `death` |
| `assister` | reťazec | kto asistoval; `kill` a `death` |
| `flash`, `flashAlpha` | float32 | sekundy zostávajúceho bleskania a ako biele; pozície |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozície |
| `zoom`, `duck`, `moveType` | | úroveň priblíženia zameriavača, ako hlboko drepí (0-1), typ pohybu podľa hry; pozície |
| `spottedBy` | reťazec | Steam ID nepriateľov, ktorí tohto hráča vidia, oddelené `\|`; pozície |
| `inventory` | reťazec | všetko, čo hráč nesie, oddelené `\|`; pozície |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | zásobník držanej zbrane a záloha; výstrely v aktuálnej sérii; pozície |
| `punchPitch`, `punchYaw` | float32 | úder spätného rázu namierenia, stupne; pozície |
| `ping` | int16 | milisekundy; pozície |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | vlastné počty výsledkovej tabuľky hry za doterajší zápas; pozície |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | peniaze minuté v tomto kole a v zápase; hodnota výbavy na začiatku kola; pozície |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, stav hráča v čase riadku, vrátane udalostí: prilba, sada na zneškodnenie, akýkoľvek pancier, zameranie (od poslednej vzorky pozície hráča až po riadok), bleskanie (vnútri `blind`, ktoré ho zasiahlo); každý riadok, ktorý uvádza hráča |
| `state_utility` | int16 | granáty, ktoré hráč nesie v čase (z `inventory`); každý riadok, ktorý uvádza hráča |
| `state_weapon` | reťazec | zbraň v ruke v čase (pri `death` vlastná obete, kde `weapon` je zbraň zabijaka); každý riadok, ktorý uvádza hráča |
| `earn_round_cs2` | int16 | čo kolo vyplatilo: pri `round_end` odmenu za výhru alebo bonus za prehru (s bonusom strany, ktorá položila bombu), pri `plant` a `defuse` 300 hráča |

## Udalosti {#events}

Ktorého hráča riadok uvádza, kde stojí a ktoré stĺpce vypĺňa.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won` a `buy` sú vyplnené na každom riadku; `inventory`, `money`, `equipment` a
stĺpce `state_*` na každom riadku, ktorý uvádza hráča (udalosti ich berú z
poslednej vzorky pozície hráča).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Vyplnené aj |
|---|---|---|---|
| `position` | hráč | hráč (chodidlá) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (držaná), `place`, a celý stav hráča (stĺpce od `flash`) - aj v čase zmrazenia |
| `kill` | zabijak | kde zabijak stál | `other` (obeť), `weapon`, `headshot`, `opening`, `traded` (odvetné zabitie), `noscope`, `attackerBlind`, `place` |
| `death` | obeť | kde obeť padla | `other` (zabijak; prázdne pre svet), `weapon`, `headshot`, `opening`, `traded` (odvetené), `noscope`, `attackerBlind`, `place` |
| `hurt` | obeť | kde bola obeť zasiahnutá | `other` (útočník), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - aj zásahy spoluhráčov a sveta |
| `shot` | strelec | odkiaľ bol výstrel | `weapon`, `place`, `detail` (vlastný účet hry o guľkách) |
| `slash` | hráč | kde sa mával nožom | `weapon` = `Knife` |
| `grenade` | hádzajúci | granát v lete, pri vzorkovaní hráčov a tam, kde sa zastavil | `weapon` (granát), `entity` |
| `throw` | hádzajúci | odkiaľ bol granát hodený | `weapon` (granát), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | hádzajúci | kde vybuchol | `weapon`, `throwerPlace` (miesto hádzajúceho v tom okamihu); `place` zostáva prázdne |
| `blind` | oslepený hráč | kde stál | `other` (bleskovač), `duration`, `weapon` = `Flashbang`, `entity`, `place` - oslepení aj spoluhráči |
| `plant` | kladač | kde položil | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | zneškodňovateľ | kde zneškodnil | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | každý hráč, ktorý kolo odohral | kde hráč naposledy stál | `won`, `earn_round_cs2` (čo kolo vyplatilo: nárast peňazí strany do ďalšieho času zmrazenia, kde to pravidlá dovoľujú, inak vlastné pravidlá), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | kladač (s jeho Steam ID), strana `T`, položiaci tím | pozícia položenia | `weapon` = `C4 Explosive`, `place` (miesto kladača pri položení: kde ležala bomba); jej čas je, keď bomba vybuchla |
| `chat` | odosielateľ | kde bol | `text` |
| každá iná herná udalosť o hráčovi pod menom hry: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | hráč | kde bol (udalosti granátu: kde bol granát) | `weapon` (predmetu), `entity`, `detail` (každé pole udalosti) |

Čo je v tabuľke a čo nie:

- Riadky **position** sú živí hráči na strane, mimo času zmrazenia a rozcvičky,
  každých `--every` tikov (predvolene osem za sekundu).
- Riadky **kill** sú iba zabitia nepriateľom - žiadne tímové zabitie, samovražda
  ani smrť spôsobená svetom. Riadky **death** sú každá smrť, vrátane týchto.
- Riadky **explode** sú každá položená bomba, ktorá vybuchla, podľa udalosti
  `bomb_exploded` dema: aj vo fáze po skončení, keď T už vyhrali likvidáciou.
  Demo bez tejto udalosti dostane jeden pre každé kolo vyhrané bombou, na konci
  kola.
- Riadky **hurt** a **blind** sú iba medzi nepriateľmi.
- **shot** vynecháva nože a C4; granáty sú riadky **throw**.
- **molotov** pokrýva molotovy a zápalné granáty (začiatok ohňa).
- Poškodenie spoluhráčov, bleskanie spoluhráčov a divákov, udalosti v čase
  zmrazenia a čokoľvek medzi kolami nie sú v tabuľke.

Pracovný príklad zo syntetického dema z testov (hodený dym, otváracie zabitie
headshotom, odvety):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

Smrť bob je odvetená zabitím ace od ben 1,9 s neskôr (riadok `death` bob:
traded 1; riadok `kill` ben: odvetné zabitie, traded 1); druhý zásah do bob bol
137 poškodenia pri 40 zdravia, takže sa počíta ako 40.

## Nápovedy `heat3d` v päte {#the-heat3d-footer-hints}

Päta Parquet súboru (metadáta kľúč/hodnota schémy) nesie pokyny na čítanie pod
kľúčom **`heat3d`**, ako objekt JSON:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Položka | Hovorí |
|---|---|
| `version`, `kind` | verzia nápovedí (1) a čo ich zapísalo (`cs2-demo`) |
| `axes.up` | Z súboru je nahor |
| `axes.flipY` | znegujte Y súboru (pozrite nižšie) |
| `axes.scale` | 1: pozície sa používajú tak, ako sú, v herných jednotkách |
| `entity.size` | hráč je **32 jednotiek** široký - šírka hráča CS2 - veľkosť, akou box replay kreslí jedného hráča |
| `columns.x` / `y` / `z` | stĺpce pozície |
| `columns.time`, `timeUnit` | `time`, v sekundách |
| `columns.personId` | hráč je osoba |
| `columns.teamId` | strana je skupina (takže T a CT, nie názvy tímov, farbia skupiny) |
| `columns.sessionId` | každé kolo (`roundId`) je relácia |
| `columns.lookMode` a `dirX`-`dirZ` | smer pohľadu je vektor v týchto stĺpcoch |
| `columns.extra` | stĺpce, ktoré sa majú ponechať ako filtre, v poradí užitočnosti |

Prehliadač, ktorý kľúč pozná, otvorí súbor bez akéhokoľvek nastavenia. Ostatné
ho ignorujú. Ak ho chcete čítať sami:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Osi a jednotky {#axes-and-units}

Súradnice sú herné: **palce** (jedna herná jednotka; hráč je stojaci 72 jednotiek
vysoký a 32 široký), **Z nahor** a pravotočivé.

Prehliadač, ktorého svet je s Y nahor, musí kresliť herné (x, y, z) ako
**(x, z, -y)** - Z sa stane výškou a Y sa zneguje. To je rotácia, nie zrkadlenie.
Nakreslené tak, ako sa kreslí ľavotočivý svet s Z nahor, ako (x, z, y), každá
mapa vyjde zrkadlene, bombová zóna A na zlej strane; `flipY: true` je to, čo nápovedy
hovoria, aby sa tomu zabránilo. [Export mapy](map-export.md) zapisuje svoju
geometriu už v rámci (x, z, -y), v tých istých jednotkách, takže leží pod
tabuľkou bez akejkoľvek úpravy.

Vzdialenosti v prehliadači sú označené v metroch; pri mierke 1 sú to herné
jednotky. Na metre vynásobte 0,0254.

## Veľkosť {#size}

Pozície dominujú: asi desať hráčov krát osem vzoriek za sekundu živej hry pri
predvolenom `--every 8`, menej pre mŕtvych hráčov a čas zmrazenia. Polovičné
`--every` ich zdvojnásobí; udalosti sa nemenia.
