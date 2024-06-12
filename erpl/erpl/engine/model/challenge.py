import pygame
from .utils import WIDTH, HEIGHT, Color, Position, debug, Size
import random
from .state import State, StatePeace
import numpy as np
from PIL import Image
import io
import os
import socket
import time

current_folder = os.path.dirname(__file__)


class ChallengeState():
    def __init__(self, sucess_challenge, fail_challenge):
        self.sucess_challenge = sucess_challenge
        self.fail_challenge = fail_challenge

    def draw(self,screen):
        pass

    def update_pygame_event(self,pygame_event,room):
        pass


class ChallengeStateQuestion(ChallengeState):
    def __init__(self, question, code, sucess_challenge, fail_challenge):
        super().__init__(sucess_challenge,fail_challenge)
        self.question = question
        self.code = code
        self.input_box = pygame.Rect(WIDTH/4+10, HEIGHT/2+10, WIDTH/2-20, HEIGHT/4-20)
        self.input_text = ""
        self.sucess_challenge = sucess_challenge
        self.fail_challenge = fail_challenge
    
    def draw(self,screen):
        background = pygame.Rect(WIDTH/4, HEIGHT/4, WIDTH/2, HEIGHT/2)
        pygame.draw.rect(screen, Color.GRAY, background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, background, 2) #borda preta do input
        font = pygame.font.Font(None, 32) #font
        pygame.draw.rect(screen, Color.WHITE, self.input_box) #quadrado branco de input
        pygame.draw.rect(screen, Color.BLACK, self.input_box, 2) #borda preta do input


        question_surface = font.render(self.question, True, Color.BLACK)
        screen.blit(question_surface, (background.x+10, background.y+10)) #print question


        
        input_surface = font.render(self.input_text, True, Color.BLACK)
        screen.blit(input_surface, (self.input_box.x+5, self.input_box.y+5)) #print input

    def update_pygame_event(self,pygame_event, room):
        if pygame_event.type == pygame.KEYDOWN:
            if pygame_event.key == pygame.K_RETURN:  # Verifica se o jogador pressionou Enter
                debug("CHALLENGE_ASK_CODE: Código Recebido: "+self.input_text+".")
                if self.input_text == self.code:
                    return self.sucess_challenge
                else:
                    return self.fail_challenge
            elif pygame_event.key == pygame.K_BACKSPACE:  # Verifica se o jogador pressionou Backspace
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += pygame_event.unicode  # Adiciona a tecla pressio
        elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
            return 0
        return None


class ChallengeMotion(ChallengeState):
    def __init__(self, sucess_challenge, fail_challenge, object_motion, trigger_motion):
        super().__init__(sucess_challenge,fail_challenge)
        self.object_motion = object_motion
        self.trigger_motion = trigger_motion
        self.last_motion = None

    def draw(self,screen):
        pass

    def update_pygame_event(self,pygame_event, room):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            print("sss")
            self.last_motion = Position(pygame_event.pos[0],pygame_event.pos[1])
        elif pygame_event.type == pygame.MOUSEMOTION:
            self.last_motion = Position(pygame_event.pos[0],pygame_event.pos[1])
            object = room.objects[self.object_motion]
            object.change_position(self.last_motion)
        elif pygame_event.type == pygame.MOUSEBUTTONUP:
            if self.last_motion != None:
                trigger_object = room.objects[self.trigger_motion]
                if(trigger_object.have_clicked(self.last_motion.x,self.last_motion.y)):
                    return self.sucess_challenge
                else:
                    return self.fail_challenge
            else:
                return self.fail_challenge

        return None
    
