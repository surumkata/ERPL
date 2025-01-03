from .trigger_tree import TriggerTree
from .action import Action
class Event:
    def __init__(self, id : str, triggers : TriggerTree, actions : [Action], repetitions : int):
       self.id = id
       self.triggers = triggers
       self.actions = actions
       self.repetitions = repetitions

    def serialize(self):
        actions = [action.serialize() for action in self.actions]
        triggers = self.triggers.serialize()

        return {
            'id' : self.id,
            'preconditions' : triggers,
            'posconditions' : actions,
            'repetitions' : self.repetitions
        }