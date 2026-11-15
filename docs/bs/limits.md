---
title: Ograničenja
nav_order: 13
lang: "bs"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Ograničenja {#limits}

Šta konverter pretpostavlja, šta ne obrađuje i šta nije provjereno. Svaka
stavka je iz koda kakav jest.

## Šta čita {#what-it-reads}

- **Samo nekomprimirane `.dem` datoteke.** `.dem.zst`, `.dem.bz2`, `.rar` i
  `.zip` moraju se prvo raspakovati. Ekstenzija se poklapa bez obzira na
  veličinu slova (`.dem`, `.DEM`), u folderima kao i za datoteke zadane po imenu.
- **Defusal mečevi.** Razlozi kraja runde, postavljanje bombe i site,
  vrste kupovine i pištolj runde su oni iz bomb defusal moda. Mape s taocima,
  Wingman i drugi modovi ne obrađuju se posebno i nisu provjereni.
- **64 tika u sekundi** se pretpostavlja (`TICKRATE = 64`) za svako vrijeme
  izračunato iz tikova; CS2 serveri rade na 64.
- Pretpostavlja se **demo sa servera** (SourceTV): ima svakog igrača.
  Snimak na strani klijenta (POV demo) nije isprobavan.

## Mečevi i runde {#matches-and-rounds}

- **Datoteke se grupišu po imenu.** Dijelovi jednog meča moraju dijeliti ime
  osim sufiksa `-pN` / `_pN`; datoteke jednog meča pod nepovezanim imenima
  postaju zasebni mečevi, a datoteke istog imena u različitim folderima
  grupišu se zajedno (zatim se dijele na lance ako ne nastavljaju jedna
  drugu).
- **Živi meč počinje na zadnjem `round_announce_match_start`** u
  datoteci. Knife runda iza koje ne slijedi ta objava računa se
  kao runda.
- **Vremena kraja runde tačna su na jedan uzorak** (`--every` tikova, zadano 1/8 s),
  jer se odluka čita iz uzorkovanog stanja igre. Veoma
  veliki `--every` može propustiti kratak prozor između kraja runde i
  početka sljedeće i izostaviti rundu kao nepotpunu.
- **Neriješeno.** Neriješena runda (status pobjede 1, razlog 10) odlučuje se bez
  pobjednika: `winner` je prazan i nijedna strana je nije dobila. Nijedno neriješeno nije
  viđeno u stvarnom demou da se ovo provjeri; provjereno je na sintetičkom.
- **Prekinute runde** krajem datoteke izostavljaju se (`incomplete`), ne
  pogađaju se; runde prije prve u datotekama navode se kao `missing`.
- **Pištolj runde** slijede dužinu poluvremena koju snimak pokazuje: gdje se
  strane prvi put zamijene između dvije uzastopne regularne runde. Snimak
  koji ne pokazuje tu zamjenu (počinje poslije poluvremena, ili završava prije njega,
  ili nedostaje runda s bilo koje strane) zna samo rundu 1 kao pištolj
  rundu. Produžetak ih nema.
- **Timovi.** Tim je naziv klana viđen najviše za njegove igrače. Bez naziva klanova
  timovi su `Started T` i `Started CT`. Igrač koji promijeni
  tim usred meča zadržava jedan tim.

## Događaji {#events}

- **Čita se sve što parser nudi**, uz ove izuzetke: brzina
  igrača (parser je izvodi iz pozicija; nije u demou), glas (audio,
  `parse_voice`), i `weapon_fire` bombe (početak postavljanja, što
  `bomb_beginplant` ima). Letovi granata čuvaju se pri uzorkovanju
  igrača (`--every`) i tamo gdje se svaka granata zaustavila, ne u svakom
  tiku.
- **Redovi izvan runde** (zagrijavanje, pauza između početka meča i
  prvog freeze vremena duža od dvije minute) izostavljaju se iz tabele; događaji
  koji ne vezuju nijednog igrača svi su u `events` dokumenta meča.
- **Redovi detonacija** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nemaju
  `place`: demo imenuje mjesta za igrače, ne za granate. Bacačevo
  mjesto u tom trenutku je u `throwerPlace`.
- **Site postavljanja** dolazi iz zone bombe u kojoj je prema igri postavljač
  stajao, inače iz naziva mjesta postavljača, inače iz drugog postavljanja u istoj
  zoni u istoj datoteci. Gdje to ništa ne kaže, `site` je prazan.
- **Smrt od svijeta** (pad, bomba) nema napadača: nema kill, nema
  teamkill, nema opening; to je smrt.

## Statistike {#statistics}

- **Odigrane runde** dolaze iz toga ko je imao poziciju u prvoj sekundi poslije
  freeze vremena. Igrač koji se poveže kasnije u rundi ne računa se kao
  da ju je odigrao (njegova ubistva se i dalje računaju).
- **Preživljavanje za KAST**: igrač ubijen u fazi poslije nije preživio
  za KAST, dok ga lista rundi i dalje navodi među preživjelima.
- **Oba igrača u 1v1** mogu dobiti clutch u istoj rundi; pogledajte
  [Statistike](statistics.md#clutches).
- **Utility šteta** su HE granate, molotovi i incendiary; ubistvo ili pogodak
  bačenim flešom ili decoyem nije utility šteta.

## Izvoz mape {#map-export}

- Treba instaliranu igru (ili `.vpk`) i CLI programa Source2Viewer; ništa
  se ne preuzima.
- Izvozi samo `world_physics`; clip brushevi i nebo izostavljaju se po
  tome što njihova imena sadrže `clip` ili `sky`, bez obzira na veličinu slova.
- Tlo se od strukture razlikuje samo po normali stranice (Z komponenta 0,7 ili
  više), pa je strma rampa struktura a ravan krov je tlo.
- Datoteka je u inčima, ne u metrima.

## Memorija i vrijeme {#memory-and-time}

- Meč se drži u memoriji cijeli dok se gradi, u jednom radniku po
  meču. S mnogo radnika i malim `--every` memorija se zbraja: smanjite
  `--jobs` ako računaru ponestane.
- Meč se piše tek kad je izgrađen: prvo `.parquet`, zatim
  `.match.json`. Pokretanje prekinuto između ostavlja tabelu bez njenog dokumenta meča;
  meč se računa kao napisan samo s oboje, pa ga sljedeće pokretanje pretvara
  ponovo. Mečevi koji još nisu počeli jednostavno se preuzimaju pri sljedećem pokretanju.
