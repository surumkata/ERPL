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
        '''start : views sounds? view_inicial? position? size?'''
        elems = start.children
        #visitar views
        self.visit(elems[0])
        i = 1
        if len(elems) > i and elems[i].data == 'sounds':
            self.visit(elems[i])
            i+=1

        if len(elems) > i and elems[i].data == 'view_inicial':
            id = self.visit(elems[i])
            for state in self.object['states']:
                if state['id'] == id:
                    self.object['initial_state'] = id
            else:
                pass
                #TODO:print error
            i+=1
        if len(elems) > i and elems[i].data == "position":
            self.object['position'] = self.visit(elems[i])
            i+=1
        if len(elems) > i and elems[i].data == "size":
            self.object['size'] = self.visit(elems[i])
        return self.object

    def views(self,views):
        '''views : "Views:" view+'''
        elems = views.children
        for elem in elems:
            result = self.visit(elem)
            self.object['states'].append(result)

    def sounds(self,sounds):
        '''sounds : "Sons:" sound+'''
        elems = sounds.children
        for elem in elems:
            result = self.visit(elem)
            if 'sounds' in self.object:
                self.object['sounds'].append(result)
            else:
                self.object['sounds'] = [result]

    
    def view_animado(self,view_animado):
        '''view  : "- View animado" ID ":" images repiticoes timesprite'''
        elems = view_animado.children
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

    def view_simples(self,view_simples):
        '''view : "- View" ID ":" image'''
        elems = view_simples.children
        id = elems[0].value
        src = self.visit(elems[1])
        return {
            'id' : self.id + '_' + id,
            'image' : src
        }

    def sound(self, sound):
        '''sound : "Sound" ID ":" source'''
        elems = sound.children
        id = elems[0].value
        src = self.visit(elems[1])
        return {
            'id' : self.id + '_' + id,
            'source' : src
        }

    def images(self,images):
        '''images : "- Imagens:" "[" TEXTO ("," TEXTO)* "]"'''
        elems = images.children
        srcs = []
        for elem in elems:
            src = f"{self.current_folder}/../assets/objects/{self.id}/{elem.value[1:-1]}"
            file = open(src)
            src = os.path.realpath(file.name)
            file.close()
            srcs.append(src)
        return srcs

    def image(self,image):
        '''image  : "- Imagem:" TEXTO'''
        elems = image.children
        src = f"{cf}/../assets/objects/"+self.id+"/"+elems[0].value[1:-1]
        file = open(src)
        src = os.path.realpath(file.name)
        file.close()
        return src
    
    def source(self,source):
        '''source  : "- Fonte:" TEXTO'''
        elems = source.children
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

    def view_inicial(self,view_inicial):
        '''view_inicial: "- View inicial:" ID'''
        elems = view_inicial.children
        id = self.id + '_' + elems[0].value
        return id

    def position(self,position):
        '''position: "- Posição:" "(" NUM "," NUM ")"'''
        elems = position.children
        x = int(elems[0].value)
        y = int(elems[0].value)
        return (x,y)

    def size(self,size):
        '''size: "- Tamanho:" "[" NUM "," NUM "]"'''
        elems = size.children
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