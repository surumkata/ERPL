from abc import ABC, abstractmethod
from .utils import Position

class Hitbox(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def translate(tx,ty):
        pass

    @abstractmethod
    def scale(sx,sy):
        pass

class HitboxRect(Hitbox):
    def __init__(self,id,x:float,y:float,w:float,h:float):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def scale(self,scaleX:float, scaleY:float):
        self.x *= scaleX
        self.y *= scaleY
        self.w *= scaleX
        self.h *= scaleY

    def translate(self,tx:float,ty:float):
        self.x += tx
        self.y += ty

class HitboxPolygon(Hitbox):
    def __init__(self,id:str,points:[Position]):
        self.id = id
        self.points = []
        for point in points:
            self.points.append((point.x,point.y))

    def scale(self,scaleX:float, scaleY:float):
        for point in self.points:
            point[0] *= scaleX
            point[1] *= scaleY

    def translate(self,tx:float, ty:float):
        for point in self.points:
            point[0] += tx
            point[1] += ty

class HitboxSquare(Hitbox):
    def __init__(self,id:str,x:float,y:float,width:float):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        
    def scale(self,scaleX:float, scaleY:float):
        self.x *= scaleX
        self.y *= scaleY
        self.width *= max(scaleX,scaleY)

    def translate(self,tx:float,ty:float):
        self.x += tx
        self.y += ty

class HitboxCircle(Hitbox):
    def __init__(self,id:str,x:float,y:float,radius:float):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius

    def scale(self,scaleX, scaleY):
        self.x *= scaleX
        self.y *= scaleY
        self.r *= scaleX

    def translate(self,tx,ty):
        self.x += tx
        self.y += ty

class HitboxTriangle(Hitbox):
    def __init__(self,id:str,x1:float,y1:float,x2:float,y2:float,x3:float,y3:float):
        self.id = id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

    def scale(self,scaleX:float, scaleY:float):
        self.x1 *= scaleX
        self.y1 *= scaleY
        self.x2 *= scaleX
        self.y2 *= scaleY
        self.x3 *= scaleX
        self.y3 *= scaleY

    def translate(self,tx:float, ty:float):
        self.x1 += tx
        self.y1 += ty
        self.x2 += tx
        self.y2 += ty
        self.x3 += tx
        self.y3 += ty


class HitboxEllipse(Hitbox):
    def __init__(self,id:str,x:float,y:float,w:float,h:float):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def scale(self,scaleX:float, scaleY:float):
        self.x *= scaleX
        self.y *= scaleY
        self.w *= scaleX
        self.h *= scaleY

    def translate(self,tx:float,ty:float):
        self.x += tx
        self.y += ty