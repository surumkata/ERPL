import pygame
from .utils import WIDTH,HEIGHT, Color, Size
from enum import Enum

class State(Enum):
    FINISH = 0
    RUNNING = 1
    CHALLENGE_MODE = 2
    TRANSITION_MODE = 3
    CHALLENGE_LISTENNING = 4

"""CLASSE DE DO ESTADO DE UMA ESCAPE ROOM"""
class GameState:
    def __init__(self,size: Size):
        #Proprities
        self.current_scenario = None
        self.time = 0 #sec
        self.size = size

        #State
        self.state = State.RUNNING
        self.challenge = None
        self.transition = None

        #Buffers
        self.buffer_click_events = []
        self.buffer_current_scenario = None
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
        if self.buffer_current_scenario != None: 
            self.current_scenario = self.buffer_current_scenario

        #Reset
        self.reset_buffers()
        
    def reset_buffers(self):
        self.buffer_click_events = []
        self.buffer_current_scenario = None
        self.buffer_obj_states = {}
        self.buffer_events_happened = []

    def draw_messages(self,screen):
        for message in self.buffer_messages:
            message.display(screen)

    def first_scenario(self, scenario_id : str):
        if self.current_scenario == None:
            self.current_scenario = scenario_id
        
    def update_current_scenario(self, scenario_id : str):
        self.current_scenario = scenario_id

    def is_challenge_mode(self):
        return self.state == State.CHALLENGE_MODE
    
    def is_challenge_listenning(self):
        return self.state == State.CHALLENGE_LISTENNING

    def is_running(self):
        return self.state == State.RUNNING

    def is_finished(self):
        return self.state == State.FINISH
    
    def is_transition(self):
        return self.state == State.TRANSITION_MODE

    def finish_game(self):
        self.state = State.FINISH
    
    def active_challenge_mode(self,challenge):
        self.challenge = challenge
        self.state = State.CHALLENGE_MODE

    def active_listenning_challenge_mode(self,challenge):
        self.challenge = challenge
        self.state = State.CHALLENGE_LISTENNING


    def active_transition_mode(self,transition):
        self.transition = transition
        self.transition.define_size(self.size)
        self.transition.play_music()
        self.state = State.TRANSITION_MODE

    def desactive_challenge_mode(self):
        self.challenge = None
        self.state = State.RUNNING
    
    def desactive_transition_mode(self):
        self.buffer_current_scenario = self.transition.next_scenario
        self.state = State.RUNNING
        self.transition = None
            
    
    def draw_finish_screen(self,screen):
        pygame.draw.rect(screen, Color.GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido/
        font = pygame.font.Font(None, 36)
        text = font.render("Você Escapou!", True, Color.WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
