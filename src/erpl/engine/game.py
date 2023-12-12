#!/usr/bin/python3

import pygame
import sys
from .model.load import load
from .model.utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, BLUE, current_folder, Position
from .model.inventory import Inventory

from .model.escape_room import EscapeRoom
import argparse

def game_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='Engine')
    parser.add_argument('--input','-i'             ,type=str, nargs=1                                , help='Input file')
    return parser.parse_args()

def do_event(event,room : EscapeRoom, inventory : Inventory):
    for poscondition in event.pos_conditions:
        poscondition.do(room,inventory)
    room.er_state.events_happend.append(event.id)

def try_do_events(room : EscapeRoom, inventory : Inventory):
    for event in room.events.values():
        if event.linked:
            continue
        if not event.repeatable > 0 and event.happen:
            continue
        if event.pre_conditions.test_tree(room, inventory):
            do_event(event=event, room=room, inventory=inventory)


def play_game(screen,room, inventory):
    # Loop principal do jogo
    clock = pygame.time.Clock()
    show_info = False
    running = True
    # Defina o volume inicial (0.5 para 50%)
    volume = 0.5
    pygame.mixer.music.set_volume(volume)
    # Loop principal do jogo
    while running:
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                running = False
            elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
                room.er_state.messages = []
                room.er_state.input_active = False
                room.er_state.click_events.append((pygame_event.pos[0],pygame_event.pos[1]))
            elif pygame_event.type == pygame.KEYDOWN:
                if room.er_state.input_active:
                    if pygame_event.key == pygame.K_RETURN:  # Verifica se o jogador pressionou Enter
                        room.er_state.messages = []
                        if room.er_state.input_text == room.er_state.input_code:
                            do_event(room.events[room.er_state.input_sucess], room, inventory)
                        else:
                            do_event(room.events[room.er_state.input_fail], room, inventory)
                        room.er_state.clear_input()
                    elif pygame_event.key == pygame.K_BACKSPACE:  # Verifica se o jogador pressionou Backspace
                        room.er_state.input_text = room.er_state.input_text[:-1]
                    else:
                        room.er_state.input_text += pygame_event.unicode  # Adiciona a tecla pressionada à entrada do jogador
                else:
                    if pygame_event.unicode == 'f':
                        show_info = not show_info
                    elif pygame_event.key == pygame.K_F1:
                        # Diminua o volume (não abaixo de 0)
                        volume = max(0, volume - 0.1)
                        pygame.mixer.music.set_volume(volume)
                    elif pygame_event.key == pygame.K_F2:
                        # Aumente o volume (não acima de 1)
                        volume = min(1, volume + 0.1)
                        pygame.mixer.music.set_volume(volume)
            elif pygame_event.type == pygame.MOUSEMOTION:
                if room.er_state.motion_activated:
                    room.er_state.last_motion = Position(pygame_event.pos[0],pygame_event.pos[1])
                    object = room.objects[room.er_state.object_motion]
                    object.change_position(room.er_state.last_motion)
            elif pygame_event.type == pygame.MOUSEBUTTONUP:
                if room.er_state.motion_activated and room.er_state.last_motion is not None:
                    trigger_object = room.objects[room.er_state.trigger_motion]
                    if(trigger_object.have_clicked(room.er_state.last_motion.x,room.er_state.last_motion.y)):
                        do_event(room.events[room.er_state.motion_sucess_event],room,inventory)
                    else:
                        do_event(room.events[room.er_state.motion_fail_event],room,inventory)
                room.er_state.motion_activated = False
                room.er_state.last_motion = None


        try_do_events(room,inventory)
        room.er_state.click_events = []
        room.update_events()
        room.update_states()
        inventory.update_items()
        if room.er_state.current_scene_buffer != None: 
            room.change_current_scene(room.er_state.current_scene_buffer)
            room.er_state.current_scene_buffer = None

        #Desenhar a room
        room.draw(screen)

        inventory.draw(screen)

        for message in room.er_state.messages:
            message.display(screen)

        # Exibir o prompt de entrada do jogador
        if room.er_state.input_active:
            pygame.draw.rect(screen, WHITE, room.er_state.input_box)
            font = pygame.font.Font(None, 32)
            input_surface = font.render(room.er_state.input_text, True, BLACK)
            width = max(200, input_surface.get_width()+10)
            room.er_state.input_box.w = width
            screen.blit(input_surface, (room.er_state.input_box.x+5, room.er_state.input_box.y+5))
            pygame.draw.rect(screen, BLACK, room.er_state.input_box, 2)


        #Tela de fim de jogo
        if room.er_state.finish_game:
            pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido/
            font = pygame.font.Font(None, 36)
            text = font.render("Você Escapou!", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)    

        clock.tick(60)

        #Fps
        if show_info:
            # Calcule os FPS
            font = pygame.font.Font(None, 36)
            fps = int(clock.get_fps())

            # Renderize o texto do FPS na tela
            fps_text = font.render(f"FPS: {fps}", True, RED)

            # Desenhe o texto do FPS na tela
            screen.blit(fps_text, (10, 670))

            # Renderize o texto na tela
            volume_text = font.render(f"Volume: {int(volume * 100)}%", True, BLUE)
            # Desenhe o texto na tela
            screen.blit(volume_text, (120, 670))

        pygame.display.flip()

    # Encerramento do jogo
    pygame.quit()
    sys.exit()

def init_game(args = None):
    # Inicialização do Pygame
    pygame.init()

    # Configurações do jogo
    # Configurar o mixer
    pygame.mixer.init()
    # Carregue a música de fundo
    filename = f'{current_folder}/../../../../assets/sounds/soundtrack.mp3'
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Escape Room 2D")

    # Loading do modelo
    if args and args.input:
        room = load(args.input[0])
    else:
        room = load()

    # Inicializar o inventário
    inventory = Inventory()

    # Play Game
    play_game(screen,room, inventory)

if __name__ == '__main__':
    args = game_parse_arguments()
    init_game(args)

