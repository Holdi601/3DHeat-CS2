---
title: "Tilastot"
nav_order: 7
lang: "fi"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Tilastot {#statistics}

Mitä kukin pelaaja teki ottelussa ja miten kukin erä meni: tulostaulu ja erälista
[ottelun asiakirjasta](output-match-json.md). Koodi:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Kaikki lasketaan ottelusta, joka rakennettiin kuten sivulla
[Ottelun rakentaminen](building-matches.md): sen tappotietueista, sen vahingosta (menetetty
terveys, vain viholliset), sen sokaisuista (vain viholliset) ja sen riveistä.

![synteettisen ottelun tekstitulostaulu](../assets/img/scoreboard.svg)

## Sopimukset {#the-conventions}

Missä peli itse ei määrittele lukua, nämä ovat määritelmät. Ne kirjoitetaan myös jokaiseen
ottelun asiakirjaan kohdassa `conventions`.

| Termi | Määritelmä |
|---|---|
| **Trade** | Kuolema on *kostettu* (traded), kun sen tappajan tappaa uhrin joukkuetoveri **5 s** sisällä; tuo tappo on *trade-tappo*. |
| **Avaus** | Erän ensimmäinen vihollisen tappo elävänä aikana. Joukkuetappo, itsemurha tai kuolema maailmalle ennen sitä ohitetaan. |
| **KAST** | Niiden erien osuus, joissa pelaaja teki **K**ill-tapon, sai **A**vustuksen (välähdysavustus lasketaan), **S**elvisi tai oli **T**raded-kuolema. |
| **Vahinko** | Menetetty terveys, vain viholliset: 137 vahingon päälaukaus 40 terveydellä olevaan pelaajaan on 40. |
| **Clutch** | Puolen viimeinen elossa oleva pelaaja, kun vihollisia on vielä pystyssä; voitettu, kun puoli voittaa erän. |
| **Osto** | Kunkin puolen mukaan, freeze timen lopun keskimääräisestä varustearvosta: kunkin säännöllisen puoliajan ensimmäinen erä on pistooli-erä (erä 1, ja puoliajan jälkeinen erä, kunhan ottelu pelasi sen); jatkoajalla ei ole pistooli-erää; sitten alle 1 500 $ eco, alle 4 000 $ force, muuten full. |

## Kuka aloitti kunkin erän {#who-started-each-round}

Useat luvut vaativat tiedon, kuka erää pelasi. Erän **aloittavat pelaajat** ovat kunkin puolen
jokainen pelaaja, jolla on elävä sijaintirivi yhden sekunnin sisällä erän varhaisimmasta
sijainnista (eli ensimmäisen sekunnin aikana freeze timen päättymisen jälkeen). Pelaajan
**pelatut erät** ovat niiden erien määrä, jotka hän aloitti. Jos pelaaja ei aloittanut yhtäkään
(hänellä ei ollut sellaista riviä), käytetään ottelun erälaskuria, jottei jaettaisi nollalla.

## Tulostaulun rivi {#the-scoreboard-line}

Yksi merkintä per pelaaja (kentän nimet: [ottelun asiakirja](output-match-json.md#pelaajat)).
"Vihollisen tappo" tarkoittaa alla tappoa, jolla on tappaja, ei joukkuetappoa eikä
itsemurhaa (uhrin oma).

| Kenttä | Laskee |
|---|---|
| `kills` | vihollisten tapot, sekä elävän että jälkeisen vaiheen |
| `deaths` | jokainen kuolema: vihollisten, joukkuetovereiden, oman käden tai maailman takia |
| `assists` | vihollisen tapot, jotka tämä pelaaja avusti ilman välähdystä (avustajan ei pidä olla tappaja) |
| `flashAssists` | vihollisen tapot, jotka tämä pelaaja avusti välähdyksellä |
| `diff` | tappoja miinus kuolemia |
| `adr` | vahinko (menetetty terveys, vain viholliset, molemmat vaiheet) / pelatut erät, yksi desimaali |
| `kast` | 100 x (erät, joissa oli tappo, avustus tai välähdysavustus, selviytyminen tai kostettu kuolema) / pelatut erät, yksi desimaali. *Selviytyminen* on: erän aloittava pelaaja, joka ei kuollut siinä, kummassakaan vaiheessa. |
| `headshotPct` | 100 x päälaukaustapot / tapot, yksi desimaali; 0, jos tappoja ei ole |
| `openingKills`, `openingDeaths` | voitetut ja hävityt avausduellit |
| `tradeKills` | tapot, jotka kostivat joukkuetoverin kuoleman |
| `tradedDeaths` | kuolemat, jotka kostettiin |
| `multiKills` | erät, joissa oli 2, 3, 4 ja 5 vihollisen tappoa (`2k`, `3k`, `4k`, `5k`); yli viisi lasketaan `5k`:ksi. Molemmat vaiheet lasketaan. |
| `clutches`, `clutchesWon` | pelatut ja voitetut clutchit (alla) |
| `utilityDamage` | HE-kranaateilla, molotovilla ja incendiaryllä tehty vahinko, yksi desimaali |
| `enemiesFlashed` | vihollisia, jotka sokaistiin **vähintään 1,0 s** tämän pelaajan välähdyksillä |
| `plants`, `defuses` | pommin asetukset ja purut (taulukon rivit) |
| `teamkills` | tapetut joukkuetoverit. Itsemurha - hyökkääjä ja uhri sama pelaaja, esimerkiksi oma kranaatti - ei ole joukkuetappo: se on vain kuolema. |
| `roundsPlayed` | aloitetut erät, kuten yllä |

Pelaajat listataan joukkueen nimen mukaan (aakkosjärjestyksessä), ja joukkueen sisällä
`diff`in mukaan, sitten `kills`in mukaan, parhain ensin.

Huomioita reunoista:

- Jälkeisen vaiheen tappo - voittajat metsästävät säästävää pelaajaa - lasketaan tappona,
  kuolemana, ADR:ssä, monitapoissa ja KAST:ssa kuten mikä tahansa muu.
- Päälaukaukset lasketaan pelaajakohtaisesti sisäisesti, mutta niitä ei kirjoiteta ottelun
  asiakirjaan; jokainen tappo erälistassa kertoo, oliko se päälaukaus.
- KAST:in *kostettu*-osa hyvittää erässä kostetun kuoleman uhrille.
- Joukkuetappot ja itsemurhat lisäävät kuoleman uhrille, mutta eivät tappoa kenellekään;
  joukkuetappo lisää tappajan `teamkills`-lukua, itsemurha ei mitään muuta.

## Clutchit {#clutches}

Jokaisessa erässä molempien puolten aloittavat pelaajat otetaan elossa oleviksi, ja erän
elävät tapot käydään läpi järjestyksessä. Kunkin kuoleman jälkeen uhri poistetaan, ja kaikki
puolet tarkastetaan: puoli, jolla on täsmälleen **yksi** pelaaja jäljellä ja vähintään yksi
vihollinen vielä pystyssä, on clutch kyseiselle pelaajalle **vastaan** niin monta vihollista,
kuin on elossa sillä hetkellä. Jokaisella pelaajalla on enintään yksi clutch per erä; se on
**voitettu**, kun pelaajan puoli voittaa erän.

Määritelmän seuraukset:

- Molemmilla puolilla voi olla clutch samassa erässä. Jos yksi puoli jää ensin yhteen (esimerkiksi
  1v3), ja toinen puoli jää sitten myös yhteen, toinen pelaaja on oman 1v1-clutchinsa.
- `against` on se luku, kun pelaaja jäi viimeiseksi, ei lopussa.
- Jälkeisen vaiheen tappoja ei käydä läpi, joten ne eivät aloita clutchia eivätkä muuta sitä.

## Selviytyjät {#survivors}

Erän **selviytyjät** ovat kunkin puolen aloittavat pelaajat miinus kaikki, jotka kuolivat sen
ollessa elävänä. Pelaaja, joka tapettiin jälkeisessä vaiheessa säästämisen aikana, on yhä
selviytyjä erälistassa - mutta ei *selvinnyt* KAST:ia varten.

## Erälista {#the-round-list}

Jokaisessa ottelun asiakirjan erässä on sen tulos, tulos, puolet, talous, asetus, selviytyjät,
clutchit ja sen tapot järjestyksessä; katso [Ottelun asiakirja](output-match-json.md#erat).

## Tekstitulostaulu {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` tulostaa nämä luvut joukkueittain; katso
[Komennot](commands.md#scoreboard-ottelu-tekstina).
