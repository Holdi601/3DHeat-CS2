---
title: "Kufizimet"
nav_order: 13
lang: "sq"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Kufizimet {#limits}

Çfarë supozon konverteri, çfarë nuk trajton, dhe çfarë nuk është
verifikuar. Çdo pikë është nga kodi siç është tani.

## Çfarë lexon {#what-it-reads}

- **Vetëm skedarë `.dem` të pangjeshur.** `.dem.zst`, `.dem.bz2`, `.rar` dhe
  `.zip` duhen shpaketuar më parë. Shtesa krahasohet pa dallim shkronjash
  (`.dem`, `.DEM`), në dosje si dhe për skedarët e dhënë me emër.
- **Ndeshje çaktivizimi bombe (defusal).** Arsyet e fundit të raundit, vendosja e bombës dhe site,
  llojet e blerjes dhe raundet e pistoletave janë ato të çaktivizimit të bombës. Hartat me
  peng, Wingman dhe mënyra të tjera nuk trajtohen posaçërisht dhe nuk janë verifikuar.
- **64 tick-e në sekondë** supozohen (`TICKRATE = 64`) për çdo kohë
  të llogaritur nga tick-et; serverat e CS2 xhirojnë me 64.
- **Një demo nga serveri** (SourceTV) supozohet: ka çdo lojtar.
  Një regjistrim nga ana e klientit (demo POV) nuk u provua.

## Ndeshjet dhe raundet {#matches-and-rounds}

- **Skedarët grupohen sipas emrit.** Pjesët e një ndeshjeje duhet të ndajnë një emër
  përveç prapashtesës `-pN` / `_pN`; skedarët e një ndeshjeje me emra të palidhur
  bëhen ndeshje të veçanta, dhe skedarët me të njëjtin emër në dosje të ndryshme
  grupohen bashkë (pastaj ndahen në zinxhirë nëse nuk vazhdojnë njëri
  tjetrin).
- **Ndeshja live nis te `round_announce_match_start` i fundit** në një
  skedar. Një raund me thika që nuk ndiqet nga ai njoftim numërohet
  si raund.
- **Kohët e fundit të raundit janë të sakta deri në një mostër** (`--every` tick-e, 1/8 s si
  parazgjedhje), sepse vendimi lexohet nga gjendja e marrë si mostër e lojës. Një `--every`
  shumë i madh mund ta humbasë një dritare të shkurtër midis fundit të një raundi dhe
  nisjes së raundit tjetër dhe ta lërë raundin jashtë si të paplotë.
- **Barazimet.** Një raund i barabartë (statusi i fitores 1, arsyeja 10) vendoset pa
  fitues: `winner` është bosh dhe asnjë anë nuk e fitoi. Asnjë barazim nuk u has
  në një demo të vërtetë për ta kontrolluar; kontrollohet në atë sintetike.
- **Raundet e prera** nga fundi i një skedari lihen jashtë (`incomplete`), nuk hamendësohen;
  raundet para të parit në skedarë listohen si `missing`.
- **Raundet e pistoletave** ndjekin gjatësinë e pjesës që tregon regjistrimi: ku
  anët ndërrohen për herë të parë midis dy raundeve rregullore njëri pas tjetrit. Një regjistrim
  që nuk e tregon atë ndërrim (nis pas pushimit të ndërmjetëm, ose mbaron para tij,
  ose mungon një raund nga të dyja anët e tij) njeh vetëm raundin 1 si raund pistoletash.
  Koha shtesë nuk ka.
- **Ekipet.** Një ekip është emri i klanit i parë më shumë për lojtarët e tij. Pa emra
  klanesh ekipet janë `Started T` dhe `Started CT`. Një lojtar që ndërron
  ekip në mes të ndeshjes mban një ekip.

## Ngjarjet {#events}

- **Çdo gjë që ofron parseri lexohet**, me këto përjashtime: shpejtësia e
  lojtarëve (parseri e nxjerr nga pozicionet; nuk është në
  demo), zëri (audio, `parse_voice`), dhe `weapon_fire` i bombës (nisja
  e një vendosjeje, që e ka `bomb_beginplant`). Fluturimet e granatave mbahen me
  mostrimin e lojtarëve (`--every`) dhe ku ndaloi çdo granatë, jo çdo
  tick.
- **Rreshtat jashtë një raundi** (ngrohja, një pauzë midis nisjes së ndeshjes dhe
  kohës së parë të ngrirjes mbi dy minuta) lihen jashtë tabelës; ngjarjet
  pa asnjë lojtar janë të gjitha te `events` i dokumentit të ndeshjes.
- **Rreshtat e shpërthimit** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nuk kanë
  `place`: demoja emërton vende për lojtarët, jo për granatat. Vendi i
  hedhësit në atë moment është te `throwerPlace`.
- **Site e vendosjes** vjen nga zona e bombës ku loja thotë se qëndronte vendosësi,
  përndryshe nga emri i vendit të vendosësit, përndryshe nga një vendosje tjetër në të njëjtën
  zonë në të njëjtin skedar. Kur asnjëra nuk e tregon, `site` është bosh.
- **Një vdekje nga bota** (një rënie, bomba) nuk ka sulmues: nuk është vrasje, as
  teamkill, as hapje; është një vdekje.

## Statistikat {#statistics}

- **Raundet e luajtura** vijnë nga kush kishte një pozicion në sekondën e parë pas
  kohës së ngrirjes. Një lojtar që lidhet më vonë në një raund nuk llogaritet
  se e ka luajtur (vrasjet e tij prapë llogariten).
- **Mbijetesa për KAST**: një lojtar i vrarë në fazën after nuk mbijetoi
  për KAST, ndërsa lista e raundeve prapë e emërton mes mbijetuesve.
- **Të dy lojtarët e një 1v1** mund të kredtohen me një clutch në një raund; shih
  [Statistikat](statistics.md#clutches).
- **Dëmi utility** është granatat HE, molotovët dhe incendiary; një vrasje ose goditje
  nga një flash ose decoy i hedhur nuk është dëm utility.

## Eksporti i hartës {#map-export}

- Kërkon lojën të instaluar (ose `.vpk`) dhe CLI të Source2Viewer; asgjë
  nuk shkarkohet.
- Eksporton vetëm `world_physics`; clip brush-et dhe qielli lihen jashtë sipas
  emrave që përmbajnë `clip` ose `sky`, në çdo shkrim.
- Toka dallohet nga struktura vetëm nga normalja e faqes (përbërësja Z 0.7 ose
  më shumë), kështu që një rampë e pjerrët është strukturë dhe një çati e sheshtë është tokë.
- Skedari është në inçe, jo në metra.

## Kujtesa dhe koha {#memory-and-time}

- Një ndeshje mbahet e tëra në kujtesë ndërsa ndërtohet, në një punëtor për
  ndeshje. Me shumë punëtorë dhe një `--every` të vogël, kujtesa mblidhet:
  ule `--jobs` nëse një makinë mbetet pa kujtesë.
- Një ndeshje shkruhet vetëm kur ndërtohet: së pari `.parquet`, pastaj
  `.match.json`. Një ekzekutim i ndalur në mes lë një tabelë pa dokumentin e saj të ndeshjes;
  një ndeshje llogaritet e shkruar vetëm me të dyja, kështu që ekzekutimi tjetër e konverton
  përsëri. Ndeshjet që nuk kanë nisur ende merren thjesht nga ekzekutimi tjetër.
