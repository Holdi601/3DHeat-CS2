---
title: Atualizações
nav_order: 14
lang: "pt"
source: updates.md
source_hash: "de8097a8303d"
nav_exclude: true
search_exclude: true
---
# Atualizações {#updates}

O 3DHeat CS2 mantém-se atualizado com as [versões do GitHub](https://github.com/Holdi601/3DHeat-CS2/releases)
deste repositório. Código:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## A verificação ao iniciar {#the-check-at-start-up}

Cada `python -m heat3d_cs2 ...` pergunta primeiro se há uma versão mais recente, antes sequer de ler os
seus argumentos:

1. A versão instalada é o ficheiro `VERSION` na raiz do repositório (`0` se não puder ser lido).
2. A versão mais recente é pedida a
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, com um limite de **5 segundos**. A
   resposta fica em cache durante **6 horas** em
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (em sistemas sem `LOCALAPPDATA`:
   `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), por isso o pedido é feito no máximo a cada seis horas.
   "Nada publicado ainda" (HTTP 404) fica em cache como uma resposta. Sem conexão, com limite de pedidos,
   atrás de um proxy - qualquer outra falha - a ferramenta continua com a versão que tem, e nada fica em
   cache.
3. As versões são comparadas como números: `v1.2.3` e `1.2.3` são iguais; tudo depois de um `-` ou `+` é
   ignorado; partes em falta contam como 0.

Quando há uma versão mais recente, diz-o no canal de erros:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- Num terminal (tanto a entrada como o canal de erros são terminais) pergunta. Enter, `y`, `yes`, `j` ou
  `ja` atualiza; qualquer outra coisa continua sem alterações. Depois de uma atualização, **o mesmo comando
  volta a correr**, com o código novo.
- Sem terminal - uma execução agendada, um pipe - só imprime onde atualizar e continua:
  `Run python -m heat3d_update in <pasta> to update.`

`HEAT3D_NO_UPDATE=1` desliga a verificação. Qualquer valor diferente de vazio, `0`, `false` ou `no` conta
como ligado.

## Atualizar a pedido {#updating-on-request}

```bash
python -m heat3d_update            # atualiza para a versão mais recente
python -m heat3d_update --check    # diz apenas se há uma nova
```

Isto pergunta sempre ao GitHub (a cache não é usada). Imprime `Up to date: <versão>.`,
`No release found (this is <versão>); offline, or nothing published yet.`, ou
`<nova> is out (this is <atual>): <url>` e depois atualiza (a não ser com `--check`). Código de saída `1`
quando uma atualização foi tentada e falhou, `0` nos outros casos.

## Como uma atualização é aplicada {#how-an-update-is-applied}

Depende de como a cópia foi instalada:

- **Uma cópia com git** (há um `.git` na raiz e `git` no `PATH`): `git pull --ff-only`. É recusada enquanto
  os ficheiros controlados tiverem alterações locais ("this checkout has local changes; commit or stash
  them, then run `git pull`"): são trabalho de alguém, e uma atualização não decide o que lhes acontece.
  Os ficheiros não controlados não bloqueiam.
- **Uma cópia transferida**: o ficheiro de código-fonte da versão (o zipball do GitHub) é transferido e
  descompactado para uma pasta temporária - as entradas que cairiam fora dela são saltadas - e o seu
  `VERSION` precisa ser a versão que a versão declara, senão nada é alterado ("the archive is version X,
  not Y"). Depois os seus ficheiros são copiados por cima da pasta. Os ficheiros que não fazem parte da
  versão - as suas demos, saídas, ambiente virtual, tudo o que criou - nunca são tocados. Os módulos
  Python que a versão já não tem são apagados dos pacotes da própria ferramenta (as pastas `heat3d_*`),
  para que um módulo antigo não ofusque o seu substituto.

Se uma atualização falhar, a mensagem é impressa e a ferramenta corre com a versão que tem.
