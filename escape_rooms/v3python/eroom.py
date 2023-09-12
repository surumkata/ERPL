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
finish_game = False
have_key = False  # Variável para verificar se o jogador tem a chave
key_activated = False  # Variável para verificar se a chave está ativada

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not key_activated:
                # Verifique se o clique ocorreu na área da chave no inventário
                if inventory_x <= event.pos[0] <= inventory_x + 50 and inventory_y <= event.pos[1] <= inventory_y + 50:
                    key_activated = not key_activated  # Alternar o estado da chave
            else:
                # Verifique se o clique ocorreu na área da porta
                if door_x <= event.pos[0] <= door_x + 100 and door_y <= event.pos[1] <= door_y + 200:
                    if have_key:
                        finish_game = True
    
            # Verifique se o clique ocorreu na área da chave no cenário
            if key_x <= event.pos[0] <= key_x + 50 and key_y <= event.pos[1] <= key_y + 50 and not have_key:
                have_key = True
    
    # Desenhar a imagem de fundo
    screen.blit(background, (0, 0))
    
    # Desenhar a imagem da porta na posição especificada
    screen.blit(door, (door_x, door_y))

    # Desenhar a imagem da chave na posição especificada, apenas se o jogador não a tiver coletado
    if not have_key:
        screen.blit(key_inactive, (key_x, key_y))
    
    # Desenhar o inventário
    if have_key:
        if key_activated:
            screen.blit(key_active, (inventory_x, inventory_y))  # Exibe a chave ativa no inventário
        else:
            screen.blit(key_inactive, (inventory_x, inventory_y))  # Exibe a chave inativa no inventário

    # Exibir a mensagem se finish_game for True
    if finish_game:
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, HEIGHT))  # Fundo colorido
        font = pygame.font.Font(None, 36)
        text = font.render("Você Escapou!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    
    
    
    pygame.display.flip()

# Encerramento do jogo
pygame.quit()
sys.exit()
