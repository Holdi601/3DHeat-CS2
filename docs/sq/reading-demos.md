---
title: "Leximi i një demoje"
nav_order: 5
lang: "sq"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Leximi i një demoje {#reading-a-demo}

Çfarë nxirret nga një skedar `.dem`, para se të interpretohet ndonjë gjë. Kodi:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Një demo e CS2 është regjistrimi i vetë serverit (SourceTV): çdo lojtar, çdo
tick, 64 tick-e në sekondë (`TICKRATE = 64`). Lexohet me
[demoparser2](https://github.com/LaihoE/demoparser) në tri thirrje, dhe
rezultati mbahet siç vjen, në një `RawPart`:

| Fusha | Mban |
|---|---|
| `path` | skedarin |
| `map` | `map_name` nga koka e demos (`de_x`); bosh nëse koka nuk ka |
| `samples` | një rresht për lojtar për tick të marrë si mostër: fushat e lojtarit dhe të rregullave më poshtë, plus `tick`, `steamid`, `name` |
| `events` | emri i ngjarjes -> rreshtat e saj, me fushat e lojtarëve të parashtesuara `user_`, `attacker_`, `assister_` siç i emërton parseri |

Asgjë në `demo.py` nuk vendos çfarë është një raund apo kush fitoi; kjo është
[Ndërtimi i një ndeshjeje](building-matches.md).

## Tick-et e marra si mostër {#the-sampled-ticks}

`parse_ticks` pyetet për tick-et `0, N, 2N, ...` deri në 4,000,000 (`LAST_TICK`,
shumë përtej çdo ndeshjeje - 17 orë me 64 tick-e në sekondë), ku *N* është `--every`
(parazgjedhje 8). Parseri ndalon në fund të demos. Çdo lojtar i pranishëm në një
tick të marrë si mostër jep një rresht, i gjallë, i vdekur, shikues apo trajner;
filtrimi bëhet më vonë.

Hapi i mostrimit ka rëndësi përtej dendësisë së hartës së nxehtësisë: momenti kur një raund
vendoset lexohet nga këto mostra (shih
[Ndërtimi i një ndeshjeje](building-matches.md#rounds)), kështu që kohët e fundit të raundeve janë
të sakta deri në një hap (1/8 s si parazgjedhje).

### Fushat e lojtarit {#player-fields}

| Prona | Bëhet |
|---|---|
| `X`, `Y`, `Z` | pozicioni, në njësitë e lojës (inçe), Z lart. demoparser2 jep origjinën e lojtarit, pra këmbët. |
| `yaw`, `pitch` | drejtimi i shikimit (gradë), kthyer në vektor njësi |
| `health`, `armor_value` | shëndeti, parzmorja |
| `team_num` | ana: 2 = T, 3 = CT; çdo gjë tjetër (shikuesit, 0, 1) nuk është anë |
| `team_clan_name` | emri i ekipit siç e tregon serveri, përdoret për të emërtuar ekipet |
| `active_weapon_name` | arma në dorë, siç e emërton loja (`AK-47`, `Karambit`) |
| `is_alive` | nëse lojtari është i gjallë - vetëm lojtarët e gjallë bëhen pozicione |
| `last_place_name` | emri i vendit të hartës (`BombsiteA`) |
| `balance` | paratë |
| `current_equip_value` | vlera e asaj që mbart lojtari |

### Fushat e rregullave të lojës {#game-rules-fields}

Lexohen paralelisht, një herë për rresht lojtari (janë të njëjta për të gjithë në një tick):

| Prona | Përdoret për |
|---|---|
| `game_time` | ora e serverit, në sekonda |
| `total_rounds_played` | numri i raundeve, që vazhdon nëpër skedarët e një ndeshjeje |
| `round_win_status` | kush fitoi raundin që sapo u luajt: 1 barazim, 2 T, 3 CT |
| `round_win_reason` | si (`CSRoundEndReason` i lojës) |
| `team_rounds_total` | rezultati i secilës anë |
| `is_warmup_period` | ngrohja lihet jashtë kudo |
| `is_freeze_period` | koha e ngrirjes lihet jashtë pozicioneve |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | koha shtesë që luhet, 0 në kohën rregullore: raundet e kohës shtesë nuk janë raunde pistoletash (parseri nuk ka emër më të shkurtër për të) |

## Ngjarjet {#the-events}

Çdo ngjarje më poshtë lexohet kur demoja e deklaron (`list_game_events`), me
`X`, `Y`, `Z`, `team_num`, `last_place_name` dhe `which_bomb_zone` (zona e
bombës ku qëndron lojtari: 0 asnjë, 1 A, 2 B) për çdo lojtar që e emërton ngjarja,
dhe `total_rounds_played` dhe `is_warmup_period` të lojës në atë
tick:

| Ngjarja | Bëhet |
|---|---|
| `player_death` | vrasje dhe vdekje; përdor `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | dëmi; përdor `dmg_health` (dëmi i bërë te shëndeti), `health` (shëndeti që mbeti), `weapon` |
| `player_blind` | lojtarët e verbuar; përdor `blind_duration` |
| `weapon_fire` | të shënat dhe hedhjet e granatave; përdor `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | ku shpërthyen granatat; përdor `x`, `y`, `z` e vetë ngjarjes (ngjarja nuk ka emër vendi për atë pikë, vetëm të hedhësit) |
| `bomb_planted` | vendosja e bombës; përdor `which_bomb_zone` dhe vendin e vendosësit, dhe `site` (numri i entitetit të zonës) |
| `bomb_defused` | çaktivizimi |
| `bomb_exploded` | kur shpërtheu bomba: koha e rreshtit `explode` |
| `round_freeze_end` | ku nis çdo raund |
| `round_prestart` | ku mbaron koha pas një raundi të vendosur |
| `round_announce_match_start` | ku nis ndeshja live |

## Dy fakte për demot që vendosin si lexohen {#two-facts-about-demos-that-decide-how-they-are-read}

- **Një ndeshje mund të ndahet nëpër skedarë**, dhe emrat e skedarëve nuk thonë
  renditjen e tyre. Numri i raundeve (`total_rounds_played`) vazhdon nëpër
  ta, dhe zakonisht edhe ora e serverit, kështu që pjesët mund të renditen nga
  ç'përmbajnë.
- **Një regjistrim mund të nisë para ndeshjes**: ngrohje, një rinisje, një raund
  me thika. Ndeshja nis te `round_announce_match_start` i **fundit** në një
  skedar; para tij çdo gjë lihet jashtë, dhe ngrohja lihet jashtë kudo.
