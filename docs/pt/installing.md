---
title: Instalação
nav_order: 3
lang: "pt"
source: installing.md
source_hash: "c7089fd9e2a6"
nav_exclude: true
search_exclude: true
---
# Instalação {#installing}

Não está habituado à linha de comandos? Leia primeiro [Antes de começar](before-you-start.md).

O 3DHeat CS2 é um pacote Python executado a partir da sua própria pasta. Não há nada para compilar
nem instalador; precisa de Python, de quatro pacotes (mais o pytest para os testes) e - só para a
exportação do mapa - do Counter-Strike 2 instalado e da versão de linha de comandos do
Source2Viewer.

## Obter o código {#getting-the-code}

Transfira um ficheiro de uma versão na
[página de versões](https://github.com/Holdi601/3DHeat-CS2/releases) e descompacte-o, ou, se tiver
Git, clone o repositório:

```bash
git clone https://github.com/Holdi601/3DHeat-CS2.git
cd 3DHeat-CS2
```

Os dois tipos de cópia podem atualizar-se sozinhos (ver [Atualizações](updates.md)). A versão
instalada é a linha única do ficheiro `VERSION`.

Execute todos os comandos a partir dessa pasta: `python -m heat3d_cs2` encontra o pacote porque
ele está na pasta atual. O pacote não é instalado em `site-packages`.

## Python e os pacotes {#python-and-the-packages}

Python 3.10 ou mais recente. Um ambiente virtual mantém os pacotes separados do resto. No Windows
(PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell recusar executar o script, execute primeiro
`Set-ExecutionPolicy -Scope Process RemoteSigned` (vale só para essa janela). No Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Funciona quando `python -m heat3d_cs2 --help` imprime `usage: heat3d_cs2 ...`.

`requirements.txt`:

| Pacote | Mínimo | Usado para | Licença |
|---|---|---|---|
| `demoparser2` | 0.42 | ler ficheiros `.dem` (jogadores por tick, eventos do jogo) | MIT |
| `pyarrow` | 15 | escrever a tabela Parquet | Apache-2.0 |
| `pandas` | 2.0 | as tabelas intermediárias | BSD-3-Clause |
| `numpy` | 1.24 | a aritmética sobre elas | BSD-3-Clause |
| `pytest` | 8.0 | só os testes | MIT |

Os comandos `demos` e `scoreboard` não precisam de mais nada.

## Para a exportação do mapa: Counter-Strike 2 e a CLI do Source2Viewer {#for-the-map-export-counter-strike-2-and-source2viewers-cli}

`python -m heat3d_cs2 map` lê o mapa do jogo que tem instalado, e decodifica-o com a **linha de
comandos do Source2Viewer**, um programa separado do projeto
[ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (licença MIT).
Não vem incluído e não se instala com o pip.

1. Transfira a versão **CLI** para o seu sistema em
   [as versões do ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)
   e descompacte-a em qualquer lugar.
2. Faça com que seja encontrada, de uma de três formas. São tentadas por esta ordem:
   1. `--source2viewer <caminho para o executável>` na linha de comandos;
   2. a variável de ambiente `HEAT3D_SOURCE2VIEWER` com o caminho do executável;
   3. um executável chamado `Source2Viewer-CLI` ou `Source2Viewer-CLI.exe` no `PATH`.

   Um candidato só é usado se o caminho existir. Se nenhum for encontrado, o comando para com
   `Source2Viewer-CLI not found: download the command line build for your system from
   https://github.com/ValveResourceFormat/ValveResourceFormat/releases, then put it on PATH, set
   HEAT3D_SOURCE2VIEWER, or pass --source2viewer`.

Definir a variável, por exemplo:

```bash
# Windows (PowerShell), para a sessão atual
$env:HEAT3D_SOURCE2VIEWER = "C:\Ferramentas\Source2Viewer\Source2Viewer-CLI.exe"
# Linux / macOS
export HEAT3D_SOURCE2VIEWER=~/ferramentas/Source2Viewer-CLI
```

### Onde o CS2 é procurado {#where-cs2-is-looked-for}

O mapa é um ficheiro `.vpk` dentro da pasta do jogo:
`<biblioteca do Steam>\steamapps\common\Counter-Strike Global Offensive\game\csgo\maps\<mapa>.vpk`.
As bibliotecas do Steam são encontradas a partir destas raízes, e de cada `"path"` listado em
`config\libraryfolders.vdf` de cada raiz:

- `C:\Program Files (x86)\Steam`
- `C:\Program Files\Steam`
- `~/.steam/steam`
- `~/.local/share/Steam`

Quando o Steam está noutro lugar, indique a própria pasta do CS2 com `--game` (a pasta que contém
`game\csgo`), ou indique o caminho do `.vpk` em vez do nome do mapa. Ver
[Exportar o mapa](map-export.md).

## Verificar a instalação {#checking-the-install}

```bash
python -m heat3d_cs2 --help
python -m pytest
```

Os testes correm numa demo sintética construída no código e não precisam de demo, jogo nem
Source2Viewer (ver [Desenvolvimento](development.md)).

Cada inicialização de `python -m heat3d_cs2` verifica primeiro, no máximo a cada seis horas, se há uma
versão mais recente; defina `HEAT3D_NO_UPDATE=1` para desligar isso (ver
[Atualizações](updates.md)).
