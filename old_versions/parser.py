#!/usr/bin/python3
from lark.visitors import Interpreter
from lark import Lark
import json
import sys
import argparse
import os
import ast
from PIL import Image
from .obj_parser import parse_obj

current_folder = os.path.dirname(__file__)

def parser_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL Parser')
    parser.add_argument('--output','-o'            ,type=str, nargs=1,required=False                                , help='Output file')
    parser.add_argument('--input','-i'             ,type=str, nargs=1,required=True                                , help='Input file')
    parser.add_argument('--grammar_erplpro','-gmpro' ,action='store_true'                                      , help='Grammar ERPL Pro' )
    parser.add_argument('--args','-args'           ,nargs='+'                                                , help='Args')
    return parser.parse_args()

class Interpreter(Interpreter):

    def __init__(self,args):
        self.escape_room = {
            'map' : {},
            'events' : {},
            'sounds' : {},
            'transitions' : {}
        }
        self.challenges = {}
        self.argsn = args
        self.args = {}
        self.locals_python = {}
        self.globals_python = {}
        self.namespace = {}
        self.WIDTH = 0
        self.HEIGHT = 0
        self.imports = {
            'objects' : {}
        }

    def get_image_size(self,path_imagem):
        try:
            with Image.open(path_imagem) as img:
                largura, altura = img.size
                return largura, altura
        except IOError:
            raise Exception("Não foi possível abrir a imagem em", path_imagem)
            return None


    def verify_pos_and_size(self,objects):
        aux_h = 0
        aux_w = round(self.WIDTH/len(objects),2)
        i = 1
        for object in objects:
            #verifica se o objeto nao tem size
            if 'size' not in objects[object]: #se nao temos de ver o size estado a estado
                for state in objects[object]['states']:
                    #verificar se o estado ja tem size
                    if 'size' in objects[object]['states'][state]:
                        continue
                    else: #se nao tiver temos deduzir o tamanho
                        objects[object]['states'][state]['size'] = self.get_image_size(objects[object]['states'][state]['filenames'][0])
            #now verify the position
            if 'position' not in objects[object]:
                if 'size' in objects[object]:
                    size_w = objects[object]['size'][0]
                    size_h = objects[object]['size'][1]
                    w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                    h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                    objects[object]['position'] = (w,h)
                else: #temos de ver a posiçao estado a estado
                    for state in objects[object]['states']:
                        size_w = objects[object]['states'][state]['size'][0]
                        size_h = objects[object]['states'][state]['size'][1]
                        w = max(0,round(aux_w * i - aux_w/2 - size_w/2,2))
                        h = max(0,round(self.HEIGHT/2 - size_h/2,2))
                        objects[object]['states'][state]['position'] = (w,h)
            i+=1
        return objects

    def get_value_type(self,value):
        if type(value) == str:
            t = 'text'
        elif type(value) == tuple and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            t = 'position'
        elif type(value) == list and len(value) == 2 and all(isinstance(element, (int, float)) for element in value):
            t = 'size'
        elif type(value) == list and all(isinstance(element, str) for element in value):
            t = 'text_list'
        elif type(value) == int or type(value) == float:
            t = 'num'
        else:
            t = type(value)
        return t
    
