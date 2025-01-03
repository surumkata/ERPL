import pygame


class Sound:
    def __init__(self, id : str, src_sound : str, loop : bool):
        self.sound = pygame.mixer.Sound(src_sound)
        self.id = id
        self.loop = loop

    def play(self):
        if self.loop:
            self.sound.play(-1)
        else:
            self.sound.play()