class ChallengeMultipleChoice(ChallengeState):
    def __init__(self, question, multiple_choices, answer, sucess_challenge, fail_challenge):
        super().__init__(sucess_challenge,fail_challenge)
        self.question = question
        self.multiple_choices = multiple_choices
        self.answer = answer

        self.background = pygame.Rect(WIDTH/8, HEIGHT/8, 3*WIDTH/4, 3*HEIGHT/4)

        self.choice_boxes = [
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 2*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 3*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 4*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 5*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20)
        ]


    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h


    def draw(self,screen):
        pygame.draw.rect(screen, Color.GRAY, self.background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, self.background, 2) #borda preta do input
        font = pygame.font.Font(None, 32) #font

        rect0 = pygame.Rect(WIDTH/8+10, HEIGHT/8+10, 3*WIDTH/4-20, 2*(3*HEIGHT/4)/6-20)
        pygame.draw.rect(screen, Color.WHITE, rect0)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, rect0, 2) #borda preta do input
        lines = self.question.split("\\n")
        y = 0
        for line in lines:
            q = font.render(line, True, Color.BLACK)
            screen.blit(q, (rect0.x+10, rect0.y+10+y)) #print question
            y+=30
        #if len(self.question) > 82:
        #    
        #    l1 = self.question[:82]
        #    l2 = self.question[82:]
        #    l1_surface = font.render(l1, True, Color.BLACK)
        #    l2_surface = font.render(l2, True, Color.BLACK)
        #    screen.blit(l1_surface, (rect0.x+10, rect0.y+10)) #print question
        #    screen.blit(l2_surface, (rect0.x+10, rect0.y+40)) #print question
        #else:
        #    question_surface = font.render(self.question, True, Color.BLACK)
        #    screen.blit(question_surface, (rect0.x+10, rect0.y+10)) #print question

        for i in range(4):
            pygame.draw.rect(screen, Color.WHITE, self.choice_boxes[i])  # Fundo colorido
            pygame.draw.rect(screen, Color.BLACK, self.choice_boxes[i], 2) #borda preta do input
            choice_surface = font.render(self.multiple_choices[i], True, Color.BLACK)
            screen.blit(choice_surface, (self.choice_boxes[i].x+10, self.choice_boxes[i].y+10)) #print question


    def update_pygame_event(self, pygame_event, room):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            #se carregou dentro ou fora da área de challenge
            if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.background):
                #se carregou numa opçao
                for i in range(4):
                    if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.choice_boxes[i]):
                        choice_answer = self.multiple_choices[i]
                        if choice_answer == self.answer:
                            return self.sucess_challenge
                        else:
                            return self.fail_challenge
                return None
            else:
                return 0
        return None


class ChallengeConnections(ChallengeState):
    def __init__(self, question, connections, sucess_challenge, fail_challenge):
        super().__init__(sucess_challenge,fail_challenge)
        self.question = question
        self.connections = connections

        self.lefts = [k for k in self.connections]
        self.rights = [v for v in self.connections.values()]

        random.shuffle(self.lefts)
        random.shuffle(self.rights)

        self.left_choice = None

        self.lefts_dones = []
        self.rights_dones = []

        self.background = pygame.Rect(WIDTH/8, HEIGHT/8, 3*WIDTH/4, 3*HEIGHT/4)

        self.left_boxes = [
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 2*(3*HEIGHT/4)/6, 3*WIDTH/8-30, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 3*(3*HEIGHT/4)/6, 3*WIDTH/8-30, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 4*(3*HEIGHT/4)/6, 3*WIDTH/8-30, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 5*(3*HEIGHT/4)/6, 3*WIDTH/8-30, (3*HEIGHT/4)/6-20)
        ]

        self.right_boxes = [
            pygame.Rect(WIDTH/8+20 + 3*WIDTH/8-20, HEIGHT/8+10 + 2*(3*HEIGHT/4)/6, 3*WIDTH/8-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+20 + 3*WIDTH/8-20, HEIGHT/8+10 + 3*(3*HEIGHT/4)/6, 3*WIDTH/8-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+20 + 3*WIDTH/8-20, HEIGHT/8+10 + 4*(3*HEIGHT/4)/6, 3*WIDTH/8-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+20 + 3*WIDTH/8-20, HEIGHT/8+10 + 5*(3*HEIGHT/4)/6, 3*WIDTH/8-20, (3*HEIGHT/4)/6-20)
        ]

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h

    def draw(self,screen):
        pygame.draw.rect(screen, Color.GRAY, self.background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, self.background, 2) #borda preta do input
        font = pygame.font.Font(None, 32) #font

        rect0 = pygame.Rect(WIDTH/8+10, HEIGHT/8+10, 3*WIDTH/4-20, 2*(3*HEIGHT/4)/6-20)
        pygame.draw.rect(screen, Color.WHITE, rect0)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, rect0, 2) #borda preta do input
        question_surface = font.render(self.question, True, Color.BLACK)
        screen.blit(question_surface, (rect0.x+10, rect0.y+10)) #print question

        for i in range(4):
            if self.lefts[i] not in self.lefts_dones:
                color = Color.WHITE if self.lefts[i] != self.left_choice else Color.RED
                pygame.draw.rect(screen, color, self.left_boxes[i])  # Fundo colorido
                pygame.draw.rect(screen, Color.BLACK, self.left_boxes[i], 2) #borda preta do input
                choice_surface = font.render(self.lefts[i], True, Color.BLACK)
                screen.blit(choice_surface, (self.left_boxes[i].x+10, self.left_boxes[i].y+10)) #print question

            if self.rights[i] not in self.rights_dones:
                pygame.draw.rect(screen, Color.WHITE, self.right_boxes[i])  # Fundo colorido
                pygame.draw.rect(screen, Color.BLACK, self.right_boxes[i], 2) #borda preta do input
                choice_surface = font.render(self.rights[i], True, Color.BLACK)
                screen.blit(choice_surface, (self.right_boxes[i].x+10, self.right_boxes[i].y+10)) #print question


    def update_pygame_event(self, pygame_event, room):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            #se carregou dentro ou fora da área de challenge
            if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.background):
                for i in range(4):
                    if self.lefts[i] not in self.lefts_dones and self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.left_boxes[i]):
                        self.left_choice = self.lefts[i]
                if self.left_choice != None:
                    for i in range(4):
                        if self.rights[i] not in self.rights_dones and self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.right_boxes[i]):
                            if self.connections[self.left_choice] == self.rights[i]:
                                self.lefts_dones.append(self.left_choice)
                                self.rights_dones.append(self.rights[i])
                                if len(self.lefts_dones) == 4:
                                    return self.sucess_challenge
                            else:
                                return self.fail_challenge

            else:
                return 0
        return None

