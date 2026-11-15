---
title: Ler uma demo
nav_order: 5
lang: "pt"
source: reading-demos.md
source_hash: "9b448a145054"
nav_exclude: true
search_exclude: true
---
# Ler uma demo {#reading-a-demo}

O que se tira de um ficheiro `.dem`, antes de qualquer interpretação. Código:
[`heat3d_cs2/demo.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/demo.py).

Uma demo de CS2 é a gravação do próprio servidor (SourceTV): cada jogador, cada tick, 64 ticks por
segundo (`TICKRATE = 64`). É lida com o
[demoparser2](https://github.com/LaihoE/demoparser) em três chamadas, e o resultado é guardado tal
como sai, num `RawPart`:

| Campo | Guarda |
|---|---|
| `path` | o ficheiro |
| `map` | `map_name` do cabeçalho da demo (`de_x`); vazio se o cabeçalho não tiver nenhum |
| `samples` | uma linha por jogador por tick amostrado: os campos de jogador e de regras abaixo, mais `tick`, `steamid`, `name` |
| `events` | nome do evento -> as suas linhas, com os campos dos jogadores prefixados por `user_`, `attacker_`, `assister_` tal como o analisador os nomeia |

Nada em `demo.py` decide o que é um round nem quem o ganhou; isso é [Construir uma partida](building-matches.md).

## Os ticks amostrados {#the-sampled-ticks}

`parse_ticks` é pedido para os ticks `0, N, 2N, ...` até 4.000.000 (`LAST_TICK`, muito além de qualquer
partida - 17 horas a 64 ticks por segundo), onde *N* é o `--every` (padrão 8). O analisador para no
fim da demo. Cada jogador presente num tick amostrado dá uma linha, esteja vivo, morto, observando ou treinador; a filtragem é feita depois.

O passo da amostragem importa além da densidade do mapa de calor: o momento em que um round é decidido é
lido destas amostras (ver [Construir uma partida](building-matches.md#rounds)), por isso os tempos de fim
de round são exatos a um passo (1/8 s por padrão).

### Campos do jogador {#player-fields}

| Propriedade | Torna-se |
|---|---|
| `X`, `Y`, `Z` | a posição, em unidades do jogo (polegadas), Z para cima. O demoparser2 dá a origem do jogador, isto é, os pés. |
| `yaw`, `pitch` | a direção do olhar (graus), transformada num vetor unitário |
| `health`, `armor_value` | vida, colete |
| `team_num` | o lado: 2 = T, 3 = CT; qualquer outro (espectadores, 0, 1) não tem lado |
| `team_clan_name` | o nome da equipa tal como o servidor o mostra, usado para dar nome às equipas |
| `active_weapon_name` | a arma na mão, tal como o jogo a chama (`AK-47`, `Karambit`) |
| `is_alive` | se o jogador está vivo - só os jogadores vivos se tornam posições |
| `last_place_name` | o nome de lugar do próprio mapa (`BombsiteA`) |
| `balance` | dinheiro |
| `current_equip_value` | o valor do que o jogador transporta |

### Campos das regras do jogo {#game-rules-fields}

Lidos em paralelo, uma vez por linha de jogador (são os mesmos para todos num tick):

| Propriedade | Usada para |
|---|---|
| `game_time` | o relógio do servidor, em segundos |
| `total_rounds_played` | a contagem de rounds, que continua pelos ficheiros de uma partida |
| `round_win_status` | quem ganhou o round que acabou de ser jogado: 1 empate, 2 T, 3 CT |
| `round_win_reason` | como (o `CSRoundEndReason` do jogo) |
| `team_rounds_total` | o resultado de cada lado |
| `is_warmup_period` | o aquecimento é deixado de fora em todo o lado |
| `is_freeze_period` | o tempo de congelamento fica de fora das posições |
| `CCSGameRulesProxy.CCSGameRules.m_nOvertimePlaying` | o prolongamento que está a ser jogado, 0 em regulamentar: os rounds de prolongamento não são rounds de pistola (o analisador não tem nome mais curto para isto) |

## Os eventos {#the-events}

Cada evento abaixo é lido quando a demo o declara (`list_game_events`), com `X`, `Y`, `Z`, `team_num`,
`last_place_name` e `which_bomb_zone` (a zona de bomba em que o jogador está: 0 nenhuma, 1 A, 2 B) para
cada jogador que o evento nomeia, e `total_rounds_played` e `is_warmup_period` do jogo nesse tick:

| Evento | Torna-se |
|---|---|
| `player_death` | mortes e kills; usa `weapon`, `headshot`, `assistedflash`, `penetrated`, `thrusmoke`, `noscope`, `attackerblind` |
| `player_hurt` | dano; usa `dmg_health` (dano causado à vida), `health` (vida que resta), `weapon` |
| `player_blind` | jogadores flashados; usa `blind_duration` |
| `weapon_fire` | tiros e lançamentos de granadas; usa `weapon` |
| `smokegrenade_detonate`, `flashbang_detonate`, `hegrenade_detonate`, `inferno_startburn`, `decoy_detonate` | onde as granadas explodiram; usa os `x`, `y`, `z` do próprio evento (o evento não tem nome de lugar para esse ponto, só o de quem lançou) |
| `bomb_planted` | a planta; usa a `which_bomb_zone` e o lugar do plantador, e `site` (o número da entidade da zona) |
| `bomb_defused` | o desarme |
| `bomb_exploded` | quando a bomba explodiu: o tempo da linha `explode` |
| `round_freeze_end` | onde começa cada round |
| `round_prestart` | onde acaba o tempo depois de um round decidido |
| `round_announce_match_start` | onde começa a partida viva |

## Dois factos sobre as demos que decidem como são lidas {#two-facts-about-demos-that-decide-how-they-are-read}

- **Uma partida pode estar dividida por vários ficheiros**, e os nomes dos ficheiros não dizem a sua
  ordem. A contagem de rounds (`total_rounds_played`) continua de um para o outro, e normalmente também o
  relógio do servidor, por isso as partes podem ser ordenadas pelo que contêm.
- **Uma gravação pode começar antes da partida**: aquecimento, um reinício, um round de faca. A partida
  começa no **último** `round_announce_match_start` de um ficheiro; antes dele tudo fica de fora, e o
  aquecimento fica de fora em todo o lado.
