#!/usr/bin/python3
from lark.visitors import Interpreter
from lark import Lark
import os
import json
cf = os.path.dirname(__file__)

class ObjInterpreter(Interpreter):
    def __init__(self,id, current_folder):
        self.object = {'views' : []}
        self.id = id
        self.current_folder = current_folder

    def start(self,start):
        '''start : views sounds? view_inicial? position? position_reference? size?'''
        elems = start.children
        #visitar views
        self.visit(elems[0])
        i = 1
        if len(elems) > i and elems[i].data == 'sounds':
            self.visit(elems[i])
            i+=1

        if len(elems) > i and elems[i].data == 'view_inicial':
            id = self.visit(elems[i])
            for view in self.object['views']:
                if view['id'] == id:
                    self.object['initial_view'] = id
            else:
                pass
                #TODO:print error
            i+=1
        if len(elems) > i and elems[i].data == "position":
            self.object['position'] = self.visit(elems[i])
            i+=1
        if len(elems) > i and elems[i].data == "position_reference":
            self.object['position_reference'] = self.visit(elems[i])
        if len(elems) > i and elems[i].data == "size":
            self.object['size'] = self.visit(elems[i])
        return self.object

    def views(self,views):
        '''views : "Views:" view+'''
        elems = views.children
        for elem in elems:
            result = self.visit(elem)
            self.object['views'].append(result)

    def sounds(self,sounds):
        '''sounds : "Sons:" sound+'''
        elems = sounds.children
        for elem in elems:
            result = self.visit(elem)
            if 'sounds' in self.object:
                self.object['sounds'].append(result)
            else:
                self.object['sounds'] = [result]

    
    def view_animado(self,view_animado):
        '''view  : "- View animado" ID ":" images repiticoes timesprite hitboxes'''
        elems = view_animado.children
        id = elems[0].value
        srcs = self.visit(elems[1])
        rs = self.visit(elems[2])
        ts = self.visit(elems[3])

        hitbox_type="DEFAULT"
        hitboxes = []
        if(len(elems) == 5):
            hitboxes = self.visit(elems[4])
            hitbox_type = "ADVANCED" if len(hitboxes) > 0 else "NO"

        return {
            'id' : self.id + '_' + id,
            'sources' : srcs,
            'repetitions' : rs,
            'time_sprite' : ts,
            "type": "VIEW_IMAGE",
            "hitbox_type": hitbox_type,
            "hitboxes" : hitboxes
        }

    def view_simples(self,view_simples):
        '''view : "- View" ID ":" image hitboxes'''
        elems = view_simples.children
        id = elems[0].value
        src = self.visit(elems[1])

        hitbox_type="DEFAULT"
        hitboxes = []
        if(len(elems) == 3):
            hitboxes = self.visit(elems[2])
            hitbox_type = "ADVANCED" if len(hitboxes) > 0 else "NO"

        return {
            'id' : self.id + '_' + id,
            'sources' : src,
            "type": "VIEW_IMAGE",
            "hitbox_type": hitbox_type,
            "hitboxes" : hitboxes
        }
    
    def view_sketch(self,view_sketch):
        '''view : "- Sketch" ID ":" draws hitboxes?'''
        elems = view_sketch.children
        id = elems[0].value
        draws = self.visit(elems[1])
        hitbox_type="DEFAULT"
        hitboxes = []
        if(len(elems) == 3):
            hitboxes = self.visit(elems[2])
            hitbox_type = "ADVANCED" if len(hitboxes) > 0 else "NO"

        return {
            'id' : self.id + '_' + id,
            'draws' : draws,
            "type": "VIEW_SKETCH",
            "hitbox_type": hitbox_type,
            "hitboxes" : hitboxes
        }

    def draws(self,draws):
        '''draws : "- Draws:" draw*'''
        elems = draws.children
        result = []

        for elem in elems:
            draw = self.visit(elem)
            result.append(draw)
        return result
    
    def draw_fill(self,draw):
        '''draw  : "- Fill:" param_color param_alpha?'''
        elems = draw.children
        result = {
            "type" : 'FILL'
        }

        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def draw_rect(self,draw):
        '''draw  : "- Rect:" param_position param_size param_tl? param_tr? param_br? param_bl?'''
        elems = draw.children
        result = {
            "type" : 'RECT'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def draw_square(self,draw):
        '''draw  : "- Square:" param_position param_width param_tl? param_tr? param_br? param_bl?'''
        elems = draw.children
        result = {
            "type" : 'SQUARE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def draw_circle(self,draw):
        '''draw  : "- Circle:" param_position param_radius'''
        elems = draw.children
        result = {
            "type" : 'CIRCLE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def draw_ellipse(self,draw):
        '''draw  : "- Circle:" param_position param_size'''
        elems = draw.children
        result = {
            "type" : 'ELLIPSE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def draw_triangle(self,draw):
        '''draw  : "- Triangle:" param_point1 param_point2 param_point3'''
        elems = draw.children
        result = {
            "type" : 'TRIANGLE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def draw_polygon(self,draw):
        '''draw  : "- Polygon:" param_points'''
        elems = draw.children
        result = {
            "type" : 'POLYGON'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def hitbox_rect(self,hitbox):
        '''draw  : "- Rect:" param_position param_size param_tl? param_tr? param_br? param_bl?'''
        elems = hitbox.children
        result = {
            "type" : 'RECT'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def hitbox_square(self,hitbox):
        '''draw  : "- Square:" param_position param_width param_tl? param_tr? param_br? param_bl?'''
        elems = hitbox.children
        result = {
            "type" : 'SQUARE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def hitbox_circle(self,hitbox):
        '''draw  : "- Circle:" param_position param_radius'''
        elems = hitbox.children
        result = {
            "type" : 'CIRCLE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def hitbox_ellipse(self,hitbox):
        '''draw  : "- Circle:" param_position param_size'''
        elems = hitbox.children
        result = {
            "type" : 'ELLIPSE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def hitbox_triangle(self,hitbox):
        '''draw  : "- Triangle:" param_point1 param_point2 param_point3'''
        elems = hitbox.children
        result = {
            "type" : 'TRIANGLE'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def hitbox_polygon(self,hitbox):
        '''hitbox  : "- Polygon:" param_points'''
        elems = hitbox.children
        result = {
            "type" : 'POLYGON'
        }
        
        for elem in elems:
            (param,value) = self.visit(elem)
            result[param] = value

        return result
    
    def param_color(self,param):
        '''param_color : ("color" "=")? color'''
        elems = param.children
        value = self.visit(elems[0])

        return ("color",value)
    
    def loop(self,loop):
        '''loop : "- Loop:" BOOLEAN'''
        child = loop.children[0]
        value = child.value
        return True if value == 'yes' else False
    
    def param_position(self,param):
        '''param_position : ("position" "=")? point'''
        elems = param.children
        value = self.visit(elems[0])

        return ("position",value)
    
    def param_size(self,param):
        '''param_size : ("size" "=")? point'''
        elems = param.children
        value = self.visit(elems[0])

        return ("size",value)
    
    def param_point1(self,param):
        '''param_point1 : ("point1" "=")? point'''
        elems = param.children
        value = self.visit(elems[0])

        return ("point1",value)
    
    def param_point2(self,param):
        '''param_point2 : ("point2" "=")? point'''
        elems = param.children
        value = self.visit(elems[0])

        return ("point2",value)
    
    def param_point3(self,param):
        '''param_point3 : ("point3" "=")? point'''
        elems = param.children
        value = self.visit(elems[0])

        return ("point3",value)
    
    def param_points(self,param):
        '''param_points : ("points" "=")? "[" point ("," point)* "]" '''
        elems = param.children
        value = []
        for elem in elems:
            value.append(self.visit(elem))

        return ("points",value)
    
    def param_width(self,param):
        '''param_width : ("width" "=")? NUM'''
        elems = param.children
        value = float(elems[0].value)

        return ("width",value)
    
    def param_radius(self,param):
        '''param_radius : ("radius" "=")? NUM'''
        elems = param.children
        value = float(elems[0].value)

        return ("radius",value)
    
    def param_tl(self,param):
        '''param_tl : ("tl" "=")? NUM'''
        elems = param.children
        value = float(elems[0].value)

        return ("tl",value)
    
    def param_tr(self,param):
        '''param_tr : ("tr" "=")? NUM'''
        elems = param.children
        value = float(elems[0].value)

        return ("tr",value)
    
    def param_bl(self,param):
        '''param_bl : ("bl" "=")? NUM'''
        elems = param.children
        value = float(elems[0].value)

        return ("bl",value)
    
    def param_br(self,param):
        '''param_br : ("br" "=")? NUM'''
        elems = param.children
        value = float(elems[0].value)

        return ("br",value)
    
    def param_alpha(self,param):
        '''param_br : ("alpha" "=")? INT'''
        elems = param.children
        value = int(elems[0].value)

        return ("alpha",value)
    
    def color_hex(self,color):
        '''color : "#" HEXCODE'''
        hexcode = color.children[0].value
        if len(hexcode) == 3:
            hexcode = ''.join([c*2 for c in hexcode])
        return "#" + hexcode

    def color_rgb(self,color):
        '''color : "rgb" "(" INT "," INT "," INT ")"'''
        elems = color.children
        r = int(elems[0].value)
        g = int(elems[1].value)
        b = int(elems[2].value)
        if(r < 0 or r > 255):
            print(f"ERROR: Esperado um valor de vermelho entre 0 e 255 e recebido o valor: {r}.")
            exit(-1)
        if(g < 0 or g > 255):
            print(f"ERROR: Esperado um valor de verde entre 0 e 255 e recebido o valor: {g}.")
            exit(-1)
        if(b < 0 or b > 255):
            print(f"ERROR: Esperado um valor de azul entre 0 e 255 e recebido o valor: {b}.")
            exit(-1)

        return f"#{r:02x}{g:02x}{b:02x}"
    
    def color_hsb(self,color):
        '''color : "hsb" "(" INT "," INT "," INT ")"'''
        elems = color.children
        h = int(elems[0].value)
        if(h < 0 or h > 360):
            print(f"ERROR: Esperado um valor de hue entre 0 e 360 e recebido o valor: {h}.")
            exit(-1)
        s = int(elems[1].value)
        if(s < 0 or s > 100):
            print(f"ERROR: Esperado um valor de saturação entre 0 e 100 e recebido o valor: {s}.")
            exit(-1)
        b = int(elems[2].value)
        if(b < 0 or b > 100):
            print(f"ERROR: Esperado um valor de azul entre 0 e 100 e recebido o valor: {b}.")
            exit(-1)

        s /= 100  # Converter S para o intervalo [0, 1]
        b /= 100  # Converter B para o intervalo [0, 1]

        c = b * s  # Chroma: intensidade da cor
        x = c * (1 - abs((h / 60) % 2 - 1))  # Componente intermediário
        m = b - c  # Ajuste de luminosidade

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        elif 300 <= h < 360:
            r, g, b = c, 0, x

        # Converter RGB para o intervalo [0, 255]
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)

        return f"#{r:02x}{g:02x}{b:02x}"

    def sound(self, sound):
        '''sound : "Sound" ID ":" "\n" source "\n" loop'''
        elems = sound.children
        id = elems[0].value
        src = self.visit(elems[1])

        loop = self.visit(elems[2]) if len(elems) == 3 else False

        return {
            'id' : self.id + '_' + id,
            'sources' : src,
            'loop' : loop
        }

    def images(self,images):
        '''images : "- Imagens:" "[" TEXTO ("," TEXTO)* "]"'''
        elems = images.children
        srcs = []
        for elem in elems:
            src = f"{self.current_folder}/{elem.value[1:-1]}"
            file = open(src)
            src = os.path.realpath(file.name)
            file.close()
            srcs.append(["PATH",src])
        return srcs

    def image(self,image):
        '''image  : "- Imagem:" TEXTO'''
        elems = image.children
        src = f"{self.current_folder}/{elems[0].value[1:-1]}"
        file = open(src)
        src = os.path.realpath(file.name)
        file.close()
        return [["PATH",src]]
    
    def source(self,source):
        '''source  : "- Fonte:" TEXTO'''
        elems = source.children
        src = f"{self.current_folder}/{elems[0].value[1:-1]}"
        file = open(src)
        src = os.path.realpath(file.name)
        file.close()
        return [["PATH",src]]

    def repiticoes(self,repiticoes):
        '''repiticoes: "- Repitições:" INT'''
        elems = repiticoes.children
        rs = int(elems[0].value)
        return rs

    def timesprite(self,timesprite):
        '''timesprite: "- Time-Sprite:" INT'''
        elems = timesprite.children
        ts = int(elems[0].value)
        return ts

    def view_inicial(self,view_inicial):
        '''view_inicial: "- View inicial:" ID'''
        elems = view_inicial.children
        id = self.id + '_' + elems[0].value
        return id

    def position(self,position):
        '''position: "- Posição:" point'''
        elems = position.children
        return self.visit(elems[0])
    
    def point(self,point):
        '''point: "(" NUM "," NUM ")"'''
        elems = point.children
        x = float(elems[0].value)
        y = float(elems[1].value)
        return {"x" : x,"y" : y}

    def position_reference(self,position):
        '''position_reference: "- Posição Referenência:" POS_REF"'''
        value = position.children[0].value
        return value

    def size(self,size):
        '''size: "- Tamanho:" point'''
        elems = size.children
        return self.visit(elems[0])
    
def parse_obj(obj_id):
    file = open(f"{cf}/../assets/objects/{obj_id}/{obj_id}.json")
    data = json.load(file)

    folder = f"{cf}/../assets/objects/{obj_id}/"

    for section in ['views', 'sounds']:
        for item in data.get(section, []):
            if 'sources' not in item:
                continue
            for source in item['sources']:
                if source[0] == "PATH":
                    source[1] = folder + source[1]

    return data

def parse_new_obj(obj_path, obj_id, current_folder):
    grammar = open(f"{cf}/grammar_erobj.txt","r")

    file = open(obj_path)
    code = file.read()
    #print(code)
    file.close()

    # analisar frase com a gramatica definida
    p = Lark(grammar)
    parse_tree = p.parse(code)
    it = ObjInterpreter(obj_id,current_folder)
    data = it.visit(parse_tree)
    return data