---
title: Desenvolvimento
nav_order: 15
lang: "pt"
source: development.md
source_hash: "b51f038901ee"
nav_exclude: true
search_exclude: true
---
# Desenvolvimento {#development}

## Estrutura {#layout}

| Caminho | O quê |
|---|---|
| [`heat3d_cs2/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/__main__.py) | `python -m heat3d_cs2`: a verificação de versão e depois a linha de comandos |
| [`heat3d_cs2/cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/cli.py) | os verbos e as opções; o agrupamento dos ficheiros de demo em partidas; o conjunto de trabalhadores |
| [`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py) | um ficheiro de demo através do demoparser2 para um `RawPart` - [Ler uma demo](reading-demos.md) |
| [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py) | partes, cadeias, o relógio, rounds, equipas, linhas, mortes, dano, cegueiras - [Construir uma partida](building-matches.md) |
| [`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py) | resumos de rounds, o placar, o documento da partida, o placar em texto - [Estatísticas](statistics.md) |
| [`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py) | a tabela Parquet com as suas indicações `heat3d`, e o JSON - [A tabela de calor](output-table.md) |
| [`heat3d_cs2/mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/mapexport.py) | encontrar o CS2 e o Source2Viewer, a malha de colisão no referencial do visualizador - [Exportar o mapa](map-export.md) |
| [`heat3d_cs2/glb.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/glb.py) | um leitor e escritor mínimo de glTF binário (sem outra dependência além do numpy) |
| [`heat3d_update/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/heat3d_update) | a verificação de versão e o atualizador - [Atualizações](updates.md) |
| [`tests/`](https://github.com/Holdi601/3DHeat-CS2/tree/main/tests) | os testes e a demo sintética |
| `VERSION` | a versão, numa linha |

O fluxo de dados:

```text
ficheiros .dem --demo.read_part--> RawPart --match.chains--> [RawPart, ...] por partida
          --match.build_match--> Match (rounds, jogadores, equipas, linhas, mortes, dano, cegueiras)
          --output.write--> <mapa>/<partida>.parquet  (output.table + HINTS)
                            <mapa>/<partida>.match.json (stats.summary)
<mapa>.vpk --CLI do Source2Viewer--> .glb world_physics --mapexport.parts_from--> glb.write
```

### Usar a partir do Python {#using-it-from-python}

```python
from heat3d_cs2.demo import read_part
from heat3d_cs2.match import build_match, chains
from heat3d_cs2.stats import summary, player_stats
from heat3d_cs2.output import write

raws = [read_part(p, every=8) for p in ["alpha-vs-bravo-m1-p1.dem", "alpha-vs-bravo-m1-p2.dem"]]
for k, chain in enumerate(chains(raws)):
    match = build_match(chain, "alpha-vs-bravo-m1" if k == 0 else f"alpha-vs-bravo-m1-{chr(97 + k)}")
    rows = match.rows          # a tabela de calor como um DataFrame do pandas
    kills = match.kills        # uma linha por morte, com todas as marcas
    doc = summary(match)       # o documento .match.json como um dicionário
    write(match, "out/" + match.map)
```

`Match.kills`, `Match.damage` e `Match.blinds` são DataFrames do pandas com mais do que as saídas
trazem - posições e lugares do atacante e da vítima em cada morte, `utility` em cada golpe - para
análises próprias.

## Testes {#tests}

```bash
python -m pytest
```

`pytest.ini` corre `tests/` em silêncio. Os testes não precisam de nenhuma demo, jogo nem
Source2Viewer: [`tests/fixtures.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/fixtures.py)
constrói uma demo manualmente, tal como o demoparser2 a daria - dois rounds, dois jogadores por lado
(`ace`, `ash` da equipa Alpha; `bob`, `ben` da Bravo), pequena o suficiente para que cada resposta
seja conhecida:

- Round 1, vitória T por eliminação: ace mata bob com um headshot (a abertura), ben mata ace 1,9 s
  depois (uma troca: a morte de bob é vingada), ash mata ben 3,1 s depois disso - sozinho contra
  um, um clutch ganho.
- Round 2, vitória T pela bomba: ash planta em A, ninguém morre, a bomba explode.

`fixtures.halves` constrói uma partida mais longa de rounds vazios, as equipas nos seus primeiros
lados ou trocadas, com a contagem de prolongamento do jogo ou sem ela, para o comprimento da
metade e as rondas de pistola.

[`tests/test_match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_match.py)
verifica nela: o vencedor, o motivo, o resultado e os lados de cada round; o relógio a começar na
partida; a economia e a planta (o seu tempo dentro do round, o seu lugar, a bomba a explodir); o
local de uma planta é sempre uma letra ou vazio, nunca um número de entidade; um empate decidido
sem vencedor; as rondas de pistola a partir de onde os lados trocam, o prolongamento deixado de
fora, e só o round 1 sem troca; equipas sem nomes de clã (`Started T` / `Started CT`); aberturas,
trocas e marcas; um suicídio que não é teamkill, e a abertura passada para a primeira morte de um
inimigo; `noscope` e `attackerBlind` na tabela e no documento da partida; o dano como vida perdida
(60, depois 40 de um 137 com 40 de vida); os números do placar e o KAST; os clutches; o placar em
texto; os eventos da tabela e onde estão (uma detonação sem lugar próprio, o do lançador em
`throwerPlace`; a explosão da equipa que plantou); que as posições são vivas, têm rótulo e
vetores de olhar unitários; que o ficheiro escrito traz as suas indicações; partes postas em ordem, quaisquer que sejam os seus nomes; um relógio de servidor reiniciado que continua; e as
linhas duplicadas de um round restaurado resolvidas para a que segue em frente.

[`tests/test_cli.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_cli.py) verifica
que as demos dentro de pastas são encontradas, seja qual for a maiúscula de `.dem`, e que uma
partida só conta como escrita com a sua tabela e o seu documento de partida.

[`tests/test_mapexport.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/tests/test_mapexport.py)
verifica as conversões de referencial (os metros do Source2Viewer para as polegadas do jogo, e daí
para o referencial do visualizador, uma rotação com determinante 1), que os clips e o céu ficam de
fora seja qual for a maiúscula e os nomes das superfícies, a divisão chão/estrutura pela normal, e
um `.glb` escrito e lido de volta.

### A verificação do chão num mapa real {#the-floor-check-on-a-real-map}

```bash
HEAT3D_CS2_DEMO=<uma demo> HEAT3D_SOURCE2VIEWER=<a CLI> python -m pytest
```

Com as duas variáveis definidas, também corre `test_players_stand_on_the_exported_floor`: converte
a demo, exporta o mapa do jogo instalado, e verifica que pelo menos 98% de 300 amostras aleatórias
de posição têm chão por baixo, com uma altura mediana acima dele inferior a 5 unidades
([Exportar o mapa](map-export.md#the-check-that-the-frame-is-right)).

## Convenções do código {#conventions-of-the-code}

- Os tempos dentro de `match.py` são segundos de partida, exceto o `time` de uma planta, segundos
  dentro do seu round tal como o documento da partida o escreve; os ticks só se tornam segundos
  através de `_Part.at`.
- Os lados são as strings `T` / `CT` em todo o lado, fora dos dados do analisador bruto
  (`team_num` 2 / 3).
- Uma nova coluna da tabela vai para `ROW_COLUMNS` (e para `NUMERIC` se for numérica) em `match.py`;
  `output.table` escolhe o seu tipo Parquet a partir dos conjuntos `INT16`, `INT32`, `FLOAT64` e
  das marcas 0/1, float32 no resto.
- Mudar o que o visualizador deve fazer com uma coluna significa mudar `HINTS` em `output.py`.

## Licença {#licence}

MIT. Pacotes de terceiros:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-CS2/blob/main/LICENSES.md).
As demos e os mapas nunca fazem parte do repositório; o seu `.gitignore` mantém fora, pelo tipo,
`*.dem`, `*.parquet`, `*.match.json`, `*.glb` e similares.
