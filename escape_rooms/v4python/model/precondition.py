from enum import Enum


"""TIPOS DE if EVENTOS"""
class EventPreConditionsType(Enum):
    CLICK = 0
    CLICK_AFTER_EVENT = 1
    ACTIVE_BY_EVENT = 2
    ACTIVE_AFTER_EVENT = 3
    ACTIVE_AFTER_TIME = 4
    ACTIVE_WHEN_STATE = 5
    ACTIVE_WHEN_NOT_STATE = 6
    ACTIVE_WHEN_ITEM_IN_USE = 7
    ACTIVE_WHEN_ITEM_NOT_IN_USE = 8
    CLICK_ITEM = 9
    CLICK_NOT = 10

class EventPreCondition:
    def __init__(self,type):
        self.type = type

#CLICK = 0
class EventPreConditionClick(EventPreCondition):
    def __init__(self, object_id):
        super().__init__(EventPreConditionsType.CLICK)
        self.object_id = object_id

#CLICK_AFTER_EVENT = 1
class EventPreConditionClickAfterEvent(EventPreCondition):
    def __init__(self, object_id, event_id):
        super().__init__(EventPreConditionsType.CLICK_AFTER_EVENT)
        self.object_id = object_id
        self.event_id = event_id

#ACTIVE_BY_EVENT = 2
class EventPreConditionActiveByEvent(EventPreCondition):
    def __init__(self, event_id):
        super().__init__(EventPreConditionsType.ACTIVE_BY_EVENT)
        self.event_id = event_id

#ACTIVE_AFTER_EVENT = 3
class EventPreConditionActiveAfterEvent(EventPreCondition):
    def __init__(self, event_id):
        super().__init__(EventPreConditionsType.ACTIVE_AFTER_EVENT)
        self.event_id = event_id

#ACTIVE_AFTER_TIME = 4
class EventPreConditionActiveAfterTime(EventPreCondition):
    def __init__(self, time):
        super().__init__(EventPreConditionsType.ACTIVE_AFTER_TIME)
        self.time = time

#ACTIVE_WHEN_STATE = 5
class EventPreConditionActiveWhenState(EventPreCondition):
    def __init__(self, object_id, state_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_STATE)
        self.object_id = object_id
        self.state_id = state_id

#ACTIVE_WHEN_STATES = 6
class EventPreConditionActiveWhenNotState(EventPreCondition):
    def __init__(self, object_id, state_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_NOT_STATE)
        self.object_id = object_id
        self.state_id = state_id

#ACTIVE_WHEN_ITEM_IN_USE = 7  
class EventPreConditionActiveWhenItemInUse(EventPreCondition):
    def __init__(self, item_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_ITEM_IN_USE)
        self.item_id = item_id

#ACTIVE_WHEN_ITEM_NOT_IN_USE = 8
class EventPreConditionActiveWhenItemNotInUse(EventPreCondition):
    def __init__(self, item_id):
        super().__init__(EventPreConditionsType.ACTIVE_WHEN_ITEM_NOT_IN_USE)
        self.item_id = item_id

#CLICK_ITEM = 9
class EventPreConditionClickItem(EventPreCondition):
   def __init__(self, item_id):
        super().__init__(EventPreConditionsType.CLICK_ITEM)
        self.item_id = item_id 

#CLICKNOT = 10
class EventPreConditionClickNot(EventPreCondition):
    def __init__(self, object_id):
        super().__init__(EventPreConditionsType.CLICK_NOT)
        self.object_id = object_id
    
