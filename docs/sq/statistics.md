---
title: "Statistikat"
nav_order: 7
lang: "sq"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Statistikat {#statistics}

Çfarë bëri çdo lojtar në një ndeshje, dhe si shkoi çdo raund: tabela e rezultateve dhe
lista e raundeve të [dokumentit të ndeshjes](output-match-json.md). Kodi:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Çdo gjë numërohet nga ndeshja e ndërtuar siç thuhet te
[Ndërtimi i një ndeshjeje](building-matches.md): regjistrat e vrasjeve të saj, dëmi (shëndeti
i humbur, vetëm armiqtë), verbimet (vetëm armiqtë) dhe rreshtat e saj.

![tabela e rezultateve si tekst e një ndeshjeje sintetike](../assets/img/scoreboard.svg)

## Konventat {#the-conventions}

Ku vetë loja nuk e përkufizon një numër, këto janë përkufizimet.
Shkruhen edhe në çdo dokument ndeshjeje nën `conventions`.

| Termi | Përkufizimi |
|---|---|
| **Trade** | Një vdekje është *traded* kur vrasësi i saj vritet nga një shok ekipi i viktimës brenda **5 s**; ajo vrasje është *trade kill*. |
| **Opening** | Vrasja e parë e një armiku në raund ndërsa është live. Një teamkill, një vetëvrasje ose një vdekje nga bota para saj anashkalohen. |
| **KAST** | Pjesa e raundeve ku një lojtar bëri një **K**ill (vrasje), një **A**ssist (asista), **S**urvived (mbijetoi), ose u **T**raded (u hakmor). Një asistë me flash llogaritet. |
| **Damage** | Shëndeti i humbur realisht, vetëm armiqtë: një goditje në kokë me dëm 137 mbi një lojtar me 40 shëndet është 40. |
| **Clutch** | Të jesh lojtari i fundit i gjallë i një ane me armiq ende në këmbë; fitohet kur ana fiton raundin. |
| **Buy** | Për anë, nga vlera mesatare e pajisjeve në fund të kohës së ngrirjes: raundi i parë i çdo pjese rregullore është raund pistoletash (raundi 1, dhe raundi pas pjesës, për sa kohë e luajti ndeshja), koha shtesë nuk ka; pastaj nën $1,500 eco, nën $4,000 force, përndryshe full. |

## Kush e nisi çdo raund {#who-started-each-round}

Disa numra duhet të dinë kush e luajti një raund. **Lojtarët fillestarë** të një raundi
janë, për anë, çdo lojtar me një rresht pozicioni live brenda një
sekonde nga pozicioni më i hershëm i atij raundi (domethënë, në sekondën e parë
pasi mbaroi koha e ngrirjes). **Raundet e luajtura** të një lojtari janë numri i
raundeve që nisi. Nëse një lojtar nuk nisi asnjë (nuk pati kurrë një rresht të tillë),
përdoret numri i raundeve të ndeshjes, që të mos ketë pjesëtim me zero.

## Linja e tabelës së rezultateve {#the-scoreboard-line}

Një hyrje për lojtar (shih [dokumentin e ndeshjes](output-match-json.md#players) për
emrat e fushave). "Vrasje armiku" më poshtë do të thotë një vrasje me sulmues, jo
teamkill, dhe jo vetëvrasje (e viktimës vetë).

| Fusha | Numëron |
|---|---|
| `kills` | vrasjet e armiqve, të fazës live dhe after |
| `deaths` | çdo vdekje: nga armiqtë, shokët e ekipit, vetja ose bota |
| `assists` | vrasjet e armiqve që ky lojtar i asistoi pa flash (asistuesi nuk duhet të jetë vrasësi) |
| `flashAssists` | vrasjet e armiqve që ky lojtar i asistoi me flash |
| `diff` | vrasje - vdekje |
| `adr` | dëmi (shëndet i humbur, vetëm armiqtë, të dyja fazat) / raundet e luajtura, një dhjetore |
| `kast` | 100 x (raunde me një vrasje, një asistë ose asistë flash, mbijetesë ose vdekje të hakmorur) / raundet e luajtura, një dhjetore. *Mbijetesa* është: një lojtar fillestar i raundit që nuk vdiq në të, në asnjërën fazë. |
| `headshotPct` | 100 x vrasje me goditje në kokë / vrasje, një dhjetore; 0 pa vrasje |
| `openingKills`, `openingDeaths` | duelet hapëse të fituara dhe të humbura |
| `tradeKills` | vrasje që hakmorën vdekjen e një shoku ekipi |
| `tradedDeaths` | vdekje që u hakmorën |
| `multiKills` | raunde me 2, 3, 4 dhe 5 vrasje armiqsh (`2k`, `3k`, `4k`, `5k`); më shumë se pesë llogaritet `5k`. Të dyja fazat llogariten. |
| `clutches`, `clutchesWon` | clutch-e të luajtura dhe të fituara (më poshtë) |
| `utilityDamage` | dëmi i bërë me granata HE, molotovë dhe incendiary, një dhjetore |
| `enemiesFlashed` | armiq të verbuar për **të paktën 1.0 s** nga flash-et e këtij lojtari |
| `plants`, `defuses` | vendosjet dhe çaktivizimet e bombës (rreshta të tabelës) |
| `teamkills` | shokë ekipi të vrarë. Një vetëvrasje - sulmuesi dhe viktima i njëjti lojtar, një granatë e vetë të themi - nuk është një: është vetëm një vdekje. |
| `roundsPlayed` | raunde të nisura, si më sipër |

Lojtarët listohen sipas emrit të ekipit (alfabetikisht), dhe brenda një ekipi sipas
`diff`, pastaj sipas `kills`, më i miri i pari.

Shënime për skajet:

- Një vrasje në fazën after - fituesit që ndjekin një lojtar që shpëton pajisjet - llogaritet
  si vrasje, vdekje, për ADR, multi-kill dhe KAST si çdo tjetër.
- Wallbang-et numërohen për lojtar brenda, por nuk shkruhen në
  dokumentin e ndeshjes; çdo vrasje në listën e raundeve thotë nëse ishte një.
- Pjesa *traded* e KAST i kredit viktimën e një vdekjeje të hakmorur në atë raund.
- Teamkill-et dhe vetëvrasjet i shtojnë viktimës një vdekje por askujt një vrasje; një
  teamkill i shton `teamkills` të vrasësit, një vetëvrasje asgjë tjetër.

## Clutch-et {#clutches}

Për çdo raund, lojtarët fillestarë të të dyja anëve merren si të gjallë, dhe
vrasjet live të raundit përshkohen sipas rendit. Pas çdo vdekjeje viktima
hiqet, dhe shikohet çdo anë: një anë me saktësisht **një** lojtar
të mbetur, dhe të paktën një armik ende të gjallë, është një clutch për atë lojtar
**kundër** numrit të armiqve të gjallë në atë moment. Çdo lojtar ka më së shumti
një clutch për raund; **fitohet** kur ana e atij lojtari fitoi
raundin.

Pasojat e përkufizimit:

- Të dyja anët mund të kenë një clutch në një raund. Nëse një anë mbetet një e para
  (një 1v3, të themi) dhe ana tjetër pastaj gjithashtu zbret në një,
  lojtari i dytë është në një clutch 1v1 të vetin.
- `against` është numri kur lojtari mbeti i fundit, jo në fund.
- Vrasjet e fazës after nuk përshkohen, kështu që nuk nisin një clutch
  dhe nuk e ndryshojnë një.

## Mbijetuesit {#survivors}

**Mbijetuesit** e një raundi janë, për anë, lojtarët e saj fillestarë minus kushdo
që vdiq ndërsa ishte live. Një lojtar i vrarë në fazën after ndërsa shpëtonte pajisjet
është prapë mbijetues në listën e raundeve - por nuk *mbijetoi* për KAST.

## Lista e raundeve {#the-round-list}

Çdo raund i dokumentit të ndeshjes mban rezultatin, shifrën, anët, ekonominë, vendosjen e bombës,
mbijetuesit, clutch-et dhe vrasjet e tij sipas rendit; shih
[Dokumenti i ndeshjes](output-match-json.md#rounds).

## Tabela e rezultateve si tekst {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` i printon këto numra për ekip;
shih [Komandat](commands.md#scoreboard---a-match-as-text).
