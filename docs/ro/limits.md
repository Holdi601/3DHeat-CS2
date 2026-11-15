---
title: Limite
nav_order: 13
lang: "ro"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Limite {#limits}

Ce presupune convertorul, ce nu tratează și ce nu este verificat. Fiecare punct este scris
după codul așa cum este acum.

## Ce citește {#what-it-reads}

- **Doar fișiere `.dem` necomprimate.** `.dem.zst`, `.dem.bz2`, `.rar` și `.zip` trebuie
  dezarhivate mai întâi. Extensia se potrivește oricare ar fi majusculele (`.dem`, `.DEM`),
  în foldere ca și pentru fișierele date pe nume.
- **Meciuri de dezamorsare de bombă.** Codurile motivului rundei, plantarea și site-ul
  bombei, tipurile de cumpărare și rundele de pistol sunt cele ale modului de dezamorsare
  a bombei. Hărțile cu ostatici, Wingman și alte moduri nu sunt tratate special și nu sunt verificate.
- **64 de tick-uri pe secundă** sunt presupuse (`TICKRATE = 64`) pentru orice timp calculat
  din tick-uri; serverele CS2 rulează la 64.
- **Un demo de la server** (SourceTV) este presupus: are pe toți jucătorii. O înregistrare
  făcută pe client (demo POV) nu a fost încercată.

## Meciuri și runde {#matches-and-rounds}

- **Fișierele sunt grupate după nume.** Părțile unui meci trebuie să aibă același nume în
  afara sufixului `-pN` / `_pN`; fișierele unui meci sub nume fără legătură devin meciuri
  separate, iar fișierele cu același nume din foldere diferite sunt grupate împreună (apoi
  împărțite în lanțuri dacă nu continuă una alteia).
- **Meciul live începe la ultimul `round_announce_match_start`** dintr-un fișier. O rundă cu
  cuțitul care nu este urmată de acel anunț este numărată ca rundă.
- **Timpii de sfârșit ai rundelor sunt exacți până la un eșantion** (`--every` tick-uri,
  1/8 s implicit), pentru că decizia se citește din starea jocului eșantionată. Un `--every`
  foarte mare poate rata o fereastră scurtă între sfârșitul unei runde și începutul următoarei
  și poate lăsa runda afară ca incompletă.
- **Egalități.** O rundă egală (statusul de câștig 1, motivul 10) este decisă fără
  câștigător: `winner` este gol și nicio parte nu a câștigat-o. Nu s-a întâlnit nicio
  egalitate într-un demo real pentru a verifica asta; este verificată pe cel sintetic.
- **Rundele întrerupte** de sfârșitul unui fișier sunt lăsate afară (`incomplete`), nu sunt
  ghicite; rundele dinaintea primei din fișiere sunt listate ca `missing`.
- **Rundele de pistol** urmează lungimea reprizei arătate de înregistrare: acolo unde
  taberele schimbă prima dată părțile între două runde regulamentare consecutive. O
  înregistrare care nu arată acea schimbare (începe după pauză, se termină înainte de ea
  sau lipsește o rundă de o parte și de alta a ei) știe doar runda 1 ca rundă de pistol.
  Prelungirea nu are niciuna.
- **Echipe.** O echipă este numele de clan cel mai des văzut pentru jucătorii săi. Fără
  nume de clan, echipele sunt `Started T` și `Started CT`. Un jucător care își schimbă
  echipa în mijlocul meciului păstrează o singură echipă.

## Evenimente {#events}

- **Tot ce oferă parserul este citit**, cu aceste excepții: viteza jucătorilor (parserul o
  deduce din poziții; nu este în demo), vocea (audio, `parse_voice`) și `weapon_fire` al
  bombei (începutul unei plantări, pe care îl are `bomb_beginplant`). Zborurile grenadelor
  sunt păstrate la eșantionarea jucătorilor (`--every`) și acolo unde s-a oprit fiecare
  grenadă, nu la fiecare tick.
- **Rândurile din afara unei runde** (încălzirea, o pauză între începutul meciului și primul
  timp de îngheț, mai lungă de două minute) sunt lăsate afară din tabel; evenimentele fără
  jucător sunt toate în `events` din documentul meciului.
- **Rândurile de detonare** (`smoke`, `flash`, `he`, `molotov`, `decoy`) nu au `place`: demo-ul
  numește locuri pentru jucători, nu pentru grenade. Locul aruncătorului în acel moment este
  în `throwerPlace`.
- **Site-ul plantării** vine din zona bombei în care jocul spune că a stat plantatorul, apoi
  din numele locului plantatorului, apoi dintr-o altă plantare din aceeași zonă din același
  fișier. Când niciuna nu spune nimic, `site` este gol.
- **O moarte provocată de lume** (o cădere, bomba) nu are atacator: nicio eliminare, niciun
  teamkill, nicio deschidere; este doar o moarte.

## Statistici {#statistics}

- **Rundele jucate** vin din cine a avut o poziție în prima secundă de după timpul de
  îngheț. Un jucător care se conectează mai târziu într-o rundă nu o numără ca jucată (eliminările
  lui contează totuși).
- **Supraviețuirea pentru KAST**: un jucător ucis în faza după nu a supraviețuit pentru KAST,
  deși lista rundei îl menționează printre supraviețuitori.
- **Ambii jucători dintr-un 1v1** pot primi un clutch în aceeași rundă; vezi
  [Statistici](statistics.md#clutches).
- **Daunele de utilitare** sunt grenadele HE, molotovele și incendiarele; o eliminare sau o
  lovitură dată de un flash aruncat sau de o momeală nu sunt daune de utilitare.

## Exportul hărții {#map-export}

- Are nevoie de jocul instalat (sau de `.vpk`) și de CLI-ul Source2Viewer; nu se descarcă nimic.
- Exportă doar `world_physics`; clipurile și cerul sunt lăsate afară după numele lor care
  conțin `clip` sau `sky`, oricare ar fi majusculele.
- Solul este deosebit de structură doar după componenta Z a normalei fiecărei fețe (0,7 sau
  mai mult), deci o rampă abruptă este structură, iar un acoperiș plat este sol.
- Fișierul este în inchi, nu în metri.

## Memorie și timp {#memory-and-time}

- Un meci este ținut în memorie întreg cât timp este construit, într-un singur lucrător pentru
  fiecare meci. Cu mulți lucrători și un `--every` mic, memoria se adună: micșorează `--jobs`
  dacă o mașină rămâne fără memorie.
- Un meci este scris abia când este construit: mai întâi `.parquet`, apoi `.match.json`. O
  rulare oprită între ele lasă un tabel fără documentul meciului; un meci contează ca scris
  doar cu amândouă, deci următoarea rulare îl convertește din nou. Meciurile care nu au
  început încă sunt pur și simplu preluate de următoarea rulare.
