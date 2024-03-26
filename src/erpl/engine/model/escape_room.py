from .object import Object
from .event import Event
from .utils import Position, Size
from .scene import Scene
from .sound import Sound

"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title : str, size : Size):
        self.title = title #TITULO
        self.scenes = {} 
        self.objects = {}
        self.events = {
        }
        self.events_buffer = {}
        self.sounds = {}
        self.size = size

    #Função que adiciona uma cena
    def add_scene(self,scene : Scene):
        self.scenes[scene.id] = scene

    #Função que adiciona um objeto
    def add_object(self, object : Object):
        self.objects[object.id] = object

    #Função que adiciona um evento de cena
    def add_event(self, event : Event):
        self.events[event.id] = event

    #Função que adiciona sons
    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound
    
    #Função que adiciona um evento de cena
    def add_event_buffer(self, id,pre_conditions,pos_conditions,repeatable,linked):
        self.events_buffer[id] = Event(id,pre_conditions,pos_conditions,repeatable,linked)
    
    #Função que desenha a cena atual
    def draw(self, screen, current_scene):
        #Desenhar a cena
        self.scenes[current_scene].draw(screen)

        #Desenhar objetos na cena
        for object in self.objects.values():
            #Se o objeto pertence à cena atual
            if current_scene == object.reference:
                object.draw(screen)

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

    def update_event(self,event):
        if event in self.events:
            self.events[event].happen = True
            self.events[event].repeatable -= 1

    def update_events_buffer(self):
        for event in self.events_buffer.values():
            self.events[event.id] = event
        self.events_buffer = {}
#
    #Função que verifica se um evento happen
    def check_if_event_occurred(self,event_id : str):
        if event_id in self.events:
            return self.events[event_id].happen
            
    #Função que devolve o state atual de um object
    def check_state_of_object(self, object_id : str, state_id : str):
        return self.objects[object_id].current_state == state_id if object_id in self.objects else False
    
    #def check_time (self, time):
    #    return time >= self.state.time
