from abc import ABC, abstractmethod
import pygame

class EventPreCondition(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def test(self,room,inventory):
        tested = False
        return tested

#CLICKED_OBJECT
class EventPreConditionClickedObject(EventPreCondition):
    def __init__(self, object_id):
        self.object_id = object_id

    def test(self,room,inventory,state):
        tested = False
        object_id = self.object_id
        if not object_id in room.objects or len(state.buffer_click_events) == 0:
            return tested
        object = room.objects[object_id]
        if object.reference == state.current_scenario:
            for (px,py) in state.buffer_click_events:
                tested = object.have_clicked(px,py) and object.current_view != None
                if tested:
                    break
        return tested
    
#CLICKED_HITBOX
class EventPreConditionClickedHitbox(EventPreCondition):
    def __init__(self, hitbox_id):
        self.hitbox_id = hitbox_id

    def test(self,room,inventory,state):
        tested = False
        hitbox_id = self.hitbox_id
        if not hitbox_id in room.scenarios[state.current_scenario].hitboxes or len(state.buffer_click_events) == 0:
            return tested

        for (px,py) in state.buffer_click_events:
            tested = room.scenarios[state.current_scenario].collide(px,py,hitbox_id)
            if tested:
                break
        return tested
    
#CLICKED_NOT_OBJECT
class EventPreConditionClickedNotObject(EventPreCondition):
    def __init__(self, object_id):
        self.object_id = object_id

    def test(self,room,inventory,state):
        tested = False
        object_id = self.object_id
        if not object_id in room.objects or len(state.buffer_click_events) == 0:
            return tested
        object = room.objects[object_id]
        tested = True
        if object.reference == state.current_scenario:
            for (px,py) in state.buffer_click_events:
                tested = tested and not object.have_clicked(px,py)
        return tested
    
#CLICKED_NOT_HITBOX
class EventPreConditionClickedNotHitbox(EventPreCondition):
    def __init__(self, hitbox_id):
        self.hitbox_id = hitbox_id

    def test(self,room,inventory,state):
        tested = False
        hitbox_id = self.hitbox_id
        if not hitbox_id in room.scenarios[state.current_scenario].hitboxes or len(state.buffer_click_events) == 0:
            return tested
        tested = True
        for (px,py) in state.buffer_click_events:
            tested = tested and not room.scenarios[state.current_scenario].collide(px,py,hitbox_id)
        return tested
    
#WHEN_OBJECT_IS_STATE
class EventPreConditionWhenObjectIsView(EventPreCondition):
    def __init__(self, object_id, view_id):
        self.object_id = object_id
        self.view_id = view_id

    def test(self,room,inventory,state):
        object_id = self.object_id
        view_id = self.view_id
        tested = room.check_view_of_object(object_id,view_id)
        return tested

#AFTER_EVENT
class EventPreConditionAfterEvent(EventPreCondition):
    def __init__(self, event_id):
        self.event_id = event_id

    def test(self,room,inventory,state):
        event_id = self.event_id
        tested = room.check_if_event_occurred(event_id)
        return tested

#ITEM_IS_IN_USE
class EventPreConditionItemIsInUse(EventPreCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def test(self,room,inventory,state):
        item_id = self.item_id
        tested = inventory.check_item_in_use(item_id)
        return tested

#ITEM_IS_NOT_IN_USE
class EventPreConditionItemNotInUse(EventPreCondition):
    def __init__(self, item_id):
        self.item_id = item_id

    def test(self,room,inventory,state):
        item_id = self.item_id
        tested = inventory.exist_item(item_id)
        tested = tested and not inventory.check_item_in_use(item_id)
        return tested

#CLICKED_ITEM
class EventPreConditionClickedItem(EventPreCondition):
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

#AFTER_TIME

class EventPreConditionAfterTime(EventPreCondition):
    def __init__(self, time):
        self.time = time

    def test(self, room, inventory, state):
        pygame_time = pygame.time.get_ticks()
        return self.time <= pygame_time
    
#IS_EQUAL_TO

class EventPreConditionIsEqualTo(EventPreCondition):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def test(self, room, inventory, state):
        if self.variable in room.variables:
            return room.variables[self.variable] == self.number
        else: return False

#IS_GREATER_THAN

class EventPreConditionIsGreaterThan(EventPreCondition):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def test(self, room, inventory, state):
        if self.variable in room.variables:
            return room.variables[self.variable] > self.number
        else: return False

#IS_LESS_THAN

class EventPreConditionIsLessThan(EventPreCondition):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def test(self, room, inventory, state):
        if self.variable in room.variables:
            return room.variables[self.variable] < self.number
        else: return False

#IS_GREATER_THAN_OR_EQUAL_TO

class EventPreConditionIsGreaterThanOrEqualTo(EventPreCondition):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def test(self, room, inventory, state):
        if self.variable in room.variables:
            return room.variables[self.variable] >= self.number
        else: return False

#IS_LESS_THAN_OR_EQUAL_TO

class EventPreConditionIsLessThanOrEqualTo(EventPreCondition):
    def __init__(self, variable, number):
        self.variable = variable
        self.number = number

    def test(self, room, inventory, state):
        if self.variable in room.variables:
            return room.variables[self.variable] <= self.number
        else: return False