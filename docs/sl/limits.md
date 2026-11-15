---
title: "Omejitve"
nav_order: 13
lang: "sl"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Omejitve {#limits}

Kaj pretvornik predpostavlja, česa ne obravnava in kaj ni preverjeno. Vsaka točka je iz kode, kakršna je zdaj.

## Kaj bere {#what-it-reads}

- **Samo nestisnjene datoteke `.dem`.** `.dem.zst`, `.dem.bz2`, `.rar` in `.zip` je treba najprej razpakirati. Končnica
  se ujema ne glede na velikost črk (`.dem`, `.DEM`), v mapah kot pri datotekah, podanih z imenom.
- **Tekme defuse.** Vzroki konca runde, postavitev bombe in mesto, vrste nakupa in pištolske runde so tisti za
  deaktivacijo bombe. Talci na kartah, Wingman in drugi načini niso posebej obravnavani in niso preverjeni.
- **64 taktov na sekundo** je predpostavljenih (`TICKRATE = 64`) za vsak čas, izračunan iz taktov; strežniki CS2 tečejo s 64.
- **Demo s strežnika** (SourceTV) je predpostavljen: ima vse igralce. Posnetek na strani odjemalca (POV demo) ni bil
  preizkušen.

## Tekme in runde {#matches-and-rounds}

- **Datoteke se združujejo po imenu.** Deli ene tekme morajo imeti isto ime brez pripone `-pN` / `_pN`; datoteke ene
  tekme pod nepovezanimi imeni postanejo ločene tekme, datoteke z istim imenom v različnih mapah pa se združijo (nato
  se razdelijo na verige, če ne nadaljujejo ena druge).
- **Živa tekma se začne pri zadnjem `round_announce_match_start`** v datoteki. Nož-runda, ki ji ta napoved ne sledi, se
  šteje kot runda.
- **Časi koncev rund so natančni do enega vzorca** (`--every` taktov, privzeto 1/8 s), ker je odločitev prebrana iz
  vzorčenega stanja igre. Zelo velik `--every` lahko zgreši kratko okno med koncem runde in začetkom naslednje ter
  izpusti rundo kot nedokončano.
- **Remiji.** Runda z remijem (stanje zmage 1, vzrok 10) je odločena brez zmagovalca: `winner` je prazen in nobena stran
  je ni dobila. V pravem demu ni bil srečan noben remi, za primerjavo; preverjen je na sintetičnem.
- **Runde, prekinjene** s koncem datoteke, so izpuščene (`incomplete`), ne ugibajo se; runde pred prvo v datotekah so
  navedene kot `missing`.
- **Pištolske runde** sledijo dolžini polčasa, ki jo kaže posnetek: kjer se strani prvič zamenjata med dvema
  zaporednima rednima rundama. Posnetek, ki te zamenjave ne kaže (začne se po polčasu, konča se pred njim, ali manjka
  runda na eni od strani), pozna samo rundo 1 kot pištolsko. Podaljšek nima pištolske runde.
- **Ekipe.** Ekipa je klanski naziv, ki se največkrat pojavi pri njenih igralcih. Brez klanskih nazivov so ekipe
  `Started T` in `Started CT`. Igralec, ki med tekmo zamenja ekipo, ostane pri eni ekipi.

## Dogodki {#events}

- **Vse, kar razčlenjevalnik ponuja, se prebere**, z naslednjimi izjemami: hitrost igralcev (razčlenjevalnik jo izpelje iz
  položajev; ni v demu), glas (zvok, `parse_voice`) in `weapon_fire` bombe (začetek postavitve, ki jo ima
  `bomb_beginplant`). Lete granat se ohranijo po vzorčenju igralcev (`--every`) in tam, kjer je granata obstala, ne na
  vsakem taktu.
- **Vrstice zunaj runde** (ogrevanje, premor med začetkom tekme in prvo zamrznitvijo, daljši od dveh minut) se izpustijo
  iz tabele; dogodki, ki se ne tičejo nobenega igralca, so vsi v `events` dokumenta tekme.
- **Vrstice detonacij** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nimajo `place`: demo navaja kraje za igralce, ne za
  granate. Kraj metalca v tistem trenutku je v `throwerPlace`.
- **Mesto postavitve** prihaja iz bombnega območja, za katerega igra pove, da je v njem stal postavljalec; sicer iz imena
  kraja postavljalca; sicer iz druge postavitve na istem območju v isti datoteki. Če nič od tega ne pove, je `site` prazen.
- **Smrt zaradi sveta** (padec, bomba) nima napadalca: ni ubijanja, ni prijateljskega ubijanja, ni prvega ubijanja; je smrt.

## Statistika {#statistics}

- **Odigrane runde** izhajajo iz tega, kdo je imel položaj v prvi sekundi po zamrznitvi. Igralec, ki se pridruži pozneje v
  rundi, se ne šteje kot da jo je igral (njegovi uboji se še vedno štejejo).
- **Preživetje za KAST**: igralec, ubit v fazi po koncu, ni preživel za KAST, čeprav ga seznam rund še vedno navaja med
  preživelimi.
- **Oba igralca 1v1** lahko dobita clutch v isti rundi; glejte [Statistika](statistics.md#clutches).
- **Škoda od pripomočkov** so HE granate, molotovke in zažigalne bombe; ubijanje ali zadetek z vrženo bliskovko ali vabo
  nista škoda od pripomočkov.

## Izvoz karte {#map-export}

- Potrebuje nameščeno igro (ali `.vpk`) in ukazno vrstico Source2Viewer; ničesar se ne prenese.
- Izvozi samo `world_physics`; clipi in nebo se izpustijo po imenih, ki vsebujejo `clip` ali `sky`, ne glede na velikost črk.
- Tla se od konstrukcije ločijo samo po normali ploskve (komponenta Z 0,7 ali več), zato je strma rampa konstrukcija in
  ravna streha tla.
- Datoteka je v palcih, ne v metrih.

## Pomnilnik in čas {#memory-and-time}

- Tekma je med gradnjo v pomnilniku v celoti, v enem delovnem procesu za tekmo. Pri mnogih delavcih in majhnem `--every`
  se pomnilnik seštevajo: zmanjšajte `--jobs`, če stroju zmanjkuje.
- Tekma se zapiše šele, ko je zgrajena: najprej `.parquet`, nato `.match.json`. Zagon, ustavljen vmes, pusti tabelo brez
  dokumenta tekme; tekma se šteje kot zapisana samo z obema, zato jo naslednji zagon pretvori znova. Tekme, ki še niso
  začete, pobere naslednji zagon.
