import pygame


"""CLASSE DE DO ESTADO DE UMA ESCAPE ROOM"""
class EscapeRoomState:
    def __init__(self):
        self.finish_game = False
        self.current_scene = None
        self.time = 0 #sec
        self.click_events = []
        self.events_happend = []
        self.changed_objects_states = {}
        self.current_scene_buffer = None
        self.messages = []
        self.input_active = False
        self.input_code = None
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.input_text = ""
        self.motion_activated = False
        self.last_motion = None

    def first_scene(self, scene_id : str):
        if self.current_scene == None:
            self.current_scene = scene_id
        
    def update_current_scene(self, scene_id : str):
        self.current_scene = scene_id
    
    def clear_input(self):
        self.input_active = False
        self.input_code = None
        self.input_box = pygame.Rect(100, 100, 140, 32)
        self.input_text = ""