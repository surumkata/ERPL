import pygame
import sys
from enum import Enum

WIDTH, HEIGHT = 1300, 700

"""TIPOS DE GATILHO (TRIGGER) DE EVENTO"""
class TriggerType(Enum):
    CLICK = 0
    CLICK_AFTER_EVENT = 1
    CLICK_WHEN_OBJECT_STATE = 2
    AFTER_EVENT = 3
    AFTER_TIME = 4
    CLICK_AFTER_TIME = 5


"""TIPOS DE EVENTOS"""
class EventType(Enum):
    EVENT_CHANGE_STATES = 0
    EVENT_PUT_IN_INVENTARIO = 1
    EVENT_SHOW_MESSAGE = 2
    EVENT_ASK_CODE = 3
    EVENT_END_GAME = 4
    EVENT_CHANGE_POSITION = 5
    EVENT_CHANGE_SIZE = 6


"""CLASSE AUXIALIRES"""
class Position():
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

class Size():
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

"""CLASSE DE GATILHO (TRIGGER)"""
class Trigger():
    def __init__(self, type : TriggerType, reference_id : str, event_id : str):
        self.type = type
        self.reference = reference_id
        self.event = event_id

#Trigger clique simples
class Click(Trigger):
    def __init__(self, reference_id : str, event_id : str):
        super().__init__(TriggerType.CLICK, reference_id, event_id)

#Trigger clique após um evento ter ocorrido
class ClickAfterEvent(Trigger):
    def __init__(self, reference_id : str, event_id : str,after_event_id : str):
        super().__init__(TriggerType.CLICK_AFTER_EVENT, reference_id, event_id)
        self.after_event_id = after_event_id

#Trigger clique quando um certo estado de um objeto
class ClickWhenStateOfObject(Trigger):
    def __init__(self, reference_id : str, event_id : str,object_id : str, state_id : str):
        super().__init__(TriggerType.CLICK_WHEN_OBJECT_STATE,reference_id,event_id)
        self.state_id = state_id
        self.object_id = object_id

#Trigger após um evento ter ocorrido
class AfterEvent(Trigger):
    def __init__(self,reference_id : str, event_id : str,after_event_id : str):
        super().__init__(TriggerType.AFTER_EVENT, reference_id, event_id)
        self.after_event_id = after_event_id

#Trigger após um evento ter ocorrido
class AfterTime(Trigger):
    def __init__(self,reference_id : str, event_id : str,time : int):
        super().__init__(TriggerType.AFTER_TIME,reference_id,event_id)
        self.time = time

#Trigger clique após um evento ter ocorrido
class ClickAfterTime(Trigger):
    def __init__(self,reference_id : str, event_id : str,time : int):
        super().__init__(TriggerType.CLICK_AFTER_TIME,reference_id,event_id)
        self.time = time

"""CLASSE DE EVENTO"""
class Event:

    def __init__(self, id : str, type : EventType, repeatable : bool):
        self.id = id
        self.type = type
        self.repeatable = repeatable
        self.happen = False

#Evento que muda estados de um objeto
class EventChangeStates(Event):
    def __init__(self, id : str, object_id : str, initial_state : str, final_state : str, repeatable : bool = True):
        super().__init__(id, EventType.EVENT_CHANGE_STATES, repeatable)
        self.object_id = object_id
        self.initial_state = initial_state
        self.final_state = final_state
        
#Evento que coloca objeto no inventario
class EventPutInInventario(Event):
    def __init__(self, id : str, object_id : str):
        super().__init__(id,EventType.EVENT_PUT_IN_INVENTARIO, False) 
        self.object_id = object_id

#Evento que mostra uma mensagem
class EventShowMessage(Event):
    def __init__(self, id : str, message : str, object_id : str = None, position : Position = None):
        super().__init__(id, EventType.EVENT_SHOW_MESSAGE, True) 
        self.message = message

#Evento que pede um código
class EventAskCode(Event):
    def __init__(self, id : str, message : str, code : str, hit_event_id : str, miss_event_id : str):
        super().__init__(id, EventType.EVENT_ASK_CODE, True) 
        self.message = message
        self.code = code
        self.hit_event = hit_event_id
        self.miss_event = miss_event_id

#Evento que finaliza um jogo
class EventEndGame(Event):
    def __init__(self,id : str, message : str):
        super().__init__(id, EventType.EVENT_END_GAME, False)
        self.message = message

#Evento que altera a posicao de um objeto
class EventChangePosition(Event):
    def __init__(self,id : str, position : Position, object_id : str):
        super().__init__(id, EventType.EVENT_CHANGE_POSITION, False)
        self.position = position
        self.object_id = object_id

