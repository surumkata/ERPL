import pygame
import sys
from enum import Enum

debug_mode = True
WIDTH, HEIGHT = 1300, 700

def debug(message : str):
    print(message)


"""TIPOS DE PRE CONDIÇOES DE EVENTOS"""
class EventPreConditionsType(Enum):
    CLICK = 0
    CLICK_AFTER_EVENT = 1
    ACTIVE_BY_EVENT = 2
    ACTIVE_AFTER_EVENT = 3
    ACTIVE_AFTER_TIME = 4
    ACTIVE_WHEN_STATE = 5
    ACTIVE_WHEN_NOT_STATE = 6
    ACTIVE_WHEN_ITEM_IN_USE = 7
    ACTIVE_WHEN_ITEM_NOT_IN_USE = 8
    CLICK_ITEM = 9
    CLICK_NOT = 10

"""TIPOS DE POS CONDIÇOES DE EVENTOS"""

class EventPosConditionsType(Enum):
    ENDGAME = 0
    CHANGE_STATE = 1
    CHANGE_POSITION = 2
    CHANGE_SIZE = 3
    SHOW_MESSAGE = 4
    ASK_CODE = 5
    PUT_INVENTORY = 6
    CHANGE_SCENE = 7
    ACTIVE_ITEM = 8
    DESACTIVE_ITEM = 9
    DELETE_ITEM = 10
    MOTION = 11

class EventPreCondition:
    def __init__(self,type):
        self.type = type

#CLICK = 0
class EventPreConditionClick(EventPreCondition):
    def __init__(self, object_id):
        super().__init__(EventPreConditionsType.CLICK)
        self.object_id = object_id

#CLICK_AFTER_EVENT = 1
class EventPreConditionClickAfterEvent(EventPreCondition):
    def __init__(self, object_id, event_id):
        super().__init__(EventPreConditionsType.CLICK_AFTER_EVENT)
        self.object_id = object_id
        self.event_id = event_id

#ACTIVE_BY_EVENT = 2
class EventPreConditionActiveByEvent(EventPreCondition):
    def __init__(self, event_id):
        super().__init__(EventPreConditionsType.ACTIVE_BY_EVENT)
        self.event_id = event_id

#ACTIVE_AFTER_EVENT = 3
class EventPreConditionActiveAfterEvent(EventPreCondition):
    def __init__(self, event_id):
        super().__init__(EventPreConditionsType.ACTIVE_AFTER_EVENT)
        self.event_id = event_id

#ACTIVE_AFTER_TIME = 4
class EventPreConditionActiveAfterTime(EventPreCondition):
    def __init__(self, time):
        super().__init__(EventPreConditionsType.ACTIVE_AFTER_TIME)
        self.time = time

#ACTIVE_WHEN_STATE = 5
class EventPreConditionActiveWhenState(EventPreCondition):
    def __init__(self, object_id, state_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_STATE)
        self.object_id = object_id
        self.state_id = state_id

#ACTIVE_WHEN_STATES = 6
class EventPreConditionActiveWhenNotState(EventPreCondition):
    def __init__(self, object_id, state_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_NOT_STATE)
        self.object_id = object_id
        self.state_id = state_id

#ACTIVE_WHEN_ITEM_IN_USE = 7  
class EventPreConditionActiveWhenItemInUse(EventPreCondition):
    def __init__(self, item_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_ITEM_IN_USE)
        self.item_id = item_id

#ACTIVE_WHEN_ITEM_NOT_IN_USE = 8
class EventPreConditionActiveWhenItemNotInUse(EventPreCondition):
    def __init__(self, item_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_ITEM_NOT_IN_USE)
        self.item_id = item_id

#CLICK_ITEM = 9
class EventPreConditionClickItem(EventPreCondition):
   def __init__(self, item_id):
        super().__init__(EventPreConditionsType.CLICK_ITEM)
        self.item_id = item_id 

