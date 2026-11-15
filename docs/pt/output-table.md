---
title: A tabela de calor
nav_order: 8
lang: "pt"
source: output-table.md
source_hash: "b235ff13fe45"
nav_exclude: true
search_exclude: true
---
# A tabela de calor (`<partida>.parquet`) {#the-heatmap-table-parquet}

Um ficheiro Parquet por partida: a posição amostrada de cada jogador vivo, e cada evento no lugar e
momento em que aconteceu, uma linha cada - uma tabela longa que o visualizador 3DHeat lê como mapa de
calor, e qualquer outra coisa como uma tabela normal. Código:
[`heat3d_cs2/output.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/output.py)
(o ficheiro), [`heat3d_cs2/match.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/match.py)
(as linhas; ver [Construir uma partida](building-matches.md)).

O ficheiro é escrito com compressão Snappy em grupos de linhas de 256.000 linhas. As linhas são
ordenadas por `time`, e depois por `event`. Só ficam dentro dele as linhas que estão dentro de um round
(do fim do tempo de congelamento do round até ao início do round seguinte).

Na demo sintética dos testes, as linhas de evento do primeiro round:

![linhas de evento da tabela](../assets/img/table-rows.svg)

Num contentor `.3dheat`, a tabela é o membro com o papel `table`
([Um ficheiro por partida](output-container.md)).

## Colunas {#columns}

As colunas, sempre nesta ordem. As colunas de texto são strings codificadas por dicionário
(`dictionary<int32, string>`) e nunca são nulas: "sem valor" é uma string vazia. As colunas numéricas
são nulas onde uma linha não tem valor.

