---
title: "Tölfræði"
nav_order: 7
lang: "is"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Tölfræði {#statistics}

Hvað hver leikmaður gerði í leik, og hvernig hver lota fór: stigataflan og
lotulistinn í [leikjaskjalinu](output-match-json.md). Kóði:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Allt er talið úr leiknum smíðuðum eins og á síðunni
[Að smíða leik](building-matches.md): fellingaskrám hans, skaða hans (tapað líf,
aðeins andstæðingar), blindum hans (aðeins andstæðingar) og röðum hans.

![the text scoreboard of a synthetic match](../assets/img/scoreboard.svg)

## Venjurnar {#the-conventions}

Þar sem leikurinn sjálfur skilgreinir ekki tölu eru þetta skilgreiningarnar.
Þær eru líka skrifaðar í hvert leikjaskjal undir `conventions`.

| Hugtak | Skilgreining |
|---|---|
| **Trade** | Dauða er *hefnt* (traded) þegar banamaður hans er felldur af einum liðsfélaga fórnarlambsins innan **5 s**; sú felling er *trade-felling*. |
| **Opening** | Fyrsta felling lotunnar á andstæðingi á meðan hún er lifandi. Teamkill, sjálfsvíg eða dauði af hendi heimsins á undan er sleppt. |
| **KAST** | Hlutfall lota þar sem leikmaður náði **K**illi (fellingu), **A**ssist (aðstoð; blindaðstoð telur), **S**urvived (lifði af), eða var **T**raded (hefnt). |
| **Damage** | Líf sem raunverulega tapast, aðeins andstæðingar: hausskot með 137 skaða á leikmann með 40 líf er 40. |
| **Clutch** | Að vera síðasti leikmaðurinn á lífi á hlið þegar andstæðingar standa enn; unnið þegar hliðin vinnur lotuna. |
| **Buy** | Fyrir hverja hlið, út frá meðalbúnaðarverðmæti við lok frystitíma: fyrsta lota hvers venjulegs hálfleiks er skammbyssulota (lota 1, og lotan eftir hálfleikinn, svo lengi sem leikurinn spilaði hana), framlenging hefur enga; síðan undir $1,500 eco, undir $4,000 force, annars full. |

## Hver byrjaði hverja lotu {#who-started-each-round}

Nokkrar tölur þurfa að vita hver spilaði lotu. **Upphafsleikmenn** lotu eru, fyrir hverja hlið, hver leikmaður
með lifandi staðarröð innan einnar sekúndu frá fyrstu stöðu þeirrar lotu (það er, á fyrstu sekúndu
eftir að frystitíminn endaði). **Spilaðar lotur** leikmanns eru fjöldi
lota sem hann byrjaði. Ef leikmaður byrjaði enga (hann hafði aldrei slíka röð),
er lotufjöldi leiksins notaður í staðinn, svo að aldrei sé deilt með núlli.

## Stigatöflulínan {#the-scoreboard-line}

Ein færsla fyrir hvern leikmann (sjá [leikjaskjalið](output-match-json.md#players) fyrir
reitaheitin). „Felling á andstæðingi“ hér að neðan merkir fellingu með árásarmanni, ekki
teamkill, og ekki sjálfsvíg (fórnarlambsins sjálfs).

| Reitur | Telur |
|---|---|
| `kills` | fellingar á andstæðingum, í live- og after-fasa |
| `deaths` | hvert dauðsfall: af hendi andstæðinga, liðsfélaga, sjálfs sín eða heimsins |
| `assists` | fellingar á andstæðingum sem þessi leikmaður aðstoðaði við án blindu (aðstoðarmaðurinn má ekki vera banamaðurinn) |
| `flashAssists` | fellingar á andstæðingum sem þessi leikmaður aðstoðaði við með blindu |
| `diff` | kills - deaths |
| `adr` | skaði (tapað líf, aðeins andstæðingar, báðir fasar) / spilaðar lotur, einn aukastafur |
| `kast` | 100 x (lotur með fellingu, aðstoð eða blindaðstoð, að lifa af eða hefnt dauðsfall) / spilaðar lotur, einn aukastafur. *Að lifa af* er: upphafsleikmaður lotunnar sem dó ekki í henni, í hvorum fasanum sem er. |
| `headshotPct` | 100 x hausskotsfellingar / fellingar, einn aukastafur; 0 án fellinga |
| `openingKills`, `openingDeaths` | opnunareinvígi unnin og töpuð |
| `tradeKills` | fellingar sem hefndu dauða liðsfélaga |
| `tradedDeaths` | dauðsföll sem var hefnt |
| `multiKills` | lotur með 2, 3, 4 og 5 fellingum á andstæðingum (`2k`, `3k`, `4k`, `5k`); fleiri en fimm telst `5k`. Báðir fasar telja. |
| `clutches`, `clutchesWon` | clutch spiluð og unnin (hér að neðan) |
| `utilityDamage` | skaði unninn með HE-handsprengjum, molotov og incendiary, einn aukastafur |
| `enemiesFlashed` | andstæðingar blindaðir í **að minnsta kosti 1,0 s** af blindum þessa leikmanns |
| `plants`, `defuses` | sprengjusetningar og aftengingar (raðir töflunnar) |
| `teamkills` | liðsfélagar felldir. Sjálfsvíg - árásarmaður og fórnarlamb sami leikmaður, eigin handsprengja til dæmis - er það ekki: það er aðeins dauðsfall. |
| `roundsPlayed` | lotur byrjaðar, eins og að ofan |

Leikmenn eru taldir upp eftir liðsheiti (í stafrófsröð), og innan liðs eftir
`diff`, síðan eftir `kills`, best fyrst.

Athugasemdir um jaðartilvik:

- Felling í after-fasa - sigurvegararnir veiða leikmann sem bjargar sér - telst
  sem felling og dauðsfall, fyrir ADR, margfaldar fellingar og KAST eins og hver önnur.
- Wallbang eru talin fyrir hvern leikmann innanhúss en ekki skrifuð í
  leikjaskjalið; hver felling í lotulistanum segir hvort hún var slík.
- *Hefnda* hluti KAST gefur fórnarlambi hefnds dauða stig í þeirri lotu.
- Teamkill og sjálfsvíg bæta dauðsfalli við fórnarlambið en engri fellingu við neinn;
  teamkill bætist við `teamkills` banamannsins, sjálfsvíg við ekkert annað.

## Clutch {#clutches}

Fyrir hverja lotu eru upphafsleikmenn beggja hliða taldir á lífi, og
live-fellingar lotunnar eru gengnar í röð. Eftir hvert dauðsfall er fórnarlambið
fjarlægt, og hver hlið skoðuð: hlið með nákvæmlega **einn** leikmann
eftir, og að minnsta kosti einn andstæðing enn á lífi, er clutch fyrir þann leikmann
**gegn** fjölda andstæðinga á lífi á því augnabliki. Hver leikmaður hefur í mesta lagi
eitt clutch í lotu; það er **unnið** þegar hlið þess leikmanns vann
lotuna.

Afleiðingar skilgreiningarinnar:

- Báðar hliðar geta haft clutch í einni lotu. Ef hlið er komin niður í einn fyrst
  (1v3, til dæmis) og hin hliðin er síðan líka komin niður í einn,
  er seinni leikmaðurinn í eigin 1v1 clutch.
- `against` er talan þegar leikmaðurinn varð sá síðasti, ekki í lokin.
- Fellingar after-fasans eru ekki gengnar, svo þær hvorki hefja clutch
  né breyta einu.

## Eftirlifendur {#survivors}

**Eftirlifendur** lotu eru, fyrir hverja hlið, upphafsleikmenn hennar að frádregnum öllum
sem dóu á meðan hún var lifandi. Leikmaður felldur í after-fasa á meðan hann bjargar sér
er enn eftirlifandi í lotulistanum - en lifði ekki af fyrir KAST.

## Lotulistinn {#the-round-list}

Hver lota leikjaskjalsins ber niðurstöðu sína, stöðu, hliðar, hagkerfi, sprengjusetningu,
eftirlifendur, clutch og fellingar sínar í röð; sjá
[Leikjaskjalið](output-match-json.md#rounds).

## Textastigataflan {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` prentar þessar tölur fyrir hvert lið;
sjá [Skipanir](commands.md#scoreboard---a-match-as-text).
