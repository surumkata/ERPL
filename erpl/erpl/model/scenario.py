from .view import View
from .sound import Sound
#from .hitbox import Hitbox
from .object import Object
from .utils import ObjText,WIDTH,HEIGHT

"""CLASSE DE CENA"""
class Scenario:
    def __init__(self, id : str, initial_view : str, views : [View], objects : [Object], texts : [ObjText] = [], sounds : [Sound] = [], floor : float = HEIGHT, ceil : float = 0):
        self.id = id
        self.initial_view = initial_view
        self.views = {}
        for view in views:
            self.views[view.id] = view
        self.sounds = {}
        for sound in sounds:
            self.sounds[sound.id] = sound
        self.objects = {}
        for object in objects:
            self.objects[object.id] = object
        self.texts = texts
        self.floor = floor
        self.ceil = ceil
    
    def add_view(self, view : View, initial : bool = False):
        self.views[view.id] = view
        if initial:
            self.initial_view = view.id

    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound

    #def add_hitboxes(self,hitboxes : [Hitbox]):
    #    for hitbox in hitboxes:
    #        self.hitboxes[hitbox.id] = hitbox
    
    def add_text(self,text:ObjText):
        self.texts.append(text)

    def add_texts(self,texts:[ObjText]):
        for text in texts:
            self.texts.append(text)

    def serialize(self):
        sounds = [self.sounds[sound_id].serialize() for sound_id in self.sounds]
        views = [self.views[view_id].serialize() for view_id in self.views]
        objects = [self.objects[obj_id].serialize() for obj_id in self.objects]
        return {
            'id' : self.id,
            'initial_view' : self.initial_view,
            'views' : views,
            'objects' : objects,
            'sounds' : sounds,
            'floor' : self.floor,
            'ceil' : self.ceil
        }