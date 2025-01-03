let gameData;

const doEvent = (gameData, event) => {
    for (let posCondition of event.posConditions) {
        posCondition.do(gameData.escapeRoom, gameData.inventory, gameData.gameState);
    }
    gameData.gameState.bufferEventsHappened.push(event.id);
};

const tryDoEvents = (gameData) => {
    for (let event of Object.values(gameData.escapeRoom.events)) {
        if (event.preConditions.root === null || event.repetitions === 0) continue;
        if (event.preConditions.testTree(gameData.escapeRoom, gameData.inventory, gameData.gameState)) {
            doEvent(gameData, event);
        }
    }
};

let textarea;  // Elemento de textarea

function preload() {
    // Carrega os dados do jogo a partir de um JSON
    fetch('tmp/game_model.json') // Carrega o JSON de um arquivo externo
        .then(response => response.json())
        .then(json => {
            gameData = load(this, json);  // 'load' é a função que você definiu para carregar os dados do jogo
            gameData.escapeRoom.variables['__time__'] = gameData.gameState.time;
        });
}

function setup() {
    createCanvas(WIDTH, HEIGHT + HEIGHT_INV);
    textarea = createElement('textarea');
    textarea.hide(); // Oculte o textarea até ser necessário

    if (gameData) {
        gameData.gameState.inputElem = textarea;
    }
}

function draw() {
    background(0);

    if (gameData) {
        tryDoEvents(gameData);
        gameData.gameState.updateBuffers(gameData.escapeRoom);
        gameData.inventory.updateItems();

        if (gameData.gameState.isRunning()) {
            gameData.escapeRoom.draw(this, gameData.gameState.currentScenario);
            gameData.inventory.draw(this);
            gameData.gameState.drawMessages(this);
        } else if (gameData.gameState.isTransition()) {
            gameData.gameState.transition.draw(this, gameData.escapeRoom.variables);
        } else if (gameData.gameState.isChallengeMode()) {
            gameData.escapeRoom.draw(this, gameData.gameState.currentScenario);
            gameData.inventory.draw(this);
            gameData.gameState.challenge.draw(this);
        } else if (gameData.gameState.isFinished()) {
            gameData.gameState.drawFinishScreen(this);
        }
    }
}

function mousePressed() {
    if (gameData) {
        if (gameData.gameState.isRunning()) {
            gameData.gameState.bufferMessages = [];
            gameData.gameState.bufferClickEvents.push([mouseX, mouseY]);
        } else if (gameData.gameState.isChallengeMode()) {
            const event = gameData.gameState.challenge.mousePressed(mouseX, mouseY, gameData.gameState);
            if (event !== undefined && event !== 0) {
                doEvent(gameData, event);
                gameData.gameState.desactivateChallengeMode();
            } else if (event === 0) {
                gameData.gameState.desactivateChallengeMode();
            }
        } else if (gameData.gameState.isTransition()) {
            if (gameData.gameState.transition.nextScenario !== null) {
                gameData.gameState.desactivateTransitionMode();
            } else {
                gameData.gameState.activeTransitionMode(gameData.escapeRoom.transitions[gameData.gameState.transition.nextTransition]);
            }
        }
    }
}

function mouseMoved() {
    if (gameData) {
        if (gameData.gameState.isChallengeMode()) {
            gameData.gameState.challenge.mouseMoved(mouseX, mouseY);
        } else if (gameData.gameState.isRunning()) {
            gameData.inventory.mouseMoved(mouseX, mouseY);
        }
    }
}
