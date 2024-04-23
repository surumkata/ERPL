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
            print(f"ERROR: Variável {id} não foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)
        
    def get_image_size(self,path_imagem):
        #TODO: melhorar talvez
        try:
            with Image.open(path_imagem) as img:
                largura, altura = img.size
                return largura, altura
        except IOError:
            print(f"ERROR: Não foi possível abrir a imagem em {path_imagem}.", file=sys.stderr)
            exit(-1)

    def verify_pos_and_size(self,objects):
        #TODO: ver se isto ta bem depois
        aux_h = 0
        aux_w = round(self.WIDTH/len(objects),2)
        i = 1
        for object in objects:
            #verifica se o objeto nao tem size
            if 'size' not in object: #se nao temos de ver o size estado a estado
                for state in object['states']:
                    #verificar se o estado ja tem size
                    if 'size' in state:
                        continue
                    else: #se nao tiver temos deduzir o tamanho
                        img = state['images'][0] if 'images' in state else state['image']
                        state['size'] = self.get_image_size(img)
            #now verify the position
            if 'position' not in object:
                if 'size' in object:
                    size_w = object['size'][0]
                    size_h = object['size'][1]
                    w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                    h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                    object['position'] = (w,h)
                else: #temos de ver a posiçao estado a estado
                    for state in object['states']:
                        if 'position' not in state:
                            size_w = state['size'][0]
                            size_h = state['size'][1]
                            w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                            h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                            state['position'] = (w,h)
            i+=1
        return objects

    def decode_python_type(self,python_type,value):
        if python_type == str:
            return 'Texto'
        elif python_type == tuple and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            return 'Posição'
        elif python_type == list and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            return 'Tamanho'
        elif python_type == list and all(isinstance(element, str) for element in value):
            return 'Lista_Texto'
        elif python_type == int or python_type == float:
            return 'Número'
        elif python_type == dict:
            #TODO: Objeto/Som/Estado/Desafio/Transição/Cenário/Evento
            return 'Objeto' 
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
        '''er_parameters : param_titulo "," param_tamanho "," param_cenarios "," param_eventos "," param_transicoes'''
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
        '''import_obj : "importa Objeto." ID'''
        children = import_obj.children
        id = children[0].value
        obj = parse_obj(id,current_folder)
        self.dict_imports['objects'][id] = obj

        for state in obj['states']:
            state_id = state['id']
            if not self.verify_id_exist(state_id):
                self.dict_vars[state_id] = {
                    "type" : "Estado",
                    "value" : state
            }
            
        if 'sounds' in obj:
            for sound in obj['sounds']:
                sound_id = sound['id']
                if not self.verify_id_exist(sound_id):
                    self.dict_vars[sound_id] = {
                        "type" : "Som",
                        "value" : sound
                    }

    def decls(self,vars):
        '''decls : (var|decl)+'''
        children = vars.children
        for child in children:
            self.visit(child)

    def adiciona_estado(self,adiciona_estado):
        '''adiciona_estado : "." ID         ".adiciona_Estado" "(" estado ")"'''
        children = adiciona_estado.children
        id = children[0].value

        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Objeto' or type == 'Cenário':
                estado = self.visit(children[1])
                self.dict_vars[id]['value']['states'].append(estado)
            else:
                print(f"ERROR: Não é possível adicionar um 'Estado' a uma variável do tipo {type}, apenas a variáveis do tipo 'Objeto' e 'Cenário'.",file=sys.stderr)
                exit(-1)
        else:
            print(f'ERROR: A variável {id} não foi inicializada.',file=sys.stderr)
            exit(-1)

    def adiciona_som(self,adiciona_som):
        '''adiciona_som    : "." ID         ".adiciona_Som"    "(" som    ")"'''
        children = adiciona_som.children
        id = children[0].value

        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Objeto' or type == 'Cenário':
                som = self.visit(children[1])
                if 'sounds' in self.dict_vars[id]['value']:
                    self.dict_vars[id]['value']['sounds'].append(som)
                else:
                    self.dict_vars[id]['value']['sounds'] = [som]
            else:
                print(f"ERROR: Não é possível adicionar um 'Som' a uma variável do tipo {type}, apenas a variáveis do tipo 'Objeto' e 'Cenário'.",file=sys.stderr)
                exit(-1)
        else:
            print(f'ERROR: A variável {id} não foi inicializada.',file=sys.stderr)
            exit(-1)


    def adiciona_objeto(self,adiciona_objeto):
        '''adiciona_objeto : "." cenario_id ".adiciona_Objeto" "(" objeto ")"'''
        children = adiciona_objeto.children
        id = self.visit(children[0])
        if id in self.dict_vars:
            type = self.dict_vars[id]['type']
            if type == 'Objeto':
                objeto = self.visit(children[1])
                self.dict_vars[id]['value']['objects'].append(objeto)
            else:
                print(f"ERROR: Não é possível adicionar um 'Objeto' a uma variável do tipo {type}, apenas a variáveis do tipo 'Cenário'.",file=sys.stderr)
                exit(-1)
        else:
            print(f'ERROR: A variável {id} não foi inicializada.',file=sys.stderr)

    def var(self,var):
        '''var : VAR "=" value'''
        children = var.children
        var_name = children[0].value[1:]
        test = self.visit(children[1])
        #print(test)
        (type,value) = test

        #Colocar id nao for tipo primário:
        if type in ["Estado", "Som", "Objeto", "Cenário", "Transição", "Desafio", "Evento"]:
            value["id"] = var_name

        if not self.verify_id_exist(var_name):
            self.dict_vars[var_name] = {
                'type' : type,
                'value' : value
            }

    def value(self,val):
        '''value : ID|python_call|lista_texto_constructor|texto_constructor|tamanho_constructor|posicao_constructor|numero_constructor|estado_constructor|objeto_constructor|objeto_imported|som_constructor|cenario_constructor|evento_constructor|desafio_constructor|transicao_constructor'''
        child = val.children[0]
        #TODO: ver se é ID
        if isinstance(child, Token):
            id = child.value
            if id in self.dict_vars:
                type = self.dict_vars[id]['type']
                if type in ["Estado", "Som", "Objeto", "Cenário", "Transição", "Desafio", "Evento"]:
                    value = dict(self.dict_vars[id]['value'])
                else:
                    value = self.dict_vars[id]['value']
                return (type,value)
            else:
                print(f'ERROR: A variável {id} não foi inicializada.',file=sys.stderr)
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

    def lista_texto(self,lista_texto):
        '''lista_texto : lista_texto_arg|lista_texto_constructor|lista_texto_python_call'''
        child = lista_texto.children[0]
        if child.data == 'lista_texto_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def lista_texto_arg(self,lista_texto_arg):
        '''lista_texto_arg : ID'''
        child = lista_texto_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Lista_Texto'):
            return self.dict_vars[id]['value'] 

    def lista_texto_python_call(self,lista_texto_python_call):
        '''lista_texto_python_call : python_call'''
        child = lista_texto_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Lista_Texto':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Lista_Texto, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def lista_texto_constructor(self,lista_texto_constructor):
        '''lista_texto_constructor : "[" texto ("," texto)* "]"'''
        children = lista_texto_constructor.children
        lista = []
        for child in children:
            lista.append(self.visit(child))
        return ("Lista_Texto",lista)

    def texto(self,texto):
        '''texto : texto_arg|texto_constructor|texto_python_call'''
        child = texto.children[0]
        if child.data == 'texto_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def texto_arg(self,texto_arg):
        '''texto_arg : ID'''
        child = texto_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Texto'):
            return self.dict_vars[id]['value'] 

    def texto_python_call(self,texto_python_call):
        '''texto_python_call : python_call'''
        child = texto_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Texto':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Texto, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def texto_constructor(self,texto_constructor):
        '''texto_constructor : TEXTO'''
        children = texto_constructor.children
        texto = children[0].value[1:-1]
        return ("Texto",texto) #(type,value)

    def tamanho(self,tamanho):
        '''tamanho : tamanho_arg|tamanho_constructor|tamanho_python_call'''
        child = tamanho.children[0]
        if child.data == 'tamanho_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def tamanho_arg(self,tamanho_arg):
        '''tamanho_arg : ID'''
        child = tamanho_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Tamanho'):
            return self.dict_vars[id]['value'] 

    def tamanho_python_call(self,tamanho_python_call):
        '''tamanho_python_call : python_call'''
        child = tamanho_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Tamanho':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Tamanho, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def tamanho_constructor(self,tamanho_constructor):
        '''tamanho_constructor : "[" NUM "," NUM "]"'''
        children = tamanho_constructor.children
        w = self.visit(children[0])
        h = self.visit(children[1])
        return("Tamanho",(w,h)) #(type,value)

    def posicao(self,posicao):
        '''posicao : posicao_arg|posicao_constructor|posicao_python_call'''
        child = posicao.children[0]
        if child.data == 'posicao_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def posicao_arg(self,posicao_arg):
        '''posicao_arg : ID'''
        child = posicao_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Posição'):
            return self.dict_vars[id]['value'] 

    def posicao_python_call(self,posicao_python_call):
        '''posicao_python_call : python_call'''
        child = posicao_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Posição':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Python do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def posicao_constructor(self,posicao_constructor):
        '''posicao_constructor : "(" numero "," numero ")"'''
        children = posicao_constructor.children
        x = self.visit(children[0])
        y = self.visit(children[1])
        return ("Posição",(x,y))

    def numero(self,numero):
        '''numero : numero_arg|numero_constructor|numero_python_call'''
        child = numero.children[0]
        if child.data == 'numero_constructor':
            (_,value) = self.visit(child)
        else:
            value = self.visit(child)
        return value

    def numero_arg(self,numero_arg):
        '''numero_arg : ID'''
        child = numero_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Número'):
            return self.dict_vars[id]['value'] 

    def numero_python_call(self,numero_python_call):
        '''numero_python_call : python_call'''
        child = numero_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Número':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Número do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def numero_constructor(self,numero_constructor):
        '''numero_constructor : NUM'''
        children = numero_constructor.children
        num = int(children[0].value)
        return("Número",num) #(type,value)

    def estados(self,estados):
        '''estados : "[" estado ("," estado)* "]"'''
        children = estados.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def estado(self,estado):
        '''estado : estado_arg|estado_constructor_id|estado_python_call'''
        child = estado.children[0]
        value = self.visit(child)
        return value

    def estado_arg(self,estado_arg):
        '''estado_arg : ID'''
        child = estado_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Estado'):
            return self.dict_vars[id]['value'] 

    def estado_id(self,estado_id):
        '''estado_id : ID'''
        child = estado_id.children[0]
        id = child.value
        #TODO: ver isto melhor do none depois
        if id == "none":
            return id
        if self.verify_arg(id,'Estado'):
            return id

    def estado_python_call(self,estado_python_call):
        '''estado_python_call : python_call'''
        child = estado_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Estado':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Estado do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def estado_constructor(self,estado_constructor):
        '''estado_constructor : estado_estatico|estado_dinamico'''
        child = estado_constructor.children[0]
        return self.visit(child)
    
    def estado_constructor_id(self,estado_constructor):
        '''estado_constructor_id : estado_estatico_id|estado_dinamico_id'''
        child = estado_constructor.children[0]
        return self.visit(child)

    def estado_estatico(self,estado_estatico):
        '''estado_estatico : "Estado.Estático" "(" param_imagem ("," param_posicao)? ("," param_tamanho)? ")"'''
        children = estado_estatico.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value
        return ("Estado",value)

    def estado_dinamico(self,estado_dinamico):
        '''estado_dinamico : "Estado.Dinâmico" "(" param_imagens "," param_repeticoes "," param_time_sprite ("," param_posicao)? ("," param_tamanho)? ")"'''
        children = estado_dinamico.children
        value = {}
        for child in children:
            (param,param_value) = self.visit(child)
            value[param] = param_value
        return ("Estado",value)
    
    def estado_estatico_id(self,estado_estatico_id):
        '''estado_estatico_id : "Estado.Estático." ID "(" param_imagem ("," param_posicao)? ("," param_tamanho)? ")"'''
        children = estado_estatico_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                "type" : "Estado",
                "value" : value
            }

        return value

    def estado_dinamico_id(self,estado_dinamico_id):
        '''estado_dinamico_id : "Estado.Dinâmico." ID "(" param_imagens "," param_repeticoes "," param_time_sprite ("," param_posicao)? ("," param_tamanho)? ")"'''
        children = estado_dinamico_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        for child in children[1:]:
            (param,param_value) = self.visit(child)
            value[param] = param_value

        self.dict_vars[id] = {
            "type" : "Estado",
            "value" : value
        }

        return value

    def sons(self,sons):
        '''sons : "[" som ("," som)* "]"'''
        children = sons.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def som(self,som):
        '''som : som_arg|som_constructor_id|som_python_call'''
        child = som.children[0]
        value = self.visit(child)
        return value

    def som_arg(self,som_arg):
        '''som_arg : ID'''
        child = som_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Som'):
            return self.dict_vars[id]['value'] 

    def som_id(self,som_id):
        '''som_id : ID'''
        child = som_id.children[0]
        id = child.value
        if self.verify_arg(id,'Som'):
            return id
        

    def som_python_call(self,som_python_call):
        '''som_python_call : python_call'''
        child = som_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Som':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Som do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def som_constructor(self,som_constructor):
        '''som_constructor : "Som" "(" param_fonte ")"'''
        child = som_constructor.children[0]
        value = {}
        (param,param_value) = self.visit(child)
        value[param] = param_value
        return ("Som",value) #(type,value)
    
    def som_constructor_id(self,som_constructor_id):
        '''som_constructor_id : "Som." ID "(" param_fonte ")"'''
        children = som_constructor_id.children
        id = children[0].value
        value = {}
        value["id"] = id
        (param,param_value) = self.visit(children[1])
        value[param] = param_value
        return value


    def objetos(self,objetos):
        '''objetos : "[" objeto ("," objeto)* "]"'''
        children = objetos.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def objeto(self,objeto):
        '''objeto : objeto_imported_id|objeto_arg|objeto_constructor_id|objeto_python_call'''
        child = objeto.children[0]
        value = self.visit(child)
        return value

    def objeto_arg(self,objeto_arg):
        '''objeto_arg : ID'''
        child = objeto_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Objeto'):
            return self.dict_vars[id]['value'] 

    def objeto_id(self,objeto_id):
        '''objeto_id : ID'''
        child = objeto_id.children[0]
        id = child.value
        if self.verify_arg(id,'Objeto'):
            return id

    def objeto_python_call(self,objeto_python_call):
        '''objeto_python_call : python_call'''
        child = objeto_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Objeto':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Objeto do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def objeto_constructor(self,objeto_constructor):
        '''objeto_constructor : "Objeto" "(" (param_estado_inicial ",")? param_estados ("," param_posicao)? ("," param_tamanho)? ("," param_sons)? ")"'''
        children = objeto_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        return ("Objeto",value)

    def objeto_imported(self,objeto_imported):
        '''objeto_imported : "Objeto." ID ("(" (param_posicao|param_tamanho|(param_posicao "," param_tamanho)) ")")?'''
        children = objeto_imported.children
        id = children[0].value
        if id in self.dict_imports['objects']:
            object = dict(self.dict_imports['objects'][id])
            other_children = children[1:]
            for child in other_children:
                param,param_value = self.visit(child)
                object[param] = param_value

            return ('Objeto',object)
        else:
           print(f"ERROR: Objeto {id} não importado anteriormente.",file=sys. stderr) 

    def objeto_constructor_id(self,objeto_constructor_id):
        '''objeto_constructor_id : "Objeto." ID "(" (param_estado_inicial ",")? param_estados ("," param_posicao)? ("," param_tamanho)? ("," param_sons)? ")"'''
        children = objeto_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                "type" : "Objeto",
                "value" : value
            }

        return value

    def objeto_imported_id(self,objeto_imported_id):
        '''objeto_imported_id : "Objeto." ID "." ID ("(" (param_posicao|param_tamanho|(param_posicao "," param_tamanho)) ")")?'''
        children = objeto_imported_id.children
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
                    "type" : "Objeto",
                    "value" : object
                }

            return object
        else:
           print(f"ERROR: Objeto {id_import} não importado anteriormente.",file=sys. stderr)
           exit(-1)

    def cenarios(self,cenarios):
        '''cenarios : "[" cenario ("," cenario)* "]"'''
        children = cenarios.children
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
        if self.verify_arg(id,'Cenário'):
            return self.dict_vars[id]['value'] 

    def cenario_id(self,cenario_id):
        '''cenario_id : ID'''
        child = cenario_id.children[0]
        id = child.value
        if self.verify_arg(id,'Cenário'):
            return id
        

    def cenario_python_call(self,cenario_python_call):
        '''cenario_python_call : python_call'''
        child = cenario_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Cenário':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Cenário do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def cenario_constructor(self,cenario_constructor):
        '''cenario_constructor : "Cenário" "(" param_estado_inicial "," param_estados "," param_objetos ("," param_sons)? ")"'''
        children = cenario_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        return ("Cenário",value)
    
    def cenario_constructor_id(self,cenario_constructor_id):
        '''cenario_constructor_id : "Cenário." ID "(" param_estado_inicial "," param_estados "," param_objetos ("," param_sons)? ")"'''
        children = cenario_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Cenário",
                    "value" : value
                }

        return value

    def transicoes(self,transicoes):
        '''transicoes : "[" transicao ("," transicao)* "]"'''
        children = transicoes.children
        result = []
        for child in children:
            result.append(self.visit(child))
        return result

    def transicao(self,transicao):
        '''transicao : transicao_arg|transicao_constructor_id|transicao_python_call'''
        child = transicao.children[0]
        value = self.visit(child)
        return value

    def transicao_arg(self,transicao_arg):
        '''transicao_arg : ID'''
        child = transicao_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Transição'):
            return self.dict_vars[id]['value'] 

    def transicao_id(self,transicao_id):
        '''transicao_id : ID'''
        child = transicao_id.children[0]
        id = child.value
        if self.verify_arg(id,'Transição'):
            return id

    def transicao_python_call(self,transicao_python_call):
        '''transicao_python_call : python_call'''
        child = transicao_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Transição':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Transição do tipo Posição, mas é do tipo {type}.",file=sys. stderr)
            exit(-1)

    def transicao_constructor(self,transicao_constructor):
        '''transicao_constructor : "Transição" "(" param_fundo "," param_musica "," param_historia "," (param_prox_cena|param_prox_trans)")"'''
        children = transicao_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        return ("Transição",value)
    
    def transicao_constructor_id(self,transicao_constructor_id):
        '''transicao_constructor_id : "Transição." ID "(" param_fundo "," param_musica "," param_historia "," (param_prox_cena|param_prox_trans)")"'''
        children = transicao_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Transição",
                    "value" : value
                }
        
        return value

    def desafio(self,desafio):
        '''desafio : desafio_arg|desafio_constructor_id|desafio_python_call'''
        child = desafio.children[0]
        value = self.visit(child)
        return value

    def desafio_arg(self,desafio_arg):
        '''desafio_arg : ID'''
        child = desafio_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Desafio'):
            return self.dict_vars[id]['value'] 

    def desafio_python_call(self,desafio_python_call):
        '''desafio_python_call : python_call'''
        child = desafio_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Desafio':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Desafio do tipo Posição, mas é do tipo {type}.",file=sys. stderr)

    def desafio_constructor(self,desafio_constructor):
        '''desafio_constructor : desafio_pergunta|desafio_arrasta|desafio_escolha_multipla|desafio_conexao|desafio_sequencia|desafio_puzzle|desafio_slidepuzzle|desafio_socket'''
        child = desafio_constructor.children[0]
        return self.visit(child)
    
    def desafio_constructor_id(self,desafio_constructor_id):
        '''desafio_constructor_id : desafio_pergunta_id|desafio_arrasta_id|desafio_escolha_multipla_id|desafio_conexao_id|desafio_sequencia_id|desafio_puzzle_id|desafio_slidepuzzle_id|desafio_socket_id'''
        child = desafio_constructor_id.children[0]
        return self.visit(child)

    def desafio_pergunta(self,desafio_pergunta):
        '''desafio_pergunta : "Desafio.Pergunta" "(" param_pergunta "," param_resposta "," param_acerto "," param_falha ")"'''
        children = desafio_pergunta.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'QUESTION'

        return ("Desafio",value)
    
    def desafio_pergunta_id(self,desafio_pergunta_id):
        '''desafio_pergunta_id : "Desafio.Pergunta." ID "(" param_pergunta "," param_resposta "," param_acerto "," param_falha ")"'''
        children = desafio_pergunta_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "QUESTION"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }

        return value

    def desafio_arrasta(self,desafio_arrasta):
        '''desafio_arrasta : "Desafio.Arrasta" "(" param_objeto "," param_objeto_gatilho "," param_acerto "," param_falha ")"'''
        children = desafio_arrasta.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'MOVE_OBJECT'

        return ("Desafio",value)
    
    def desafio_arrasta_id(self,desafio_arrasta_id):
        '''desafio_arrasta_id : "Desafio.Arrasta." ID "(" param_objeto "," param_objeto_gatilho "," param_acerto "," param_falha ")"'''
        children = desafio_arrasta_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "MOVE_OBJECT"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def desafio_escolha_multipla(self,desafio_escolha_multipla):
        '''desafio_escolha_multipla : "Desafio.Escolha_Múltipla" "(" param_pergunta "," param_escolhas "," param_resposta "," param_acerto "," param_falha ")"'''
        children = desafio_escolha_multipla.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'MULTIPLE_CHOICE'

        return ("Desafio",value)
    
    def desafio_escolha_multipla_id(self,desafio_escolha_multipla_id):
        '''desafio_escolha_multipla_id : "Desafio.Escolha_Múltipla." ID "(" param_pergunta "," param_escolhas "," param_resposta "," param_acerto "," param_falha ")"'''
        children = desafio_escolha_multipla_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "MULTIPLE_CHOICE"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def desafio_conexao(self,desafio_conexao):
        '''desafio_conexao : "Desafio.Conexão" "(" param_pergunta "," param_lista1 "," param_lista2 "," param_acerto "," param_falha ")"'''
        children = desafio_conexao.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'CONNECTIONS'

        return ("Desafio",value)
    
    def desafio_conexao_id(self,desafio_conexao_id):
        '''desafio_conexao_id : "Desafio.Conexão." ID "(" param_pergunta "," param_lista1 "," param_lista2 "," param_acerto "," param_falha ")"'''
        children = desafio_conexao_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "CONNECTIONS"
        
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def desafio_sequencia(self,desafio_sequencia):
        '''desafio_sequencia : "Desafio.Sequência" "(" param_pergunta "," param_sequencia "," param_acerto "," param_falha ")"'''
        children = desafio_sequencia.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'SEQUENCE'

        return ("Desafio",value)
    
    def desafio_sequencia_id(self,desafio_sequencia_id):
        '''desafio_sequencia_id : "Desafio.Sequência." ID "(" param_pergunta "," param_sequencia "," param_acerto "," param_falha ")"'''
        children = desafio_sequencia_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "SEQUENCE"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def desafio_puzzle(self,desafio_puzzle):
        '''desafio_puzzle : "Desafio.Puzzle" "(" param_imagem "," param_acerto ")"'''
        children = desafio_puzzle.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'PUZZLE'

        return ("Desafio",value)

    def desafio_puzzle_id(self,desafio_puzzle_id):
        '''desafio_puzzle_id : "Desafio.Puzzle." ID "(" param_imagem "," param_acerto ")"'''
        children = desafio_puzzle_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "PUZZLE"
        
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def desafio_slidepuzzle(self,desafio_slidepuzzle):
        '''desafio_slidepuzzle : "Desafio.SlidePuzzle" "(" param_imagem "," param_acerto ")"'''
        children = desafio_slidepuzzle.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'SLIDEPUZZLE'

        return ("Desafio",value)
    
    def desafio_slidepuzzle_id(self,desafio_slidepuzzle_id):
        '''desafio_slidepuzzle_id : "Desafio.SlidePuzzle." ID "(" param_imagem "," param_acerto ")"'''
        children = desafio_slidepuzzle_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "SLIDEPUZZLE"

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def desafio_socket(self,desafio_socket):
        '''desafio_socket : "Desafio.Socket" "(" param_host "," param_port "," param_mensagem "," param_acerto "," param_falha ")"'''
        children = desafio_socket.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value
        
        value['type'] = 'SOCKET_CONNECTION'

        return ("Desafio",value)
    
    def desafio_socket_id(self,desafio_socket_id):
        '''desafio_socket_id : "Desafio.Socket." ID "(" param_host "," param_port "," param_mensagem "," param_acerto "," param_falha ")"'''
        children = desafio_socket_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        value["type"] = "SOCKET_CONNECTION"
        
        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Desafio",
                    "value" : value
                }
        
        return value

    def eventos(self,eventos):
        '''eventos : "[" evento ("," evento)* "]"'''
        children = eventos.children
        value = []
        for child in children:
            value.append(self.visit(child))
        return value

    def evento(self,evento):
        '''evento : evento_arg|evento_constructor_id|evento_python_call'''
        child = evento.children[0]
        value = self.visit(child)
        return value

    def evento_arg(self,evento_arg):
        '''evento_arg : ID'''
        child = evento_arg.children[0]
        id = child.value
        if self.verify_arg(id,'Evento'):
            return self.dict_vars[id]['value'] 

    def evento_id(self,evento_id):
        '''evento_id : ID'''
        child = evento_id.children[0]
        id = child.value
        if self.verify_arg(id,'Evento'):
            return id

    def evento_python_call(self,evento_python_call):
        '''evento_python_call : python_call'''
        child = evento_python_call.children[0]
        (type,value) = self.visit(child)
        if type == 'Evento':
            return value
        else:
            print(f"ERROR: Esperado uma variável vinda do Evento do tipo Posição, mas é do tipo {type}.",file=sys. stderr)

    def evento_constructor(self,evento_constructor):
        '''evento_constructor : "Evento" "(" (param_se ",")? param_entao ("," param_repeticoes)? ")"'''
        children = evento_constructor.children
        value = {}
        for child in children:
            param,param_value = self.visit(child)
            value[param] = param_value

        return ("Evento",value)
    
    def evento_constructor_id(self,evento_constructor_id):
        '''evento_constructor_id : "Evento." ID "(" (param_se ",")? param_entao ("," param_repeticoes)? ")"'''
        children = evento_constructor_id.children
        id = children[0]
        value = {}
        value["id"] = id
        for child in children[1:]:
            param,param_value = self.visit(child)
            value[param] = param_value

        if not self.verify_id_exist(id):
            self.dict_vars[id] = {
                    "type" : "Evento",
                    "value" : value
                }    
        
        return value

    def param_cenarios(self,param_cenarios):
        '''param_cenarios : "cenários" "=" cenarios'''
        child = param_cenarios.children[0]
        value = self.visit(child)
        return ('scenarios',value)


    def param_entao(self,param_entao):
        '''param_entao : "então" "=" poscondicoes'''
        child = param_entao.children[0]
        value = self.visit(child)
        return ('posconditions',value)

    def param_estado_inicial(self,param_estado_inicial):
        '''param_estado_inicial : "estado_inicial" "=" estado_arg'''
        child = param_estado_inicial.children[0]
        value = self.visit(child)
        return ('initial_state',value)

    def param_estados(self,param_estados):
        '''param_estados : "estados" "=" estados'''
        child = param_estados.children[0]
        value = self.visit(child)
        return ('states',value)

    def param_escolhas(self,param_escolhas):
        '''param_escolhas : "escolhas" "=" lista_texto'''
        child = param_escolhas.children[0]
        value = self.visit(child)
        return ('choices',value)

    def param_eventos(self,param_eventos):
        '''param_eventos : "eventos" "=" eventos'''
        child = param_eventos.children[0]
        value = self.visit(child)
        return ('events',value)

    def param_falha(self,param_falha):
        '''param_falha : "falha" "=" evento_arg'''
        child = param_falha.children[0]
        value = self.visit(child)
        return ('fail',value)

    def param_fonte(self,param_fonte):
        '''param_fonte : "fonte" "=" texto'''
        child = param_fonte.children[0]
        value = self.visit(child)

        try:
            file = open(value)
            src = os.path.realpath(file.name)
            file.close()
        except:
            print(f"ERROR: Ficheiro de som '{value}' não encontrado!",file=sys.stderr)
            exit(-1)

        return ('source',src) #(param,value)

    def param_fundo(self,param_fundo):
        '''param_fundo : "fundo" "=" estado'''
        child = param_fundo.children[0]
        value = self.visit(child)
        return ('background',value)

    def param_historia(self,param_historia):
        '''param_historia : "história" "=" texto'''
        child = param_historia.children[0]
        value = self.visit(child)
        return ('story',value)

    def param_host(self,param_host):
        '''param_host : "host" "=" texto'''
        child = param_host.children[0]
        value = self.visit(child)
        return ('host',value)

    def param_imagem(self,param_imagem):
        '''param_imagem : "imagem" "=" texto'''
        child = param_imagem.children[0]
        value = self.visit(child)

        try:
            file = open(value)
            src = os.path.realpath(file.name)
            file.close()
        except:
            print(f"ERROR: Ficheiro de imagem '{value}' não encontrado!",file=sys.stderr)
            exit(-1)

        return ('image',src)

    def param_imagens(self,param_imagens):
        '''param_imagens : "imagens" "=" lista_texto'''
        child = param_imagens.children[0]
        values = self.visit(child)
        
        srcs = []
        for value in values:
            try:
                file = open(value)
                src = os.path.realpath(file.name)
                file.close()
                srcs.append(src)
            except:
                print(f"ERROR: Ficheiro de imagem '{value}' não encontrado!",file=sys.stderr)
                exit(-1)

        return ('images',srcs)

    def param_lista1(self,param_lista1):
        '''param_lista1 : "lista1" "=" lista_texto'''
        child = param_lista1.children[0]
        value = self.visit(child)
        return ('list1',value)

    def param_lista2(self,param_lista2):
        '''param_lista2 : "lista2" "=" lista_texto'''
        child = param_lista2.children[0]
        value = self.visit(child)
        return ('list2',value)

    def param_mensagem(self,param_mensagem):
        '''param_mensagem : "mensagem" "=" texto'''
        child = param_mensagem.children[0]
        value = self.visit(child)
        return ('message',value)

    def param_musica(self,param_musica):
        '''param_musica : "música" "=" som'''
        child = param_musica.children[0]
        value = self.visit(child)
        return ('music',value)

    def param_objeto(self,param_objeto):
        '''param_objeto : "objeto" "=" objeto_id'''
        child = param_objeto.children[0]
        value = self.visit(child)
        return ('object',value)
    
    def param_objeto_gatilho(self,param_objeto_gatilho):
        '''param_objeto_gatilho : "objeto" "=" objeto_id'''
        child = param_objeto_gatilho.children[0]
        value = self.visit(child)
        return ('object_trigger',value)

    def param_objetos(self,param_objetos):
        '''param_objetos : "objetos" "=" objetos'''
        child = param_objetos.children[0]
        value = self.visit(child)

        return ('objects',value)

    def param_pergunta(self,param_pergunta):
        '''param_pergunta : "pergunta" "=" texto'''
        child = param_pergunta.children[0]
        value = self.visit(child)
        return ('question',value)

    def param_port(self,param_port):
        '''param_port : "port" "=" numero'''
        child = param_port.children[0]
        value = self.visit(child)
        return ('port',value)

    def param_posicao(self,param_posicao):
        '''param_posicao : "posição" "=" posição'''
        child = param_posicao.children[0]
        value = self.visit(child)
        return ('position',value)

    def param_prox_cena(self,param_prox_cena):
        '''param_prox_cena : "próxima_cena" "=" cenario_id'''
        child = param_prox_cena.children[0]
        value = self.visit(child)
        return ('next_scenario',value)

    def param_prox_trans(self,param_prox_trans):
        '''param_prox_trans : "próxima_transição" "=" transicao_id'''
        child = param_prox_trans.children[0]
        value = self.visit(child)
        return ('next_transition',value)

    def param_se(self,param_se):
        '''param_se : "se" "=" precondicoes'''
        child = param_se.children[0]
        value = self.visit(child)
        return ('preconditions',value)

    def param_sequencia(self,param_sequencia):
        '''param_sequencia : "sequência" "=" lista_texto'''
        child = param_sequencia.children[0]
        value = self.visit(child)
        return ('sequence',value)

    def param_sons(self,param_sons):
        '''param_sons : "sons" "=" sons'''
        child = param_sons.children[0]
        value = self.visit(child)
        return ('sounds',value)
    
    def param_sucesso(self,param_sucesso):
        '''param_sucesso : "sucesso" "=" evento_arg'''
        child = param_sucesso.children[0]
        value = self.visit(child)
        return ('sucess',value)

    def param_repeticoes(self,param_repeticoes):
        '''param_repeticoes : "repetições" "=" numero'''
        child = param_repeticoes.children[0]
        value = self.visit(child)
        return ('repetitions',value)

    def param_resposta(self,param_resposta):
        '''param_resposta : "resposta" "=" texto'''
        child = param_resposta.children[0]
        value = self.visit(child)
        return ('answer',value)

    def param_tamanho(self,param_tamanho):
        '''param_tamanho : "tamanho" "=" tamanho'''
        child = param_tamanho.children[0]
        value = self.visit(child)
        return ('size',value)

    def param_time_sprite(self,param_time_sprite):
        '''param_time_sprite : "time_sprite" "=" numero'''
        child = param_time_sprite.children[0]
        value = self.visit(child)
        return ('time_sprite',value)

    def param_titulo(self,param_titulo):
        '''param_titulo : "título" "=" texto'''
        child = param_titulo.children[0]
        value = self.visit(child)
        return ('title',value)

    def param_transicoes(self,param_transicoes):
        '''param_transicoes : "transições" "=" (transicoes|"[""]")'''
        children = param_transicoes.children
        if len(children) > 0:
            value = self.visit(children[0])
        else:
            value = []
        return ('transitions',value)

    def precondicoes(self,precondicoes):
        '''precondicoes : precondicao|preconds_e|preconds_ou|preconds_nao|preconds_grupo'''
        child = precondicoes.children[0]
        if child.data == 'precondicao':
            return {
                "var" : self.visit(child)
            }
        else:
            return self.visit(child)

    def preconds_e(self,preconds_e):
        '''preconds_e : precondicoes "e" precondicoes'''
        children = preconds_e.children
        left = self.visit(children[0])
        right = self.visit(children[1])
        result = {
            "operator" : "AND",
            "left" : left,
            "right" : right

        }
        return result

    def preconds_ou(self,preconds_ou):
        '''preconds_ou : precondicoes "ou" precondicoes'''
        children = preconds_ou.children
        left = self.visit(children[0])
        right = self.visit(children[1])
        result = {
            "operator" : "OR",
            "left" : left,
            "right" : right

        }
        return result

    def preconds_nao(self,preconds_nao):
        '''preconds_nao : "não" precondicoes'''
        child = preconds_nao.children[0]
        left = self.visit(child)
        right = None
        result = {
            "operator" : "NOT",
            "left" : left,
            "right" : right

        }
        return result

    def preconds_grupo(self,preconds_grupo):
        '''preconds_grupo : "(" precondicoes ")"'''
        child = preconds_grupo.children[0]
        return self.visit(child)

    def precondicao(self,precondicao):
        '''precondicao : precond_clique_obj | precond_clique_nao_obj | precond_obj_esta_est | precond_ev_ja_aconteceu | precond_obj_uso | precond_depois_tempo'''
        child = precondicao.children[0]
        return self.visit(child)

    def precond_clique_obj(self,precond_clique_obj):
        '''precond_clique_obj : "clique" objeto_id'''
        children = precond_clique_obj.children
        
        return {
            'type' : 'CLICKED_OBJECT',
            'object' : self.visit(children[0]),
            }

    def precond_clique_nao_obj(self,precond_clique_nao_obj):
        '''precond_clique_nao_obj : "clique não" objeto_id'''
        children = precond_clique_nao_obj.children
        return {
            'type' : 'CLICKED_NOT_OBJECT',
            'object' : self.visit(children[0]),
            }

    def precond_obj_esta_est(self,precond_obj_esta_est):
        '''precond_obj_esta_est : objeto_id "está" estado_id'''
        children = precond_obj_esta_est.children

        object_id = self.visit(children[0])
        state_id = self.visit(children[1])

        #TODO: verificar se state faz parte do obj (SO FALTA TESTAR)

        found = False
        for state in self.dict_vars[object_id]['value']['states']:
            if state['id'] == state_id:
                found = True
                break
        
        if not found:
            print(f'ERROR: Na pré condição "{object_id} está {state_id}", o {state_id} não é um \'Estado\' do \'Objeto\' {object_id}.',file=sys.stderr)
            exit(-1)
        
        return {
            'type' : 'WHEN_OBJECT_IS_STATE',
            'object' : object_id,
            'state' : state_id
        }

    def precond_ev_ja_aconteceu(self,precond_ev_ja_aconteceu):
        '''precond_ev_ja_aconteceu : evento_id "já aconteceu""'''
        children = precond_ev_ja_aconteceu.children

        return {
            'type' : 'AFTER_EVENT',
            'event' : self.visit(children[0])
            }

    def precond_obj_uso(self,precond_obj_uso):
        '''precond_obj_uso : objeto_id "está em uso"'''
        children = precond_obj_uso.children
        return {
                'type' : 'ITEM_IS_IN_USE',
                'item' : self.visit(children[0])
            }
    def precond_depois_tempo(self, precond_depois_tempo):
        '''precond_depois_tempo : "já tiver passado" numero "segundos"'''
        children = precond_depois_tempo.children
        return {
            'type' : 'AFTER_TIME',
            'time' : self.visit(children[0]) * 1000 #segundos -> milisegundos
        }

    def poscondicoes(self,poscondicoes):
        '''poscondicoes : poscondicao ("e" poscondicao)*'''
        children = poscondicoes.children
        posconds = []
        for child in children:
            posconds.append(self.visit(child))

        return posconds


    def poscondicao(self,poscondicao):
        '''poscondicao : poscond_obj_muda_est|poscond_obj_vai_inv|poscond_fim_de_jogo|poscond_mostra_msg|poscond_obj_muda_tam|poscond_obj_muda_pos|poscond_muda_cena|poscond_remove_obj|poscond_toca_som|poscond_comeca_des|poscond_trans'''
        children = poscondicao.children
        return self.visit(children[0])

    def poscond_obj_muda_est(self,poscond_obj_muda_est):
        '''poscond_obj_muda_est : objeto_id "muda para" estado_id'''
        children = poscond_obj_muda_est.children

        object_id = self.visit(children[0])
        state_id = self.visit(children[1])
        
        #TODO: verificar se estado_id está em objeto (SO FALTA TESTAR)
        found = False if state_id != "none" else True #TODO: ver melhor isto do none
        if not found:
            for state in self.dict_vars[object_id]['value']['states']:
                if state['id'] == state_id:
                    found = True
                    break
        
        if not found:
            print(f'ERROR: Na pós condição "{object_id} muda para {state_id}", o {state_id} não é um \'Estado\' do \'Objeto\' {object_id}.',file=sys.stderr)
            exit(-1)

        return {
            'type' : 'OBJ_CHANGE_STATE',
            'object' : object_id,
            'state' : state_id
            }

    def poscond_obj_vai_inv(self,poscond_obj_vai_inv):
        '''poscond_obj_vai_inv : objeto_id "vai para o inventário"'''
        children = poscond_obj_vai_inv.children
        return {
            'type' : 'OBJ_PUT_INVENTORY',
            'object' : self.visit(children[0])
            }

    def poscond_fim_de_jogo(self,poscond_fim_de_jogo):
        '''poscond_fim_de_jogo : "fim de jogo"'''
        return {
            'type' : 'END_GAME',
            }

    def poscond_mostra_msg(self,poscond_mostra_msg):
        '''poscond_mostra_msg : "mostra mensagem" text "em" posicao'''
        children = poscond_mostra_msg.children
        return {
            'type' : 'SHOW_MESSAGE',
            'message' : self.visit(children[0]),
            'position' : self.visit(children[1])
            }

    def poscond_obj_muda_tam(self,poscond_obj_muda_tam):
        '''poscond_obj_muda_tam : objeto_id "muda tamanho para" tamanho'''
        children = poscond_obj_muda_tam.children
        return {
                'type' : 'OBJ_CHANGE_SIZE',
                'object' : self.visit(children[0]),
                'size' : self.visit(children[1]),
            }

    def poscond_obj_muda_pos(self,poscond_obj_muda_pos):
        '''poscond_obj_muda_pos : objeto_id "muda posição para" posicao'''
        children = poscond_obj_muda_pos.children
        return {
                'type' : 'OBJ_CHANGE_POSITION',
                'object' : self.visit(children[0]),
                'position' : self.visit(children[1]),
            }

    def poscond_muda_cena(self,poscond_muda_cena):
        '''poscond_muda_cena : "muda para cena" cenario_id'''
        children = poscond_muda_cena.children
        return {
                'type' : 'CHANGE_SCENARIO',
                'scenario' : self.visit(children[0]),
            }

    def poscond_remove_obj(self,poscond_remove_obj):
        '''poscond_remove_obj : objeto_id "é removid" ("o"|"a")'''
        children = poscond_remove_obj.children
        return {
                'type' : 'DELETE_ITEM',
                'item' : self.visit(children[0])
            }

    def poscond_toca_som(self,poscond_toca_som):
        '''poscond_toca_som : "toca" som_id "do" ID'''
        children = poscond_toca_som.children


        sound_id = self.visit(children[0])
        source_id = children[1].value

        if source_id in self.dict_vars:
            source_type = self.dict_vars[source_id]['type']
            if source_type == 'Objeto' or source_type == 'Cenário':
                found = False
                if 'sounds' in self.dict_vars[source_id]['value']:
                    for sound in self.dict_vars[source_id]['value']['sounds']:
                        if sound['id'] == sound_id:
                            found = True
                            break
                
                if not found:
                    print(f'ERROR: Na pós condição "toca {sound_id} do {source_id}", o {sound_id} não é um \'Som\' do \'{source_type}\' {source_id}.',file=sys.stderr)
                    exit(-1)
                
            else:
                print(f"ERROR: Esperado uma variável do tipo Objeto ou Cenário, mas a variável {source_id} é do tipo {source_type}.",file=sys.stderr)
                exit(-1)
        else:
            print(f"ERROR: Variável {source_id} não foi inicializada anteriormente.",file=sys.stderr)
            exit(-1)

        if source_type == 'Objeto':
            source_type = 'Object'
        elif source_type == 'Cenário':
            source_type = 'Scenario'

        return {
                'type' : 'PLAY_SOUND',
                'sound' : sound_id,
                'source_id' : source_id,
                'source_type' : source_type
            }

    def poscond_comeca_des(self,poscond_comeca_des):
        '''poscond_comeca_des : "começa desafio" desafio_arg'''
        children = poscond_comeca_des.children
        return self.visit(children[0])

    def poscond_trans(self,poscond_trans):
        '''poscond_trans : "transição" transicao_arg'''
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