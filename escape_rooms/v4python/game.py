#!/usr/bin/python3

import pygame
import sys
from model.load import load
from model.utils import WIDTH, HEIGHT, BLACK, WHITE, GREEN, debug, BalloonMessage
from model.inventory import Inventory
from model.poscondition import EventPosCondition, EventPosConditionsType, EventPosConditionDesactiveItem, EventPosConditionActiveItem
from model.precondition import EventPreConditionClickItem, EventPreConditionActiveWhenItemInUse, EventPreConditionActiveWhenItemNotInUse
from model.precondition_tree import PreConditionTree, PreConditionOperatorAnd, PreConditionVar
from model.escape_room import EscapeRoom
import argparse

def parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='Engine')
    parser.add_argument('--input','-i'             ,type=str, nargs=1                                , help='Input file')
    return parser.parse_args()

def do_event(event,room : EscapeRoom, inventory : Inventory):
    for poscondition in event.pos_conditions:
        do_poscondition(poscondition,room, inventory)
    room.er_state.events_happend.append(event.id)

def try_do_events(room : EscapeRoom, inventory : Inventory):
    for event in room.events.values():
        if event.linked:
            continue
        if not event.repeatable > 0 and event.happen:
            continue
        if event.pre_conditions.test_tree(room, inventory):
            do_event(event=event, room=room, inventory=inventory)

def do_poscondition(poscondition : EventPosCondition,room : EscapeRoom, inventory : Inventory):
    type = poscondition.type
    if type == EventPosConditionsType.ENDGAME:
        room.er_state.finish_game = True
        debug("EVENT_ENDGAME.")
    elif type == EventPosConditionsType.CHANGE_STATE:
        object_id = poscondition.object_id
        state_id = poscondition.state_id
        room.er_state.changed_objects_states[object_id] = state_id #colocar no buffer o estado do objeto para ser posteriormente alterado
        debug("EVENT_CHANGE_STATE: Mudando o estado do objeto "+object_id+" para "+state_id+".")
    elif type == EventPosConditionsType.PUT_INVENTORY:
        #Transformar Objeto em Item
        #Remover dos objetos da sala
        #Colocar no inventário
        #Criar eventos de ativo e desativo
        object_id = poscondition.object_id
        object = room.objects[object_id]
        del room.objects[object_id]
        slot = inventory.find_empty_slot()
        inventory.update_add.append((object,slot))
        desativar = PreConditionTree(PreConditionOperatorAnd(PreConditionVar(EventPreConditionClickItem(object_id)),PreConditionVar(EventPreConditionActiveWhenItemInUse(object_id))))
        ativar = PreConditionTree(PreConditionOperatorAnd(PreConditionVar(EventPreConditionClickItem(object_id)),PreConditionVar(EventPreConditionActiveWhenItemNotInUse(object_id))))
        room.add_event_buffer("desativar_"+object_id,desativar,[EventPosConditionDesactiveItem(object_id)],True,False)
        room.add_event_buffer("ativar"+object_id,ativar,[EventPosConditionActiveItem(object_id)],True,False)
        debug("EVENT_PUT_IN_INVENTORY: Colocando item "+object_id+" no slot "+str(slot)+" do inventário.")
    elif type == EventPosConditionsType.ACTIVE_ITEM:
        item_id = poscondition.item_id
        inventory.active_item(item_id) #TODO: maybe need a buffer
        debug("EVENT_ACTIVE_ITEM: Ativando item "+item_id+".")
    elif type == EventPosConditionsType.DESACTIVE_ITEM:
        item_id = poscondition.item_id
        inventory.desactive_item(item_id) #TODO: maybe need a buffer
        debug("EVENT_DESACTIVE_ITEM: Desativando item "+item_id+".")
    elif type == EventPosConditionsType.DELETE_ITEM:
        item_id = poscondition.item_id
        inventory.update_remove.append(item_id)
        debug("EVENT_DELETE_ITEM: Removendo item "+item_id+".")
    elif type == EventPosConditionsType.SHOW_MESSAGE:
        message = poscondition.message
        pos = poscondition.position
        room.er_state.messages.append(BalloonMessage(message,pos.x,pos.y))
        debug("EVENT_MESSAGE: Mostrando mensagem '"+str(message)+"' na posição ("+str(pos.x)+","+str(pos.y)+").")
    elif type == EventPosConditionsType.ASK_CODE:
        room.er_state.input_active = True
        room.er_state.input_code = poscondition.code
        room.er_state.messages.append(BalloonMessage(poscondition.message,300,300))
        room.er_state.input_sucess = poscondition.sucess_event
        room.er_state.input_fail = poscondition.fail_event
        debug("EVENT_ASKCODE: Pedindo código "+poscondition.code+".")
    elif type == EventPosConditionsType.CHANGE_SIZE:
        object_id = poscondition.object_id
        size = poscondition.size
        room.objects[object_id].change_size(size)
        debug("EVENT_CHANGE_SIZE: Mudando "+object_id +" para o tamanho ("+str(size.x)+","+str(size.y)+").")
    elif type == EventPosConditionsType.CHANGE_POSITION:
        object_id = poscondition.object_id
        pos = poscondition.position
        room.objects[object_id].change_position(pos)
        debug("EVENT_CHANGE_POSITION: Mudando "+object_id +" para a posição ("+str(pos.x)+","+str(pos.y)+").")
    elif type == EventPosConditionsType.CHANGE_SCENE:
        scene_id = poscondition.scene_id
        room.er_state.current_scene_buffer = scene_id
        debug("EVENT_CHANGE_SCENE: Mudando para cena "+scene_id+".")

def play_game(room, inventory):

    running = True
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

        pygame.display.flip()

    # Encerramento do jogo
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    args = parse_arguments()

    # Inicialização do Pygame
    pygame.init()

    # Configurações do jogo

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

