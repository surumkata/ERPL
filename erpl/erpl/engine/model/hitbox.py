import pygame
from abc import ABC, abstractmethod
import math

class Hitbox(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def collide(self,px,py):
        pass

    @abstractmethod
    def translate(tx,ty):
        pass

    @abstractmethod
    def scale(sx,sy):
        pass

class HitboxRect(Hitbox):
    def __init__(self,id,x,y,w,h):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def scale(self,scaleX, scaleY):
        self.x *= scaleX
        self.y *= scaleY
        self.w *= scaleX
        self.h *= scaleY

    def translate(self,tx,ty):
        self.x += tx
        self.y += ty

    def collide(self,px,py):
        return px >= self.x and px <= self.x + self.w and py >= self.y and py <= self.y + self.h

class HitboxPolygon(Hitbox):
    def __init__(self,id,points):
        self.id = id
        self.points = []
        for point in points:
            self.points.append((point['x'],point['y']))

    def scale(self,scaleX, scaleY):
        for point in self.points:
            point[0] *= scaleX
            point[1] *= scaleY

    def translate(self,tx, ty):
        for point in self.points:
            point[0] += tx
            point[1] += ty

    def collide(self,px, py):
        collision = False

        # percorre cada um dos vértices, mais o próximo vértice na lista
        next_vertex = 0
        for current in range(len(self.points)):

            # obtém o próximo vértice na lista, se chegar ao fim, volta para 0
            next_vertex = current + 1
            if next_vertex == len(self.points):
                next_vertex = 0

            # obtém os pontos nos vértices atuais e próximos
            vc = self.points[current]  # c para "current"
            vn = self.points[next_vertex]  # n para "next"

            # compara posição e altera a variável 'collision' de forma alternada
            if ((vc[1] > py and vn[1] < py) or (vc[1] < py and vn[1] > py)) and \
               (px < (vn[0] - vc[0]) * (py - vc[1]) / (vn[1] - vc[1]) + vc[0]):
                collision = not collision

        return collision

class HitboxSquare(Hitbox):
    def __init__(self,id,x,y,r):
        self.id = id
        self.x = x
        self.y = y
        self.w = r
        self.h = r
        
    def scale(self,scaleX, scaleY):
        self.x *= scaleX
        self.y *= scaleY
        self.w *= scaleX
        self.h *= scaleX

    def translate(self,tx,ty):
        self.x += tx
        self.y += ty

    def collide(self,px,py):
        return px >= self.x and px <= self.x + self.w and py >= self.y and py <= self.y + self.h

class HitboxCircle(Hitbox):
    def __init__(self,id,x,y,r):
        self.id = id
        self.x = x
        self.y = y
        self.r = r

    def scale(self,scaleX, scaleY):
        self.x *= scaleX
        self.y *= scaleY
        self.r *= scaleX

    def translate(self,tx,ty):
        self.x += tx
        self.y += ty

    def collide(self,px,py):
        # Calcula os raios em x e y

        # Descartar pontos fora da caixa delimitadora
        if px > self.x + self.r or px < self.x - self.r or py > self.y + self.r or py < self.y - self.r:
            return False

        # Comparar o ponto com seu equivalente na elipse
        xx = px - self.x
        yy = py - self.y
        eyy = self.r * math.sqrt(abs(self.r * self.r - xx * xx)) / self.r

        return yy <= eyy and yy >= -eyy

class HitboxTriangle(Hitbox):
    def __init__(self,id,x1,y1,x2,y2,x3,y3):
        self.id = id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

    def scale(self,scaleX, scaleY):
        self.x1 *= scaleX
        self.y1 *= scaleY
        self.x2 *= scaleX
        self.y2 *= scaleY
        self.x3 *= scaleX
        self.y3 *= scaleY

    def translate(self,tx, ty):
        self.x1 += tx
        self.y1 += ty
        self.x2 += tx
        self.y2 += ty
        self.x3 += tx
        self.y3 += ty

    def collide(self,px, py):
        # obtém a área do triângulo original
        area_orig = abs((self.x2 - self.x1) * (self.y3 - self.y1) - (self.x3 - self.x1) * (self.y2 - self.y1))

        # obtém a área dos 3 triângulos formados entre o ponto e os cantos do triângulo
        area1 = abs((self.x1 - px) * (self.y2 - py) - (self.x2 - px) * (self.y1 - py))
        area2 = abs((self.x2 - px) * (self.y3 - py) - (self.x3 - px) * (self.y2 - py))
        area3 = abs((self.x3 - px) * (self.y1 - py) - (self.x1 - px) * (self.y3 - py))

        # se a soma das três áreas for igual à área original, o ponto está dentro do triângulo!
        return area1 + area2 + area3 == area_orig


class HitboxEllipse(Hitbox):
    def __init__(self,id,x,y,w,h):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def scale(self,scaleX, scaleY):
        self.x *= scaleX
        self.y *= scaleY
        self.w *= scaleX
        self.h *= scaleY

    def translate(self,tx,ty):
        self.x += tx
        self.y += ty
    
    def collide(self,px,py):
        # Calcula os raios em x e y
        rx = self.w / 2
        ry = self.h / 2

        # Descartar pontos fora da caixa delimitadora
        if px > self.x + rx or px < self.x - rx or py > self.y + ry or py < self.y - ry:
            return False

        # Comparar o ponto com seu equivalente na elipse
        xx = px - self.x
        yy = py - self.y
        eyy = ry * math.sqrt(abs(rx * rx - xx * xx)) / rx

        return yy <= eyy and yy >= -eyy