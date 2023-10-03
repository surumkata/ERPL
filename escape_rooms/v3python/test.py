import pygame
import sys
__images = "../../images/"


# Inicialização do Pygame
pygame.init()

# Configurações do jogo
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Room 2D")

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)

# Carregando a imagem de fundo
background = pygame.image.load(__images + "room.png")  # Substitua "background.jpg" pelo nome da sua imagem de fundo
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Carregando a imagem da porta
door = pygame.image.load(__images + "door.png")  # Substitua "door.png" pelo nome da sua imagem da porta
door = pygame.transform.scale(door, (100, 200))  # Ajuste o tamanho conforme necessário

# Carregando a imagem da chave inativa
key_inactive = pygame.image.load(__images + "key.png")  # Substitua "key.png" pelo nome da sua imagem da chave inativa
key_inactive = pygame.transform.scale(key_inactive, (50, 50))  # Ajuste o tamanho conforme necessário

# Carregando a imagem da chave ativa
key_active = pygame.image.load(__images + "active_key.png")  # Substitua "active_key.png" pelo nome da sua imagem da chave ativa
key_active = pygame.transform.scale(key_active, (50, 50))  # Ajuste o tamanho conforme necessário

# Posições dos objetos na tela
door_x, door_y = 600, 300  # Posição da porta
key_x, key_y = 200, 400    # Posição da chave

# Posição do inventário
inventory_x, inventory_y = 10, 10

# Variáveis para controlar a exibição da mensagem
show_message = False
message_text = ""
message_x, message_y = 0, 0
message_display_time = 60  # Tempo de exibição da mensagem em quadros
have_key = False
key_activated = False


# Variável para controlar a entrada do jogador
input_box = pygame.Rect(100, 100, 140, 32)
input_text = ""
input_active = False

# Classe para representar mensagens de balão de fala
class BalloonMessage:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def display(self):
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (self.x, self.y)
        pygame.draw.rect(screen, GREEN, (text_rect.left - 10, text_rect.top - 5, text_rect.width + 20, text_rect.height + 10))
        screen.blit(text_surface, text_rect)

# Lista de mensagens de balão de fala
balloon_messages = []

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Verifique se o mouse está fora da área da mensagem e clique para fechá-la
            if not message_x <= pygame.mouse.get_pos()[0] <= message_x + 260 or not message_y <= pygame.mouse.get_pos()[1] <= message_y + 60:
                if pygame.mouse.get_pressed()[0]:
                    balloon_messages.clear()

            # Verifique se o clique ocorreu na área da chave no inventário
            if have_key:
                if inventory_x <= event.pos[0] <= inventory_x + 50 and inventory_y <= event.pos[1] <= inventory_y + 50:
                    key_activated = not key_activated  # Alternar o estado da chave
                else:
                    # Verifique se o clique ocorreu na área da porta
                    if door_x <= event.pos[0] <= door_x + 100 and door_y <= event.pos[1] <= door_y + 200:
                        if key_activated:
                            show_message = True
    
            # Verifique se o clique ocorreu na área da chave no cenário
            elif key_x <= event.pos[0] <= key_x + 50 and key_y <= event.pos[1] <= key_y + 50:
                input_text = ""
                input_active = True
                # Mostrar a mensagem de balão de fala
                message_text = "Você deseja pegar a chave? Digite 'SIM' para confirmar."
                balloon_messages.append(BalloonMessage(message_text, key_x + 25, key_y - 30))
        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:  # Verifica se o jogador pressionou Enter
                    if input_text.upper() == "SIM":
                        have_key = True
                        message_text = "Pegaste na chave!"
                    else:
                        message_text = "Resposta incorreta!"
                    balloon_messages.append(BalloonMessage(message_text, input_box.x, input_box.y - 30))
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  # Verifica se o jogador pressionou Backspace
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode  # Adiciona a tecla pressionada à entrada do jogador
    
    # Desenhar a imagem de fundo
    screen.blit(background, (0, 0))
    
    # Desenhar a imagem da porta na posição especificada
    screen.blit(door, (door_x, door_y))
    
    # Exibir a mensagem se show_message for True
    if show_message:
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido
        font = pygame.font.Font(None, 36)
        text = font.render("Você Escapou!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    
    # Desenhar o inventário
    if have_key:
        if key_activated:
            screen.blit(key_active, (inventory_x, inventory_y))  # Exibe a chave ativa no inventário
        else:
            screen.blit(key_inactive, (inventory_x, inventory_y))  # Exibe a chave inativa no inventário
    else:
        screen.blit(key_inactive,(key_x,key_y))
    
    # Exibir as mensagens de balão de fala
    for message in balloon_messages:
        message.display()
    
    # Exibir o prompt de entrada do jogador
    if input_active:
        pygame.draw.rect(screen, WHITE, input_box)
        font = pygame.font.Font(None, 32)
        input_surface = font.render(input_text, True, BLACK)
        width = max(200, input_surface.get_width()+10)
        input_box.w = width
        screen.blit(input_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, BLACK, input_box, 2)


    pygame.display.flip()

# Encerramento do jogo
pygame.quit()
sys.exit()
