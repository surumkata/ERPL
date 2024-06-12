#!/usr/bin/python3

import os

# Configuração para ocultar a message de boas-vindas do Pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import sys
from .model.load import load
from .model.utils import WIDTH, HEIGHT, Color, current_folder, Position, Size
from .model.inventory import Inventory
import math

from .model.escape_room import EscapeRoom
import argparse

def pe_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='Engine')
    parser.add_argument('--input','-i'             ,type=str, nargs=1                                , help='Input file')
    return parser.parse_args()
        

def distance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

#def clicked_circles(x,y,pos,size,r=8):
#    c1x,c1y = pos.x, pos.y
#    c2x,c2y = pos.x + size.x, pos.y
#    c3x,c3y = pos.x, pos.y + size.y
#    c4x,c4y = pos.x + size.x, pos.y + size.y
#    clickedc1 = distance(x,y,c1x,c1y) <= r
#    clickedc2 = distance(x,y,c2x,c2y) <= r
#    clickedc3 = distance(x,y,c3x,c3y) <= r
#    clickedc4 = distance(x,y,c4x,c4y) <= r
#    return clickedc1 or clickedc2 or clickedc3 or clickedc4



def play_editor(screen,room, inventory):
    # Loop principal do jogo
    clock = pygame.time.Clock()
    show_info = True
    running = True
    master_object = None
    master_size = None
    master_position = None
    font = pygame.font.Font(None, 36)
    motion_activated = False
    motion_size = False
    motion_circle = None
    last_motion_x = None
    last_motion_y = None
    last_click_x = None
    last_click_y = None
    last_position = None
    last_size = None
    keys_down = []
    shift_pressed = False
    r = 8
    # Loop principal do jogo
    while running:
        for pygame_event in pygame.event.get():
            #print(pygame_event)
            if pygame_event.type == pygame.QUIT:
                running = False
            elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
                # QUANDO CLICA NUM OBJETO APARECE A HITBOX DELE E A POSICAO
                for id,object in room.objects.items():
                    if not motion_activated and master_object is not None:
                        if(distance(pygame_event.pos[0],pygame_event.pos[1],master_position.x, master_position.y) <= r): #CANTO SUPERIOR ESQUERDO
                            motion_size = True
                            motion_circle = 1
                        elif (distance(pygame_event.pos[0],pygame_event.pos[1],master_position.x + master_size.x, master_position.y) <= r): #CANTO SUPERIOR DIREITO
                            motion_size = True
                            motion_circle = 2
                        elif(distance(pygame_event.pos[0],pygame_event.pos[1],master_position.x, master_position.y + master_size.y) <= r): #CANTO INFERIOR ESQUERDO
                            motion_size = True
                            motion_circle = 3
                        elif (distance(pygame_event.pos[0],pygame_event.pos[1],master_position.x + master_size.x, master_position.y + master_size.y) <= r): #CANTO INFERIOR DIREITO
                            motion_size = True
                            motion_circle = 4
                        if motion_size:
                            last_click_x,last_click_y = pygame_event.pos[0],pygame_event.pos[1]
                            last_motion_x,last_motion_y = None,None

                    if not motion_size and object.have_clicked(pygame_event.pos[0],pygame_event.pos[1]):
                        if master_size is not None and master_object is not None:
                            room.objects[master_object].change_size(master_size)
                        master_object = id
                        master_size = room.objects[master_object].size
                        last_size = Size(master_size.x,master_size.y)
                        master_position = room.objects[master_object].position
                        last_position = Position(master_position.x,master_position.y)
                        motion_activated = True
                        last_click_x,last_click_y = pygame_event.pos[0],pygame_event.pos[1]
                        last_motion_x,last_motion_y = None,None
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
                elif motion_size:
                    if last_motion_x is not None and last_motion_y is not None:
                        dif_motion_x = pygame_event.pos[0] - last_motion_x
                        dif_motion_y = pygame_event.pos[1] - last_motion_y
                    else:
                        dif_motion_x = pygame_event.pos[0] - last_click_x
                        dif_motion_y = pygame_event.pos[1] - last_click_y
                    last_motion_x = pygame_event.pos[0]
                    last_motion_y = pygame_event.pos[1]
                    if shift_pressed:
                        #if abs(dif_motion_x) >= abs(dif_motion_y):
                        #    ratio = master_size.x / master_size.y
                        #    dif_motion_y = int(dif_motion_x * ratio)
                        #else:
                        #    ratio = master_size.y / master_size.x
                        #    dif_motion_x = int(dif_motion_y * ratio)

                        if master_size.y > master_size.x:
                            ratio = master_size.y / master_size.x
                            dif_motion_x = int(dif_motion_y * ratio)
                        else:
                            ratio = master_size.x / master_size.y
                            dif_motion_y = int(dif_motion_x * ratio)
                            
                        dif_motion_x = max(dif_motion_y,dif_motion_x)
                        dif_motion_y = max(dif_motion_y,dif_motion_x)

                    if motion_circle == 1: #CANTO SUPERIOR ESQUERDO
                        master_size.x = max(1,master_size.x - dif_motion_x)
                        master_size.y = max(1,master_size.y - dif_motion_y)
                        master_position.x = max(1,master_position.x + dif_motion_x)
                        master_position.y = max(1,master_position.y + dif_motion_y)
                    elif motion_circle == 2: #CANTO SUPERIOR DIREITO
                        master_size.x = max(1,master_size.x + dif_motion_x)
                        master_size.y = max(1,master_size.y - dif_motion_y)
                        master_position.y = max(1,master_position.y + dif_motion_y)
                    elif motion_circle == 3: #CANTO INFERIOR ESQUERDO
                        master_size.y = max(1,master_size.y + dif_motion_y)
                        master_position.x = max(1,master_position.x + dif_motion_x)
                        master_size.x = max(1,master_size.x - dif_motion_x)
                    elif motion_circle == 4: #CANTO INFERIOR DIREITO
                        master_size.x = max(1,master_size.x + dif_motion_x)
                        master_size.y = max(1,master_size.y + dif_motion_y)
                    #room.objects[master_object].change_size(master_size)
                    

            elif pygame_event.type == pygame.KEYUP:
                if pygame_event.key == 1073742049:
                    shift_pressed = False
                elif len(keys_down) > 0:
                    if pygame_event.key == pygame.K_UP:
                        keys_down.remove(pygame.K_UP)
                    elif pygame_event.key == pygame.K_DOWN:
                        keys_down.remove(pygame.K_DOWN)
                    elif pygame_event.key == pygame.K_LEFT:
                        keys_down.remove(pygame.K_LEFT)
                    elif pygame_event.key == pygame.K_RIGHT:
                        keys_down.remove(pygame.K_RIGHT)
            elif pygame_event.type == pygame.KEYDOWN:
                if pygame_event.unicode == 'f':
                    show_info = not show_info
                if master_object is not None:
                    if pygame_event.key == 1073742049: #SHIFT
                        shift_pressed = True
                    elif pygame_event.key == pygame.K_UP:
                        master_position.y -= 1
                        keys_down.append(pygame.K_UP)
                    elif pygame_event.key == pygame.K_DOWN:
                        master_position.y += 1
                        keys_down.append(pygame.K_DOWN)
                    elif pygame_event.key == pygame.K_LEFT:
                        master_position.x -= 1
                        keys_down.append(pygame.K_LEFT)
                    elif pygame_event.key == pygame.K_RIGHT:
                        master_position.x += 1
                        keys_down.append(pygame.K_RIGHT)
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
                        room.objects[master_object].change_size(master_size)
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
            elif pygame_event.type == pygame.TEXTINPUT:
                if pygame_event.text == 'q':
                    master_size.x += 1
                elif pygame_event.text == 'w':
                        master_size.x -= 1
                elif pygame_event.text == 'e':
                    master_size.y += 1
                elif pygame_event.text == 'r':
                    master_size.y -= 1
            elif pygame_event.type == pygame.MOUSEBUTTONUP:
                motion_activated = False
                motion_size = False

        if len(keys_down) > 0:
            if pygame.K_UP in keys_down:
                master_position.y -= 1
            if pygame.K_DOWN in keys_down:
                master_position.y += 1
            if pygame.K_LEFT in keys_down:
                master_position.x -= 1
            if pygame.K_RIGHT in keys_down:
                master_position.x += 1

        #Desenhar a room
        room.draw(screen)
        inventory.draw(screen)

        if master_object is not None:

            size_text = font.render(f"Size: {master_size.x,master_size.y}", True, Color.GREEN)
            position_text = font.render(f"Position: {master_position.x,master_position.y}", True, Color.GREEN)

            #width = room.objects[master_object].states[room.objects[master_object].current_state].image_width
            #height = room.objects[master_object].states[room.objects[master_object].current_state].image_height
            #hitbox_text = font.render(f"HITBOX: {width,height}", True, BLACK)

            screen.blit(size_text, (10, 500))
            screen.blit(position_text, (10, 530))
            #screen.blit(hitbox_text, (10, 560))
            rect_color = Color.GREEN if shift_pressed else Color.RED
            if motion_size:
                pygame.draw.rect(screen, rect_color, (master_position.x, master_position.y, master_size.x, master_size.y))
            else:
                pygame.draw.rect(screen, rect_color, (master_position.x, master_position.y, master_size.x, master_size.y),2)
            #pygame.draw.rect(screen, BLACK, (master_position.x, master_position.y, width, height))
            pygame.draw.circle(screen, Color.RED, (master_position.x, master_position.y) ,r) #CANTO SUPERIOR ESQUERDO
            pygame.draw.circle(screen, Color.GREEN, (master_position.x + master_size.x, master_position.y) ,r) #CANTO SUPERIOR DIREITO
            pygame.draw.circle(screen, Color.BLUE, (master_position.x, master_position.y + master_size.y) ,r) #CANTO INFERIOR ESQUERDO
            pygame.draw.circle(screen, Color.BLACK, (master_position.x + master_size.x, master_position.y + master_size.y) ,r) #CANTO INFERIOR DIREITO

        clock.tick(60)
        

        #Fps
        if show_info:
            # Calcule os FPS
            
            fps = int(clock.get_fps())

            # Renderize o text do FPS na tela
            fps_text = font.render(f"FPS: {fps}", True, Color.RED)
            # Desenhe o text do FPS na tela
            screen.blit(fps_text, (10, 440))

            # Renderize o text na tela
            object_text = font.render(f"Object: {master_object}", True, Color.BLUE)
            # Desenhe o text na tela
            screen.blit(object_text, (10, 470))

        pygame.display.flip()

    # Encerramento do jogo
    pygame.quit()
    sys.exit()

def init_pe(args):
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
    return screen,room, inventory

if __name__ == '__main__':
    args = pe_parse_arguments()
    screen,room,inventory = init_pe(args)
    # Play Editor
    play_editor(screen,room, inventory)