class ChallengeSequence(ChallengeState):
    def __init__(self, question, sequence, sucess_challenge, fail_challenge):
        super().__init__(sucess_challenge,fail_challenge)
        self.question = question
        self.sequence = sequence

        self.shuffle_sequence = list(sequence)
        random.shuffle(self.shuffle_sequence)

        self.choice = 0

        self.dones = []

        self.background = pygame.Rect(WIDTH/8, HEIGHT/8, 3*WIDTH/4, 3*HEIGHT/4)

        self.boxes = [
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 2*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 3*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 4*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20),
            pygame.Rect(WIDTH/8+10, HEIGHT/8+10 + 5*(3*HEIGHT/4)/6, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20)
        ]

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h

    def draw(self,screen):
        pygame.draw.rect(screen, Color.GRAY, self.background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, self.background, 2) #borda preta do input
        font = pygame.font.Font(None, 32) #font

        rect0 = pygame.Rect(WIDTH/8+10, HEIGHT/8+10, 3*WIDTH/4-20, 2*(3*HEIGHT/4)/6-20)
        pygame.draw.rect(screen, Color.WHITE, rect0)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, rect0, 2) #borda preta do input
        question_surface = font.render(self.question, True, Color.BLACK)
        screen.blit(question_surface, (rect0.x+10, rect0.y+10)) #print question

        for i in range(4):
            color = Color.WHITE
            if self.shuffle_sequence[i] in self.dones:
                color = Color.BLUE
            pygame.draw.rect(screen, color, self.boxes[i])  # Fundo colorido
            pygame.draw.rect(screen, Color.BLACK, self.boxes[i], 2) #borda preta do input
            choice_surface = font.render(self.shuffle_sequence[i], True, Color.BLACK)
            screen.blit(choice_surface, (self.boxes[i].x+10, self.boxes[i].y+10)) #print question


    def update_pygame_event(self, pygame_event, room):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            #se carregou dentro ou fora da área de challenge
            if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.background):
                for i in range(4):
                    if self.shuffle_sequence[i] not in self.dones and self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.boxes[i]):
                        if self.sequence[self.choice] != self.shuffle_sequence[i]:
                            return self.fail_challenge
                        else:
                            self.choice+=1
                            self.dones.append(self.shuffle_sequence[i])
                            if self.choice == 4:
                                return self.sucess_challenge

            else:
                return 0
        return None
    