#---------------------------------------------------------------------------------
#--------------------------------   Rules   --------------------------------------
#---------------------------------------------------------------------------------
    
    def start(self,start : str):
        '''start : python_block? imps? atrbs? sala sons? transicoes? desafios? eventos?'''
        elems = start.children
        i = 0
        #visitar python_block
        if elems[i].data == 'python_block':
            self.visit(elems[i])
            i+=1
        
        #visitar imports
        if elems[i].data == 'imps':
            self.visit(elems[i])
            i+=1
        
        #visitar args
        if elems[i].data == 'atrbs':
            self.visit(elems[i])
            i+=1

        #visitar mapa
        self.escape_room['map'] = self.visit(elems[i])
        i+=1
        #visitar transicoes
        if len(elems) > i and elems[i].data == 'transicoes':
            self.escape_room['transitions'] = self.visit(elems[i])
            i+=1
        #visitar sounds
        if len(elems) > i and elems[i].data == 'sons':
            self.escape_room['sounds'] = self.visit(elems[i])
            i+=1
        #visitar desafios
        if len(elems) > i and elems[i].data == 'desafios':
            self.visit(elems[i])
            i+=1
        if len(elems) > i:      
        #visitar todos os eventos
            self.escape_room['events'] = self.visit(elems[i])
        return self.escape_room
    
    def python_block(self,python_block):
        '''python_block  : "python{" python_code "}"'''
        elems = python_block.children
        code = elems[0].value
        code = code[3:-3]
        exec(code,self.namespace)
        # Dicionário de variáveis locais após a execução
        self.locals_python = {key: value for key, value in self.namespace.items() if key in code}

        # Dicionário de variáveis globais após a execução
        self.globals_python = globals().copy()

    def imps(self,imports):
        '''imports       : import+'''
        elems = imports.children
        for elem in elems:
            self.visit(elem)

    def obj_import(self,obj_import):
        '''import        : "importa " "Objeto." ID'''
        elems = obj_import.children
        id = elems[0].value
        obj = parse_obj(id,current_folder)
        self.imports['objects'][id] = obj


    def atrbs(self,atrbs):
        '''atrbs : atrb+'''
        elems = atrbs.children
        for elem in elems:
            self.visit(elem)

    def atrb(self,atrb):
        '''atrb : ARG "=" value'''
        elems = atrb.children
        arg = elems[0].value[1:]
        type,value = self.visit(elems[1])
        self.args[arg] = {
            'type' : type,
            'value' : value
        }

    def value_text(self, value_text):
        '''value : TEXT'''
        elems = value_text.children
        type = 'text'
        value = elems[0].value[1:-1]
        return (type,value)
    
    def value_text_list(self, value_text_list):
        '''value : text_list_value'''
        elems = value_text_list.children
        type = 'text_list'
        value = self.visit(elems[0])
        return (type,value)
    
    def value_pglobal(self, value_pglobal):
        '''value : "pglobal_" ID '''
        elems = value_pglobal.children
        id = elems[0].value
        value = self.globals_python[id]
        return (self.get_value_type(value),value)
    
    def value_plocal(self, value_plocal):
        '''value : "pglobal_" ID '''
        elems = value_plocal.children
        id = elems[0].value
        value = self.locals_python[id]
        return (self.get_value_type(value),value)
    
    def value_pfunc(self, value_pfunc):
        '''value : "pfunc_" FUNC '''
        elems = value_pfunc.children
        func = elems[0].value
        value = eval(func,self.namespace)
        return (self.get_value_type(value),value)

    def value_posicao(self, value_posicao):
        '''value : posicao'''
        elems = value_posicao.children
        type = 'position'
        value = self.visit(elems[0])
        return (type,value)
    
    def value_tamanho(self, value_tamanho):
        '''value : tamanho'''
        elems = value_tamanho.children
        type = 'size'
        value = self.visit(elems[0])
        return (type,value)
    
    def value_num(self, value_num):
        '''value : TEXT'''
        elems = value_num.children
        type = 'num'
        value = int(elems[0].value)
        return (type,value)
    
    def sala(self,sala):
        '''sala : "S""(" ID "," tamanho ")""{" cenas "}"'''
        elems = sala.children
        id = elems[0].value
        size = self.visit(elems[1])
        self.WIDTH = size[0]
        self.HEIGHT = size[1]
        scenes = self.visit(elems[2])

        result = {
                 'size' : size,
                 'scenes' : scenes
                 }

        return {id : result}
    
    def cenas(self,cenas):
        '''cenas : cena ("," cena)*'''
        elems = cenas.children
        result = {}
    
        #visitar todas as cenas
        for elem in elems:
            (scene_id,scene) = self.visit(elem)
            result[scene_id] = scene

        return result

    
    def cena (self,cena):
        '''cena : "C""(" ID ")""{" estobjs "}"'''
        elems = cena.children
        id = elems[0].value
        (states,objects) = self.visit(elems[1])
        result = {}
        #visitar estados
        result['states'] = states

        #visitar objetos
        result['objects'] = self.verify_pos_and_size(objects)

        return (id,result)
    
    def estobjs(self, estobjs):
        '''estobjs : (estado|objeto) ("," (estado|objeto))*'''
        elems = estobjs.children
        states = {}
        objects = {}

        for elem in elems:
            (id,value) = self.visit(elem)
            if elem.data == 'estado':
                states[id] = value
            elif elem.data == 'objeto' or elem.data == 'obj_imported':
                objects[id] = value
        return states,objects


    def objeto (self,objeto):
        '''objeto : "Objeto" ID posicao? tamanho? "{" estados "}"'''
        elems = objeto.children
        id = elems[0].value

        i = 1
        result = {}
        if len(elems) > i and (elems[i].data == 'posicao' or elems[i].data == 'posicao_arg'):
            result['position'] = self.visit(elems[i])
            i+=1

        if len(elems) > i and (elems[i].data == 'tamanho' or elems[i].data == 'tamanho_arg'):
            result['size'] = self.visit(elems[i])
            i+=1
        #visitar estados
        result['states'] = self.visit(elems[i])

        return (id,result)

    def obj_imported (self, obj_imported):
        '''objeto : "Objeto."ID ID posicao? tamanho?'''
        elems = obj_imported.children
        id_imported = elems[0].value
        id = elems[1].value
        if id_imported in self.imports['objects']:
            result = dict(self.imports['objects'][id_imported])
        else:
            raise Exception(f"{id_imported} não foi importado!")
        i = 2
        if len(elems) > i and (elems[i].data == 'posicao' or elems[i].data == 'posicao_arg'):
            result['position'] = self.visit(elems[i])
            i+=1

        if len(elems) > i and (elems[i].data == 'tamanho' or elems[i].data == 'tamanho_arg'):
            result['size'] = self.visit(elems[i])
            i+=1
        return (id,result)

    def estados (self,estados):
        '''estados : estado ("," estado)*'''
        elems = estados.children

        result = {}
        #visitar todos os estados
        for elem in elems:
            (id,state) = self.visit(elem)
            result[id] = state

        return result

    def estado (self,estado):
        '''estado : "Estado" INICIAL? ID filename posicao? tamanho?'''
        elems = estado.children
        result = {'initial' : False}

        i = 0
        if elems[i].type == 'INICIAL':
            result['initial'] = True
            i+=1

        id = elems[i].value
        i+=1
        result['filenames'] = [self.visit(elems[i])]
        i+=1

        if len(elems) > i and (elems[i].data == 'posicao' or elems[i].data == 'posicao_arg'):
            result['position'] = self.visit(elems[i])
            i+=1
        if len(elems) > i and (elems[i].data == 'tamanho' or elems[i].data == 'tamanho_arg'):
            result['size'] = self.visit(elems[i])

        return (id,result)

    def estado_animado_lista(self,estado):
        '''estado : "Estado" INICIAL? "animado" "(" numero  "," numero ")" ID filenames posicao? tamanho?'''
        elems = estado.children
        result = {'initial' : False}

        i = 0
        if hasattr(elems[i], 'type') and elems[i].type == 'INICIAL':
            result['initial'] = True
            i+=1
        
        result['time_sprite'] = self.visit(elems[i])
        i+=1
        result['repeate'] = self.visit(elems[i])
        i+=1
        id = elems[i].value
        i+=1
        result['filenames'] = self.visit(elems[i])
        i+=1
        if len(elems) > i and (elems[i].data == 'posicao' or elems[i].data == 'posicao_arg'):
            result['position'] = self.visit(elems[i])
            i+=1
        if len(elems) > i and (elems[i].data == 'tamanho' or elems[i].data == 'tamanho_arg'):
            result['size'] = self.visit(elems[i])

        return (id,result)
    
    def sons (self, sons):
        '''sons : "M" "{" som ("," som)* "}"'''
        elems = sons.children
        result = {}
        #visitar todos os sons
        for elem in elems:
            (id, src) = self.visit(elem)
            result[id] = src

        return result
    
    def som(self,som):
        '''som : ID "(" filename ")"'''
        elems = som.children
        id = elems[0].value
        src = self.visit(elems[1])

        return (id,src)
    
    def transicoes(self,transicoes):
        '''"transicoes : #Transições:" transicao+'''
        elems = transicoes.children
        result = {}
        #vistar todas as transicoes
        for elem in elems:
            (id, transicao) = self.visit(elem)
            result[id] = transicao

        return result
    
    def transicao(self, transicao):
        '''"Transição" ID ":" tfundo tmusica ttexto (tproxcena|tproxtrans)'''
        elems = transicao.children
        id = elems[0].value
        trans = {}
        trans['background'] = self.visit(elems[1])
        i = 2
        #visitar tmusica
        if len(elems) > i and elems[i].data == 'tmusica':
            trans['music'] = self.visit(elems[i])
            i+=1
        #visitar story
        if len(elems) > i and elems[i].data == 'ttexto':
            trans['story'] = self.visit(elems[i])
            i+=1
        if len(elems) > i and elems[i].data == "tproxcena":
            trans['next_scene'] = self.visit(elems[i])
        elif len(elems) > i and elems[i].data == "tproxtrans":
            trans['next_transition'] = self.visit(elems[i])

        return (id,trans)

    def tfundo(self,tfundo):
        '''tfundo : "- fundo:" text'''
        elems = tfundo.children
        return self.visit(elems[0])
    
    def tmusica(self,tmusica):
        '''tmusica : "- musica:" text'''
        elems = tmusica.children
        return self.visit(elems[0])

    def ttexto(self,ttexto):
        '''ttexto : "- história" text'''
        elems = ttexto.children
        return self.visit(elems[0])
    
    def tproxcena(self,tproxcena):
        '''tproxcena : "- próxima cena:" ID'''
        elems = tproxcena.children
        return elems[0].value
    
    def tproxtrans(self,tproxtrans):
        '''tproxtrans : "- próxima transição:" ID'''
        elems = tproxtrans.children
        return elems[0].value

    def desafios (self, eventos):
        '''"#Desafios:" desafio+'''
        elems = eventos.children
        #visitar todos os eventos
        for elem in elems:
            (id, desafio) = self.visit(elem)
            self.challenges[id] = desafio
    
    def desafio(self, desafio):
        '''desafio : "Desafio" ID ":" des'''
        elems = desafio.children
        id = elems[0].value
        des = self.visit(elems[1])
        return id,des

    def pede_codigo(self,des):
        '''des : "pede_código" "(" text "," text "," posicao "," ID "," ID ")"'''
        elems = des.children
        return {
            'type' : 'AskCode',
            'code' : self.visit(elems[0]),
            'message' : self.visit(elems[1]),
            'position' : self.visit(elems[2]),
            'sucess_event' : elems[3].value,
            'fail_event' : elems[4].value
            }
    
    def arrasta_objeto(self,des):
        '''des : "arrasta" ID ", se deixar em cima de" ID "faz" ID "se não faz" ID'''
        elems = des.children
        return {
            'type' : 'MoveObject',
            'object' : elems[0].value,
            'object_trigger' : elems[1].value,
            'sucess_event' : elems[2].value,
            'fail_event' : elems[3].value
            }
    
    def escolha_multipla(self,des):
        '''des : "pergunta" text "com as escolhas múltiplas" "[" text "," text "," text "," text "]" "em que a respota é" text ", se acertar faz" ID "e se errar faz" ID'''
        elems = des.children
        return {
            'type' : 'MultipleChoice',
            'question' : self.visit(elems[0]),
            'multiple_choices' : [self.visit(elems[1]),self.visit(elems[2]),self.visit(elems[3]),self.visit(elems[4])],
            'answer' : self.visit(elems[5]),
            'sucess_event' : elems[6].value,
            'fail_event' : elems[7].value
        }

    def ligacoes(self,des):
        '''des : "conecta" "[" text "," text "," text "," text "]" "a" "[" text "," text "," text "," text "]" "com mensagem" text ", se acertar faz" ID "e se errar faz" ID'''
        elems = des.children
        return {
            'type' : 'Connections',
            'connections' : {
                self.visit(elems[0]):self.visit(elems[1]),
                self.visit(elems[2]):self.visit(elems[3]),
                self.visit(elems[4]):self.visit(elems[5]),
                self.visit(elems[6]):self.visit(elems[7]),
                },
            'question' : self.visit(elems[8]),
            'sucess_event' : elems[9].value,
            'fail_event' : elems[10].value
        }
    
    def ordem(self,des):
        '''des : "escolhe em ordem" "[" text "," text "," text ","  text "]" "com mensagem" text ", se acertar faz" ID "e se errar faz" ID'''
        elems = des.children
        return {
            'type' : 'Order',
            'order' : [
                self.visit(elems[0]),
                self.visit(elems[1]),
                self.visit(elems[2]),
                self.visit(elems[3]),
                ],
            'question' : self.visit(elems[4]),
            'sucess_event' : elems[5].value,
            'fail_event' : elems[6].value
        }
    
    def puzzle(self,des):
        '''des : "puzzle" text, se completar faz ID'''
        elems = des.children
        return {
            'type' : 'Puzzle',
            'puzzle' : self.visit(elems[0]),
            'sucess_event' : elems[1].value,
            'fail_event' : None
        }

    def slide_puzzle(self,des):
        '''des : "slidepuzzle" text, se completar faz ID'''
        elems = des.children
        return {
            'type' : 'SlidePuzzle',
            'puzzle' : self.visit(elems[0]),
            'sucess_event' : elems[1].value,
            'fail_event' : None
        }
    
    def socket(self,des):
        '''des : "socket" text numero text ", se acertar faz" ID "e se errar faz" ID '''
        elems = des.children
        return {
            'type' : 'SocketConnection',
            'host' : self.visit(elems[0]),
            'port' : self.visit(elems[1]),
            'text' : self.visit(elems[2]),
            'sucess_event' : elems[3].value,
            'fail_event' : elems[4].value
        }

    def eventos (self, eventos):
        '''eventos : "E{" evento+ "}"'''
        elems = eventos.children
        result = {}
        #visitar todos os eventos
        for elem in elems:
            (id, evento) = self.visit(elem)
            result[id] = evento

        return result
    
    def evento_simples(self,evento):
        '''evento : ID "(" numero? ")" "{" precondicoes "}" "=>" "{" poscondicoes "}"'''
        elems = evento.children
        id = elems[0].value

        result = {}
        i = 1
        if (len(elems) == 4):
            result['repetivel'] = self.visit(elems[i])
            i+=1
        else:
            result['repetivel'] = sys.maxsize

        #visitar precondicoes
        result['precondicoes'] = self.visit(elems[i])
        i+=1
        #visitar poscondicoes
        result['poscondicoes'] = self.visit(elems[i])
        result['linked'] = False
        return (id,result)

    def evento_ligado(self,evento):
        '''evento        : ID "(""-"")" "{""}" "=>" "{" poscondicoes "}"'''
        elems = evento.children
        id = elems[0].value

        result = {}
        result['precondicoes'] = {}
        #visitar poscondicoes
        result['poscondicoes'] = self.visit(elems[1])
        result['repetivel'] = sys.maxsize
        result['linked'] = True

        return (id,result)

    def precondicoes_simples(self,precondicoes):
        '''precondicoes : precondicao '''
        elems = precondicoes.children
        var = self.visit(elems[0])
        result = {
            "variavel" : var
        }
        return result


    def precondicoes_e(self,precondicoes):
        '''precondicoes | precondicoes "&&" precondicoes '''
        elems = precondicoes.children
        left = self.visit(elems[0])
        right = self.visit(elems[1])
        result = {
            "operator" : "e",
            "left" : left,
            "right" : right

        }
        return result


    def precondicoes_ou(self,precondicoes):
        '''precondicoes | precondicoes "||" precondicoes '''
        elems = precondicoes.children
        left = self.visit(elems[0])
        right = self.visit(elems[1])
        result = {
            "operator" : "ou",
            "left" : left,
            "right" : right

        }
        return result


    def precondicoes_nao(self,precondicoes):
        '''precondicoes | "~" precondicoes '''
        elems = precondicoes.children
        left = self.visit(elems[0])
        right = None
        result = {
            "operator" : "nao",
            "left" : left,
            "right" : right

        }
        return result

    def precondicoes_grupo(self,precondicoes):
        '''precondicoes | "(" precondicoes ")" '''
        elems = precondicoes.children
        return self.visit(elems[0])

    def clique(self,precondicao):
        '''precondicao : "clique" "(" ID ")"'''
        elems = precondicao.children
        return {
            'type' : 'Click',
            'object' : elems[0].value,
            }

    def clique_nao(self,precondicao):
        '''precondicao : "clique_não" "(" ID ")"'''
        elems = precondicao.children
        return {
            'type' : 'ClickNot',
            'object' : elems[0].value,
            }

    def esta_estado(self,precondicao):
        '''precondicao : ID "@" ID"'''
        elems = precondicao.children
        return {
            'type' : 'WhenStateObject',
            'object' : elems[0].value,
            'state' : elems[1].value
            }

    def clique_depois(self,precondicao):
        '''"clique_depois" "(" ID "," ID ")"'''
        elems = precondicao.children
        return {
            'type' : 'ClickAfterEvent',
            'object' : elems[0].value,
            'event' : elems[1].value
            }

    def uso(self,precondicao):
        '''"uso" "(" ID ")"'''
        elems = precondicao.children
        return {
                'type' : 'ItemActived',
                'item' : elems[0].value
            }
    
    def poscondicoes (self, poscondicoes):
        '''poscondicoes : poscondicao ("e" poscondicao)*'''
        elems = poscondicoes.children

        result = []

        #visitar todas as poscondicoes
        for elem in elems:
            result.append(self.visit(elem))

        return result

    def muda_estado(self,poscondicao):
        '''poscondicao : ID "@" ID '''
        elems = poscondicao.children
        return {
            'type' : 'ChangeState',
            'object' : elems[0].value,
            'state' : elems[1].value
            }

    def vai_inv(self,poscondicao):
        '''poscondicao : ID ">>" "inventário" '''
        elems = poscondicao.children
        return {
            'type' : 'PutInInventory',
            'object' : elems[0].value
            }

    def fim_de_jogo(self,poscondicao):
        '''poscondicao : "fim""("")" '''
        elems = poscondicao.children
        return {
            'type' : 'EndGame',
            }

    def mensagem(self,poscondicao):
        '''poscondicao : "mensagem""("text","posicao")" '''
        elems = poscondicao.children
        return {
            'type' : 'ShowMessage',
            'message' : self.visit(elems[0]),
            'position' : self.visit(elems[1])
            }


    def muda_tamanho(self,poscondicao):
        '''poscondicao : ID ">>" tamanho '''
        elems = poscondicao.children
        return {
                'type' : 'ChangeSize',
                'object' : elems[0].value,
                'size' : self.visit(elems[1]),
            }

    def muda_posicao(self,poscondicao):
        '''poscondicao : ID ">>" posicao '''
        elems = poscondicao.children
        return {
                'type' : 'ChangePosition',
                'object' : elems[0].value,
                'position' : self.visit(elems[1]),
            }

    def muda_cena(self,poscondicao):
        '''poscondicao : "cena" "." ID  '''
        elems = poscondicao.children
        return {
                'type' : 'ChangeScene',
                'scene' : elems[0].value,
            }

    def remove(self,poscondicao):
        '''poscondicao : "remove" "(" ID ")" '''
        elems = poscondicao.children
        return {
                'type' : 'DeleteItem',
                'item' : elems[0].value
            }
    
    def toca_som(self,poscondicao):
        '''poscondicao : "toca" "(" ID ")"'''
        elems = poscondicao.children
        return {
                'type' : 'PlaySound',
                'sound' : elems[0].value
            }
    
    def comeca_desafio(self,poscondicao):
        '''poscondicao : "começa desafio" "(" ID ")"'''
        elems = poscondicao.children
        id = elems[0].value
        if id in self.challenges:
            return self.challenges[id]
        return {}
    
    def transiciona(self,poscondicao):
        '''poscondicao : "transição" ID'''
        elems = poscondicao.children
        return {
            'type' : 'Transition',
            'transition' : elems[0].value
        }

    def posicao (self, posicao):
        '''posicao : posicao_value'''
        return self.visit(posicao.children[0])

    def tamanho (self,tamanho):
        '''tamanho : tamanho_value'''
        return self.visit(tamanho.children[0])
    
    def posicao_arg (self, posicao):
        '''posicao : ARG'''
        elems = posicao.children
        arg = elems[0].value[1:]
        if arg in self.args:
            if self.args[arg]['type'] == 'position':
                return self.args[arg]['value']
            else:
                raise Exception(f"Tipo de {arg} errado!\n {self.args[arg]['type']} != Position")
        else:
            raise Exception(f"Argumento {arg} não definido")

    def tamanho_arg (self,tamanho):
        '''tamanho : ARG'''
        elems = tamanho.children
        arg = elems[0].value[1:]
        if arg in self.args:
            if self.args[arg]['type'] == 'size':
                return self.args[arg]['value']
            else:
                raise Exception(f"Tipo de {arg} errado!\n {self.args[arg]['type']} != Size")
        else:
            raise Exception(f"Argumento {arg} não definido")
    
    def posicao_value (self, posicao):
        '''posicao : "(" par ")"'''
        return self.visit(posicao.children[0])

    def tamanho_value (self,tamanho):
        '''tamanho : "[" par "]"'''
        return self.visit(tamanho.children[0])

    def par(self,par):
        '''par : numero "," numero'''
        elems = par.children
        return (self.visit(elems[0]),self.visit(elems[1]))
    
    def text_list(self, text_list):
        return self.visit(text_list.children[0])

    def text_list_value (self, text_list_value):
        '''text_list_value : "[" text ("," text)* "]"'''
        elems = text_list_value.children
        result = []
        for elem in elems:
            result.append(self.visit(elem))
        return result
    
    def text_list_arg(self,text_list_arg):
        '''text_list : ARG'''
        elems = text_list_arg.children
        arg = elems[0].value[1:]
        if arg in self.args:
            if self.args[arg]['type'] == 'text_list':
                return self.args[arg]['value']
            else:
                raise Exception(f"Tipo de {arg} errado!\n {self.args[arg]['type']} != List Text")
        else:
            raise Exception(f"Argumento {arg} não definido")
    
    def text(self,text):
        '''text : TEXTO'''
        elems = text.children
        return elems[0].value[1:-1]
    
    def numero(self,numero):
        '''numero : NUM'''
        elems = numero.children
        return int(elems[0].value)
    
    def num_arg(self,num_arg):
        '''numero : ARG'''
        elems = num_arg.children
        arg = elems[0].value[1:]
        if arg in self.args:
            if self.args[arg]['type'] == 'num':
                return self.args[arg]['value']
            else:
                raise Exception(f"Tipo de {arg} errado!\n {self.args[arg]['type']} != Num")
        else:
            raise Exception(f"Argumento {arg} não definido")

    def text_argn(self,text):
        '''text : ARGN'''
        elems = text.children
        arg = elems[0].value[1:]
        arg = int(arg)
        try:
            return self.argsn[arg]
        except:
            raise Exception(f"Não foi provido um arg: {arg}")
    
    def text_arg(self,text):
        '''text : ARG'''
        elems = text.children
        arg = elems[0].value[1:]
        if arg in self.args:
            if self.args[arg]['type'] == 'text':
                return self.args[arg]['value']
            else:
                raise Exception(f"Tipo de {arg} errado!\n {self.args[arg]['type']} != Text")
        else:
            raise Exception(f"Argumento {arg} não definido")
    
    def text_pfunc(self,text_pfunc):
        '''text : "pfunc_" FUNC'''
        elems = text_pfunc.children
        func = elems[0].value
        value = eval(func,self.namespace)
        t = self.get_value_type(value)
        if t == 'text':
            return value
        else:
            raise Exception(f"Tipo de {arg} errado!\n {t} != Text")

    def color (self, color):
        '''color : "(" numero "," numero "," numero ")"'''
        elems = color.children
        return (self.visit(elems[0]),self.visit(elems[1]),self.visit(elems[2]))
    
    def python_code(self, code):
        code = code[0]
        try:
            # Avalia o código Python inserido
            evaluated_code = ast.literal_eval(code)
            return evaluated_code
        except SyntaxError:
            # Se não for uma expressão Python, executa o código diretamente
            exec(code, globals(), self.variables)

def parse(args):
    if args.grammar_erplpro:
        grammar = open(f"{current_folder}/grammar_erplpro.txt","r")
    else:
        grammar = open(f"{current_folder}/grammar_erpl.txt","r")
        #raise Exception("Nenhuma gramática escolhida! Use -gm1 or -gm2")

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

def main():
    args = parser_parse_arguments()
    parse(args)
    

if __name__ == '__main__':
    main()