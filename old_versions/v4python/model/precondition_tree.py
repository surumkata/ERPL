from model.precondition import EventPreConditionsType

class PreConditionTree():
    def __init__(self,root):
        self.root = root

    def test_tree(self,room, inventory):
        return self.root.test_node(room, inventory)

def test_precondition(precondition, room, inventory):
    type = precondition.type
    tested = False
    if type == EventPreConditionsType.CLICK:
        object_id = precondition.object_id
        if not object_id in room.objects:
            return tested
        object = room.objects[object_id]
        if object.reference == room.er_state.current_scene:
            for (px,py) in room.er_state.click_events:
                tested = object.have_clicked(px,py)
                if tested: break
    elif type == EventPreConditionsType.CLICK_NOT:
        object_id = precondition.object_id
        if not object_id in room.objects or len(room.er_state.click_events) == 0:
            return tested
        object = room.objects[object_id]
        tested = True
        if object.reference == room.er_state.current_scene:
            for (px,py) in room.er_state.click_events:
                tested = tested and not object.have_clicked(px,py)
    elif type == EventPreConditionsType.CLICK_ITEM:
        item_id = precondition.item_id
        item = inventory.get_item(item_id)
        if item != None:
            for (px,py) in room.er_state.click_events:
                tested = item.have_clicked(px,py)
                if tested: break
    elif type == EventPreConditionsType.ACTIVE_WHEN_STATE:
        object_id = precondition.object_id
        state_id = precondition.state_id
        tested = room.check_state_of_object(object_id,state_id)
    elif type == EventPreConditionsType.ACTIVE_WHEN_NOT_STATE:
        object_id = precondition.object_id
        state_id = precondition.state_id
        tested = not room.check_state_of_object(object_id,state_id)
    elif type == EventPreConditionsType.ACTIVE_WHEN_ITEM_IN_USE:
        
        item_id = precondition.item_id
        tested = inventory.check_item_in_use(item_id)
    elif type == EventPreConditionsType.ACTIVE_WHEN_ITEM_NOT_IN_USE:
        item_id = precondition.item_id
        tested = inventory.exist_item(item_id)
        tested = tested and not inventory.check_item_in_use(item_id)
    elif type == EventPreConditionsType.CLICK_AFTER_EVENT:
        object_id = precondition.object_id
        object = room.objects[object_id]
        clicked = False
        if object.reference == room.er_state.current_scene:
            for (px,py) in room.er_state.click_events:
                clicked = object.have_clicked(px,py)
                if clicked:
                    break
        if clicked:
            event_id = precondition.event_id
            tested = room.check_if_event_occurred(event_id)
    else:
        print("ERRO TIPO DE EVENTO PRE")
        return False
    return tested

class PreConditionNode():
    def __init__(self,value,left,right, is_operator=False):
        self.value = value
        self.left = left
        self.right = right
        self.is_operator = is_operator

    def test_node(self, room, inventory):
        if self.is_operator:
            if self.value == "and":
                return self.left.test_node(room, inventory) and self.right.test_node(room, inventory)
            elif self.value == "or":
                return self.left.test_node(room, inventory) or self.right.test_node(room, inventory)
            elif self.value == "not":
                return not self.left.test_node(room, inventory)
        else:
            return test_precondition(self.value, room, inventory)
            #return testar self.value

class PreConditionOperatorAnd(PreConditionNode):
    def __init__(self, left, right):
        super().__init__("and", left, right, is_operator=True)

class PreConditionOperatorOr(PreConditionNode):
    def __init__(self, left, right):
        super().__init__("or", left, right, is_operator=True)

class PreConditionOperatorNot(PreConditionNode):
    def __init__(self, left):
        super().__init__("not", left, None, is_operator=True)

class PreConditionVar(PreConditionNode):
    def __init__(self, value):
        super().__init__(value, None, None)