class ChallengeSlidePuzzle(ChallengeState):
    def __init__(self, image, sucess_challenge):
        super().__init__(sucess_challenge,None)
        self.background = pygame.Rect(WIDTH/8, HEIGHT/8, 3*WIDTH/4, 3*HEIGHT/4)
        self.grid_size = (3,3)
        self.size_piece = 100
        positions = []
        gap = 5
        puzzle_width = self.grid_size[0]*self.size_piece
        puzzle_height = self.grid_size[1]*self.size_piece
        offset_x = WIDTH/2-puzzle_width/2
        offset_y = HEIGHT/2-puzzle_height/2
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                positions.append(Position(offset_x+self.size_piece*col+col*gap,offset_y+self.size_piece*row+row*gap))
        row = self.grid_size[1] - 1
        col = self.grid_size[0] - 1
        rect = pygame.Rect(offset_x+self.size_piece*col+col*gap,offset_y+self.size_piece*row+row*gap,self.size_piece,self.size_piece)
        peaces = self.recort_image(image)

        self.matrix = []
        for i in range(self.grid_size[1]*self.grid_size[0]-1):
            self.matrix.append(("P",peaces[i],positions[i]))
        self.matrix.append(("R",rect,positions[i+1]))

    #Função que verifica se foi clicado na área do object
    def have_clicked_peace(self, x : int, y : int, position):
        return position.x <= x <= position.x + self.size_piece and position.y <= y <= position.y  + self.size_piece

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h
    

    def is_adjacent(self, x : int):
        adjacents = []
        adjacents.append(x+self.grid_size[1])
        adjacents.append(x-self.grid_size[1])
        if x % self.grid_size[0] != 0:
            adjacents.append(x-1)
        if (x+1) % self.grid_size[0] != 0:
            adjacents.append(x+1)
        for i in adjacents:
            if i >= 0 and i <=self.grid_size[0] * self.grid_size[1]-1  and self.matrix[i][0] == 'R':
                return i
        return -1
        
    def swap(self,i,x):
        type_i,piece,position_i = self.matrix[i]
        type_x,rect,position_x = self.matrix[x]

        self.matrix[i] = (type_x,rect,position_i)
        self.matrix[x] = (type_i,piece,position_x)
        rect.x = position_i.x
        rect.y = position_i.y
    
    def is_done(self):
        last = -1
        for type,rect,position in self.matrix:
            if type == 'P':
                id,_ = rect
                if id < last:
                    return False
                last = id
            elif last < self.grid_size[0] * self.grid_size[1] - 2:
                return False
        return True

    def recort_image(self, image_path):
        # Abra a image
        image = Image.open(image_path)
        peaces = []
        size = 300
        
        # Redimensione a image para um quadrado
        image = image.resize((size,size))

        # Calcule as dimensões de cada célula do grid
        cell_width = size // self.grid_size[0]
        cell_height = size // self.grid_size[1]
        i = 0
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                # Calcule as coordenadas de recorte para a célula atual
                left = col * cell_width
                upper = row * cell_height
                right = left + cell_width
                lower = upper + cell_height

                # Recorte a image usando as coordenadas calculadas
                cell_image = image.crop((left, upper, right, lower))

                # Salve ou faça o que for necessário com a célula da image
                # Aqui você pode addr ao seu array de images
                buffer = io.BytesIO()
                cell_image.save(buffer, format='PNG')
                buffer.seek(0)

                py_image = pygame.image.load_extended(buffer).convert_alpha()
                py_image = pygame.transform.scale(py_image, (cell_width,cell_height))

                peaces.append((i,py_image))
                if len(peaces) == self.grid_size[0]*self.grid_size[1]-1:
                    break
                # Fechar o object io.BytesIO
                buffer.close()
                i+=1
        # Garante que o embaralhamento seja possível de resolver
        random.shuffle(peaces)
        while not self.is_solvable(peaces):
            random.shuffle(peaces)

        for peace in peaces:
            print(peace[0])

        return peaces

    def is_solvable(self, peaces):
        inversions = 0
        for i in range(len(peaces)):
            for j in range(i + 1, len(peaces)):
                if peaces[i][0] > peaces[j][0]:
                    inversions += 1
        board_size = self.grid_size[0] * self.grid_size[1]
        if board_size % 2 != 0 : #Se o boardsize é impar
            # then é solucionável se o número total de inversões for par
            return inversions % 2 == 0
        else: #se for par
            #then é solucionavel se o number total de inversoes mais a linha em que se encontra o espaço vazio (que neste caso é sempre a ultima) for impar
            return (inversions + self.grid_size[1]-1) % 2 != 0
        
    def draw(self, screen):
        pygame.draw.rect(screen, Color.GRAY, self.background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, self.background, 2) #borda preta do input

        for type,rect,position in self.matrix:
            if type == 'P':
                i,image = rect
                screen.blit(image, (position.x, position.y))
            else:
                pygame.draw.rect(screen, Color.RED, rect)

    def update_pygame_event(self, pygame_event, room):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            #se carregou dentro ou fora da área de challenge
            if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.background):
                i = 0
                for type,rect,position in self.matrix:
                    if type == 'P':
                        if self.have_clicked_peace(pygame_event.pos[0],pygame_event.pos[1],position):
                            x = self.is_adjacent(i)
                            if x != -1:
                                self.swap(i,x)
                                if self.is_done():
                                    return self.sucess_challenge
                                else:
                                    break
                                
                    i+=1
            else:
                return 0
        return None

