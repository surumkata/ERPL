# ERPL
## Escape Room Programming Language

ERPL (Escape Room Programming Language) é uma DSL para a criação de Escape Rooms.

## Modelo

EscapeRoom
- titúlo: titúlo da escape room.
- tamanho: tamanho dos cenários da escape room.
- cenários: cenários presentes na escape room.
- eventos: eventos presentes na escape room.
- transições: transições presentes na escape room.

Cenário
- id: identifcador do cenário.
- estados: visuais do cenário.
- sons: aúdios do cenário.
- objetos: objetos presentes no cenário.

Objeto
- id: identificador do objeto.
- estados: visuais do objeto.
- sons: aúdios do objeto.
- posição: posição do objeto no cenário.
- tamanho: tamanho do objeto.

Estado
- Estado Estático:
 -- id: identificador do estado.
 -- imagem: imagem do estado.
 -- posição: posição do estado.
 -- tamanho: tamanho do estado.
- Estado Dinâmico:
-- id: identificador do estado.
-- imagens: imagens da animação do estado.
-- posição: posição do estado.
-- tamanho: tamanho do estado.
-- repetições: número de repetições da animação.
-- tempo entre sprites: tempo entre cada imagem durante a animação.

Som
 - id: identificador do som.
 - fonte: fonte de aúdio.

Evento:
 - id
 - pré-condições: condições para a realização do evento.
 - pós-condições: condições realizadas durante o evento.

Desafio:
 - Desafio Pergunta:
    -- id
    -- pergunta
    -- resposta
    -- evento de sucesso
    -- evento de falha
 - Desafio Arrasta:
    -- id
    -- objeto de arrasto
    -- objeto de gatilho
    -- evento de sucesso
    -- evento de falha
 - Desafio Escolha Múltipla:
    -- id
    -- pergunta
    -- escolhas
    -- resposta
    -- evento de sucesso
    -- evento de falha 
 - Desafio Conexão:
    -- id
    -- pergunta
    -- primeira lista
    -- segunda lista
    -- evento de sucesso
    -- evento de falha
 - Desafio Sequência:
    -- id
    -- pergunta
    -- sequência
    -- evento de sucesso
    -- evento de falha
 - Desafio Puzzle:
    -- id
    -- imagem
    -- evento de sucesso
 - Desafio Slide Puzzle:
    -- id
    -- imagem
    -- evento de sucesso
 - Desafio Socket
    -- id
    -- host
    -- port
    -- mensagem
    -- evento de sucesso
    -- evento de falha

Transição:
 - id: identificador da transição.
 - fundo: estado de fundo da transição.
 - música: som a passar na transição.
 - história: texto a passar na transição. 
 - próxima cena|transição: o que vem a seguir da transição.