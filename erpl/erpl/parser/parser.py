#!/usr/bin/python3
from lark.visitors import Interpreter
from lark import Lark, Token, Tree
import sys
import json
import os
from PIL import Image
import copy
import math
import requests
import re
from io import BytesIO

from .obj_parser import parse_obj

from erpl.model.object import Object
from erpl.model.scenario import Scenario
from erpl.model.event import Event

current_folder = os.path.dirname(__file__)

class Interpreter(Interpreter):
    def __init__(self, args):
        
        self.WIDTH = 1280
        self.HEIGHT = 720

        self.FLOOR = 720
        self.CEIL = 0

        self.aux = 0

        self.args = args

        #variáveis para o python_block
        self.locals_python = {}
        self.globals_python = {}
        self.namespace = {}
        
        #variáveis
        self.dict_vars = {}

        self.restricted_vars = ["_timer_", "_timerms_", "_sucesses_", "_fails_"]
        regressive_timer_vars = [f"_regressive_timer_{minuto}min_" for minuto in range(1, 91)]
        self.restricted_vars.extend(regressive_timer_vars)

        self.buffer_scale = []
        self.buffer_translate = []


        #variáveis para imports
        self.dict_imports = {
            'objects' : {}
        }


    def getMinBB(self,draws):
        minX = self.WIDTH
        minY = self.HEIGHT

        for draw in draws:
            draw_minX = self.WIDTH
            draw_minY = self.HEIGHT
            type_ = draw['type']
            if(type_ == 'RECT' or type_ == 'SQUARE'):
                draw_minX = draw['position']['x']
                draw_minY = draw['position']['y'] 
            if(type_ == 'POLYGON'):
                xs = []
                ys = []
                for point in draw['points']:
                    xs.append(point['x'])
                    ys.append(point['y'])
                draw_minX = min(xs)
                draw_minY = min(ys) 
            if(type_ == 'CIRCLE'):
                draw_minX = draw['position']['x'] - draw['radius']
                draw_minY = draw['position']['y'] - draw['radius']  
            if(type_ == 'ELLIPSE'):
                draw_minX = draw['position']['x'] - draw['size']['x']
                draw_minY = draw['position']['y'] - draw['size']['y'] 
            if(type_ == 'TRIANGLE'):
                x1,x2,x3 = draw['point1']['x'],draw['point2']['x'],draw['point3']['x']
                y1,y2,y3 = draw['point1']['y'],draw['point2']['y'],draw['point3']['y']
                draw_minX = min(x1,x2,x3)
                draw_minY = min(y1,y2,y3)
            minX = min(minX,draw_minX)
            minY = min(minY,draw_minY)
        return minX,minY

    def translateDraws(self,draws,tX,tY):
        for draw in draws:
           type_ = draw['type']
           if(type_ in ['RECT','SQUARE','ELLIPSE','CIRCLE']):
               draw['position']['x'] += tX
               draw['position']['y'] += tY
           if(type_ == 'POLYGON'):
               for point in draw['points']:
                   point['x'] += tX
                   point['y'] += tY
           if(type_ == 'TRIANGLE'):
               draw['point1']['x'] += tX
               draw['point2']['x'] += tX
               draw['point3']['x'] += tX
               draw['point1']['y'] += tY
               draw['point2']['y'] += tY
               draw['point3']['y'] += tY

    def scaleDraws(self,draws,scaleX,scaleY):
        for draw in draws:
            type_ = draw['type']
            if(type_ in 'RECT' or type_ in 'ELLPISE'):
                draw['position']['x'] *= scaleX
                draw['position']['y'] *= scaleY
                draw['size']['x'] *= scaleX
                draw['size']['y'] *= scaleY
            if(type_ == 'POLYGON'):
                for point in draw['points']:
                    point['x'] *= scaleX
                    point['y'] *= scaleY
            if(type_ in 'CIRCLE'):
               draw['position']['x'] *= scaleX
               draw['position']['y'] *= scaleY
               draw['radius'] *= max(scaleX,scaleY)
            if(type_ in 'SQUARE'):
               draw['position']['x'] *= scaleX
               draw['position']['y'] *= scaleY
               draw['width'] *= max(scaleX,scaleY)
            if(type_ == 'TRIANGLE'):
                draw['point1']['x'] *= scaleX
                draw['point2']['x'] *= scaleX
                draw['point3']['x'] *= scaleX
                draw['point1']['y'] *= scaleY
                draw['point2']['y'] *= scaleY
                draw['point3']['y'] *= scaleY

    def translateTo(self,obj,newX,newY):
        views = obj['views']

        for view in views:          
            type_ = view['type']
            hitbox_type = view['hitbox_type']
            if(type_ == 'VIEW_IMAGE'):
                view['position'] = {
                    'x' : newX,
                    'y' : newY
                }
            elif(type_ == 'VIEW_SKETCH'):
                draws = view['draws']
                
                minX, minY = self.getMinBB(draws)

                tX = newX - minX
                tY = newY - minY

                self.translateDraws(draws,tX,tY)
            
            if(hitbox_type == 'ADVANCED'):
                hitboxes = view['hitboxes']
                
                minX, minY = self.getMinBB(hitboxes)

                tX = newX - minX
                tY = newY - minY
                self.translateDraws(hitboxes,tX,tY)

    def scaleTo(self,obj,scaleX,scaleY):

        views = obj['views']

        if 'size' in obj:
            obj['size']['x'] *= scaleX
            obj['size']['y'] *= scaleY

        for view in views:         
            type_ = view['type']
            hitbox_type = view['hitbox_type']
            if(type_ == 'VIEW_IMAGE'):
                if 'size' in view:
                    view['size']['x'] *= scaleX
                    view['size']['y'] *= scaleY
            elif(type_ == 'VIEW_SKETCH'):
                draws = view['draws']
                
                newX, newY = self.getMinBB(draws)

                self.scaleDraws(draws,scaleX,scaleY)

                minX, minY = self.getMinBB(draws)

                tX = newX - minX
                tY = newY - minY

                self.translateDraws(draws,tX,tY)

            if(hitbox_type == 'ADVANCED'):
                hitboxes = view['hitboxes']
                
                newX, newY = self.getMinBB(hitboxes)

                self.scaleDraws(hitboxes,scaleX,scaleY)

                minX, minY = self.getMinBB(hitboxes)

                tX = newX - minX
                tY = newY - minY

                self.translateDraws(hitboxes,tX,tY)

    def verify_id_exist(self,id):
        if id in self.dict_vars:
            print(f"ERROR: Variável {id} já foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)
        else:
            return False

    def verify_arg(self, id, type):
        if id in self.restricted_vars:
            print(f"ERROR: Não pode utilizar o nome "+id+" para uma variável porque é um nome restrito.")

        if id in self.dict_vars:
            if self.dict_vars[id]['type'] == type:
                return True
            else:
                print(f"ERROR: Esperado uma variável do tipo {type}, mas a variável {id} é do tipo {self.dict_vars[id]['type']}.",file=sys.stderr)
                exit(-1)
        else:
            print(f"ERROR: Variável {id} não foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)
        
    def get_image_size(self,path_image):
        try:
            with Image.open(path_image) as img:
                largura, altura = img.size
                return {"x":largura, "y":altura}
        except IOError:
            print(f"ERROR: Não foi possível abrir a image em {path_image}.", file=sys.stderr)
            exit(-1)

    def verify_pos_and_size(self,objects,floor,ceil):
        if(len(objects) == 0):
            return objects
        aux_h = 0
        aux_w = round(self.WIDTH/len(objects),2)
        i = 1
        for object in objects:
            #verifica se o object not tem size
            if 'size' not in object: #se not temos de ver o size view a view
                for view in object['views']:
                    if view['type'] == 'VIEW_SKETCH':
                        continue
                    #verificar se o view ja tem size
                    if 'size' in view:
                        continue
                    else: #se not tiver temos deduzir o size
                        img = view['sources'][0]
                        if(img[0] == 'PATH'):
                            view['size'] = self.get_image_size(img[1])
                        elif(img[0] == 'URL'):
                            try:
                                headers = {
                                    "user-agent": "curl/7.84.0",
                                    "accept": "*/*"
                                }
                                response = requests.get(url=img[1], headers=headers)

                                # Verifica se o status da resposta é 200 (sucesso)
                                if response.status_code == 200:

                                    # Tenta abrir o conteúdo da resposta como uma imagem
                                    try:
                                        image = Image.open(BytesIO(response.content))
                                        size = image.size  # O tamanho da imagem no formato (largura, altura)
                                        view['size'] = {
                                            'x' : size[0],
                                            'y' : size[1]
                                        }

                                    except IOError:
                                        print("ERROR: O conteúdo não é uma imagem.")
                                else:
                                    print("ERROR: can't get the size, status code não é 200..")

                            except Exception as e:
                                print(f"ERROR: can't now the size.. Erro: {e}")
                                exit(-1)
                        elif(img[0] == 'LIB'):
                            try:
                                headers = {
                                    "user-agent": "curl/7.84.0",
                                    "accept": "*/*"
                                }
                                response = requests.get(url=f"https://surumkata.github.io/weberpl/assets/{img[1]}.png", headers=headers)
                                # Verifica se o status da resposta é 200 (sucesso)
                                if response.status_code == 200:

                                    # Tenta abrir o conteúdo da resposta como uma imagem
                                    try:
                                        image = Image.open(BytesIO(response.content))
                                        size = image.size  # O tamanho da imagem no formato (largura, altura)
                                        view[size] = size  # Aqui você pode armazenar o tamanho da imagem como preferir

                                    except IOError:
                                        print("ERROR: O conteúdo não é uma imagem.")
                                else:
                                    print("ERROR: can't get the size, status code não é 200..")
                            except Exception as e:
                                print(f"ERROR: can't now the size.. Erro: {e}")
                                exit(-1)
                        else:
                            #TODO: melhor erro
                            print(f"ERROR: can't now the size..")
                            exit(-1)
            else:
                for view in object['views']:
                    if 'size' not in view:
                        view['size'] = copy.deepcopy(object['size'])
                del object['size']
            #now verify the position
            if 'position' not in object:
                if 'size' in object:
                    size_w = object['size']["x"]
                    size_h = object['size']["y"]
                    w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                    h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                    for view in object['views']:
                        if view['type'] == 'VIEW_SKETCH':
                            continue
                        if 'position' not in view:
                            view['position'] = {"x": w, "y": h} 
                else: #temos de ver a posiçao view a view
                    for view in object['views']:
                        if view['type'] == 'VIEW_SKETCH':
                            continue
                        if 'position' not in view:
                            size_w = view['size']["x"]
                            size_h = view['size']["y"]
                            w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                            h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                            view['position'] = {"x": w, "y": h}
            else:
                for view in object['views']:
                    if view['type'] == 'VIEW_SKETCH':
                            continue
                    if 'position' not in view:
                        view['position'] = copy.deepcopy(object['position'])
                del object['position']
            if 'position_reference' in object:
                for view in object['views']:
                    if view['type'] == 'VIEW_SKETCH':
                            continue
                    if object['position_reference'] == 'floor':
                        view['position']["y"] = floor - view['size']["y"]
                    elif object['position_reference'] == 'ceil':
                        view['position']["y"] = ceil    
            i+=1
        return objects

    def decode_python_type(self,python_type,value):
        if python_type == str:
            return 'Text'
        elif python_type == tuple and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            return 'Point'
        elif python_type == list and all(isinstance(element, str) for element in value):
            return 'Text_List'
        elif python_type == int:
            return 'Integer'
        elif python_type == float:
            return 'Number'
        #TODO: Object/Sound/View/Challenge/Transition/Scenario/Event/Draw/Hitbox/Variable
        elif python_type == Object:
            return 'Object'
        elif python_type == Scenario:
            return 'Scenario'
        elif python_type == Event:
            return 'Event'
        return python_type

    def start(self,start):
        '''start : er imports? decls? python_block?'''
        children = start.children

        #percorrer python_block se houver
        if (children[len(children)-1].data == 'python_block'):
            self.visit(children[len(children)-1])

        i=1
        
        #percorrer imports
        if (len(children) > i and children[i].data == 'imports'):
            self.visit(children[i])
            i+=1

        #percorrer declarações
        if (len(children) > i and children[i].data == 'decls'):
            self.visit(children[i])
            i+=1


        return self.visit(children[0])

    def er(self,er):
        '''er : "EscapeRoom(" er_parameters ")"'''
        child = er.children[0]
        return self.visit(child)

    def er_parameters(self,er_parameters):
        '''er_parameters : param_title "," param_scenarios "," param_events "," param_transitions ("," param_variables)? "," param_start'''
        children = er_parameters.children
        escape_room = {}
        for child in children:
            param,param_value = self.visit(child)
            escape_room[param] = param_value

        escape_room["start_type"] = escape_room["start"]["source"]
        escape_room["start"] = escape_room["start"]["id"]

        for scenario in escape_room['scenarios']:
            floor = scenario['floor'] if 'floor' in scenario else self.FLOOR
            ceil = scenario['ceil'] if 'ceil' in scenario else self.CEIL
            if 'objects' in scenario:
                scenario['objects'] = self.verify_pos_and_size(objects=scenario['objects'],floor=floor,ceil=ceil)

        for scale in self.buffer_scale:
            obj_id = scale['object']
            sX = scale['sx']
            sY = scale['sy']
            for scenario in escape_room['scenarios']:
                if 'objects' in scenario:
                    for object in scenario['objects']:
                        if(object['id'] == obj_id):
                            self.scaleTo(object,sX,sY)

        for translate in self.buffer_translate:
            obj_id = translate['object']
            tX = translate['tx']
            tY = translate['ty']
            for scenario in escape_room['scenarios']:
                if 'objects' in scenario:
                    for object in scenario['objects']:
                        if(object['id'] == obj_id):
                            self.translateTo(object,tX,tY)

        return escape_room


    def imports(self,imps):
        '''imports : import_obj+'''
        children = imps.children
        for child in children:
            self.visit(child)

    def import_obj(self,import_obj):
        '''import_obj : "import Object." ID'''
        children = import_obj.children
        id = children[0].value
        obj = parse_obj(id)
        self.dict_imports['objects'][id] = obj

        for view in obj['views']:
            view_id = view['id']
            if not self.verify_id_exist(view_id):
                self.dict_vars[view_id] = {
                    "type" : "View",
                    "value" : view
            }
            
        if 'sounds' in obj:
            for sound in obj['sounds']:
                sound_id = sound['id']
                if not self.verify_id_exist(sound_id):
                    self.dict_vars[sound_id] = {
                        "type" : "Sound",
                        "value" : sound
                    }

    def decls(self,vars):
        '''decls : (var|decl)+'''
        children = vars.children
        for child in children:
            self.visit(child)

    def add_view(self,add_view):
        '''add_view : ID         ".add_View" "(" view ")"'''
        children = add_view.children
        id = children[0].value

        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Object' or type == 'Scenario':
                view = self.visit(children[1])
                self.dict_vars[id]['value']['views'].append(view)
            else:
                print(f"ERROR: Não é possível addr um 'View' a uma variável do tipo {type}, apenas a variáveis do tipo 'Object' e 'Scenario'.",file=sys.stderr)
                exit(-1)
        else:
            print(f'ERROR: A variável {id} not foi inicializada.',file=sys.stderr)
            exit(-1)

    def add_sound(self,add_sound):
        '''add_sound    : ID         ".add_Sound"    "(" sound    ")"'''
        children = add_sound.children
        id = children[0].value

        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Object' or type == 'Scenario':
                sound = self.visit(children[1])
                if 'sounds' in self.dict_vars[id]['value']:
                    self.dict_vars[id]['value']['sounds'].append(sound)
                else:
                    self.dict_vars[id]['value']['sounds'] = [sound]
            else:
                print(f"ERROR: Não é possível addr um 'Sound' a uma variável do tipo {type}, apenas a variáveis do tipo 'Object' e 'Scenario'.",file=sys.stderr)
                exit(-1)
        else:
            print(f'ERROR: A variável {id} not foi inicializada.',file=sys.stderr)
            exit(-1)


    def add_object(self,add_object):
        '''add_object : scenario_id ".add_Object" "(" object ")"'''
        children = add_object.children
        id = self.visit(children[0])
        object = self.visit(children[1])
        self.dict_vars[id]['value']['objects'].append(object)

    def translate_obj(self,translate_obj):
        '''translate_obj  : object_id ".translateTo" "(" number "," number ")"'''
        children = translate_obj.children
        obj_id = self.visit(children[0])
        tx = self.visit(children[1])
        ty = self.visit(children[2])

        self.buffer_translate.append({
            'object' : obj_id,
            'tx' : tx,
            'ty' : ty
        })

    def scale_obj(self,scale_obj):
        '''scale_obj  : object_id ".scaleTo" "(" number ("," number)? ")"'''
        children = scale_obj.children
        obj_id = self.visit(children[0])
        sx = self.visit(children[1])
        sy = self.visit(children[2]) if len(children) == 3 else sx
        self.buffer_scale.append({
            'object' : obj_id,
            'sx' : sx,
            'sy' : sy
        })
        

    def var(self,var):
        '''var : ID "=" value'''
        children = var.children
        var_name = children[0].value
        test = self.visit(children[1])

        (type,value) = test

        #Colocar id not for tipo primário:
        if type in ["View", "Sound", "Object", "Scenario", "Transition", 'Challenge', "Event","Draw","Hitbox","Variable"]:
            value["id"] = var_name

        if not self.verify_id_exist(var_name):
            self.dict_vars[var_name] = {
                'type' : type,
                'value' : value
            }

    def value(self,val):
        '''value : ID|comand_arg|python_call|list_text_constructor|text_constructor|size_constructor|position_constructor|number_constructor|view_constructor|object_constructor|object_imported|sound_constructor|scenario_constructor|event_constructor|challenge_constructor|transition_constructor'''
        child = val.children[0]
        #TODO: ver se é ID
        if isinstance(child, Token):
            id = child.value
            if id in self.dict_vars:
                type = self.dict_vars[id]['type']
                if type in ["View", "Sound", "Object", "Scenario", "Transition", 'Challenge', "Event", "Draw", "Hitbox", "Object_Text"]:
                    value = copy.deepcopy(self.dict_vars[id]['value'])
                else:
                    value = self.dict_vars[id]['value']
                return (type,value)
            else:
                print(f'ERROR: A variável {id} not foi inicializada.',file=sys.stderr)
                exit(-1)
        else:
            return self.visit(child)

    def comand_arg(self,comand_arg):
        child = int(comand_arg.children[0][1:])
        value = self.args[child] if child < len(self.args) else None
        if value == None:
            print(f'ERROR: O parametro ${child} não foi passado.',file=sys.stderr)
            exit(-1)
        return value

    def python_call(self,python_call):
        '''python_call : python_local|python_function'''
        children = python_call.children
        (type,value) = self.visit(children[0])

        if type in ['Object','Scenario','Event']:
            value = value.serialize()

        return (type,value)

    def python_local(self,python_local):
        '''python_local : "Python.Local." ID'''
        child = python_local.children[0]
        id = child.value
        value = self.locals_python[id]
        return (self.decode_python_type(type(value),value),value) #(python_type,python_value)

    def python_function(self,python_function):
        '''python_function : "Python.Function." FUNC'''
        child = python_function.children[0]
        func = child.value
        value = eval(func,self.namespace)
        return (self.decode_python_type(type(value),value),value) #(python_type,python_value)

    def list_text(self,list_text):
        '''list_text : list_text_arg|list_text_constructor|list_text_python_call'''
        child = list_text.children[0]
        if child.data == 'list_text_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def list_text_arg(self,list_text_arg):
        '''list_text_arg : ID'''
        child = list_text_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Text_List'):
            return self.dict_vars[id]['value'] 

    def list_text_python_call(self,list_text_python_call):
        '''list_text_python_call : python_call'''
        child = list_text_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Text_List':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Lista_Texto, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def list_text_constructor(self,list_text_constructor):
        '''list_text_constructor : "[" text ("," text)* "]"'''
        children = list_text_constructor.children
        list = []
        for child in children:
            list.append(self.visit(child))
        return ("Lista_Texto",list)

    def text(self,text):
        '''text : text_arg|text_constructor|text_python_call|text_comand_arg'''
        child = text.children[0]
        if child.data == 'text_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value
    
    def text_comand_arg(self,text_comand_arg):
        '''text_comand_arg : command_arg'''
        child = text_comand_arg.children[0]
        return self.visit(child)

    def text_arg(self,text_arg):
        '''text_arg : ID'''
        child = text_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Text'):
            return self.dict_vars[id]['value'] 

    def text_python_call(self,text_python_call):
        '''text_python_call : python_call'''
        child = text_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Text':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Texto, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def text_constructor(self,text_constructor):
        '''text_constructor : TEXTO'''
        children = text_constructor.children
        text = children[0].value[1:-1]
        return ('Text',text) #(type,value)


    def format_text(self,format_text):
        '''format_text : format_text_arg|format_text_constructor|format_text_python_call'''
        child = format_text.children[0]
        if child.data == 'format_text_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        # Expressão regular para capturar conteúdo dentro de chaves {}
        pattern = r'{(.*?)}'

        # Encontrar todas as correspondências
        variables = re.findall(pattern, value)
        for variable in variables:
            #Verificar que elas existem e são do tipo Variables
            if variable in self.restricted_vars:
                continue
            self.verify_arg(variable,'Variable')

        return value

    def format_text_arg(self,format_text_arg):
        '''format_text_arg : ID'''
        child = format_text_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Format_Text'):
            return self.dict_vars[id]['value'] 

    def format_text_python_call(self,format_text_python_call):
        '''format_text_python_call : python_call'''
        child = format_text_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Format_Text':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Format_Texto, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def format_text_constructor(self,format_text_constructor):
        '''format_text_constructor : "f" TEXTO'''
        children = format_text_constructor.children
        text = children[0].value[1:-1]
        return ('Format_Text',text) #(type,value)

    def point(self,position):
        '''position : point_arg|point_constructor|point_python_call'''
        child = position.children[0]
        if child.data == 'point_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def point_arg(self,position_arg):
        '''point_arg : ID'''
        child = position_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Point'):
            return self.dict_vars[id]['value'] 

    def point_python_call(self,position_python_call):
        '''point_python_call : python_call'''
        child = position_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Point':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Point, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def point_constructor(self,position_constructor):
        '''point_constructor : "(" number "," number ")"'''
        children = position_constructor.children
        x = self.visit(children[0])
        y = self.visit(children[1])
        return ('Point',{"x" : x,"y" : y})

    def number(self,number):
        '''number : number_arg|number_constructor|number_python_call'''
        child = number.children[0]
        if child.data == 'number_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def number_arg(self,number_arg):
        '''number_arg : ID'''
        child = number_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Number'):
            return self.dict_vars[id]['value'] 

    def number_python_call(self,number_python_call):
        '''number_python_call : python_call'''
        child = number_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Number':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Número do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def number_constructor(self,number_constructor):
        '''number_constructor : NUM'''
        children = number_constructor.children
        num = float(children[0].value)
        return('Number',num) #(type,value)
    
    def integer(self,integer):
        '''integer : integer_arg|integer_constructor|integer_python_call'''
        child = integer.children[0]
        if child.data == 'integer_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def integer_arg(self,integer_arg):
        '''integer_arg : ID'''
        child = integer_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Integer'):
            return self.dict_vars[id]['value'] 

    def integer_python_call(self,integer_python_call):
        '''integer_python_call : python_call'''
        child = integer_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Integer':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Número do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def integer_constructor(self,integer_constructor):
        '''integer_constructor : INT'''
        children = integer_constructor.children
        num = int(children[0].value)
        return('Integer',num) #(type,value) 
    
    def color(self,color):
        '''color : color_arg|color_constructor|color_constructor_rgb|color_constructor_hsb|color_python_call'''
        child = color.children[0]
        if child.data == 'color_constructor' or child.data == 'color_constructor_rgb' or child.data == 'color_constructor_hsb':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def color_arg(self,color_arg):
        '''color_arg : ID'''
        child = color_arg.children[0]
        if self.verify_arg(id,'Color'):
            return self.dict_vars[id]['value'] 
    
    def color_python_call(self,color_python_call):
        '''color_python_call     : python_call'''
        child = color_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Color':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Número do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)
    
    def color_constructor(self,color_constructor):
        '''color_constructor     : "#" HEXCODE'''
        hexcode = color_constructor.children[0].value
        if len(hexcode) == 3:
            hexcode = ''.join([c*2 for c in hexcode])
        return('Color',"#"+hexcode) #(type,value)

    def color_constructor_rgb(self,color_constructor_rgb):
        '''color_constructor_rgb : "rgb" "(" integer "," integer "," integer ")"'''
        children = color_constructor_rgb.children
        r = self.visit(children[0])
        if(r < 0 or r > 255):
            print(f"ERROR: Esperado um valor de vermelho entre 0 e 255 e recebido o valor: {r}.")
            exit(-1)
        g = self.visit(children[1])
        if(g < 0 or g > 255):
            print(f"ERROR: Esperado um valor de verde entre 0 e 255 e recebido o valor: {g}.")
            exit(-1)
        b = self.visit(children[2])
        if(b < 0 or b > 255):
            print(f"ERROR: Esperado um valor de azul entre 0 e 255 e recebido o valor: {b}.")
            exit(-1)

        return('Color',f"#{r:02x}{g:02x}{b:02x}")
    
    def color_constructor_hsb(self,color_constructor_hsb):
        '''color_constructor_hsb : "hsb" "(" integer "," integer "," integer ")"'''
        children = color_constructor_hsb.children
        h = self.visit(children[0])
        if(h < 0 or h > 360):
            print(f"ERROR: Esperado um valor de hue entre 0 e 360 e recebido o valor: {h}.")
            exit(-1)
        s = self.visit(children[1])
        if(s < 0 or s > 100):
            print(f"ERROR: Esperado um valor de saturação entre 0 e 100 e recebido o valor: {s}.")
            exit(-1)
        b = self.visit(children[2])
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

        return('Color',f"#{r:02x}{g:02x}{b:02x}")


    def views(self,views):
        '''views : "[" view ("," view)* "]"'''
        children = views.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def view(self,view):
        '''view : view_arg|view_constructor_id|view_python_call'''
        child = view.children[0]
        value = self.visit(child)
        return value

    def view_arg(self,view_arg):
        '''view_arg : ID'''
        child = view_arg.children[0]
        id = child.value
        if self.verify_arg(id,'View'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def view_id(self,view_id):
        '''view_id : ID'''
        child = view_id.children[0]
        id = child.value
        #TODO: ver isto melhor do none depois
        if id == "none":
            return id
        if self.verify_arg(id,'View'):
            return id

    def view_python_call(self,view_python_call):
        '''view_python_call : python_call'''
        child = view_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'View':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do View do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def view_constructor(self,view_constructor):
        '''view_constructor : view_static|view_animated'''
        child = view_constructor.children[0]
        return self.visit(child)
    
    def view_constructor_id(self,view_constructor):
        '''view_constructor_id : view_static_id|view_animated_id'''
        child = view_constructor.children[0]
        return self.visit(child)

    def view_static(self,view_static):
        '''view_static : "View.Estático" "(" param_image ("," param_position)? ("," param_size)? ")"'''
        children = view_static.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'VIEW_IMAGE'
        if 'hitboxes' in value:
            if len(value['hitboxes']) > 0:
                value['hitbox_type'] = 'ADVANCED'
            else:
                value['hitbox_type'] = 'NO' 
        else:
            value['hitbox_type'] = 'DEFAULT'
    
        return ('View',value)

    def view_animated(self,view_animated):
        '''view_animated : "View.Dinâmico" "(" param_images "," param_repetitions "," param_time_sprite ("," param_position)? ("," param_size)? ")"'''
        children = view_animated.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'VIEW_IMAGE'
        if 'hitboxes' in value:
            if len(value['hitboxes']) > 0:
                value['hitbox_type'] = 'ADVANCED'
            else:
                value['hitbox_type'] = 'NO' 
        else:
            value['hitbox_type'] = 'DEFAULT'
        
        return ('View',value)
    
    def view_sketch(self,view_sketch):
        '''view_sketch : "View.Sketch" "(" param_draws ")"'''
        children = view_sketch.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'VIEW_SKETCH'
        if 'hitboxes' in value:
            if len(value['hitboxes']) > 0:
                value['hitbox_type'] = 'ADVANCED'
            else:
                value['hitbox_type'] = 'NO' 
        else:
            value['hitbox_type'] = 'DEFAULT'
        
        return ('View',value)
    
    def view_static_id(self,view_static_id):
        '''view_static_id : "View.Estático." ID "(" param_image ("," param_position)? ("," param_size)? ")"'''
        children = view_static_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'VIEW_IMAGE'
        if 'hitboxes' in value:
            if len(value['hitboxes']) > 0:
                value['hitbox_type'] = 'ADVANCED'
            else:
                value['hitbox_type'] = 'NO' 
        else:
            value['hitbox_type'] = 'DEFAULT'

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                "type" : 'View',
                "value" : value
            }

        return value

    def view_animated_id(self,view_animated_id):
        '''view_animated_id : "View.Dinâmico." ID "(" param_images "," param_repetitions "," param_time_sprite ("," param_position)? ("," param_size)? ")"'''
        children = view_animated_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'VIEW_IMAGE'
        if 'hitboxes' in value:
            if len(value['hitboxes']) > 0:
                value['hitbox_type'] = 'ADVANCED'
            else:
                value['hitbox_type'] = 'NO' 
        else:
            value['hitbox_type'] = 'DEFAULT'

        self.dict_vars[id] = {
            "type" : 'View',
            "value" : value
        }

        return value
    
    def view_sketch_id(self,view_sketch_id):
        '''view_sketch_id : "View.Sketch." ID "(" param_draws ("," param_hitboxes)? ")"'''
        children = view_sketch_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'VIEW_SKETCH'

        if 'hitboxes' in value:
            if len(value['hitboxes']) > 0:
                value['hitbox_type'] = 'ADVANCED'
            else:
                value['hitbox_type'] = 'NO' 
        else:
            value['hitbox_type'] = 'DEFAULT'

        self.dict_vars[id] = {
            "type" : 'View',
            "value" : value
        }

        return value
    
    def draws(self,draws):
        '''draws : "[" draw ("," draw)* "]"'''
        children = draws.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def draw(self,draw):
        '''draw : draw_arg|draw_constructor_id|draw_python_call'''
        child = draw.children[0]
        value = self.visit(child)
        return value

    def draw_arg(self,draw_arg):
        '''draw_arg : ID'''
        child = draw_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Draw'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def draw_id(self,draw_id):
        '''draw_id : ID'''
        child = draw_id.children[0]
        id = child.value
        #TODO: ver isto melhor do none depois
        if id == "none":
            return id
        if self.verify_arg(id,'Draw'):
            return id

    def draw_python_call(self,draw_python_call):
        '''draw_python_call : python_call'''
        child = draw_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Draw':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do View do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def draw_constructor(self,draw_constructor):
        '''draw_constructor : draw_rect | draw_polygon | draw_square | draw_circle | draw_line | draw_ellipse | draw_arc | draw_triangle | draw_fill'''
        child = draw_constructor.children[0]
        return self.visit(child)
    
    def draw_constructor_id(self,draw_constructor_id):
        '''draw_constructor_id : draw_rect_id | draw_polygon_id | draw_square_id | draw_circle_id | draw_line_id | draw_ellipse_id | draw_arc_id | draw_triangle_id | draw_fill_id'''
        child = draw_constructor_id.children[0]
        return self.visit(child)
    
    def draw_rect(self,draw_rect):
        '''draw_rect : "Draw.Rect"         "(" param_position "," param_size "," param_tl "," param_tr "," param_bl "," param_br  ")""'''
        children = draw_rect.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'RECT'
    
        return ('Draw',value)
    
    def draw_polygon(self,draw_polygon):
        '''draw_polygon : "Draw.Polygon" "(" param_points ")"'''
        children = draw_polygon.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'POLYGON'
    
        return ('Draw',value)
    
    def draw_triangle(self,draw_triangle):
        '''draw_triangle         : "Draw.Triangle"     "(" param_point1   "," param_point2 "," param_point3                                   ")"'''
        children = draw_triangle.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'TRIANGLE'
    
        return ('Draw',value)

    def draw_line(self,draw_line):
        '''draw_line             : "Draw.Line"         "(" param_point1   "," param_point2                                                    ")"'''
        children = draw_line.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'LINE'
    
        return ('Draw',value)

    def draw_ellipse(self,draw_ellipse):
        '''draw_ellipse          : "Draw.Ellipse"      "(" param_position "," param_size                                                      ")"'''
        children = draw_ellipse.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ELLIPSE'
    
        return ('Draw',value)

    def draw_arc(self,draw_arc):
        '''draw_arc              : "Draw.Arc"          "(" param_position "," param_size "," param_arcstart "," param_arcstop                 ")"'''
        children = draw_arc.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ARC'
    
        return ('Draw',value)

    def draw_circle(self,draw_circle):
        '''draw_circle           : "Draw.Circle"       "(" param_position "," param_radius                                                    ")"'''
        children = draw_circle.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'CIRCLE'
    
        return ('Draw',value)

    def draw_square(self,draw_square):
        '''draw_square : "Draw.Square" "(" param_position "," param_width "," param_tl "," param_tr "," param_bl "," param_br ")"'''
        children = draw_square.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'SQUARE'
    
        return ('Draw',value)

    def draw_fill(self,draw_fill):
        '''draw_fill : "Draw.Fill" "(" param_color ("," param_opacity)? ")"'''
        children = draw_fill.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'FILL'
    
        return ('Draw',value)
    
    def draw_rect_id(self,draw_rect_id):
        '''draw_rect_id : "Draw.Rect." ID     "(" param_position "," param_size "," param_tl "," param_tr "," param_bl "," param_br  ")"'''
        children = draw_rect_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'RECT'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value
    
    def draw_polygon_id(self,draw_polygon_id):
        '''draw_polygon : "Draw.Polygon." ID "(" param_points ")"'''
        children = draw_polygon_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'POLYGON'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_triangle_id(self,draw_triangle_id):
        '''draw_triangle_id      : "Draw.Triangle." ID "(" param_point1   "," param_point2 "," param_point3                                   ")"'''
        children = draw_triangle_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'TRIANGLE'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_line_id(self,draw_line_id):
        '''draw_line_id          : "Draw.Line." ID     "(" param_point1   "," param_point2                                                    ")"'''
        children = draw_line_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'LINE'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_ellipse_id(self,draw_ellipse_id):
        '''draw_ellipse_id       : "Draw.Ellipse." ID  "(" param_position "," param_size                                                      ")"'''
        children = draw_ellipse_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ELLIPSE'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_arc_id(self,draw_arc_id):
        '''draw_arc_id           : "Draw.Arc." ID      "(" param_position "," param_size "," param_arcstart "," param_arcstop                 ")"'''
        children = draw_arc_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ARC'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_circle_id(self,draw_circle_id):
        '''draw_circle_id        : "Draw.Circle." ID   "(" param_position "," param_radius                                                    ")"'''
        children = draw_circle_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'CIRCLE'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_square_id(self,draw_square_id):
        '''draw_square_id        : "Draw.Square." ID   "(" param_position "," param_width "," param_tl "," param_tr "," param_bl "," param_br ")"'''
        children = draw_square_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'SQUARE'

        self.dict_vars[id] = {
            "type" : 'Draw',
            "value" : value
        }

        return value

    def draw_fill_id(self,draw_fill):
        '''draw_fill : "Draw.Fill" "(" param_color ("," param_opacity)? ")"'''
        children = draw_fill.children
        value = {}
        value["id"] = "FILL" + str(self.aux)
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'FILL'

        self.dict_vars["FILL" + str(self.aux)] = {
            "type" : 'Draw',
            "value" : value
        }

        self.aux+=1

        return value
    
    def hitboxes(self,hitboxes):
        '''hitboxes : "[" hitbox ("," hitbox)* "]"'''
        children = hitboxes.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def hitbox(self,hitbox):
        '''hitbox : hitbox_arg|hitbox_constructor_id|hitbox_python_call'''
        child = hitbox.children[0]
        value = self.visit(child)
        return value

    def hitbox_arg(self,hitbox_arg):
        '''hitbox_arg : ID'''
        child = hitbox_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Hitbox'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def hitbox_id(self,hitbox_id):
        '''hitbox_id : ID'''
        child = hitbox_id.children[0]
        id = child.value
        if self.verify_arg(id,'Hitbox'):
            return id

    def hitbox_python_call(self,hitbox_python_call):
        '''hitbox_python_call : python_call'''
        child = hitbox_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Hitbox':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do View do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def hitbox_constructor(self,hitbox_constructor):
        '''hitbox_constructor : hitbox_rect | hitbox_polygon | hitbox_square | hitbox_circle | hitbox_line | hitbox_ellipse | hitbox_arc | hitbox_triangle | hitbox_fill'''
        child = hitbox_constructor.children[0]
        return self.visit(child)
    
    def hitbox_constructor_id(self,hitbox_constructor_id):
        '''hitbox_constructor_id : hitbox_rect_id | hitbox_polygon_id | hitbox_square_id | hitbox_circle_id | hitbox_line_id | hitbox_ellipse_id | hitbox_arc_id | hitbox_triangle_id | hitbox_fill_id'''
        child = hitbox_constructor_id.children[0]
        return self.visit(child)
    
    def hitbox_rect(self,hitbox_rect):
        '''hitbox_rect : "Hitbox.Rect" "(" param_position "," param_size ")""'''
        children = hitbox_rect.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'RECT'
    
        return ('Hitbox',value)
    
    def hitbox_polygon(self,hitbox_polygon):
        '''hitbox_polygon : "Hitbox.Polygon" "(" param_points ")"'''
        children = hitbox_polygon.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'POLYGON'
    
        return ('Hitbox',value)
    
    def hitbox_triangle(self,hitbox_triangle):
        '''hitbox_triangle         : "Hitbox.Triangle"     "(" param_point1   "," param_point2 "," param_point3                                   ")"'''
        children = hitbox_triangle.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'TRIANGLE'
    
        return ('Hitbox',value)

    def hitbox_line(self,hitbox_line):
        '''hitbox_line             : "Hitbox.Line"         "(" param_point1   "," param_point2                                                    ")"'''
        children = hitbox_line.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'LINE'
    
        return ('Hitbox',value)

    def hitbox_ellipse(self,hitbox_ellipse):
        '''hitbox_ellipse          : "Hitbox.Ellipse"      "(" param_position "," param_size                                                      ")"'''
        children = hitbox_ellipse.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ELLIPSE'
    
        return ('Hitbox',value)

    def hitbox_arc(self,hitbox_arc):
        '''hitbox_arc              : "Hitbox.Arc"          "(" param_position "," param_size "," param_arcstart "," param_arcstop                 ")"'''
        children = hitbox_arc.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ARC'
    
        return ('Hitbox',value)

    def hitbox_circle(self,hitbox_circle):
        '''hitbox_circle           : "Hitbox.Circle"       "(" param_position "," param_radius                                                    ")"'''
        children = hitbox_circle.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'CIRCLE'
    
        return ('Hitbox',value)

    def hitbox_square(self,hitbox_square):
        '''hitbox_square : "Hitbox.Square" "(" param_position "," param_width ")"'''
        children = hitbox_square.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'SQUARE'
    
        return ('Hitbox',value)

    def hitbox_fill(self,hitbox_fill):
        '''hitbox_fill : "Hitbox.Fill" "(" param_color ("," param_opacity)? ")"'''
        children = hitbox_fill.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'FILL'
    
        return ('Hitbox',value)
    
    def hitbox_rect_id(self,hitbox_rect_id):
        '''hitbox_rect_id : "Hitbox.Rect." ID     "(" param_position "," param_size ")"'''
        children = hitbox_rect_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'RECT'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value
    
    def hitbox_polygon_id(self,hitbox_polygon_id):
        '''hitbox_polygon : "Hitbox.Polygon." ID "(" param_points ")"'''
        children = hitbox_polygon_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'POLYGON'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_triangle_id(self,hitbox_triangle_id):
        '''hitbox_triangle_id      : "Hitbox.Triangle." ID "(" param_point1   "," param_point2 "," param_point3                                   ")"'''
        children = hitbox_triangle_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'TRIANGLE'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_line_id(self,hitbox_line_id):
        '''hitbox_line_id          : "Hitbox.Line." ID     "(" param_point1   "," param_point2                                                    ")"'''
        children = hitbox_line_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'LINE'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_ellipse_id(self,hitbox_ellipse_id):
        '''hitbox_ellipse_id       : "Hitbox.Ellipse." ID  "(" param_position "," param_size                                                      ")"'''
        children = hitbox_ellipse_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ELLIPSE'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_arc_id(self,hitbox_arc_id):
        '''hitbox_arc_id           : "Hitbox.Arc." ID      "(" param_position "," param_size "," param_arcstart "," param_arcstop                 ")"'''
        children = hitbox_arc_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'ARC'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_circle_id(self,hitbox_circle_id):
        '''hitbox_circle_id        : "Hitbox.Circle." ID   "(" param_position "," param_radius                                                    ")"'''
        children = hitbox_circle_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'CIRCLE'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_square_id(self,hitbox_square_id):
        '''hitbox_square_id        : "Hitbox.Square." ID   "(" param_position "," param_width ")"'''
        children = hitbox_square_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'SQUARE'

        self.dict_vars[id] = {
            "type" : 'Hitbox',
            "value" : value
        }

        return value

    def hitbox_fill_id(self,hitbox_fill):
        '''hitbox_fill : "Hitbox.Fill" "(" param_color ("," param_opacity)? ")"'''
        children = hitbox_fill.children
        value = {}
        value["id"] = "FILL" + str(self.aux)
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        value['type'] = 'FILL'

        self.dict_vars["FILL" + str(self.aux)] = {
            "type" : 'Hitbox',
            "value" : value
        }

        self.aux+=1

        return value

    def variables(self,variables):
        '''variables : "[" variable ("," variable)* "]"'''
        children = variables.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def variable(self,variable):
        '''variable : variable_arg|variable_constructor_id|variable_python_call'''
        child = variable.children[0]
        value = self.visit(child)
        return value
    
    def variable_arg(self,variable_arg):
        '''variable_arg : ID'''
        child = variable_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Variable'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def variable_id(self,variable_id):
        '''variable_id : ID'''
        child = variable_id.children[0]
        id = child.value
        if self.verify_arg(id,'Variable'):
            return id

    def variable_python_call(self,variable_python_call):
        '''variable_python_call : python_call'''
        child = variable_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Variable':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do tipo Variable, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def variable_constructor(self,object_constructor):
        '''variable_constructor : "Variable" "(" param_number ")"'''
        children = object_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value

        return ('Variable',value)

    def variable_constructor_id(self,variable_constructor_id):
        '''variable_constructor_id : "Variable." ID "(" param_number ")"'''
        children = variable_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                "type" : 'Variable',
                "value" : value
            }

        return value

    def sounds(self,sounds):
        '''sounds : "[" sound ("," sound)* "]"'''
        children = sounds.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def sound(self,sound):
        '''sound : sound_arg|sound_constructor_id|sound_python_call'''
        child = sound.children[0]
        value = self.visit(child)
        return value

    def sound_arg(self,sound_arg):
        '''sound_arg : ID'''
        child = sound_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Sound'):
            return copy.deepcopy(self.dict_vars[id]['value']) 

    def sound_id(self,sound_id):
        '''sound_id : ID'''
        child = sound_id.children[0]
        id = child.value
        if self.verify_arg(id,'Sound'):
            return id
        

    def sound_python_call(self,sound_python_call):
        '''sound_python_call : python_call'''
        child = sound_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Sound':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Sound do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def sound_constructor(self,sound_constructor):
        '''sound_constructor : "Sound" "(" param_source ("," param_loop)? ")"'''
        children = sound_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value

        if 'loop' not in value:
            value['loop'] = False

        return ('Sound',value) #(type,value)
    
    def sound_constructor_id(self,sound_constructor_id):
        '''sound_constructor_id : "Sound." ID "(" param_source ("," param_loop)? ")"'''
        children = sound_constructor_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        
        value = {}
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        if 'loop' not in value:
            value['loop'] = False

        return value


    def objects(self,objects):
        '''objects : "[" object ("," object)* "]"'''
        children = objects.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def object(self,object):
        '''object : object_imported_id|object_arg|object_constructor_id|object_python_call'''
        child = object.children[0]
        value = self.visit(child)
        return value

    def object_arg(self,object_arg):
        '''object_arg : ID'''
        child = object_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Object'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def object_id(self,object_id):
        '''object_id : ID'''
        child = object_id.children[0]
        id = child.value
        if self.verify_arg(id,'Object'):
            return id

    def object_python_call(self,object_python_call):
        '''object_python_call : python_call'''
        child = object_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Object':
            value = value.serialize()
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Object do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def object_constructor(self,object_constructor):
        '''object_constructor : "Object" "(" (param_view_inicial ",")? param_views ("," param_position)? ("," param_size)? ("," param_sounds)? ")"'''
        children = object_constructor.children
        value = {}
        have_initial_view = False
        for child in children:
            if(child.data == "param_view_inicial"):
                have_initial_view = True
                continue
            param,param_value = self.visit(child)
            value[param] = param_value
        if have_initial_view:
            param,param_value = self.visit(children[0])
            value[param] = param_value
        return ('Object',value)

    def object_imported(self,object_imported):
        '''object_imported : "Object." ID ("(" (param_position|param_size|(param_position "," param_size)) ")")?'''
        children = object_imported.children
        id = children[0].value
        if id in self.dict_imports['objects']:
            object = copy.deepcopy(self.dict_imports['objects'][id])
            other_children = children[1:]
            for child in other_children:
                param,param_value = self.visit(child)
                object[param] = param_value

            return ('Object',object)
        else:
           print(f"ERROR: Object {id} not importdo anteriormente.",file=sys. stderr) 

    def object_constructor_id(self,object_constructor_id):
        '''object_constructor_id : "Object." ID "(" (param_view_inicial ",")? param_views ("," param_position)? ("," param_size)? ("," param_sounds)? ")"'''
        children = object_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        have_initial_view = False
        for child in children[1:]:
            if(child.data == "param_view_inicial"):
                have_initial_view = True
                continue
            param,param_value = self.visit(child)
            value[param] = param_value
        if have_initial_view:
            param,param_value = self.visit(children[1])
            value[param] = param_value
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                "type" : 'Object',
                "value" : value
            }

        return value

    def object_imported_id(self,object_imported_id):
        '''object_imported_id : "Object." ID "." ID ("(" (param_position|param_size|(param_position "," param_size)) ")")?'''
        children = object_imported_id.children
        id_import = children[0].value
        id_value = children[1].value
        if id_import in self.dict_imports['objects']:
            object = copy.deepcopy(self.dict_imports['objects'][id_import])
            object["id"] = id_value
            other_children = children[2:]
            for child in other_children:
                param,param_value = self.visit(child)
                object[param] = param_value

            if not self.verify_id_exist(id):
                self.dict_vars[id] = {
                    "type" : 'Object',
                    "value" : object
                }

            return object
        else:
           print(f"ERROR: Object {id_import} not importdo anteriormente.",file=sys. stderr)
           exit(-1)

    def obj_texts(self,obj_texts):
        '''obj_texts : "[" obj_text ("," obj_text)* "]"'''
        children = obj_texts.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def obj_text(self,obj_text):
        '''obj_text : obj_text_arg|obj_text_constructor_id|obj_text_python_call'''
        child = obj_text.children[0]
        value = self.visit(child)
        return value

    def obj_text_arg(self,obj_text_arg):
        '''obj_text_arg : ID'''
        child = obj_text_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Object_Text'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def obj_text_id(self,obj_text_id):
        '''obj_text_id : ID'''
        child = obj_text_id.children[0]
        id = child.value
        if self.verify_arg(id,'Object_Text'):
            return id

    def obj_text_python_call(self,obj_text_python_call):
        '''obj_text_python_call : python_call'''
        child = obj_text_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Object_Text':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Object_Text do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def obj_text_constructor(self,obj_text_constructor):
        '''obj_text_constructor : "Text" "(" param_text ("," param_color)? "," param_position ("," param_width)? ")"'''
        children = obj_text_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        return ('Object_Text',value)
    
    def obj_text_constructor_id(self,obj_text_constructor_id):
        '''obj_text_constructor_id : "Text" "(" param_text ("," param_color)? "," param_position ("," param_width)? ")"'''
        children = obj_text_constructor_id.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                "type" : 'Object_Text',
                "value" : value
            }

        return value

    def scenarios(self,scenarios):
        '''scenarios : "[" scenario ("," scenario)* "]"'''
        children = scenarios.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def scenario(self,scenario):
        '''scenario : scenario_arg|scenario_constructor_id|scenario_python_call'''
        child = scenario.children[0]
        value = self.visit(child)
        return value

    def scenario_arg(self,scenario_arg):
        '''scenario_arg : ID'''
        child = scenario_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Scenario'):
            return copy.deepcopy(self.dict_vars[id]['value'] )

    def scenario_id(self,scenario_id):
        '''scenario_id : ID'''
        child = scenario_id.children[0]
        id = child.value
        if self.verify_arg(id,'Scenario'):
            return id
        

    def scenario_python_call(self,scenario_python_call):
        '''scenario_python_call : python_call'''
        child = scenario_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Scenario':
            value = value.serialize()
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Scenario do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def scenario_constructor(self,scenario_constructor):
        '''scenario_constructor : "Scenario" "(" param_view_inicial "," param_views "," param_objects ("," param_sounds)? ("," param_ceil)? ("," param_floor)? ")"'''
        children = scenario_constructor.children
        value = {}
        have_initial_view = False
        for child in children:
            if(child.data == "param_view_inicial"):
                have_initial_view = True
                continue
            param,param_value = self.visit(child)
            value[param] = param_value
        if have_initial_view:
            param,param_value = self.visit(children[0])
            value[param] = param_value

        if 'floor' not in value:
            value['floor'] = self.FLOOR
        if 'ceil' not in value:
            value['ceil'] = self.CEIL

        return ('Scenario',value)
    
    def scenario_constructor_id(self,scenario_constructor_id):
        '''scenario_constructor_id : "Scenario." ID "(" param_view_inicial "," param_views "," param_objects ("," param_sounds)? ("," param_ceil)? ("," param_floor)? ")"'''
        children = scenario_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        have_initial_view = False
        for child in children[1:]:
            if(child.data == "param_view_inicial"):
                have_initial_view = True
                continue
            param,param_value = self.visit(child)
            value[param] = param_value
        if have_initial_view:
            param,param_value = self.visit(children[1])
            value[param] = param_value
        
        if 'floor' not in value:
            value['floor'] = self.FLOOR
        if 'ceil' not in value:
            value['ceil'] = self.CEIL

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Scenario',
                    "value" : value
                }

        return value

    def transitions(self,transitions):
        '''transitions : "[" transition ("," transition)* "]"'''
        children = transitions.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def transition(self,transition):
        '''transition : transition_arg|transition_constructor_id|transition_python_call'''
        child = transition.children[0]
        value = self.visit(child)
        return value

    def transition_arg(self,transition_arg):
        '''transition_arg : ID'''
        child = transition_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Transition'):
            return copy.deepcopy(self.dict_vars[id]['value']) 

    def transition_id(self,transition_id):
        '''transition_id : ID'''
        child = transition_id.children[0]
        id = child.value
        if self.verify_arg(id,'Transition'):
            return id

    def transition_python_call(self,transition_python_call):
        '''transition_python_call : python_call'''
        child = transition_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Transition':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Transition do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def transition_constructor(self,transition_constructor):
        '''transition_constructor : "Transition" "(" param_background "," param_music "," param_story "," (param_next_scene|param_next_trans)")"'''
        children = transition_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value

        if "next_scenario" in value:
            value["next"] = value["next_scenario"]
            value["next_type"] = "SCENARIO"
            del value["next_scenario"]
        else:
            value["next"] = value["next_transition"]
            value["next_type"] = "TRANSITION"
            del value["next_transition"]
        
        return ('Transition',value)
    
    def transition_constructor_id(self,transition_constructor_id):
        '''transition_constructor_id : "Transition." ID "(" param_background "," param_music "," param_story "," (param_next_scene|param_next_trans)")"'''
        children = transition_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Transition',
                    "value" : value
                }
        
        return value

    def challenge(self,challenge):
        '''challenge : challenge_arg|challenge_constructor_id|challenge_python_call'''
        child = challenge.children[0]
        value = self.visit(child)
        return value

    def challenge_arg(self,challenge_arg):
        '''challenge_arg : ID'''
        child = challenge_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Challenge'):
            return copy.deepcopy(self.dict_vars[id]['value'])

    def challenge_python_call(self,challenge_python_call):
        '''challenge_python_call : python_call'''
        child = challenge_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Challenge':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Challenge do tipo Posição, mas é do tipo {type}.",file=sys. stderr)

    def challenge_constructor(self,challenge_constructor):
        '''challenge_constructor : challenge_question|challenge_motion|challenge_multiple_choice|challenge_connection|challenge_sequence|challenge_puzzle|challenge_slidepuzzle|challenge_socket'''
        child = challenge_constructor.children[0]
        return self.visit(child)
    
    def challenge_constructor_id(self,challenge_constructor_id):
        '''challenge_constructor_id : challenge_question_id|challenge_motion_id|challenge_multiple_choice_id|challenge_connection_id|challenge_sequence_id|challenge_puzzle_id|challenge_slidepuzzle_id|challenge_socket_id'''
        child = challenge_constructor_id.children[0]
        return self.visit(child)

    def challenge_question(self,challenge_question):
        '''challenge_question : "Challenge.Pergunta" "(" param_question "," param_answer "," param_acerto "," param_fail ")"'''
        children = challenge_question.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'QUESTION'

        return ('Challenge',value)
    
    def challenge_question_id(self,challenge_question_id):
        '''challenge_question_id : "Challenge.Pergunta." ID "(" param_question "," param_answer "," param_acerto "," param_fail ")"'''
        children = challenge_question_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "QUESTION"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }

        return value

    def challenge_motion(self,challenge_motion):
        '''challenge_motion : "Challenge.Motion" "(" param_motion_object "," param_trigger_object "," param_acerto "," param_fail ")"'''
        children = challenge_motion.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'MOTION_OBJECT'

        return ('Challenge',value)
    
    def challenge_motion_id(self,challenge_motion_id):
        '''challenge_motion_id : "Challenge.Motion." ID "(" param_motion_object "," param_trigger_object "," param_acerto "," param_fail ")"'''
        children = challenge_motion_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "MOTION_OBJECT"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def challenge_multiple_choice(self,challenge_multiple_choice):
        '''challenge_multiple_choice : "Challenge.Multiple_Choice" "(" param_question "," param_choices "," param_answer "," param_acerto "," param_fail ")"'''
        children = challenge_multiple_choice.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'MULTIPLE_CHOICE'

        return ('Challenge',value)
    
    def challenge_multiple_choice_id(self,challenge_multiple_choice_id):
        '''challenge_multiple_choice_id : "Challenge.Multiple_Choice." ID "(" param_question "," param_choices "," param_answer "," param_acerto "," param_fail ")"'''
        children = challenge_multiple_choice_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "MULTIPLE_CHOICE"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def challenge_connection(self,challenge_connection):
        '''challenge_connection : "Challenge.Connection" "(" param_question "," param_list1 "," param_list2 "," param_acerto "," param_fail ")"'''
        children = challenge_connection.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'CONNECTIONS'

        return ('Challenge',value)
    
    def challenge_connection_id(self,challenge_connection_id):
        '''challenge_connection_id : "Challenge.Connection." ID "(" param_question "," param_list1 "," param_list2 "," param_acerto "," param_fail ")"'''
        children = challenge_connection_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "CONNECTIONS"
        
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def challenge_sequence(self,challenge_sequence):
        '''challenge_sequence : "Challenge.Sequence" "(" param_question "," param_sequence "," param_acerto "," param_fail ")"'''
        children = challenge_sequence.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'SEQUENCE'

        return ('Challenge',value)
    
    def challenge_sequence_id(self,challenge_sequence_id):
        '''challenge_sequence_id : "Challenge.Sequence." ID "(" param_question "," param_sequence "," param_acerto "," param_fail ")"'''
        children = challenge_sequence_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "SEQUENCE"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def challenge_puzzle(self,challenge_puzzle):
        '''challenge_puzzle : "Challenge.Puzzle" "(" param_image "," param_acerto ")"'''
        children = challenge_puzzle.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'PUZZLE'

        return ('Challenge',value)

    def challenge_puzzle_id(self,challenge_puzzle_id):
        '''challenge_puzzle_id : "Challenge.Puzzle." ID "(" param_image "," param_acerto ")"'''
        children = challenge_puzzle_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "PUZZLE"
        
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def challenge_slidepuzzle(self,challenge_slidepuzzle):
        '''challenge_slidepuzzle : "Challenge.SlidePuzzle" "(" param_image "," param_acerto ")"'''
        children = challenge_slidepuzzle.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'SLIDEPUZZLE'

        return ('Challenge',value)
    
    def challenge_slidepuzzle_id(self,challenge_slidepuzzle_id):
        '''challenge_slidepuzzle_id : "Challenge.SlidePuzzle." ID "(" param_image "," param_acerto ")"'''
        children = challenge_slidepuzzle_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "SLIDEPUZZLE"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def challenge_socket(self,challenge_socket):
        '''challenge_socket : "Challenge.Socket" "(" param_host "," param_port "," param_message "," param_acerto "," param_fail ")"'''
        children = challenge_socket.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'SOCKET_CONNECTION'

        return ('Challenge',value)
    
    def challenge_socket_id(self,challenge_socket_id):
        '''challenge_socket_id : "Challenge.Socket." ID "(" param_host "," param_port "," param_message "," param_acerto "," param_fail ")"'''
        children = challenge_socket_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "SOCKET_CONNECTION"
        
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : 'Challenge',
                    "value" : value
                }
        
        return value

    def events(self,events):
        '''events : "[" event ("," event)* "]"'''
        children = events.children
        value = []
        for child in children:
            value.append(self.visit(child))
        return value

    def event(self,event):
        '''event : event_arg|event_constructor_id|event_python_call'''
        child = event.children[0]
        value = self.visit(child)
        return value

    def event_arg(self,event_arg):
        '''event_arg : ID'''
        child = event_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Event'):
            return copy.deepcopy(self.dict_vars[id]['value']) 

    def event_id(self,event_id):
        '''event_id : ID'''
        child = event_id.children[0]
        id = child.value
        if self.verify_arg(id,'Event'):
            return id

    def event_python_call(self,event_python_call):
        '''event_python_call : python_call'''
        child = event_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Event':
            value = value.serialize()
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Event do tipo Posição, mas é do tipo {type}.",file=sys. stderr)

    def event_constructor(self,event_constructor):
        '''event_constructor : "Event" "(" (param_if ",")? param_then ("," param_repetitions)? ")"'''
        children = event_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value

        return ("Event",value)
    
    def event_constructor_id(self,event_constructor_id):
        '''event_constructor_id : "Event." ID "(" (param_if ",")? param_then ("," param_repetitions)? ")"'''
        children = event_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Event",
                    "value" : value
                }    
        
        return value
    
    def sources(self,sources):
        '''sources : "[" source ("," source)* "]"'''
        children = sources.children
        sources = []
        for child in children:
            sources.append(self.visit(child))
        return sources
    
    def source(self, source):
        '''source : text | "ImageLib." ID'''
        child = source.children[0]
        src = []
        if isinstance(child, Tree):
                value = self.visit(child)
                try:
                    file = open(value)
                    src = ["PATH",os.path.realpath(file.name)]
                    file.close()
                except:
                    try:
                        headers = {
                                "user-agent": "curl/7.84.0",
                                "accept": "*/*"
                            }
                        response = requests.get(url=value,headers=headers)
                        if(response.status_code == 200):
                            src = ["URL",value]
                        else:
                            print(f"ERROR: {response} url: '{value}'",file=sys.stderr)
                            exit(-1)
                    except:
                            print(f"ERROR: Ficheiro de image ou url '{value}' not encontrado!",file=sys.stderr)
                            exit(-1)
        else:
            src = ['LIB', child]
        return src

    def param_scenarios(self,param_scenarios):
        '''param_scenarios : "scenarios" "=" scenarios'''
        child = param_scenarios.children[0]
        value = self.visit(child)
        return ('scenarios',value)


    def param_then(self,param_then):
        '''param_then : "then" "=" posconditions'''
        child = param_then.children[0]
        value = self.visit(child)
        return ('posconditions',value)

    def param_view_inicial(self,param_view_inicial):
        '''param_view_inicial : "view_inicial" "=" view_arg'''
        child = param_view_inicial.children[0]
        value = self.visit(child)
        return ('initial_view',value)

    def param_views(self,param_views):
        '''param_views : "views" "=" views'''
        child = param_views.children[0]
        value = self.visit(child)
        return ('views',value)

    def param_choices(self,param_choices):
        '''param_choices : "choices" "=" list_text'''
        child = param_choices.children[0]
        value = self.visit(child)
        return ('choices',value)
    
    def param_ceil(self,param_ceil):
        '''param_ceil : "ceil" "=" number'''
        child = param_ceil.children[0]
        value = self.visit(child)
        return ('ceil',value)

    def param_floor(self,param_floor):
        '''param_floor : "floor" "=" number'''
        child = param_floor.children[0]
        value = self.visit(child)
        return ('floor',value)

    def param_events(self,param_events):
        '''param_events : "events" "=" events'''
        child = param_events.children[0]
        value = self.visit(child)
        return ('events',value)

    def param_fail(self,param_fail):
        '''param_fail : "fail" "=" event_arg'''
        child = param_fail.children[0]
        value = self.visit(child)
        #value = value['posconditions']
        return ('fail',value)

    def param_source(self,param_source):
        '''param_source : "source" "=" source'''
        child = param_source.children[0]
        value = self.visit(child)

        return ('sources',[value]) #(param,value)
    
    def param_loop(self,param_loop):
        '''param_loop : "loop" "=" BOOLEAN'''
        child = param_loop.children[0]
        value = child.value
        if value=='yes':
            value = True
        else:
            value = False
        return ('loop',value)

    def param_background(self,param_background):
        '''param_background : "background" "=" view'''
        child = param_background.children[0]
        value = self.visit(child)
        
        return ('view',value)

    def param_story(self,param_story):
        '''param_story : "story" "=" (list_text|list_format_text)'''
        child = param_story.children[0]
        value = self.visit(child)
        if (child.data == 'list_text'):
            return ('story',value)
        else:
            return ('format_story', value)
    
    def param_texts(self,param_texts):
        '''param_texts : "texts" "=" text'''
        child = param_texts.children[0]
        value = self.visit(child)

        return ('texts',value)


    def param_text(self,param_texts):
        '''param_text : "text" "=" (text|format_text)'''
        child = param_texts.children[0]
        value = self.visit(child)
        if (child.data == 'text'):
            return ('text',value)
        else:
            return ('format_text', value)

    def param_start(self,param_start):
        '''param_start : "start" "=" ID'''

        child = param_start.children[0]
        source_id = child.value

        if source_id in self.dict_vars:
            source_type = self.dict_vars[source_id]['type']
            if not (source_type == 'Transition' or source_type == 'Scenario'):
                print(f"ERROR: Esperado uma variável do tipo Transition ou Scenario, mas a variável {source_id} é do tipo {source_type}.",file=sys.stderr)
                exit(-1)
        else:
            print(f"ERROR: Variável {source_id} não foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)


        return ('start',{'source' : source_type.upper(), 'id' : source_id})

    def param_host(self,param_host):
        '''param_host : "host" "=" text'''
        child = param_host.children[0]
        value = self.visit(child)
        return ('host',value)

    def param_image(self,param_image):
        '''param_image : "image" "=" source'''
        child = param_image.children[0]
        value = self.visit(child)

        return ('sources',[value])

    def param_images(self,param_images):
        '''param_images : "images" "=" sources'''
        child = param_images.children[0]
        values = self.visit(child)

        return ('sources',values)

    def param_list1(self,param_list1):
        '''param_list1 : "list1" "=" list_text'''
        child = param_list1.children[0]
        value = self.visit(child)
        return ('list1',value)

    def param_list2(self,param_list2):
        '''param_list2 : "list2" "=" list_text'''
        child = param_list2.children[0]
        value = self.visit(child)
        return ('list2',value)

    def param_message(self,param_message):
        '''param_message : "message" "=" text'''
        child = param_message.children[0]
        value = self.visit(child)
        return ('message',value)

    def param_music(self,param_music):
        '''param_music : "música" "=" sound'''
        child = param_music.children[0]
        value = self.visit(child)
        return ('music',value)

    def param_motion_object(self,param_motion_object):
        '''param_motion_object : "motion_object" "=" object_id'''
        child = param_motion_object.children[0]
        value = self.visit(child)
        return ('motion_object',value)
    
    def param_trigger_object(self,param_trigger_object):
        '''param_trigger_object : "object" "=" object_id'''
        child = param_trigger_object.children[0]
        value = self.visit(child)
        return ('trigger_object',value)

    def param_objects(self,param_objects):
        '''param_objects : "objects" "=" objects'''
        child = param_objects.children[0]
        value = self.visit(child)

        return ('objects',value)

    def param_question(self,param_question):
        '''param_question : "question" "=" text'''
        child = param_question.children[0]
        value = self.visit(child)
        return ('question',value)

    def param_port(self,param_port):
        '''param_port : "port" "=" number'''
        child = param_port.children[0]
        value = self.visit(child)
        return ('port',value)

    def param_position(self,param_position):
        '''param_position : "position" "=" position'''
        child = param_position.children[0]
        value = self.visit(child)
        return ('position',value)
    
    def param_position_reference(self,param_position_reference):
        '''param_position_reference : "position_reference" "=" POS_REF'''
        value = param_position_reference.children[0].value
        return ('position_reference',value)

    def param_next_scene(self,param_next_scene):
        '''param_next_scene : "próxima_cena" "=" scenario_id'''
        child = param_next_scene.children[0]
        value = self.visit(child)
        return ('next_scenario',value)

    def param_next_trans(self,param_next_trans):
        '''param_next_trans : "próxima_transition" "=" transition_id'''
        child = param_next_trans.children[0]
        value = self.visit(child)
        return ('next_transition',value)

    def param_if(self,param_if):
        '''param_if : "se" "=" preconditions'''
        child = param_if.children[0]
        value = self.visit(child)
        return ('preconditions',value)

    def param_sequence(self,param_sequence):
        '''param_sequence : "sequence" "=" list_text'''
        child = param_sequence.children[0]
        value = self.visit(child)
        return ('sequence',value)

    def param_sounds(self,param_sounds):
        '''param_sounds : "sounds" "=" sounds'''
        child = param_sounds.children[0]
        value = self.visit(child)
        return ('sounds',value)
    
    def param_sucess(self,param_sucess):
        '''param_sucess : "sucess" "=" event_arg'''
        child = param_sucess.children[0]
        value = self.visit(child)
        #value = value['posconditions']
        return ('sucess',value)

    def param_repetitions(self,param_repetitions):
        '''param_repetitions : "repetições" "=" number'''
        child = param_repetitions.children[0]
        value = self.visit(child)
        return ('repetitions',value)

    def param_answer(self,param_answer):
        '''param_answer : "answer" "=" text'''
        child = param_answer.children[0]
        value = self.visit(child)
        return ('answer',value)

    def param_size(self,param_size):
        '''param_size : "size" "=" size'''
        child = param_size.children[0]
        value = self.visit(child)
        return ('size',value)

    def param_time_sprite(self,param_time_sprite):
        '''param_time_sprite : "time_sprite" "=" number'''
        child = param_time_sprite.children[0]
        value = self.visit(child)
        return ('time_sprite',value)

    def param_title(self,param_title):
        '''param_title : "title" "=" text'''
        child = param_title.children[0]
        value = self.visit(child)
        return ('title',value)

    def param_transitions(self,param_transitions):
        '''param_transitions : "transições" "=" transitions'''
        children = param_transitions.children
        value = self.visit(children[0])
        return ('transitions',value)
    
    def param_draws(self,param_draws):
        '''param_draws : "draws" "=" draws'''
        children = param_draws.children
        value = self.visit(children[0])
        return ('draws',value)

    def param_hitboxes(self,param_hitboxes):
        '''param_hitboxes : "hitboxes" "=" hitboxes'''
        children = param_hitboxes.children
        value = self.visit(children[0])
        return ('hitboxes',value)
    
    def param_variables(self,param_variables):
        '''param_variables : "variables" "=" variables'''
        children = param_variables.children
        value = self.visit(children[0])
        return ('variables',value)
    
    def param_tl(self,param_tl):
        '''param_tl : "tl" "=" number'''
        child = param_tl.children[0]
        value = self.visit(child)
        return ('tl',value)
    
    def param_tr(self,param_tr):
        '''param_tr : "tr" "=" number'''
        child = param_tr.children[0]
        value = self.visit(child)
        return ('tr',value)
    
    def param_bl(self,param_bl):
        '''param_bl : "bl" "=" number'''
        child = param_bl.children[0]
        value = self.visit(child)
        return ('bl',value)
    
    def param_br(self,param_br):
        '''param_br : "br" "=" number'''
        child = param_br.children[0]
        value = self.visit(child)
        return ('br',value)
    
    def param_point1(self,param_point1):
        '''param_point1 : "point1" "=" position'''
        child = param_point1.children[0]
        value = self.visit(child)
        return ('point1',value)
    
    def param_point2(self,param_point2):
        '''param_point2 : "point2" "=" position'''
        child = param_point2.children[0]
        value = self.visit(child)
        return ('point2',value)
    
    def param_point3(self,param_point3):
        '''param_point3 : "point3" "=" position'''
        child = param_point3.children[0]
        value = self.visit(child)
        return ('point3',value)
    
    def param_points(self,param_points):
        '''param_points : "points" "=" positions'''
        child = param_points.children[0]
        value = self.visit(child)
        return ('points',value)
    
    def param_radius(self,param_radius):
        '''param_radius : "radius" "=" number'''
        child = param_radius.children[0]
        value = self.visit(child)
        return ('radius',value)

    def param_number(self,param_number):
        '''param_number : "number" "=" number'''
        child = param_number.children[0]
        value = self.visit(child)
        return ('number',value)
    
    def param_width(self,param_width):
        '''param_width : "width" "=" number'''
        child = param_width.children[0]
        value = self.visit(child)
        return ('width',value)
    
    def param_arcstart(self,param_arcstart):
        '''param_arcstart : "arcstart" "=" number'''
        child = param_arcstart.children[0]
        value = self.visit(child) * (math.pi/180)
        return ('arcstart',value)
    
    def param_arcstop(self,param_arcstop):
        '''param_arcstop : "arcstop" "=" number'''
        child = param_arcstop.children[0]
        value = self.visit(child) * (math.pi/180)
        return ('arcstop',value)
    
    def param_color(self,param_color):
        '''param_color : "color" "=" color'''
        child = param_color.children[0]
        value = self.visit(child)
        return ('color',value)


    def preconditions(self,preconditions):
        '''preconditions : precondition|preconds_and|preconds_ou|preconds_not|preconds_group'''
        child = preconditions.children[0]
        if child.data == 'precondition':
            return {
                "var" : self.visit(child)
            }
        else:
            return self.visit(child)

    def preconds_and(self,preconds_and):
        '''preconds_and : preconditions "and" preconditions'''
        children = preconds_and.children
        left = self.visit(children[0])
        right = self.visit(children[1])
        result = {
            "operator" : "AND",
            "left" : left,
            "right" : right

        }
        return result

    def preconds_ou(self,preconds_ou):
        '''preconds_ou : preconditions "or" preconditions'''
        children = preconds_ou.children
        left = self.visit(children[0])
        right = self.visit(children[1])
        result = {
            "operator" : "OR",
            "left" : left,
            "right" : right

        }
        return result

    def preconds_not(self,preconds_not):
        '''preconds_not : "not" preconditions'''
        child = preconds_not.children[0]
        left = self.visit(child)
        right = None
        result = {
            "operator" : "NOT",
            "left" : left,
            "right" : right

        }
        return result

    def preconds_group(self,preconds_group):
        '''preconds_group : "(" preconditions ")"'''
        child = preconds_group.children[0]
        return self.visit(child)

    def precondition(self,precondition):
        '''precondition : precond_click_obj | precond_click_not_obj | precond_obj_is_view | precond_ev_already_hap | precond_obj_in_use | precond_already_passed'''
        child = precondition.children[0]
        return self.visit(child)

    def precond_click_obj(self,precond_click_obj):
        '''precond_click_obj : "click" ID'''
        children = precond_click_obj.children

        id = children[0].value

        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Object':
                return {
                    'type' : 'CLICKED_OBJECT',
                    'object' : id,
                }
            elif type == 'Hitbox':
                return {
                    'type' : 'CLICKED_HITBOX',
                    'hitbox' : id,
                }   
            else:
                print(f"ERROR: Esperado uma variável do tipo Object ou Hitbox, mas a variável {id} é do tipo {type}.",file=sys.stderr)
                exit(-1)
        else:
            print(f"ERROR: Variável {id} não foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)
        
        
        

    def precond_click_not_obj(self,precond_click_not_obj):
        '''precond_click_not_obj : "click not" ID'''
        children = precond_click_not_obj.children
        id = children[0].value

        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Object':
                return {
                    'type' : 'CLICKED_NOT_OBJECT',
                    'object' : id,
                }
            elif type == 'Hitbox':
                return {
                    'type' : 'CLICKED_NOT_HITBOX',
                    'hitbox' : id,
                }   
            else:
                print(f"ERROR: Esperado uma variável do tipo Object ou Hitbox, mas a variável {id} é do tipo {type}.",file=sys.stderr)
                exit(-1)

    def precond_obj_is_view(self,precond_obj_is_view):
        '''precond_obj_is_view : object_id "is" view_id'''
        children = precond_obj_is_view.children

        object_id = self.visit(children[0])
        view_id = children[1].value

        found = False
        for view in self.dict_vars[object_id]['value']['views']:
            if view['id'] == view_id:
                found = True
                break
        
        if not found:
            print(f'ERROR: Na pré condição "{object_id} is {view_id}", o {view_id} not é um \'View\' do \'Object\' {object_id}.',file=sys.stderr)
            exit(-1)
        
        return {
            'type' : 'WHEN_OBJECT_IS_VIEW',
            'object' : object_id,
            'view' : view_id
        }

    def precond_ev_already_hap(self,precond_ev_already_hap):
        '''precond_ev_already_hap : event_id "already happened""'''
        children = precond_ev_already_hap.children

        return {
            'type' : 'AFTER_EVENT',
            'event' : self.visit(children[0])
            }

    def precond_obj_in_use(self,precond_obj_in_use):
        '''precond_obj_in_use : object_id "is in use"'''
        children = precond_obj_in_use.children
        return {
                'type' : 'OBJ_IS_IN_USE',
                'object' : self.visit(children[0])
            }
    def precond_already_passed(self, precond_already_passed):
        '''precond_already_passed : "já tiver passado" number "seconds"'''
        children = precond_already_passed.children
        return {
            'type' : 'AFTER_TIME',
            'time' : self.visit(children[0]) * 1000 #seconds -> miliseconds
        }

    def precond_var_equal(self, precond_var_equal):
        '''precond_var_equal : variable_id "is equal to" number'''
        children = precond_var_equal.children
        return {
            'type' : 'IS_EQUAL_TO',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }

    def precond_var_greater(self, precond_var_greater):
        '''precond_var_greater : variable_id "is greater than" number'''
        children = precond_var_greater.children
        return {
            'type' : 'IS_GREATER_THAN',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }
    
    def precond_var_less(self, precond_var_less):
        '''precond_var_greater : variable_id "is less than" number'''
        children = precond_var_less.children
        return {
            'type' : 'IS_LESS_THAN',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }
    
    def precond_var_greater_equal(self, precond_var_greater_equal):
        '''precond_var_greater : variable_id "is greater than or equal to" number'''
        children = precond_var_greater_equal.children
        return {
            'type' : 'IS_GREATER_THAN_OR_EQUAL_TO',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }
    
    def precond_var_less_equal(self, precond_var_less_equal):
        '''precond_var_less_equal : variable_id "is less than or equal to" number'''
        children = precond_var_less_equal.children
        return {
            'type' : 'IS_LESS_THAN_OR_EQUAL_TO',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }

    def posconditions(self,posconditions):
        '''posconditions : poscondition ("and" poscondition)*'''
        children = posconditions.children
        posconds = []
        for child in children:
            posconds.append(self.visit(child))

        return posconds


    def poscondition(self,poscondition):
        '''poscondition : poscond_obj_muda_view|poscond_obj_vai_inv|poscond_fim_de_jogo|poscond_mostra_msg|poscond_obj_muda_tam|poscond_obj_muda_pos|poscond_muda_cena|poscond_remove_obj|poscond_play_sound|poscond_comeca_des|poscond_trans'''
        children = poscondition.children
        return self.visit(children[0])

    def poscond_obj_muda_view(self,poscond_obj_muda_view):
        '''poscond_obj_muda_view : object_id "change to" view_id'''
        children = poscond_obj_muda_view.children

        object_id = self.visit(children[0])
        view_id = children[1].value
        
        #TODO: verificar se view_id is em object (SO FALTA TESTAR)
        found = False if view_id != "none" else True #TODO: ver melhor isto do none
        if not found:
            for view in self.dict_vars[object_id]['value']['views']:
                if view['id'] == view_id:
                    found = True
                    break
        
        if not found:
            print(f'ERROR: Na pós condição "{object_id} change to {view_id}", o {view_id} not é um \'View\' do \'Object\' {object_id}.',file=sys.stderr)
            exit(-1)

        return {
            'type' : 'OBJ_CHANGE_VIEW',
            'object' : object_id,
            'view' : view_id
            }

    def poscond_obj_vai_inv(self,poscond_obj_vai_inv):
        '''poscond_obj_vai_inv : object_id "goes to inventory"'''
        children = poscond_obj_vai_inv.children
        return {
            'type' : 'OBJ_PUT_INVENTORY',
            'object' : self.visit(children[0])
            }

    def poscond_fim_de_jogo(self,poscond_fim_de_jogo):
        '''poscond_fim_de_jogo : "end of game" ("whit message" (text|format_text))?'''
        children = poscond_fim_de_jogo.children
        type = 'END_GAME'
        if(len(children) > 0):
            message = self.visit(children[0])
            if not (children[0].data == 'text'):
                type = 'END_GAME_FORMAT_MESSAGE'
        else:
            message = "Congratulations! You Escaped!"
        return {
            'type' : type,
            'message' : message
            }

    def poscond_mostra_msg(self,poscond_mostra_msg):
        '''poscond_mostra_msg : "show message" (text|format_text) "in" position'''
        children = poscond_mostra_msg.children
        if children[0].data == 'text':
            return {
                'type' : 'SHOW_MESSAGE',
                'message' : self.visit(children[0]),
                'position' : self.visit(children[1])
                }
        else:
            return {
                'type' : 'SHOW_FORMAT_MESSAGE',
                'message' : self.visit(children[0]),
                'position' : self.visit(children[1])
                }

    def poscond_obj_muda_tam(self,poscond_obj_muda_tam):
        '''poscond_obj_muda_tam : object_id "change size to" size'''
        children = poscond_obj_muda_tam.children
        return {
                'type' : 'OBJ_SCALE',
                'object' : self.visit(children[0]),
                'scale' : self.visit(children[1]),
            }

    def poscond_obj_muda_pos(self,poscond_obj_muda_pos):
        '''poscond_obj_muda_pos : object_id "move to" position'''
        children = poscond_obj_muda_pos.children
        return {
                'type' : 'OBJ_CHANGE_POSITION',
                'object' : self.visit(children[0]),
                'position' : self.visit(children[1]),
            }

    def poscond_muda_cena(self,poscond_muda_cena):
        '''poscond_muda_cena : "change to cena" scenario_id'''
        children = poscond_muda_cena.children
        return {
                'type' : 'CHANGE_SCENARIO',
                'scenario' : self.visit(children[0]),
            }

    def poscond_remove_obj(self,poscond_remove_obj):
        '''poscond_remove_obj : object_id "is removed"'''
        children = poscond_remove_obj.children
        return {
                'type' : 'REMOVE_OBJ',
                'object' : self.visit(children[0])
            }

    def poscond_play_sound(self,poscond_play_sound):
        '''poscond_play_sound : "play" sound_id "do" ID'''
        children = poscond_play_sound.children


        sound_id = self.visit(children[0])
        source_id = children[1].value

        if source_id in self.dict_vars:
            source_type = self.dict_vars[source_id]['type']
            if source_type == 'Object' or source_type == 'Scenario':
                found = False
                if 'sounds' in self.dict_vars[source_id]['value']:
                    for sound in self.dict_vars[source_id]['value']['sounds']:
                        if sound['id'] == sound_id:
                            found = True
                            break
                
                if not found:
                    print(f'ERROR: Na pós condição "play {sound_id} do {source_id}", o {sound_id} not é um \'Sound\' do \'{source_type}\' {source_id}.',file=sys.stderr)
                    exit(-1)
                
            else:
                print(f"ERROR: Esperado uma variável do tipo Object ou Scenario, mas a variável {source_id} é do tipo {source_type}.",file=sys.stderr)
                exit(-1)
        else:
            print(f"ERROR: Variável {source_id} não foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)

        return {
                'type' : 'PLAY_SOUND',
                'sound' : sound_id,
                'source_id' : source_id,
                'source_type' : source_type
            }

    def poscond_comeca_des(self,poscond_comeca_des):
        '''poscond_comeca_des : "start challenge" challenge_arg'''
        children = poscond_comeca_des.children
        return self.visit(children[0])

    def poscond_trans(self,poscond_trans):
        '''poscond_trans : "transition" transition_id'''
        children = poscond_trans.children
        return {
            'type' : 'TRANSITION',
            'transition' : self.visit(children[0])
        }
    
    def poscond_var_decreases(self,poscond_var_decreases):
        '''poscond_var_decreases : variable_id "decreases" number'''
        children = poscond_var_decreases.children
        return {
            'type' : 'VAR_DECREASES',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }
    
    def poscond_var_increases(self,poscond_var_increases):
        '''poscond_var_increases : variable_id "increases" number'''
        children = poscond_var_increases.children
        return {
            'type' : 'VAR_INCREASES',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }
    
    def poscond_var_becomes(self,poscond_var_becomes):
        '''poscond_var_becomes : variable_id "becomes" number'''
        children = poscond_var_becomes.children
        return {
            'type' : 'VAR_BECOMES',
            'variable' : self.visit(children[0]),
            'number' : self.visit(children[1])
        }

    def python_block(self,python_block):
        '''python_block : "Python" "=" PYTHON_CODE'''
        children = python_block.children
        code = children[0].value
        exec(code,self.namespace)

        # Dicionário de variáveis locais após a execução
        self.locals_python = {key: value for key, value in self.namespace.items() if key in code}

        # Dicionário de variáveis globais após a execução
        self.globals_python = globals().copy()



def parse(args):
    grammar = open(f"{current_folder}/grammar_erpl.txt","r")

    if not args.args:
       args.args = []

    # ficheiro com a frase para analisar
    if args.input:
        file = open(args.input[0])
        code = file.read()
        file.close()
    else:
        code = sys.stdin.read()

    # analisar frase com a gramatica definida
    p = Lark(grammar)
    parse_tree = p.parse(code)
    it = Interpreter(args.args)
    data = it.visit(parse_tree)

    #Serializing json
    if args.output:
        with open(args.output[0], "w") as outfile:
            json.dump(data, outfile, indent = 3)
    else:
        print(json.dumps(data))
    return code