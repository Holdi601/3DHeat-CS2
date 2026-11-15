---
title: "Korlátok"
nav_order: 13
lang: "hu"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Korlátok {#limits}

Mit feltételez a konvertáló, mit nem kezel, és mi nincs ellenőrizve. Minden pont a kódból van, ahogy most áll.

## Mit olvas {#what-it-reads}

- **Csak tömörítetlen `.dem` fájlokat.** A `.dem.zst`, `.dem.bz2`, `.rar` és `.zip` fájlokat előbb ki kell csomagolni.
  A kiterjesztést bármilyen nagybetűvel felismerjük (`.dem`, `.DEM`), mappákban éppúgy, mint a névvel megadott fájloknál.
- **Bombadefuzálós meccsek.** A körvégi okok, a bomba lerakása és helye, a vásárlástípusok és a pisztolykörök a
  bombadefuzálós módé. A túsz-pályák, a Wingman és más módok nincsenek külön kezelve, és nincsenek ellenőrizve.
- **64 tick másodpercenként** feltételezett (`TICKRATE = 64`) minden tickből számolt időhöz; a CS2 szerverek 64-en futnak.
- **Szerveroldali demó** (SourceTV) feltételezett: ebben minden játékos benne van. Kliensoldali felvétel (POV-demó) nem
  lett kipróbálva.

## Meccsek és körök {#matches-and-rounds}

- **A fájlok név szerint csoportosulnak.** Egy meccs részeinek nevének a `-pN` / `_pN` utótagtól eltekintve egyeznie kell;
  a különböző nevű, de egy meccshez tartozó fájlok külön meccsekké válnak, az azonos nevű, különböző mappákban lévő
  fájlok pedig együtt csoportosulnak (majd láncokra bomlanak, ha nem folytatják egymást).
- **Az élő meccs a fájl utolsó `round_announce_match_start` eseményénél kezdődik.** Az a kés-kör, amelyet nem követ ez a
  bejelentés, körként számít.
- **A körök vége egy mintavételig pontos** (`--every` tick, alapértelmezetten 1/8 s), mert az eldöntést a mintavételezett
  játékállapotból olvassuk. Egy nagyon nagy `--every` kihagyhat egy rövid ablakot a kör vége és a következő kezdete
  között, és a kört hiányosként hagyja ki.
- **Döntetlenek.** Egy döntetlen kör (győzelmi állapot 1, ok 10) győztes nélkül dől el: a `winner` üres, és egyik oldal sem
  nyerte. Valódi demóban nem találkoztunk döntetlennel, amelyhez hasonlítani lehetne; a szintetikus demón ellenőrizve.
- **A fájl végén megszakadt körök** kimaradnak (`incomplete`), nem találgatjuk meg őket; a fájlokban az első előtti körök
  `missing`-ként vannak felsorolva.
- **A pisztolykörök** a felvétel által mutatott félidő-hossz szerint követik a meccset: ahol az oldalak először cserélnek
  két egymást követő szabályos kör között. Egy felvétel, amely nem mutatja ezt a cserét (a félidő után indul, vagy előtte ér
  véget, vagy a csere két oldalán lévő kör hiányzik), csak az 1. kört ismeri pisztolykörként. A hosszabbításnak nincs
  pisztolykörje.
- **Csapatok.** A csapat az a klánnév, amelyet legtöbbször látunk a játékosainál. Klánnevek nélkül a csapatok `Started T`
  és `Started CT`. A meccs közben csapatot váltó játékos egy csapatnál marad.

## Események {#events}

- **A parser minden kínált adatot beolvas**, az alábbi kivételekkel: a játékosok sebessége (a parser a pozíciókból
  számolja; a demóban nincs benne), a hang (`parse_voice`), és a `weapon_fire` a bombánál (a lerakás kezdete, amelyet a
  `bomb_beginplant` ad). A gránátrepülések a játékosok mintavételezésénél (`--every`) és ott maradnak meg, ahol a gránát
  megállt, nem minden ticken.
- **A körön kívüli sorok** (bemelegítés, egy szünet a meccs kezdete és az első freeze time között, kettő percnél
  hosszabban) kimaradnak a táblázatból; a játékoshoz nem köthető események mind ott vannak a meccsdokumentum `events`
  mezőjében.
- **A gránátrobbanás-sorok** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nem kapnak `place`-t: a demó játékosoknak ad
  helyet, gránátoknak nem. A dobó helye abban a pillanatban a `throwerPlace`-ben van.
- **A lerakás bombazónája** abból jön, amelyben a játék szerint a lerakó állt; ennek hiányában a lerakó helynevéből; ha
  ez sincs, egy másik, ugyanazon a zónán ugyanabban a fájlban történt lerakásból. Ahol ezek egyike sem mond semmit, a
  `site` üres.
- **A világnak okozott halál** (esés, bomba) nem rendelkezik támadóval: nincs gyilkosság, nincs csapattárs-ölés, nincs
  nyitó; halál.

## Statisztika {#statistics}

- **A lejátszott körök** abból jönnek, hogy kinek volt pozíciója a freeze time utáni első másodpercben. Az a játékos, aki
  később csatlakozik a körben, nem számít úgy, hogy játszotta (a gyilkosságai viszont számítanak).
- **Túlélés a KAST-hoz**: az utána fázisban megölt játékos nem élte túl a KAST szempontjából, bár a körlistában továbbra is
  a túlélők között szerepel.
- **Mindkét játékos egy 1v1-ben** kaphat klucsot ugyanabban a körben; lásd [Statisztika](statistics.md#clutches).
- **A segédeszköz-sebzés** a HE-gránátok, a molotovok és az incendiary-k; a dobott villanás vagy csali által okozott
  gyilkosság vagy találat nem segédeszköz-sebzés.

## Pályaexport {#map-export}

- A játék telepítését (vagy a `.vpk`-t) és a Source2Viewer CLI-jét igényli; semmit nem tölt le.
- Csak a `world_physics`-t exportálja; a klipeket és az égboltot a nevük alapján hagyja ki, `clip` vagy `sky` szerepel-e
  bennük, bármilyen nagybetűvel.
- A talajt a szerkezettől csak a lap normálvektora különbözteti meg (Z-komponens 0,7 vagy több), így a meredek rámpa szerkezet,
  a lapos tető pedig talaj.
- A fájl hüvelykben van, nem méterben.

## Memória és idő {#memory-and-time}

- Egy meccs a felépítése közben egészben a memóriában van, munkavégzőnként egy meccs. Sok munkavégzővel és kis `--every`
  értékkel a memória összeadódik: csökkentsd a `--jobs` értékét, ha a gép kevés memóriát tud.
- Egy meccs csak felépítéskor íródik: előbb a `.parquet`, majd a `.match.json`. Ha a futás a kettő között áll le, a táblázat
  meccsdokumentum nélkül marad; egy meccs csak akkor számít megírtnak, ha mindkettő megvan, így a következő futás újra
  konvertálja. A még el nem kezdett meccseket a következő futás egyszerűen felveszi.
