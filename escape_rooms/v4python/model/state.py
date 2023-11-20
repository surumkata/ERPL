import pygame
from model.utils import Position, Size


"""CLASSE DE UM ESTADO"""
class State:
    def __init__(self, id : str, src_image : str, size : Size, position : Position):
        self.id = id
        # Carregando a imagem da porta
        self.src_image = src_image
        self.image = pygame.image.load(self.src_image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size.x,size.y))  # Ajuste o tamanho conforme necessário
        self.position = position
        self.size = size

    def change_size(self, size):
        self.image = pygame.image.load(self.src_image) 
        self.image = pygame.transform.scale(self.image, (size.x,size.y))

    def change_position(self, position):
        self.position = position