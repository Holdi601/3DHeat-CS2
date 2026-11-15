---
title: Limites
nav_order: 13
lang: "pt"
source: limits.md
source_hash: "f34f8f92a3ea"
nav_exclude: true
search_exclude: true
---
# Limites {#limits}

O que o conversor assume, o que não trata e o que não está verificado. Cada ponto vem do código tal
como está.

## O que lê {#what-it-reads}

- **Só ficheiros `.dem` não comprimidos.** `.dem.zst`, `.dem.bz2`, `.rar` e `.zip` precisam de ser descompactados primeiro. A extensão é reconhecida em qualquer maiúscula ou minúscula (`.dem`,
  `.DEM`), nas pastas como nos ficheiros indicados pelo nome.
- **Partidas de desarme de bomba.** As razões de fim de round, a planta da bomba e o local, os
  tipos de compra e as rondas de pistola são os do desarme de bombas. Mapas de reféns, Wingman e
  outros modos não são tratados de forma especial e não estão verificados.
- **64 ticks por segundo** são assumidos (`TICKRATE = 64`) para todos os tempos calculados a partir
  de ticks; os servidores do CS2 correm a 64.
- **Uma demo do servidor** (SourceTV) é assumida: tem todos os jogadores. Uma gravação do ponto de
  vista do cliente (demo POV) não foi testada.

## Partidas e rounds {#matches-and-rounds}

- **Os ficheiros são agrupados pelo nome.** As partes de uma partida precisam partilhar o nome, à
  parte um sufixo `-pN` / `_pN`; ficheiros de uma partida com nomes não relacionados passam a ser
  partidas separadas, e ficheiros com o mesmo nome em pastas diferentes ficam agrupados (depois
  separados em cadeias se não continuarem uns aos outros).
- **A partida viva começa no último `round_announce_match_start`** de um ficheiro. Um round de faca
  que não seja seguido desse anúncio é contado como round.
- **Os tempos de fim de round são exatos a uma amostra** (`--every` ticks, 1/8 s por padrão),
  porque a decisão é lida do estado do jogo amostrado. Um `--every` muito grande pode falhar uma
  janela curta entre o fim de um round e o início do seguinte e deixar o round de fora como
  incompleto.
- **Empates.** Um round empatado (estado de vitória 1, razão 10) é decidido sem vencedor: `winner`
  fica vazio e nenhum dos lados o ganhou. Nenhum empate apareceu numa demo real para comparar; é
  verificado na demo sintética.
- **Rounds cortados** pelo fim de um ficheiro ficam de fora (`incomplete`), não são adivinhados;
  os rounds anteriores ao primeiro dos ficheiros são listados como `missing`.
- **As rondas de pistola** seguem o comprimento da metade que a gravação mostra: onde os lados
  trocam pela primeira vez entre dois rounds regulamentares seguidos. Uma gravação que não mostra
  essa troca (começa depois do intervalo, ou acaba antes, ou falta um round de cada lado dela)
  conhece só o round 1 como ronda de pistola. O prolongamento não tem nenhuma.
- **Equipas.** Uma equipa é o nome de clã visto mais vezes nos seus jogadores. Sem nomes de clã, as
  equipas são `Started T` e `Started CT`. Um jogador que muda de equipa no meio da partida mantém
  uma só equipa.

## Eventos {#events}

- **Tudo o que o analisador oferece é lido**, com estas exceções: a velocidade dos jogadores (o
  analisador calcula-a a partir das posições; não está na demo), a voz (áudio, `parse_voice`) e o
  `weapon_fire` da bomba (o início de uma planta, que `bomb_beginplant` tem). As trajetórias das
  granadas são guardadas à amostragem dos jogadores (`--every`) e no ponto onde cada granada parou,
  não em cada tick.
- **Linhas fora de um round** (aquecimento, uma pausa entre o início da partida e o primeiro tempo
  de congelamento para além de dois minutos) ficam de fora da tabela; os eventos que não dizem
  respeito a nenhum jogador estão todos no `events` do documento da partida.
- **As linhas de detonação** (`smoke`, `flash`, `he`, `molotov`, `decoy`) não têm `place`: a demo dá
  nomes de lugares aos jogadores, não às granadas. O lugar de quem lançou nesse momento está em
  `throwerPlace`.
- **O local da planta** vem da zona de bomba que o jogo diz em que o plantador estava, senão do nome
  do lugar do plantador, senão de outra planta na mesma zona no mesmo ficheiro. Quando nenhum deles
  diz nada, `site` fica vazio.
- **Uma morte para o mundo** (uma queda, a bomba) não tem atacante: nem kill, nem teamkill, nem
  abertura; é só uma morte.

## Estatísticas {#statistics}

- **Os rounds jogados** vêm de quem tinha uma posição no primeiro segundo depois do tempo de
  congelamento. Um jogador que entra mais tarde num round não conta como o tendo jogado (as suas
  kills continuam a contar).
- **Sobrevivência para o KAST**: um jogador morto na fase after não sobreviveu para o KAST, embora a
  lista de rounds ainda o nomeie entre os sobreviventes.
- **Os dois jogadores de um 1v1** podem ser creditados com um clutch no mesmo round; ver
  [Estatísticas](statistics.md#clutches).
- **O dano de utilitário** são granadas HE, molotovs e incendiárias; uma kill ou golpe por um flash
  ou decoy lançado não é dano de utilitário.

## Exportação do mapa {#map-export}

- Precisa do jogo instalado (ou do `.vpk`) e da CLI do Source2Viewer; nada é transferido.
- Exporta só `world_physics`; os clip brushes e o céu ficam de fora pelos seus nomes conterem
  `clip` ou `sky`, em qualquer maiúscula ou minúscula.
- O chão é distinguido da estrutura só pela normal da face (componente Z de 0,7 ou mais), por isso
  uma rampa íngreme é estrutura e um telhado plano é chão.
- O ficheiro está em polegadas, não em metros.

## Memória e tempo {#memory-and-time}

- Uma partida fica em memória por inteiro enquanto é construída, num trabalhador por partida. Com
  muitos trabalhadores e um `--every` pequeno, a memória soma-se: reduza `--jobs` se uma máquina
  ficar sem memória.
- Uma partida só é escrita quando está construída: primeiro o `.parquet`, depois o `.match.json`.
  Uma execução interrompida no meio deixa uma tabela sem o seu documento de partida; uma partida só
  conta como escrita com os dois, por isso a execução seguinte converte de novo. As partidas
  ainda não começadas são simplesmente apanhadas pela execução seguinte.
