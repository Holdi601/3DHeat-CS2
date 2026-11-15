---
title: Antes de começar
nav_order: 2
lang: "pt"
source: before-you-start.md
source_hash: "41a5fe42a33a"
nav_exclude: true
search_exclude: true
---
# Antes de começar {#before-you-start}

Nunca usou a linha de comando? Esta página leva do zero até um 3DHeat CS2
funcionando em cerca de dez minutos. Escrevem-se comandos num *terminal*, uma janela
onde se escreve uma linha e se prime Enter.

## 1. Instalar o Python {#install-python}

1. Transfira o Python 3.10 ou mais recente em <https://www.python.org/downloads/>.
2. Execute o instalador. No primeiro ecrã, marque **Add python.exe to PATH**,
   depois clique em **Install Now**.
3. Verifique: abra um terminal (passo 3) e escreva `python --version`. Deve aparecer
   `Python 3.` e um número 10 ou maior.

No Linux ou no macOS, o Python geralmente já está instalado: use `python3` onde
estas páginas dizem `python`.

## 2. Obter o 3DHeat CS2 {#get-3dheat-cs2}

Transfira o zip na [página de lançamentos](https://github.com/Holdi601/3DHeat-CS2/releases) e descompacte-o,
por exemplo em `C:\Ferramentas\3DHeat-CS2`. (Se tiver o Git, `git clone` também funciona.)

## 3. Abrir um terminal nessa pasta {#open-a-terminal-in-that-folder}

- **Windows:** abra a pasta no Explorador de Ficheiros, clique na barra de endereço, escreva
  `powershell` e prima Enter. Abre uma janela azul ou preta, já nessa
  pasta.
- **macOS / Linux:** abra o *Terminal* e escreva `cd ` (com um espaço), arraste a
  pasta para a janela, prima Enter.

`cd <pasta>` move o terminal para outra pasta. Todos os comandos destas páginas são
escritos na própria pasta da ferramenta.

## 4. Instalar o que ela precisa {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Deve aparecer `Successfully installed ...` no final (ou `Requirement
already satisfied`).

## 5. Verificar se funciona {#check-it-works}

```bash
python -m heat3d_cs2 --help
```

Deve aparecer: `usage: heat3d_cs2 [-h] {demos,map,scoreboard} ...`.

## Como ler os comandos destas páginas {#how-to-read-the-commands-on-these-pages}

- Palavras entre `<colchetes angulares>` são marcadores: escreva o seu próprio ficheiro ou pasta
  no lugar, sem os colchetes. `python -m heat3d_cs2 demos <ficheiros de demo ou pastas> -o out` quer dizer
  que se substitui a parte entre colchetes.
- Um caminho com espaços vai entre aspas: `"C:\Meus Jogos\meu ficheiro"`.
- Linhas que começam com `#` nos exemplos são comentários; não as escreve.
- O sucesso tem este aspeto: depois de `demos`, uma linha `1 match(es), 1 at a time` e depois uma linha por
  partida terminando em `lost 0`.

## Erros comuns {#common-errors}

| Aparece | Faça isto |
|---|---|
| `'python' is not recognized` ou `command not found` | O Python não está no PATH: execute o instalador de novo e marque **Add python.exe to PATH**, depois abra um novo terminal. No macOS/Linux tente `python3`. |
| `No module named ...` | o passo 4 foi saltado ou foi executado noutra pasta: use `cd` para ir à pasta da ferramenta e execute de novo. |
| `pip is not recognized` | use `python -m pip ...` em vez de `pip ...`. |
| `No such file or directory` / `can't open file` | o terminal está na pasta errada, ou o caminho está escrito errado: verifique, e coloque entre aspas os caminhos com espaços. |
| texto vermelho que termina numa linha `error:` | leia a última linha: ela diz o que falta. A página [Comandos](commands.md) lista as mensagens. |