class ChallengePuzzle(ChallengeState):
    def __init__(self, image, sucess_challenge):
        super().__init__(sucess_challenge,None)



        self.background = pygame.Rect(WIDTH/8, HEIGHT/8, 3*WIDTH/4, 3*HEIGHT/4)
        s = 0.8
        self.sizes = [
            Size(176*s,144*s),
            Size(176*s,176*s),
            Size(168*s,144*s),
            Size(140*s,176*s),
            Size(144*s,200*s),
            Size(168*s,144*s),
            Size(173*s,204*s),
            Size(173*s,152*s),
            Size(176*s,136*s),
            Size(176*s,168*s),
            Size(168*s,136*s),
            Size(141*s,168*s),
        ]
        pd = Position(400,200)
        self.positions = [
            Position(pd.x         , pd.y        ),
            Position(pd.x + 136*s , pd.y        ),
            Position(pd.x + 280*s , pd.y        ),
            Position(pd.x + 417*s , pd.y        ),
            Position(pd.x         , pd.y + 113*s),
            Position(pd.x + 112*s , pd.y + 137*s),
            Position(pd.x + 248*s , pd.y + 109*s),
            Position(pd.x + 384*s , pd.y + 137*s),
            Position(pd.x         , pd.y + 282*s),
            Position(pd.x + 136*s , pd.y + 250*s),
            Position(pd.x + 280*s , pd.y + 282*s),
            Position(pd.x + 416*s , pd.y + 250*s),
        ]

        self.random_positions = [
            Position(200, 140),
            Position(200, 200),
            Position(200, 300),
            Position(200, 400),
            Position(200, 450),
            Position(200, 350),
            Position(900, 200),
            Position(900, 300),
            Position(900, 400),
            Position(900, 450),
            Position(900, 140),
            Position(900, 350),
        ]

        random.shuffle(self.random_positions)

        self.rect = pygame.Rect(pd.x,pd.y,557*s,419*s)

        x = 2
        y = 2
        self.right_places = []
        for i in range(3):
            for j in range(4):
                self.right_places.append(pygame.Rect(pd.x + x,pd.y + y,137*s,137*s))
                x+=138*s
            y+=138*s
            x=2

        self.recort_image(image)

        self.motion = False
        self.motion_peace = -1
        self.dones = []
    #Função que verifica se foi clicado na área do object
    def have_clicked_peace(self, x : int, y : int, p : int):
        return self.peaces[p].position.x <= x <= self.peaces[p].position.x + self.sizes[p].x and self.peaces[p].position.y <= y <= self.peaces[p].position.y  + self.sizes[p].y

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h
        
    def recort_image(self, image):
        # Abra as images
        image = Image.open(image)
        self.peaces = []
        for i in range(0, 12):
            mask = Image.open(f'{current_folder}/../../assets/images/moldes/molde{i}.jpg').convert('L')
    	
            # Redimensione a image para as dimensões do molde
            image_resized = image.resize(mask.size)

            # Empilhe as images
            image_with_transparency = np.dstack((np.array(image_resized), np.array(mask)))

            # Converta para image do tipo PIL
            image_with_transparency_pil = Image.fromarray(image_with_transparency)

            # Encontre os limites not transparentes
            bbox = image_with_transparency_pil.getbbox()

            # Recorte a image usando os limites encontrados
            image_cropped = image_with_transparency_pil.crop(bbox)

            buffer = io.BytesIO()
            image_cropped.save(buffer, format='PNG')
            buffer.seek(0)

            image_pygame = StatePeace(i,buffer,self.sizes[i],self.random_positions[i])

            self.peaces.append(image_pygame)
            
            # Fechar o object io.BytesIO
            buffer.close()

    
    #Função que verifica se foi clicado na área do object
    def have_clicked_peace(self, x : int, y : int, p : int):
        return self.peaces[p].position.x <= x <= self.peaces[p].position.x + self.sizes[p].x and self.peaces[p].position.y <= y <= self.peaces[p].position.y  + self.sizes[p].y

    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h

    def draw(self,screen):
        pygame.draw.rect(screen, Color.GRAY, self.background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, self.background, 2) #borda preta do input


        for i in range(12):
            self.peaces[i].draw(screen)
        
        for i in range(12):
            if i in self.dones:
                continue
            pygame.draw.rect(screen, Color.RED, self.right_places[i], 2)


    def update_pygame_event(self, pygame_event, room):
        if self.motion:
            if pygame_event.type == pygame.MOUSEMOTION:
                self.last_motion = Position(pygame_event.pos[0]+self.adapt_click_x,pygame_event.pos[1]+self.adapt_click_y)
                self.peaces[self.motion_peace].change_position(self.last_motion)
            elif pygame_event.type == pygame.MOUSEBUTTONUP:
                self.motion = False
                if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.right_places[self.motion_peace]):
                    self.peaces[self.motion_peace].change_position(self.positions[self.motion_peace])
                    self.dones.append(self.motion_peace)

                    if len(self.dones) == 12:
                        return self.sucess_challenge
        else:
            if pygame_event.type == pygame.MOUSEBUTTONDOWN:
                if self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.background):
                    for i in range(12):
                        if i in self.dones:
                            continue
                        if self.have_clicked_peace(pygame_event.pos[0],pygame_event.pos[1],i):
                            print(f"CARREGOU NA PEÇA {i}")
                            self.motion = True
                            self.motion_peace = i
                            self.adapt_click_x = (self.peaces[i].position.x-pygame_event.pos[0])
                            self.adapt_click_y = (self.peaces[i].position.y-pygame_event.pos[1])
                            break
                else:
                    return 0

        return None
    
