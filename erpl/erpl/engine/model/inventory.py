import pygame

from .utils import Position, Size, Color
from .view import View


class Item:
    def __init__(self, id : str, size : Size, view : View, slot : int):
        self.id = id
        self.size = Size(0,0)
        self.position = Position(0,0)
        if size.x >= size.y:
            self.size.x = 60
            self.size.y = size.y * 60 / size.x
        else:
            self.size.y = 60
            self.size.x = size.x * 60 / size.y
        
        self.position.x = (80-self.size.x) + 10+(slot*90)
        self.position.y = (80-self.size.x) + 10

        view.change_size(self.size)
        self.view = view

        self.in_use = False
    
    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int):
        return self.position.x <= x <= self.position.x + self.size.x and self.position.y <= y <= self.position.y + self.size.y
    
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

    def find_empty_slot(self):
        for slot,item in self.slots.items():
            if item == None:
                return slot
        return self.items

    def add(self, object, slot):
        self.slots[slot] = Item(object.id,object.size,object.views[object.current_view], slot)
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
        pygame.draw.rect(screen, Color.GRAY, (0, 0, 1280, 100))
        i = 1
        while True:
            x = 10+((i-1)*90)
            if x < 1280 - 80:
                pygame.draw.rect(screen, Color.WHITE, (x, 10, 80, 80))
                i+=1
            else:
                break
        for item in self.slots.values():
            if item != None:
                item.draw(screen)