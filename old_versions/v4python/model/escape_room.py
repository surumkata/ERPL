from model.er_state import EscapeRoomState
from model.object import Object
from model.event import Event
from model.utils import Position, Size
from model.scenario import Scenario

"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title : str):
        self.title = title #TITULO
        self.scenarios = {} 
        self.objects = {}
        self.events = {
        }
        self.events_buffer = {}
        self.er_state = EscapeRoomState() #ID DA CENA ATUAL

    #Função que adiciona uma cena
    def add_scenario(self,scenario : Scenario):
        self.scenarios[scenario.id] = scenario
        self.er_state.first_scenario(scenario.id)

    #Função que adiciona um objeto
    def add_object(self, object : Object):
        self.objects[object.id] = object

    #Função que adiciona um evento de cena
    def add_event(self, event : Event):
        self.events[event.id] = event
    
    #Função que adiciona um evento de cena
    def add_event_buffer(self, id,pre_conditions,pos_conditions,repeatable,linked):
        self.events_buffer[id] = Event(id,pre_conditions,pos_conditions,repeatable,linked)

    #Função que muda a cena atual
    def change_current_scenario(self,scenario_id : str):
        if scenario_id in self.scenarios:
            self.er_state.update_current_scenario(scenario_id)
    
    #Função que desenha a cena atual
    def draw(self, screen):
        #Desenhar a cena
        current_scenario = self.er_state.current_scenario
        self.scenarios[current_scenario].draw(screen)

        #Desenhar objetos na cena
        for object in self.objects.values():
            #Se o objeto pertence à cena atual
            if current_scenario == object.reference:
                object.draw(screen)

    ##Função que muda o state atual de um object
    #def change_object_state(self, scenario_id : str, object_id : str ,state_id : str):
    #    self.scenarios[scenario_id].change_object_state(object_id,state_id)

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
