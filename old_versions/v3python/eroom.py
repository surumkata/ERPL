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
    def __init__(self, type : TriggerType):
        self.type = type

#Trigger clique simples
class Click(Trigger):
    def __init__(self):
        super().__init__(TriggerType.CLICK)

#Trigger clique após um evento ter ocorrido
class ClickAfterEvent(Trigger):
    def __init__(self,scene_id : str,object_id : str,event_id : str):
        super().__init__(TriggerType.CLICK_AFTER_EVENT)
        self.scene_id = scene_id
        self.object_id = object_id
        self.event_id = event_id

#Trigger clique quando um certo estado de um objeto
class ClickWhenStateOfObject(Trigger):
    def __init__(self,object_id : str, state_id : str):
        super().__init__(TriggerType.CLICK_WHEN_OBJECT_STATE)
        self.state_id = state_id
        self.object_id = object_id

#Trigger após um evento ter ocorrido
class AfterEvent(Trigger):
    def __init__(self,scene_id : str,object_id : str,event_id : str):
        super().__init__(TriggerType.AFTER_EVENT)
        self.scene_id = scene_id
        self.object_id = object_id
        self.event_id = event_id

#Trigger após um evento ter ocorrido
class AfterTime(Trigger):
    def __init__(self,time : int):
        super().__init__(TriggerType.AFTER_TIME)
        self.time = time

#Trigger clique após um evento ter ocorrido
class ClickAfterTime(Trigger):
    def __init__(self,time : int):
        super().__init__(TriggerType.CLICK_AFTER_TIME)
        self.time = time

"""CLASSE DE EVENTO"""
class Event:

    def __init__(self, id : str, trigger : Trigger, type : EventType, repeatable : bool):
        self.id = id
        self.trigger = trigger
        self.type = type
        self.repeatable = repeatable
        self.happen = False

#Evento que muda estados de um objeto
class EventChangeStates(Event):
    def __init__(self, id : str, trigger : Trigger, object_id : str, initial_state : str, final_state : str, repeatable : bool = True):
        super().__init__(id, trigger, EventType.EVENT_CHANGE_STATES, repeatable)
        self.object_id = object_id
        self.initial_state = initial_state
        self.final_state = final_state
        
#Evento que coloca objeto no inventario
class EventPutInInventario(Event):
    def __init__(self, id : str, trigger : Trigger):
        super().__init__(id, trigger,EventType.EVENT_PUT_IN_INVENTARIO, False) 

#Evento que mostra uma mensagem
class EventShowMessage(Event):
    def __init__(self, id : str, trigger : Trigger, message : str):
        super().__init__(id, trigger, EventType.EVENT_SHOW_MESSAGE, True) 
        self.message = message

#Evento que pede um código
class EventAskCode(Event):
    def __init__(self, id : str, trigger : Trigger , message : str, code : str, hit_event_id : str, miss_event_id : str):
        super().__init__(id, trigger, EventType.EVENT_ASK_CODE, True) 
        self.message = message
        self.code = code
        self.hit_event = hit_event_id
        self.miss_event = miss_event_id

#Evento que finaliza um jogo
class EventEndGame(Event):
    def __init__(self,id : str,trigger : Trigger):
        super().__init__(id, trigger, EventType.EVENT_END_GAME, False)

#Evento que altera a posicao de um objeto
class EventChangePosition(Event):
    def __init__(self,id : str,trigger : Trigger, position : Position):
        super().__init__(id, trigger, EventType.EVENT_CHANGE_POSITION, False)
        self.position = position

#Evento que altera a posicao de um objeto
class EventChangeSize(Event):
    def __init__(self,id : str,trigger : Trigger, size : Size):
        super().__init__(id, trigger, EventType.EVENT_CHANGE_SIZE, False)
        self.size = size

"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id, src_image, size):
        self.id = id
        # Carregando a imagem da porta
        self.image = pygame.image.load(src_image)  # Substitua "door.png" pelo nome da sua imagem da porta
        self.image = pygame.transform.scale(self.image, (size.x,size.y))  # Ajuste o tamanho conforme necessário

