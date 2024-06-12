import cv2


image = cv2.imread(f'm.png')
# Obtenha as dimensões da image
altura, largura = image.shape[:2]
print(f"Largura: {largura}, Altura: {altura}")