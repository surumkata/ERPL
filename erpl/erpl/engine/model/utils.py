import pygame
import os
import re

debug_mode = True
WIDTH, HEIGHT = 1280,720
HEIGHT_INV = HEIGHT * 0.15


class Color():
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLACK = (0,0,0)
    BLUE = (0,0,255)
    GRAY = (89,89,89)

current_folder = os.path.dirname(__file__)
__sounds = f"{current_folder}/../../../../assets/sounds/"

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
        text_surface = font.render(self.text, True, Color.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        pygame.draw.rect(screen, Color.RED, (text_rect.left - 10, text_rect.top - 5, text_rect.width + 20, text_rect.height + 10))
        screen.blit(text_surface, text_rect)

class Text:
    def __init__(self,text,x,y,size,color,text_format = False):
        self.size = int(size)
        self.font = pygame.font.Font(None, self.size) #font
        self.color = pygame.Color(color)
        self.text = text
        self.x = x
        self.y = y
        self.text_format = text_format

    def draw(self,screen,variables):
        text = self.text

        if self.text_format:
            vars = re.findall(r'{(.*?)}', text)
            # Substituir as variáveis pelos valores em room.variables
            for var in vars:
                if var in variables:
                    # Substitui as ocorrências da variável pelo valor correto de room.variables[var]
                    value = variables[var]
                    if isinstance(value, float) and value.is_integer():
                        value = str(int(value))
                    else: value = str(value)
                    text = text.replace(f"{{{var}}}", value)


        self.text_render = self.font.render(text, True, self.color)
        screen.blit(self.text_render, (self.x,self.y)) #print question


def debug(message : str):
    print(message)