#CLICKNOT = 10
class EventPreConditionClickNot(EventPreCondition):
    def __init__(self, object_id):
        super().__init__(EventPreConditionsType.CLICK_NOT)
        self.object_id = object_id

class EventPosCondition:
    def __init__(self,type):
        self.type = type

#ENDGAME = 0
class EventPosConditionEndGame(EventPosCondition):
    def __init__(self, message = ""):
        super().__init__(EventPosConditionsType.ENDGAME)
        #self.message = message

#CHANGE_STATE = 1
class EventPosConditionChangeState(EventPosCondition):
    def __init__(self, object_id, state_id):
        super().__init__(EventPosConditionsType.CHANGE_STATE)
        self.object_id = object_id
        self.state_id = state_id

#CHANGE_POSITION = 2
class EventPosConditionChangePosition(EventPosCondition):
    def __init__(self, object_id, position):
        super().__init__(EventPosConditionsType.CHANGE_POSITION)
        self.object_id = object_id
        self.position = position

#CHANGE_SIZE = 3
class EventPosConditionChangeSize(EventPosCondition):
    def __init__(self, object_id, size):
        super().__init__(EventPosConditionsType.CHANGE_SIZE)
        self.object_id = object_id
        self.size = size

#SHOW_MESSAGE = 4
class EventPosConditionShowMessage(EventPosCondition):
    def __init__(self, position, message):
        super().__init__(EventPosConditionsType.SHOW_MESSAGE)
        self.position = position
        self.message = message

#ASK_CODE = 5
class EventPosConditionAskCode(EventPosCondition):
    def __init__(self, code, message, sucess_event, fail_event):
        super().__init__(EventPosConditionsType.ASK_CODE)
        self.code = code
        self.message = message
        self.sucess_event = sucess_event
        self.fail_event = fail_event

#PUT_INVENTORY = 6
class EventPosConditionPutInventory(EventPosCondition):
    def __init__(self, object_id):
        super().__init__(EventPosConditionsType.PUT_INVENTORY)
        self.object_id = object_id

#CHANGE_SCENE = 7
class EventPosConditionChangeScene(EventPosCondition):
    def __init__(self, scene_id):
        super().__init__(EventPosConditionsType.CHANGE_SCENE)
        self.scene_id = scene_id

#ACTIVE_ITEM = 8
class EventPosConditionActiveItem(EventPosCondition):
    def __init__(self, item_id):
        super().__init__(EventPosConditionsType.ACTIVE_ITEM)
        self.item_id = item_id

#DESACTIVE_ITEM = 9
class EventPosConditionDesactiveItem(EventPosCondition):
    def __init__(self, item_id):
        super().__init__(EventPosConditionsType.DESACTIVE_ITEM)
        self.item_id = item_id

#DELETE_ITEM = 10
class EventPosConditionDeleteItem(EventPosCondition):
    def __init__(self, item_id):
        super().__init__(EventPosConditionsType.DELETE_ITEM)
        self.item_id = item_id

#DELETE_ITEM = 11
class EventPosConditionMotionItem(EventPosCondition):
    def __init__(self, item_id, back_position, trigger_item, sucess_event):
        super().__init__(EventPosConditionsType.MOTION)
        self.item_id = item_id
        self.back_position = back_position
        self.trigger_item = trigger_item
        self.sucess_event = sucess_event

class Event:
    def __init__(self, id : str, pre_conditions : [EventPreCondition], pos_conditions : [EventPosCondition], repeatable : bool, linked : bool = False):
       self.id = id
       self.pre_conditions = pre_conditions
       self.pos_conditions = pos_conditions
       self.repeatable = repeatable
       self.happen = False
       self.linked = linked


"""CLASSE AUXIALIRES"""
class Position():
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

class Size():
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y


"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id : str, src_image : str, size : Size, position : Position):
        self.id = id
        # Carregando a imagem da porta
        self.src_image = src_image
        self.image = pygame.image.load(self.src_image) 
        self.image = pygame.transform.scale(self.image, (size.x,size.y))  # Ajuste o tamanho conforme necessário
        self.position = position
        self.size = size

    def change_size(self, size):
        self.image = pygame.image.load(self.src_image) 
        self.image = pygame.transform.scale(self.image, (size.x,size.y))

    def change_position(self, position):
        self.position = position

