from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
from lark import Lark,Discard ,Token,Tree
import json
import sys

grammar= '''
start         : sala eventos?

sala          : "S""(" ID "," tamanho ")""{" cenas "}"
cenas         : cena ("," cena)*
cena          : "C""(" ID ")""{" estobjs "}"
estobjs       : (estado|objeto) ("," (estado|objeto))*
objeto        : "O""(" ID ("," posicao "," tamanho)? ")""{" estados "}"

estados       : estado ("," estado)*
estado        : (ESTADO|ESTADOINICIAL) "(" ID "," filename ("," posicao "," tamanho)? ")"

eventos       : "E{" evento+ "}"
evento        : ID "(" NUM? ")" "{" precondicoes "}" "=>" "{" poscondicoes "}" -> evento_simples
              | ID "(""-"")" "{""}" "=>" "{" poscondicoes "}"                         -> evento_ligado


precondicoes  : precondicao                             -> precondicoes_simples
              | precondicoes "&&" precondicoes          -> precondicoes_e
              | precondicoes "||" precondicoes          -> precondicoes_ou
              | "~" precondicoes                        -> precondicoes_nao
              | "(" precondicoes ")"                    -> precondicoes_grupo

precondicao   : "clique" "(" ID ")"                     -> clique
              | "clique_não" "(" ID ")"                 -> clique_nao
              | ID "@" ID                               -> esta_estado
              | "clique_depois" "(" ID "," ID ")"       -> clique_depois
              | "uso" "(" ID ")"                        -> uso

poscondicoes  : poscondicao ("&&" poscondicao)*
poscondicao   : ID "@" ID                               -> muda_estado
              | ID ">>" "inventário"                    -> vai_inv
              | "fim""("")"                             -> fim_de_jogo
              | "mensagem""("TEXTO","posicao")"         -> mensagem   
              | "pede_código" "(" TEXTO "," TEXTO "," ID "," ID ")" -> pede_codigo
              | ID ">>" tamanho                         -> muda_tamanho
              | ID ">>" posicao                         -> muda_posicao
              | "cena" "." ID                           -> muda_cena
              | "remove" "(" ID ")"                     -> remove

posicao       : "(" par ")"
tamanho       : "[" par "]"
par           : NUM "," NUM
filename      : TEXTO

ESTADO        : /E/
ESTADOINICIAL : /Ei/

ID            : /[\w\-_]+/
TEXTO         : /"[^"]*"/
NUM           : /\d+/

%import common.WS
%ignore WS
'''

class Interpreter(Interpreter):

#---------------------------------------------------------------------------------
#--------------------------------   Utils   --------------------------------------
#---------------------------------------------------------------------------------

    def print_details(self):
        print(self.escape_room)

    #verifica se determinado atributo faz sentido na definiçao atual
    def valida_atributo(self,atributo):
        pass

    #verifica se determinado valor faz sentido no atributo atual
    def valida_valor(self,valor):
        pass

    def add_carateristica(self,carateristica,valor):
        tipo = self.current_tipo
        id = self.current_id
        #adicionar ao dicionario correspondente com tipo_atual respetivo
        self.escape_room[tipo][id][carateristica] = valor

#---------------------------------------------------------------------------------
#--------------------------------   Rules   --------------------------------------
#---------------------------------------------------------------------------------

    def __init__(self):
        self.escape_room = {
            'map' : {},
            'events' : {},
        }

    def start(self,start):
        '''start : sala eventos?'''
        elems = start.children
        #visitar mapa
        self.escape_room['map'] = self.visit(elems[0])
        #visitar todos os eventos
        if len(elems) > 1:
            self.escape_room['events'] = self.visit(elems[1])
        #self.print_details()
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
        '''estado : (ESTADO|ESTADOINICIAL) "(" ID "," filename ("," posicao "," tamanho)?'''
        elems = estado.children
        id = elems[1].value
        filename = self.visit(elems[2])

        result = {
            'filename' : filename,
            'initial' : False
        }

        if(len(elems) == 5):
            result['position'] = self.visit(elems[3])
            result['size'] = self.visit(elems[4])

        if elems[0].type == 'ESTADOINICIAL':
            result['initial'] = True
        return (id,result)


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
        '''evento        : ID "(" NUM? ")" "{" precondicoes "}" "=>" "{" poscondicoes "}"'''
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
        '''poscondicao : "pede_código" "(" TEXTO "," TEXTO "," ID "," ID ")" '''
        elems = poscondicao.children
        return {
            'type' : 'AskCode',
            'code' : elems[0].value[1:-1],
            'message' : elems[1].value[1:-1],
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

    def filename (self, filename):
        '''filename : TEXTO'''
        elems = filename.children
        return elems[0].value[1:-1]

# ficheiro com a frase para analisar
file = open("../erpl/v5.txt")
code = file.read()
file.close()


# analisar frase com a gramatica definida
p = Lark(grammar)
parse_tree = p.parse(code)
it = Interpreter()
data = it.visit(parse_tree)

#Serializing json  
with open("../models/sample4.json", "w") as outfile:
    json.dump(data, outfile, indent = 3)