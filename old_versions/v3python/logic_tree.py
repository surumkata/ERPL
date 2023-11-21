from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
from lark import Lark,Discard ,Token,Tree

class Node:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Variable:
    def __init__(self, name):
        self.name = name

    def evaluate(self, variables):
        return variables.get(self.name, False)
    
    def __str__(self):
        return str(self.name)

class Operator:
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, variables):
        if self.operator == 'AND':
            return self.left.evaluate(variables) and self.right.evaluate(variables)
        elif self.operator == 'OR':
            return self.left.evaluate(variables) or self.right.evaluate(variables)
        elif self.operator == 'NOT':
            return not self.left.evaluate(variables)
    
    def __str__(self):
        if self.operator != 'NOT':
            return "(" + str(self.left) + " " + str(self.operator) + " " + str(self.right) + ")"
        else:
            return str(self.operator) + " " + str(self.left)

class Tree:
    def __init__(self, value):
        self.root = Node(value)

    def evaluate_tree(self,variables):
        if isinstance(self.root, Node):
            node_value = self.root.value
            if isinstance(node_value, Variable):
                return self.evaluate(variables)
            elif isinstance(node_value, Operator):
                if node_value.operator == 'NOT':  # NOT operator
                    return node_value.evaluate(variables)
                elif node_value.operator == 'AND' or node_value.operator == 'OR':  # AND or OR operator
                    left_result = node_value.left.evaluate(variables)
                    right_result = node_value.right.evaluate(variables)
                    if node_value.operator == 'AND':
                        return left_result and right_result
                    elif node_value.operator == 'OR':
                        return left_result or right_result
                else:
                    raise ValueError(f"Operador desconhecido: {node_value.operator}")
        else:
            raise ValueError(f"ERROR INSTANCE")
            
    def __str__(self):
        return "TREE: " + str(self.root)
        
grammar ="""
start: expression

expression: VAR -> var
          | expression "AND" expression  -> and_
          | expression "OR" expression  -> or_
          | "NOT" expression  -> not_
          | "(" expression ")"  -> group

          
%import common.WS
%ignore WS
%import common.CNAME
VAR: CNAME
"""

# Crie o analisador Lark
parser = Lark(grammar)

class Interpreter(Interpreter):

    def start(self,start):
        elems = start.children
        node = self.visit(elems[0])
        return {"tree" : node}

    def and_(self, items):
        elems = items.children
        left = self.visit(elems[0])
        right = self.visit(elems[1])
        return {"operator" : "and",
                "left" : left,
                "right" : right}

    def or_(self, items):
        elems = items.children
        left = self.visit(elems[0])
        right = self.visit(elems[1])
        return {"operator" : "or",
                "left" : left,
                "right" : right}

    def not_(self, items):
        elems = items.children
        left = self.visit(elems[0])
        right = None
        return {"operator" : "not",
                "left" : left,
                "right" : right}

    def group(self, items):
        return self.visit(items.children[0])

    def var(self, token):
        return {"variable" : token.children[0].value}



# Exemplo de uso:
input_expression = "A OR NOT(B AND C)"
tree = parser.parse(input_expression)
it = Interpreter()
parsed_expression = it.visit(tree)
print(parsed_expression)



variables = {'A': True, 'B': False, 'C': False}

t = parsed_expression['tree']

def write_tree(tree):
    if 'operator' in tree:
        if tree['operator'] == 'not':
            return tree['operator'] + ' ' + write_tree(tree['left'])
        else:
            return "(" + write_tree(tree['left']) + ' ' + tree['operator'] + ' ' + write_tree(tree['right']) + ")"
    elif 'variable' in tree:
        return tree['variable']
    
print(write_tree(t))