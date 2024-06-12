from abc import ABC, abstractmethod
from .utils import debug, BalloonMessage, Position
from .precondition import EventPreConditionClickedItem, EventPreConditionItemIsInUse, EventPreConditionItemNotInUse
from .precondition_tree import PreConditionTree, PreConditionOperatorAnd, PreConditionVar
import sys
from .challenge import ChallengeSocketConnection, ChallengeSlidePuzzle, ChallengePuzzle, ChallengeSequence, ChallengeConnections, ChallengeQuestion, ChallengeMotion, ChallengeMultipleChoice

class EventPosCondition(ABC):
    def __init__(self,type):
        pass

    @abstractmethod
    def do(self,room,inventory):
        pass

#END_GAME = 0
class EventPosConditionEndGame(EventPosCondition):
    def __init__(self, message = ""):
        self.message = message
    
    def do(self,room,inventory,state):
        state.finish_game()
        debug("EVENT_ENDGAME.")

#OBJ_CHANGE_STATE = 1
class EventPosConditionObjChangeState(EventPosCondition):
    def __init__(self, object_id, view_id):
        self.object_id = object_id
        self.view_id = view_id

    def do(self,room,inventory,state):
        state.buffer_obj_views[self.object_id] = self.view_id #colocar no buffer o view do object para ser posteriormente alterado
        debug("EVENT_CHANGE_STATE: Mudando o view do object "+self.object_id+" para "+self.view_id+".")

#OBJ_CHANGE_POSITION = 2
class EventPosConditionObjChangePosition(EventPosCondition):
    def __init__(self, object_id, position):
        self.object_id = object_id
        self.position = position

    def do(self,room,inventory,state):
        room.objects[self.object_id].change_position(self.position)
        debug("EVENT_CHANGE_POSITION: Mudando "+self.object_id +" para a position ("+str(self.position.x)+","+str(self.position.y)+").")

#OBJ_CHANGE_SIZE = 3
class EventPosConditionObjChangeSize(EventPosCondition):
    def __init__(self, object_id, size):
        self.object_id = object_id
        self.size = size

    def do(self,room,inventory,state):
        object_id = self.object_id
        size = self.size
        room.objects[object_id].change_size(size)
        debug("EVENT_CHANGE_SIZE: Mudando "+object_id +" para o size ("+str(size.x)+","+str(size.y)+").")

#SHOW_MESSAGE = 4
class EventPosConditionShowMessage(EventPosCondition):
    def __init__(self, message, position : Position):
        self.message = message
        self.position = position

    def do(self,room,inventory,state):
        state.buffer_messages.append(BalloonMessage(self.message,self.position.x,self.position.y))
        debug("EVENT_MESSAGE: Mostrando message '"+str(self.message)+"'.")

#QUESTION = 5
class EventPosConditionQuestion(EventPosCondition):
    def __init__(self, code, question, sucess_event, fail_event):
        self.code = code
        self.question = question
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_ask_code = ChallengeQuestion(self.question,self.code, self.sucess_event, self.fail_event)
        state.active_challenge_mode(challenge_ask_code)
        debug("EVENT_ASKCODE: Pedindo código "+self.code+".")

#OBJ_PUT_INVENTORY = 6
class EventPosConditionObjPutInventory(EventPosCondition):
    def __init__(self, object_id):
        self.object_id = object_id
    
    def do(self,room,inventory,state):
        #Transformar Object em Item
        #Remover dos objects da sala
        #Colocar no inventário
        #Criar events de ativo e desativo
        object_id = self.object_id
        object = room.objects[object_id]
        del room.objects[object_id]
        slot = inventory.find_empty_slot()
        inventory.update_add.append((object,slot))
        desativar = PreConditionTree(PreConditionOperatorAnd(PreConditionVar(EventPreConditionClickedItem(object_id)),PreConditionVar(EventPreConditionItemIsInUse(object_id))))
        ativar = PreConditionTree(PreConditionOperatorAnd(PreConditionVar(EventPreConditionClickedItem(object_id)),PreConditionVar(EventPreConditionItemNotInUse(object_id))))
        room.add_event_buffer("desativar_"+object_id,desativar,[EventPosConditionDesactiveItem(object_id)],sys.maxsize)
        room.add_event_buffer("ativar"+object_id,ativar,[EventPosConditionActiveItem(object_id)],sys.maxsize)
        debug("EVENT_PUT_IN_INVENTORY: Colocando item "+object_id+" no slot "+str(slot)+" do inventário.")

#CHANGE_SCENARIO = 7
class EventPosConditionChangeScenario(EventPosCondition):
    def __init__(self, scenario_id):
        self.scenario_id = scenario_id

    def do(self,room,inventory,state):
        state.buffer_current_scenario = self.scenario_id
        debug("EVENT_CHANGE_SCENE: Mudando para cena "+self.scenario_id+".")

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


#PLAY_SOUND
class EventPosConditionPlaySound(EventPosCondition):
    def __init__(self,sound_id,source_id,source_type):
        self.sound_id = sound_id
        self.source_id = source_id
        self.source_type = source_type
    
    def do(self,room,inventory,state):
        if self.source_type == 'Object':
            room.objects[self.source_id].sounds[self.sound_id].play()
        elif self.source_type == 'Scenario':
            room.scenarios[self.source_id].sounds[self.sound_id].play()
        debug("EVENT_PLAY_SOUND: Tocando sound "+self.sound_id+".")


#MOTION_OBJECT = 9
class EventPosConditionMoveObject(EventPosCondition):
    def __init__(self,object_id, trigger_object, sucess_event, fail_event):
        self.object_id = object_id
        self.trigger_object = trigger_object
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_motion = ChallengeMotion(self.sucess_event,self.fail_event, self.object_id, self.trigger_object)
        state.active_challenge_mode(challenge_motion)
        debug("EVENT_POSCONDITION_MOTION_OBJECT: Motion object "+self.object_id+".")

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

#SEQUENCE = 12
class EventPosConditionSequence(EventPosCondition):
    def __init__(self,sequence,question, sucess_event, fail_event):
        self.question = question
        self.sequence = sequence
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_sequence = ChallengeSequence(self.question,self.sequence,self.sucess_event,self.fail_event)
        state.active_challenge_mode(challenge_sequence)
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

#TRANSITION = 15
class EventPosConditionTransition(EventPosCondition):
    def __init__(self,transition):
        self.transition = transition
    
    def do(self,room,inventory,state):
        transition = room.transitions[self.transition]
        state.active_transition_mode(transition)
        debug("EVENT_POSCONDITION_TRANSITION")

#SOCKET_CONNECTION = 12
class EventPosConditionSocketConnection(EventPosCondition):
    def __init__(self,host,port,text, sucess_event, fail_event):
        self.host = host
        self.port = port
        self.text = text
        self.sucess_event = sucess_event
        self.fail_event = fail_event

    def do(self,room,inventory,state):
        challenge_socket_connection = ChallengeSocketConnection(self.host,self.port,self.text,self.sucess_event,self.fail_event)
        state.active_listenning_challenge_mode(challenge_socket_connection)
        debug("EVENT_POSCONDITION_ORDER")