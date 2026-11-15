---
title: "Frissítések"
nav_order: 14
lang: "hu"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Frissítések {#updates}

A 3DHeat CS2 ezt a tároló [GitHub-kiadásaiból](https://github.com/Holdi601/3DHeat-CS2/releases) tartja naprakészen. Kód:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Az ellenőrzés indításkor {#the-check-at-start-up}

Minden `python -m heat3d_cs2 ...` először megkérdezi, hogy megjelent-e újabb kiadás, mielőtt még beolvasná a
kapcsolóit:

1. A telepített verzió a tároló gyökerében lévő `VERSION` fájl (`0`, ha nem olvasható).
2. A legújabb kiadást a `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest` címen kérdezzük le, **5 másodperces**
   időkorláttal. A választ **6 órára** gyorsítótárazzuk a `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` fájlban
   (ha nincs `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), így a kérés legfeljebb hatoránként egyszer
   megy ki. A "még nincs kiadás" (HTTP 404) is válaszként gyorsítótárazódik. Ha nincs hálózat, korlátozás van, proxy van mögötte
   - bármilyen más hiba -, az eszköz a meglévő verzióval megy tovább, és semmi nem kerül a gyorsítótárba.
3. A verziókat számként hasonlítjuk össze: a `v1.2.3` és az `1.2.3` egyenlő, a `-` vagy `+` utáni rész figyelmen kívül marad,
   a hiányzó részek 0-nak számítanak.

Ha újabb kiadás van, a hibafolyamon ezt mondja:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Terminálban (a bemeneti és a hibafolyam is terminál) rákérdez. Az Enter, `y`, `yes`, `j` vagy `ja` frissít; minden más
  továbbmegy változatlanul. A frissítés után **ugyanaz a parancs újra lefut**, az új kóddal.
- Terminál nélkül - ütemezett futás, csővezeték - csak kiírja, hol kell frissíteni, és megy tovább:
  `Run python -m heat3d_update in <folder> to update.`

A `HEAT3D_NO_UPDATE=1` kikapcsolja az ellenőrzést. Minden érték, amely nem üres, `0`, `false` vagy `no`, bekapcsoltnak számít.

## Frissítés kérésre {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Ez mindig megkérdezi a GitHubot (a gyorsítótárat nem használja). Kiírja: `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, vagy `<new> is out (this is <current>): <url>`,
és utána frissít (kivéve `--check` esetén). Kilépési kód `1`, ha egy frissítést megkíséreltek és az sikertelen volt, egyébként
`0`.

## Hogyan alkalmazódik a frissítés {#how-an-update-is-applied}

Attól függ, hogyan lett telepítve a másolat:

- **Git-másolat** (van `.git` a gyökérben, és a `git` a `PATH`-on): `git pull --ff-only`. Akkor utasítja el, ha a követett
  fájlokban helyi változtatások vannak ("this checkout has local changes; commit or stash them, then run `git pull`"): ezek
  valakinek a munkái, és egy frissítés nem dönti el, mi legyen velük. A követetlen fájlok nem akadályozzák.
- **Letöltött másolat**: a kiadás forrásarchívuma (a GitHub zipball-ja) letöltődik és egy ideiglenes mappába csomagolódik ki
  - a mappából kilépő bejegyzéseket kihagyjuk -, és a `VERSION`-jének meg kell egyeznie azzal a verzióval, amelyet a kiadás állít,
  különben semmi nem változik ("the archive is version X, not Y"). Ezután a fájljai átmásolódnak a mappára. A kiadás részét nem
  képező fájlok - a demóid, a kimenetek, a virtuális környezet, bármi, amit te készítettél - sosem érintődnek. A kiadásból
  kikerült Python-modulok törlődnek az eszköz saját csomagjaiból (a `heat3d_*` mappák), hogy egy elavult modul ne takarja el
  a helyettesítőjét.

Ha egy frissítés elbukik, az üzenet kiíródik, és az eszköz a meglévő verziójával fut tovább.
