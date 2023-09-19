import pygame
import sys


WIDTH, HEIGHT = 1300, 700


"""TIPOS DE GATILHO (TRIGGER) DE EVENTO"""
CLICK = 1
CLICK_AFTER_EVENT = 2
CLICK_WHEN_OBJECT_STATE = 3


"""TIPOS DE EVENTOS"""
EVENT_CHANGE_STATES = 0
EVENT_PUT_IN_INVENTARIO = 1
EVENT_SHOW_MESSAGE = 2
EVENT_ASK_CODE = 3
EVENT_END_GAME = 4

"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title):
        self.title = title #TITULO
        self.scenes = {} #CENAS (DICIONARIO [CHAVE = ID DA CENA])
        self.current_scene = None #ID DA CENA ATUAL

    #Função que adiciona uma cena
    def add_scene(self,scene):
        self.scenes[scene.id] = scene
        if self.current_scene == None: #Se for a primeira cena a ser adicionar fica a atual
            self.current_scene = scene.id
    
    #Função que muda a cena atual
    def change_current_scene(self,scene_id):
        if scene_id in self.scenes:
            self.current_scene = scene_id
    
    #Função que desenha a cena atual
    def draw(self):
        self.scenes[self.current_scene].draw()

    #Função que muda o state atual de um object
    def change_object_state(self,scene_id,object_id,state_id):
        self.scenes[scene_id].change_object_state(object_id,state_id)
    
    #Função que coloca um evento como ocurrido
    def happened_event(self,scene_id,object_id,evento_id):
        self.scenes[scene_id].happened_event(object_id,evento_id)

    #Função que verifica se um evento happen
    def check_if_event_occurred(self,scene_id,object_id,evento_id):
        return self.scenes[scene_id].check_if_event_occurred(object_id,evento_id)
    
    #Função que devolve o state atual de um object
    def get_current_state_of_object(self,scene_id,object_id):
        return self.scenes[scene_id].get_current_state_of_object(object_id)

"""CLASSE DE CENA"""
class Scene:
    def __init__(self, id, src_image):
        self.id = id
        self.objects = {}
        self.background = pygame.image.load(src_image)
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
    
    def add_object(self,object):
        self.objects[object.id] = object

    def draw(self):
        # Desenhar a imagem de fundo
        screen.blit(self.background, (0, 0))

        # Desenhar todos os objects da cena
        for object in self.objects.values():
            object.draw()

    def change_object_state(self,object_id,state_id):
        self.objects[object_id].change_state(state_id)

    def happened_event(self,object_id,evento_id):
        self.objects[object_id].happened_event(evento_id)

    def check_if_event_occurred(self,object_id,evento_id):
        return self.objects[object_id].check_if_event_occurred(evento_id)

    def get_current_state_of_object(self,object_id):
        return self.objects[object_id].get_current_state()
    
"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id, position, size):
        self.id = id
        self.states = {}
        self.events = {}
        self.position = position
        self.size = size
        self.current_state = None

    def add_state(self,state_id,srcImage):
        state = State(state_id,srcImage,self.size)
        self.states[state_id] = state
        if self.current_state == None:
            self.current_state = state_id
    
    def add_event(self,evento):
        self.events[evento.id] = evento

    def have_clicked(self, x, y):
        return self.position.x <= x <= self.position.x + self.size.x and self.position.y <= y <= self.position.y + self.size.y
    
    def changePosition(self,position):
        self.position = position

    def draw(self):
        if(self.current_state != None):
            screen.blit(self.states[self.current_state].image, (self.position.x, self.position.y))
    
    def change_state(self,state_id):
        if state_id in self.states:
            self.current_state = state_id
    
    def happened_event(self, evento_id):
        self.events[evento_id].happen = True

    def get_current_state(self):
        return self.current_state
    
    def check_if_event_occurred(self,evento_id):
        return self.events[evento_id].happen
    
"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id, srcImage, size):
        self.id = id
        # Carregando a imagem da porta
        self.image = pygame.image.load(srcImage)  # Substitua "door.png" pelo nome da sua imagem da porta
        self.image = pygame.transform.scale(self.image, (size.x,size.y))  # Ajuste o tamanho conforme necessário


"""CLASSE DE EVENTO"""
class Event:

    def __init__(self, id, trigger,type,repeatable):
        self.id = id
        self.trigger = trigger
        self.type = type
        self.repeatable = repeatable
        self.happen = False

class EventChangeStates(Event):
    def __init__(self, id, trigger, object, initial_state, final_state, repeatable = True):
        super().__init__(id, trigger, EVENT_CHANGE_STATES, repeatable)
        self.object = object
        self.initial_state = initial_state
        self.final_state = final_state
        
class EventPutInInventario(Event):
    def __init__(self,id,trigger):
        super().__init__(id, trigger,EVENT_PUT_IN_INVENTARIO, False) 
    
class EventShowMessage(Event):
    def __init__(self,id,trigger,message):
        super().__init__(id, trigger, EVENT_SHOW_MESSAGE, True) 
        self.message = message

class EventAskCode(Event):
    def __init__(self,id,trigger,message, codigo):
        super().__init__(id, trigger, EVENT_ASK_CODE, True) 
        self.message = message
        self.codigo = codigo

class EventEndGame(Event):
    def __init__(self,id,trigger):
        super().__init__(id, trigger, EVENT_END_GAME, False)


"""CLASSE AUXIALIRES"""
class Position():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Size():
    def __init__(self, x, y):
        self.x = x
        self.y = y

"""CLASSE DE GATILHO (TRIGGER)"""
class Trigger():
    def __init__(self, type):
        self.type = type

