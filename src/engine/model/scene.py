from model.state import State

"""CLASSE DE CENA"""
class Scene:
    def __init__(self, id : str):
        self.id = id
        self.current_state = None
        self.states = {}

    def change_current_state(self, state_id : str):
        self.current_state = state_id
        self.states[state_id].repeate = self.states[state_id].repeateInit
        self.states[state_id].current_sprite = 0
    
    def add_state(self, state : State, initial : bool = False):
        self.states[state.id] = state
        if initial:
            self.current_state = state.id

    def draw (self, screen):
        if self.current_state != None:
            self.states[self.current_state].draw(screen)