class TriggerNode():
    def __init__(self,value,left,right, is_operator=False):
        self.value = value
        self.left = left
        self.right = right
        self.is_operator = is_operator

    def serialize(self):
        if self.is_operator:
            if self.value == "and":
                return {
                    'operator' : 'AND',
                    'left' : self.left.serialize(),
                    'right' : self.right.serialize()
                }
            elif self.value == "or":
                return {
                    'operator' : 'OR',
                    'left' : self.left.serialize(),
                    'right' : self.right.serialize()
                }
            elif self.value == "not":
                return {
                    'operator' : 'NOT',
                    'left' : self.left.serialize()
                }
        else:
            return {'var':self.value.serialize()}
            #return testar self.value

class NodeAnd(TriggerNode):
    def __init__(self, left, right):
        super().__init__("and", left, right, is_operator=True)

class NodeOr(TriggerNode):
    def __init__(self, left, right):
        super().__init__("or", left, right, is_operator=True)

class NodeNot(TriggerNode):
    def __init__(self, left):
        super().__init__("not", left, None, is_operator=True)

class NodeVar(TriggerNode):
    def __init__(self, value):
        super().__init__(value, None, None)

class TriggerTree():
    def __init__(self,root:TriggerNode):
        self.root = root
    
    def serialize(self):
        return self.root.serialize()