class Click(Trigger):
    def __init__(self):
        super().__init__(CLICK)

class ClickAfterEvent(Trigger):
    def __init__(self,scene,object,evento):
        super().__init__(CLICK_AFTER_EVENT)
        self.scene = scene
        self.object = object
        self.evento = evento

class ClickWhenStateOfObject(Trigger):
    def __init__(self,object, state):
        super().__init__(CLICK_WHEN_OBJECT_STATE)
        self.state = state
        self.object = object


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

scene = Scene('scene', __images + "room.png")

door = Object('porta',Position(600,300),Size(100,200))

door.add_state('fechada',__images+'door.png')
door.add_state('aberta',__images+'open_door.png')

key = Object('chave',Position(200,400),Size(50, 50))

key.add_state('normal',__images+'key.png')
key.add_state('ativa',__images+'active_key.png')

key.add_event(EventPutInInventario('chave_inventario',Click()))
key.add_event(EventChangeStates('ativar',ClickAfterEvent('scene','chave','chave_inventario'),'chave','normal','ativa'))
key.add_event(EventChangeStates('desativar',ClickAfterEvent('scene','chave','chave_inventario'),'chave','ativa','normal'))

door.add_event(EventChangeStates('abrir_porta',ClickWhenStateOfObject('chave','ativa'),'porta','fechada','aberta',False))
door.add_event(EventChangeStates('apagar_chave',ClickWhenStateOfObject('chave','ativa'),'chave','ativa',None,False))
door.add_event(EventEndGame('fim',ClickWhenStateOfObject('porta','aberta')))

scene.add_object(door)
scene.add_object(key)

room.add_scene(scene)

# Posição do inventário
inventory_x, inventory_y = 10, 10

# Variáveis para controlar a exibição da message
finish_game = False

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        #Carregar em fechar jogo = encerra o jogo
        if event.type == pygame.QUIT:
            running = False
        
        #Evento de clique
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #Dicionarios auxiliares
            buffer_happen_events = {}
            buffer_changed_objects_states = {}
            
            #Clique foi na porta
            if door.have_clicked(event.pos[0],event.pos[1]):
                #Iterar todos os eventos ligados à porta
                for evento_id,evento in door.events.items():
                    #Se o evento ainda não aconteceu ou é repetível
                    if (not evento.happen or evento.repeatable):
                        #Se o tipo de gatilho de evento é Clique quando estado de objeto
                        if evento.trigger.type == CLICK_WHEN_OBJECT_STATE:
                            #Verificar se o estado de objeto do gatilho é igual ao atual
                            if room.get_current_state_of_object(room.current_scene,evento.trigger.object) == evento.trigger.state:
                                #Verificar o tipo de evento é mudança de estados
                                if evento.type == EVENT_CHANGE_STATES:
                                    #VERIFICAR SE ESTADO INICIAL BATE CERTO COM O ATUAL
                                    if evento.initial_state == room.get_current_state_of_object(room.current_scene, evento.object):
                                        buffer_changed_objects_states[evento.object] = evento.final_state #colocar no buffer o estado do objeto para ser posteriormente alterado
                                        buffer_happen_events[evento.id] = door.id #colocar o evento no buffer para ser atualizado (que aconteceu)
                                #Verificar se o tipo de evento é "fim de jogo"
                                elif evento.type == EVENT_END_GAME:
                                    finish_game = True
            
            #Clique foi na chave
            elif key.have_clicked(event.pos[0],event.pos[1]):
                #Iterar todos os eventos ligados à chave
                for evento_id,evento in key.events.items():
                    #Se o evento ainda não aconteceu ou é repetível
                    if (not evento.happen or evento.repeatable):
                        #Se o tipo de gatilho de evento é apenas clique
                        if evento.trigger.type == CLICK:
                            #LÓGICA DE TODOS OS TIPOS DE EVENTOS
                            #Verficar se o evento é do tipo colocar no inventario
                            if evento.type == EVENT_PUT_IN_INVENTARIO:
                                #TODO:COLOCAR POSICAO NO INVENTARIO
                                key.changePosition(Position(inventory_x,inventory_y)) #Mudar a posicao do objeto para a do slot no inventario
                                buffer_happen_events[evento.id] = key.id #colocar o evento no buffer para ser atualizado (que aconteceu)
                        #Se o tipo de gatilho de evento é clique depois de evento
                        elif evento.trigger.type == CLICK_AFTER_EVENT:
                            #Verificar se o evento do gatilho já ocorreu
                            if room.check_if_event_occurred(evento.trigger.scene,evento.trigger.object,evento.trigger.evento):                        
                                #LOGICA DE TODOS OS TIPOS DE EVENTOS
                                if evento.type == EVENT_CHANGE_STATES:
                                    #VERIFICAR SE ESTADO INICIAL BATE CERTO COM O ATUAL
                                    if evento.initial_state == room.get_current_state_of_object(room.current_scene, evento.object):
                                        buffer_changed_objects_states[evento.object] = evento.final_state
                                        buffer_happen_events[evento.id] = key.id


            #Atualizar os eventos que occorreram com o clique
            for evento_id,object_id in buffer_happen_events.items():
                room.happened_event(room.current_scene,object_id,evento_id)
            #Atualizar os estados que mudaram com o clique
            for object_id,state_id in buffer_changed_objects_states.items():
                room.change_object_state(room.current_scene,object_id,state_id)
    
    room.draw()

    if finish_game:
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido/
        font = pygame.font.Font(None, 36)
        text = font.render("Você Escapou!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    
    
    
    pygame.display.flip()

# Encerramento do jogo
pygame.quit()
sys.exit()