"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id : str, position : Position, size : Size):
        self.id = id
        self.states = {}
        self.events = {}
        self.position = position
        self.size = size
        self.current_state = None

    #Função que adiciona um estado ao objeto
    def add_state(self,state_id : str, src_image : str):
        state = State(state_id,src_image,self.size)
        self.states[state_id] = state
        if self.current_state == None:
            self.current_state = state_id
    
    #Função que adiciona um evento ao objeto
    def add_event(self,event : Event):
        self.events[event.id] = event

    #Função que verifica se foi clicado na área do objeto
    def have_clicked(self, x : int, y : int):
        return self.position.x <= x <= self.position.x + self.size.x and self.position.y <= y <= self.position.y + self.size.y
    
    #Função que muda a posição do objeto
    def change_position(self,position : Position):
        self.position = position

    #Função que muda o tamanho do objeto
    def change_size(self,size : Size):
        self.size = size

    #Função que desenha o objeto (usando o estado atual)
    def draw(self):
        if(self.current_state != None):
            screen.blit(self.states[self.current_state].image, (self.position.x, self.position.y))
    
    #Função que altera o estado atual do objeto
    def change_current_state(self,state_id : str):
        if state_id in self.states or state_id == None:
            self.current_state = state_id
    
    #Função que coloca um evento como ocurrido
    def happened_event(self, event_id : str):
        self.events[event_id].happen = True

    #Função que devolve o estado atual de um object
    def get_current_state(self):
        return self.current_state
    
    #Função que verifica se um evento aconteceu
    def check_if_event_occurred(self,event_id : str):
        return self.events[event_id].happen

"""CLASSE DE CENA"""
class Scene:
    def __init__(self, id, src_image):
        self.id = id
        self.objects = {}
        self.background = pygame.image.load(src_image)
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
    
    def add_object(self,object : Object):
        self.objects[object.id] = object

    def draw(self):
        # Desenhar a imagem de fundo
        screen.blit(self.background, (0, 0))

        # Desenhar todos os objects da cena
        for object in self.objects.values():
            object.draw()

    #Função que muda o state atual de um object
    def change_object_state(self,object_id : str,state_id : str):
        self.objects[object_id].change_current_state(state_id)

    #Função que coloca um evento como ocurrido
    def happened_event(self,object_id : str,event_id : str):
        self.objects[object_id].happened_event(event_id)

    #Função que verifica se um evento aconteceu
    def check_if_event_occurred(self,object_id : str,event_id : str):
        return self.objects[object_id].check_if_event_occurred(event_id)

    #Função que devolve o state atual de um object
    def get_current_state_of_object(self,object_id : str):
        return self.objects[object_id].get_current_state()

"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title : str):
        self.title = title #TITULO
        self.scenes = {} #CENAS (DICIONARIO [CHAVE = ID DA CENA])
        self.current_scene = None #ID DA CENA ATUAL
        self.finish_game = False

    #Função que adiciona uma cena
    def add_scene(self,scene : Scene):
        self.scenes[scene.id] = scene
        if self.current_scene == None: #Se for a primeira cena a ser adicionar fica a atual
            self.current_scene = scene.id

    def add_object(self,scene_id : str, object : Object):
        if scene_id in self.scenes:
            self.scenes[scene_id].add_object(object)
    
    #Função que muda a cena atual
    def change_current_scene(self,scene_id : str):
        if scene_id in self.scenes:
            self.current_scene = scene_id
    
    #Função que desenha a cena atual
    def draw(self):
        self.scenes[self.current_scene].draw()

    #Função que muda o state atual de um object
    def change_object_state(self, scene_id : str, object_id : str ,state_id : str):
        self.scenes[scene_id].change_object_state(object_id,state_id)
    
    #Função que coloca um evento como ocurrido
    def happened_event(self,scene_id : str,object_id : str ,event_id : str):
        self.scenes[scene_id].happened_event(object_id,event_id)

    #Função que verifica se um evento happen
    def check_if_event_occurred(self,scene_id : str,object_id : str,event_id : str):
        return self.scenes[scene_id].check_if_event_occurred(object_id,event_id)
    
    #Função que devolve o state atual de um object
    def get_current_state_of_object(self,scene_id : str,object_id : str):
        return self.scenes[scene_id].get_current_state_of_object(object_id)

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
    scene = Scene(cena, background)
    cenas[cena] = scene
    aux[cena] = []

