---
title: Abans de començar
nav_order: 2
lang: "ca"
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Abans de començar {#before-you-start}

Si ets nou amb la línia d'ordres, aquesta pàgina et porta des de no tenir res fins a un 3DHeat CS2
en funcionament en uns deu minuts. Escriu ordres en un *terminal*, una finestra on
escriu una línia i prem Intro.

## 1. Instal·lar Python {#install-python}

1. Descarrega Python 3.10 o posterior des de <https://www.python.org/downloads/>.
2. Executa l'instal·lador. A la primera pantalla marca **Add python.exe to PATH**,
   i després fes clic a **Install Now**.
3. Comprova-ho: obre una terminal (pas 3) i escriu `python --version`. Hauries de veure
   `Python 3.` i un número 10 o superior.

A Linux o macOS, Python sol estar ja instal·lat: fes servir `python3` on aquestes pàgines
diuen `python`.

## 2. Obtenir 3DHeat CS2 {#get-3dheat-cs2}

Descarrega el zip de la [pàgina de versions](https://github.com/Holdi601/3DHeat-CS2/releases) i
descomprimeix'l, per exemple a `C:\Eines\3DHeat-CS2`. (Si té Git, `git clone` també funciona.)

## 3. Obrir una terminal en aquesta carpeta {#open-a-terminal-in-that-folder}

- **Windows:** obre la carpeta a l'Explorador de fitxers, fes clic a la barra d'adreces, escriu
  `powershell` i prem Intro. S'obre una finestra blava o negra, ja en aquesta carpeta.
- **macOS / Linux:** obre *Terminal* i escriu `cd ` (amb un espai), arrossega la
  carpeta a la finestra, i prem Intro.

`cd <carpeta>` mou la terminal a una altra carpeta. Totes les ordres d'aquestes
pàgines s'escriuen a la carpeta de l'eina.

## 4. Instal·lar el que necessita {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Al final hauries de veure `Successfully installed ...` (o `Requirement
already satisfied`).

## 5. Comprovar que funciona {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Hauries de veure: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Com llegir les ordres d'aquestes pàgines {#how-to-read-the-commands-on-these-pages}

- Les paraules entre `<angles>` són marcadors de posició: escriu el seu propi fitxer o carpeta en
  lloc seu, sense els angles. `python -m heat3d_cs2 demos <fitxers de demo o carpetes> -o out` vol dir
  que substitueixi la part entre angles.
- Una ruta amb espais va entre cometes: `"C:\My Games\my file"`.
- Les línies que comencen amb `#` als exemples són comentaris; no els escriu.
- Un èxit té aquest aspecte: després de `demos`, una línia `1 match(es), 1 at a time` i després una línia per
  partida que acaba amb `lost 0`.

## Errors habituals {#common-errors}

| Veu | Què fer |
|---|---|
| `'python' is not recognized` o `command not found` | Python no és al PATH: torna a executar l'instal·lador i marca **Add python.exe to PATH**, i després obre una terminal nova. A macOS/Linux prova `python3`. |
| `No module named ...` | s'ha saltat el pas 4 o s'ha executat en una altra carpeta: fes `cd` a la carpeta de l'eina i torna-la a executar. |
| `pip is not recognized` | fes servir `python -m pip ...` en lloc de `pip ...`. |
| `No such file or directory` / `can't open file` | la terminal és a la carpeta equivocada, o la ruta està mal escrita: comprova-la, i posa entre cometes les rutes amb espais. |
| text vermell que acaba en una línia `error:` | llegeix l'última línia: diu què falta. La pàgina [Ordres](../commands.md) enumera els missatges. |
