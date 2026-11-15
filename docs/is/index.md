---
title: "Heim"
nav_order: 1
lang: is
source: index.md
source_hash: "937e30dc7322"
nav_exclude: true
search_exclude: true
permalink: /is/
---
# 3DHeat CS2 {#dheat-cs2}

**Hvað er þetta?** Counter-Strike 2 getur vistað upptöku af leik, kallaða
*demo*. Þetta verkfæri breytir demo í skrár sem 3DHeat-skoðarinn getur sýnt í 3D:
hvar allir stóðu, dóu, köstuðu og settu sprengju, lotu fyrir lotu. Það getur líka
breytt CS2-korti í 3D líkan til að sýna þær á.

**Hvers vegna ætti ég að nota það?** Til að fara yfir þína eigin leiki, til að leggja marga leiki
af einu korti hvern yfir annan sem eitt hitakort, og fyrir leiktölfræði eins og ADR
(meðalskaði á lotu) og KAST (hlutfall lota þar sem leikmaður drap,
aðstoðaði, lifði af eða var „traded“).

**Dæmi:** `alpha-vs-bravo-m1.dem` inn, `out/de_x/alpha-vs-bravo-m1.3dheat`
út (`de_x` er tilbúið kortaheiti).

![demos: frá demo-skrám að einni skrá fyrir hvern leik](../assets/img/is/pipeline.svg)

