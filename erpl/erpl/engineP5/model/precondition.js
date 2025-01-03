// Classe abstrata EventPreCondition
class EventPreCondition {
  constructor() {}

  // Método abstrato test
  test(room, inventory, state) {
      return false; // Implementação deve ser sobrescrita nas subclasses
  }
}

// Subclasse EventPreConditionClickedObject
class EventPreConditionClickedObject extends EventPreCondition {
  constructor(objectId) {
      super();
      this.objectId = objectId;
  }

  test(room, inventory, state) {
      let tested = false;
      const objectId = this.objectId;
      if (!room.objects.hasOwnProperty(objectId)) {
          return tested;
        }
        const object = room.objects[objectId];
        if (object.reference === state.currentScenario) {
            for (const [mX,mY] of state.bufferClickEvents) {
                tested = object.haveClicked(mX,mY);
                if (tested) {
                    break;
                }
          }
      }
      return tested;
  }
}

// Subclasse EventPreConditionClickedNotObject
class EventPreConditionClickedNotObject extends EventPreCondition {
  constructor(objectId) {
      super();
      this.objectId = objectId;
  }

  test(room, inventory, state) {
      let tested = false;
      const objectId = this.objectId;
      if (!room.objects.hasOwnProperty(objectId) || state.bufferClickEvents.length === 0) {
          return tested;
      }
      const object = room.objects[objectId];
      tested = true;
      if (object.reference === state.currentScenario) {
        for (const [mX,mY] of state.bufferClickEvents) {
              tested = tested && !object.haveClicked(mX,mY);
          }
      }
      return tested;
  }
}

// Subclasse EventPreConditionClickedObject
class EventPreConditionClickedHitbox extends EventPreCondition {
    constructor(hitboxId) {
        super();
        this.hitboxId = hitboxId;
    }
  
    test(room, inventory, state) {
        let tested = false;
        const hitboxId = this.hitboxId;
        if(state.currentScenario == undefined || state.currentScenario == null){
            return tested;
        }
        if (!room.scenarios[state.currentScenario].hitboxes.hasOwnProperty(hitboxId) || state.bufferClickEvents.length === 0){
            return tested;
        }
        for (const [mX,mY] of state.bufferClickEvents) {
            tested = room.scenarios[state.currentScenario].collide(mX,mY,hitboxId)
            if (tested) {
                break;
            }
        }
        return tested;
    }
  }
  
  // Subclasse EventPreConditionClickedNotObject
  class EventPreConditionClickedNotHitbox extends EventPreCondition {
    constructor(hitboxId) {
        super();
        this.hitboxId = hitboxId;
    }
  
    test(room, inventory, state) {
        let tested = false;
        const hitboxId = this.hitboxId;

        if(state.currentScenario == undefined || state.currentScenario == null){
            return tested;
        }
        if (!room.scenarios[state.currentScenario].hitboxes.hasOwnProperty(hitboxId) || state.bufferClickEvents.length === 0){
            return tested;
        }
        tested = true;
        for (const [mX,mY] of state.bufferClickEvents) {
            tested = tested && !room.scenarios[state.currentScenario].collide(mX,mY,hitboxId)
        }
        return tested;
    }
  }

// Subclasse EventPreConditionWhenObjectIsView
class EventPreConditionWhenObjectIsView extends EventPreCondition {
  constructor(objectId, viewId) {
      super();
      this.objectId = objectId;
      this.viewId = viewId;
  }

  test(room, inventory, state) {
      const objectId = this.objectId;
      const viewId = this.viewId;
      return room.checkViewOfObject(objectId, viewId);
  }
}

// Subclasse EventPreConditionAfterEvent
class EventPreConditionAfterEvent extends EventPreCondition {
  constructor(eventId) {
      super();
      this.eventId = eventId;
  }

  test(room, inventory, state) {
      const eventId = this.eventId;
      return room.checkIfEventOccurred(eventId);
  }
}

// Subclasse EventPreConditionItemIsInUse
class EventPreConditionItemIsInUse extends EventPreCondition {
  constructor(itemId) {
      super();
      this.itemId = itemId;
  }

  test(room, inventory, state) {
      const itemId = this.itemId;
      return inventory.checkItemInUse(itemId);
  }
}

// Subclasse EventPreConditionItemNotInUse
class EventPreConditionItemNotInUse extends EventPreCondition {
  constructor(itemId) {
      super();
      this.itemId = itemId;
  }

  test(room, inventory, state) {
      const itemId = this.itemId;
      return inventory.existItem(itemId) && !inventory.checkItemInUse(itemId);
  }
}

// Subclasse EventPreConditionClickedItem
class EventPreConditionClickedItem extends EventPreCondition {
  constructor(itemId) {
      super();
      this.itemId = itemId;
  }

  test(room, inventory, state) {
      let tested = false;
      const itemId = this.itemId;
      const item = inventory.getItem(itemId);
      if (item !== null) {
          for (const [mX, mY] of state.bufferClickEvents) {
              tested = item.haveClicked(mX, mY);
              if (tested) {
                  break;
              }
          }
      }
      return tested;
  }
}

// Subclasse EventPreConditionAfterTime
class EventPreConditionAfterTime extends EventPreCondition {
  constructor(time) {
      super();
      this.time = time;
  }

  test(room, inventory, state) {
      const d = new Date();
      let time = d.getTime();
      return this.time <= (time - state.time);
  }
}

// Subclasse EventPreConditionIsEqualTo
class EventPreConditionIsEqualTo extends EventPreCondition {
    constructor(variable,number) {
        super();
        this.variable = variable;
        this.number = number;
    }
  
    test(room, inventory, state) {
        if(room.variables.hasOwnProperty(this.variable)){
            return room.variables[this.variable] == this.number
        }
        else return false;
    }
  }

// Subclasse EventPreConditionIsGreaterThan
class EventPreConditionIsGreaterThan extends EventPreCondition {
    constructor(variable,number) {
        super();
        this.variable = variable;
        this.number = number;
    }
  
    test(room, inventory, state) {
        if(room.variables.hasOwnProperty(this.variable)){
            return room.variables[this.variable] > this.number
        }
        else return false;
    }
  }


  // Subclasse EventPreConditionIsLessThan
class EventPreConditionIsLessThan extends EventPreCondition {
    constructor(variable,number) {
        super();
        this.variable = variable;
        this.number = number;
    }
  
    test(room, inventory, state) {
        if(room.variables.hasOwnProperty(this.variable)){
            return room.variables[this.variable] < this.number
        }
        else return false;
    }
  }

    // Subclasse EventPreConditionIsGreaterThanOrEqualTo
class EventPreConditionIsGreaterThanOrEqualTo extends EventPreCondition {
    constructor(variable,number) {
        super();
        this.variable = variable;
        this.number = number;
    }
  
    test(room, inventory, state) {
        if(room.variables.hasOwnProperty(this.variable)){
            return room.variables[this.variable] >= this.number
        }
        else return false;
    }
  }

      // Subclasse EventPreConditionIsLessThanOrEqualTo
class EventPreConditionIsLessThanOrEqualTo extends EventPreCondition {
    constructor(variable,number) {
        super();
        this.variable = variable;
        this.number = number;
    }
  
    test(room, inventory, state) {
        if(room.variables.hasOwnProperty(this.variable)){
            return room.variables[this.variable] <= this.number
        }
        else return false;
    }
  }