class ChallengeSocketConnection(ChallengeState):
    def __init__(self, host, port, text,sucess_challenge, fail_challenge):
        super().__init__(sucess_challenge,fail_challenge)
        self.host = host
        self.port = port
        self.text = text

        socket_created = False

        while not socket_created:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((self.host, self.port))
                socket_created = True
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    print("Porta já in use. Tentando novamente em alguns seconds...")
                    time.sleep(5)  # Espera 5 seconds antes de tentar novamente
                    continue
                else:
                    raise

        
        # Define um tempo limite de 5 seconds para s.accept()
        self.socket.settimeout(1)
    
        # Começa a escutar conexões
        self.socket.listen()

        self.listening = True


        self.background = pygame.Rect(WIDTH/4, HEIGHT/4, WIDTH/2, HEIGHT/2)
    
    #Função que verifica se foi clicado na área do object
    def have_clicked(self, x : int, y : int, rect):
        return rect.x <= x <= rect.x + rect.w and rect.y <= y <= rect.y  + rect.h

    
    def draw(self,screen):
        pygame.draw.rect(screen, Color.GRAY, self.background)  # Fundo colorido
        pygame.draw.rect(screen, Color.BLACK, self.background, 2) #borda preta do input

        font = pygame.font.Font(None, 32) #font
        text_surface = font.render(self.text, True, Color.BLACK)
        screen.blit(text_surface, (self.background.x+10, self.background.y+10)) #print question

    def update_pygame_event(self,pygame_event, room):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            if not self.have_clicked(pygame_event.pos[0],pygame_event.pos[1],self.background):
                self.listening = False
                self.socket.close()
                debug("Socket closed!")
                return 0
        return None
                
    def listen(self):
        while self.listening:
            try:
                #print("Tentanto connection...")
                conn, addr = self.socket.accept()
                with conn:
                    #print('Conectado por', addr)
                    data = conn.recv(1024)
                    decoded_data = data.decode()
                    debug(f'Mensagem recebida: {decoded_data}')
                    if decoded_data == "-1":
                        return self.fail_challenge
                    elif decoded_data == "0":
                        return 0
                    elif decoded_data == "1":
                        return self.sucess_challenge
                    else:
                        return None
            except socket.timeout:
                # Continue aguardando conexões
                pass
            except OSError as e:
                if e.errno == 9:
                    pass
                else:
                    raise