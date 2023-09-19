import pygame
import sys
from enum import Enum


WIDTH, HEIGHT = 1300, 700


"""TIPOS DE GATILHO (TRIGGER) DE EVENTO"""
class TriggerType(Enum):
    CLICK = 0
    CLICK_AFTER_EVENT = 1
    CLICK_WHEN_OBJECT_STATE = 2


"""TIPOS DE EVENTOS"""
class EventType(Enum):
    EVENT_CHANGE_STATES = 0
    EVENT_PUT_IN_INVENTARIO = 1
    EVENT_SHOW_MESSAGE = 2
    EVENT_ASK_CODE = 3
    EVENT_END_GAME = 4


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
    def __init__(self, id : str, trigger : Trigger , message : str, code : str):
        super().__init__(id, trigger, EventType.EVENT_ASK_CODE, True) 
        self.message = message
        self.code = code

#Evento que finaliza um jogo
class EventEndGame(Event):
    def __init__(self,id : str,trigger : Trigger):
        super().__init__(id, trigger, EventType.EVENT_END_GAME, False)

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
    def chage_position(self,position : Position):
        self.position = position

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

scene = Scene('cena', __images + "room.png")

door = Object('porta',Position(600,300),Size(100,200))

door.add_state('fechada',__images+'door.png')
door.add_state('aberta',__images+'open_door.png')

key = Object('chave',Position(200,400),Size(50, 50))

key.add_state('normal',__images+'key.png')
key.add_state('ativa',__images+'active_key.png')

key.add_event(EventPutInInventario('chave_inventario',Click()))
key.add_event(EventChangeStates('ativar',ClickAfterEvent('cena','chave','chave_inventario'),'chave','normal','ativa'))
key.add_event(EventChangeStates('desativar',ClickAfterEvent('cena','chave','chave_inventario'),'chave','ativa','normal'))

door.add_event(EventChangeStates('abrir_porta',ClickWhenStateOfObject('chave','ativa'),'porta','fechada','aberta',False))
door.add_event(EventChangeStates('apagar_chave',ClickWhenStateOfObject('chave','ativa'),'chave','ativa',None,False))
door.add_event(EventEndGame('fim',ClickWhenStateOfObject('porta','aberta')))

scene.add_object(door)
scene.add_object(key)

room.add_scene(scene)

# Posição do inventário
inventory_x, inventory_y = 10, 10

#Dicionarios auxiliares
buffer_happen_events = {}
buffer_changed_objects_states = {}


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

def try_do_event(object, event):
    if not event.happen or event.repeatable:
        if check_trigger(event.trigger):
            #Verificar o tipo de evento é mudança de estados
            if event.type == EventType.EVENT_CHANGE_STATES:
                #VERIFICAR SE ESTADO INICIAL BATE CERTO COM O ATUAL
                if event.initial_state == room.get_current_state_of_object(room.current_scene, event.object_id):
                    buffer_changed_objects_states[event.object_id] = event.final_state #colocar no buffer o estado do objeto para ser posteriormente alterado
                    buffer_happen_events[event.id] = object.id #colocar o evento no buffer para ser atualizado (que aconteceu)

            elif event.type == EventType.EVENT_SHOW_MESSAGE:
                pass
                #TODO:

            #Verficar se o evento é do tipo colocar no inventario
            elif event.type == EventType.EVENT_PUT_IN_INVENTARIO:
                #TODO:COLOCAR POSICAO NO INVENTARIO
                object.chage_position(Position(inventory_x,inventory_y)) #Mudar a posicao do objeto para a do slot no inventario
                buffer_happen_events[event.id] = object.id #colocar o evento no buffer para ser atualizado (que aconteceu)

            elif event.type == EventType.EVENT_ASK_CODE:
                pass
                #TODO:

            #Verificar se o tipo de evento é "fim de jogo"
            elif event.type == EventType.EVENT_END_GAME:
                room.finish_game = True

running = True
# Loop principal do jogo
while running:
    for pygame_event in pygame.event.get():
        #Carregar em fechar jogo = encerra o jogo
        if pygame_event.type == pygame.QUIT:
            running = False
        
        #Evento de clique
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            
            for object in room.scenes[room.current_scene].objects.values():
                if object.have_clicked(pygame_event.pos[0],pygame_event.pos[1]):
                    for event in object.events.values():
                        try_do_event(object,event)

            #Atualizar os eventos que occorreram com o clique
            for event_id,object_id in buffer_happen_events.items():
                room.happened_event(room.current_scene,object_id,event_id)
            #Atualizar os estados que mudaram com o clique
            for object_id,state_id in buffer_changed_objects_states.items():
                room.change_object_state(room.current_scene,object_id,state_id)
            # RESET BUFFERS
            buffer_happen_events = {}
            buffer_changed_objects_states = {}
    
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
