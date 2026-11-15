---
title: "Rajoitukset"
nav_order: 13
lang: "fi"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Rajoitukset {#limits}

Mitä muunnin olettaa, mitä se ei käsittele ja mitä ei ole todennettu. Jokainen kohta
on koodista sellaisena kuin se nyt on.

## Mitä se lukee {#what-it-reads}

- **Vain pakkaamattomat `.dem`-tiedostot.** `.dem.zst`, `.dem.bz2`, `.rar` ja `.zip`
  pitää purkaa ensin. Pääte tunnistetaan kirjainkoosta riippumatta (`.dem`, `.DEM`),
  kansioissa kuten nimen mukaan annetuissa tiedostoissa.
- **Pommipelin ottelut.** Erän lopun syyt, pommin asetus ja paikka, ostotyypit ja
  pistooli-erät ovat pommipelin mukaisia. Panttivankikartat, Wingman ja muut moodit
  eivät ole erikoiskäsittelyssä eivätkä ole todennettuja.
- **64 tikkiä sekunnissa** oletetaan (`TICKRATE = 64`) kaikille tikeistä lasketuille
  ajoille; CS2-palvelimet kulkevat 64:llä.
- **Palvelimen demo** (SourceTV) oletetaan: siinä on jokainen pelaaja. Asiakaspuolen
  nauhoitusta (POV-demo) ei ole kokeiltu.

## Ottelut ja erät {#matches-and-rounds}

- **Tiedostot ryhmitellään nimen mukaan.** Saman ottelun osien pitää jakaa nimi
  `-pN`- / `_pN`-päätettä lukuun ottamatta; eri nimillä olevat saman ottelun tiedostot
  muodostavat erilliset ottelut, ja saman nimen omaavat tiedostot eri kansioissa
  ryhmitellään yhteen (ja jaetaan sitten ketjuiksi, jos ne eivät jatka toisiaan).
- **Elävä ottelu alkaa tiedoston viimeisestä `round_announce_match_start`-tapahtumasta.**
  Veitsierää, jota ei seuraa tuo ilmoitus, lasketaan eräksi.
- **Erän loppuajat ovat tarkkoja yhden näytteen tarkkuudella** (`--every`-tikit, oletuksena
  1/8 s), koska ratkaisu luetaan näytteistetystä pelin tilasta. Hyvin suuri `--every`
  voi ohittaa lyhyen ikkunan erän päättymisen ja seuraavan erän alkamisen välillä ja
  jättää erän pois keskeneräisenä.
- **Tasapelit.** Tasapelin erä (voittotila 1, syy 10) ratkeaa ilman voittajaa: `winner`
  on tyhjä eikä kumpikaan puoli voittanut sitä. Oikeassa demossa ei ole tavattu tasapeliä,
  jota vastaan tätä voisi verrata; se on tarkistettu synteettisellä demolla.
- **Erät, jotka katkaistaan tiedoston lopussa**, jätetään pois (`incomplete`), niitä ei
  arvata; ennen ensimmäistä erää tiedostoissa olevat erät luetellaan kohdassa `missing`.
- **Pistooli-erät** seuraavat puoliajan pituutta, jonka nauhoitus näyttää: kohta, jossa
  puolet vaihtuvat kahden peräkkäisen säännöllisen erän välillä. Nauhoitus, joka ei näytä
  tuota vaihtoa (se alkaa puoliajan jälkeen tai päättyy ennen sitä, tai jokin erä sen
  kummallakin puolella puuttuu), tuntee vain erän 1 pistooli-eränä. Jatkoajalla ei ole
  pistooli-eriä.
- **Joukkueet.** Joukkue on klaanin nimi, jota sen pelaajilla nähtiin useimmin. Ilman
  klaanin nimiä joukkueet ovat `Started T` ja `Started CT`. Pelaaja, joka vaihtaa
  joukkuetta kesken ottelun, säilyttää yhden joukkueen.

## Tapahtumat {#events}

- **Kaikki, minkä jäsentäjä tarjoaa, luetaan**, näillä poikkeuksilla: pelaajien nopeus
  (jäsentäjä johtaa sen sijainneista; sitä ei ole demossa), ääni (`parse_voice`), ja
  pommin `weapon_fire` (pommin asetuksen alku, jonka `bomb_beginplant` jo antaa).
  Kranaattien lennot säilytetään pelaajien näytteistyksellä (`--every`) ja siellä, missä
  kukin kranaatti pysähtyi, ei joka tikillä.
- **Rivit erän ulkopuolella** (warmup, tauko ottelun alun ja ensimmäisen freeze timen
  välillä, yli kaksi minuuttia) jätetään pois taulukosta; tapahtumat, jotka eivät koske
  yhtään pelaajaa, ovat kaikki ottelun asiakirjan `events`-kohdassa.
- **Räjähdysrivien** (`smoke`, `flash`, `he`, `molotov`, `decoy`) `place` on tyhjä: demo
  nimeää paikat pelaajille, ei kranaateille. Heittäjän paikka sillä hetkellä on
  `throwerPlace`-kohdassa.
- **Asetuksen alue** tulee pommialueesta, jonka peli kertoo asettajan seisoneen, muuten
  asettajan paikan nimestä, muuten toisesta saman tiedoston asetuksesta samalla
  alueella. Jos mikään näistä ei kerro, `site` on tyhjä.
- **Kuolema maailmalle** (putoaminen, pommi) ei ole tappajaa: ei tappoa, ei joukkuetappoa,
  ei avausta; se on kuolema.

## Tilastot {#statistics}

- **Pelatut erät** tulevat siitä, kuka oli sijainnissa ensimmäisen sekunnin aikana
  freeze timen jälkeen. Pelaaja, joka liittyy erän aikana myöhemmin, ei lasketa pelanneeksi
  sitä (hänen tapponsa lasketaan silti).
- **KAST:n selviytyminen**: pelaaja, joka tapettiin jälkeisessä vaiheessa, ei selvinnyt
  KAST:ia varten, vaikka erän lista nimeää hänet yhä selviytyjien joukossa.
- **Molemmat pelaajat 1v1-tilanteessa** voivat saada clutchin samassa erässä; katso
  [Tilastot](statistics.md#clutchit).
- **Apuvahinko** on HE-kranaatit, molotovit ja incendiaryt; tappo tai osuma heitetyllä
  välähdyksellä tai decoylla ei ole apuvahinkoa.

## Kartan vienti {#map-export}

- Tarvitsee pelin asennettuna (tai `.vpk`-tiedoston) ja Source2Viewerin CLI:n; mitään
  ei ladata.
- Vie vain `world_physics`-mallin; leikebrushit ja taivas jätetään pois nimien
  perusteella, joissa on `clip` tai `sky`, kirjainkoosta riippumatta.
- Maa erotetaan rakenteesta pelkällä pinnan normaalilla (Z-komponentti 0,7 tai enemmän),
  joten jyrkkä rinne on rakennetta ja tasainen katto on maata.
- Tiedosto on tuumissa, ei metreissä.

## Muisti ja aika {#memory-and-time}

- Ottelu pidetään muistissa kokonaisena, kun se rakennetaan, yhdessä työprosessissa per
  ottelu. Kun työprosesseja on paljon ja `--every` on pieni, muisti kasvaa: pienennä
  `--jobs`-arvoa, jos kone loppuu kesken.
- Ottelu kirjoitetaan vasta, kun se on rakennettu: ensin `.parquet`, sitten
  `.match.json`. Ajo, joka pysähtyy siinä välissä, jättää taulukon ilman ottelun
  asiakirjaa; ottelu lasketaan kirjoitetuksi vain, kun molemmat ovat olemassa, joten
  seuraava ajo muuntaa sen uudelleen. Vielä aloittamatta olevat ottelut otetaan vain
  seuraavassa ajossa.
