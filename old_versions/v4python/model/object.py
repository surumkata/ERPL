
from model.utils import Position, Size
from model.state import State

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

    def draw(self, screen):
        if self.current_state != None:
            screen.blit(self.states[self.current_state].image, (self.position.x, self.position.y))