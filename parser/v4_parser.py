from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
from lark import Lark,Discard ,Token,Tree
import json

grammar= '''
start         : mapa eventos?

mapa          : "#Mapa:" sala
sala          : "Sala" ID tamanho ("contém" cena)+
cena          : "Cena" ID estados objetos
objetos       : ("contém" objeto)+
objeto        : "Objeto" ID posicao tamanho estados

estados       : ("tem" estado)+
estado        : (ESTADO|ESTADOINICIAL) ID filename

eventos       : "#Eventos:" evento+
evento        : (EVENTO|EVENTOUNICO) ID ":" se "," entao "."
              | EVENTOLIG ID ":" poscondicoes "."

se            : ("Se"|"se") precondicoes
precondicoes  : precondicao ("e" precondicao)*
precondicao   : CLIQUE ID
              | CLIQUENOT ID
              | ID ESTA ID
              | ID NAOESTA ID
              | CLIQUE ID DEPOISDE ID TERACONTECIDO
              | ID EMUSO
              | ID NAOEMUSO

entao         : ("Então"|"então") poscondicoes
poscondicoes  : poscondicao ("e" poscondicao)*
poscondicao   : ID MUDAPARA ID
              | ID VAIINVENTARIO
              | FIMDEJOGO
              | MOSTRAMSG TEXTO "em" posicao
              | PEDECODIGO TEXTO "com mensagem" TEXTO ", se acertar faz" ID "e se errar faz" ID
              | ID MUDATAMANHO tamanho
              | ID MUDAPOSICAO posicao
              | MUDAPARACENA ID
              | ID REMOVEITEM

posicao       : "(" par ")"
tamanho       : "[" par "]"
par           : NUM "," NUM
filename      : TEXTO

ESTADO        : /Estado/
ESTADOINICIAL : /Estado inicial/

EVENTO        : /Evento/
EVENTOUNICO   : /Evento único/
EVENTOLIG     : /Evento ligado/

EMUSO         : /está em uso/
NAOEMUSO      : /não está em uso/
DEPOISDE      : /depois de/
TERACONTECIDO : /ter acontecido/
NAOESTA       : /não está/
ESTA          : /está/
CLIQUE        : /clique/
CLIQUENOT     : /clique não/


MUDAPARACENA  : /muda para cena/
MUDAPOSICAO   : /muda posição para/
MUDATAMANHO   : /muda tamanho para/
MUDAPARA      : /muda para/
VAIINVENTARIO : /vai para o inventário/
FIMDEJOGO     : /fim de jogo/
MOSTRAMSG     : /mostra mensagem/
PEDECODIGO    : /pede código/
REMOVEITEM    : /é removid(o|a)/

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
        '''start : mapa eventos?'''
        elems = start.children
        #visitar mapa
        self.escape_room['map'] = self.visit(elems[0])
        #visitar todos os eventos
        if len(elems) > 1:
            self.escape_room['events'] = self.visit(elems[1])
        #self.print_details()
        return self.escape_room
        
    def mapa(self,mapa):
        '''mapa : '#Mapa:' sala'''
        elems = mapa.children
        #visitar sala
        return self.visit(elems[0])
    
    def sala(self,sala):
        '''sala : 'Sala' ID tamanho ('contém' cena)+'''
        elems = sala.children
        id = elems[0].value
        size = self.visit(elems[1])

        result = {
                 'size' : size,
                 'scenes' : {}
                 }
        
        #visitar todas as cenas
        for elem in elems[2:]:
            (scene_id,scene) = self.visit(elem)
            result['scenes'][scene_id] = scene

        return {id : result}
    
    def cena (self,cena):
        '''cena : "Cena" ID estados objetos'''
        elems = cena.children
        id = elems[0].value
        result = {}
        #visitar estados
        result['states'] = self.visit(elems[1])

        #visitar objetos
        result['objects'] = self.visit(elems[2])

        return (id,result)

    def objetos (self,objetos):
        '''objetos : ("contém" objeto)+'''
        elems = objetos.children
        result = {}
        #visitar todos os objetos
        for elem in elems:
            (id,object) = self.visit(elem)
            result[id] = object
        
        return result

    def objeto (self,objeto):
        '''objeto : 'Objeto' ID posicao tamanho estados'''
        elems = objeto.children
        id = elems[0].value
        position = self.visit(elems[1])
        size = self.visit(elems[2])
        
        result = {
            'size' : size,
            'position' : position,
            'states' : []
        }

        #visitar estados
        result['states'] = self.visit(elems[3])

        return (id,result)

    def estados (self,estados):
        '''estados : ("tem" estado)+'''
        elems = estados.children

        result = {}
        #visitar todos os estados
        for elem in elems:
            (id,state) = self.visit(elem)
            result[id] = state

        return result

    def estado (self,estado):
        '''estado : (ESTADO|ESTADOINICIAL) ID filename'''
        elems = estado.children
        id = elems[1].value
        filename = self.visit(elems[2])

        result = {
            'filename' : filename,
            'initial' : False
        }

        if elems[0].type == 'ESTADOINICIAL':
            result['initial'] = True
        return (id,result)

    def eventos (self, eventos):
        '''eventos : "#Eventos:" evento+'''
        elems = eventos.children
        result = {}
        #visitar todos os eventos
        for elem in elems:
            (id, evento) = self.visit(elem)
            result[id] = evento

        return result

    def evento (self, evento):
        '''evento : (EVENTO|EVENTOUNICO) ID ":" se "," entao "."
                  | EVENTOLIG ID ":" poscondicoes'''
        elems = evento.children
        id = elems[1].value

        result = {}

        if(not elems[0].type == 'EVENTOLIG'):
            #visitar se
            result['precondicoes'] = self.visit(elems[2])
            #visitar entao
            result['poscondicoes'] = self.visit(elems[3])

            if elems[0].type == 'EVENTO':
                result['repetivel'] = True
            else: result['repetivel'] = False 
        else :
            result['precondicoes'] = []
            result['poscondicoes'] = self.visit(elems[2])
            result['repetivel'] = True
            result['linked'] = True

        return (id,result)

    def se (self,se):
        '''se : ("Se"|"se") precondicoes'''
        elems = se.children
        #visitar precondicoes
        result = self.visit(elems[0])
        return result

    def precondicoes (self, precondicoes):
        '''precondicoes : precondicao ("e" precondicao)*'''
        elems = precondicoes.children

        result = []

        #visitar todas as precondicoes
        for elem in elems:
            result.append(self.visit(elem))

        return result

    def precondicao (self,precondicao):
        '''precondicao : CLIQUE ID
                    | CLIQUENOT ID
                    | CLIQUE ID DEPOISDE ID TERACONTECIDO
                    | ID ESTA ID
                    | ID NAOESTA ID
                    | ID EMUSO
                    | ID NAOEMUSO'''
        
        elems = precondicao.children
        result = {}
        if elems[0].type == 'CLIQUE':
            object_id = elems[1].value
            if(len(elems) > 2):
                if elems[2].type == 'DEPOISDE' and elems[4].type == 'TERACONTECIDO':
                    event_id = elems[3].value
                    result = {
                            'type' : 'ClickAfterEvent',
                            'object' : object_id,
                            'event' : event_id
                            }
            else:
                result = {
                        'type' : 'Click',
                        'object' : object_id,
                        }
        elif elems[0].type == 'CLIQUENOT':
            object_id = elems[1].value
            result = {
                        'type' : 'ClickNot',
                        'object' : object_id,
                        }
        elif elems[1].type == 'ESTA':
            object_id = elems[0].value
            state_id = elems[2].value
            result = {
                    'type' : 'WhenStateObject',
                    'object' : object_id,
                    'state' : state_id
            }
        elif elems[1].type == 'NAOESTA':
            object_id = elems[0].value
            state_id = elems[2].value
            result = {
                    'type' : 'WhenNotStateObject',
                    'object' : object_id,
                    'state' : state_id
            }
        elif elems[1].type == 'EMUSO':
            item_id = elems[0].value
            result = {
                'type' : 'ItemActived',
                'item' : item_id
            }
        elif elems[1].type == 'NAOEMUSO':
            item_id = elems[0].value
            result = {
                'type' : 'ItemNotActived',
                'item' : item_id
            }
        return result

    def entao (self, entao):
        '''entao : ("Então"|"então") poscondicoes'''
        elems = entao.children
        #visitar poscondicoes
        result = self.visit(elems[0])
        return result

    def poscondicoes (self, poscondicoes):
        '''poscondicoes : poscondicao ("e" poscondicao)*'''
        elems = poscondicoes.children

        result = []

        #visitar todas as poscondicoes
        for elem in elems:
            result.append(self.visit(elem))

        return result

    def poscondicao (self, poscondicao):
        '''poscondicao  : ID MUDAPARA ID
                 | ID VAIINVENTARIO
                 | FIMDEJOGO
                 | MOSTRAMSG TEXTO 'em' posicao
                 | PEDECODIGO TEXTO "com mensagem" TEXTO ", se acertar" ID "e se errar" ID
                 | ID MUDATAMANHO tamanho
                 | ID MUDAPOSICAO posicao
                 | MUDAPARACENA ID
                 | ID REMOVEITEM'''
        
        elems = poscondicao.children
        result = {}
        if elems[0].type == 'FIMDEJOGO':
            result = {
                'type' : 'EndGame'
            }
        elif elems[1].type == 'VAIINVENTARIO':
            object_id = elems[0].value
            result = {
                'type' : 'PutInInventory',
                'object' : object_id
            }

        elif elems[1].type == 'MUDAPARA':
            object_id = elems[0].value
            state_id = elems[2].value
            result = {
                'type' : 'ChangeState',
                'object' : object_id,
                'state' : state_id
            }
        elif elems[0].type == 'MOSTRAMSG':
            message = elems[1].value[1:-1]
            position = self.visit(elems[2])
            result = {
                'type' : 'ShowMessage',
                'message' : message,
                'position' : position
            }
        elif elems[0].type == 'PEDECODIGO':
            code = elems[1].value[1:-1]
            message = elems[2].value[1:-1]
            sucess_event = elems[3].value
            fail_event = elems[4].value
            result = {
                'type' : 'AskCode',
                'code' : code,
                'message' : message,
                'sucess_event' : sucess_event,
                'fail_event' : fail_event
            }
        elif elems[1].type == 'MUDATAMANHO':
            object_id = elems[0].value
            size = self.visit(elems[2])
            result = {
                'type' : 'ChangeSize',
                'object' : object_id,
                'size' : size,
            }
        elif elems[1].type == 'MUDAPOSICAO':
            object_id = elems[0].value
            pos = self.visit(elems[2])
            result = {
                'type' : 'ChangePosition',
                'object' : object_id,
                'position' : pos,
            }
        elif elems[0].type == 'MUDAPARACENA':
            scene_id = elems[1].value
            result = {
                'type' : 'ChangeScene',
                'scene' : scene_id,
            }
        elif elems[1].type == 'REMOVEITEM':
            item_id = elems[0].value
            result = {
                'type' : 'DeleteItem',
                'item' : item_id
            }

        return result

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
file = open("../erpl/v4.txt")
code = file.read()
file.close()


# analisar frase com a gramatica definida
p = Lark(grammar)
parse_tree = p.parse(code)
it = Interpreter()
data = it.visit(parse_tree)

#Serializing json  
with open("../models/sample2.json", "w") as outfile:
    json.dump(data, outfile, indent = 3)