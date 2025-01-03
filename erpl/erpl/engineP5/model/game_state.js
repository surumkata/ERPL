/* CLASSE DE DO ESTADO DE UMA ESCAPE ROOM */
const State = Object.freeze({
  FINISH: 0,
  RUNNING: 1,
  CHALLENGE_MODE: 2,
  TRANSITION_MODE: 3,
  CHALLENGE_LISTENNING: 4
});

class GameState {
  constructor(size) {
      // Propriedades
      this.currentScenario = null;
      const d = new Date();
      let time = d.getTime();
      this.time = time;
      this.size = size;

      // Estado
      this.state = State.RUNNING;
      this.challenge = null;
      this.transition = null;

      // Buffers
      this.bufferClickEvents = [];
      this.bufferCurrentScenario = null;
      this.bufferMessages = [];
      this.bufferObjViews = {};
      this.bufferEventsHappened = [];

      this.inputElem = null;
  }

  updateBuffers(room) {
      // Atualiza os eventos que foram feitos
      for (let event of this.bufferEventsHappened) {
          room.updateEvent(event);
      }
      this.bufferEventsHappened = [];

      // Adiciona os eventos do buffer à sala
      room.updateEventsBuffer();

      // Atualiza as visualizações dos objetos
      for (let [obj, objView] of Object.entries(this.bufferObjViews)) {
          room.changeObjectCurrentView(obj, objView);
      }
      this.bufferObjViews = {};

      // Atualiza o cenário atual
      if (this.bufferCurrentScenario !== null) {
          this.currentScenario = this.bufferCurrentScenario;
      }

      // Reseta
      this.resetBuffers();
  }

  resetBuffers() {
      this.bufferClickEvents = [];
      this.bufferCurrentScenario = null;
      this.bufferObjViews = {};
      this.bufferEventsHappened = [];
  }

  drawMessages(p5) {
      for (let message of this.bufferMessages) {
          message.display(p5);
      }
  }

  firstScenario(scenarioId) {
      if (this.currentScenario === null) {
          this.currentScenario = scenarioId;
      }
  }

  updateCurrentScenario(scenarioId) {
      this.currentScenario = scenarioId;
  }

  isChallengeMode() {
      return this.state === State.CHALLENGE_MODE;
  }

  isChallengeListening() {
      return this.state === State.CHALLENGE_LISTENNING;
  }

  isRunning() {
      return this.state === State.RUNNING;
  }

  isFinished() {
      return this.state === State.FINISH;
  }

  isTransition() {
      return this.state === State.TRANSITION_MODE;
  }

  finishGame(message) {
      this.state = State.FINISH;
      this.endMessage = message;
  }

  activeChallengeMode(challenge) {
      this.challenge = challenge;
      this.state = State.CHALLENGE_MODE;
  }

  activeListeningChallengeMode(challenge) {
      this.challenge = challenge;
      this.state = State.CHALLENGE_LISTENNING;
  }

  activeTransitionMode(transition) {
      this.transition = transition;
      //this.transition.defineSize(this.size);
      //this.transition.playMusic();
      this.state = State.TRANSITION_MODE;
  }

  desactivateChallengeMode() {
      this.challenge = null;
      this.state = State.RUNNING;
      this.inputElem.hide();
  }

  desactivateTransitionMode() {
      this.bufferCurrentScenario = this.transition.nextScenario;
      this.state = State.RUNNING;
      this.transition = null;
  }

  drawFinishScreen(p5) {
    // Fundo colorido
    p5.background(150); // Cinza (equivalente a Color.GRAY no pygame)
  
    // Definir a cor do texto (equivalente a Color.WHITE no pygame)
    p5.fill(255); // Branco
  
    // Definir a fonte e tamanho do texto
    p5.textSize(26);
    p5.textAlign(p5.CENTER, p5.CENTER); // Centralizar o texto horizontalmente e verticalmente
  
    // Desenhar o texto na tela
    p5.text(this.endMessage, WIDTH / 2, (HEIGHT+HEIGHT_INV) / 2);
  }

}