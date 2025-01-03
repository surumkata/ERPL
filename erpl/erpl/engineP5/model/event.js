class EventEr {
  constructor(id, preConditions, posConditions, repetitions) {
    this.id = id;
    this.preConditions = preConditions;
    this.posConditions = posConditions;
    this.repetitions = repetitions;
    this.happen = false;
  }
}