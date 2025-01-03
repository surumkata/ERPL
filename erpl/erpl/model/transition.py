import pygame
from .utils import Size, Color, HEIGHT_INV
import re

class Transition():
    def __init__(self,id,background,music,story,next_scenario = None,next_transition = None,format_story= False):
        self.id = id
        self.background = pygame.image.load(background).convert_alpha()
        self.music = music
        self.story = story
        self.next_scenario = next_scenario
        self.next_transition = next_transition
        self.format_story = format_story

    def define_size(self,size : Size):
        self.background = pygame.transform.scale(self.background, (size.x,size.y+HEIGHT_INV))  # Ajuste o size conforme necessário

    def play_music(self):
        if self.music != None:
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.music != None:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        
    def draw(self, screen, variables):
        screen.blit(self.background, (0, 0))            

        if self.story != None:
            lines = self.story
            
            if self.format_story:
                format_lines = []
                for message in lines:
                    # Substituir as variáveis da f-string pelos valores em room.variables
                    # Extrair as variáveis presentes na f-string
                    vars = re.findall(r'{(.*?)}', message)
                    # Substituir as variáveis pelos valores em room.variables
                    for var in vars:
                        if var in variables:
                            # Substitui as ocorrências da variável pelo valor correto de room.variables[var]
                            value = variables[var]
                            if isinstance(value, float) and value.is_integer():
                                value = str(int(value))
                            else: value = str(value)
                            message = message.replace(f"{{{var}}}", value)
                    format_lines.append(message)
                lines = format_lines


            font = pygame.font.Font(None, 32) # Font
            max_line_width = max(font.size(line)[0] for line in lines)  # Determina a largura máxima da linha
            text_height = font.get_height() * len(lines)  # Determina a altura total do texto
            line_spacing = 5  # Espaço entre as linhas
            text_height += (len(lines) - 1) * line_spacing  # Adiciona espaço entre as linhas
            text_surface = pygame.Surface((max_line_width, text_height), pygame.SRCALPHA)  # Superfície para o texto

            # Desenha o texto na superfície
            y = 0
            for line in lines:
                q = font.render(line, True, Color.WHITE)
                text_surface.blit(q, (0, y))
                y += font.get_height() + line_spacing  # Ajusta a posição para o próximo linha

            # Obtenha o retângulo que envolve o texto e ajuste sua posição e tamanho
            text_rect = text_surface.get_rect(topleft=(100, 100))

            # Desenha um retângulo cinza ao redor do texto
            pygame.draw.rect(screen, Color.GRAY, text_rect.inflate(10, 10))

            # Blit a superfície do texto na tela
            screen.blit(text_surface, text_rect.topleft)