from .view import View
from .sound import Sound
from .hitbox import Hitbox

"""CLASSE DE CENA"""
class Scenario:
    def __init__(self, id : str):
        self.id = id
        self.current_view = None
        self.views = {}
        self.sounds = {}
        self.texts = []
        self.hitboxes = {}

    def change_current_view(self, view_id : str):
        self.current_view = view_id
        self.views[view_id].repeate = self.views[view_id].repeateInit
        self.views[view_id].current_sprite = 0
    
    def add_view(self, view : View, initial : bool = False):
        self.views[view.id] = view
        if initial:
            self.current_view = view.id

    def draw (self, screen, variables):
        if self.current_view != None:
            self.views[self.current_view].draw(screen)
            
            for text in self.texts:
                text.draw(screen,variables)

    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound

    def add_hitboxes(self,hitboxes : [Hitbox]):
        for hitbox in hitboxes:
            self.hitboxes[hitbox.id] = hitbox
    
    def add_texts(self,texts):
        for text in texts:
            self.texts.append(text)
    
    def collide(self,px,py,hitbox_id):
        if hitbox_id not in self.hitboxes: return False
        else: return self.hitboxes[hitbox_id].collide(px,py)