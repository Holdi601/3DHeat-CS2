---
title: Før du går i gang
nav_order: 2
lang: "da"
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Før du går i gang {#before-you-start}

Ny til kommandolinjen? Denne side fører dig fra ingenting til en fungerende
3DHeat CS2 på cirka ti minutter. Du skriver kommandoer i en *terminal*, et vindue
hvor du skriver en linje og trykker Enter.

## 1. Installer Python {#install-python}

1. Hent Python 3.10 eller nyere fra <https://www.python.org/downloads/>.
2. Kør installationsprogrammet. På den første skærm sætter du flueben i **Add python.exe to PATH**,
   og klikker derefter på **Install Now**.
3. Kontrollér det: åbn en terminal (trin 3) og skriv `python --version`. Du bør
   se `Python 3.` og et tal på 10 eller højere.

På Linux eller macOS er Python normalt allerede installeret: brug `python3`, hvor
siderne siger `python`.

## 2. Hent 3DHeat CS2 {#get-3dheat-cs2}

Hent zip-filen fra [udgivelsessiden](https://github.com/Holdi601/3DHeat-CS2/releases) og pak den ud,
for eksempel til `C:\Tools\3DHeat-CS2`. (Har du Git, virker `git clone` også.)

## 3. Åbn en terminal i den mappe {#open-a-terminal-in-that-folder}

- **Windows:** åbn mappen i Stifinder, klik i adresselinjen, skriv
  `powershell` og tryk Enter. Et blåt eller sort vindue åbner, allerede i
  den mappe.
- **macOS / Linux:** åbn *Terminal* og skriv `cd ` (med et mellemrum), træk
  mappen ind i vinduet, tryk Enter.

`cd <folder>` flytter terminalen til en anden mappe. Alle kommandoer på disse
sider skrives i værktøjets egen mappe.

## 4. Installer det, det har brug for {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Du bør se `Successfully installed ...` til sidst (eller `Requirement
already satisfied`).

## 5. Kontrollér, at det virker {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Du bør se: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Sådan læser du kommandoerne på disse sider {#how-to-read-the-commands-on-these-pages}

- Ord i `<vinkelparenteser>` er **pladsholdere**: skriv i stedet din egen fil eller mappe,
  uden parenteserne. `python -m heat3d_cs2 demos <demo files or folders> -o out` betyder,
  at du erstatter den del i parentes.
- En sti med mellemrum skal stå i anførselstegn: `"C:\My Games\my file"`.
- Linjer, der starter med `#` i eksemplerne, er kommentarer; du skriver dem ikke.
- Succes ser sådan ud: efter `demos` en linje `1 match(es), 1 at a time` og derefter en linje pr. kamp, der slutter med `lost 0`.

## Almindelige fejl {#common-errors}

| Du ser | Gør dette |
|---|---|
| `'python' is not recognized` eller `command not found` | Python står ikke på PATH: kør installationsprogrammet igen og sæt flueben i **Add python.exe to PATH**, og åbn derefter en ny terminal. På macOS/Linux prøv `python3`. |
| `No module named ...` | trin 4 blev sprunget over, eller kørt i en anden mappe: `cd` til værktøjets mappe og kør det igen. |
| `pip is not recognized` | brug `python -m pip ...` i stedet for `pip ...`. |
| `No such file or directory` / `can't open file` | terminalen står i den forkerte mappe, eller stien er skrevet forkert: tjek den, og sæt stier med mellemrum i anførselstegn. |
| rød tekst, der slutter med en `error:`-linje | læs den sidste linje: den siger, hvad der mangler. Siden [Kommandoer](../commands.md) lister meddelelserne. |
