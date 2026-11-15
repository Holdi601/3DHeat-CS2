---
title: Prije nego što počnete
nav_order: 2
lang: "hr"
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Prije nego što počnete {#before-you-start}

Ne znate ništa o naredbenom retku? Ova stranica vas vodi od nule do radnog
3DHeat CS2 u oko deset minuta. Naredbe upisujete u *terminal*, prozor u koji
napišete redak i pritisnete Enter.

## 1. Instalirajte Python {#install-python}

1. Preuzmite Python 3.10 ili noviji s <https://www.python.org/downloads/>.
2. Pokrenite instalaciju. Na prvom zaslonu označite **Add python.exe to PATH**,
   zatim kliknite **Install Now**.
3. Provjerite: otvorite terminal (korak 3) i upišite `python --version`. Trebali biste
   vidjeti `Python 3.` i broj 10 ili veći.

Na Linuxu ili macOS-u Python je obično već instaliran: umjesto `python` upotrijebite `python3`,
kao što pišu ove stranice.

## 2. Nabavite 3DHeat CS2 {#get-3dheat-cs2}

Preuzmite zip s [stranice izdanja](https://github.com/Holdi601/3DHeat-CS2/releases) i raspakirajte ga,
na primjer u `C:\Tools\3DHeat-CS2`. (Ako imate Git, radi i `git clone`.)

## 3. Otvorite terminal u toj mapi {#open-a-terminal-in-that-folder}

- **Windows:** otvorite mapu u File Exploreru, kliknite adresnu traku, upišite
  `powershell` i pritisnite Enter. Otvara se plavi ili crni prozor, već u
  toj mapi.
- **macOS / Linux:** otvorite *Terminal* i upišite `cd ` (s razmakom), povucite
  mapu u prozor, pritisnite Enter.

`cd <folder>` premješta terminal u drugu mapu. Sve naredbe na ovim stranicama upisuju se
u mapi samog alata.

## 4. Instalirajte što treba {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na kraju biste trebali vidjeti `Successfully installed ...` (ili `Requirement
already satisfied`).

## 5. Provjerite radi li {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Trebali biste vidjeti: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Kako čitati naredbe na ovim stranicama {#how-to-read-the-commands-on-these-pages}

- Riječi u `<kutnim zagradama>` su **mjesta za upis**: upišite umjesto njih svoju datoteku ili mapu,
  bez zagrada. `python -m heat3d_cs2 demos <demo files or folders> -o out` znači
  da zamijenite zagrađeni dio.
- Put koji ima razmake ide u navodnike: `"C:\My Games\my file"`.
- Redci koji počinju s `#` u primjerima su komentari; ne upisujete ih.
- Uspjeh izgleda ovako: nakon `demos`, redak `1 match(es), 1 at a time` i zatim po jedan redak za svaku utakmicu koji završava s `lost 0`.

## Česte greške {#common-errors}

| Vidite | Učinite ovo |
|---|---|
| `'python' is not recognized` ili `command not found` | Python nije u PATH-u: ponovno pokrenite instalaciju i označite **Add python.exe to PATH**, zatim otvorite novi terminal. Na macOS-u/Linuxu probajte `python3`. |
| `No module named ...` | korak 4 je preskočen ili je pokrenut u drugoj mapi: `cd` u mapu alata i pokrenite ga ponovno. |
| `pip is not recognized` | umjesto `pip ...` upotrijebite `python -m pip ...`. |
| `No such file or directory` / `can't open file` | terminal je u krivoj mapi, ili je put krivo upisan: provjerite ga, a putove s razmacima stavite u navodnike. |
| crveni tekst koji završava redom `error:` | pročitajte zadnji redak: kaže što nedostaje. Stranica [Naredbe](commands.md) navodi poruke. |
