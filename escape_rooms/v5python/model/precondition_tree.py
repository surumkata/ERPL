class PreConditionTree():
    def __init__(self,root):
        self.root = root

    def test_tree(self,room, inventory):
        return self.root.test_node(room, inventory)

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
            return self.value.test(room, inventory)
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