#Evento que altera a posicao de um objeto
class EventChangeSize(Event):
    def __init__(self,id : str, size : Size, object_id : str):
        super().__init__(id, EventType.EVENT_CHANGE_SIZE, False)
        self.size = size
        self.object_id = object_id

"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id : str, src_image : str, size : Size, reference_id : str):
        self.id = id
        # Carregando a imagem da porta
        self.image = pygame.image.load(src_image)  # Substitua "door.png" pelo nome da sua imagem da porta
        self.image = pygame.transform.scale(self.image, (size.x,size.y))  # Ajuste o tamanho conforme necessário
        self.reference = reference_id

"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id : str, scene_id : str, position : Position, size : Size):
        self.id = id
        self.current_state = None
        self.reference = scene_id
        self.position = position
        self.size = size

    def change_current_state(self, state_id : str):
        self.current_state = state_id

    #Função que verifica se foi clicado na área do objeto
    def have_clicked(self, x : int, y : int):
        return self.position.x <= x <= self.position.x + self.size.x and self.position.y <= y <= self.position.y + self.size.y

    #Função que muda a posição do objeto
    def change_position(self,position : Position):
        self.position = position

    #Função que muda o tamanho do objeto
    def change_size(self,size : Size):
        self.size = size

"""CLASSE DE CENA"""
class Scene:
    def __init__(self, id : str):
        self.id = id
        self.current_state = None

    def change_current_state(self, state_id : str):
        self.current_state = state_id

"""CLASSE DE DO ESTADO DE UMA ESCAPE ROOM"""
class EscapeRoomState:
    def __init__(self):
        self.finish_game = False
        self.current_scene = None
        self.time = 0 #sec
        self.events_happend = []
        self.changed_objects_states = {}
    
    def first_scene(self, scene_id : str):
        if self.current_scene == None:
            self.current_scene = scene_id
        
    def update_current_scene(self, scene_id : str):
        self.current_scene = scene_id
    
"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title : str):
        self.title = title #TITULO
        self.scenes = {} 
        self.objects = {}
        self.states = {
            "scene" : {},
            "object" : {}
        } 
        self.events = {
            "scene" : {},
            "object" : {}
        }  
        self.triggers = {
            "click" : {
                'object' : [],
                'scene' : []
            },
            "passive" : []
        } 
        self.er_state = EscapeRoomState() #ID DA CENA ATUAL

    #Função que adiciona uma cena
    def add_scene(self,scene : Scene):
        self.scenes[scene.id] = scene
        self.er_state.first_scene(scene.id)

    #Função que adiciona um objeto
    def add_object(self, object : Object):
        self.objects[object.id] = object

    #Função que adiciona um evento de cena
    def add_event(self, event : Event, ref_scene : bool = False, ref_object : bool = False):
        ref = 'scene' if ref_scene else 'object' if ref_object else None
        self.events[ref][event.id] = event
    
    #Função que adiciona um estado de cena
    def add_state(self, state_id, ref_id, src_image, ref_scene : bool = False, ref_object : bool = False):

        if(ref_scene):
            size = Size(1280,720) #TODO:
            state = State(state_id,src_image,size,ref_id)
            self.states['scene'][state.id] = state
        elif(ref_object): 
            size = self.objects[ref_id].size
            state = State(state_id,src_image,size,ref_id)
            self.states['object'][state.id] = state
    
    #Função que adiciona um gatilho
    def add_trigger(self, trigger : Trigger, ref_scene : bool = False, ref_object : bool = False, click_trigger : bool = False, passive_trigger : bool = False):
        ref = 'scene' if ref_scene else 'object' if ref_object else None
        type = 'click' if click_trigger else 'passive' if passive_trigger else None
        
        if(click_trigger): self.triggers['click'][ref].append(trigger)
        elif(passive_trigger): self.trigger['passive'].append(trigger)

    #Função que muda a cena atual
    def change_current_scene(self,scene_id : str):
        if scene_id in self.scenes:
            self.er_state.update_current_scene(scene_id)
    
    #Função que desenha a cena atual
    def draw(self):
        #Desenhar a cena
        current_scene = self.er_state.current_scene
        current_scene_state_id = self.scenes[current_scene].current_state
        scene_state = self.states['scene'][current_scene_state_id]
        screen.blit(scene_state.image, (0,0))

        #Desenhar objetos na cena
        for object in self.objects.values():
            #Se o objeto pertence à cena atual
            if current_scene == object.reference:
                current_object_state_id = object.current_state
                if current_object_state_id != None:
                    obj_state = self.states['object'][current_object_state_id]
                    screen.blit(obj_state.image, (object.position.x, object.position.y))


    def get_event(self,event_id : str):
        if event_id in self.events['scene']:
            return self.events['scene'][event_id]
        elif event_id in self.events['object']:
            return self.events['object'][event_id]
        else: return None

    ##Função que muda o state atual de um object
    #def change_object_state(self, scene_id : str, object_id : str ,state_id : str):
    #    self.scenes[scene_id].change_object_state(object_id,state_id)

    def change_object_current_state(self, object_id : str, state_id):
        if object_id in self.objects and state_id in self.states['object']:
            self.objects[object_id].change_current_state(state_id)


    def change_object_position(self, object_id : str, position : Position):
        self.objects[object_id].change_position(position)

    def change_object_size(self, object_id : str, size : Size):
        self.objects[object_id].change_size(size)

    def update_events(self):
        for event in self.er_state.events_happend:
            if event in self.events['object']:
                self.events['object'][event].happen = True
            elif event in self.events['scene']:
                self.events['scene'][event].happen = True
        
        self.er_state.events_happend = []
    
    def update_states(self):
        for obj,state in self.er_state.changed_objects_states.items():
            self.change_object_current_state(obj,state)
        
        self.er_state.changed_objects_states = {}
