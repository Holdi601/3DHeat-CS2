---
title: Aktualizácie
nav_order: 14
lang: "sk"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Aktualizácie {#updates}

3DHeat CS2 sa udržiava aktuálny z
[vydaní na GitHube](https://github.com/Holdi601/3DHeat-CS2/releases) tohto
repozitára. Kód:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Kontrola pri spustení {#the-check-at-start-up}

Každé `python -m heat3d_cs2 ...` najprv zistí, či nie je vydaná novšia verzia,
ešte predtým, než prečíta svoje argumenty:

1. Nainštalovaná verzia je súbor `VERSION` v koreni repozitára (`0`, ak sa
   nedá prečítať).
2. Najnovšie vydanie sa pýta na
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, s
   časovým limitom **5 sekúnd**. Odpoveď sa ukladá do vyrovnávacej pamäte na
   **6 hodín** v `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (v systémoch
   bez `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), takže
   žiadosť sa robí najviac každých šesť hodín. „Zatiaľ nič nevydané“ (HTTP 404)
   sa ukladá ako každá iná odpoveď. Offline, pri obmedzení počtu žiadostí, za
   proxy - akákoľvek iná chyba - nástroj pokračuje s verziou, ktorú má, a nič sa
   neukladá.
3. Verzie sa porovnávajú ako čísla: `v1.2.3` a `1.2.3` sú rovnaké, všetko za
   `-` alebo `+` sa ignoruje, chýbajúce časti sa počítajú ako 0.

Keď je vydaná novšia verzia, povie to na chybovom výstupe:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- V termináli (vstup aj chybový výstup sú terminály) sa pýta. Enter, `y`,
  `yes`, `j` alebo `ja` aktualizuje; čokoľvek iné pokračuje bez zmeny. Po
  aktualizácii sa **ten istý príkaz spustí znova**, na novom kóde.
- Bez terminálu - naplánovaný beh, rúra - iba vypíše, kde sa aktualizovať, a
  pokračuje: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` kontrolu vypne. Každá hodnota iná ako prázdna, `0`,
`false` alebo `no` znamená zapnuté.

## Aktualizácia na požiadanie {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Vždy sa pýta GitHubu (vyrovnávacia pamäť sa nepoužije). Vypíše `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, alebo
`<new> is out (this is <current>): <url>` a potom aktualizuje (pokiaľ nie je
`--check`). Návratový kód `1`, keď sa aktualizácia pokúsila a zlyhala, inak `0`.

## Ako sa aktualizácia uplatní {#how-an-update-is-applied}

Závisí to od toho, ako bola kópia nainštalovaná:

- **Git checkout** (v koreni je `.git` a `git` je v `PATH`): `git pull --ff-only`.
  Odmietne sa, kým sledované súbory majú lokálne zmeny („this checkout has local
  changes; commit or stash them, then run `git pull`“): sú to niečia práca a
  aktualizácia nerozhoduje, čo sa s nimi stane. Nesledované súbory to
  neblokujú.
- **Stiahnutá kópia**: zdrojový archív vydania (zipball GitHubu) sa stiahne a
  rozbalí do dočasného priečinka - položky, ktoré by pristáli mimo neho, sa
  preskočia - a jeho `VERSION` musí byť verzia, ktorú vydanie uvádza, inak sa
  nič nezmení („the archive is version X, not Y“). Potom sa jeho súbory
  skopírujú cez priečinok. Súbory, ktoré nie sú súčasťou vydania - vaše dema,
  výstupy, virtuálne prostredie, čokoľvek, čo ste vytvorili - sa nikdy
  nedotknú. Python moduly, ktoré vydanie už nemá, sa zmažú z vlastných balíkov
  nástroja (priečinky `heat3d_*`), aby zastaraný modul nezatienil svojho
  náhradníka.

Ak aktualizácia zlyhá, správa sa vypíše a nástroj beží na verzii, ktorú má.
