---
title: O documento da partida
nav_order: 9
lang: "pt"
source: output-match-json.md
source_hash: "9f7c7bd2cbaf"
nav_exclude: true
search_exclude: true
---
# O documento da partida (`<partida>.match.json`) {#the-match-document-matchjson}

Um documento JSON por partida, ao lado da sua tabela: as equipas, o resultado, cada round com o seu
resultado, a economia, a planta, as mortes, os clutches e os sobreviventes, e a linha do placar de
cada jogador. É o que o separador Partida do visualizador 3DHeat carrega.
Código: `summary()` em
[`heat3d_cs2/stats.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_cs2/stats.py);
os números estão definidos em [Estatísticas](statistics.md).

O ficheiro é UTF-8, indentado com um espaço, e mantém os caracteres não ASCII (nomes de jogadores e
de equipas) tal como são. Os tempos são segundos, arredondados a três casas decimais para os rounds e
a duas para as mortes e a planta.

## O documento {#the-document}

| Campo | Tipo | O quê |
|---|---|---|
| `format` | texto | sempre `heat3d-cs2-match` - como um leitor reconhece o ficheiro |
| `version` | número | `3`. Um documento versão 1 dá o `time` de uma planta em segundos de partida; a partir da 2 é em segundos dentro do round, como o de uma morte. A 3 acrescenta os campos a partir de `header` e põe o tempo de congelamento na tabela. |
| `match` | texto | o nome da partida, tal como os ficheiros se chamam |
| `map` | texto | o mapa (`de_x`) |
| `demos` | texto[] | os ficheiros de demo de que foi construído, só os nomes dos ficheiros, pela ordem da partida |
| `teams` | texto[] | os nomes das equipas em ordem de aparecimento (round 1: o lado T primeiro) |
| `score` | objeto | nome da equipa -> rounds ganhos: o resultado do último round |
| `rounds` | objeto[] | cada round completo, em ordem - [abaixo](#rounds) |
| `incomplete` | número[] | números de rounds cortados pelo fim de uma demo e deixados de fora |
| `missing` | número[] | números de rounds antes do primeiro que as demos têm: `[1, 2]` quando a gravação começa no round 3 |
| `halfLength` | número ou null | rounds numa metade regulamentar, a partir de onde os lados trocam pela primeira vez (`12` no formato de 24 rounds); null quando a gravação não mostra a troca |
| `pistolRounds` | número[] | as rondas de pistola com que a `buy` é contada: o round 1, e o round a seguir à metade quando `halfLength` é conhecido; nunca um round de prolongamento |
| `players` | objeto[] | o placar - [abaixo](#players) |
| `conventions` | objeto | as definições por trás dos números, [abaixo](#conventions) |
| `header` | objeto | o cabeçalho da primeira demo tal como o analisador o dá: nome do servidor, versão do patch, versão da demo, mapa |
| `profiles` | objeto | Steam ID -> o que se mantém igual para um jogador durante a partida: `crosshair_code`, `music_kit_id`, `rank`, `comp_wins`, `player_color`, `is_connected` (o último visto) |
| `playerInfo` | objeto[] | cada jogador que as demos listam, treinadores e casters incluídos: Steam ID, nome, número da equipa |
| `skins`, `itemDrops` | objeto[] | skins de armas e itens largados, quando a demo os tem (as demos de torneio a partir da transmissão não têm) |
| `chat` | objeto[] | cada linha de chat da partida: tempo, round, jogador, lado, texto |
| `events` | objeto[] | cada evento do jogo que não diz respeito a nenhum jogador, em ordem de tempo, com todos os seus campos: sinais e fases de round, `round_officially_ended`, `buytime_ended`, `server_message`, `server_cvar` (as definições do servidor à medida que mudam), os planos de câmara de chase e fixos do realizador da transmissão, `cs_win_panel_match`, ... |
| `state` | objeto[] | o estado do jogo onde mudou: tempo, campo, valor - tempos mortos (`is_terrorist_timeout`, `num_ct_timeouts`, `is_technical_timeout`, `is_waiting_for_resume`), a bomba (`is_bomb_planted`, `is_bomb_dropped`), `ct_losing_streak` / `t_losing_streak`, `game_phase`, `round_in_progress`, os jogadores vivos, o `match_start_time` e o `round_start_time` do servidor |
| `selfCheck` | objeto | `completeness`: para onde foi tudo o que a demo tinha - por nome de evento, classe de propriedade, mensagem de rede, quadro e tabela de strings, a sua contagem de `seen`, `decoded`, `partial`, `raw` e `lost`, os ficheiros auxiliares escritos, o total de `lost` (0 guardado com `--no-bulk`), as propriedades que o analisador lista mas não consegue ler (`unreadProps`). A convenção: [Os conversores guardam tudo](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); os ficheiros auxiliares: a seção Completeness do README |

## Rounds {#rounds}

| Campo | Tipo | O quê |
|---|---|---|
| `number` | número | o round, a partir de 1 |
| `start` | número | segundos da partida quando acabou o tempo de congelamento |
| `end` | número | segundos da partida quando o round foi decidido |
| `until` | número | segundos da partida quando começou o round seguinte (o fim da fase after) |
| `winner` | texto | `T` ou `CT`; vazio num empate |
| `winnerTeam` | texto | o nome da equipa do lado vencedor; vazio num empate |
| `reason` | texto | `bomb`, `defuse`, `elimination`, `time`, `surrender`, `draw` ou `other` |
| `score` | objeto | nome da equipa -> rounds ganhos depois deste |
| `sides` | objeto | nome da equipa -> `T` / `CT` neste round |
| `equipment` | objeto | lado -> valor total do equipamento dos seus jogadores vivos no fim do congelamento, em dólares |
| `buy` | objeto | lado -> `pistol`, `eco`, `force` ou `full` |
| `plant` | objeto ou null | a planta da bomba: `site` (`A` ou `B`; vazio quando a demo não o diz), `time` (segundos **dentro do round**, como o de uma morte), `player`, `steamid`, `x`, `y`, `z` (unidades do jogo), `place` (o nome do lugar do plantador: onde a bomba ficou) |
| `survivors` | objeto | lado -> nomes dos jogadores iniciais ainda vivos quando o round foi decidido, ordenados |
| `clutches` | objeto[] | cada um: `player`, `steamid`, `side`, `against` (inimigos vivos quando o jogador ficou o último), `won` |
| `kills` | objeto[] | cada morte do round, em ordem - abaixo |

Como estes são encontrados: [Construir uma partida](building-matches.md#rounds);
clutches e sobreviventes: [Estatísticas](statistics.md#clutches).

### As mortes de um round {#a-rounds-kills}

Cada morte no round, incluindo a fase after:

| Campo | Tipo | O quê |
|---|---|---|
| `time` | número | segundos **dentro do round** (desde o fim do congelamento) |
| `attacker`, `attackerSide` | texto | quem matou e o seu lado; vazio para o mundo |
| `victim`, `victimSide` | texto | a vítima e o seu lado |
| `assister` | texto ou null | o jogador que assistiu, ou null |
| `flashAssist` | bool | a assistência foi um flash |
| `weapon` | texto | tal como o jogo a chama |
| `headshot` | bool | |
| `wallbang` | bool | a bala atravessou alguma coisa |
| `throughSmoke` | bool | a kill foi através de fumo |
| `noscope` | bool | uma arma com mira disparou sem mira |
| `attackerBlind` | bool | quem matou estava cegado por um flash |
| `opening` | bool | a primeira kill de um inimigo no round |
| `traded` | bool | esta morte foi vingada em menos de 5 s |
| `trade` | bool | esta kill vingou um colega em menos de 5 s |
| `teamkill` | bool | atacante e vítima do mesmo lado, dois jogadores diferentes |
| `suicide` | bool | atacante e vítima o mesmo jogador (uma granada própria, por exemplo); não é teamkill |
| `after` | bool | a kill aconteceu depois do round ser decidido |
| `place` | texto | onde estava a **vítima** (o nome do lugar no mapa) |

## Jogadores {#players}

Uma entrada por jogador, agrupados por nome de equipa e depois pelos melhores primeiro em mortes
menos mortes sofridas, e depois em mortes:

| Campo | Tipo | O quê |
|---|---|---|
| `name`, `steamid`, `team` | texto | quem |
| `kills`, `deaths` | número | |
| `assists`, `flashAssists` | número | assistências sem e com flash |
| `diff` | número | kills - mortes |
| `adr` | número | dano médio por round jogado, vida perdida |
| `kast` | número | percentagem de rounds jogados com uma kill, uma assistência, uma sobrevivência ou uma morte vingada |
| `headshotPct` | número | percentagem de kills que foram headshots |
| `openingKills`, `openingDeaths` | número | duelos de abertura ganhos e perdidos |
| `tradeKills`, `tradedDeaths` | número | kills de vingança; mortes que foram vingadas |
| `multiKills` | objeto | `{"2k": n, "3k": n, "4k": n, "5k": n}`: rounds com esse número de kills |
| `clutches`, `clutchesWon` | número | |
| `utilityDamage` | número | dano com HE, molotov, incendiária |
| `enemiesFlashed` | número | inimigos cegados pelo menos 1 s |
| `plants`, `defuses` | número | |
| `teamkills` | número | companheiros mortos; os suicídios não contam |
| `roundsPlayed` | número | rounds começados |

Cada definição: [Estatísticas](statistics.md#the-scoreboard-line).

## Convenções {#conventions}

Escritas em cada documento para que quem o lê saiba o que os números significam sem esta página:

```json
"conventions": {
 "tradeSeconds": 5,
 "buy": "pistol: the first round of each regulation half (pistolRounds), none in overtime; else average equipment under $1500 eco, under $4000 force, otherwise full",
 "damage": "health actually lost, enemies only",
 "kast": "rounds with a kill, an assist (flash assists count), survival or a traded death"
}
```

## Um exemplo {#an-example}

Da demo sintética de dois rounds dos testes, encurtado (`...` marca o que foi deixado de fora):

```json
{
 "format": "heat3d-cs2-match",
 "version": 3,
 "match": "alpha-vs-bravo-m1",
 "map": "de_test",
 "demos": ["synthetic.dem"],
 "teams": ["Alpha", "Bravo"],
 "score": {"Alpha": 2, "Bravo": 0},
 "rounds": [
  {
   "number": 1, "start": 10.0, "end": 26.0, "until": 33.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "elimination",
   "score": {"Alpha": 1, "Bravo": 0},
   "sides": {"Alpha": "T", "Bravo": "CT"},
   "equipment": {"T": 1600, "CT": 1600},
   "buy": {"T": "pistol", "CT": "pistol"},
   "plant": null,
   "survivors": {"CT": [], "T": ["ash"]},
   "clutches": [
    {"player": "ben", "steamid": "4", "side": "CT", "against": 2, "won": false},
    {"player": "ash", "steamid": "2", "side": "T", "against": 1, "won": true}
   ],
   "kills": [
    {"time": 10.0, "attacker": "ace", "attackerSide": "T", "victim": "bob", "victimSide": "CT",
     "assister": null, "flashAssist": false, "weapon": "AK-47", "headshot": true,
     "wallbang": false, "throughSmoke": false, "noscope": false, "attackerBlind": false,
     "opening": true, "traded": true, "trade": false, "teamkill": false, "suicide": false,
     "after": false, "place": "CTSpawn"},
    ...
   ]
  },
  {
   "number": 2, "start": 40.0, "end": 75.0, "until": 85.0,
   "winner": "T", "winnerTeam": "Alpha", "reason": "bomb",
   "buy": {"T": "full", "CT": "full"},
   "plant": {"site": "A", "time": 22.5, "player": "ash", "steamid": "2",
             "x": 120.0, "y": 10.0, "z": -160.0, "place": "BombsiteA"},
   ...
  }
 ],
 "incomplete": [],
 "missing": [],
 "halfLength": null,
 "pistolRounds": [1],
 "players": [
  {"name": "ash", "steamid": "2", "team": "Alpha", "kills": 1, "deaths": 0, "assists": 0,
   "flashAssists": 0, "diff": 1, "adr": 50.0, "kast": 100.0, "headshotPct": 0.0,
   "openingKills": 0, "openingDeaths": 0, "tradeKills": 1, "tradedDeaths": 0,
   "multiKills": {"2k": 0, "3k": 0, "4k": 0, "5k": 0}, "clutches": 1, "clutchesWon": 1,
   "utilityDamage": 0.0, "enemiesFlashed": 0, "plants": 1, "defuses": 0, "teamkills": 0,
   "roundsPlayed": 2},
  ...
 ],
 "conventions": {...}
}
```

A ordem das chaves dentro de `survivors`, `equipment` e `buy` não é fixa.
