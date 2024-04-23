#!/usr/bin/python3
from lark.visitors import Interpreter
from lark import Lark
import os
import json
cf = os.path.dirname(__file__)

class ObjInterpreter(Interpreter):
    def __init__(self,id, current_folder):
        self.object = {'states' : []}
        self.id = id
        self.current_folder = current_folder

    def start(self,start):
        '''start : estados sons? estado_inicial? posicao? tamanho?'''
        elems = start.children
        #visitar estados
        self.visit(elems[0])
        i = 1
        if len(elems) > i and elems[i].data == 'sons':
            self.visit(elems[i])
            i+=1

        if len(elems) > i and elems[i].data == 'estado_inicial':
            id = self.visit(elems[i])
            for state in self.object['states']:
                if state['id'] == id:
                    self.object['initial_state'] = id
            else:
                pass
                #TODO:print error
            i+=1
        if len(elems) > i and elems[i].data == "posicao":
            self.object['position'] = self.visit(elems[i])
            i+=1
        if len(elems) > i and elems[i].data == "tamanho":
            self.object['size'] = self.visit(elems[i])
        return self.object

    def estados(self,estados):
        '''estados : "Estados:" estado+'''
        elems = estados.children
        for elem in elems:
            result = self.visit(elem)
            self.object['states'].append(result)

    def sons(self,sons):
        '''sons : "Sons:" som+'''
        elems = sons.children
        for elem in elems:
            result = self.visit(elem)
            if 'sounds' in self.object:
                self.object['sounds'].append(result)
            else:
                self.object['sounds'] = [result]

    
    def estado_animado(self,estado_animado):
        '''estado  : "- Estado animado" ID ":" imagens repiticoes timesprite'''
        elems = estado_animado.children
        id = elems[0].value
        srcs = self.visit(elems[1])
        rs = self.visit(elems[2])
        ts = self.visit(elems[3])
        return {
            'id' : self.id + '_' + id,
            'images' : srcs,
            'repetitions' : rs,
            'time_sprite' : ts
        }

    def estado_simples(self,estado_simples):
        '''estado : "- Estado" ID ":" imagem'''
        elems = estado_simples.children
        id = elems[0].value
        src = self.visit(elems[1])
        return {
            'id' : self.id + '_' + id,
            'image' : src
        }

    def som(self, som):
        '''som : "Som" ID ":" fonte'''
        elems = som.children
        id = elems[0].value
        src = self.visit(elems[1])
        return {
            'id' : self.id + '_' + id,
            'source' : src
        }

    def imagens(self,imagens):
        '''imagens : "- Imagens:" "[" TEXTO ("," TEXTO)* "]"'''
        elems = imagens.children
        srcs = []
        for elem in elems:
            src = f"{self.current_folder}/../assets/objects/{self.id}/{elem.value[1:-1]}"
            file = open(src)
            src = os.path.realpath(file.name)
            file.close()
            srcs.append(src)
        return srcs

    def imagem(self,imagem):
        '''imagem  : "- Imagem:" TEXTO'''
        elems = imagem.children
        src = f"{cf}/../assets/objects/"+self.id+"/"+elems[0].value[1:-1]
        file = open(src)
        src = os.path.realpath(file.name)
        file.close()
        return src
    
    def fonte(self,fonte):
        '''fonte  : "- Fonte:" TEXTO'''
        elems = fonte.children
        src = f"{cf}/../assets/objects/"+self.id+"/"+elems[0].value[1:-1]
        file = open(src)
        src = os.path.realpath(file.name)
        file.close()
        return src

    def repiticoes(self,repiticoes):
        '''repiticoes: "- Repitições:" NUM'''
        elems = repiticoes.children
        rs = int(elems[0].value)
        return rs

    def timesprite(self,timesprite):
        '''timesprite: "- Time-Sprite:" NUM'''
        elems = timesprite.children
        ts = int(elems[0].value)
        return ts

    def estado_inicial(self,estado_inicial):
        '''estado_inicial: "- Estado inicial:" ID'''
        elems = estado_inicial.children
        id = self.id + '_' + elems[0].value
        return id

    def posicao(self,posicao):
        '''posicao: "- Posição:" "(" NUM "," NUM ")"'''
        elems = posicao.children
        x = int(elems[0].value)
        y = int(elems[0].value)
        return (x,y)

    def tamanho(self,tamanho):
        '''tamanho: "- Tamanho:" "[" NUM "," NUM "]"'''
        elems = tamanho.children
        w = int(elems[0].value)
        h = int(elems[0].value)
        return (w,h)
    
def parse_obj(obj_id, current_folder):
    grammar = open(f"{cf}/grammar_erobj.txt","r")

    file = open(f"{cf}/../assets/objects/{obj_id}/{obj_id}.erobj")
    code = file.read()
    file.close()

    # analisar frase com a gramatica definida
    p = Lark(grammar)
    parse_tree = p.parse(code)
    it = ObjInterpreter(obj_id,current_folder)
    data = it.visit(parse_tree)

    return data