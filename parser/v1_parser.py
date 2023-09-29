from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
from lark import Lark,Discard ,Token,Tree
import json

grammar= '''
start         : definicao+
definicao     : assinatura carateristica+
assinatura    : "#" TIPO ID ":"
carateristica : "--" ATRIBUTO ":" valor
valor         : TEXTO
              | ID
              | par
              | TIPO_EVENTO
              | TIPO_GATILHO
par           : "(" NUM "," NUM ")"

TIPO          : /(ROOM)|(CENA)|(OBJETO)|(ESTADO\(INICIAL\))|(ESTADO)|(EVENTO)|(GATILHO)/
ATRIBUTO      : /(TAMANHO)|(BACKGROUND)|(REFERENTE)|(POSICAO)|(IMAGEM)|(TIPO)|(CENA)|(OBJETO)|(ESTADO_INICIAL)|(ESTADO_FINAL)|(EVENTO)|(ESTADO)|(GATILHO)/
ID            : /[\w\.\-_]+/
TEXTO         : /"[^"]*"/
NUM           : /\d+/
TIPO_EVENTO   : /(MUDAR_ESTADOS)|(FIM_DE_JOGO)|(COLOCA_NO_INVENTARIO)/
TIPO_GATILHO  : /(CLIQUE|CLIQUE_DEPOIS_DE_EVENTO|(CLIQUE_QUANDO_ESTADO_DE_OBJETO))/

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
            'ROOM' : {},
            'CENA' : {},
            'OBJETO' : {},
            'ESTADO' : {},
            'EVENTO' : {},
            'GATILHO' : {}
        }

    def start(self,start):
        '''start : definicao+'''
        elems = start.children
        #visitar todas as defincoes
        for elem in elems:
            self.visit(elem)
        #self.print_details()
        return self.escape_room
        

    def definicao(self,definicao):
        '''definicao : assinatura carateristica+'''
        elems = definicao.children
        #visitar assinatura
        self.visit(elems[0])
        
        #visitar carasteriscas
        for elem in elems[1:]:
            self.visit(elem)
    
    def assinatura(self,assinatura):
        '''assinatura : "#" TIPO ID ":"'''
        #buscar o valor do tipo e id
        elems = assinatura.children
        tipo = elems[0].value
        id = elems[1].value

        #adicionar o id ao dicionario com tipo respetivo
        if tipo == 'ESTADO' or tipo == 'ESTADO(INICIAL)':
            self.escape_room['ESTADO'][id] = {'estado_inicial' : False}
            if tipo == 'ESTADO(INICIAL)':
                self.escape_room['ESTADO'][id]['estado_inicial'] = True
            #definir o tipo atual
            self.current_tipo = 'ESTADO'
        else:
            self.escape_room[tipo][id] = {}
            #definir o tipo atual
            self.current_tipo = tipo
        self.current_id = id

    def carateristica(self,carateristica):
        '''carateristica : "--" ATRIBUTO ":" valor'''
        elems = carateristica.children
        atributo = elems[0].value
        self.valida_atributo(atributo)
        self.current_atributo = atributo

        valor = self.visit(elems[1])
        self.valida_valor(valor)
        self.add_carateristica(atributo,valor)


    def valor(self,valor):
        '''valor : TEXTO
                 | ID
                 | par
                 | TIPO_EVENTO
                 | TIPO_GATILHO'''
        elem = valor.children[0]
        if type(elem) == Tree:
            val = self.visit(elem)
        else:
            val = elem.value
        return val

    def par(self,par):
        '''par : "(" NUM "," NUM ")"'''
        elems = par.children
        return (int(elems[0].value),int(elems[1].value))
    

# ficheiro com a frase para analisar
file = open("../erpl/v1.txt")
code = file.read()
file.close()


# analisar frase com a gramatica definida
p = Lark(grammar)
parse_tree = p.parse(code)
it = Interpreter()
data = it.visit(parse_tree)

# Serializing json  
with open("../models/sample.json", "w") as outfile:
    json.dump(data, outfile, indent = 4)