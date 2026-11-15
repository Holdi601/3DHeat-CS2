---
title: Updates
nav_order: 14
lang: "nl"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Updates {#updates}

3DHeat CS2 houdt zichzelf actueel via de [releases op GitHub](https://github.com/Holdi601/3DHeat-CS2/releases) van deze repository. Code: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py), [`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## De controle bij het opstarten {#the-check-at-start-up}

Elke `python -m heat3d_cs2 ...` vraagt eerst of er een nieuwere release is, nog voordat hij zijn argumenten leest:

1. De geïnstalleerde versie is het bestand `VERSION` in de hoofdmap van de repository (`0` als het niet gelezen kan worden).
2. De nieuwste release wordt opgevraagd bij `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, met een time-out van **5 seconden**. Het antwoord wordt **6 uur** bewaard in `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (op systemen zonder `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), zodat de aanvraag hooguit elke zes uur wordt gedaan. "Nog niets uitgebracht" (HTTP 404) wordt bewaard als een antwoord. Offline, rate-limited, achter een proxy - elke andere fout - gaat de tool door met de versie die hij heeft, en er wordt niets bewaard.
3. Versies worden als getallen vergeleken: `v1.2.3` en `1.2.3` zijn gelijk, alles na een `-` of `+` wordt genegeerd, ontbrekende delen tellen als 0.

Wanneer er een nieuwere release is, meldt hij dat op de foutstroom:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- In een terminal (zowel de invoer- als de foutstroom zijn terminals) vraagt hij het. Enter, `y`, `yes`, `j` of `ja` update; al het andere gaat door zonder wijziging. Na een update **draait dezelfde opdracht opnieuw**, op de nieuwe code.
- Zonder terminal - een geplande run, een pijp - meldt hij alleen waar je kunt updaten en gaat door: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` schakelt de controle uit. Elke waarde behalve leeg, `0`, `false` of `no` telt als aan.

## Op verzoek updaten {#updating-on-request}

```bash
python -m heat3d_update            # update naar de nieuwste release
python -m heat3d_update --check    # alleen zeggen of er een is
```

Dit vraagt altijd GitHub (de bewaarde kopie wordt niet gebruikt). Het drukt `Up to date: <version>.` af, `No release found (this is <version>); offline, or nothing published yet.`, of `<new> is out (this is <current>): <url>` en werkt dan bij (tenzij `--check`). Afsluitcode `1` wanneer een update is geprobeerd en mislukt, `0` anders.

## Hoe een update wordt toegepast {#how-an-update-is-applied}

Dat hangt af van hoe de kopie is geïnstalleerd:

- **Een git-kopie** (er is een `.git` in de hoofdmap en `git` op `PATH`): `git pull --ff-only`. Dat wordt geweigerd zolang bijgehouden bestanden lokale wijzigingen hebben ("this checkout has local changes; commit or stash them, then run `git pull`"): dat is iemands werk, en een update beslist niet wat ermee gebeurt. Niet-bijgehouden bestanden blokkeren het niet.
- **Een gedownloade kopie**: het bronarchief van de release (het zipbestand van GitHub) wordt gedownload en uitgepakt in een tijdelijke map - items die buiten die map zouden terechtkomen worden overgeslagen - en zijn `VERSION` moet de versie zijn die de release opgeeft, anders wordt er niets veranderd ("the archive is version X, not Y"). Daarna worden zijn bestanden over de map gekopieerd. Bestanden die geen deel van de release zijn - je demo's, uitvoer, virtuele omgeving, alles wat jij hebt gemaakt - worden nooit aangeraakt. Python-modules die de release niet meer heeft, worden verwijderd uit de eigen pakketten van de tool (de mappen `heat3d_*`), zodat een verouderde module zijn vervanger niet kan overschaduwen.

Als een update mislukt, wordt de melding afgedrukt en draait de tool door op de versie die hij heeft.
