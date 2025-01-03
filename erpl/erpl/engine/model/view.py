import pygame
from .utils import Position, Size, HEIGHT, WIDTH
import requests
from io import BytesIO
from abc import ABC, abstractmethod
from .hitbox import HitboxRect, HitboxTriangle, HitboxCircle, HitboxPolygon, HitboxEllipse, HitboxSquare, Hitbox

"""CLASSE DE UM ESTADO"""
class View:
    def __init__(self, id : str, src_images : [str], size : Size, position : Position, time_sprite : int, repeate : int, hitboxes : [Hitbox]):
        self.id = id
        self.position = position
        self.size = size
        self.src_images = src_images
        # Carregando a image da porta
        self.images = []
        for src_image in self.src_images:
            self.load_image(src_image=src_image)
        
        self.time_sprite = time_sprite

        self.current_sprite = 0
        self.current_time_sprite = 0
        self.repeateInit = repeate
        self.repeate = self.repeateInit
        self.hitboxes = hitboxes
        self.make_hitboxes_bbox()
    
    def load_images(self):
        for i,image in enumerate(self.images):
            self.load_image(self.src_images[i])

    def load_image(self,src_image):
        self.images = []
        try:
            image = pygame.image.load(src_image).convert_alpha()
        except:
            try:
                headers = {
                    "user-agent": "curl/7.84.0",
                    "accept": "*/*"
                }
                response = requests.get(url=src_image,headers=headers)
                image = pygame.image.load(BytesIO(response.content))
            except Exception as e:
                print(e)
                print("No file or url image with source: " + src_image)
                exit(-1)
        image = pygame.transform.scale(image, (self.size.x,self.size.y))  # Ajuste o size conforme necessário
        self.images.append(image)

    def change_size(self, scale):
        position = Position(self.position.x,self.position.y);
    
        self.position.x *= scale.x
        self.position.y *= scale.y
        self.size.x *= scale.x
        self.size.y *= scale.y

        self.load_images()
        
        for hitbox in self.hitboxes:
            hitbox.scale(scale.x,scale.y)

        self.make_hitboxes_bbox()
        self.change_position(position)

    def change_position(self, position):
        self.position.x = position.x
        self.position.y = position.y
        translate_x = position.x-self.hitboxbb['xmin']
        translate_y = position.y-self.hitboxbb['ymin']

        for hitbox in self.hitboxes:
            hitbox.translate(translate_x,translate_y)
        
        self.make_hitboxes_bbox()



    def change_sprite(self):
        self.current_time_sprite += 1
        if self.current_time_sprite == self.time_sprite:
            self.current_time_sprite = 0
            self.current_sprite += 1
            if self.current_sprite == len(self.images):
                self.repeate -= 1
                self.current_sprite = self.current_sprite-1 if self.repeate == 0 else 0


    def draw(self,screen):
        screen.blit(self.images[self.current_sprite], (self.position.x, self.position.y))
        if self.repeate > 0: self.change_sprite()

    def collide(self,px,py):
        collide = False
        for hitbox in self.hitboxes:
           collide = collide or hitbox.collide(px,py)
        return collide

    def make_hitboxes_bbox(self):
        xmin = WIDTH
        ymin = HEIGHT
        xmax = 0
        ymax = 0
        pass

        for hitbox in self.hitboxes:
            if isinstance(hitbox, HitboxRect) or isinstance(hitbox,HitboxSquare) or isinstance(hitbox, HitboxEllipse):
                hitbox_xmin = hitbox.x
                hitbox_ymin = hitbox.y
                hitbox_xmax = hitbox.x+hitbox.w
                hitbox_ymax = hitbox.y+hitbox.h
            elif isinstance(hitbox, HitboxPolygon) or isinstance(hitbox, HitboxTriangle):
                xs = []
                ys = []
                for point in hitbox.points:
                    xs.append(point.x)
                    ys.append(point.y)
                
                hitbox_xmin = min(xs)
                hitbox_ymin = min(ys)
                hitbox_xmax = max(xs)
                hitbox_ymax = min(ys)
            elif isinstance(hitbox, HitboxCircle):
                hitbox_xmin = hitbox.x - hitbox.r
                hitbox_ymin = hitbox.y - hitbox.r
                hitbox_xmax = hitbox.x + hitbox.r
                hitbox_ymax = hitbox.y + hitbox.r
            xmin = min(xmin,hitbox_xmin)
            ymin = min(ymin,hitbox_ymin)
            xmax = max(xmax,hitbox_xmax)
            ymax = max(ymax,hitbox_ymax)
        
        self.hitboxbb = {
            "xmin" : xmin,
            "ymin" : ymin,
            "xmax" : xmax,
            "ymax" : ymax
    }
    

