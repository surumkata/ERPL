import pygame


class Sound:
    def __init__(self, id : str, src_sound : str):
        self.sound = pygame.mixer.Sound(src_sound)
        self.id = id

    def play(self):
        self.sound.play()