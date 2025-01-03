from abc import ABC, abstractmethod

class Trigger(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def serialize(self):
        return {}

#CLICKED_OBJECT
class TriggerClickedObject(Trigger):
    def __init__(self, object_id):
        self.object_id = object_id
    
    def serialize(self):
        return {
            'type' : 'CLICKED_OBJECT',
            'object' : self.object_id
        }
    
#CLICKED_HITBOX
class TriggerClickedHitbox(Trigger):
    def __init__(self, hitbox_id):
        self.hitbox_id = hitbox_id

    def serialize(self):
        return {
            'type' : 'CLICKED_HITBOX',
            'hitbox' : self.hitbox_id
        }
    
#CLICKED_NOT_OBJECT
class TriggerClickedNotObject(Trigger):
    def __init__(self, object_id):
        self.object_id = object_id

    def serialize(self):
        return {
            'type' : 'CLICKED_NOT_OBJECT',
            'object' : self.object_id
        }
    
#CLICKED_NOT_HITBOX
class TriggerClickedNotHitbox(Trigger):
    def __init__(self, hitbox_id):
        self.hitbox_id = hitbox_id

    def serialize(self):
        return {
            'type' : 'CLICKED_NOT_HITBOX',
            'hitbox' : self.hitbox_id
        }
    
#WHEN_OBJECT_IS_STATE
class TriggerWhenObjectIsView(Trigger):
    def __init__(self, object_id, view_id):
        self.object_id = object_id
        self.view_id = view_id

    def serialize(self):
        return {
            'type' : 'WHEN_OBJECT_IS_VIEW',
            'object' : self.object_id,
            'view' : self.view_id
        }

#AFTER_EVENT
class TriggerAfterEvent(Trigger):
    def __init__(self, event_id):
        self.event_id = event_id

    def serialize(self):
        return {
            'type' : 'AFTER_EVENT',
            'event' : self.event_id
        }

#ITEM_IS_IN_USE
class TriggerObjIsInUse(Trigger):
    def __init__(self, object):
        self.object = object

    def serialize(self):
        return {
            'type' : 'OBJ_IS_IN_USE',
            'object' : self.object
        }

#AFTER_TIME

class TriggerAfterTime(Trigger):
    def __init__(self, time):
        self.time = time

    def serialize(self):
        return {
            'type' : 'AFTER_TIME',
            'time' : self.time
        }
    
#IS_EQUAL_TO

class TriggerIsEqualTo(Trigger):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'IS_EQUAL_TO',
            'variable' : self.variable,
            'number' : self.number
        }

#IS_GREATER_THAN

class TriggerIsGreaterThan(Trigger):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'IS_GREATER_THAN',
            'variable' : self.variable,
            'number' : self.number
        }

#IS_LESS_THAN

class TriggerIsLessThan(Trigger):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'IS_LESS_THAN',
            'variable' : self.variable,
            'number' : self.number
        }

#IS_GREATER_THAN_OR_EQUAL_TO

class TriggerIsGreaterThanOrEqualTo(Trigger):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'IS_GREATER_THAN_OR_EQUAL_TO',
            'variable' : self.variable,
            'number' : self.number
        }

#IS_LESS_THAN_OR_EQUAL_TO

class TriggerIsLessThanOrEqualTo(Trigger):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def serialize(self):
        return {
            'type' : 'IS_LESS_THAN_OR_EQUAL_TO',
            'variable' : self.variable,
            'number' : self.number
        }