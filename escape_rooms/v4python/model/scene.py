from model.state import State

"""CLASSE DE CENA"""
class Scene:
    def __init__(self, id : str):
        self.id = id
        self.current_state = None
        self.states = {}

    def change_current_state(self, state_id : str):
        self.current_state = state_id
    
    def add_state(self, state : State, initial : bool = False):
        self.states[state.id] = state
        if initial:
            self.current_state = state.id

    def draw (self, screen):
        screen.blit(self.states[self.current_state].image, (0,0))