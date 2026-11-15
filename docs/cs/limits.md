---
title: Omezení
nav_order: 13
lang: "cs"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Omezení {#limits}

Co převodník předpokládá, co neřeší a co není ověřeno. Každý bod pochází z kódu
v jeho dnešní podobě.

## Co se čte {#what-it-reads}

- **Jen nekomprimované soubory `.dem`.** `.dem.zst`, `.dem.bz2`, `.rar` a
  `.zip` je nutné nejdřív rozbalit. Přípona se shoduje v jakémkoli psaní
  (`.dem`, `.DEM`), ve složkách i u souborů zadaných jménem.
- **Zápasy defusal.** Důvody konce kola, položení bomby a zóna, typy nákupu a
  pistolová kola jsou ty z režimu defusal. Mapy s rukojmími, Wingman a další
  režimy nejsou řešeny zvlášť a nejsou ověřeny.
- **64 taktů za sekundu** se předpokládá (`TICKRATE = 64`) pro každý čas
  počítaný z taktů; servery CS2 běží na 64.
- **Dema ze serveru** (SourceTV) se předpokládají: obsahují všechny hráče.
  Záznam u klienta (POV demo) nebyl zkoušen.

## Zápasy a kola {#matches-and-rounds}

- **Soubory se seskupují podle názvu.** Části jednoho zápasu musí mít stejný
  název kromě přípony `-pN` / `_pN`; soubory jednoho zápasu pod nesouvisejícími
  názvy se stanou samostatnými zápasy a soubory se stejným názvem v různých
  složkách se seskupí dohromady (a pak se rozdělí na řetězy, pokud nenavazují
  jeden na druhý).
- **Živý zápas začíná u posledního `round_announce_match_start`** v souboru.
  Kolo nožů, za kterým toto oznámení nenásleduje, se počítá jako kolo.
- **Konce kol jsou přesné na jeden vzorek** (takty `--every`, default 1/8 s),
  protože rozhodnutí se čte z vzorkovaného herního stavu. Velmi velké `--every`
  může přehlédnout krátké okno mezi koncem kola a začátkem dalšího a kolo pak
  vynechat jako neúplné.
- **Remízy.** Kolo v remíze (stav výhry 1, důvod 10) je rozhodnuto bez
  vítěze: `winner` je prázdné a nevyhrála ho žádná strana. Žádná remíza nebyla
  v reálném demu k ověření; je ověřena na syntetickém.
- **Kola přerušená** koncem souboru se vynechají (`incomplete`), nehádají se;
  kola před prvními v souborech jsou uvedena jako `missing`.
- **Pistolová kola** se řídí délkou poločasu, kterou záznam ukazuje: tam, kde
  se strany poprvé prohodí mezi dvěma po sobě jdoucími řádnými koly. Záznam,
  který tu výměnu neukazuje (začíná až po poločase, nebo končí před ním, nebo
  chybí kolo na některé straně), zná jako pistolové kolo jen kolo 1.
  Prodloužení žádné pistolové kolo nemá.
- **Týmy.** Tým je název klanu, který se u jeho hráčů viděl nejčastěji. Bez
  názvů klanů jsou týmy `Started T` a `Started CT`. Hráč, který během zápasu
  změní tým, si zachová jeden tým.

## Události {#events}

- **Čte se všechno, co parser nabízí**, s těmito výjimkami: rychlost hráčů
  (parser ji odvozuje z pozic; v demu není), hlas (zvuk, `parse_voice`) a
  `weapon_fire` bomby (začátek položení, které má `bomb_beginplant`). Dráhy
  granátů se uchovají ve vzorkování hráčů (`--every`) a tam, kde se granát
  zastavil, ne v každém taktu.
- **Řádky mimo kolo** (rozcvička, pauza mezi začátkem zápasu a prvním zmrazením
  delší než dvě minuty) se vynechají z tabulky; události, které se netýkají
  žádného hráče, jsou všechny v `events` dokumentu zápasu.
- **Řádky detonací** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nemají
  `place`: dema pojmenovávají místa pro hráče, ne pro granáty. Místo hodícího
  v ten okamžik je v `throwerPlace`.
- **Zóna položení** pochází z bombové zóny, kterou hra uvádí pro plantéra, jinak
  z názvu místa plantéra, jinak z jiného položení ve stejné zóně ve stejném
  souboru. Kde žádné z toho nic neříká, je `site` prázdné.
- **Smrt způsobená světu** (pád, bomba) nemá útočníka: žádné zabití, žádné
  týmové zabití, žádné otevření; je to smrt.

## Statistiky {#statistics}

- **Odehrané kolo** se počítá podle toho, kdo měl pozici v první sekundě po
  zmrazení. Hráč, který se připojí později v kole, se za něj nepočítá (jeho
  zabití se počítají).
- **Přežití pro KAST**: hráč zabitý ve fázi po nebyl pro KAST přeživší, i když
  ho seznam kol mezi přeživšími pořád uvádí.
- **Oba hráči v 1v1** mohou dostat clutch v jednom kole; viz
  [Statistiky](statistics.md#clutches).
- **Poškození utilitou** jsou granáty HE, molotovy a zápalné granáty; zabití
  nebo zásah hozeným zábleskem nebo návnadou poškozením utilitou není.

## Export mapy {#map-export}

- Potřebuje nainstalovanou hru (nebo `.vpk`) a Source2Viewer CLI; nic se
  nestahuje.
- Exportuje jen `world_physics`; clipy a obloha se vynechají podle toho, že
  jejich názvy obsahují `clip` nebo `sky`, bez ohledu na velikost písmen.
- Zem se od konstrukce rozlišuje jen podle normály plochy (složka Z 0,7 nebo
  více), takže strmá rampa je konstrukce a plochá střecha je zem.
- Soubor je v palcích, ne v metrech.

## Paměť a čas {#memory-and-time}

- Zápas se drží v paměti celý, zatímco se sestavuje, v jednom pracovním
  procesu na zápas. Při mnoha procesech a malém `--every` paměť přibývá: u
  slabšího počítače snižte `--jobs`.
- Zápas se zapíše až po sestavení: nejdřív `.parquet`, pak `.match.json`. Běh
  zastavený mezi tím nechá tabulku bez dokumentu zápasu; zápas se počítá jako
  zapsaný jen s oběma, takže se příště převede znovu. Zápasy, které ještě
  nezačaly, si příští běh prostě vezme.
