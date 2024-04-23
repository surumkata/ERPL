from .precondition_tree import PreConditionTree
from .poscondition import EventPosCondition
import sys

class Event:
    def __init__(self, id : str, pre_conditions : PreConditionTree, pos_conditions : [EventPosCondition], repetitions : int):
       self.id = id
       self.pre_conditions = pre_conditions
       self.pos_conditions = pos_conditions
       self.repetitions = repetitions
       self.happen = False

       self.inifity_repetitions = True if self.repetitions == None else False