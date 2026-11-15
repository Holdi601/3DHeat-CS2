---
title: "Ograničenja"
nav_order: 13
lang: "hr"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Ograničenja {#limits}

Što pretvarač pretpostavlja, što ne obrađuje i što nije provjereno. Svaka točka je iz koda kakav jest.

## Što čita {#what-it-reads}

- **Samo nekomprimirane `.dem` datoteke.** `.dem.zst`, `.dem.bz2`, `.rar` i `.zip` moraju se prvo raspakirati. Nastavak se prepoznaje bez obzira na veličinu slova (`.dem`, `.DEM`), u mapama kao i za datoteke navedene imenom.
- **Mečevi bomba-deaktivacije.** Razlozi završetka runde, postavljanje bombe i mjesto, vrste kupovine i runde s pištoljima su oni bomba-deaktivacije. Mape s taocima, Wingman i drugi modovi nisu posebno obrađeni i nisu provjereni.
- **64 tika u sekundi** se pretpostavlja (`TICKRATE = 64`) za svako vrijeme izračunato iz tikova; CS2 poslužitelji rade na 64.
- **Demo snimka s poslužitelja** (SourceTV) se pretpostavlja: ima svakog igrača. Snimka na strani klijenta (POV demo) nije isprobana.

## Mečevi i runde {#matches-and-rounds}

- **Datoteke se grupiraju po imenu.** Dijelovi jednog meča moraju imati isto ime osim sufiksa `-pN` / `_pN`; datoteke jednog meča pod nepovezanim imenima postaju zasebni mečevi, a datoteke istog imena u različitim mapama grupiraju se zajedno (zatim se dijele u lance ako ne nastavljaju jedna drugu).
- **Živi meč počinje na zadnjem `round_announce_match_start`** u datoteci. Runda s nožem koja nije praćena tom najavom broji se kao runda.
- **Vremena završetka rundi točna su do jednog uzorka** (`--every` tikova, zadano 1/8 s), jer se odluka čita iz uzorkovanog stanja igre. Vrlo velik `--every` može promašiti kratak prozor između kraja jedne runde i početka sljedeće i ostaviti rundu van kao nepotpunu.
- **Neriješene runde.** Neriješena runda (win status 1, razlog 10) odlučena je bez pobjednika: `winner` je prazan i nijedna strana je nije pobijedila. Nijedna neriješena runda nije se susrela u stvarnoj demo snimci za provjeru; provjerava se na sintetičkoj.
- **Runde prekinute** krajem datoteke se izostavljaju (`incomplete`), ne pogađaju se; runde prije prve u datotekama navedene su kao `missing`.
- **Runde s pištoljima** slijede duljinu poluvremena koju snimka pokazuje: gdje se strane prvi put zamijene između dvije uzastopne regularne runde. Snimka koja ne pokazuje tu zamjenu (počinje nakon poluvremena, ili završava prije njega, ili nedostaje runda s jedne ili druge strane od njega) zna samo za rundu 1 kao rundu s pištoljima. Produženje nema nijednu.
- **Timovi.** Tim je naziv kluba koji je najčešće viđen za njegove igrače. Bez naziva klubova timovi su `Started T` i `Started CT`. Igrač koji promijeni tim usred meča zadržava jedan tim.

## Događaji {#events}

- **Čita se sve što parser nudi**, uz ove iznimke: brzina igrača (parser je izvodi iz položaja; nije u demo snimci), glas (zvuk, `parse_voice`) i `weapon_fire` bombe (početak postavljanja, koji ima `bomb_beginplant`). Letovi granata čuvaju se u uzorkovanju igrača (`--every`) i na mjestu gdje je svaka granata stala, a ne u svakom tiku.
- **Redci izvan runde** (zagrijavanje, pauza između početka meča i prvog freeze timea duže od dvije minute) izostavljaju se iz tablice; svi događaji koji se ne tiču nijednog igrača nalaze se u `events` dokumenta meča.
- **Redci detonacije** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nemaju `place`: demo imenuje mjesta za igrače, a ne za granate. Mjesto bacača u tom trenutku nalazi se u `throwerPlace`.
- **Mjesto postavljanja** dolazi iz zone bombe u kojoj igra kaže da je postavljač stajao, inače iz naziva mjesta postavljača, inače iz drugog postavljanja na istoj zoni u istoj datoteci. Gdje nijedno od toga ništa ne kaže, `site` je prazan.
- **Smrt od svijeta** (pad, bomba) nema napadača: nema ubojstva, nema teamkilla, nema prvog ubojstva; to je smrt.

## Statistika {#statistics}

- **Odigrane runde** dolaze iz toga tko je imao položaj u prvoj sekundi nakon freeze timea. Igrač koji se spoji kasnije u rundi ne računa se kao da ju je odigrao (njegova ubojstva se i dalje računaju).
- **Preživljavanje za KAST**: igrač ubijen u fazi nakon nije preživio za KAST, iako ga popis rundi i dalje navodi među preživjelima.
- **Oba igrača u 1v1** mogu dobiti clutch u istoj rundi; vidi [Statistika](statistics.md#clutches).
- **Šteta pomoćnim sredstvima** su HE granate, molotovi i zapaljive; ubojstvo ili pogodak bačenim bljeskalicom ili decoyem nije šteta pomoćnim sredstvima.

## Izvoz karte {#map-export}

- Treba instalirana igra (ili `.vpk`) i Source2Viewerov CLI; ništa se ne preuzima.
- Izvozi se samo `world_physics`; clip elementi i nebo se izostavljaju po tome što im ime sadrži `clip` ili `sky`, bez obzira na veličinu slova.
- Tlo se od strukture razlikuje samo po normali plohe (Z komponenta 0,7 ili više), pa je strma rampa struktura, a ravan krov tlo.
- Datoteka je u inčima, a ne u metrima.

## Memorija i vrijeme {#memory-and-time}

- Meč se drži u memoriji cijel dok se gradi, u jednom radniku po meču. Uz mnogo radnika i mali `--every` memorija se zbraja: smanjite `--jobs` ako se stroju ponestaje memorije.
- Meč se piše tek kad je izgrađen: prvo `.parquet`, zatim `.match.json`. Pokretanje zaustavljeno između ostavlja tablicu bez dokumenta meča; meč se smatra zapisanim samo s oba, pa se sljedeći put ponovno pretvara. Mečevi koji još nisu započeti jednostavno pokupi sljedeće pokretanje.
