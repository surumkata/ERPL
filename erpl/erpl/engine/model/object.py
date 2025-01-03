
from .utils import Position, Size
from .view import View
from .sound import Sound

"""CLASSE DE UM OBJETO"""
class Object:
    def __init__(self, id : str = None, scenario_id : str = None):
        self.id = id
        self.current_view = None
        self.reference = scenario_id
        self.views = {}
        self.sounds = {}

    def change_current_view(self, view_id : str):
        if (view_id in self.views):
            self.current_view = view_id
            #self.position = self.views[view_id].position
            #self.size = self.views[view_id].size
            if(self.views[view_id].__class__.__name__ == 'View'):
                self.views[view_id].repeate = self.views[view_id].repeateInit
                self.views[view_id].current_sprite = 0
        else:
            self.current_view = None

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int):
        if(self.current_view != None and self.current_view in self.views):
            return self.views[self.current_view].collide(x,y)
        else:
            return False

    #Função que muda a position do object
    def change_position(self,position : Position):
        for view in self.views.values():
            view.change_position(position)

    #Função que muda o size do object
    def change_size(self,size : Size):
        for view in self.views.values():
            view.change_size(size)


    def add_view(self, view : View, initial : bool = False):
        self.views[view.id] = view
        if initial:
            self.change_current_view(view.id)

    def add_sound(self, sound : Sound):
        self.sounds[sound.id] = sound

    def draw(self, screen):
        if self.current_view != None:
            self.views[self.current_view].draw(screen)