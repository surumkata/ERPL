from abc import ABC, abstractmethod


#"""TIPOS DE if EVENTOS"""
#    CLICK = 0
#    CLICK_AFTER_EVENT = 1
#    ACTIVE_BY_EVENT = 2
#    ACTIVE_AFTER_EVENT = 3
#    ACTIVE_AFTER_TIME = 4
#    ACTIVE_WHEN_STATE = 5
#    ACTIVE_WHEN_NOT_STATE = 6
#    ACTIVE_WHEN_ITEM_IN_USE = 7
#    ACTIVE_WHEN_ITEM_NOT_IN_USE = 8
#    CLICK_ITEM = 9
#    CLICK_NOT = 10

class EventPreCondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def test(self,room,inventory):
        tested = False
        return tested

#CLICK = 0
class EventPreConditionClick(EventPreCondition):
    def __init__(self, object_id):
        self.object_id = object_id

    def test(self,room,inventory,state):
        tested = False
        object_id = self.object_id
        if not object_id in room.objects:
            return tested
        object = room.objects[object_id]
        if object.reference == state.current_scene:
            for (px,py) in state.buffer_click_events:
                tested = object.have_clicked(px,py)
                if tested:
                    break
        return tested

#CLICK_AFTER_EVENT = 1
class EventPreConditionClickAfterEvent(EventPreCondition):
    def __init__(self, object_id, event_id):
        self.object_id = object_id
        self.event_id = event_id

    def test(self,room,inventory,state):
        tested = False
        return tested

#ACTIVE_BY_EVENT = 2
class EventPreConditionActiveByEvent(EventPreCondition):
    def __init__(self, event_id):
        self.event_id = event_id

    def test(self,room,inventory,state):
        tested = False
        return tested

#ACTIVE_AFTER_EVENT = 3
class EventPreConditionActiveAfterEvent(EventPreCondition):
    def __init__(self, event_id):
        self.event_id = event_id

    def test(self,room,inventory,state):
        tested = False
        object_id = self.object_id
        object = room.objects[object_id]
        clicked = False
        if object.reference == state.current_scene:
            for (px,py) in state.buffer_click_events:
                clicked = object.have_clicked(px,py)
                if clicked:
                    break
        if clicked:
            event_id = self.event_id
            tested = room.check_if_event_occurred(event_id)
        return tested

#ACTIVE_AFTER_TIME = 4
class EventPreConditionActiveAfterTime(EventPreCondition):
    def __init__(self, time):
        self.time = time

    def test(self,room,inventory,state):
        tested = False
        return tested

#ACTIVE_WHEN_STATE = 5
class EventPreConditionActiveWhenState(EventPreCondition):
    def __init__(self, object_id, state_id):
        self.object_id = object_id
        self.state_id = state_id

    def test(self,room,inventory,state):
        object_id = self.object_id
        state_id = self.state_id
        tested = room.check_state_of_object(object_id,state_id)
        return tested

#ACTIVE_WHEN_STATES = 6
class EventPreConditionActiveWhenNotState(EventPreCondition):
    def __init__(self, object_id, state_id):
        self.object_id = object_id
        self.state_id = state_id

    def test(self,room,inventory,state):
        object_id = self.object_id
        state_id = self.state_id
        tested = not room.check_state_of_object(object_id,state_id)
        return tested

#ACTIVE_WHEN_ITEM_IN_USE = 7  
class EventPreConditionActiveWhenItemInUse(EventPreCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def test(self,room,inventory,state):
        item_id = self.item_id
        tested = inventory.check_item_in_use(item_id)
        return tested

#ACTIVE_WHEN_ITEM_NOT_IN_USE = 8
class EventPreConditionActiveWhenItemNotInUse(EventPreCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def test(self,room,inventory,state):
        item_id = self.item_id
        tested = inventory.exist_item(item_id)
        tested = tested and not inventory.check_item_in_use(item_id)
        return tested

#CLICK_ITEM = 9
class EventPreConditionClickItem(EventPreCondition):
    def __init__(self, item_id):
        self.item_id = item_id
    
    def test(self,room,inventory,state):
        tested = False
        item_id = self.item_id
        item = inventory.get_item(item_id)
        if item != None:
            for (px,py) in state.buffer_click_events:
                tested = item.have_clicked(px,py)
                if tested: break
        return tested

#CLICKNOT = 10
class EventPreConditionClickNot(EventPreCondition):
    def __init__(self, object_id):
        self.object_id = object_id

    def test(self,room,inventory,state):
        tested = False
        object_id = self.object_id
        if not object_id in room.objects or len(state.buffer_click_events) == 0:
            return tested
        object = room.objects[object_id]
        tested = True
        if object.reference == state.current_scene:
            for (px,py) in state.buffer_click_events:
                tested = tested and not object.have_clicked(px,py)
        return tested
    
