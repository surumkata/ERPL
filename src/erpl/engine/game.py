#!/usr/bin/python3

import os
import threading

# Configuração para ocultar a mensagem de boas-vindas do Pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from .model.load import load
from .model.utils import WIDTH, HEIGHT, current_folder
from .model.inventory import Inventory
from .model.escape_room import EscapeRoom
from .model.game_state import GameState
import argparse
from .model.settings import Settings




def game_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='Engine')
    parser.add_argument('--input','-i'             ,type=str, nargs=1                                , help='Input file')
    return parser.parse_args()

def do_event(event,room : EscapeRoom, inventory : Inventory,state : GameState):
    for poscondition in event.pos_conditions:
        poscondition.do(room,inventory,state)
    state.buffer_events_happened.append(event.id)

def try_do_events(room : EscapeRoom, inventory : Inventory,state : GameState):
    for event in room.events.values():
        if event.pre_conditions.root == None: #nao tem preconditions
            continue
        if not event.inifity_repetitions and not event.repetitions > 0: #nao tem mais repetiçoes
            continue
        if event.pre_conditions.test_tree(room, inventory,state):
            do_event(event=event, room=room, inventory=inventory, state=state)

def listening_challenge(room : EscapeRoom, inventory : Inventory,state : GameState):
    event = state.challenge.listen()
    if event != None and event != 0:
        do_event(room.events[event],room,inventory,state)
        state.desactive_challenge_mode()
    if event == 0:
        state.desactive_challenge_mode()


def play_game(screen,room, inventory, state):
    running = True
    settings = Settings()
    created_thread = False
    # Loop principal do jogo
    while running:
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                running = False
            elif state.is_running():
                #running normal mode
                if pygame_event.type == pygame.MOUSEBUTTONDOWN:
                    state.buffer_messages = []
                    state.buffer_click_events.append((pygame_event.pos[0],pygame_event.pos[1]))
                elif pygame_event.type == pygame.KEYDOWN:
                    #clica numa tecla durante o jogo normal
                    if pygame_event.unicode == 'f':
                        settings.show_info = not settings.show_info
                    elif pygame_event.key == pygame.K_F1:
                        settings.change_volume(0.1)
                    elif pygame_event.key == pygame.K_F2:
                        settings.change_volume(-0.1)
            elif state.is_challenge_mode():
                event = state.challenge.update_pygame_event(pygame_event,room)
                if event != None and event != 0:
                    do_event(room.events[event],room,inventory,state)
                    state.desactive_challenge_mode()
                if event == 0:
                    state.desactive_challenge_mode()
            elif state.is_transition():
                #se clicar no rato acaba a transiçao
                if pygame_event.type == pygame.MOUSEBUTTONDOWN:
                    state.transition.stop_music()
                    if state.transition.next_scenario != None:
                        state.desactive_transition_mode()
                    else:
                        state.active_transition_mode(room.transitions[state.transition.next_transition])
            elif state.is_challenge_listenning():
                if state.challenge.update_pygame_event(pygame_event,room) == 0:
                    state.desactive_challenge_mode()

        if state.is_challenge_listenning():
            room.draw(screen,state.current_scenario)
            inventory.draw(screen)
            state.challenge.draw(screen)

            if not created_thread:
                # Inicia a thread para escutar mensagens
                message_listener = threading.Thread(target=listening_challenge, args=(room,inventory,state))
                message_listener.start()
                created_thread = True
        else:
            created_thread = False

        #Tenta fazer eventos
        try_do_events(room,inventory,state)

        #Atualiza os buffers depois dos eventos
        state.update_buffers(room)
        
        #Atualiza os eventos do inventário
        inventory.update_items()

        if state.is_running():
            room.draw(screen,state.current_scenario)
            inventory.draw(screen)
            state.draw_messages(screen)

        elif state.is_transition():
            state.transition.draw(screen)

        elif state.is_challenge_mode():
            room.draw(screen,state.current_scenario)
            inventory.draw(screen)
            state.challenge.draw(screen)
        
        #Tela de fim de jogo
        elif state.is_finished():
            state.draw_finish_screen(screen)
             

        settings.clock.tick(60)

        if settings.show_info:
            settings.draw_info(screen)

        pygame.display.flip()

    # Encerramento do jogo
    pygame.quit()

def init_game(args = None):
    # Inicialização do Pygame
    pygame.init()

    # Configurações do jogo
    # Configurar o mixer
    pygame.mixer.init()

    
    ## Carregue a música de fundo
    #filename = f'{current_folder}/../../../../assets/sounds/soundtrack.mp3'
    #pygame.mixer.music.load(filename)
    #pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Escape Room 2D")

    # Loading do modelo
    room,state = load(args.input[0]) if args and args.input else load()

    # Inicializar o inventário  
    inventory = Inventory()

    return screen,room,inventory,state


if __name__ == '__main__':
    args = game_parse_arguments()
    screen,room,inventory,state = init_game(args)
    # Play Game
    play_game(screen,room,inventory, state)

