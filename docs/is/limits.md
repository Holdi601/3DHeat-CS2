---
title: "Takmarkanir"
nav_order: 13
lang: "is"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Takmarkanir {#limits}

Hvað breytirinn gerir ráð fyrir, hvað hann meðhöndlar ekki, og hvað er ekki
staðfest. Hvert atriði er úr kóðanum eins og hann er nú.

## Hvað hann les {#what-it-reads}

- **Aðeins óþjappaðar `.dem`-skrár.** `.dem.zst`, `.dem.bz2`, `.rar` og
  `.zip` verður að pakka fyrst upp. Endingin er pöruð án tillits til stafagerðar
  (`.dem`, `.DEM`), í möppum eins og fyrir skrár gefnar með nafni.
- **Sprengjuleikir (defusal).** Lokaástæður lota, sprengjusetningin og site,
  kaupgerðirnar og skammbyssulloturnar eru þær úr sprengjuleik. Gíslakort,
  Wingman og aðrir leikhamir eru ekki meðhöndlaðir sérstaklega og eru ekki staðfestir.
- **64 tikk á sekúndu** er gert ráð fyrir (`TICKRATE = 64`) fyrir hvern tíma
  reiknaðan úr tikkum; CS2-þjónar ganga á 64.
- **Demo frá þjóninum** (SourceTV) er gert ráð fyrir: hún hefur alla leikmenn.
  Upptaka á biðlara (POV-demo) var ekki reynd.

## Leikir og lotur {#matches-and-rounds}

- **Skrám er hópað eftir nafni.** Hlutar eins leiks verða að deila nafni
  fyrir utan `-pN` / `_pN` viðskeyti; skrár eins leiks undir óskyldum nöfnum
  verða aðskildir leikir, og skrár með sama nafni í ólíkum möppum eru
  hópaðar saman (síðan skipt í keðjur ef þær halda ekki áfram hver
  frá annarri).
- **Lifandi leikur byrjar við síðasta `round_announce_match_start`** í
  skrá. Hnífalota sem fylgir ekki sú tilkynning er talin
  sem lota.
- **Lokatímar lota eru nákvæmir upp á eitt sýni** (`--every` tikk, sjálfgefið 1/8 s),
  því ákvörðunin er lesin úr sýnatekinni leikstöðu. Mjög stórt `--every`
  getur misst af stuttum glugga milli loka lotu og upphafs
  næstu lotu og skilið lotuna eftir úti sem incomplete.
- **Jafntefli.** Jafnteflislota (sigurstaða 1, ástæða 10) er ákvörðuð án
  sigurvegara: `winner` er tómt og hvorug hliðin vann hana. Ekkert jafntefli fannst í
  raunverulegri demo-skrá til að prófa þetta gegn; það er prófað á gervi-skránni.
- **Lotur skornar af** við enda skráar eru sleppt (`incomplete`), ekki giskað á
  þær; lotur á undan þeirri fyrstu í skránum eru taldar upp sem `missing`.
- **Skammbyssulotur** fylgja hálfleikslengdinni sem upptakan sýnir: þar sem
  hliðar skipta fyrst milli tveggja samliggjandi venjulegra lota. Upptaka
  sem sýnir ekki það skipti (hún byrjar eftir hálfleik, eða endar á undan,
  eða lota hvoru megin við það vantar) þekkir aðeins lotu 1 sem skammbyssulotu.
  Framlenging hefur enga.
- **Lið.** Lið er klanheitið sem sést mest hjá leikmönnum þess. Án klanheita
  eru liðin `Started T` og `Started CT`. Leikmaður sem skiptir um
  lið í miðjum leik heldur einu liði.

## Atburðir {#events}

- **Allt sem þáttarinn býður er lesið**, með þessum undantekningum: hraði
  leikmannanna (þáttarinn leiðir hann af staðsetningum; hann er ekki í
  demo-skránni), rödd (hljóð, `parse_voice`), og `weapon_fire` sprengjunnar (byrjun
  sprengjusetningar, sem `bomb_beginplant` hefur). Flug handsprengna er geymt á
  sýnatökutíðni leikmannanna (`--every`) og þar sem hver handsprengja stöðvaðist, ekki á hverju
  tikki.
- **Raðir utan lotu** (upphitun, hlé milli upphafs leiksins og
  fyrsta frystitíma umfram tvær mínútur) eru felldar úr töflunni; atburðir
  sem tengjast engum leikmanni eru allir í `events` leikjaskjalsins.
- **Sprengingarraðir** (`smoke`, `flash`, `he`, `molotov`, `decoy`) hafa engan
  `place`: demo-skráin nefnir staði fyrir leikmenn, ekki fyrir handsprengjur. Staður
  kastarans á því augnabliki er í `throwerPlace`.
- **Site sprengjusetningarinnar** kemur frá sprengjusvæðinu sem leikurinn segir að setjandinn
  hafi staðið á, annars staðarheiti setjandans, annars önnur sprengjusetning á sama
  svæði í sömu skrá. Þar sem ekkert af þessu segir til er `site` tómt.
- **Dauði af hendi heimsins** (fall, sprengjan) hefur engan árásarmann: engin felling, enginn
  teamkill, engin opnun; það er dauðsfall.

## Tölfræði {#statistics}

- **Spilaðar lotur** koma frá því hver hafði stöðu fyrstu sekúndu eftir
  frystitíma. Leikmaður sem tengist síðar í lotu telst ekki
  hafa spilað hana (fellingar hans telja samt).
- **Að lifa af fyrir KAST**: leikmaður felldur í after-fasa lifði ekki af
  fyrir KAST, þótt lotulistinn nefni hann samt meðal eftirlifenda.
- **Báðir leikmenn í 1v1** geta fengið clutch í einni lotu; sjá
  [Tölfræði](statistics.md#clutches).
- **Hjálpartækjaskaði** er HE-handsprengjur, molotov og incendiary; felling eða högg
  af kastaðri blindu eða decoy er ekki hjálpartækjaskaði.

## Kortaútflutningur {#map-export}

- Þarf uppsettan leikinn (eða `.vpk`) og CLI Source2Viewer; ekkert
  er sótt.
- Flytur aðeins út `world_physics`; clip og himinn eru sleppt þar sem
  heiti þeirra innihalda `clip` eða `sky`, hver sem stafagerðin er.
- Jörð er greind frá mannvirki eingöngu eftir normal flatarins (Z-hluti 0,7 eða
  meira), svo bratt skábretti er mannvirki og flatt þak er jörð.
- Skráin er í tommum, ekki metrum.

## Minni og tími {#memory-and-time}

- Leikur er geymdur heill í minni á meðan hann er smíðaður, í einu vinnuferli fyrir
  hvern leik. Með mörgum vinnuferlum og litlu `--every` leggst minni saman: lækkaðu
  `--jobs` ef vél verður uppiskroppa.
- Leikur er skrifaður aðeins þegar hann er smíðaður: fyrst `.parquet`, síðan
  `.match.json`. Keyrsla stöðvuð þar á milli skilur eftir töflu án leikjaskjals síns;
  leikur telst skrifaður aðeins með bæði, svo næsta keyrsla umbreytir honum
  aftur. Leikir sem ekki eru byrjaðir eru einfaldlega teknir af næstu keyrslu.
