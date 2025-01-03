from .utils import Position, Size
from .view import View
from .sound import Sound

"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id : str,initial_view : str, views : [View] = [], sounds : [Sound] = [], position : Position = None, size : Size = None):
        self.id = id
        self.initial_view = initial_view
        self.views = {}
        for view in views:
            self.views[view.id] = view
        self.sounds = {}
        for sound in sounds:
            self.sounds[sound.id] = sound
        self.position = position
        self.size = size

    def set_size(self,size : Size):
        self.size = size

    def set_position(self,position : Position):
        self.position = position

    def get_size(self):
        return self.size

    def get_position(self):
        return self.position


    def add_view(self, view : View, initial : bool = False):
        self.views[view.id] = view
        if initial:
            self.initial_view = view.id

    def get_view(self, view_id : str):
        return self.views[view_id] if view_id in self.views else None
    
    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound
    
    def get_sound(self, sound_id : str):
        return self.sounds[sound_id] if sound_id in self.sounds else None

    def serialize(self):
        sounds = [self.sounds[sound_id].serialize() for sound_id in self.sounds]
        views = [self.views[view_id].serialize() for view_id in self.views]
        return {
            'id' : self.id,
            'initial_view' : self.initial_view,
            'views' : views,
            'sounds' : sounds
        }