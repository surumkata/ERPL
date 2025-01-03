#!/usr/bin/python3

#Imports
import os
import threading
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from .model.load import load
from .model.utils import WIDTH, HEIGHT, HEIGHT_INV
from .model.inventory import Inventory
from .model.escape_room import EscapeRoom
from .model.game_state import GameState
from .model.settings import Settings

# Configuração para ocultar a message de boas-vindas do Pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

def do_event(event,room : EscapeRoom, inventory : Inventory,state : GameState):
    '''Do the pos-conditions of an event'''
    for poscondition in event.pos_conditions:
        poscondition.do(room,inventory,state)
    state.buffer_events_happened.append(event.id)

def try_do_events(room : EscapeRoom, inventory : Inventory,state : GameState):
    '''Test whether an event is to be held'''
    for event in room.events.values():
        if event.pre_conditions.root == None: #not tem preconditions
            continue
        if not event.inifity_repetitions and not event.repetitions > 0: #not tem mais repetiçoes
            continue
        if event.pre_conditions.test_tree(room, inventory,state):
            do_event(event=event, room=room, inventory=inventory, state=state)

def listening_challenge(room : EscapeRoom, inventory : Inventory,state : GameState):
    '''Listen to the challenge'''
    (status,event) = state.challenge.listen()
    
    if event != None and event != 0:
        do_event(event,room,inventory,state)
        state.desactive_challenge_mode()
    if event == 0:
        state.desactive_challenge_mode()
    if status == True:
        room.variables['_sucesses_'] += 1
    else:
        room.variables['_fails_'] += 1


def play_game(screen,room, inventory, state):
    '''Main function of the game'''
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
                result = state.challenge.update_pygame_event(pygame_event,room)
                if result != None and result != 0:
                    (status,event) = result
                    do_event(event,room,inventory,state)
                    state.desactive_challenge_mode()
                    if status == True:
                        room.variables['_sucesses_'] += 1
                    else:
                        room.variables['_fails_'] += 1
                if result == 0:
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

        if not state.is_finished():
            #Tenta fazer events
            try_do_events(room,inventory,state)

            #Atualiza os buffers depois dos events
            state.update_buffers(room)

            #Atualiza os events do inventário
            inventory.update_items()

            if state.is_running():
                room.draw(screen,state.current_scenario)
                inventory.draw(screen)
                state.draw_messages(screen)

            elif state.is_transition():
                state.transition.draw(screen,room.variables)

            elif state.is_challenge_mode():
                room.draw(screen,state.current_scenario)
                inventory.draw(screen)
                state.challenge.draw(screen)
        
            ticks = pygame.time.get_ticks()
            room.variables['_timer_'] = int(ticks / 1000)
            room.variables['_timerms_'] = ticks

            for minutos_total in range(1, 91):  # De 1 até 90
                segundos_restantes = minutos_total * 60 - int(ticks / 1000)
                minutos = segundos_restantes // 60
                segundos = segundos_restantes % 60
                room.variables[f'_regressive_timer_{minutos_total}min_'] = f"{minutos:02}:{segundos:02}"

        #Tela de end of game
        else:
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

    
    ## Carregue a música de background
    #filename = f'{current_folder}/../../../../assets/sounds/soundtrack.mp3'
    #pygame.mixer.music.load(filename)
    #pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT+HEIGHT_INV))

    # Loading do modelo
    room,state = load(args.input[0]) if args and args.input else load()

    pygame.display.set_caption(room.title)
    # Inicializar o inventário  
    inventory = Inventory()

    return screen,room,inventory,state
