---
title: "Përditësimet"
nav_order: 14
lang: "sq"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Përditësimet {#updates}

3DHeat CS2 e mban veten të përditësuar nga
[botimet në GitHub](https://github.com/Holdi601/3DHeat-CS2/releases) të kësaj depoje. Kodi:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Kontrolli gjatë nisjes {#the-check-at-start-up}

Çdo `python -m heat3d_cs2 ...` pyet së pari nëse ka dalë një botim më i ri,
madje para se të lexojë argumentet e veta:

1. Versioni i instaluar është skedari `VERSION` në rrënjën e depoje
   (`0` nëse nuk lexohet).
2. Botimi më i ri kërkohet te
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, me një
   afat prej **5 sekondash**. Përgjigjja ruhet në cache për **6 orë** në
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (në sisteme pa
   `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), kështu që
   kërkesa bëhet më së shumti çdo gjashtë orë. "Ende asgjë e botuar" (HTTP 404)
   ruhet në cache si një përgjigje. Pa internet, me kufizim kërkesash, pas një proxy - çdo dështim tjetër -
   mjeti vazhdon me versionin që ka, dhe asgjë nuk ruhet në cache.
3. Versionet krahasohen si numra: `v1.2.3` dhe `1.2.3` janë të barabarta, çdo gjë
   pas një `-` ose `+` shpërfillet, pjesët që mungojnë llogariten 0.

Kur ka dalë një botim më i ri, e thotë në rrjedhën e gabimeve:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Në një terminal (si hyrja ashtu edhe rrjedha e gabimeve janë terminale) pyet.
  Enter, `y`, `yes`, `j` ose `ja` përditëson; çdo gjë tjetër vazhdon pa ndryshim.
  Pas një përditësimi **e njëjta komandë xhirohet përsëri**, mbi kodin e ri.
- Pa terminal - një xhirim i planifikuar, një pipe - vetëm printon ku të përditësosh
  dhe vazhdon: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` e fik kontrollin. Çdo vlerë tjetër përveç bosh,
`0`, `false` ose `no` llogaritet si aktive.

## Përditësimi me kërkesë {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Kjo e pyet gjithmonë GitHub (cache nuk përdoret). Printon `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, ose
`<new> is out (this is <current>): <url>` dhe pastaj përditëson (përveç me `--check`).
Kodi i daljes `1` kur një përditësim u provua dhe dështoi, `0` përndryshe.

## Si zbatohet një përditësim {#how-an-update-is-applied}

Varet nga si u instalua kopja:

- **Një checkout me git** (ka një `.git` në rrënjë dhe `git` në `PATH`):
  `git pull --ff-only`. Refuzohet ndërsa skedarët e ndjekur kanë ndryshime lokale
  ("this checkout has local changes; commit or stash them, then run
  `git pull`"): ato janë puna e dikujt, dhe një përditësim nuk vendos çfarë
  ndodh me to. Skedarët e pandjekur nuk e bllokojnë.
- **Një kopje e shkarkuar**: arkiva burimore e botimit (zipball i GitHub) shkarkohet
  dhe shpaketohet në një dosje të përkohshme - hyrjet që do të binin
  jashtë saj anashkalohen - dhe `VERSION` i saj duhet të jetë versioni që pretendon
  botimi, përndryshe asgjë nuk ndryshon ("the archive is version X, not Y"). Pastaj
  skedarët e saj kopjohen mbi dosjen. Skedarët që nuk janë pjesë e botimit -
  demot e tua, daljet, mjedisi virtual, çdo gjë që ke bërë - nuk preken kurrë.
  Modulet Python që botimi nuk i ka më fshihen nga paketat e vetë mjetit
  (dosjet `heat3d_*`), që një modul i vjetër të mos hijezojë zëvendësuesin e tij.

Nëse një përditësim dështon, mesazhi printohet dhe mjeti xhirohet me versionin
që ka.
