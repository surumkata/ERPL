from enum import Enum
from abc import ABC, abstractmethod
from model.utils import debug, BalloonMessage
from model.precondition import EventPreConditionClickItem, EventPreConditionActiveWhenItemInUse, EventPreConditionActiveWhenItemNotInUse
from model.precondition_tree import PreConditionTree, PreConditionOperatorAnd, PreConditionVar
import sys

#"""TIPOS DE then EVENTOS"""
#    ENDGAME = 0
#    CHANGE_STATE = 1
#    CHANGE_POSITION = 2
#    CHANGE_SIZE = 3
#    SHOW_MESSAGE = 4
#    ASK_CODE = 5
#    PUT_INVENTORY = 6
#    CHANGE_SCENE = 7
#    ACTIVE_ITEM = 8
#    DESACTIVE_ITEM = 9
#    DELETE_ITEM = 10

class EventPosCondition(ABC):
    def __init__(self,type):
        pass

    @abstractmethod
    def do(self,room,inventory):
        pass

#ENDGAME = 0
class EventPosConditionEndGame(EventPosCondition):
    def __init__(self, message = ""):
        self.message = message
    
    def do(self,room,inventory):
        room.er_state.finish_game = True
        debug("EVENT_ENDGAME.")

#CHANGE_STATE = 1
class EventPosConditionChangeState(EventPosCondition):
    def __init__(self, object_id, state_id):
        self.object_id = object_id
        self.state_id = state_id

    def do(self,room,inventory):
        object_id = self.object_id
        state_id = self.state_id
        room.er_state.changed_objects_states[object_id] = state_id #colocar no buffer o estado do objeto para ser posteriormente alterado
        debug("EVENT_CHANGE_STATE: Mudando o estado do objeto "+object_id+" para "+state_id+".")

#CHANGE_POSITION = 2
class EventPosConditionChangePosition(EventPosCondition):
    def __init__(self, object_id, position):
        self.object_id = object_id
        self.position = position

    def do(self,room,inventory):
        object_id = self.object_id
        pos = self.position
        room.objects[object_id].change_position(pos)
        debug("EVENT_CHANGE_POSITION: Mudando "+object_id +" para a posição ("+str(pos.x)+","+str(pos.y)+").")

#CHANGE_SIZE = 3
class EventPosConditionChangeSize(EventPosCondition):
    def __init__(self, object_id, size):
        self.object_id = object_id
        self.size = size

    def do(self,room,inventory):
        object_id = self.object_id
        size = self.size
        room.objects[object_id].change_size(size)
        debug("EVENT_CHANGE_SIZE: Mudando "+object_id +" para o tamanho ("+str(size.x)+","+str(size.y)+").")

#SHOW_MESSAGE = 4
class EventPosConditionShowMessage(EventPosCondition):
    def __init__(self, position, message):
        self.position = position
        self.message = message

    def do(self,room,inventory):
        message = self.message
        pos = self.position
        room.er_state.messages.append(BalloonMessage(message,pos.x,pos.y))
        debug("EVENT_MESSAGE: Mostrando mensagem '"+str(message)+"' na posição ("+str(pos.x)+","+str(pos.y)+").")

#ASK_CODE = 5
class EventPosConditionAskCode(EventPosCondition):
    def __init__(self, code, message, sucess_event, fail_event):
        self.code = code
        self.message = message
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory):
        room.er_state.input_active = True
        room.er_state.input_code = self.code
        room.er_state.messages.append(BalloonMessage(self.message,300,300))
        room.er_state.input_sucess = self.sucess_event
        room.er_state.input_fail = self.fail_event
        debug("EVENT_ASKCODE: Pedindo código "+self.code+".")

#PUT_INVENTORY = 6
class EventPosConditionPutInventory(EventPosCondition):
    def __init__(self, object_id):
        self.object_id = object_id
    
    def do(self,room,inventory):
        #Transformar Objeto em Item
        #Remover dos objetos da sala
        #Colocar no inventário
        #Criar eventos de ativo e desativo
        object_id = self.object_id
        object = room.objects[object_id]
        del room.objects[object_id]
        slot = inventory.find_empty_slot()
        inventory.update_add.append((object,slot))
        desativar = PreConditionTree(PreConditionOperatorAnd(PreConditionVar(EventPreConditionClickItem(object_id)),PreConditionVar(EventPreConditionActiveWhenItemInUse(object_id))))
        ativar = PreConditionTree(PreConditionOperatorAnd(PreConditionVar(EventPreConditionClickItem(object_id)),PreConditionVar(EventPreConditionActiveWhenItemNotInUse(object_id))))
        room.add_event_buffer("desativar_"+object_id,desativar,[EventPosConditionDesactiveItem(object_id)],sys.maxsize,False)
        room.add_event_buffer("ativar"+object_id,ativar,[EventPosConditionActiveItem(object_id)],sys.maxsize,False)
        debug("EVENT_PUT_IN_INVENTORY: Colocando item "+object_id+" no slot "+str(slot)+" do inventário.")

#CHANGE_SCENE = 7
class EventPosConditionChangeScene(EventPosCondition):
    def __init__(self, scene_id):
        self.scene_id = scene_id

    def do(self,room,inventory):
        room.er_state.current_scene_buffer = self.scene_id
        debug("EVENT_CHANGE_SCENE: Mudando para cena "+self.scene_id+".")

#ACTIVE_ITEM = 8
class EventPosConditionActiveItem(EventPosCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def do(self,room,inventory):
        inventory.active_item(self.item_id) #TODO: maybe need a buffer
        debug("EVENT_ACTIVE_ITEM: Ativando item "+self.item_id+".")

#DESACTIVE_ITEM = 8
class EventPosConditionDesactiveItem(EventPosCondition):
    def __init__(self, item_id):
        self.item_id = item_id
    
    def do(self,room,inventory):
        inventory.desactive_item(self.item_id) #TODO: maybe need a buffer
        debug("EVENT_DESACTIVE_ITEM: Desativando item "+self.item_id+".")

#DELETE_ITEM = 8
class EventPosConditionDeleteItem(EventPosCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def do(self,room,inventory):
        inventory.update_remove.append(self.item_id)
        debug("EVENT_DELETE_ITEM: Removendo item "+self.item_id+".")

class EventPosConditionPlaySound(EventPosCondition):
    def __init__(self,sound_id):
        self.sound_id = sound_id
    
    def do(self,room,inventory):
        room.sounds[self.sound_id].play()
        debug("EVENT_PLAY_SOUND: Tocando som "+self.sound_id+".")