"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id : str, scene_id : str, position : Position, size : Size):
        self.id = id
        self.current_state = None
        self.reference = scene_id
        self.position = position
        self.size = size
        self.states = {}

    def change_current_state(self, state_id : str):
        if (state_id in self.states):
            self.current_state = state_id
            self.position = self.states[state_id].position
            self.size = self.states[state_id].size
        else:
            self.current_state = None

    #Função que verifica se foi clicado na área do objeto
    def have_clicked(self, x : int, y : int):
        return self.position.x <= x <= self.position.x + self.size.x and self.position.y <= y <= self.position.y + self.size.y

    #Função que muda a posição do objeto
    def change_position(self,position : Position):
        self.position = position
        for state in self.states.values():
            state.change_position(position)

    #Função que muda o tamanho do objeto
    def change_size(self,size : Size):
        self.size = size
        for state in self.states.values():
            state.change_size(size)

    def add_state(self, state : State, initial : bool = False):
        self.states[state.id] = state
        if initial:
            self.change_current_state(state.id)

    def draw(self):
        if self.current_state != None:
            screen.blit(self.states[self.current_state].image, (self.position.x, self.position.y))

"""CLASSE DE CENA"""
class Scene:
    def __init__(self, id : str):
        self.id = id
        self.current_state = None
        self.states = {}

    def change_current_state(self, state_id : str):
        self.current_state = state_id
    
    def add_state(self, state : State, initial : bool = False):
        self.states[state.id] = state
        if initial:
            self.current_state = state.id

    def draw (self):
        screen.blit(self.states[self.current_state].image, (0,0))

"""CLASSE DE DO ESTADO DE UMA ESCAPE ROOM"""
class EscapeRoomState:
    def __init__(self):
        self.finish_game = False
        self.current_scene = None
        self.time = 0 #sec
        self.click_events = []
        self.events_happend = []
        self.changed_objects_states = {}
        self.current_scene_buffer = None
        self.messages = []
        self.input_active = False
        self.input_code = None
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.input_text = ""
        self.motion_actived = False
        self.item_motion = None

    def first_scene(self, scene_id : str):
        if self.current_scene == None:
            self.current_scene = scene_id
        
    def update_current_scene(self, scene_id : str):
        self.current_scene = scene_id
    
    def clear_input(self):
        self.input_active = False
        self.input_code = None
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.input_text = ""
    
"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title : str):
        self.title = title #TITULO
        self.scenes = {} 
        self.objects = {}
        self.events = {
        }
        self.events_buffer = {}
        self.er_state = EscapeRoomState() #ID DA CENA ATUAL

    #Função que adiciona uma cena
    def add_scene(self,scene : Scene):
        self.scenes[scene.id] = scene
        self.er_state.first_scene(scene.id)

    #Função que adiciona um objeto
    def add_object(self, object : Object):
        self.objects[object.id] = object

    #Função que adiciona um evento de cena
    def add_event(self, event : Event):
        self.events[event.id] = event
    
    #Função que adiciona um evento de cena
    def add_event_buffer(self, event : Event):
        self.events_buffer[event.id] = event

    #Função que muda a cena atual
    def change_current_scene(self,scene_id : str):
        if scene_id in self.scenes:
            self.er_state.update_current_scene(scene_id)
    
    #Função que desenha a cena atual
    def draw(self):
        #Desenhar a cena
        current_scene = self.er_state.current_scene
        self.scenes[current_scene].draw()

        #Desenhar objetos na cena
        for object in self.objects.values():
            #Se o objeto pertence à cena atual
            if current_scene == object.reference:
                object.draw()

    ##Função que muda o state atual de um object
    #def change_object_state(self, scene_id : str, object_id : str ,state_id : str):
    #    self.scenes[scene_id].change_object_state(object_id,state_id)

    def change_object_current_state(self, object_id : str, state_id):
        if object_id in self.objects:
            self.objects[object_id].change_current_state(state_id)

    def change_object_position(self, object_id : str, position : Position):
        if object_id in self.objects:
            self.objects[object_id].change_position(position)

    def change_object_size(self, object_id : str, size : Size):
        if object_id in self.objects:
            self.objects[object_id].change_size(size)

    def update_events(self):
        for event in self.er_state.events_happend:
            if event in self.events:
                self.events[event].happen = True
        
        for event in self.events_buffer.values():
            self.events[event.id] = event
        self.events_buffer = {}

        self.er_state.events_happend = []
    
    def update_states(self):
        for obj,state in self.er_state.changed_objects_states.items():
            self.change_object_current_state(obj,state)
        
        self.er_state.changed_objects_states = {}
