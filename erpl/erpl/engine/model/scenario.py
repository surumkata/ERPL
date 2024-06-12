from .view import View
from .sound import Sound

"""CLASSE DE CENA"""
class Scenario:
    def __init__(self, id : str):
        self.id = id
        self.current_view = None
        self.views = {}
        self.sounds = {}
        

    def change_current_view(self, view_id : str):
        self.current_view = view_id
        self.views[view_id].repeate = self.views[view_id].repeateInit
        self.views[view_id].current_sprite = 0
    
    def add_view(self, view : View, initial : bool = False):
        self.views[view.id] = view
        if initial:
            self.current_view = view.id

    def draw (self, screen):
        if self.current_view != None:
            self.views[self.current_view].draw(screen)

    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound