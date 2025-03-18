## Funcionalidades 
### Sistema de pontos e tempo decorrido 

    Essa funcionalidade consiste em implementar ao jogador a chance de fazer pontos ao longo que o jogo acontece. 
    Além de também mostrar quanto tempo o jogador demorou em uma partida e que, dependendo do seu tempo total, irá 
    influenciar a sua pontuação final. 

#### O sistema de pontos visa ter: 

- A cada jogada, que esteja dentro das regras, o jogador ganha uma certa pontuação.
  - O pontos funcionam de maneira que: 
    - Cartas movidas de forma correta no tableau, 5 pontos 
    - Cartas movidas do Tableau para fundação, 15 pontos 
    - Catas movidas do waste para fundação, 10 pontos 
    - Cartas movidas do waste para o tableau, 5 pontos
- Se o jogador desfazer uma jogada, os pontos ganhados com esta jogada são perdidos.
- Ao ganhar o jogo:
  - é mostrado a pontuação total das jogadas.
  - Pontuação de tempo (sistema de tempo decorrido). 
  - E a soma total dessas duas pontuações.

#### O sistema de tempo decorrido visa ter: 

- uma cronometragem do tempo total do jogo.
- dependo de quanto tempo o jogador conseguir resolver o jogo, ganha pontos de tempo. 

    
    O sistema de ponto e o sistema de tempo deccorido estão ligados de forma que a pontuação final do jogador 
    depende de quanto tempo demorou a sua partida.

#### No fim do jogo aparece um menu com as seguintes informações: 
 
- Pontuação 
- bônus de tempo 
- Pontuação total 
- tempo que o jogador demorou a temrinar a jogada 


### Sistema de dicas 

    Essa funcionalidade consiste em ajudar o jogador a continuar o jogo em um momento de bloqueio. 

#### Esse sistema visa ter:

- um botão de dica
- Uma vez que o jogador não conseguir mais avançar com o jogo e resolver apertar o botão de dica, o sistema 
move uma carta, dentro das regras de jogo.
- Se não houver nenhuma jogada possível no tableau para mover, a dica será olhar as cartas dentro do stock. 
- Se o jogador apertar o botão de dicas em todas as cartas do stock e também não existir nenhuma jogada no tableau, 
é mostrado uma mensagem que não é possível continuar com o jogo e se o jogador deseja iniciar um novo jogo. 
- O sistema de pontuação também pode estar interligado com o sistema dicas uma vez que ao terminar o jogo a quantidade de dicas 
usadas podem diminuir a pontuação final. 

  

Consertar:
- verificar a sobreposição do tempo ao carregar o último jogo