#
    #Função que verifica se um evento happen
    def check_if_event_occurred(self,event_id : str):
        if event_id in self.events:
            return self.events[event_id].happen
    #
    #Função que devolve o state atual de um object
    def check_state_of_object(self, object_id : str, state_id : str):
        return self.objects[object_id].current_state == state_id
    
    def check_time (self, time):
        return time >= self.er_state.time
    
    def exist_object(self,object_id):
        return object_id in self.objects


# Classe para representar mensagens de balão de fala
class BalloonMessage:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def display(self):
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        pygame.draw.rect(screen, RED, (text_rect.left - 10, text_rect.top - 5, text_rect.width + 20, text_rect.height + 10))
        screen.blit(text_surface, text_rect)



class Item:
    def __init__(self, id : str, size : Size, state : State, slot : int):
        self.id = id
        self.size = Size(0,0)
        self.position = Position(0,0)
        if size.x >= size.y:
            self.size.x = 60
            self.size.y = size.y * 60 / size.x
        else:
            self.size.y = 60
            self.size.x = size.x * 60 / size.y
        
        self.position.x = (80-self.size.x) + 10+(slot*90)
        self.position.y = (80-self.size.x) + 10

        state.change_size(self.size)
        self.state = state

        self.in_use = False
    
    #Função que verifica se foi clicado na área do objeto
    def have_clicked(self, x : int, y : int):
        return self.position.x <= x <= self.position.x + self.size.x and self.position.y <= y <= self.position.y + self.size.y
    
    def draw(self):
        screen.blit(self.state.image, (self.position.x,self.position.y))
        if self.in_use:
            pygame.draw.rect(screen, RED, (self.position.x, self.position.y, 10, 10))

    def change_position(self, position : Position):
        self.position = position
            

# Classe Inventário
class Inventory:
    def __init__(self):
        self.items = 0
        self.slots = {}
        self.update_in_use = []
        self.update_add = []
        self.update_remove = []
        self.last_active = None

    def find_empty_slot(self):
        for slot,item in self.slots.items():
            if item == None:
                return slot
        return self.items

    def add(self, object, slot):
        self.slots[slot] = Item(object.id,object.size,object.states[object.current_state], slot)
        pre = EventPreConditionClickItem(object.id)
        pos = EventPosConditionMotionItem(object.id,self.slots[slot].position,"nota","aumentar_nota")

        room.add_event(Event("arrastar",[pre],[pos],True))
        self.items += 1
    
    def remove(self,item_id):
        for slot,item in self.slots.items():
            if item != None and item.id == item_id:
                self.slots[slot] = None
                self.items -= 1

    def active_item(self, item_id):
        for slot,item in self.slots.items():
            if item != None and item.id == item_id:
                if self.last_active != None:
                    self.update_in_use.append((self.last_active,False))
                self.update_in_use.append((slot,True)) #Coloca no buffer
                self.last_active = slot
                break
    
    def desactive_item(self, item_id):
        for slot,item in self.slots.items():
            if item != None and item.id == item_id:
                self.update_in_use.append((slot,False)) #Coloca no buffer
                break

    def update_items(self):
        for slot,in_use in self.update_in_use:
            if self.slots[slot] != None:
                self.slots[slot].in_use = in_use
        for (item,slot) in self.update_add:
            self.add(item,slot)
        for item in self.update_remove:
            self.remove(item)

        self.update_in_use = []
        self.update_add = []
        self.update_remove = []

    def check_item_in_use(self,item_id):
        for item in self.slots.values():
            if item != None and item.id == item_id:
                return item.in_use
        return False
    
    def get_item(self,item_id):
        for item in self.slots.values():
            if item != None and item.id == item_id:
                return item
        return None
    
    def exist_item(self,item_id):
        for item in self.slots.values():
            if item != None and item.id == item_id:
                return True
        return False

    def draw(self):
        pygame.draw.rect(screen, RED, (0, 0, 1300, 100))
        i = 1
        while True:
            x = 10+((i-1)*90)
            if x < 1300 - 80:
                pygame.draw.rect(screen, GREEN, (x, 10, 80, 80))
                i+=1
            else:
                break
        for item in self.slots.values():
            if item != None:
                item.draw()
        
