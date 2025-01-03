import os

WIDTH, HEIGHT = 1280,720
HEIGHT_INV = HEIGHT * 0.15


current_folder = os.path.dirname(__file__)

"""CLASSE AUXIALIRES"""
class Position():
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y

class Size():
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y

class ObjText:
    def __init__(self,text:str,x:float,y:float,size:int,color:str,text_format : bool = False):
        self.size = int(size)
        self.color = color
        self.text = text
        self.x = x
        self.y = y
        self.text_format = text_format