class EscapeRoom {
  // Construtor de escape room
  constructor(title) {
      this.title = title; // TITULO
      this.scenarios = {};
      this.objects = {};
      this.events = {};
      this.eventsBuffer = {};
      this.transitions = {};
      this.variables = {
        "_sucesses_" : 0.0,
        "_fails_" : 0.0
     }
  }

  // Função que add uma cena
  addScenario(scenario) {
      this.scenarios[scenario.id] = scenario;
  }

  // Função que add um objeto
  addObject(object) {
      this.objects[object.id] = object;
  }

  // Função que add um evento
  addEvent(event) {
      this.events[event.id] = event;
  }

  // Função que add uma transição
  addTransition(transition) {
      this.transitions[transition.id] = transition;
  }

  // Função que add uma transição
  addVariable(variable, number) {
    this.variables[variable] = number;
    }

  // Função que add um evento ao buffer
  addEventBuffer(id, preConditions, postConditions, repetitions) {
      this.eventsBuffer[id] = new EventEr(id, preConditions, postConditions, repetitions);
  }

  changeObjectCurrentView(objectId, viewId) {
      if (objectId in this.objects) {
          this.objects[objectId].changeCurrentView(viewId);
      }
  }

  changeObjectPosition(objectId, position) {
      if (objectId in this.objects) {
          this.objects[objectId].changePosition(position);
      }
  }

  changeObjectSize(objectId, size) {
      if (objectId in this.objects) {
          this.objects[objectId].changeSize(size);
      }
  }

  updateEvent(event) {
      if (event in this.events) {
          this.events[event].happen = true;
          this.events[event].repetitions -= 1;
      }
  }

  updateEventsBuffer() {
      for (let event of Object.values(this.eventsBuffer)) {
          this.events[event.id] = event;
      }
      this.eventsBuffer = {};
  }

  // Função que verifica se um evento aconteceu
  checkIfEventOccurred(eventId) {
      if (eventId in this.events) {
          return this.events[eventId].happen;
      }
      return false;
  }

  // Função que devolve a view atual de um objeto
  checkViewOfObject(objectId, viewId) {
      return objectId in this.objects ? this.objects[objectId].currentView === viewId : false;
  }
    
  //Função que desenha a cena atual
  draw(p5, currentScenario, invisibleViews = 0, hitboxs = false){
    //Desenhar cena atual
    if (currentScenario in this.scenarios){
      this.scenarios[currentScenario].draw(p5,this.variables);
    }
    else {
      return;
    }
    
    //Desenhar objetos dessa cena
    for (var objectId in this.objects){
      let object = this.objects[objectId];
      //desenhar objeto se pertencer à cena
      if (currentScenario == object.reference){
        object.draw(p5,invisibleViews,hitboxs);
      } 
    }
  }
}