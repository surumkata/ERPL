 const debugMode = true;
 let WIDTH = 1280;
 let HEIGHT = 720;
 let HEIGHT_INV = HEIGHT * 0.15;
 let SCALE_EDIT = 0.5;

 function setWIDTH(value) {
    WIDTH = value;
}

 function setHEIGHT(value) {
    HEIGHT = value;
}

 function setHEIGHT_INV(value) {
    HEIGHT_INV = value;
}

 function setSCALE_EDIT(value){
    SCALE_EDIT = value;
}


 const Color = {
    WHITE: [255, 255, 255],
    GREEN: [0, 255, 0],
    RED: [255, 0, 0],
    BLACK: [0, 0, 0],
    BLUE: [0, 0, 255],
    GRAY: [89, 89, 89]
};

// CLASSES AUXILIARES
 class Position {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

 class Size {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

 class Text {
    constructor(id, text, x, y, size, color, textFormat = false) {
      this.id = id;
      this.size = parseInt(size * 0.8); // tamanho da fonte
      this.color = color; // cor em formato p5.js
      this.text = text;
      this.x = x;
      this.y = y + size/2;
      this.textFormat = textFormat; // ativar formatação de texto dinâmico
    }
  
    draw(p5, variables) {
      let displayText = this.text;
  
      if (this.textFormat) {
        displayText = replaceVariables(displayText,variables);
      }
  
      // Definir a fonte e o tamanho do texto
      p5.textSize(this.size);
      p5.fill(this.color);
  
      // Renderizar o texto na posição (x, y)
      p5.text(displayText, this.x, this.y);
    }
  }

  function replaceVariables(displayText, variables) {
    // Substituir variáveis nos placeholders {variable}
    const matches = [...displayText.matchAll(/\{(.*?)\}/g)];
    for (let match of matches) {
      const varName = match[1];
  
      // Verificar se a variável está no formato _regressive_timer_nmin_
      const regressiveTimerMatch = varName.match(/^_regressive_timer_(\d+)min_$/);
      if (regressiveTimerMatch) {
        const nMinutes = parseInt(regressiveTimerMatch[1], 10); // Extrair número de minutos (n)
        
        // Calcular o tempo já passado
        const startTime = variables["__time__"]; // Tempo inicial do Date
        const currentTime = new Date(); // Tempo atual
        const elapsedTime = Math.floor((currentTime - startTime) / 1000); // Tempo passado em segundos
  
        // Calcular o tempo restante
        const totalSeconds = nMinutes * 60; // Total de segundos baseado nos minutos
        const remainingSeconds = totalSeconds - elapsedTime; // Segundos restantes
  
        // Se o tempo já acabou, definir 00:00
        let displayTime = "00:00";
        if (remainingSeconds > 0) {
          const minutes = Math.floor(remainingSeconds / 60);
          const seconds = remainingSeconds % 60;
          displayTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
  
        // Substituir a variável pelo tempo formatado (mm:ss)
        displayText = displayText.replace(`{${varName}}`, displayTime);
      } else if (varName === '_timer_') {
        // Substituir pelos segundos passados
        const startTime = variables["__time__"]; // Tempo inicial do Date
        const currentTime = new Date(); // Tempo atual
        const elapsedTime = Math.floor((currentTime - startTime) / 1000); // Tempo passado em segundos
        displayText = displayText.replace(`{${varName}}`, elapsedTime);
      } else if (varName === '_timerms_') {
        // Substituir pelos milissegundos passados
        const startTime = variables["__time__"]; // Tempo inicial do Date
        const currentTime = new Date(); // Tempo atual
        const elapsedTime = currentTime - startTime; // Tempo passado em milissegundos
        displayText = displayText.replace(`{${varName}}`, elapsedTime);
      } else if (variables.hasOwnProperty(varName)) {
        // Substituir outras variáveis como no código original
        let value = variables[varName];
        if (typeof value === "number" && value % 1 === 0) {
          value = Math.floor(value); // Garantir que seja inteiro
        }
        displayText = displayText.replace(`{${varName}}`, value);
      }
    }
  
    return displayText;
  }

// Classe para representar mensagens de balão de fala
 class BalloonMessage {
    constructor(text, x, y) {
        this.text = text;
        this.x = x;
        this.y = y;
    }

    display(p5) {      
        
        p5.textSize(20);
        // Mede o texto para determinar a posição e tamanho do retângulo
        let textWidth = p5.textWidth(this.text);
        let textHeight = p5.textAscent() + p5.textDescent();
        
        // Desenha o retângulo vermelho
        p5.fill(0, 0, 0);
        p5.rect(this.x-10, this.y-textHeight-2, textWidth + 20, textHeight + 10);
        
        // Desenha o texto branco
        p5.fill(255);  // Cor branca
        p5.text(this.text, this.x, this.y);
    }
}

 function debug(message) {
    console.log(message);
}