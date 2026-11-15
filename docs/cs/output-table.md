---
title: Teplotní tabulka
nav_order: 8
lang: "cs"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# Teplotní tabulka (`<zápas>.parquet`) {#the-heatmap-table-parquet}

Jeden soubor Parquet na zápas: pozice každého živého hráče, vzorkované, a každá
událost v místě, kde se stala, jeden řádek na každou - dlouhá tabulka, kterou
prohlížeč 3DHeat čte jako teplotní mapu, a cokoli jiného jako obyčejnou
tabulku. Kód:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(soubor), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(řádky; viz [Sestavení zápasu](building-matches.md)).

Soubor se zapisuje s kompresí Snappy po skupinách řádků po 256 000 řádcích.
Řádky jsou seřazeny podle `time`, pak podle `event`. Patří do něj jen řádky uvnitř
kola (od konce jeho zmrazení po začátek dalšího kola).

Na syntetickém demu z testů: řádky událostí prvního kola:

![řádky událostí v tabulce](../assets/img/table-rows.svg)

V kontejneru `.3dheat` je tabulka položkou s rolí `table`
([Jeden soubor na zápas](output-container.md)).

## Sloupce {#columns}

Sloupce ve vždy stejném pořadí. Textové sloupce jsou řetězce kódované slovníkem
(`dictionary<int32, string>`) a nikdy nejsou null: „žádná hodnota“ je prázdný
řetězec. Číselné sloupce jsou null tam, kde řádek nemá hodnotu.