inventory = Inventory()
__images = "../../images/"

import json
file = open("../../models/sample2.json")
jsonString = file.read()
escape_room_json = json.loads(jsonString)


# Inicialização do Pygame
pygame.init()

# Configurações do jogo

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room 2D")

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)

data_map = escape_room_json['map']
data_events = escape_room_json['events']

for room_id,data_room in data_map.items():
    (size_x,size_y) = data_room['size']
    scenes = data_room['scenes']
    room = EscapeRoom(room_id)
    for scene_id,data_scene in scenes.items():
        scene = Scene(scene_id)
        scene_states = data_scene['states']
        for ss_id,ss in scene_states.items():
            ss_filename = __images + ss['filename']
            ss_initial = ss['initial']
            scene.add_state(State(ss_id,ss_filename,Size(size_x,size_y),Position(0,0)),ss_initial)
        room.add_scene(scene)
        objects = data_scene['objects']
        for object_id,data_object in objects.items():
            (obj_size_x,obj_size_y) = data_object['size'] if 'size' in data_object else (None,None)
            (obj_pos_x,obj_pos_y) = data_object['position'] if 'position' in data_object else (None,None)
            obj_states = data_object['states']
            object = Object(object_id, scene_id, Position(obj_pos_x,obj_pos_y),Size(obj_size_x,obj_size_y))
            for os_id,os in obj_states.items():
                os_filename = __images + os['filename']
                os_initial = os['initial']
                (os_size_x,os_size_y) =  os['size'] if 'size' in os else (obj_size_x,obj_size_y)
                (os_pos_x,os_pos_y) =  os['position'] if 'position' in os else (obj_pos_x,obj_pos_y)
                object.add_state(State(os_id,os_filename,Size(os_size_x,os_size_y),Position(os_pos_x,os_pos_y)),os_initial) #TODO: estado para items
            room.add_object(object)

