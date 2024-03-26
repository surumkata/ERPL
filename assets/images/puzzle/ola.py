import cv2


imagem = cv2.imread(f'm.png')
# Obtenha as dimensões da imagem
altura, largura = imagem.shape[:2]
print(f"Largura: {largura}, Altura: {altura}")