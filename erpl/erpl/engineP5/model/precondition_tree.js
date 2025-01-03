// Classe PreConditionTree
 class PreConditionTree {
  constructor(root) {
      this.root = root;
  }

  testTree(room, inventory, state) {
      return this.root.testNode(room, inventory, state);
  }
}

// Classe PreConditionNode
 class PreConditionNode {
  constructor(value, left = null, right = null, isOperator = false) {
      this.value = value;
      this.left = left;
      this.right = right;
      this.isOperator = isOperator;
  }

  testNode(room, inventory, state) {
      if (this.isOperator) {
          if (this.value === "and") {
              return this.left.testNode(room, inventory, state) && this.right.testNode(room, inventory, state);
          } else if (this.value === "or") {
              return this.left.testNode(room, inventory, state) || this.right.testNode(room, inventory, state);
          } else if (this.value === "not") {
              return !this.left.testNode(room, inventory, state);
          }
      } else {
          return this.value.test(room, inventory, state);
      }
  }
}

// Classes para Operadores Lógicos
 class PreConditionOperatorAnd extends PreConditionNode {
  constructor(left, right) {
      super("and", left, right, true);
  }
}

 class PreConditionOperatorOr extends PreConditionNode {
  constructor(left, right) {
      super("or", left, right, true);
  }
}

 class PreConditionOperatorNot extends PreConditionNode {
  constructor(left) {
      super("not", left, null, true);
  }
}

// Classe PreConditionVar
 class PreConditionVar extends PreConditionNode {
  constructor(value) {
      super(value);
  }
}
