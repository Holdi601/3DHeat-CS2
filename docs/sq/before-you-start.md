---
title: "Para se të fillosh"
nav_order: 2
lang: sq
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Para se të fillosh {#before-you-start}

Je i ri me vijën e komandës? Kjo faqe të çon nga zero te një 3DHeat CS2 që funksionon në
rreth dhjetë minuta. Shkruaj komanda në një *terminal*, një dritare
ku shkruan një rresht dhe shtyp Enter.

## 1. Instalo Python {#install-python}

1. Shkarko Python 3.10 ose më të ri nga <https://www.python.org/downloads/>.
2. Nis instaluesin. Në ekranin e parë zgjidh **Add python.exe to PATH**,
   pastaj kliko **Install Now**.
3. Kontrollo: hap një terminal (hapi 3) dhe shkruaj `python --version`. Duhet të
   shih `Python 3.` dhe një numër 10 ose më të madh.

Në Linux ose macOS, Python zakonisht është tashmë i instaluar: përdor `python3` aty ku
këto faqe thonë `python`.

## 2. Merr 3DHeat CS2 {#get-3dheat-cs2}

Shkarko zip-in nga
[faqja Releases](https://github.com/Holdi601/3DHeat-CS2/releases) dhe çzipoje, për
shembull te `C:\Tools\3DHeat-CS2`. (Nëse ke Git, funksionon edhe `git clone`.)

## 3. Hap një terminal në atë dosje {#open-a-terminal-in-that-folder}

- **Windows:** hap dosjen në File Explorer, kliko te shiriti i adresës, shkruaj
  `powershell` dhe shtyp Enter. Hapet një dritare blu ose e zezë, tashmë
  brenda asaj dosjeje.
- **macOS / Linux:** hap *Terminal* dhe shkruaj `cd ` (me një hapësirë), tërhiq
  dosjen në dritare, shtyp Enter.

`cd <folder>` e zhvendos terminalin në një dosje tjetër. Të gjitha komandat në këto
faqe shkruhen në dosjen e vetë mjetit.

## 4. Instalo çfarë i duhet {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Në fund duhet të shohësh `Successfully installed ...` (ose `Requirement
already satisfied`).

## 5. Kontrollo që funksionon {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Duhet të shohësh: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Si t'i lexo komandat në këto faqe {#how-to-read-the-commands-on-these-pages}

- Fjalët në `<angle brackets>` janë vendmbajtës: shkruaj skedarin ose dosjen tënde
  në vend të tyre, pa kllapat. `python -m heat3d_cs2 demos <demo files or folders> -o out` do të thotë se
  e zëvendëso pjesën në kllapa.
- Një shteg me hapësira vendoset në thonjëza: `"C:\My Games\my file"`.
- Rreshtat që nisin me `#` në shembuj janë komente; nuk i shkruaj.
- Suksesi duket kështu: pas `demos`, një rresht `1 match(es), 1 at a time` dhe pastaj një rresht për çdo ndeshje që mbaron me `lost 0`.

## Gabimet e zakonshme {#common-errors}

| Çfarë sheh | Çfarë të bësh |
|---|---|
| `'python' is not recognized` ose `command not found` | Python nuk është në PATH: nis përsëri instaluesin dhe zgjidh **Add python.exe to PATH**, pastaj hap një terminal të ri. Në macOS/Linux provo `python3`. |
| `No module named ...` | hapi 4 u anashkalua ose u ekzekutua në një dosje tjetër: bëj `cd` te dosja e mjetit dhe ekzekutoje përsëri. |
| `pip is not recognized` | përdor `python -m pip ...` në vend të `pip ...`. |
| `No such file or directory` / `can't open file` | terminali është në dosjen e gabuar, ose shtegu është shkruar gabim: kontrolloje, dhe vendos shtigjet me hapësira në thonjëza. |
| tekst i kuq që mbaron me një rresht `error:` | lexo rreshtin e fundit: thotë çfarë mungon. Faqja [Komandat](../commands.md) liston mesazhet. |
