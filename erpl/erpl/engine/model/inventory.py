import pygame

from .utils import Position, Size, Color, WIDTH, HEIGHT, HEIGHT_INV
from .view import View, ViewSketch
import math

SQUARE_SIZE = 80

class Item:
    def __init__(self, id : str, view : View, slot : int, slotPosition : Position):
        self.id = id
        self.size = Size(0,0)
        self.position = Position(0,0)
        self.slot = slot

        self.slotPosition = slotPosition

        padding = 10
        objSize = SQUARE_SIZE - padding*2

        if isinstance(view, ViewSketch):
            width = view.bb.xmax - view.bb.xmin
            height = view.bb.ymax - view.bb.ymin
        elif isinstance(view,View):
            width = view.size.x
            height = view.size.y

        if width >= height:
            self.size.x = objSize
            self.size.y = height * objSize/width
        else:
            self.size.y = objSize
            self.size.x = width * objSize/height
        if self.size.x == objSize:
            self.position.x = self.slotPosition.x + padding
            self.position.y = self.slotPosition.y + SQUARE_SIZE/2 - self.size.y/2
        else:
            self.position.x = self.slotPosition.x + SQUARE_SIZE/2 - self.size.x/2
            self.position.y = self.slotPosition.y + padding

        scalex = self.size.x / width
        scaley = self.size.y / height
        print(scalex,scaley)

        view.change_size(Size(scalex,scaley))
        view.change_position(self.position)


        self.view = view
        self.in_use = False
        self.hover = False
    
    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int):
        return self.slotPosition.x <= x and x <= self.slotPosition.x + SQUARE_SIZE and self.slotPosition.y <= y and y <= self.slotPosition.y + SQUARE_SIZE
    
    def draw(self, screen):
        screen.blit(self.view.images[0], (self.position.x,self.position.y))
        if self.in_use:
            pygame.draw.rect(screen, Color.RED, (self.position.x, self.position.y, 10, 10))
            

# Classe Inventário
class Inventory:
    def __init__(self):
        self.items = 0
        self.slots = {}
        self.update_in_use = []
        self.update_add = []
        self.update_remove = []
        self.last_active = None

        self.inWidth = WIDTH
        self.invHeight = HEIGHT_INV
        self.squareSize = SQUARE_SIZE
        self.padding = (self.invHeight - 80) / 2
    
        self.numberSquares = WIDTH / (self.squareSize+self.padding)
        self.numberSquares = math.floor(self.numberSquares)
    
        self.startPadding = (WIDTH - (self.numberSquares * (self.squareSize+self.padding))) / 2
  

    def find_empty_slot(self):
        for slot,item in self.slots.items():
            if item == None:
                return slot
        return self.items

    def add(self, object, slot):
        x = self.startPadding + ((slot) * (self.squareSize + self.padding))
        y = self.padding
        self.slots[slot] = Item(object.id,object.views[object.current_view], slot, Position(x,y))
        self.items += 1
    
    def remove(self,item_id):
        for slot,item in self.slots.items():
            if item != None and item.id == item_id:
                self.slots[slot] = None
                self.items -= 1

    def active_item(self, item_id):
        for slot,item in self.slots.items():
            if item != None and item.id == item_id:
                if self.last_active != None:
                    self.update_in_use.append((self.last_active,False))
                self.update_in_use.append((slot,True)) #Coloca no buffer
                self.last_active = slot
                break
    
    def desactive_item(self, item_id):
        for slot,item in self.slots.items():
            if item != None and item.id == item_id:
                self.update_in_use.append((slot,False)) #Coloca no buffer
                break

    def update_items(self):
        for slot,in_use in self.update_in_use:
            if self.slots[slot] != None:
                self.slots[slot].in_use = in_use
        for (item,slot) in self.update_add:
            self.add(item,slot)
        for item in self.update_remove:
            self.remove(item)

        self.update_in_use = []
        self.update_add = []
        self.update_remove = []

    def check_item_in_use(self,item_id):
        for item in self.slots.values():
            if item != None and item.id == item_id:
                return item.in_use
        return False
    
    def get_item(self,item_id):
        for item in self.slots.values():
            if item != None and item.id == item_id:
                return item
        return None
    
    def exist_item(self,item_id):
        for item in self.slots.values():
            if item != None and item.id == item_id:
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, Color.WHITE, (0, 0, self.inWidth, self.invHeight))
        pygame.draw.rect(screen, Color.BLACK, (0, 0, self.inWidth, self.invHeight),2)

        i = 1
        #Desenhar slots
        while True:
            x = self.startPadding + ((i - 1) * (self.squareSize + self.padding))
            if x < self.inWidth - self.squareSize:
                pygame.draw.rect(screen, Color.BLACK, (x, self.padding, self.squareSize, self.squareSize),2)
                i+=1
            else:
                break
        
        # Desenha os items nos slots   
        for item in self.slots.values():
            if item != None:
                item.draw(screen)