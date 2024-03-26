import pygame
from .utils import Position, Size

"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id : str, src_images : [str], size : Size, position : Position, time_sprite : int, repeate : int):
        self.id = id
        self.position = position
        self.size = size
        self.src_images = src_images
        # Carregando a imagem da porta
        self.images = []
        for src_image in self.src_images:
            image = pygame.image.load(src_image).convert_alpha()
            image = pygame.transform.scale(image, (self.size.x,self.size.y))  # Ajuste o tamanho conforme necessário
            self.images.append(image)
        
        self.time_sprite = time_sprite

        self.current_sprite = 0
        self.current_time_sprite = 0
        self.repeateInit = repeate
        self.repeate = self.repeateInit

    def change_size(self, size):
        self.size = size
        for i,image in enumerate(self.images):
            self.images[i] = pygame.image.load(self.src_images[i]).convert_alpha()
            self.images[i] = pygame.transform.scale(self.images[i], (self.size.x,self.size.y))

    def change_position(self, position):
        self.position = position

    def change_sprite(self):
        self.current_time_sprite += 1
        if self.current_time_sprite == self.time_sprite:
            self.current_time_sprite = 0
            self.current_sprite += 1
            if self.current_sprite == len(self.images):
                self.repeate -= 1
                self.current_sprite = self.current_sprite-1 if self.repeate == 0 else 0


    def draw(self,screen):
        screen.blit(self.images[self.current_sprite], (self.position.x, self.position.y))
        if self.repeate > 0: self.change_sprite()
    

class StatePeace(State):
    def __init__(self,id,buffer, size : Size, position : Position):
        self.id = id
        self.position = position
        self.size = size
        image = pygame.image.load_extended(buffer).convert_alpha()
        image = pygame.transform.scale(image, (self.size.x,self.size.y))  # Ajuste o tamanho conforme necessário
        self.images = [image]

        self.time_sprite = 0
        self.current_sprite = 0
        self.current_time_sprite = 0
        self.repeateInit = 0
        self.repeate = self.repeateInit

    def change_size(self, size):
        return super().change_size(size)
    
    def change_position(self, position):
        return super().change_position(position)
    
    def draw(self, screen):
        screen.blit(self.images[self.current_sprite], (self.position.x, self.position.y))