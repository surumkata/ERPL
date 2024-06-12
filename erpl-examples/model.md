# ERPL
## Escape Room Programming Language

ERPL (Escape Room Programming Language) é uma DSL para a criação de Escape Rooms.

## Modelo

EscapeRoom
- titúlo: titúlo da escape room.
- size: size dos scenarios da escape room.
- scenarios: scenarios presentes na escape room.
- events: events presentes na escape room.
- transições: transições presentes na escape room.

Scenario
- id: identifcador do scenario.
- views: visuais do scenario.
- sounds: aúdios do scenario.
- objects: objects presentes no scenario.

Object
- id: identificador do object.
- views: visuais do object.
- sounds: aúdios do object.
- position: position do object no scenario.
- size: size do object.

View
- View Estático:
 -- id: identificador do view.
 -- image: image do view.
 -- position: position do view.
 -- size: size do view.
- View Dinâmico:
-- id: identificador do view.
-- images: images da animação do view.
-- position: position do view.
-- size: size do view.
-- repetições: número de repetições da animação.
-- tempo entre sprites: tempo entre cada image durante a animação.

Sound
 - id: identificador do sound.
 - source: source de aúdio.

Event:
 - id
 - pré-condições: condições para a realização do event.
 - pós-condições: condições realizadas durante o event.

Challenge:
 - Challenge Question:
    -- id
    -- question
    -- answer
    -- event de sucess
    -- event de fail
 - Challenge Motion:
    -- id
    -- object de arrasto
    -- object de trigger
    -- event de sucess
    -- event de fail
 - Challenge Multiple_Choice:
    -- id
    -- question
    -- choices
    -- answer
    -- event de sucess
    -- event de fail 
 - Challenge Connection:
    -- id
    -- question
    -- primeira list
    -- segunda list
    -- event de sucess
    -- event de fail
 - Challenge Sequence:
    -- id
    -- question
    -- sequence
    -- event de sucess
    -- event de fail
 - Challenge Puzzle:
    -- id
    -- image
    -- event de sucess
 - Challenge Slide Puzzle:
    -- id
    -- image
    -- event de sucess
 - Challenge Socket
    -- id
    -- host
    -- port
    -- message
    -- event de sucess
    -- event de fail

Transition:
 - id: identificador da transition.
 - background: view de background da transition.
 - música: sound a passar na transition.
 - história: text a passar na transition. 
 - próxima cena|transition: o que vem a seguir da transition.