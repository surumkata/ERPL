
from .utils import Position, Size
from .state import State

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
            self.states[state_id].repeate = self.states[state_id].repeateInit
            self.states[state_id].current_sprite = 0
        else:
            self.current_state = None

    #Função que verifica se foi clicado na área do objeto
    def have_clicked(self, x : int, y : int):
        #TODO: melhor hit_box
        return self.position.x + self.size.x * 0.1 <= x <= self.position.x + self.size.x * 0.9 and self.position.y + self.size.y * 0.1 <= y <= self.position.y  + self.size.y * 0.9

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

    def position_is_none(self):
        return self.position.x == None or self.position.y == None
    
    def size_is_none(self):
        return self.size.x == None or self.size.y == None

    def add_state(self, state : State, initial : bool = False):
        self.states[state.id] = state
        if self.position_is_none():
            self.position = Position(state.position.x,state.position.y)
        if self.size_is_none():
            self.size = Size(state.size.x,state.size.y)
        if initial:
            self.change_current_state(state.id)

    def draw(self, screen):
        if self.current_state != None:
            self.states[self.current_state].draw(screen)