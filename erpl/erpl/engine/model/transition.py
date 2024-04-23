import pygame
from .utils import Size, Color

class Transition():
    def __init__(self,id,background,music,story,next_scenario = None,next_transition = None):
        self.id = id
        self.background = pygame.image.load(background).convert_alpha()
        self.music = music
        self.story = story
        self.next_scenario = next_scenario
        self.next_transition = next_transition

    def define_size(self,size : Size):
        self.background = pygame.transform.scale(self.background, (size.x,size.y))  # Ajuste o tamanho conforme necessário

    def play_music(self):
        if self.music != None:
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.music != None:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        
    def draw(self,screen):
        screen.blit(self.background, (0, 0))

        if self.story != None:
            font = pygame.font.Font(None, 32) #font

            lines = self.story.split("\\n")
            y = 0
            for line in lines:
                q = font.render(line, True, Color.BLACK)
                screen.blit(q, (100, 100+y))
                y+=30