for objeto,atributos in objetos.items():
    (px,py) = atributos['POSICAO']
    (sx,sy) = atributos['TAMANHO']
    scene_id = atributos['REFERENTE']
    object = Object(objeto,Position(px,py),Size(sx,sy))
    objetos[objeto] = object
    aux[scene_id].append(objeto)

for estado,atributos in estados.items():
    object_id = atributos['REFERENTE']
    imagem = __images + atributos['IMAGEM'][1:-1]
    objetos[object_id].add_state(estado,imagem)
    if 'estado_inicial' in atributos and atributos['estado_inicial']:
        objetos[object_id].change_current_state(estado)

for gatilho,atributos in gatilhos.items():
    type = atributos['TIPO']
    if type == 'CLIQUE':
        gatilhos[gatilho] = Click()

    elif type == 'CLIQUE_DEPOIS_DE_EVENTO':
        scene_id = atributos['CENA']
        object_id = atributos['OBJETO']
        event_id = atributos['EVENTO']
        gatilhos[gatilho] = ClickAfterEvent(scene_id,object_id,event_id)

    elif type == 'CLIQUE_QUANDO_ESTADO_DE_OBJETO':
        object_id = atributos['OBJETO']
        state_id = atributos['ESTADO']
        gatilhos[gatilho] = ClickWhenStateOfObject(object_id,state_id)
    
    elif type == 'DEPOIS_DE_EVENTO':
        scene_id = atributos['CENA']
        object_id = atributos['OBJETO']
        event_id = atributos['EVENTO']
        gatilhos[gatilho] = AfterEvent(scene_id,object_id,event_id)

for evento, atributos in eventos.items():
    type = atributos['TIPO']
    referente = atributos['REFERENTE']
    if type == 'MUDAR_ESTADOS':
        object_id = atributos['OBJETO']
        estado_inicial = atributos['ESTADO_INICIAL']
        estado_final = atributos['ESTADO_FINAL']
        gatilho_id = atributos['GATILHO']
        objetos[referente].add_event(EventChangeStates(evento,
                                            gatilhos[gatilho_id],
                                            object_id,
                                            estado_inicial,
                                            estado_final,
                                            repeatable=True)) #TODO:ADD À GRAM

    elif type == 'COLOCA_NO_INVENTARIO':
        gatilho_id = atributos['GATILHO']
        objetos[referente].add_event(EventPutInInventario(evento,
                                            gatilhos[gatilho_id]))

    elif type == 'FIM_DE_JOGO':
        gatilho_id = atributos['GATILHO']
        objetos[referente].add_event(EventEndGame(evento,
                                            gatilhos[gatilho_id]))

    elif type == 'PEDIR_CODIGO':
        pass

    elif type == 'MOSTRAR_MENSAGEM':
        pass


for cena,objetos_da_cena in aux.items():
    for objeto_id in objetos_da_cena:
        cenas[cena].add_object(objetos[objeto_id])
    room.add_scene(cenas[cena])


# Posição do inventário
inventory_x, inventory_y = 10, 10

#Dicionarios auxiliares
buffer_happen_events = {}
buffer_changed_objects_states = {}

def is_click_trigger(trigger_type):
    return trigger_type == TriggerType.CLICK or trigger_type == TriggerType.CLICK_AFTER_EVENT or trigger_type == TriggerType.CLICK_WHEN_OBJECT_STATE

def check_trigger(trigger):
    #Se o tipo de gatilho de evento é apenas clique
    if trigger.type == TriggerType.CLICK:
        return True
    #Se o tipo de gatilho de evento é clique depois de evento
    elif trigger.type == TriggerType.CLICK_AFTER_EVENT:
        #Verificar se o evento do gatilho já ocorreu
        return room.check_if_event_occurred(trigger.scene_id,trigger.object_id,trigger.event_id)
    #Se o tipo de gatilho de evento é Clique quando estado de objeto
    elif trigger.type == TriggerType.CLICK_WHEN_OBJECT_STATE:
        #Verificar se o estado de objeto do gatilho é igual ao estado atual do objeto
        return room.get_current_state_of_object(room.current_scene,trigger.object_id) == trigger.state_id
    elif trigger.type == TriggerType.AFTER_EVENT:
        #Verificar se o evento do gatilho já ocorreu
        return room.check_if_event_occurred(trigger.scene_id,trigger.object_id,trigger.event_id)
    elif trigger.type == TriggerType.AFTER_TIME:
        #verificar se o tempo do gatilho já passou
        #TODO:
        return False

