---
title: Estatísticas
nav_order: 7
lang: "pt"
source: statistics.md
source_hash: "12da70d07058"
nav_exclude: true
search_exclude: true
---
# Estatísticas {#statistics}

O que cada jogador fez numa partida, e como foi cada round: o placar e a lista de rounds do
[documento da partida](output-match-json.md). Código:
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py).
Tudo é contado a partir da partida construída como em [Construir uma partida](building-matches.md): os seus registos de morte, o seu dano (vida perdida, só inimigos), as suas cegueiras (só inimigos) e as
suas linhas.

![o placar em texto de uma partida sintética](../assets/img/scoreboard.svg)

## As convenções {#the-conventions}

Quando o próprio jogo não define um número, estas são as convenções. Estão também escritas em cada
documento da partida, em `conventions`.

| Termo | Definição |
|---|---|
| **Trade** (vingança) | Uma morte é *vingada* quando o seu assassino é morto por um colega da vítima em até **5 s**; essa kill é uma *kill de vingança*. |
| **Abertura** | A primeira kill de um inimigo no round, enquanto está vivo. Um teamkill, um suicídio ou uma morte para o mundo antes disso são ignorados. |
| **KAST** | A fração de rounds em que um jogador fez uma **K**ill, uma **A**ssistência (uma assistência de flash conta), **S**obreviveu, ou foi **T**radado (vingado). |
| **Dano** | Vida efetivamente perdida, só inimigos: um headshot de 137 de dano num jogador com 40 de vida são 40. |
| **Clutch** | Ser o último jogador vivo de um lado com inimigos ainda de pé; ganho quando o lado ganha o round. |
| **Compra** | Por lado, a partir do valor médio do equipamento no fim do tempo de congelamento: o primeiro round de cada metade regulamentar é uma ronda de pistola (o round 1, e o round a seguir à metade, desde que a partida o tenha jogado), o prolongamento não tem nenhuma; depois abaixo de 1.500 $ eco, abaixo de 4.000 $ force, senão full. |

## Quem começou cada round {#who-started-each-round}

Vários números precisam de saber quem jogou um round. Os **jogadores iniciais** de um round são, por
lado, cada jogador com uma linha de posição viva a um segundo do primeiro instante de posição desse
round (ou seja, no primeiro segundo depois de acabar o tempo de congelamento). Os **rounds jogados** de
um jogador são o número de rounds que começou. Se um jogador não começou nenhum (nunca teve tal linha),
usa-se em vez disso a contagem de rounds da partida, para que nunca haja divisão por zero.

## A linha do placar {#the-scoreboard-line}

Uma entrada por jogador (ver [o documento da partida](output-match-json.md#players) para os nomes dos
campos). "Kill de inimigo" abaixo significa uma kill com um atacante, não um teamkill, e não um suicídio
(o suicídio da própria vítima).

| Campo | Conta |
|---|---|
| `kills` | kills de inimigos, da fase live e da fase after |
| `deaths` | cada morte: por inimigos, companheiros, por si próprio ou pelo mundo |
| `assists` | kills de inimigos que este jogador assistiu sem flash (quem assiste não pode ser o assassino) |
| `flashAssists` | kills de inimigos que este jogador assistiu com flash |
| `diff` | kills - mortes |
| `adr` | dano (vida perdida, só inimigos, nas duas fases) / rounds jogados, uma casa decimal |
| `kast` | 100 x (rounds com uma kill, uma assistência ou assistência de flash, sobrevivência ou morte vingada) / rounds jogados, uma casa decimal. *Sobrevivência* é: um jogador inicial do round que não morreu nele, em qualquer das fases. |
| `headshotPct` | 100 x kills com headshot / kills, uma casa decimal; 0 sem kills |
| `openingKills`, `openingDeaths` | duelos de abertura ganhos e perdidos |
| `tradeKills` | kills que vingaram a morte de um colega |
| `tradedDeaths` | mortes que foram vingadas |
| `multiKills` | rounds com 2, 3, 4 e 5 kills de inimigos (`2k`, `3k`, `4k`, `5k`); mais de cinco conta como `5k`. Ambas as fases contam. |
| `clutches`, `clutchesWon` | clutches jogados e ganhos (abaixo) |
| `utilityDamage` | dano causado com granadas HE, molotovs e incendiárias, uma casa decimal |
| `enemiesFlashed` | inimigos cegados durante **pelo menos 1,0 s** pelos flashes deste jogador |
| `plants`, `defuses` | plantas e desativações de bombas (linhas da tabela) |
| `teamkills` | companheiros mortos. Um suicídio - atacante e vítima o mesmo jogador, uma granada própria, por exemplo - não é um: é só uma morte. |
| `roundsPlayed` | rounds começados, como acima |

Os jogadores são listados por nome de equipa (em ordem alfabética), e dentro de uma equipa por
`diff`, depois por `kills`, o melhor primeiro.

Notas sobre os limites:

- Uma kill na fase after - os vencedores a caçar um jogador que poupa - conta como kill, como morte,
  para ADR, multi-kills e KAST, como qualquer outra.
- Os wallbangs são contados por jogador internamente, mas não são escritos no documento da partida; cada
  kill na lista de rounds diz se foi um.
- A parte *vingada* do KAST credita a vítima de uma morte vingada nesse round.
- Os teamkills e os suicídios somam uma morte à vítima mas nenhuma kill a ninguém; um teamkill soma aos
  `teamkills` do assassino, um suicídio não soma a mais nada.

## Clutches {#clutches}

Para cada round, os jogadores iniciais dos dois lados são tomados como vivos, e as kills vivas do round
são percorridas em ordem. Depois de cada morte, a vítima é retirada, e cada lado é verificado: um lado
com exatamente **um** jogador restante, e pelo menos um inimigo ainda vivo, é um clutch para esse jogador
**contra** o número de inimigos vivos naquele momento. Cada jogador tem no máximo um clutch por round; é
**ganho** quando o lado desse jogador ganha o round.

Consequências da definição:

- Os dois lados podem ter um clutch no mesmo round. Se um lado fica primeiro reduzido a um (um 1v3, por
  exemplo) e depois o outro lado também fica reduzido a um, o segundo jogador está num clutch 1v1 próprio.
- `against` é a contagem quando o jogador ficou o último, não no fim.
- As kills da fase after não são percorridas, por isso não iniciam nem alteram um clutch.

## Sobreviventes {#survivors}

Os **sobreviventes** de um round são, por lado, os seus jogadores iniciais menos todos os que morreram
enquanto estava live. Um jogador morto na fase after, enquanto poupava, continua a ser sobrevivente na
lista de rounds - mas não *sobreviveu* para o KAST.

## A lista de rounds {#the-round-list}

Cada round do documento da partida traz o seu resultado, pontuação, lados, economia, planta,
sobreviventes, clutches e as suas kills em ordem; ver
[O documento da partida](output-match-json.md#rounds).

## O placar em texto {#the-text-scoreboard}

`python -m heat3d_cs2 scoreboard <match.json>` imprime estes números por equipa; ver
[Comandos](commands.md#scoreboard---a-match-as-text).