for event_id, data_event in data_events.items():
    data_preconditions = data_event['precondicoes']
    data_posconditions = data_event['poscondicoes']
    repeatable = data_event['repetivel']
    pre_conditions = []
    pos_conditions = []

    for data_condition in data_preconditions:
        type = data_condition['type']
        if type == "Click":
            object_id = data_condition['object']
            event_precondition = EventPreConditionClick(object_id)
        elif type == "ClickNot":
            object_id = data_condition['object']
            event_precondition = EventPreConditionClickNot(object_id)

        elif type == "WhenStateObject":
            object_id = data_condition['object']
            state_id = data_condition['state']
            event_precondition = EventPreConditionActiveWhenState(object_id,state_id)

        elif type == "WhenNotStateObject":
            object_id = data_condition['object']
            state_id = data_condition['state']
            event_precondition = EventPreConditionActiveWhenNotState(object_id,state_id)

        elif type == "ClickAfterEvent":
            object_id = data_condition['object']
            after_event_id = data_condition['event']
            event_precondition = EventPreConditionClickAfterEvent(object_id,after_event_id)
        elif type == 'ItemNotActived':
            item_id = data_condition['item']
            event_precondition = EventPreConditionActiveWhenItemNotInUse(item_id)
        elif type == 'ItemActived':
            item_id = data_condition['item']
            event_precondition = EventPreConditionActiveWhenItemInUse(item_id)
        
        pre_conditions.append(event_precondition)

    for data_action in data_posconditions:
        type = data_action['type']
        if type == "ChangeState":
            object_id = data_action['object']
            state_id = data_action['state']
            event_poscondition = EventPosConditionChangeState(object_id,state_id)
        elif type == "EndGame":
            event_poscondition = EventPosConditionEndGame()
        elif type == "PutInInventory":
            object_id = data_action['object']
            event_poscondition = EventPosConditionPutInventory(object_id)
        elif type == "DeleteItem":
            item_id = data_action['item']
            event_poscondition = EventPosConditionDeleteItem(item_id)
        elif type == 'ShowMessage':
            message = data_action['message']
            (msg_pos_x,msg_pos_y) = data_action['position']
            event_poscondition = EventPosConditionShowMessage(Position(msg_pos_x,msg_pos_y),message)
        elif type == 'AskCode':
            code = data_action['code']
            message = data_action['message']
            sucess_event = data_action['sucess_event']
            fail_event = data_action['fail_event']
            event_poscondition = EventPosConditionAskCode(code,message,sucess_event,fail_event)
        elif type == 'ChangeSize':
            object_id = data_action['object']
            (size_x,size_y) = data_action['size']
            event_poscondition = EventPosConditionChangeSize(object_id,Size(size_x,size_y))
        elif type == 'ChangePosition':
            object_id = data_action['object']
            (pos_x,pos_y) = data_action['position']
            event_poscondition = EventPosConditionChangePosition(object_id,Position(size_x,size_y))
        elif type == 'ChangeScene':
            scene_id = data_action['scene']
            event_poscondition = EventPosConditionChangeScene(scene_id)
        pos_conditions.append(event_poscondition)

    linked = 'linked' in data_event

    room.add_event(Event(event_id,pre_conditions,pos_conditions,repeatable, linked))




def test_precondition(precondition):
    type = precondition.type
    tested = False
    if type == EventPreConditionsType.CLICK:
        object_id = precondition.object_id
        if not object_id in room.objects:
            return tested
        object = room.objects[object_id]
        if object.reference == room.er_state.current_scene:
            for (px,py) in room.er_state.click_events:
                tested = object.have_clicked(px,py)
                if tested: break
    elif type == EventPreConditionsType.CLICK_NOT:
        object_id = precondition.object_id
        if not object_id in room.objects or len(room.er_state.click_events) == 0:
            return tested
        object = room.objects[object_id]
        tested = True
        if object.reference == room.er_state.current_scene:
            for (px,py) in room.er_state.click_events:
                tested = tested and not object.have_clicked(px,py)
    elif type == EventPreConditionsType.CLICK_ITEM:
        item_id = precondition.item_id
        item = inventory.get_item(item_id)
        if item != None:
            for (px,py) in room.er_state.click_events:
                tested = item.have_clicked(px,py)
                if tested: break
    elif type == EventPreConditionsType.ACTIVE_WHEN_STATE:
        object_id = precondition.object_id
        state_id = precondition.state_id
        tested = room.check_state_of_object(object_id,state_id)
    elif type == EventPreConditionsType.ACTIVE_WHEN_NOT_STATE:
        object_id = precondition.object_id
        state_id = precondition.state_id
        tested = not room.check_state_of_object(object_id,state_id)
    elif type == EventPreConditionsType.ACTIVE_WHEN_ITEM_IN_USE:
        
        item_id = precondition.item_id
        tested = inventory.check_item_in_use(item_id)
    elif type == EventPreConditionsType.ACTIVE_WHEN_ITEM_NOT_IN_USE:
        item_id = precondition.item_id
        tested = inventory.exist_item(item_id) or room.exist_object(item_id)
        tested = tested and not inventory.check_item_in_use(item_id)
    elif type == EventPreConditionsType.CLICK_AFTER_EVENT:
        object_id = precondition.object_id
        object = room.objects[object_id]
        clicked = False
        if object.reference == room.er_state.current_scene:
            for (px,py) in room.er_state.click_events:
                clicked = object.have_clicked(px,py)
                if clicked:
                    break
        if clicked:
            event_id = precondition.event_id
            tested = room.check_if_event_occurred(event_id)
    return tested

