import pygame
from .utils import Color

class Settings():
    def __init__(self):
        self.volume = 0.5
        self.show_info = False
        self.clock = pygame.time.Clock()
        pygame.mixer.music.set_volume(self.volume)
    
    def change_volume(self,v):
        self.volume += v
        self.volume = min(1,self.volume)
        self.volume = max(0,self.volume)
        pygame.mixer.music.set_volume(self.volume)
    
    def draw_info(self,screen):
        # Calcule os FPS
        font = pygame.font.Font(None, 36)
        fps = int(self.clock.get_fps())
        # Renderize o text do FPS na tela
        fps_text = font.render(f"FPS: {fps}", True, Color.RED)
        # Desenhe o text do FPS na tela
        screen.blit(fps_text, (10, 670))
        # Renderize o text na tela
        volume_text = font.render(f"Volume: {int(self.volume * 100)}%", True, Color.BLUE)
        # Desenhe o text na tela
        screen.blit(volume_text, (120, 670))