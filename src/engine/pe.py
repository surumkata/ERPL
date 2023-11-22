#!/usr/bin/python3

import pygame
import sys
from model.load import load
from model.utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, BLUE, current_folder, Position, Size
from model.inventory import Inventory

from model.escape_room import EscapeRoom
import argparse

def parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='Engine')
    parser.add_argument('--input','-i'             ,type=str, nargs=1                                , help='Input file')
    return parser.parse_args()
        

def play_game(room, inventory):
    # Loop principal do jogo
    clock = pygame.time.Clock()
    show_info = True
    running = True
    master_object = None
    master_size = None
    master_position = None
    font = pygame.font.Font(None, 36)
    motion_activated = False
    last_motion_x = None
    last_motion_y = None
    last_click_x = None
    last_click_y = None
    last_position = None
    last_size = None
    # Loop principal do jogo
    while running:
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                running = False
            elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
                # QUANDO CLICA NUM OBJETO APARECE A HITBOX DELE E A POSICAO
                for id,object in room.objects.items():
                    if object.have_clicked(pygame_event.pos[0],pygame_event.pos[1]):
                        master_object = id
                        master_size = room.objects[master_object].size
                        last_size = Size(master_size.x,master_size.y)
                        master_position = room.objects[master_object].position
                        last_position = Position(master_position.x,master_position.y)
                        motion_activated = True
                        last_click_x,last_click_y = pygame_event.pos[0],pygame_event.pos[1]
                        break
            elif pygame_event.type == pygame.MOUSEMOTION:
                if motion_activated:
                    if last_motion_x is not None and last_motion_y is not None:
                        dif_motion_x = pygame_event.pos[0] - last_motion_x
                        dif_motion_y = pygame_event.pos[1] - last_motion_y
                    else:
                        dif_motion_x = pygame_event.pos[0] - last_click_x
                        dif_motion_y = pygame_event.pos[1] - last_click_y
                    last_motion_x = pygame_event.pos[0]
                    last_motion_y = pygame_event.pos[1]
                    master_position.x += dif_motion_x
                    master_position.y += dif_motion_y
            elif pygame_event.type == pygame.KEYDOWN:
                if pygame_event.unicode == 'f':
                    show_info = not show_info
                if master_object is not None:
                    if pygame_event.key == pygame.K_UP:
                        master_position.y -= 1
                    elif pygame_event.key == pygame.K_DOWN:
                        master_position.y += 1
                    elif pygame_event.key == pygame.K_LEFT:
                        master_position.x -= 1
                    elif pygame_event.key == pygame.K_RIGHT:
                        master_position.x += 1
                    elif pygame_event.unicode == 'q':
                        master_size.x += 1
                    elif pygame_event.unicode == 'w':
                        master_size.x -= 1
                    elif pygame_event.unicode == 'e':
                        master_size.y += 1
                    elif pygame_event.unicode == 'r':
                        master_size.y -= 1
                    elif pygame_event.key == 13:
                        master_position = None
                        master_size = None
                        last_position = None
                        last_size = None
                        master_object = None
                    elif pygame_event.key == pygame.K_BACKSPACE:
                        room.objects[master_object].change_position(last_position)
                        room.objects[master_object].change_size(last_size)
                        master_position = None
                        master_size = None
                        last_position = None
                        last_size = None
                        master_object = None
                        last_motion_x = None
                        last_motion_y = None
                        motion_activated = False
            elif pygame_event.type == pygame.MOUSEBUTTONUP:
                if motion_activated:
                    motion_activated = False
                    if last_motion_y is not None:
                        master_position = None
                        master_size = None
                        last_position = None
                        last_size = None
                        last_motion_x = None
                        last_motion_y = None
                        master_object = None

        #Desenhar a room
        room.draw(screen)
        inventory.draw(screen)

        if master_object is not None:

            size_text = font.render(f"Size: {master_size.x,master_size.y}", True, GREEN)
            position_text = font.render(f"Position: {master_position.x,master_position.y}", True, GREEN)

            screen.blit(size_text, (10, 500))
            screen.blit(position_text, (10, 530))
            pygame.draw.rect(screen, RED, (master_position.x, master_position.y, master_size.x, master_size.y),2)



        clock.tick(60)

        #Fps
        if show_info:
            # Calcule os FPS
            
            fps = int(clock.get_fps())

            # Renderize o texto do FPS na tela
            fps_text = font.render(f"FPS: {fps}", True, RED)
            # Desenhe o texto do FPS na tela
            screen.blit(fps_text, (10, 440))

            # Renderize o texto na tela
            object_text = font.render(f"Object: {master_object}", True, BLUE)
            # Desenhe o texto na tela
            screen.blit(object_text, (10, 470))

        pygame.display.flip()

    # Encerramento do jogo
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    args = parse_arguments()

    # Inicialização do Pygame
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Escape Room 2D")

    # Loading do modelo
    if args.input:
        room = load(args.input[0])
    else:
        room = load()

    # Inicializar o inventário
    inventory = Inventory()
    play_game(room, inventory)

