import pygame
import os

debug_mode = True
WIDTH, HEIGHT = 1300, 700

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)
BLUE = (0,0,255)

current_folder = os.path.dirname(__file__)
__images = f"{current_folder}/../../assets/images/"
__sounds = f"{current_folder}/../../assets/sounds/"

"""CLASSE AUXIALIRES"""
class Position():
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y

class Size():
    def __init__(self, x : int, y : int):
        self.x = x
        self.y = y


# Classe para representar mensagens de balão de fala
class BalloonMessage:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def display(self, screen):
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        pygame.draw.rect(screen, RED, (text_rect.left - 10, text_rect.top - 5, text_rect.width + 20, text_rect.height + 10))
        screen.blit(text_surface, text_rect)

def debug(message : str):
    print(message)