#
    #Função que verifica se um evento happen
    def check_if_event_occurred(self,event_id : str):
        if event_id in self.events['scene']:
            return self.events['scene'][event_id].happen
        elif event_id in self.events['object']:
            return self.events['object'][event_id].happen 
    #
    #Função que devolve o state atual de um object
    def check_state_of_object(self, object_id : str, state_id : str):
        return self.objects[object_id].current_state == state_id
    
    def check_time (self, time):
        return time >= self.er_state.time

__images = "../../images/"

import json
file = open("../../models/sample.json")
jsonString = file.read()
escape_room = json.loads(jsonString)


# Inicialização do Pygame
pygame.init()

# Configurações do jogo

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room 2D")

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

room = EscapeRoom('Escape Room')
cenas = escape_room['CENA']
objetos = escape_room['OBJETO']
eventos = escape_room['EVENTO']
estados = escape_room['ESTADO']
gatilhos = escape_room['GATILHO']

aux = {}

for cena,atributos in cenas.items():
    background = __images + atributos['BACKGROUND'][1:-1]
    scene = Scene(cena)
    scene.change_current_state("background")
    room.add_scene(scene)
    room.add_state("background",cena,background,ref_scene=True)

for objeto,atributos in objetos.items():
    (px,py) = atributos['POSICAO']
    (sx,sy) = atributos['TAMANHO']
    scene_id = atributos['REFERENTE']
    object = Object(objeto,scene_id,Position(px,py),Size(sx,sy))
    room.add_object(object)

for estado,atributos in estados.items():
    ref_id = atributos['REFERENTE']
    imagem = __images + atributos['IMAGEM'][1:-1]
    room.add_state(estado,ref_id,imagem,ref_object=True)
    if 'estado_inicial' in atributos and atributos['estado_inicial']:
        room.change_object_current_state(ref_id,estado)

for atributos in gatilhos.values():
    type = atributos['TIPO']
    referente = atributos['REFERENTE']
    evento = atributos['EVENTO']
    if type == 'CLIQUE':
        gatilho = Click(referente,evento)
        room.add_trigger(gatilho,ref_object=True,click_trigger=True)

    elif type == 'CLIQUE_DEPOIS_DE_EVENTO':
        after_event = atributos['AFTER_EVENTO']
        gatilho = ClickAfterEvent(referente,evento,after_event)
        room.add_trigger(gatilho,ref_object=True,click_trigger=True)

    elif type == 'CLIQUE_QUANDO_ESTADO_DE_OBJETO':
        object_id = atributos['OBJETO']
        state_id = atributos['ESTADO']
        gatilho = ClickWhenStateOfObject(referente,evento,object_id,state_id)
        room.add_trigger(gatilho,ref_object=True,click_trigger=True)
    
    elif type == 'DEPOIS_DE_EVENTO':
        after_event = atributos['AFTER_EVENTO']
        gatilho = AfterEvent(referente,evento,after_event)
        room.add_trigger(gatilho,ref_object=True,passive_trigger=True)

for evento, atributos in eventos.items():
    type = atributos['TIPO']
    if type == 'MUDAR_ESTADOS':
        object_id = atributos['OBJETO']
        estado_inicial = atributos['ESTADO_INICIAL']
        estado_final = atributos['ESTADO_FINAL']
        room.add_event(EventChangeStates(evento,object_id,estado_inicial,estado_final,repeatable=True),ref_object=True)

    elif type == 'COLOCA_NO_INVENTARIO':
        object_id = atributos['OBJETO']
        room.add_event(EventPutInInventario(evento,object_id),ref_object=True)

    elif type == 'FIM_DE_JOGO':
        mensagem = atributos['MENSAGEM']
        room.add_event(EventEndGame(evento,mensagem),ref_object=True)

    elif type == 'PEDIR_CODIGO':
        pass

    elif type == 'MOSTRAR_MENSAGEM':
        pass


