from .precondition_tree import PreConditionTree
from .poscondition import EventPosCondition

class Event:
    def __init__(self, id : str, pre_conditions : PreConditionTree, pos_conditions : [EventPosCondition], repeatable : int, linked : bool = False):
       self.id = id
       self.pre_conditions = pre_conditions
       self.pos_conditions = pos_conditions
       self.repeatable = repeatable
       self.happen = False
       self.linked = linked