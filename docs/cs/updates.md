---
title: Aktualizace
nav_order: 14
lang: "cs"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Aktualizace {#updates}

3DHeat CS2 se udržuje aktuální sám z [vydání (releases)](https://github.com/Holdi601/3DHeat-CS2/releases)
tohoto repozitáře. Kód:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## Kontrola při spuštění {#the-check-at-start-up}

Každé `python -m heat3d_cs2 ...` se nejdřív zeptá, zda není vydáno novější
vydání, ještě předtím, než přečte své argumenty:

1. Nainstalovaná verze je soubor `VERSION` v kořeni repozitáře (`0`, když ho
   nejde přečíst).
2. Nejnovější vydání se zjišťuje na
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, s
   časovým limitem **5 sekund**. Odpověď se ukládá do mezipaměti na **6 hodin**
   v `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (systémy bez
   `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), takže se
   dotaz dělá nejvýš každých šest hodin. „Zatím nic nevydáno“ (HTTP 404) se
   ukládá jako odpověď. Offline, omezeno počtem dotazů, za proxy - jakákoli jiná
   chyba - nástroj běží dál s verzí, kterou má, a nic se neukládá.
3. Verze se porovnávají jako čísla: `v1.2.3` a `1.2.3` jsou stejné, cokoli za
   `-` nebo `+` se ignoruje, chybějící části se počítají jako 0.

Když je vydáno novější vydání, řekne to na chybovém výstupu:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- V terminálu (vstup i chybový výstup jsou terminály) se zeptá. Enter, `y`,
  `yes`, `j` nebo `ja` aktualizuje; cokoli jiného pokračuje beze změny. Po
  aktualizaci se **stejný příkaz spustí znovu**, už s novým kódem.
- Bez terminálu - naplánované spuštění, roura - jen vypíše, kde se aktualizovat,
  a pokračuje: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` kontrolu vypne. Každá hodnota jiná než prázdná, `0`,
`false` nebo `no` znamená zapnuto.

## Aktualizace na žádost {#updating-on-request}

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

Vždy se ptá GitHubu (mezipaměť se nepoužije). Vypíše `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, nebo
`<new> is out (this is <current>): <url>` a pak aktualizuje (pokud není `--check`).
Návratový kód `1`, když se aktualizace pokusila a selhala, jinak `0`.

## Jak se aktualizace provádí {#how-an-update-is-applied}

Záleží na tom, jak byla kopie nainstalována:

- **Kopie z gitu** (v kořeni je `.git` a `git` je na `PATH`): `git pull --ff-only`.
  Odmítne se, dokud sledované soubory mají lokální změny („this checkout has
  local changes; commit or stash them, then run `git pull`“): to je něčí práce a
  aktualizace nerozhoduje, co se s nimi stane. Nesledované soubory aktualizaci
  neblokují.
- **Stažená kopie**: zdrojový archiv vydání (zipball GitHubu) se stáhne a
  rozbalí do dočasné složky - položky, které by skončily mimo ni, se přeskočí -
  a jeho `VERSION` musí být verze, kterou vydání uvádí, jinak se nic nezmění
  („the archive is version X, not Y“). Pak se jeho soubory zkopírují přes složku.
  Soubory, které nejsou součástí vydání - vaše dema, výstupy, virtuální prostředí,
  cokoli, co jste vytvořili - se nikdy nedotknou. Moduly Pythonu, které vydání
  už nemá, se smažou z vlastních balíčků nástroje (složky `heat3d_*`), aby
  zastaralý modul nezastínil svou náhradu.

Když aktualizace selže, zpráva se vypíše a nástroj běží na verzi, kterou má.
