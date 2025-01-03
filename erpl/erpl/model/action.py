from abc import ABC, abstractmethod
from .utils import Size,Position


class Action(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def serialize(self):
        return {}

#END_GAME
class ActionEndGame(Action):
    def __init__(self, message = ""):
        self.message = message

    def serialize(self):
        return {
            'type' : 'END_GAME',
            'message' : self.message
        }

#END_GAME
class ActionEndGameFormatMessage(Action):
    def __init__(self, message = ""):
        self.message = message

    def serialize(self):
        return {
            'type' : 'END_GAME_FORMAT_MESSAGE',
            'message' : self.message
        }

#OBJ_CHANGE_STATE = 1
class ActionObjChangeView(Action):
    def __init__(self, object_id, view_id):
        self.object_id = object_id
        self.view_id = view_id

    def serialize(self):
        return {
            'type' : 'OBJ_CHANGE_VIEW',
            'object' : self.object_id,
            'view' : self.view_id
        }
    
#OBJ_CHANGE_POSITION = 2
class ActionObjChangePosition(Action):
    def __init__(self, object_id, position : Position):
        self.object_id = object_id
        self.position = position

    def serialize(self):
        return {
            'type' : 'OBJ_CHANGE_POSITION',
            'object' : self.object_id,
            'position' : {'x' : self.position.x, 'y' : self.position.y}
        }

#OBJ_CHANGE_SIZE = 3
class ActionObjScale(Action):
    def __init__(self, object_id, scale : Size):
        self.object_id = object_id
        self.scale = scale

    def serialize(self):
        return {
            'type' : 'OBJ_SCALE',
            'object' : self.object_id,
            'scale' : {'x' : self.scale.x, 'y' : self.scale.y}

        }

#SHOW_MESSAGE = 4
class ActionShowMessage(Action):
    def __init__(self, message, position : Position):
        self.message = message
        self.position = position

    def serialize(self):
        return {
            'type' : 'SHOW_MESSAGE',
            'message' : self.message,
            'position' : {'x' : self.position.x, 'y' : self.position.y}
        }

#SHOW_FORMAT_MESSAGE
class ActionShowFormatMessage(Action):
    def __init__(self, message, position : Position):
        self.message = message
        self.position = position

    def serialize(self):
        return {
            'type' : 'SHOW_FORMAT_MESSAGE',
            'message' : self.message,
            'position' : {'x' : self.position.x, 'y' : self.position.y}
        }


#QUESTION = 5
class ActionQuestion(Action):
    def __init__(self, question, answer, sucess:[Action], fail:[Action]):
        self.question = question
        self.answer = answer
        self.sucess = sucess
        self.fail = fail

    def serialize(self):
        return {
            'type' : 'QUESTION',
            'question' : self.question,
            'answer' : self.answer,
            'sucess' : [action.serialize() for action in self.sucess],
            'fail' : [action.serialize() for action in self.fail],
        }

#OBJ_PUT_INVENTORY = 6
class ActionObjGoesToInventory(Action):
    def __init__(self, object_id):
        self.object_id = object_id

    def serialize(self):
        return {
            'type' : 'OBJ_PUT_INVENTORY',
            'object' : self.object_id
        }


#CHANGE_SCENARIO = 7
class ActionChangeScenario(Action):
    def __init__(self, scenario_id):
        self.scenario_id = scenario_id

    def serialize(self):
        return {
            'type' : 'CHANGE_SCENARIO',
            'scenario' : self.scenario_id
        }


#DELETE_ITEM = 8
class ActionRemoveObj(Action):
    def __init__(self, object_id):
        self.object_id = object_id

    def serialize(self):
        return {
            'type' : 'REMOVE_OBJ',
            'object' : self.object_id
        }


#PLAY_SOUND
class ActionPlaySound(Action):
    def __init__(self,sound_id,source_id,source_type):
        self.sound_id = sound_id
        self.source_id = source_id
        self.source_type = source_type

    def serialize(self):
        return {
            'type' : 'PLAY_SOUND',
            'sound' : self.sound_id,
            'source_id' : self.source_id,
            'source_type' : self.source_type
        }


#MOTION_OBJECT = 9
class ActionMotion(Action):
    def __init__(self,motion_object, trigger_object, sucess, fail):
        self.motion_object = motion_object
        self.trigger_object = trigger_object
        self.sucess = sucess
        self.fail = fail

    def serialize(self):
        return {
            'type' : 'MOTION_OBJECT',
            'motion_object' : self.motion_object,
            'trigger_object' : self.trigger_object,
            'sucess' : [action.serialize() for action in self.sucess],
            'fail' : [action.serialize() for action in self.fail],
        }


#MULTIPLE_CHOICE = 10
class ActionMultipleChoice(Action):
    def __init__(self,question, choices, answer, sucess, fail):
        self.question = question
        self.answer = answer
        self.choices = choices
        self.sucess = sucess
        self.fail = fail

    def serialize(self):
        return {
            'type' : 'MULTIPLE_CHOICE',
            'question' : self.question,
            'choices' : self.choices,
            'answer' : self.answer,
            'sucess' : [action.serialize() for action in self.sucess],
            'fail' : [action.serialize() for action in self.fail],
        }



#CONNECTIONS = 11
class ActionMatch(Action):
    def __init__(self,question,list1,list2, sucess, fail):
        self.question = question
        self.list1 = list1
        self.list2 = list2
        self.sucess = sucess
        self.fail = fail

    def serialize(self):
        return {
            'type' : 'CONNECTIONS',
            'question' : self.question,
            'list1' : self.list1,
            'list2' : self.list2,
            'sucess' : [action.serialize() for action in self.sucess],
            'fail' : [action.serialize() for action in self.fail],
        }


#SEQUENCE = 12
class ActionSequence(Action):
    def __init__(self,sequence,question, sucess, fail):
        self.question = question
        self.sequence = sequence
        self.sucess = sucess
        self.fail = fail

    def serialize(self):
        return {
            'type' : 'SEQUENCE',
            'question' : self.question,
            'sequence' : self.sequence,
            'sucess' : [action.serialize() for action in self.sucess],
            'fail' : [action.serialize() for action in self.fail],
        }


#PUZZLE = 13
class ActionPuzzle(Action):
    def __init__(self,image, sucess):
        self.image = image
        self.sucess = sucess

    def serialize(self):
        return {
            'type' : 'PUZZLE',
            'sources' : [['PATH',self.image]],
            'sucess' : [action.serialize() for action in self.sucess],
        }


#SLIDEPUZZLE = 14
class ActionSlidingPuzzle(Action):
    def __init__(self,image, sucess):
        self.image = image
        self.sucess = sucess

    def serialize(self):
        return {
            'type' : 'SLIDEPUZZLE',
            'sources' : [['PATH',self.image]],
            'sucess' : [action.serialize() for action in self.sucess],
        }


#TRANSITION = 15
class ActionTransition(Action):
    def __init__(self,transition_id):
        self.transition_id = transition_id

    def serialize(self):
        return {
            'type' : 'TRANSITION',
            'transition' : self.transition_id
        }


#SOCKET_CONNECTION = 12
class ActionSocketConnection(Action):
    def __init__(self,host,port,text, sucess, fail):
        self.host = host
        self.port = port
        self.text = text
        self.sucess = sucess
        self.fail = fail

    def serialize(self):
        return {
            'type' : 'SOCKET_CONNECTION',
            'host' : self.host,
            'port' : self.port,
            'text' : self.text,
            'sucess' : [action.serialize() for action in self.sucess],
            'fail' : [action.serialize() for action in self.fail],
        }

#VAR_DECREASES
class ActionVarDecreases(Action):
    def __init__(self,variable,number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'VAR_DECREASES',
            'variable' : self.variable,
            'number' : self.number
        }


#VAR_INCREASES
class ActionVarIncreases(Action):
    def __init__(self,variable,number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'VAR_INCREASES',
            'variable' : self.variable,
            'number' : self.number
        }
    

#VAR_BECOMES
class ActionVarBecomes(Action):
    def __init__(self,variable,number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'VAR_BECOMES',
            'variable' : self.variable,
            'number' : self.number
        }
