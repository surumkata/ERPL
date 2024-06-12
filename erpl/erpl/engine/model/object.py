
from .utils import Position, Size
from .view import View
from .sound import Sound

"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id : str, scenario_id : str, position : Position, size : Size):
        self.id = id
        self.current_view = None
        self.reference = scenario_id
        self.position = position
        self.size = size
        self.views = {}
        self.sounds = {}

    def change_current_view(self, view_id : str):
        if (view_id in self.views):
            self.current_view = view_id
            self.position = self.views[view_id].position
            self.size = self.views[view_id].size
            self.views[view_id].repeate = self.views[view_id].repeateInit
            self.views[view_id].current_sprite = 0
        else:
            self.current_view = None

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int):
        #TODO: melhor hit_box
        return self.position.x + self.size.x * 0.1 <= x <= self.position.x + self.size.x * 0.9 and self.position.y + self.size.y * 0.1 <= y <= self.position.y  + self.size.y * 0.9

    #Função que muda a position do object
    def change_position(self,position : Position):
        self.position = position
        for view in self.views.values():
            view.change_position(position)

    #Função que muda o size do object
    def change_size(self,size : Size):
        self.size = size
        for view in self.views.values():
            view.change_size(size)

    def position_is_none(self):
        return self.position.x == None or self.position.y == None
    
    def size_is_none(self):
        return self.size.x == None or self.size.y == None

    def add_view(self, view : View, initial : bool = False):
        self.views[view.id] = view
        if self.position_is_none():
            self.position = Position(view.position.x,view.position.y)
        if self.size_is_none():
            self.size = Size(view.size.x,view.size.y)
        if initial:
            self.change_current_view(view.id)

    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound

    def draw(self, screen):
        if self.current_view != None:
            self.views[self.current_view].draw(screen)