class ViewPeace(View):
    def __init__(self,id,buffer, size : Size, position : Position):
        self.id = id
        self.position = position
        self.size = size
        image = pygame.image.load_extended(buffer).convert_alpha()
        image = pygame.transform.scale(image, (self.size.x,self.size.y))  # Ajuste o size conforme necessário
        self.images = [image]

        self.time_sprite = 0
        self.current_sprite = 0
        self.current_time_sprite = 0
        self.repeateInit = 0
        self.repeate = self.repeateInit

    def change_size(self, size):
        self.size = size
    
    def change_position(self, position):
        self.position = position
    
    def draw(self, screen):
        screen.blit(self.images[self.current_sprite], (self.position.x, self.position.y))

class ViewSketch:
    def __init__(self,id, hitboxes : [Hitbox]):
        self.id = id
        self.draws = []
        self.hitboxes = hitboxes

    def add_draw(self,draw):
        self.draws.append(draw)

    def draw(self,screen):
        for draw in self.draws:
            draw.draw(screen)

    def change_position(self,position):
        translate_x = (position.x-self.bb['xmin'])
        translate_y = (position.y-self.bb['ymin'])
        self.translate(translate_x,translate_y)
    
    def translate(self,tx,ty):
        for draw in self.draws:
            draw.translate(tx,ty)
        for hitbox in self.hitboxes:
            hitbox.translate(tx,ty)
        self.make_bbox()

    def change_size(self,scale):
        pos = Position(self.bb['xmin'],self.bb['ymin'])
        for draw in self.draws:
            draw.scale(scale.x,scale.y)
        for hitbox in self.hitboxes:
            hitbox.scale(scale.x,scale.y)
        self.make_bbox()
        self.change_position(pos)

    def collide(self,px,py):
        collide = False
        for hitbox in self.hitboxes:
           print(hitbox)
           collide = collide or hitbox.collide(px,py)
        return collide

    def make_bbox(self):
        xmin = WIDTH
        ymin = HEIGHT
        xmax = 0
        ymax = 0
        pass

        for draw in self.draws:
            if isinstance(draw, Rect) or isinstance(draw,Square) or isinstance(draw, Ellipse):
                draw_xmin = draw.rect.left
                draw_ymin = draw.rect.top
                draw_xmax = draw.rect.left+draw.rect.width
                draw_ymax = draw.rect.top+draw.rect.height
            elif isinstance(draw, Polygon) or isinstance(draw, Triangle):
                xs = []
                ys = []
                for point in draw.points:
                    xs.append(point[0])
                    ys.append(point[1])
                
                draw_xmin = min(xs)
                draw_ymin = min(ys)
                draw_xmax = max(xs)
                draw_ymax = min(ys)
            elif isinstance(draw, Circle):
                draw_xmin = draw.x - draw.r
                draw_ymin = draw.y - draw.r
                draw_xmax = draw.x + draw.r
                draw_ymax = draw.y + draw.r
            xmin = min(xmin,draw_xmin)
            ymin = min(ymin,draw_ymin)
            xmax = max(xmax,draw_xmax)
            ymax = max(ymax,draw_ymax)
        
        self.bb = {
            "xmin" : xmin,
            "ymin" : ymin,
            "xmax" : xmax,
            "ymax" : ymax
        }