# Posição do inventário
inventory_x, inventory_y = 10, 10

def is_click_trigger(trigger_type):
    return trigger_type == TriggerType.CLICK or trigger_type == TriggerType.CLICK_AFTER_EVENT or trigger_type == TriggerType.CLICK_WHEN_OBJECT_STATE

def check_trigger(trigger):
    #Se o tipo de gatilho de evento é apenas clique
    if trigger.type == TriggerType.CLICK:
        return True
    #Se o tipo de gatilho de evento é clique depois de evento ou depois de evento
    elif trigger.type == TriggerType.CLICK_AFTER_EVENT or trigger.type == TriggerType.AFTER_EVENT:
        #Verificar se o evento do gatilho já ocorreu
        return room.check_if_event_occurred(trigger.after_event_id)
    #Se o tipo de gatilho de evento é Clique quando estado de objeto
    elif trigger.type == TriggerType.CLICK_WHEN_OBJECT_STATE:
        #Verificar se o estado de objeto do gatilho é igual ao estado atual do objeto
        return room.check_state_of_object(trigger.object_id,trigger.state_id)
    #Se o tipo de gatilho é depois de um tempo ou clique depois de um tempo
    elif trigger.type == TriggerType.AFTER_TIME or trigger.type == TriggerType.CLICK_AFTER_TIME:
        #verificar se o tempo do gatilho já passou
        return room.check_time(trigger.time)

def do_event(event):
    #Verificar o tipo de evento é mudança de estados
    if event.type == EventType.EVENT_CHANGE_STATES:
        #VERIFICAR SE ESTADO INICIAL BATE CERTO COM O ATUAL
        if room.check_state_of_object(event.object_id,event.initial_state):
            room.er_state.changed_objects_states[event.object_id] = event.final_state #colocar no buffer o estado do objeto para ser posteriormente alterado
            room.er_state.events_happend.append(event.id)
    elif event.type == EventType.EVENT_SHOW_MESSAGE:
        pass
        #TODO  
    #Verficar se o evento é do tipo colocar no inventario
    elif event.type == EventType.EVENT_PUT_IN_INVENTARIO:
        #TODO:COLOCAR POSICAO NO INVENTARIO
        room.change_object_position(event.object_id, Position(inventory_x,inventory_y)) #Mudar a posicao do objeto para a do slot no inventario
        room.er_state.events_happend.append(event.id)
    
    #Verificar se o evento é do tipo pedir codigo
    elif event.type == EventType.EVENT_ASK_CODE:
        pass
        #TODO

    #Verificar se o tipo de evento é "fim de jogo"
    elif event.type == EventType.EVENT_END_GAME:
        room.er_state.finish_game = True

    #Verificar se o evento é do tipo mudar posicao
    elif event.type == EventType.EVENT_CHANGE_POSITION:
        room.change_object_position(event.object_id, Position(event.position.x,event.position.y)) #Mudar a posicao do objeto
        room.er_state.events_happend.append(event.id)
    
    #Verificar se o evento é do tipo mudar tamanho
    elif event.type == EventType.EVENT_CHANGE_SIZE:
        room.change_object_size(event.object_id, Size(event.size.x,event.size.y)) #Mudar o tamanho do objeto
        room.er_state.events_happend.append(event.id)


running = True
# Loop principal do jogo
while running:
    for pygame_event in pygame.event.get():
        #Carregar em fechar jogo = encerra o jogo
        if pygame_event.type == pygame.QUIT:
            running = False
        
        #Evento c/ gatilho clique
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            clicked_on_object = False

            for object in room.objects.values():
                #Se clicou no objeto
                if object.have_clicked(pygame_event.pos[0],pygame_event.pos[1]):
                    #Passar por todos os gatilhos clicaveis
                    for trigger in room.triggers['click']['object']:
                        #Se o gatilho clicavel for deste objeto
                        if trigger.reference == object.id:
                            #Checa-se o gatilho
                            if check_trigger(trigger):
                                event = room.get_event(trigger.event)
                                print(trigger.event)
                                if not event.happen or event.repeatable:
                                    #Faz-se o evento
                                    do_event(event)

            room.update_events()
            room.update_states()
        
        #Percorrer todos os gatilhos passivos
        passive_triggers = room.triggers['passive']
        done_event = True
        while(done_event):
            done_event = False
            i = 0
            for trigger in passive_triggers:
                if check_trigger():
                    event = room.get_event(trigger.event)
                    if not event.happen or event.repeatable:
                        #Faz-se o evento
                        do_event(event)
                        done_event = True
                        room.update_events()
                        room.update_states()
                        passive_triggers.pop(i)
                        break
                i+=1
    
    #Desenhar a room
    room.draw()

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