def do_poscondition(poscondition):
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
        
        #room.add_event_buffer(Event("desativar_"+object_id,[EventPreConditionClickItem(object_id),EventPreConditionActiveWhenItemInUse(object_id)],[EventPosConditionDesactiveItem(object_id)],True,False))
        #room.add_event_buffer(Event("ativar"+object_id,[EventPreConditionClickItem(object_id),EventPreConditionActiveWhenItemNotInUse(object_id)],[EventPosConditionActiveItem(object_id)],True,False))
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
    elif type == EventPosConditionsType.MOTION:
        item_id = poscondition.item_id
        room.er_state.motion_actived = True
        room.er_state.item_motion = item_id
        room.er_state.back_motion = poscondition.back_position
        room.er_state.trigger_motion = poscondition.trigger_item
        room.er_state.motion_sucess_event = poscondition.sucess_event
        debug("EVENT_MOTION_ITEM: Arrastando item "+item_id+".")
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

def do_event(event):
    for poscondition in event.pos_conditions:
        do_poscondition(poscondition)
    room.er_state.events_happend.append(event.id)

def try_do_events():
    for event in room.events.values():
        if event.linked:
            continue
        if not event.repeatable and event.happen:
            continue
        sucess_test = True
        for precondition in event.pre_conditions:
            if not test_precondition(precondition):
                sucess_test = False
                break
        if sucess_test:
            do_event(event)


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
                        do_event(room.events[room.er_state.input_sucess])
                    else:
                        do_event(room.events[room.er_state.input_fail])
                    room.er_state.clear_input()
                elif pygame_event.key == pygame.K_BACKSPACE:  # Verifica se o jogador pressionou Backspace
                    room.er_state.input_text = room.er_state.input_text[:-1]
                else:
                    room.er_state.input_text += pygame_event.unicode  # Adiciona a tecla pressionada à entrada do jogador
        elif pygame_event.type == pygame.MOUSEMOTION:
            if(room.er_state.motion_actived):
                room.er_state.last_motion = Position(pygame_event.pos[0],pygame_event.pos[1])
                item = inventory.get_item(room.er_state.item_motion)
                item.change_position(room.er_state.last_motion)

        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            if(room.er_state.motion_actived):
                room.er_state.motion_actived = False
                debug("Parando de arrastar")
                tobj = room.objects[room.er_state.trigger_motion]
                if(tobj.have_clicked(room.er_state.last_motion.x,room.er_state.last_motion.y)):
                    do_event(room.events[room.er_state.motion_sucess_event])
                
                item = inventory.get_item(room.er_state.item_motion)
                item.change_position(room.er_state.back_motion)

                #room.er_state.item_motion = item_id
                #room.er_state.back_motion = poscondition.back_position
                #room.er_state.trigger_motion = poscondition.trigger_position
                #room.er_state.motion_sucess_event = poscondition.sucess_event


    try_do_events()
    room.er_state.click_events = []
    room.update_events()
    room.update_states()
    inventory.update_items()
    if room.er_state.current_scene_buffer != None: 
        room.change_current_scene(room.er_state.current_scene_buffer)
        room.er_state.current_scene_buffer = None

    #Desenhar a room
    room.draw()
    
    inventory.draw()

    for message in room.er_state.messages:
        message.display()
    
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
