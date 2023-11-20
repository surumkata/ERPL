import pygame
from model.utils import Position, Size


"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id : str, src_images : [str], size : Size, position : Position):
        self.id = id
        self.position = position
        self.size = size
        self.src_images = src_images
        # Carregando a imagem da porta
        self.images = []
        for src_image in self.src_images:
            image = pygame.image.load(src_image)
            image = pygame.transform.scale(image, (self.size.x,self.size.y))  # Ajuste o tamanho conforme necessário
            self.images.append(image)

        self.image = pygame.image.load(src_images[0])
        self.image = pygame.transform.scale(image, (self.size.x,self.size.y))

        self.current_sprite = 0

    def change_size(self, size):
        self.size = size
        for i,image in enumerate(self.images):
            image = pygame.image.load(self.src_images[i]) 
            image = pygame.transform.scale(image, (self.size.x,self.size.y))

    def change_position(self, position):
        self.position = position

    def change_sprite(self):
        # Atualize a animação
        self.current_sprite += 1
        if self.current_sprite >= len(self.images):
            self.current_sprite = 0
    
