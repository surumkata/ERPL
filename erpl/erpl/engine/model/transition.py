import pygame
from .utils import Size, Color

class Transition():
    def __init__(self,id,background,music,story,next_scenario = None,next_transition = None):
        self.id = id
        print(background)
        self.background = pygame.image.load(background).convert_alpha()
        self.music = music
        self.story = story
        self.next_scenario = next_scenario
        self.next_transition = next_transition

    def define_size(self,size : Size):
        self.background = pygame.transform.scale(self.background, (size.x,size.y))  # Ajuste o size conforme necessário

    def play_music(self):
        if self.music != None:
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.music != None:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        
    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        if self.story != None:
            font = pygame.font.Font(None, 32) # Font

            lines = self.story.split("\\n")
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