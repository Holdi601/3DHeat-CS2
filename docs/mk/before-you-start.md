---
title: Пред да започнете
nav_order: 2
lang: mk
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Пред да започнете {#before-you-start}

Нови сте со командната линија? Оваа страница ве води од нула до 3DHeat CS2 што работи за
околу десет минути. Пишувате команди во *терминал*, прозорец
во кој пишувате линија и притискате Enter.

## 1. Инсталирајте Python {#install-python}

1. Преземете Python 3.10 или понов од <https://www.python.org/downloads/>.
2. Пуштете го инсталерот. На првиот екран штиклирајте **Add python.exe to PATH**,
   а потоа кликнете **Install Now**.
3. Проверете: отворете терминал (чекор 3) и напишете `python --version`. Треба да
   видите `Python 3.` и број 10 или повеќе.

На Linux или macOS, Python обично веќе е инсталиран: користете `python3` таму каде што
овие страници велат `python`.

## 2. Преземете го 3DHeat CS2 {#get-3dheat-cs2}

Преземете го zip-от од
[страницата со изданија (Releases)](https://github.com/Holdi601/3DHeat-CS2/releases) и распакувајте го, на
пример во `C:\Tools\3DHeat-CS2`. (Ако имате Git, работи и `git clone`.)

## 3. Отворете терминал во таа папка {#open-a-terminal-in-that-folder}

- **Windows:** отворете ја папката во File Explorer, кликнете во адресната лента, напишете
  `powershell` и притиснете Enter. Се отвора син или црн прозорец, веќе во
  таа папка.
- **macOS / Linux:** отворете *Terminal* и напишете `cd ` (со празно место), повлечете ја
  папката во прозорецот, притиснете Enter.

`cd <folder>` го преместува терминалот во друга папка. Сите команди на овие
страници се пишуваат во сопствената папка на алатката.

## 4. Инсталирајте што му треба {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

На крајот треба да видите `Successfully installed ...` (или `Requirement
already satisfied`).

## 5. Проверете дали работи {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Треба да видите: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Како да ги читате командите на овие страници {#how-to-read-the-commands-on-these-pages}

- Зборовите во `<аголни загради>` се места за пополнување: напишете своја датотека или папка
  наместо нив, без заградите. `python -m heat3d_cs2 demos <demo files or folders> -o out` значи
  дека го заменувате делот во заградите.
- Патека со празни места оди во наводници: `"C:\My Games\my file"`.
- Линиите што почнуваат со `#` во примерите се коментари; не ги пишувате.
- Успехот изгледа вака: по `demos`, линија `1 match(es), 1 at a time` и потоа по една линија за секој меч што завршува со `lost 0`.

## Чести грешки {#common-errors}

| Што гледате | Направете го ова |
|---|---|
| `'python' is not recognized` или `command not found` | Python не е во PATH: пуштете го инсталерот повторно и штиклирајте **Add python.exe to PATH**, потоа отворете нов терминал. На macOS/Linux обидете се со `python3`. |
| `No module named ...` | чекор 4 е прескокнат или пуштен во друга папка: со `cd` одете во папката на алатката и пуштете го повторно. |
| `pip is not recognized` | користете `python -m pip ...` наместо `pip ...`. |
| `No such file or directory` / `can't open file` | терминалот е во погрешна папка, или патеката е погрешно напишана: проверете ја, и ставете ги патеките со празни места во наводници. |
| црвен текст што завршува со линија `error:` | прочитајте ја последната линија: кажува што недостасува. Страницата [Команди](../commands.md) ги наведува пораките. |