| Coluna | Tipo | O quê |
|---|---|---|
| `match` | texto | o nome da partida (`alpha-vs-bravo-m1`, ou `...-b` para uma segunda cadeia) |
| `map` | texto | o mapa, do cabeçalho da demo (`de_x`) |
| `round` | int16 | o número do round, a partir de 1 |
| `roundId` | texto | `<partida> #NN`, o número do round com dois dígitos (`alpha-vs-bravo-m1 #07`): único entre partidas, a sessão do visualizador |
| `phase` | texto | `freeze` no tempo de congelamento do round (desde o fim do round anterior), `live` até ao round ser decidido, `after` enquanto os vencedores caçam e os perdedores poupam |
| `time` | float64 | segundos desde o início da partida (o início vivo do seu primeiro ficheiro), num só relógio para os seus ficheiros |
| `roundTime` | float32 | segundos desde que acabou o tempo de congelamento deste round; negativo no tempo de congelamento |
| `event` | texto | o que a linha é - ver [Eventos](#events) |
| `player` | texto | o nome do jogador (para cada evento, qual jogador está abaixo) |
| `steamid` | texto | o Steam ID do jogador (64 bits, como texto) |
| `side` | texto | `T` ou `CT` neste round; vazio quando o jogador não estava em nenhum lugar |
| `team` | texto | o nome da equipa do jogador (ou `Started T` / `Started CT`); para `explode`, a equipa que plantou |
| `x`, `y`, `z` | float32 | posição nas coordenadas do próprio jogo: polegadas (unidades do jogo), **Z para cima**, de mão direita |
| `dirX`, `dirY`, `dirZ` | float32 | para onde o jogador olha, um vetor unitário no mesmo referencial; só posições |
| `health` | int16 | 0-100; posições, e em `hurt` o que sobrou depois do golpe |
| `armor` | int16 | 0-100; posições, e em `hurt` o que sobrou depois do golpe |
| `money` | int32 | o dinheiro do jogador; só posições |
| `equipment` | int32 | o valor do que o jogador transporta; só posições |
| `weapon` | texto | a arma tal como o jogo a chama (`AK-47`, `M4A1-S`, `Knife` para qualquer skin de faca) |
| `place` | texto | o nome de lugar do próprio mapa na posição da linha (`BombsiteA`, `CTSpawn`); vazio nas detonações de granadas: a demo não dá nome de lugar ao lugar onde a granada explodiu |
| `throwerPlace` | texto | o nome do lugar de quem lançou quando a granada explodiu; só detonações de granadas |
| `other` | texto | o outro jogador de uma morte, kill, golpe ou flash |
| `damage` | float32 | vida perdida; só `hurt` |
| `duration` | float32 | segundos cegado; só `blind` |
| `headshot` | int8 | 0/1; só `kill` e `death` |
| `opening` | int8 | 0/1, a primeira kill de um inimigo no round; só `kill` e `death` |
| `traded` | int8 | 0/1. Para um `kill`: foi uma kill de vingança. Para um `death`: foi vingada em menos de 5 s. Só `kill` e `death`. |
| `noscope` | int8 | 0/1, a kill foi com uma arma com mira disparada sem mira (o `noscope` do evento); só `kill` e `death` |
| `attackerBlind` | int8 | 0/1, quem matou estava cegado por um flash quando matou (o `attackerblind` do evento); só `kill` e `death` |
| `won` | int8 | 0/1, se o lado desta linha ganhou o round; nulo quando `side` está vazio |
| `buy` | texto | a compra do lado desta linha neste round: `pistol`, `eco`, `force`, `full` |
| `detail` | texto | cada campo do evento que as outras colunas não guardam, como um objeto JSON (os nomes do próprio jogo): as balas de um tiro (`fire_bullets`: origem, ângulos, imprecisão, dispersão, índice de recuo, semente...), o `dominated`, `revenge`, `attackerinair`, `wipe`... de uma morte, o `defindex` de um item, um passo sem nada |
| `text` | texto | uma linha de chat; só `chat` |
| `entity` | int32 | a entidade da granada: o voo de um `throw` (linhas `grenade`), a sua detonação e os jogadores que cegou partilham essa |
| `hitgroup` | texto | onde a bala atingiu (`head`, `chest`, ...); `hurt`, `kill`, `death` |
| `armorDamage` | int16 | colete perdido; só `hurt` |
| `hitLocalX`, `hitLocalY`, `hitLocalZ` | float32 | onde no corpo a bala atingiu, no referencial da vítima em metros (x para a frente, y para cima a partir dos pés, z para a direita): o raio do tiro (`fire_bullets`, senão o olho e a vista do atacante) traçado até um corpo na posição em que a vítima estava de pé e agachada, até a parte que `hitgroup` nomeia; só `hurt` |
| `hitDirX`, `hitDirY`, `hitDirZ` | float32 | a direção do tiro no mesmo referencial; `hitMiss` a que distância (m) o raio passou ao lado da parte nomeada (0: passou por ela); `hitFrom` `bullet` ou `aim` |
| `penetrated` | int16 | paredes que a bala mortal atravessou; `kill` e `death` |
| `throughSmoke` | int8 | 0/1, morto através de fumo; `kill` e `death` |
| `distance` | float32 | a distância da kill tal como o jogo a conta (metros); `kill` e `death` |
| `assister` | texto | quem assistiu; `kill` e `death` |
| `flash`, `flashAlpha` | float32 | segundos de flash que restam, e quão branco; posições |
| `helmet`, `defuser`, `scoped`, `walking`, `airborne`, `buyZone`, `bombZone`, `defusing`, `spotted` | int8 | 0/1; posições |
| `zoom`, `duck`, `moveType` | | o nível de zoom da mira, quão agachado (0-1), o tipo de movimento do jogo; posições |
| `spottedBy` | texto | os Steam IDs dos inimigos que veem este jogador, separados por `\|`; posições |
| `inventory` | texto | tudo o que o jogador transporta, separado por `\|`; posições |
| `ammo`, `ammoReserve`, `shotsFired` | int16 | o carregador e a reserva da arma na mão; tiros na rajada atual; posições |
| `punchPitch`, `punchYaw` | float32 | o impulso de mira do recuo, em graus; posições |
| `ping` | int16 | milissegundos; posições |
| `killsTotal`, `deathsTotal`, `assistsTotal`, `headshotKillsTotal`, `damageTotal`, `utilityDamageTotal`, `enemiesFlashedTotal`, `objectiveTotal`, `aceRoundsTotal`, `threeKillRoundsTotal`, `aliveTimeTotal`, `moneySavedTotal`, `mvps`, `score` | int | as contagens próprias do placar do jogo para a partida até agora; posições |
| `cashSpent`, `cashSpentTotal`, `roundStartEquipment` | int32 | dinheiro gasto neste round e na partida; valor do equipamento quando o round começou; posições |
| `state_helmet`, `state_defuser`, `state_kevlar`, `state_scoped`, `state_flashed` | int8 | 0/1, o estado do jogador no tempo da linha, eventos incluídos: capacete, kit de desarme, qualquer colete, com mira (desde a última amostra de posição do jogador até a linha), cegado (dentro de um `blind` que o atingiu); cada linha que nomeia um jogador |
| `state_utility` | int16 | granadas transportadas no momento (de `inventory`); cada linha que nomeia um jogador |
| `state_weapon` | texto | a arma na mão no momento (numa `death`, a da própria vítima, onde `weapon` é a do assassino); cada linha que nomeia um jogador |
| `earn_round_cs2` | int16 | o que o round pagou: em `round_end` o prémio de vitória ou o bónus de derrota (com o bónus do lado que plantou), em `plant` e `defuse` os 300 do jogador |

## Eventos {#events}

Qual jogador uma linha nomeia, onde está, e que colunas preenche.
`match`, `map`, `round`, `roundId`, `phase`, `time`, `roundTime`, `event`, `won` e `buy` são preenchidos
em todas as linhas; `inventory`, `money`, `equipment` e as colunas `state_*` em cada linha que nomeia um
jogador (os eventos as tiram da última amostra de posição do jogador).

| `event` | `player` / `side` / `team` | `x`, `y`, `z` | Também preenchido |
|---|---|---|---|
| `position` | o jogador | o jogador (pés) | `dirX`-`dirZ`, `health`, `armor`, `money`, `equipment`, `weapon` (na mão), `place`, e todo o estado do jogador (as colunas a partir de `flash`) - também no tempo de congelamento |
| `kill` | quem matou | onde estava quem matou | `other` (vítima), `weapon`, `headshot`, `opening`, `traded` (uma kill de vingança), `noscope`, `attackerBlind`, `place` |
| `death` | a vítima | onde a vítima caiu | `other` (quem matou; vazio para o mundo), `weapon`, `headshot`, `opening`, `traded` (vingada), `noscope`, `attackerBlind`, `place` |
| `hurt` | a vítima | onde a vítima foi atingida | `other` (atacante), `damage`, `health`, `armor`, `armorDamage`, `hitgroup`, `weapon`, `place` - também os golpes de companheiros e do mundo |
| `shot` | quem disparou | de onde o tiro foi disparado | `weapon`, `place`, `detail` (o relato do jogo sobre as balas) |
| `slash` | o jogador | onde uma faca foi movida | `weapon` = `Knife` |
| `grenade` | quem lançou | a granada em voo, à amostragem dos jogadores e onde parou | `weapon` (a granada), `entity` |
| `throw` | quem lançou | de onde a granada foi lançada | `weapon` (a granada), `place` |
| `smoke`, `flash`, `he`, `molotov`, `decoy` | quem lançou | onde explodiu | `weapon`, `throwerPlace` (o lugar de quem lançou naquele momento); `place` fica vazio |
| `blind` | o jogador flashado | onde estava | `other` (quem flashou), `duration`, `weapon` = `Flashbang`, `entity`, `place` - companheiros flashados também |
| `plant` | quem plantou | onde plantou | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `defuse` | quem desativou | onde desativou | `weapon` = `C4 Explosive`, `place`, `earn_round_cs2` (300) |
| `round_end` | cada jogador que jogou o round | onde o jogador esteve por último | `won`, `earn_round_cs2` (o que o round lhe pagou: a subida do dinheiro do lado até ao próximo tempo de congelamento onde as regras o permitem, senão as próprias regras), `detail` (`winner`, `reason`, `lossBonus`, `plant`) |
| `explode` | quem plantou (com o seu Steam ID), lado `T`, a equipa que plantou | a posição da planta | `weapon` = `C4 Explosive`, `place` (o do plantador na planta: onde a bomba ficou); o seu tempo é quando a bomba explodiu |
| `chat` | quem enviou | onde estava | `text` |
| cada outro evento do jogo sobre um jogador, com o nome do jogo: `item_pickup`, `item_equip`, `player_footstep`, `player_jump`, `weapon_reload`, `weapon_zoom`, `player_spawn`, `bomb_beginplant`, `bomb_begindefuse`, `bomb_dropped`, `bomb_pickup`, `bomb_exploded`, `smokegrenade_expired`, `inferno_expire`, `decoy_started`, `player_team`, `player_disconnect`, ... | o jogador | onde estava (um evento de granada: onde estava a granada) | `weapon` (de um item), `entity`, `detail` (cada campo do evento) |

O que está e o que não está:

- As linhas **position** são jogadores vivos num lado, fora do tempo de congelamento e do aquecimento,
  a cada `--every` ticks (oito por segundo por padrão).
- As linhas **kill** são só kills por um inimigo - nenhum teamkill, suicídio ou morte para o mundo. As
  linhas **death** são todas as mortes, incluindo essas.
- As linhas **explode** são todas as bombas plantadas que explodiram, pelo `bomb_exploded` da demo: também
  na fase after, quando os Ts já tinham ganho por eliminação. Uma demo sem esse evento tem uma para cada
  round ganho pela bomba, no fim do round.
- As linhas **hurt** e **blind** são só entre inimigos.
- **shot** deixa de fora facas e o C4; as granadas são linhas **throw**.
- **molotov** cobre molotovs e incendiárias (o início do fogo).
- O dano de companheiros, os flashes de companheiros e de espectadores, os eventos do tempo de
  congelamento e tudo o que está entre rounds não estão na tabela.

Um exemplo trabalhado, da demo sintética dos testes (um fumo lançado, uma abertura com headshot,
vinganças):

| time | roundTime | event | player | side | x | y | weapon | other | damage | headshot | opening | traded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18.75 | 8.75 | throw | ash | T | 120 | 10 | Smoke Grenade | | | | | |
| 19.84 | 9.84 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 60 | | | |
| 20.00 | 10.00 | death | bob | CT | -500 | -300 | AK-47 | ace | | 1 | 1 | 1 |
| 20.00 | 10.00 | hurt | bob | CT | -500 | -300 | AK-47 | ace | 40 | | | |
| 20.00 | 10.00 | kill | ace | T | 100 | 0 | AK-47 | bob | | 1 | 1 | 0 |
| 20.16 | 10.16 | smoke | ash | T | 50 | 60 | Smoke Grenade | | | | | |
| 21.88 | 11.88 | death | ace | T | 100 | 0 | AK-47 | ben | | 0 | 0 | 1 |
| 21.88 | 11.88 | kill | ben | CT | -520 | -320 | AK-47 | ace | | 0 | 0 | 1 |

A morte de bob é vingada pela kill de ace por ben 1,9 s depois (a linha `death` de bob: traded 1; a
linha `kill` de ben: uma kill de vingança, traded 1); o segundo golpe em bob foram 137 de dano com 40 de
vida, por isso conta 40.

## As indicações `heat3d` no rodapé {#the-heat3d-footer-hints}

O rodapé Parquet do ficheiro (metadados chave/valor do esquema) traz instruções de leitura sob a chave
**`heat3d`**, um objeto JSON:

```json
{
  "version": 1,
  "kind": "cs2-demo",
  "axes": {"up": "z", "flipX": false, "flipY": true, "flipZ": false, "scale": 1},
  "entity": {"size": 32},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player",
    "teamId": "side",
    "sessionId": "roundId",
    "lookMode": "vector", "dirX": "dirX", "dirY": "dirY", "dirZ": "dirZ",
    "extra": ["event", "match", "round", "roundTime", "phase", "weapon", "place", "won", "buy", "opening", "team"]
  }
}
```

| Entrada | Diz |
|---|---|
| `version`, `kind` | a versão das indicações (1) e o que as escreveu (`cs2-demo`) |
| `axes.up` | o Z do ficheiro é para cima |
| `axes.flipY` | negar o Y do ficheiro (ver abaixo) |
| `axes.scale` | 1: as posições são usadas tal como estão, em unidades do jogo |
| `entity.size` | um jogador tem **32 unidades** de largura - a largura do jogador de CS2 - o tamanho que um replay em caixa desenha |
| `columns.x` / `y` / `z` | as colunas de posição |
| `columns.time`, `timeUnit` | `time`, em segundos |
| `columns.personId` | o jogador é a pessoa |
| `columns.teamId` | o lado é o grupo (por isso T e CT, não os nomes das equipas, colorem os grupos) |
| `columns.sessionId` | cada round (`roundId`) é uma sessão |
| `columns.lookMode` e `dirX`-`dirZ` | a direção do olhar é um vetor nessas colunas |
| `columns.extra` | as colunas a manter como filtros, em ordem de utilidade |

Um visualizador que conhece a chave abre o ficheiro sem nada para definir. Qualquer outro ignora-a. Para
a ler por si:

```python
import json
import pyarrow.parquet as pq

table = pq.read_table("out/de_x/alpha-vs-bravo-m1.parquet")
hints = json.loads(table.schema.metadata[b"heat3d"])
rows = table.to_pandas()
kills = rows[rows["event"] == "kill"]
```

## Eixos e unidades {#axes-and-units}

As coordenadas são as do próprio jogo: **polegadas** (uma unidade do jogo; um jogador tem 72 unidades
de altura de pé e 32 de largura), **Z para cima**, e de mão direita.

Um visualizador cujo mundo tem Y para cima precisa desenhar o (x, y, z) do jogo como **(x, z, -y)** - Z
passa a ser a altura e Y é negado. É uma rotação, não um espelho. Desenhado à maneira de um mundo Z para
cima esquerdo, como (x, z, y), cada mapa sai espelhado, com o lugar A do lado errado; `flipY: true` é o
que as indicações dizem para o evitar. A [exportação do mapa](map-export.md) escreve a sua geometria já
no referencial (x, z, -y), nas mesmas unidades, por isso fica por baixo da tabela sem nenhum ajuste.

As distâncias no visualizador são rotuladas em metros; com escala 1 são unidades do jogo. Multiplique por
0,0254 para metros.

## Tamanho {#size}

As posições dominam: cerca de dez jogadores x 8 amostras por segundo de jogo ao vivo com o `--every 8`
padrão, menos para jogadores mortos e tempo de congelamento. Reduzir `--every` para metade duplica-as;
os eventos não são afetados.
