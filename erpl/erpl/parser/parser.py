#!/usr/bin/python3
from lark.visitors import Interpreter
from lark import Lark, Token, Tree
import argparse
import sys
import json
import os
from PIL import Image

from .obj_parser import parse_obj

current_folder = os.path.dirname(__file__)


def parser_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL Parser')
    parser.add_argument('--output','-o'            ,type=str, nargs=1,required=False                                , help='Output file')
    parser.add_argument('--input','-i'             ,type=str, nargs=1,required=True                                 , help='Input file')
    parser.add_argument('--args','-args'           ,nargs='+'                                                       , help='Args')
    return parser.parse_args()


class Interpreter(Interpreter):
    def __init__(self):
        
        self.WIDTH = 0
        self.HEIGHT = 0

        #variáveis para o python_block
        self.locals_python = {}
        self.globals_python = {}
        self.namespace = {}
        
        #variáveis
        self.dict_vars = {}

        #variáveis para imports
        self.dict_imports = {
            'objects' : {}
        }

    def verify_id_exist(self,id):
        if id in self.dict_vars:
            print(f"ERROR: Variável {id} já foi inicializada antes.",file=sys.stderr)
            exit(-1)
        else:
            return False

    def verify_arg(self, id, type):
        if id in self.dict_vars:
            if self.dict_vars[id]['type'] == type:
                return True
            else:
                print(f"ERROR: Esperado uma variável do tipo {type}, mas a variável {id} é do tipo {self.dict_vars[id]['type']}.",file=sys.stderr)
                exit(-1)
        else:
            print(f"ERROR: Variável {id} not foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)
        
    def get_image_size(self,path_image):
        #TODO: melhorar talvez
        try:
            with Image.open(path_image) as img:
                largura, altura = img.size
                return largura, altura
        except IOError:
            print(f"ERROR: Não foi possível abrir a image em {path_image}.", file=sys.stderr)
            exit(-1)

    def verify_pos_and_size(self,objects):
        #TODO: ver se isto ta bem depois
        aux_h = 0
        aux_w = round(self.WIDTH/len(objects),2)
        i = 1
        for object in objects:
            #verifica se o object not tem size
            if 'size' not in object: #se not temos de ver o size view a view
                for view in object['views']:
                    #verificar se o view ja tem size
                    if 'size' in view:
                        continue
                    else: #se not tiver temos deduzir o size
                        img = view['images'][0] if 'images' in view else view['image']
                        view['size'] = self.get_image_size(img)
            #now verify the position
            if 'position' not in object:
                if 'size' in object:
                    size_w = object['size'][0]
                    size_h = object['size'][1]
                    w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                    h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                    object['position'] = (w,h)
                else: #temos de ver a posiçao view a view
                    for view in object['views']:
                        if 'position' not in view:
                            size_w = view['size'][0]
                            size_h = view['size'][1]
                            w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                            h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                            view['position'] = (w,h)
            i+=1
        return objects

    def decode_python_type(self,python_type,value):
        if python_type == str:
            return 'Text'
        elif python_type == tuple and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            return 'Position'
        elif python_type == list and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            return 'Size'
        elif python_type == list and all(isinstance(element, str) for element in value):
            return 'Text_List'
        elif python_type == int or python_type == float:
            return 'Number'
        elif python_type == dict:
            #TODO: Object/Sound/View/Challenge/Transition/Scenario/Event
            return 'Object' 
        return python_type

    def start(self,start):
        '''start : er imports? vars? python_block?'''
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
        '''er_parameters : param_title "," param_size "," param_scenarios "," param_events "," param_transitions'''
        children = er_parameters.children
        escape_room = {}
        for child in children:
            param,param_value = self.visit(child)
            escape_room[param] = param_value
        
        self.WIDTH = escape_room['size'][0]
        self.HEIGHT = escape_room['size'][1]

        for scenario in escape_room['scenarios']:
            scenario['objects'] = self.verify_pos_and_size(objects=scenario['objects'])

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
        obj = parse_obj(id,current_folder)
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
        '''add_object : cenario_id ".add_Object" "(" object ")"'''
        children = add_object.children
        id = self.visit(children[0])
        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Object':
                object = self.visit(children[1])
                self.dict_vars[id]['value']['objects'].append(object)
            else:
                print(f"ERROR: Não é possível addr um 'Object' a uma variável do tipo {type}, apenas a variáveis do tipo 'Scenario'.",file=sys.stderr)
                exit(-1)
        else:
            print(f'ERROR: A variável {id} not foi inicializada.',file=sys.stderr)

    def var(self,var):
        '''var : ID "=" value'''
        children = var.children
        var_name = children[0].value
        test = self.visit(children[1])
        #print(test)
        (type,value) = test

        #Colocar id not for tipo primário:
        if type in ["View", "Sound", "Object", "Scenario", "Transition", 'Challenge', "Event"]:
            value["id"] = var_name

        if not self.verify_id_exist(var_name):
            self.dict_vars[var_name] = {
                'type' : type,
                'value' : value
            }

    def value(self,val):
        '''value : ID|python_call|list_text_constructor|text_constructor|size_constructor|position_constructor|number_constructor|view_constructor|object_constructor|object_imported|sound_constructor|cenario_constructor|event_constructor|challenge_constructor|transition_constructor'''
        child = val.children[0]
        #TODO: ver se é ID
        if isinstance(child, Token):
            id = child.value
            if id in self.dict_vars:
                type = self.dict_vars[id]['type']
                if type in ["View", "Sound", "Object", "Scenario", "Transition", 'Challenge', "Event"]:
                    value = dict(self.dict_vars[id]['value'])
                else:
                    value = self.dict_vars[id]['value']
                return (type,value)
            else:
                print(f'ERROR: A variável {id} not foi inicializada.',file=sys.stderr)
                exit(-1)
        else:
            return self.visit(child)

    def python_call(self,python_call):
        '''python_call : python_local|python_function'''
        children = python_call.children
        return self.visit(children[0])

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
        '''text : text_arg|text_constructor|text_python_call'''
        child = text.children[0]
        if child.data == 'text_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

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

    def size(self,size):
        '''size : size_arg|size_constructor|size_python_call'''
        child = size.children[0]
        if child.data == 'size_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def size_arg(self,size_arg):
        '''size_arg : ID'''
        child = size_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Size'):
            return self.dict_vars[id]['value'] 

    def size_python_call(self,size_python_call):
        '''size_python_call : python_call'''
        child = size_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Size':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Tamanho, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def size_constructor(self,size_constructor):
        '''size_constructor : "[" NUM "," NUM "]"'''
        children = size_constructor.children
        w = self.visit(children[0])
        h = self.visit(children[1])
        return('Size',(w,h)) #(type,value)

    def position(self,position):
        '''position : position_arg|position_constructor|position_python_call'''
        child = position.children[0]
        if child.data == 'position_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def position_arg(self,position_arg):
        '''position_arg : ID'''
        child = position_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Position'):
            return self.dict_vars[id]['value'] 

    def position_python_call(self,position_python_call):
        '''position_python_call : python_call'''
        child = position_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Position':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def position_constructor(self,position_constructor):
        '''position_constructor : "(" number "," number ")"'''
        children = position_constructor.children
        x = self.visit(children[0])
        y = self.visit(children[1])
        return ('Position',(x,y))

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
        num = int(children[0].value)
        return('Number',num) #(type,value)

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
            return self.dict_vars[id]['value'] 

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
        return ('View',value)

    def view_animated(self,view_animated):
        '''view_animated : "View.Dinâmico" "(" param_images "," param_repetitions "," param_time_sprite ("," param_position)? ("," param_size)? ")"'''
        children = view_animated.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value
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

        self.dict_vars[id] = {
            "type" : 'View',
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
            return self.dict_vars[id]['value'] 

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
        '''sound_constructor : "Sound" "(" param_source ")"'''
        child = sound_constructor.children[0]
        value = {}
        (param,param_value) = self.visit(child)
        value[param] = param_value
        return ('Sound',value) #(type,value)
    
    def sound_constructor_id(self,sound_constructor_id):
        '''sound_constructor_id : "Sound." ID "(" param_source ")"'''
        children = sound_constructor_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        (param,param_value) = self.visit(children[1])
        value[param] = param_value
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
            return self.dict_vars[id]['value'] 

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
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Object do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def object_constructor(self,object_constructor):
        '''object_constructor : "Object" "(" (param_view_inicial ",")? param_views ("," param_position)? ("," param_size)? ("," param_sounds)? ")"'''
        children = object_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        return ('Object',value)

    def object_imported(self,object_imported):
        '''object_imported : "Object." ID ("(" (param_position|param_size|(param_position "," param_size)) ")")?'''
        children = object_imported.children
        id = children[0].value
        if id in self.dict_imports['objects']:
            object = dict(self.dict_imports['objects'][id])
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
        for child in children[1:]:
            param,param_value = self.visit(child)
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
            object = dict(self.dict_imports['objects'][id_import])
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

    def scenarios(self,scenarios):
        '''scenarios : "[" cenario ("," cenario)* "]"'''
        children = scenarios.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def cenario(self,cenario):
        '''cenario : cenario_arg|cenario_constructor_id|cenario_python_call'''
        child = cenario.children[0]
        value = self.visit(child)
        return value

    def cenario_arg(self,cenario_arg):
        '''cenario_arg : ID'''
        child = cenario_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Scenario'):
            return self.dict_vars[id]['value'] 

    def cenario_id(self,cenario_id):
        '''cenario_id : ID'''
        child = cenario_id.children[0]
        id = child.value
        if self.verify_arg(id,'Scenario'):
            return id
        

    def cenario_python_call(self,cenario_python_call):
        '''cenario_python_call : python_call'''
        child = cenario_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Scenario':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Scenario do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def cenario_constructor(self,cenario_constructor):
        '''cenario_constructor : "Scenario" "(" param_view_inicial "," param_views "," param_objects ("," param_sounds)? ")"'''
        children = cenario_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        return ('Scenario',value)
    
    def cenario_constructor_id(self,cenario_constructor_id):
        '''cenario_constructor_id : "Scenario." ID "(" param_view_inicial "," param_views "," param_objects ("," param_sounds)? ")"'''
        children = cenario_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

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
            return self.dict_vars[id]['value'] 

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
            return self.dict_vars[id]['value'] 

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
            return self.dict_vars[id]['value'] 

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

    def param_events(self,param_events):
        '''param_events : "events" "=" events'''
        child = param_events.children[0]
        value = self.visit(child)
        return ('events',value)

    def param_fail(self,param_fail):
        '''param_fail : "fail" "=" event_arg'''
        child = param_fail.children[0]
        value = self.visit(child)
        return ('fail',value)

    def param_source(self,param_source):
        '''param_source : "source" "=" text'''
        child = param_source.children[0]
        value = self.visit(child)

        try:
            file = open(value)
            src = os.path.realpath(file.name)
            file.close()
        except:
            print(f"ERROR: Ficheiro de sound '{value}' not encontrado!",file=sys.stderr)
            exit(-1)

        return ('source',src) #(param,value)

    def param_background(self,param_background):
        '''param_background : "background" "=" view'''
        child = param_background.children[0]
        value = self.visit(child)
        
        return ('background',value)

    def param_story(self,param_story):
        '''param_story : "história" "=" text'''
        child = param_story.children[0]
        value = self.visit(child)
        return ('story',value)

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
            print(f"ERROR: Variável {source_id} not foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)


        return ('start',{'source' : source_type, 'id' : source_id})

    def param_host(self,param_host):
        '''param_host : "host" "=" text'''
        child = param_host.children[0]
        value = self.visit(child)
        return ('host',value)

    def param_image(self,param_image):
        '''param_image : "image" "=" text'''
        child = param_image.children[0]
        value = self.visit(child)

        try:
            file = open(value)
            src = os.path.realpath(file.name)
            file.close()
        except:
            print(f"ERROR: Ficheiro de image '{value}' not encontrado!",file=sys.stderr)
            exit(-1)

        return ('image',src)

    def param_images(self,param_images):
        '''param_images : "images" "=" list_text'''
        child = param_images.children[0]
        values = self.visit(child)
        
        srcs = []
        for value in values:
            try:
                file = open(value)
                src = os.path.realpath(file.name)
                file.close()
                srcs.append(src)
            except:
                print(f"ERROR: Ficheiro de image '{value}' not encontrado!",file=sys.stderr)
                exit(-1)

        return ('images',srcs)

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

    def param_next_scene(self,param_next_scene):
        '''param_next_scene : "próxima_cena" "=" cenario_id'''
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
        '''param_transitions : "transições" "=" (transitions|"[""]")'''
        children = param_transitions.children
        if len(children) > 0:
            value = self.visit(children[0])
        else:
            value = []
        return ('transitions',value)

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
        '''precond_click_obj : "click" object_id'''
        children = precond_click_obj.children
        
        return {
            'type' : 'CLICKED_OBJECT',
            'object' : self.visit(children[0]),
            }

    def precond_click_not_obj(self,precond_click_not_obj):
        '''precond_click_not_obj : "click not" object_id'''
        children = precond_click_not_obj.children
        return {
            'type' : 'CLICKED_NOT_OBJECT',
            'object' : self.visit(children[0]),
            }

    def precond_obj_is_view(self,precond_obj_is_view):
        '''precond_obj_is_view : object_id "is" view_id'''
        children = precond_obj_is_view.children

        object_id = self.visit(children[0])
        view_id = self.visit(children[1])

        #TODO: verificar se view faz parte do obj (SO FALTA TESTAR)

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
                'type' : 'ITEM_IS_IN_USE',
                'item' : self.visit(children[0])
            }
    def precond_already_passed(self, precond_already_passed):
        '''precond_already_passed : "já tiver passado" number "seconds"'''
        children = precond_already_passed.children
        return {
            'type' : 'AFTER_TIME',
            'time' : self.visit(children[0]) * 1000 #seconds -> miliseconds
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
        view_id = self.visit(children[1])
        
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
        '''poscond_fim_de_jogo : "end of game"'''
        return {
            'type' : 'END_GAME',
            }

    def poscond_mostra_msg(self,poscond_mostra_msg):
        '''poscond_mostra_msg : "show message" text "in" position'''
        children = poscond_mostra_msg.children
        return {
            'type' : 'SHOW_MESSAGE',
            'message' : self.visit(children[0]),
            'position' : self.visit(children[1])
            }

    def poscond_obj_muda_tam(self,poscond_obj_muda_tam):
        '''poscond_obj_muda_tam : object_id "change size to" size'''
        children = poscond_obj_muda_tam.children
        return {
                'type' : 'OBJ_CHANGE_SIZE',
                'object' : self.visit(children[0]),
                'size' : self.visit(children[1]),
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
        '''poscond_muda_cena : "change to cena" cenario_id'''
        children = poscond_muda_cena.children
        return {
                'type' : 'CHANGE_SCENARIO',
                'scenario' : self.visit(children[0]),
            }

    def poscond_remove_obj(self,poscond_remove_obj):
        '''poscond_remove_obj : object_id "is removed"'''
        children = poscond_remove_obj.children
        return {
                'type' : 'DELETE_ITEM',
                'item' : self.visit(children[0])
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
            print(f"ERROR: Variável {source_id} not foi inicializada anteriormente.",file=sys.stderr)
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
    it = Interpreter()
    data = it.visit(parse_tree)

    #Serializing json
    if args.output:
        with open(args.output[0], "w") as outfile:
            json.dump(data, outfile, indent = 3)
    else:
        print(json.dumps(data))
    return code

def main():
    args = parser_parse_arguments()
    parse(args)
    

if __name__ == '__main__':
    main()