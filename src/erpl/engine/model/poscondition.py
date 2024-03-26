from abc import ABC, abstractmethod
from .utils import debug, BalloonMessage
from .precondition import EventPreConditionClickItem, EventPreConditionActiveWhenItemInUse, EventPreConditionActiveWhenItemNotInUse
from .precondition_tree import PreConditionTree, PreConditionOperatorAnd, PreConditionVar
import sys
from .challenge import ChallengeSlidePuzzle, ChallengePuzzle, ChallengeOrder, ChallengeConnections, ChallengeStateAskCode, ChallengeMotion, ChallengeMultipleChoice

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
    
    def do(self,room,inventory,state):
        state.finish_game()
        debug("EVENT_ENDGAME.")

#CHANGE_STATE = 1
class EventPosConditionChangeState(EventPosCondition):
    def __init__(self, object_id, state_id):
        self.object_id = object_id
        self.state_id = state_id

    def do(self,room,inventory,state):
        state.buffer_obj_states[self.object_id] = self.state_id #colocar no buffer o estado do objeto para ser posteriormente alterado
        debug("EVENT_CHANGE_STATE: Mudando o estado do objeto "+self.object_id+" para "+self.state_id+".")

#CHANGE_POSITION = 2
class EventPosConditionChangePosition(EventPosCondition):
    def __init__(self, object_id, position):
        self.object_id = object_id
        self.position = position

    def do(self,room,inventory,state):
        room.objects[self.object_id].change_position(self.position)
        debug("EVENT_CHANGE_POSITION: Mudando "+self.object_id +" para a posição ("+str(self.position.x)+","+str(self.position.y)+").")

#CHANGE_SIZE = 3
class EventPosConditionChangeSize(EventPosCondition):
    def __init__(self, object_id, size):
        self.object_id = object_id
        self.size = size

    def do(self,room,inventory,state):
        object_id = self.object_id
        size = self.size
        room.objects[object_id].change_size(size)
        debug("EVENT_CHANGE_SIZE: Mudando "+object_id +" para o tamanho ("+str(size.x)+","+str(size.y)+").")

#SHOW_MESSAGE = 4
class EventPosConditionShowMessage(EventPosCondition):
    def __init__(self, position, message):
        self.position = position
        self.message = message

    def do(self,room,inventory,state):
        state.buffer_messages.append(BalloonMessage(self.message,self.position.x,self.position.y))
        debug("EVENT_MESSAGE: Mostrando mensagem '"+str(self.message)+"' na posição ("+str(self.position.x)+","+str(self.position.y)+").")

#ASK_CODE = 5
class EventPosConditionAskCode(EventPosCondition):
    def __init__(self, code, question, sucess_event, fail_event, position):
        self.code = code
        self.question = question
        self.sucess_event = sucess_event
        self.fail_event = fail_event
        self.position = position

    def do(self,room,inventory,state):
        challenge_ask_code = ChallengeStateAskCode(self.question,self.code, self.sucess_event, self.fail_event)
        state.active_challenge_mode(challenge_ask_code)
        debug("EVENT_ASKCODE: Pedindo código "+self.code+".")

#PUT_INVENTORY = 6
class EventPosConditionPutInventory(EventPosCondition):
    def __init__(self, object_id):
        self.object_id = object_id
    
    def do(self,room,inventory,state):
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

    def do(self,room,inventory,state):
        state.buffer_current_scene = self.scene_id
        debug("EVENT_CHANGE_SCENE: Mudando para cena "+self.scene_id+".")

#ACTIVE_ITEM = 8
class EventPosConditionActiveItem(EventPosCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def do(self,room,inventory,state):
        inventory.active_item(self.item_id) #TODO: maybe need a buffer
        debug("EVENT_ACTIVE_ITEM: Ativando item "+self.item_id+".")

#DESACTIVE_ITEM = 8
class EventPosConditionDesactiveItem(EventPosCondition):
    def __init__(self, item_id):
        self.item_id = item_id
    
    def do(self,room,inventory,state):
        inventory.desactive_item(self.item_id) #TODO: maybe need a buffer
        debug("EVENT_DESACTIVE_ITEM: Desativando item "+self.item_id+".")

#DELETE_ITEM = 8
class EventPosConditionDeleteItem(EventPosCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def do(self,room,inventory,state):
        inventory.update_remove.append(self.item_id)
        debug("EVENT_DELETE_ITEM: Removendo item "+self.item_id+".")

class EventPosConditionPlaySound(EventPosCondition):
    def __init__(self,sound_id):
        self.sound_id = sound_id
    
    def do(self,room,inventory,state):
        room.sounds[self.sound_id].play()
        debug("EVENT_PLAY_SOUND: Tocando som "+self.sound_id+".")


#MOVE_OBJECT = 9
class EventPosConditionMoveObject(EventPosCondition):
    def __init__(self,object_id, object_trigger, sucess_event, fail_event):
        self.object_id = object_id
        self.object_trigger = object_trigger
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_motion = ChallengeMotion(self.sucess_event,self.fail_event, self.object_id, self.object_trigger)
        state.active_challenge_mode(challenge_motion)
        debug("EVENT_POSCONDITION_MOVE_OBJECT: Arrasta objeto "+self.object_id+".")

#MULTIPLE_CHOICE = 10
class EventPosConditionMultipleChoice(EventPosCondition):
    def __init__(self,question, answer, multiple_choices, sucess_event, fail_event):
        self.question = question
        self.answer = answer
        self.multiple_choices = multiple_choices
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_multiple_choice = ChallengeMultipleChoice(self.question,self.multiple_choices,self.answer,self.sucess_event,self.fail_event)
        state.active_challenge_mode(challenge_multiple_choice)
        debug("EVENT_POSCONDITION_MULTIPLE_CHOICE")


#CONNECTIONS = 11
class EventPosConditionConnections(EventPosCondition):
    def __init__(self,connections,question, sucess_event, fail_event):
        self.question = question
        self.connections = connections
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_connections = ChallengeConnections(self.question,self.connections,self.sucess_event,self.fail_event)
        state.active_challenge_mode(challenge_connections)
        debug("EVENT_POSCONDITION_CONNECTIONS")

#CONNECTIONS = 12
class EventPosConditionOrder(EventPosCondition):
    def __init__(self,order,question, sucess_event, fail_event):
        self.question = question
        self.order = order
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_order = ChallengeOrder(self.question,self.order,self.sucess_event,self.fail_event)
        state.active_challenge_mode(challenge_order)
        debug("EVENT_POSCONDITION_ORDER")

#PUZZLE = 13
class EventPosConditionPuzzle(EventPosCondition):
    def __init__(self,image, sucess_event):
        self.image = image
        self.sucess_event = sucess_event

    def do(self,room,inventory,state):
        challenge_puzzle = ChallengePuzzle(self.image,self.sucess_event)
        state.active_challenge_mode(challenge_puzzle)
        debug("EVENT_POSCONDITION_PUZZLE")

#SLIDEPUZZLE = 14
class EventPosConditionSlidePuzzle(EventPosCondition):
    def __init__(self,image, sucess_event):
        self.image = image
        self.sucess_event = sucess_event

    def do(self,room,inventory,state):
        challenge_puzzle = ChallengeSlidePuzzle(self.image,self.sucess_event)
        state.active_challenge_mode(challenge_puzzle)
        debug("EVENT_POSCONDITION_SLIDE_PUZZLE")