| Sloupec | Typ | Co |
|---|---|---|
| `match` | řetězec | název zápasu (`alpha-vs-bravo-m1`, nebo `...-b` pro druhý řetěz) |
| `map` | řetězec | mapa z hlavičky dema (`de_x`) |
| `round` | int16 | číslo kola, od 1 |
| `roundId` | řetězec | `<zápas> #NN`, číslo kola ve dvou číslicích (`alpha-vs-bravo-m1 #07`): jedinečné napříč zápasy, relace prohlížeče |
| `phase` | řetězec | `freeze` v zmrazení kola (od konce předchozího kola), `live` až do rozhodnutí kola, `after`, dokud vítězové hledají a poražení šetří |
| `time` | float64 | sekundy od začátku zápasu (živý začátek jeho prvního souboru), na společných hodinách napříč jeho soubory |
| `roundTime` | float32 | sekundy od konce zmrazení tohoto kola; záporné v zmrazení |
| `event` | řetězec | co řádek je - viz [Události](#events) |
| `player` | řetězec | jméno hráče (u každé události je níže uvedeno, který hráč) |
| `steamid` | řetězec | Steam ID hráče (64bitové, jako text) |
| `side` | řetězec | `T` nebo `CT` v tomto kole; prázdné, když hráč nebyl na žádné straně |
| `team` | řetězec | název týmu hráče (nebo `Started T` / `Started CT`); pro `explode` tým, který bombu položil |
| `x`, `y`, `z` | float32 | pozice v souřadnicích samotné hry: palce (herní jednotky), **Z nahoru**, pravotočivé |
| `dirX`, `dirY`, `dirZ` | float32 | kam se hráč dívá, jednotkový vektor ve stejném rámci; jen pozice |
| `health` | int16 | 0-100; pozice, a u `hurt` co zbylo po zásahu |
| `armor` | int16 | 0-100; pozice, a u `hurt` co zbylo po zásahu |
| `money` | int32 | peníze hráče; jen pozice |
| `equipment` | int32 | hodnota toho, co hráč nese; jen pozice |
| `weapon` | řetězec | zbraň tak, jak ji hra pojmenuje (`AK-47`, `M4A1-S`, `Knife` pro každý skin nože) |
| `place` | řetězec | název místa na mapě na pozici řádku (`BombsiteA`, `CTSpawn`); prázdné u detonací granátů: dema nepojmenují místo, kam granát dopadl |
| `throwerPlace` | řetězec | název místa hodícího, když granát vybuchl; jen detonace granátů |
| `other` | řetězec | druhý hráč zabití, smrti, zásahu nebo záblesku |
| `damage` | float32 | ztracené zdraví; jen `hurt` |
| `duration` | float32 | sekundy oslepení; jen `blind` |
| `headshot` | int8 | 0/1; jen `kill` a `death` |
| `opening` | int8 | 0/1, první zabití nepřítele v kole; jen `kill` a `death` |
| `traded` | int8 | 0/1. U `kill`: byl to odplatný kill. U `death`: byla pomstěna do 5 s. Jen `kill` a `death`. |
| `noscope` | int8 | 0/1, zabití zaměřovanou zbraní vystřelenou bez zaměření (`noscope` události); jen `kill` a `death` |
| `attackerBlind` | int8 | 0/1, vrah byl při zabití oslepen (`attackerblind` události); jen `kill` a `death` |
| `won` | int8 | 0/1, zda strana tohoto řádku vyhrála kolo; null, když je `side` prázdné |
| `buy` | řetězec | nákup strany tohoto řádku v tomto kole: `pistol`, `eco`, `force`, `full` |
| `detail` | řetězec | každé pole události, které ostatní sloupce nenesou, jako objekt JSON (herní názvy): výstřel (`fire_bullets`: počátek, úhly, nepřesnost, rozptyl, index zpětného rázu, seed...), `dominated`, `revenge`, `attackerinair`, `wipe`... smrti, `defindex` předmětu, u kroku nic |
| `text` | řetězec | řádek chatu; jen `chat` |
| `entity` | int32 | entita granátu: let hodu (řádky `grenade`), jeho detonace a hráči, které oslepil, ji sdílejí |
| `hitgroup` | řetězec | kam kulka zasáhla (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | ztracený pancíř; jen `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | kam na těle kulka zasáhla, v rámci oběti v metrech (x dopředu, y nahoru od nohou, z vpravo): paprsek výstřelu (`fire_bullets`, jinak oko útočníka a pohled) vystopovaný na tělo v pozici, v jaké oběť stála a dřepěla, na část, kterou pojmenovává `hitgroup`; jen `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | směr výstřelu ve stejném rámci; `hitMiss` jak daleko (m) paprsek minul pojmenovanou část (0: prošel jí); `hitFrom` `bullet` nebo `aim` |
| `penetrated` | int16 | zdi, kterými smrtící kulka prošla; `kill` a `death` |
| `throughSmoke` | int8 | 0/1, zabito přes kouř; `kill` a `death` |
| `distance` | float32 | vzdálenost zabití, jak ji hra počítá (metry); `kill` a `death` |
| `assister` | řetězec | kdo asistoval; `kill` a `death` |
| `flash`, `flashAlpha` | float32 | sekundy zbývajícího záblesku a jak bílý; pozice |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; pozice |
| `zoom`, `duck`, `moveType` | | úroveň přiblížení, jak hluboko dřepí (0-1), herní typ pohybu; pozice |
| `spottedBy` | řetězec | Steam ID nepřátel, kteří tohoto hráče vidí, oddělené `\|`; pozice |
| `inventory` | řetězec | všechno, co hráč nese, oddělené `\|`; pozice |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | zásobník a záloha držené zbraně; výstřely v aktuální dávce; pozice |
| `punchPitch`, `punchYaw` | float32 | náraz zpětného rázu na míření, stupně; pozice |
| `ping` | int16 | milisekundy; pozice |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | vlastní počty herní výsledkové tabule za zápas zatím; pozice |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | peníze utracené v tomto kole a v zápase; hodnota výbavy na začátku kola; pozice |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, stav hráče v čase řádku, včetně událostí: helma, sada na deaktivaci, jakýkoli pancíř, zaměřen (od posledního vzorku pozice hráče až po řádek), oslepen (uvnitř `blind`, které hráče zasáhlo); každý řádek, který jmenuje hráče |
| `state_utility` | int16 | granáty, které nese v čase (z `inventory`); každý řádek, který jmenuje hráče |
| `state_weapon` | řetězec | zbraň v ruce v čase (u `death` vlastní oběti, kde `weapon` je zbraň vraha); každý řádek, který jmenuje hráče |
| `earn_round_cs2` | int16 | co kolo vyplatilo: u `round_end` odměna za výhru nebo bonus za prohru (s bonusem strany, která bombu položila), u `plant` a `defuse` 300 pro hráče |

## Události {#events}

Který hráč řádek jmenuje, kde stojí a které sloupce vyplňuje.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`,
`won` a `buy` jsou vyplněné na každém řádku; `inventory`, `money`, `equipment` a
sloupce `state_*` na každém řádku, který jmenuje hráče (události je berou z
posledního vzorku pozice hráče).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Také vyplněno |
|---|---|---|---|
| `position` | hráč | hráč (nohy) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (držená), `place` a celý stav hráče (sloupce od `flash` dál) - i v zmrazení |
| `kill` | vrah | kde vrah stál | `other` (oběť), `weapon`, `headshot`, `opening`, `traded` (odplatné zabití), `noscope`, `attackerBlind`, `place` |
| `death` | oběť | kam oběť padla | `other` (vrah; prázdné pro svět), `weapon`, `headshot`, `opening`, `traded` (pomstěna), `noscope`, `attackerBlind`, `place` |
| `hurt` | oběť | kde byla oběť zasažena | `other` (útočník), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - i zásahy spoluhráčů a světa |
| `shot` | střelec | odkud byl výstřel vypálen | `weapon`, `place`, `detail` (herní popis kulek) |
| `slash` | hráč | kde byl nožem máchnuto | `weapon` = `Knife` |
| `grenade` | hodící | granát v letu, ve vzorkování hráčů a kde se zastavil | `weapon` (granát), `entity` |
| `throw` | hodící | odkud byl granát hozen | `weapon` (granát), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | hodící | kde vybuchl | `weapon`, `throwerPlace` (místo hodícího v ten okamžik); `place` zůstává prázdné |
| `blind` | oslepený hráč | kde stál | `other` (zábleskař), `duration`, `weapon` = `Flashbang`, `entity`, `place` - oslepení spoluhráči také |
| `plant` | plantér | kde položil | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | deaktivátor | kde deaktivoval | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | každý hráč, který kolo odehrál | kde hráč naposledy stál | `won`, `earn_round_cs2` (co kolo vyplatilo: vzestup peněz strany do dalšího zmrazení, kde to pravidla dovolí, jinak vlastní pravidla), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | plantér (s jeho Steam ID), strana `T`, tým, který položil | pozice položení | `weapon` = `C4 Explosive`, `place` (plantérovo při položení: kde bomba ležela); jeho čas je, kdy bomba vybuchla |
| `chat` | odesílatel | kde byl | `text` |
| každá jiná herní událost o hráči pod herním názvem: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | hráč | kde byl (u událostí granátu: kde granát byl) | `weapon` (předmětu), `entity`, `detail` (každé pole události) |

Co je dovnitř a co ne:

- Řádky **position** jsou živí hráči na straně, mimo zmrazení a rozcvičku,
  každých `--every` taktů (osm za sekundu ve výchozím nastavení).
- Řádky **kill** jsou jen zabití nepřítelem - žádné týmové zabití, sebevražda
  ani smrt způsobená světu. Řádky **death** jsou každá smrt, včetně těchto.
- Řádky **explode** jsou každá položená bomba, která vybuchla, podle
  `bomb_exploded` z dema: i ve fázi po, když T už vyhrálo eliminací. Dema bez
  této události dostanou jeden řádek za každé kolo, které vyhrála bomba, na konci kola.
- Řádky **hurt** a **blind** jsou jen mezi nepřáteli.
- **shot** vynechává nože a C4; granáty jsou řádky **throw**.
- **molotov** pokrývá molotovy i zápalné granáty (začátek ohně).
- Poškození spoluhráčů, záblesky spoluhráčů a diváků, události ve zmrazení
  a cokoli mezi koly v tabulce nejsou.

Příklad z práce, ze syntetického dema z testů (hozený kouř, otevírací zabití
headshotem, odplaty):

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

Bobovu smrt pomstí zabití ace od bena 1,9 s později (řádek `death` boba:
traded 1; řádek `kill` bena: odplatné zabití, traded 1); druhý zásah na boba
byl 137 poškození na 40 zdraví, takže se počítá 40.

## Nápovědy `heat3d` v patičce {#the-heat3d-footer-hints}

Patička souboru Parquet (metadata schématu klíč/hodnota) nese pokyny ke čtení
pod klíčem **`heat3d`**, objekt JSON:

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

| Položka | Říká |
|---|---|
| `version`, `kind` | verze nápověd (1) a co je zapsalo (`cs2-demo`) |
| `axes.up` | Z souboru je nahoře |
| `axes.flipY` | obrátit Y souboru (viz níže) |
| `axes.scale` | 1: pozice se používají tak, jak jsou, v herních jednotkách |
| `entity.size` | hráč má šířku **32 jednotek** - šířku hráče v CS2 - velikost, kterou přehrávání kvádrů kreslí jako jeho tělo |
| `columns.x` / `y` / `z` | sloupce pozic |
| `columns.time`, `timeUnit` | `time`, v sekundách |
| `columns.personId` | hráč je osoba |
| `columns.teamId` | strana je skupina (takže T a CT, ne názvy týmů, barví skupiny) |
| `columns.sessionId` | každé kolo (`roundId`) je relace |
| `columns.lookMode` a `dirX`-`dirZ` | směr pohledu je vektor v těchto sloupcích |
| `columns.extra` | sloupce, které se ponechají jako filtry, v pořadí užitečnosti |

Prohlížeč, který klíč zná, otevře soubor bez jakéhokoli nastavování. Ostatní ho
ignorují. Přečíst si ho sami:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Osy a jednotky {#axes-and-units}

Souřadnice jsou samotné hry: **palce** (jedna herní jednotka; hráč je stojící 72
jednotek vysoký a 32 široký), **Z nahoru**, pravotočivé.

Prohlížeč, jehož svět má Y nahoru, musí kreslit (x, y, z) hry jako
**(x, z, -y)** - Z se stane výškou a Y se obrátí. Je to rotace, ne zrcadlení.
Nakreslené způsobem levotočivého světa se Z nahoru, jako (x, z, y), by každá
mapa vyšla zrcadlově, místo A na špatné straně; `flipY: true` je to, co nápovědy
říkají, aby se tomu zabránilo. [Export mapy](map-export.md) zapisuje svou geometrii
už v rámci (x, z, -y), ve stejných jednotkách, takže leží pod tabulkou bez
jakéhokoli přizpůsobení.

Vzdálenosti v prohlížeči jsou označené v metrech; při měřítku 1 jsou to herní
jednotky. Pro metry vynásobte 0,0254.

## Velikost {#size}

Převažují pozice: zhruba deset hráčů krát 8 vzorků za sekundu živé hry při
výchozím `--every 8`, méně pro mrtvé hráče a zmrazení. Půlení `--every` pozice
zdvojnásobí; události to neovlivní.