Nánar: 3DHeat CS2 breytir **Counter-Strike 2 demo** í hitakortstöflu og leikjaskjal
fyrir hvern leik, og **CS2-korti** í borðarúmfræði. Úttakið er gert
fyrir [3DHeat](https://holdi601.github.io/3DHeat/) mælingaskoðarann
([kóði](https://github.com/Holdi601/3DHeat)), en það eru
venjulegar skrár - Parquet, JSON og glTF tvíundarskrá - sem hvað sem er annað getur
líka lesið.

Þetta er lítill Python-pakki, `heat3d_cs2`, keyrður úr skipanalínu. Hann les
demo af diski (hann sækir engin) með
[demoparser2](https://github.com/LaihoE/demoparser), og flytur út kort úr
uppsettum leiknum með skipanalínuútgáfu af Source2Viewer
([ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat)).

## Fljótleg byrjun {#quick-start}

Hefurðu aldrei notað skipanalínu? Lestu fyrst [Áður en þú byrjar](before-you-start.md).

```bash
pip install -r requirements.txt
python -m heat3d_cs2 demos <demo files or folders> -o out   # every match in them
python -m heat3d_cs2 map <map> -o out/<map>/<map>.glb       # the map from the installed game
python -m heat3d_cs2 scoreboard out/<map>/<match>.3dheat    # a match's scoreboard as text
```

Þú ættir að sjá `1 match(es), 1 at a time ...` og síðan eina línu fyrir hvern leik
(sjá [Skipanir](../commands.md#what-is-printed)).

`demos` skrifar, fyrir hvern leik, eina skrá í möppu nefnda eftir kortinu:
`out/<map>/<match>.3dheat`, [`.3dheat` gám](../output-container.md) - snið skoðarans með
einni skrá fyrir hvern leik ([lýsing](https://holdi601.github.io/3DHeat/container.html)).
Hann geymir þessa hluta; `--loose` skrifar þá sem aðskildar skrár í staðinn:

| Hluti | Hvað hann geymir | Hlaðið í skoðarann í |
|---|---|---|
| `<match>.parquet` (hlutverk `table`) | sérhvern lifandi leikmann átta sinnum á sekúndu með stöðu hans (heilsa, peningar, blinding, scoped, svæði, birgðir, ...), og sérhvern atburð þar sem hann gerðist (kill, death, hurt, shot, throw, sprengingar handsprengna, blind, plant, defuse, explode, og lok lotu fyrir hvern leikmann með því sem lotan gaf honum), ein röð hvert | flipanum Hitakort |
| `<match>.match.json` (hlutverk `match`, leikjaskjalið) | lið, stig, hverja lotu (sigurvegara, hvernig, hagkerfi, sprengju, dráp í röð, clutch, eftirlifendur) og stigatöflulínu hvers leikmanns | flipanum Leikur |
| `<match>.events/props/strings/packets.parquet` | allt annað sem demo-ið geymir, í heild (hliðarskrár) | geymt fyrir heilleika |

`map` skrifar `<map>.glb`: árekstrarnet kortsins (collision mesh) - gólf, veggir, kassar,
án skreytinga - skipt í land og mannvirki, í sama ramma og einingum
og töflurnar, svo það liggur nákvæmlega undir hitakortinu (spjaldið Bakgrunnur / borð).

## Kort yfir þessi skjöl {#map-of-this-documentation}

| Síða | Hvað hún fjallar um |
|---|---|
| [Áður en þú byrjar](before-you-start.md) | Python, skipanalína, staðgenglar, hvernig árangur og algengar villur líta út |
| [Uppsetning](../installing.md) | Python, pakkarnir, skipanalína Source2Viewer, hvar CS2 þarf að vera |
| [Skipanir](../commands.md) | `demos`, `map`, `scoreboard`: hver valkostur, hvað er prentað, útgöngukóðar |
| [Lestur demo](../reading-demos.md) | hvað er lesið úr demo-skrá: sýnatekin tikk, eigindir leikmanna, leikreglur, atburðir |
| [Að smíða leik](../building-matches.md) | hlutar og keðjur, leikklukkan, lotur, lið og hliðar, raðir, dráp, trades, opnanir, skaði, blindingar, hagkerfi |
| [Tölfræði](../statistics.md) | stigataflan: K/D/A, ADR, KAST, HS%, opnanir, trades, margföld dráp, clutch, utility, blindingar |
| [Hitakortstaflan](../output-table.md) | Parquet-skráin: hver dálkur, gerð hans, hvaða atburðir fylla hann, `heat3d` fótvísbendingarnar, ásarnir |
| [Leikjaskjalið](../output-match-json.md) | `.match.json` skjalið, reitur fyrir reit |
| [Ein skrá fyrir hvern leik](../output-container.md) | `.3dheat` gámurinn sem `demos` skrifar sjálfgefið, `--loose` |
| [Kortaútflutningur](../map-export.md) | hvernig árekstrarnet korts er flutt út, ramminn, nöfn hnúta, einingar |
| [Notkun með 3DHeat](../using-with-3dheat.md) | að hlaða töflum, leikjaskjölum og kortum í flipana Hitakort og Leikur í skoðaranum |
| [Takmarkanir](../limits.md) | hvað er gert ráð fyrir, hvað er ekki meðhöndlað, hvað er óstaðfest |
| [Uppfærslur](../updates.md) | útgáfuathugunin við ræsingu og `python -m heat3d_update` |
| [Þróun](../development.md) | uppbygging kóðans, prófanir, gervidemo-prófunarsafnið (fixture) |
| [Skipanayfirlit](../cli-reference.md) | `--help` hverrar skipunar, búið til úr kóðanum |
| [Viðhald](../maintaining.md) | útgáfugátlisti fyrir þessar síður |

## Hvað það er athugað gegn {#what-it-is-checked-against}

Demo úr náttúrunni eru ekki ein hrein skrá fyrir hvern leik. Umbreytirinn meðhöndlar
leik skiptan á skrár í hvaða röð sem er, þjón endurræstan í miðjum leik, tvo
mismunandi leiki geymda undir einu nafni, lotur endurheimtar úr öryggisafriti, upptöku
sem byrjar seint eða endar snemma, hlé, og þjálfara á hlið liðs -
sjá [Að smíða leik](../building-matches.md). Athugað yfir stórt safn
mótsdemoa: í hverjum leik
fylgja stigin lotusigurvegurunum, dráp hverrar hliðar eru dauðsföll hinnar,
og hver lota byrjar fimm gegn fimm.

## Hvað á að beina því að {#what-to-point-it-at}

Demo úr þínum eigin leikjum, demo sem þú sóttir í höndunum af mótsvef, eða demo
úr API sem þú hefur aðgang að. Demo er upptaka þar sem efnið
tilheyrir útgefanda hennar og skipuleggjendum: notaðu það sem kemur út til þinnar eigin
greiningar, og dreifðu ekki demo eða gögnum unnum úr þeim. Vefir sem
bjóða demo banna oft sjálfvirkt niðurhal í skilmálum sínum, sem er ástæðan fyrir því að
verkfærið les demo af diski og sækir engin.

## Hluti af 3DHeat {#part-of-3dheat}

3DHeat CS2 er eitt af ókeypis verkfærunum í kringum 3DHeat-skoðarann, hvert með sína eigin
geymslu, eigin útgáfur og leyfi:

| Verkfæri | Hvað það gerir | Skjöl |
|---|---|---|
| [3DHeat](https://github.com/Holdi601/3DHeat) | skoðarinn: hitakort, kappakstursgreining og leikjayfirlit í 3D | [vefur](https://holdi601.github.io/3DHeat/) |
| [GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | brautir og borð úr skrám sem leikir senda með, sem 3D líkön | [vefur](https://holdi601.github.io/3DHeat-GameFiles/) |
| [GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | hringmælingagögn úr kappakstursleikjum; borð endurbyggð úr leikmyndbandi | [vefur](https://holdi601.github.io/3DHeat-GameCapture/) |
| [Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | viðbót fyrir Unreal Editor sem flytur borð út sem eitt 3D líkan | [vefur](https://holdi601.github.io/3DHeat-UnrealExporter/) |
| [CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demo í töflur og leikjaskjöl; kort í 3D líkön | [vefur](https://holdi601.github.io/3DHeat-CS2/) |
| [Watcher](https://github.com/Holdi601/3DHeat-Watcher) | skráir í bakgrunni það sem leikir birta um leik þinn | [vefur](https://holdi601.github.io/3DHeat-Watcher/) |
| [Ext-WarThunder](https://github.com/Holdi601/3DHeat-Ext-WarThunder) | War Thunder upptökur í töflur og leikjaskjöl | [vefur](https://holdi601.github.io/3DHeat-Ext-WarThunder/) |
| [Ext-WoT](https://github.com/Holdi601/3DHeat-Ext-WoT) | World of Tanks upptökur í töflur og leikjaskjöl | [vefur](https://holdi601.github.io/3DHeat-Ext-WoT/) |
| [Ext-WoWs](https://github.com/Holdi601/3DHeat-Ext-WoWs) | World of Warships upptökur í töflur og leikjaskjöl | [vefur](https://holdi601.github.io/3DHeat-Ext-WoWs/) |
| [Ext-Squad](https://github.com/Holdi601/3DHeat-Ext-Squad) | Squad þjónsdemo í töflur og leikjaskjöl | [vefur](https://holdi601.github.io/3DHeat-Ext-Squad/) |
| [Ext-DCS](https://github.com/Holdi601/3DHeat-Ext-DCS) | DCS World kort í 3D líkön | [vefur](https://holdi601.github.io/3DHeat-Ext-DCS/) |
| [Ext-IL2](https://github.com/Holdi601/3DHeat-Ext-IL2) | IL-2 Sturmovik kort í 3D líkön | [vefur](https://holdi601.github.io/3DHeat-Ext-IL2/) |

## Leyfi {#licence}

MIT - sjá [`LICENSE`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSE),
og [`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md)
fyrir pakka þriðju aðila og það sem leikirnir sem það les skylda.
