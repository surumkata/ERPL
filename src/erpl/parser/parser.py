#!/usr/bin/python3

from lark.visitors import Interpreter
from lark import Lark
import json
import sys
import argparse
import os
from imageplustxt import add_text_to_image
import glob

import re 
def sorted_alphanum(l): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def parser_parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL Parser')
    parser.add_argument('--output','-o'            ,type=str, nargs=1,required=False                                , help='Output file')
    parser.add_argument('--input','-i'             ,type=str, nargs=1,required=False                                , help='Input file')
    parser.add_argument('--grammar_erpl','-gm1'    ,action='store_true'                                      , help='Grammar ERPL' )
    parser.add_argument('--grammar_erplpro','-gm2' ,action='store_true'                                      , help='Grammar ERPL Pro' )
    parser.add_argument('--args','-args'           ,nargs='+'                                                , help='Args')
    return parser.parse_args()

class Interpreter(Interpreter):

#---------------------------------------------------------------------------------
#--------------------------------   Rules   --------------------------------------
#---------------------------------------------------------------------------------

    def __init__(self,args):
        self.escape_room = {
            'map' : {},
            'events' : {},
            'sounds' : {}
        }
        self.__images = f"{os.path.dirname(__file__)}/../../../assets/images/"
        self.__fonts = f"{os.path.dirname(__file__)}/../../../assets/fonts/"
        self.argsn = args
        self.args = {}

    def start(self,start : str):
        '''start : atrbs? sala sons? eventos?'''
        elems = start.children
        i = 0
        #visitar args
        if elems[i].data == 'atrbs':
            self.visit(elems[i])
            i+=1
        #visitar mapa
        self.escape_room['map'] = self.visit(elems[i])
        i+=1
        #visitar sounds
        if len(elems) > i and elems[i].data == 'sons':
            self.escape_room['sounds'] = self.visit(elems[i])
            i+=1
        if len(elems) > i:      
        #visitar todos os eventos
            self.escape_room['events'] = self.visit(elems[i])
        return self.escape_room
    
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
        result['objects'] = objects

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
            elif elem.data == 'objeto':
                objects[id] = value
        return states,objects


    def objeto (self,objeto):
        '''objeto : "O""(" ID ("," posicao "," tamanho)? ")""{" estados "}"'''
        elems = objeto.children
        id = elems[0].value

        i = 1
        result = {}

        if(len(elems) == 4):
            result['position'] = self.visit(elems[i])
            i+=1
            result['size'] = self.visit(elems[i])
            i+=1

        #visitar estados
        result['states'] = self.visit(elems[i])

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
        '''estado : "Estado" INICIAL? ID filename (posicao tamanho)?'''
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

        if(len(elems) > i+1):
            result['position'] = self.visit(elems[i])
            result['size'] = self.visit(elems[i+1])

        return (id,result)

    def estado_animado_lista(self,estado):
        '''estado : "Estado" INICIAL? "animado" "(" numero  "," numero ")" ID "[" filenames "]" (posicao tamanho)?'''
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
        if(len(elems) > i+1):
            result['position'] = self.visit(elems[i])
            result['size'] = self.visit(elems[i+1])

        return (id,result)
    
    def estado_animado_glob(self,estado):
        '''estado : "Estado" INICIAL? "animado" "(" numero "," numero ")" ID "glob" REVERSE? "(" text ")" (posicao tamanho)?'''
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
        arg = self.visit(elems[i])
        result['filenames'] = glob.glob(self.__images + arg)
        result['filenames'] = sorted_alphanum([filename.replace(self.__images,"") for filename in result['filenames']])
        
        i+=1

        if(len(elems) > i and elems[i].type == 'REVERSE'):
            result['filenames'] = result['filenames'][::-1]
        
        if(len(elems) > i+1):
            result['position'] = self.visit(elems[i])
            result['size'] = self.visit(elems[i+1])

        return (id,result)
    
    def estado_img_plus_text(self,estado):
        '''estado : "Estado" INICIAL? ID "image_plus_txt" "(" filename "," filename "," text "," filename ("," color)? ")" (posicao tamanho)? '''
        elems = estado.children
        result = {'initial' : False}

        i = 0
        if elems[i].type == 'INICIAL':
            result['initial'] = True
            i+=1
        
        id = elems[i].value
        i+=1
        input = self.visit(elems[i])
        i+=1
        output = self.visit(elems[i])
        i+=1
        text = self.visit(elems[i])
        i+=1
        font = self.visit(elems[i])
        i+=1
        color = (255,255,255)
        if len(elems) > i and elems[i].data == 'color':
            color = self.visit(elems[i])
            i+=1

        if(len(elems) > i+1):
            result['position'] = self.visit(elems[i])
            result['size'] = self.visit(elems[i+1])

        add_text_to_image(self.__images + input,self.__images + output,text,color, self.__fonts + font)

        result['filenames'] = [output]
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

    def pede_codigo(self,poscondicao):
        '''poscondicao : "pede_código" "(" text "," text "," posicao "," ID "," ID ")"'''
        elems = poscondicao.children
        return {
            'type' : 'AskCode',
            'code' : self.visit(elems[0]),
            'message' : self.visit(elems[1]),
            'position' : self.visit(elems[2]),
            'sucess_event' : elems[3].value,
            'fail_event' : elems[4].value
            }
    
    def arrasta_objeto(self,poscondicao):
        '''poscondicao : "arrasta" ID ", se deixar em cima de" ID "faz" ID "se não faz" ID'''
        elems = poscondicao.children
        return {
            'type' : 'MoveObject',
            'object' : elems[0].value,
            'object_trigger' : elems[1].value,
            'sucess_event' : elems[2].value,
            'fail_event' : elems[3].value
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
    
    #def filenames (self, filenames):
    #    '''filenames : filename ("," filename)*'''
    #    elems = filenames.children
    #    result = []
    #    for elem in elems:
    #        result.append(self.visit(elem))
    #    return result

    def filename (self, filename):
        '''filename : text'''
        elems = filename.children
        return self.visit(elems[0])
    
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

    def color (self, color):
        '''color : "(" numero "," numero "," numero ")"'''
        elems = color.children
        return (self.visit(elems[0]),self.visit(elems[1]),self.visit(elems[2]))


def parse(args):
    current_folder = os.path.dirname(__file__)
    if args.grammar_erpl:
        grammar = open(f"{current_folder}/grammar_erpl.txt","r")
    elif args.grammar_erplpro:
        grammar = open(f"{current_folder}/grammar_erplpro.txt","r")
    else:
        raise Exception("Nenhuma gramática escolhida! Use -gm1 or -gm2")

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

def main():
    args = parser_parse_arguments()
    parse(args)
    

if __name__ == '__main__':
    main()