def try_do_event(object, event):
    if not event.happen or event.repeatable:
        if check_trigger(event.trigger):
            do_event(object,event)

def do_event(object,event):
    #Verificar o tipo de evento é mudança de estados
    if event.type == EventType.EVENT_CHANGE_STATES:
        #VERIFICAR SE ESTADO INICIAL BATE CERTO COM O ATUAL
        if event.initial_state == room.get_current_state_of_object(room.current_scene, event.object_id):
            buffer_changed_objects_states[event.object_id] = event.final_state #colocar no buffer o estado do objeto para ser posteriormente alterado
            buffer_happen_events[event.id] = object.id #colocar o evento no buffer para ser atualizado (que aconteceu  
    elif event.type == EventType.EVENT_SHOW_MESSAGE:
        pass
        #TODO  
    #Verficar se o evento é do tipo colocar no inventario
    elif event.type == EventType.EVENT_PUT_IN_INVENTARIO:
        #TODO:COLOCAR POSICAO NO INVENTARIO
        object.change_position(Position(inventory_x,inventory_y)) #Mudar a posicao do objeto para a do slot no inventario
        buffer_happen_events[event.id] = object.id #colocar o evento no buffer para ser atualizado (que aconteceu  
    
    #Verificar se o evento é do tipo pedir codigo
    elif event.type == EventType.EVENT_ASK_CODE:
        pass
        #TODO

    #Verificar se o tipo de evento é "fim de jogo"
    elif event.type == EventType.EVENT_END_GAME:
        room.finish_game = True

    #Verificar se o evento é do tipo mudar posicao
    elif event.type == EventType.EVENT_CHANGE_POSITION:
        object.change_position(Position(event.position.x,event.position.y))  #Mudar a posicao do objeto
        buffer_happen_events[event.id] = object.id #colocar o evento no buffer para ser atualizado (que aconteceu 
    
    #Verificar se o evento é do tipo mudar tamanho
    elif event.type == EventType.EVENT_CHANGE_SIZE:
        object.change_size(Size(event.size.x,event.size.y))  #Mudar o tamanho do objeto
        buffer_happen_events[event.id] = object.id #colocar o evento no buffer para ser atualizado (que aconteceu 


update = False
running = True
# Loop principal do jogo
while running:
    for pygame_event in pygame.event.get():
        #Carregar em fechar jogo = encerra o jogo
        if pygame_event.type == pygame.QUIT:
            running = False
        
        #Evento c/ gatilho clique
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            
            for object in room.scenes[room.current_scene].objects.values():
                if object.have_clicked(pygame_event.pos[0],pygame_event.pos[1]):
                    for event in object.events.values():
                        if is_click_trigger(event.trigger.type):
                            try_do_event(object,event)

            #Atualizar os eventos que occorreram com o clique
            for event_id,object_id in buffer_happen_events.items():
                room.happened_event(room.current_scene,object_id,event_id)
                if not update: update = True
            #Atualizar os estados que mudaram com o clique
            for object_id,state_id in buffer_changed_objects_states.items():
                room.change_object_state(room.current_scene,object_id,state_id)
                if not update: update = True
            # RESET BUFFERS
            buffer_happen_events = {}
            buffer_changed_objects_states = {}
        
        #Eventos com gatilhos "temporais"
        if update:
            update = False
            #Percorrer todos os eventos com gatilhos especiais
            for object in room.scenes[room.current_scene].objects.values():
                for event in object.events.values():
                    if not is_click_trigger(event.trigger.type):
                            try_do_event(object,event)
    
    #Desenhar a room
    room.draw()

    #Tela de fim de jogo
    if room.finish_game:
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido/
        font = pygame.font.Font(None, 36)
        text = font.render("Você Escapou!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)    
    
    pygame.display.flip()

# Encerramento do jogo
pygame.quit()
sys.exit()
