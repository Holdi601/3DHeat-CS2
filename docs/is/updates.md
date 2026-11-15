---
title: "Uppfærslur"
nav_order: 14
lang: "is"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Uppfærslur {#updates}

3DHeat CS2 heldur sér uppfærðu frá
[GitHub-útgáfum](https://github.com/Holdi601/3DHeat-CS2/releases) þessa hugbúnaðarsafns. Kóði:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Athugunin við ræsingu {#the-check-at-start-up}

Hver `python -m heat3d_cs2 ...` spyr fyrst hvort nýrri útgáfa sé komin,
áður en hún les færibreytur sínar:

1. Uppsetta útgáfan er skráin `VERSION` í rót hugbúnaðarsafnsins
   (`0` ef ekki er hægt að lesa hana).
2. Nýjasta útgáfan er spurð af
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, með
   **5 sekúndna** tímamörkum. Svarið er geymt í skyndiminni í **6 klukkustundir** í
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (á kerfum án
   `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), svo
   beiðnin er gerð í mesta lagi á sex tíma fresti. „Ekkert gefið út enn“ (HTTP 404)
   er geymt eins og svar. Án nets, með hraðatakmörkun, bak við milliþjón - hver önnur
   bilun - heldur verkfærið áfram með útgáfuna sem það hefur, og ekkert er
   geymt.
3. Útgáfur eru bornar saman sem tölur: `v1.2.3` og `1.2.3` eru jafnar, allt
   á eftir `-` eða `+` er hunsað, vantandi hlutar teljast 0.

Þegar nýrri útgáfa er komin segir það frá því á villustraumnum:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Í skipanalínu (bæði inntak og villustraumur eru skipanalínur) spyr það.
  Enter, `y`, `yes`, `j` eða `ja` uppfærir; allt annað heldur áfram óbreytt.
  Eftir uppfærslu **keyrist sama skipunin aftur**, á nýja kóðanum.
- Án skipanalínu - tímasett keyrsla, pípa - prentar það aðeins hvar á að
  uppfæra og heldur áfram: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` slekkur á athuguninni. Hvert gildi annað en tómt,
`0`, `false` eða `no` telst kveikt.

## Uppfærsla að beiðni {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Þetta spyr alltaf GitHub (skyndiminnið er ekki notað). Það prentar `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, eða
`<new> is out (this is <current>): <url>` og uppfærir síðan (nema `--check`).
Útgöngukóði `1` þegar uppfærsla var reynd og mistókst, annars `0`.

## Hvernig uppfærsla er framkvæmd {#how-an-update-is-applied}

Það fer eftir því hvernig afritið var sett upp:

- **Git-afrit** (`.git` er í rótinni og `git` á `PATH`):
  `git pull --ff-only`. Það er neitað á meðan fylgdar skrár hafa staðbundnar breytingar
  („this checkout has local changes; commit or stash them, then run
  `git pull`“): það er vinna einhvers, og uppfærsla ákveður ekki hvað
  verður um hana. Skrár sem ekki er fylgst með hindra það ekki.
- **Niðurhalað afrit**: frumkóðasafn útgáfunnar (zipball GitHub) er
  sótt og pakkað upp í tímabundna möppu - færslum sem myndu lenda
  utan hennar er sleppt - og `VERSION` þess verður að vera útgáfan sem útgáfan
  segist vera, annars er engu breytt („the archive is version X, not Y“). Síðan eru
  skrár þess afritaðar yfir möppuna. Skrár sem eru ekki hluti útgáfunnar -
  demo-skrárnar þínar, úttak, sýndarumhverfi, allt sem þú bjóst til - eru aldrei
  snertar. Python-einingar sem útgáfan hefur ekki lengur eru eyddar úr
  eigin pökkum verkfærisins (`heat3d_*`-möppunum), svo úrelt eining getur ekki
  skyggt á arftaka sinn.

Ef uppfærsla mistekst er skilaboðið prentað og verkfærið heldur áfram á útgáfunni
sem það hefur.