class Draw(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def draw(self,screen):
        pass

    @abstractmethod
    def translate(tx,ty):
        pass

    @abstractmethod
    def scale(sx,sy):
        pass

class Rect(Draw):
    def __init__(self,x,y,w,h,tl,tr,br,bl,color):
        self.rect = pygame.Rect(x, y, w, h)
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.color = pygame.Color(color)

    def draw(self,screen):
        pygame.draw.rect(surface=screen,
                         color=self.color,
                         rect=self.rect,
                         border_top_left_radius=self.tl,
                         border_top_right_radius=self.tr,
                         border_bottom_right_radius=self.br,
                         border_bottom_left_radius=self.bl
                         )
        
    def scale(self,scaleX, scaleY):
        self.rect.left *= scaleX
        self.rect.top *= scaleY
        self.rect.width *= scaleX
        self.rect.height *= scaleY

    def translate(self,tx,ty):
        self.rect.left += tx
        self.rect.top += ty

class Polygon(Draw):
    def __init__(self,points,color):
        self.points = []
        for point in points:
            self.points.append((point['x'],point['y']))
        self.color = pygame.Color(color)

    def draw(self,screen):
        pygame.draw.polygon(surface=screen,
                            color=self.color,
                            points=self.points
        )

    def scale(self,scaleX, scaleY):
        for point in self.points:
            point[0] *= scaleX
            point[1] *= scaleY

    def translate(self,tx, ty):
        for point in self.points:
            point[0] += tx
            point[1] += ty

class Square(Draw):
    def __init__(self,x,y,r,tl,tr,br,bl,color):
        self.rect = pygame.Rect(x, y, r, r)
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.color = pygame.Color(color)

    def draw(self,screen):
        pygame.draw.rect(surface=screen,
                         color=self.color,
                         rect=self.rect,
                         border_top_left_radius=self.tl,
                         border_top_right_radius=self.tr,
                         border_bottom_right_radius=self.br,
                         border_bottom_left_radius=self.bl
                         )
        
    def scale(self,scaleX, scaleY):
        self.rect.left *= scaleX
        self.rect.top *= scaleY
        self.rect.width *= scaleX
        self.rect.height *= scaleY

    def translate(self,tx,ty):
        self.rect.left += tx
        self.rect.top += ty

class Circle(Draw):
    def __init__(self,x,y,r,color):
        self.x = x
        self.y = y
        self.r = r
        self.color = pygame.Color(color)

    def draw(self,screen):
        pygame.draw.circle(screen, self.color, (self.x,self.y), self.r)

    def scale(self,scaleX, scaleY):
        self.x *= scaleX
        self.y *= scaleY
        self.r *= scaleX

    def translate(self,tx,ty):
        self.x += tx
        self.y += ty

class Triangle(Draw):
    def __init__(self,x1,y1,x2,y2,x3,y3,color):
        self.points = [(x1, y1), (x2, y2), (x3, y3)]
        self.color = pygame.Color(color)
    
    def draw(self,screen):
        pygame.draw.polygon(surface=screen,color=self.color,points=self.points)

    def scale(self,scaleX, scaleY):
        for point in self.points:
            point[0] *= scaleX
            point[1] *= scaleY

    def translate(self,tx, ty):
        for point in self.points:
            point[0] += tx
            point[1] += ty

class Ellipse(Draw):
    def __init__(self,x,y,w,h,color):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = pygame.Color(color)

    def draw(self,screen):
        pygame.draw.ellipse(surface=screen,color=self.color,rect=self.rect)

    def scale(self,scaleX, scaleY):
        self.rect.left *= scaleX
        self.rect.top *= scaleY
        self.rect.width *= scaleX
        self.rect.height *= scaleY

    def translate(self,tx,ty):
        self.rect.left += tx
        self.rect.top += ty
