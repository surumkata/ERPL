from .object import Object
from .event import Event
from .utils import Position, Size
from .scenario import Scenario
from .sound import Sound
from .transition import Transition

"""CLASSE DE UMA ESCAPE ROOM"""
class EscapeRoom:
    #Construtor de escape room
    def __init__(self, title : str):
        self.title = title #TITULO
        self.scenarios = {} 
        self.objects = {}
        self.events = {}
        self.events_buffer = {}
        self.transitions = {}
        self.variables = {
            "_timer_" : 0.0,
            "_timerms_" : 0.0,
            "_sucesses_" : 0.0,
            "_fails_" : 0.0
        }

    #Função que add uma cena
    def add_scenario(self,scenario : Scenario):
        self.scenarios[scenario.id] = scenario

    #Função que add um object
    def add_object(self, object : Object):
        self.objects[object.id] = object

    #Função que add um event
    def add_event(self, event : Event):
        self.events[event.id] = event
    
    #Função que add uma transition
    def add_transition(self, transition : Transition):
        self.transitions[transition.id] = transition
    
    #Função que add uma transition
    def add_variable(self, variable : str, number : float):
        self.variables[variable] = number

    #Função que add um event ao buffer
    def add_event_buffer(self, id,pre_conditions,pos_conditions,repetitions):
        self.events_buffer[id] = Event(id,pre_conditions,pos_conditions,repetitions)

    def change_object_current_view(self, object_id : str, view_id):
        if object_id in self.objects:
            self.objects[object_id].change_current_view(view_id)

    def change_object_position(self, object_id : str, position : Position):
        if object_id in self.objects:
            self.objects[object_id].change_position(position)

    def change_object_size(self, object_id : str, size : Size):
        if object_id in self.objects:
            self.objects[object_id].change_size(size)

    def update_event(self,event):
        if event in self.events:
            self.events[event].happen = True
            if not self.events[event].inifity_repetitions:
                self.events[event].repetitions -= 1

    def update_events_buffer(self):
        for event in self.events_buffer.values():
            self.events[event.id] = event
        self.events_buffer = {}
#
    #Função que verifica se um event happen
    def check_if_event_occurred(self,event_id : str):
        if event_id in self.events:
            return self.events[event_id].happen
        else: return False
            
    #Função que devolve o view atual de um object
    def check_view_of_object(self, object_id : str, view_id : str):
        return self.objects[object_id].current_view == view_id if object_id in self.objects else False

    #Função que desenha a cena atual
    def draw(self, screen, current_scenario):
        #Desenhar a cena
        if current_scenario in self.scenarios:
            self.scenarios[current_scenario].draw(screen,self.variables)
        else: return
        
        #Desenhar objects na cena
        for object in self.objects.values():
            #Se o object pertence à cena atual
            if current_scenario == object.reference:
                object.draw(screen)