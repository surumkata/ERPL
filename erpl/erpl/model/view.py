from .utils import Position, Size, HEIGHT, WIDTH
from abc import ABC, abstractmethod
from .hitbox import HitboxRect, HitboxTriangle, HitboxCircle, HitboxPolygon, HitboxEllipse, HitboxSquare, Hitbox
import os

class View(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def translateTo(tx,ty):
        pass

    @abstractmethod
    def scaleTo(sx,sy):
        pass


"""CLASSE DE UM ESTADO"""
class Image(View):
    def __init__(self, id : str, src_image : str, size : Size = None, position : Position = None, hitboxes : [Hitbox] = []):
        self.id = id
        self.position = position
        self.size = size
        file = open(src_image)
        self.sources = [["PATH",os.path.realpath(file.name)]]
        file.close()
        self.hitboxes = hitboxes

    def serialize(self):
        return {
            'id' : self.id,
            'type' : 'VIEW_IMAGE',
            'position' : {
                'x' : self.position.x,
                'y' : self.position.y
            },
            'size' : {
                'x' : self.size.x,
                'y' : self.size.y
            },
            'sources' : self.sources,
            'hitboxes' : [],
            'hitbox_type' : 'DEFAULT'
        }

    def scaleTo(self, scaleX: float,scaleY: float):
        tX,tY = self.position.x,self.position.y
    
        self.position.x *= scaleX
        self.position.y *= scaleY
        self.size.x *= scaleX
        self.size.y *= scaleY
        
        for hitbox in self.hitboxes:
            hitbox.scale(scaleX,scaleY)

        self.__make_hitboxes_bbox()
        self.translateTo(tX,tY)

    def translateTo(self, tX: float, tY: float):
        self.position.x = tX
        self.position.y = tY
        translate_x = tX-self.minX
        translate_y = tY-self.minY

        for hitbox in self.hitboxes:
            hitbox.translate(translate_x,translate_y)
        
        self.__make_hitboxes_bbox()

    def __make_hitboxes_bbox(self):
        self.minX = WIDTH
        self.minY = HEIGHT

        for hitbox in self.hitboxes:
            if isinstance(hitbox, HitboxRect) or isinstance(hitbox,HitboxSquare):
                hitbox_xmin = hitbox.x
                hitbox_ymin = hitbox.y
            elif isinstance(hitbox, HitboxEllipse):
                hitbox_xmin = hitbox.x - hitbox.radiusW
                hitbox_ymin = hitbox.y = hitbox.radiusH
            elif isinstance(hitbox, HitboxPolygon):
                xs = []
                ys = []
                for point in hitbox.points:
                    xs.append(point.x)
                    ys.append(point.y)
                
                hitbox_xmin = min(xs)
                hitbox_ymin = min(ys)
            elif isinstance(hitbox, HitboxTriangle):
                hitbox_xmin = min(hitbox.x1,hitbox.x2,hitbox.x3)
                hitbox_ymin = min(hitbox.y1,hitbox.y2,hitbox.y3)
            elif isinstance(hitbox, HitboxCircle):
                hitbox_xmin = hitbox.x - hitbox.radius
                hitbox_ymin = hitbox.y - hitbox.radius
            self.minX = min(self.minX,hitbox_xmin)
            self.minY = min(self.minY,hitbox_ymin)

"""CLASSE DE UM ESTADO"""
class Animation(View):
    def __init__(self, id : str, src_images : [str], size : Size = None, position : Position = None, time_sprite : int = 0, repetitions : int = 0, hitboxes : [Hitbox] = []):
        self.id = id
        self.position = position
        self.size = size
        self.src_images = src_images
        self.time_sprite = time_sprite
        self.repetitions = repetitions
        self.hitboxes = hitboxes

    def scaleTo(self, scaleX: float,scaleY: float):
        tX,tY = self.position.x,self.position.y
    
        self.position.x *= scaleX
        self.position.y *= scaleY
        self.size.x *= scaleX
        self.size.y *= scaleY
        
        for hitbox in self.hitboxes:
            hitbox.scale(scaleX,scaleY)

        self.__make_hitboxes_bbox()
        self.translateTo(tX,tY)

    def translateTo(self, tX: float, tY: float):
        self.position.x = tX
        self.position.y = tY
        translate_x = tX-self.minX
        translate_y = tY-self.minY

        for hitbox in self.hitboxes:
            hitbox.translate(translate_x,translate_y)
        
        self.__make_hitboxes_bbox()

    def __make_hitboxes_bbox(self):
        self.minX = WIDTH
        self.minY = HEIGHT

        for hitbox in self.hitboxes:
            if isinstance(hitbox, HitboxRect) or isinstance(hitbox,HitboxSquare):
                hitbox_xmin = hitbox.x
                hitbox_ymin = hitbox.y
            elif isinstance(hitbox, HitboxEllipse):
                hitbox_xmin = hitbox.x - hitbox.radiusW
                hitbox_ymin = hitbox.y = hitbox.radiusH
            elif isinstance(hitbox, HitboxPolygon):
                xs = []
                ys = []
                for point in hitbox.points:
                    xs.append(point.x)
                    ys.append(point.y)
                
                hitbox_xmin = min(xs)
                hitbox_ymin = min(ys)
            elif isinstance(hitbox, HitboxTriangle):
                hitbox_xmin = min(hitbox.x1,hitbox.x2,hitbox.x3)
                hitbox_ymin = min(hitbox.y1,hitbox.y2,hitbox.y3)
            elif isinstance(hitbox, HitboxCircle):
                hitbox_xmin = hitbox.x - hitbox.radius
                hitbox_ymin = hitbox.y - hitbox.radius
            self.minX = min(self.minX,hitbox_xmin)
            self.minY = min(self.minY,hitbox_ymin)

class Draw(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def translate(tx,ty):
        pass

    @abstractmethod
    def scale(sx,sy):
        pass

class Rect(Draw):
    def __init__(self,x: float,y: float,w: float,h: float,tl: float=0,tr: float=0,br: float=0,bl: float=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl

    def scale(self,scaleX: float, scaleY: float):
        self.x *= scaleX
        self.y *= scaleY
        self.w *= scaleX
        self.h *= scaleY

    def translate(self,tx: float,ty: float):
        self.x += tx
        self.y += ty

class Polygon(Draw):
    def __init__(self,points : [Position]):
        self.points = []
        for point in points:
            self.points.append((point.x,point.y))

    def scale(self,scaleX : float, scaleY: float):
        for point in self.points:
            point[0] *= scaleX
            point[1] *= scaleY

    def translate(self,tx: float, ty: float):
        for point in self.points:
            point[0] += tx
            point[1] += ty

class Square(Draw):
    def __init__(self,x : float,y : float,width : float,tl : float=0,tr : float=0,br : float=0,bl : float=0):
        self.x = x
        self.y = y
        self.width = width
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        
    def scale(self,scaleX: float, scaleY: float):
        self.x     *= scaleX
        self.y     *= scaleY
        self.width *= max(scaleX,scaleY)

    def translate(self,tx: float,ty: float):
        self.x += tx
        self.y += ty

class Circle(Draw):
    def __init__(self,x : float,y : float,radius : float):
        self.x = x
        self.y = y
        self.radius = radius

    def scale(self,scaleX : float, scaleY : float):
        self.x *= scaleX
        self.y *= scaleY
        self.radius *= max(scaleX,scaleY)

    def translate(self,tx : float,ty : float):
        self.x += tx
        self.y += ty

class Triangle(Draw):
    def __init__(self,x1 : float,y1 : float,x2 : float,y2 : float,x3 : float,y3 : float):
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3

    def scale(self,scaleX : float, scaleY : float):
        self.x1 *= scaleX
        self.x2 *= scaleX
        self.x3 *= scaleX
        self.y1 *= scaleY
        self.y2 *= scaleY
        self.y3 *= scaleY

    def translate(self,tX : float, tY : float):
        self.x1 += tX
        self.x2 += tX
        self.x3 += tX
        self.y1 += tY
        self.y2 += tY
        self.y3 += tY

class Ellipse(Draw):
    def __init__(self,x : float,y : float, radiusW : float, radiusH : float):
        self.x = x
        self.y = y
        self.radiusW = radiusW
        self.radiusH = radiusH

    def scale(self,scaleX : float , scaleY : float):
        self.x *= scaleX
        self.y *= scaleY
        self.radiusW *= scaleX
        self.radiusH *= scaleY

    def translate(self,tx : float,ty : float):
        self.x += tx
        self.y += ty


class Sketch(View):
    def __init__(self, id : str, draws : [Draw], hitboxes : [Hitbox]):
        self.id = id
        self.draws = draws
        self.hitboxes = hitboxes

    def add_draw(self,draw : Draw):
        self.draws.append(draw)


    def translateTo(self,tX : float,tY : float):
        translate_x = (tX-self.minX)
        translate_y = (tY-self.minY)
        self.__translate(translate_x,translate_y)
    
    def __translate(self,tX : float,tY : float):
        for draw in self.draws:
            draw.translate(tX,tY)
        for hitbox in self.hitboxes:
            hitbox.translate(tX,tY)
        self.__make_bbox()

    def scaleTo(self,scaleX,scaleY):
        tX,tY = self.minX,self.minY
        for draw in self.draws:
            draw.scale(scaleX,scaleY)
        for hitbox in self.hitboxes:
            hitbox.scale(scaleX,scaleY)
        self.__make_bbox()
        self.translateTo(tX,tY)

    def __make_bbox(self):
        self.minX = WIDTH
        self.minY = HEIGHT

        for draw in self.draws:
            if isinstance(draw, Rect) or isinstance(draw,Square):
                draw_xmin = draw.x
                draw_ymin = draw.y
            elif isinstance(draw, Ellipse):
                draw_xmin = draw.x - draw.radiusW
                draw_ymin = draw.y = draw.radiusH
            elif isinstance(draw, Polygon):
                xs = []
                ys = []
                for point in draw.points:
                    xs.append(point.x)
                    ys.append(point.y)
                
                draw_xmin = min(xs)
                draw_ymin = min(ys)
            elif isinstance(draw, Triangle):
                draw_xmin = min(draw.x1,draw.x2,draw.x3)
                draw_ymin = min(draw.y1,draw.y2,draw.y3)
            elif isinstance(draw, Circle):
                draw_xmin = draw.x - draw.radius
                draw_ymin = draw.y - draw.radius
            self.minX = min(self.minX,draw_xmin)
            self.minY = min(self.minY,draw_ymin)
