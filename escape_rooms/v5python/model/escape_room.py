from model.er_state import EscapeRoomState
from model.object import Object
from model.event import Event
from model.utils import Position, Size
from model.scene import Scene
from model.sound import Sound

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
        self.sounds = {}

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

    #Função que adiciona sons
    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound
    
    #Função que adiciona um evento de cena
    def add_event_buffer(self, id,pre_conditions,pos_conditions,repeatable,linked):
        self.events_buffer[id] = Event(id,pre_conditions,pos_conditions,repeatable,linked)

    #Função que muda a cena atual
    def change_current_scene(self,scene_id : str):
        if scene_id in self.scenes:
            self.er_state.update_current_scene(scene_id)
    
    #Função que desenha a cena atual
    def draw(self, screen):
        #Desenhar a cena
        current_scene = self.er_state.current_scene
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

    def update_events(self):
        for event in self.er_state.events_happend:
            if event in self.events:
                self.events[event].happen = True
                self.events[event].repeatable -= 1
        
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
