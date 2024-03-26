import pygame
from .utils import WIDTH,HEIGHT, Color
from enum import Enum

class State(Enum):
    FINISH = 0
    RUNNING = 1
    CHALLENGE_MODE = 2

"""CLASSE DE DO ESTADO DE UMA ESCAPE ROOM"""
class GameState:
    def __init__(self):
        #Proprities
        self.current_scene = None
        self.time = 0 #sec

        #State
        self.state = State.RUNNING
        self.challenge = None

        #Buffers
        self.buffer_click_events = []
        self.buffer_current_scene = None
        self.buffer_messages = []
        self.buffer_obj_states = {}
        self.buffer_events_happened = []
        

    def update_buffers(self, room):
        #Atualiza os eventos que foram feitos
        for event in self.buffer_events_happened:
            room.update_event(event)
        self.buffer_events_happened = []
        
        #Adiciona os eventos do buffer à room
        room.update_events_buffer()

        #Atualiza os estados dos objetos
        for obj,obj_state in self.buffer_obj_states.items():
            room.change_object_current_state(obj,obj_state)
        self.buffer_obj_states = {}

        #Atualiza a cena atual
        if self.buffer_current_scene != None: 
            self.current_scene = self.buffer_current_scene

        #Reset
        self.reset_buffers()
        
    def reset_buffers(self):
        self.buffer_click_events = []
        self.buffer_current_scene = None
        self.buffer_obj_states = {}
        self.buffer_events_happened = []

    def draw_messages(self,screen):
        for message in self.buffer_messages:
            message.display(screen)

    def first_scene(self, scene_id : str):
        if self.current_scene == None:
            self.current_scene = scene_id
        
    def update_current_scene(self, scene_id : str):
        self.current_scene = scene_id

    def is_challenge_mode(self):
        return self.state == State.CHALLENGE_MODE

    def is_running(self):
        return self.state == State.RUNNING

    def is_finished(self):
        return self.state == State.FINISH

    def finish_game(self):
        self.state = State.FINISH
    
    def active_challenge_mode(self,challenge):
        self.challenge = challenge
        self.state = State.CHALLENGE_MODE

    def desactive_challenge_mode(self):
        self.challenge = None
        self.state = State.RUNNING
    
    def draw_finish_screen(self,screen):
        pygame.draw.rect(screen, Color.GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido/
        font = pygame.font.Font(None, 36)
        text = font.render("Você Escapou!", True, Color.WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
