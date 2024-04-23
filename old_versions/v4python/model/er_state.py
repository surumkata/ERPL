import pygame


"""CLASSE DE DO ESTADO DE UMA ESCAPE ROOM"""
class EscapeRoomState:
    def __init__(self):
        self.finish_game = False
        self.current_scenario = None
        self.time = 0 #sec
        self.click_events = []
        self.events_happend = []
        self.changed_objects_states = {}
        self.current_scenario_buffer = None
        self.messages = []
        self.input_active = False
        self.input_code = None
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.input_text = ""

    def first_scenario(self, scenario_id : str):
        if self.current_scenario == None:
            self.current_scenario = scenario_id
        
    def update_current_scenario(self, scenario_id : str):
        self.current_scenario = scenario_id
    
    def clear_input(self):
        self.input_active = False
        self.input_code = None
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.input_text = ""