from enum import Enum

"""TIPOS DE then EVENTOS"""

class EventPosConditionsType(Enum):
    ENDGAME = 0
    CHANGE_STATE = 1
    CHANGE_POSITION = 2
    CHANGE_SIZE = 3
    SHOW_MESSAGE = 4
    ASK_CODE = 5
    PUT_INVENTORY = 6
    CHANGE_SCENE = 7
    ACTIVE_ITEM = 8
    DESACTIVE_ITEM = 9
    DELETE_ITEM = 10

class EventPosCondition:
    def __init__(self,type):
        self.type = type

#ENDGAME = 0
class EventPosConditionEndGame(EventPosCondition):
    def __init__(self, message = ""):
        super().__init__(EventPosConditionsType.ENDGAME)
        #self.message = message

#CHANGE_STATE = 1
class EventPosConditionChangeState(EventPosCondition):
    def __init__(self, object_id, state_id):
        super().__init__(EventPosConditionsType.CHANGE_STATE)
        self.object_id = object_id
        self.state_id = state_id

#CHANGE_POSITION = 2
class EventPosConditionChangePosition(EventPosCondition):
    def __init__(self, object_id, position):
        super().__init__(EventPosConditionsType.CHANGE_POSITION)
        self.object_id = object_id
        self.position = position

#CHANGE_SIZE = 3
class EventPosConditionChangeSize(EventPosCondition):
    def __init__(self, object_id, size):
        super().__init__(EventPosConditionsType.CHANGE_SIZE)
        self.object_id = object_id
        self.size = size

#SHOW_MESSAGE = 4
class EventPosConditionShowMessage(EventPosCondition):
    def __init__(self, position, message):
        super().__init__(EventPosConditionsType.SHOW_MESSAGE)
        self.position = position
        self.message = message

#ASK_CODE = 5
class EventPosConditionAskCode(EventPosCondition):
    def __init__(self, code, message, sucess_event, fail_event):
        super().__init__(EventPosConditionsType.ASK_CODE)
        self.code = code
        self.message = message
        self.sucess_event = sucess_event
        self.fail_event = fail_event

#PUT_INVENTORY = 6
class EventPosConditionPutInventory(EventPosCondition):
    def __init__(self, object_id):
        super().__init__(EventPosConditionsType.PUT_INVENTORY)
        self.object_id = object_id

#CHANGE_SCENE = 7
class EventPosConditionChangeScene(EventPosCondition):
    def __init__(self, scene_id):
        super().__init__(EventPosConditionsType.CHANGE_SCENE)
        self.scene_id = scene_id

#ACTIVE_ITEM = 8
class EventPosConditionActiveItem(EventPosCondition):
    def __init__(self, item_id):
        super().__init__(EventPosConditionsType.ACTIVE_ITEM)
        self.item_id = item_id

#DESACTIVE_ITEM = 8
class EventPosConditionDesactiveItem(EventPosCondition):
    def __init__(self, item_id):
        super().__init__(EventPosConditionsType.DESACTIVE_ITEM)
        self.item_id = item_id

#DELETE_ITEM = 8
class EventPosConditionDeleteItem(EventPosCondition):
    def __init__(self, item_id):
        super().__init__(EventPosConditionsType.DELETE_ITEM)
        self.item_id = item_id

