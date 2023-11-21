#!/usr/bin/python3

from lark.visitors import Interpreter
from lark import Lark
import json
import sys
import argparse
import os

def parse_arguments():
    '''Define and parse arguments using argparse'''
    parser = argparse.ArgumentParser(description='ERPL Parser')
    parser.add_argument('--output','-o'            ,type=str, nargs=1,required=False                                , help='Output file')
    parser.add_argument('--input','-i'             ,type=str, nargs=1,required=False                                , help='Input file')
    parser.add_argument('--grammar_erpl','-gm1'    ,action='store_true'                                      , help='Grammar ERPL' )
    parser.add_argument('--grammar_erplpro','-gm2'    ,action='store_true'                                      , help='Grammar ERPL Pro' )
    return parser.parse_args()

class Interpreter(Interpreter):

#---------------------------------------------------------------------------------
#--------------------------------   Rules   --------------------------------------
#---------------------------------------------------------------------------------

    def __init__(self):
        self.escape_room = {
            'map' : {},
            'events' : {},
            'sounds' : {}
        }

    def start(self,start):
        '''start : sala sons? eventos?'''
        elems = start.children
        #visitar mapa
        self.escape_room['map'] = self.visit(elems[0])
        i = 1
        if elems[i].data == 'sons':
            self.escape_room['sounds'] = self.visit(elems[i])
            i+=1
        if len(elems) > i:      
        #visitar todos os eventos
            self.escape_room['events'] = self.visit(elems[i])
        return self.escape_room
    
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

    def estado_animado(self,estado):
        '''estado : "Estado" INICIAL? "animado" "(" NUM  "," NUM ")" ID "[" filenames "]" (posicao tamanho)?'''
        elems = estado.children
        result = {'initial' : False}

        i = 0
        if elems[i].type == 'INICIAL':
            result['initial'] = True
            i+=1
        
        result['time_sprite'] = int(elems[i].value)
        i+=1
        result['repeate'] = int(elems[i].value)
        i+=1
        id = elems[i].value
        i+=1
        result['filenames'] = self.visit(elems[i])
        i+=1
        if(len(elems) > i+1):
            result['position'] = self.visit(elems[i])
            result['size'] = self.visit(elems[i+1])

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
        '''evento : ID "(" NUM? ")" "{" precondicoes "}" "=>" "{" poscondicoes "}"'''
        elems = evento.children
        id = elems[0].value

        result = {}
        i = 1
        if (len(elems) == 4):
            result['repetivel'] = int(elems[i].value)
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
        '''poscondicao : "mensagem""("TEXTO","posicao")" '''
        elems = poscondicao.children
        return {
            'type' : 'EndGame',
            }

    def mensagem(self,poscondicao):
        '''poscondicao : "fim""("")" '''
        elems = poscondicao.children
        return {
            'type' : 'ShowMessage',
            'message' : elems[0].value[1:-1],
            'position' : self.visit(elems[1])
            }

    def pede_codigo(self,poscondicao):
        '''poscondicao : "pede_código" "(" TEXTO "," TEXTO "," posicao "," ID "," ID ")" -> pede_codigo'''
        elems = poscondicao.children
        return {
            'type' : 'AskCode',
            'code' : elems[0].value[1:-1],
            'message' : elems[1].value[1:-1],
            'position' : self.visit(elems[2]),
            'sucess_event' : elems[3].value,
            'fail_event' : elems[4].value
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
        '''posicao : "(" par ")"'''
        return self.visit(posicao.children[0])

    def tamanho (self,tamanho):
        '''tamanho : "[" par "]"'''
        return self.visit(tamanho.children[0])

    def par(self,par):
        '''par : NUM "," NUM'''
        elems = par.children
        return (int(elems[0].value),int(elems[1].value))
    
    #def filenames (self, filenames):
    #    '''filenames : filename ("," filename)*'''
    #    elems = filenames.children
    #    result = []
    #    for elem in elems:
    #        result.append(self.visit(elem))
    #    return result

    def filename (self, filename):
        '''filename : TEXTO'''
        elems = filename.children
        return elems[0].value[1:-1]


def main():
    current_folder = os.path.dirname(__file__)
    args = parse_arguments()
    if args.grammar_erpl:
        grammar = open(f"{current_folder}/grammar_erpl.txt","r")
    elif args.grammar_erplpro:
        grammar = open(f"{current_folder}/grammar_erplpro.txt","r")
    else:
        print("ERRO! Nenhuma gramática escolhida")
        return

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

if __name__ == '__main__':
    main()