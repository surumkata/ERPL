//Módulo dos Desafios (Challenges)
//Classe abstracta de Desafio
class Challenge {
    //Todos os desafios tem um sucess (actions caso o desafio seja bem sucedido) e um fail (actions caso o desafio seja falhado)
    constructor(sucess, fail) {
        this.sucess = sucess;
        this.fail = fail;

        //Variáveis auxiliares no desenho dos desafios.
        this.background = [WIDTH / 4, HEIGHT/4 +HEIGHT_INV, WIDTH / 2, HEIGHT / 2];
        this.bigBackground = [WIDTH/8, HEIGHT/8+HEIGHT_INV, 3*WIDTH/4, 3*HEIGHT/4];

        this.WHITE = 255
        this.GRAY = 128
        this.BLACK = 0

        this.padding = 10
        
        this.backgroundColor = this.GRAY
        this.backgroundStrokeColor = this.BLACK
        this.backgroundStrokeWeight = 2
        
        this.textSize = 32
        this.textColor = this.WHITE
        this.textStrokeColor = this.BLACK
        this.textStrokeWeight = 1
    }
  
    draw(p5) {
        // Abstract method to be implemented in subclasses
    }

    mousePressed(mX,mY,gameState) {
        // Abstract method to be implemented in subclasses
    }

    mouseMoved(mX,mY){
        // Abstract method to be implemented in subclasses
    }

    drawBigBackground(p5) {
        p5.fill(this.backgroundColor);
        p5.stroke(this.backgroundStrokeColor);
        p5.strokeWeight(this.backgroundStrokeWeight);
        p5.rect(this.bigBackground[0],this.bigBackground[1],this.bigBackground[2],this.bigBackground[3]);
    }

    drawBackground(p5) {
        p5.fill(this.backgroundColor);
        p5.stroke(this.backgroundStrokeColor);
        p5.strokeWeight(this.backgroundStrokeWeight);
        p5.rect(this.background[0],this.background[1],this.background[2],this.background[3]);
    }


    //Função auxiliar para detetar colisão com um retângulo
    rectCollision(mx,my,rect){
        let rectx = rect[0];
        let recty = rect[1];
        let rectw = rect[2];
        let recth = rect[3];
        if(rectx <= mx && mx <= rectx + rectw && recty <= my && my <= recty  + recth){
            return true;
        }
        return false;
    }

    //Função auxiliar para detetar colisão com um triângulo
    triangleCollision(px, py, triangle) {
        let x1 = triangle[0]
        let y1 = triangle[1]
        let x2 = triangle[2]
        let y2 = triangle[3]
        let x3 = triangle[4]
        let y3 = triangle[5]
        // get the area of the triangle
        var areaOrig = Math.floor(Math.abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)));
        //console.log("totalArea: " + areaOrig);
      
        // get the area of 3 triangles made between the point and the corners of the triangle
        var area1 = Math.floor(Math.abs((x1 - px) * (y2 - py) - (x2 - px) * (y1 - py)));
        var area2 = Math.floor(Math.abs((x2 - px) * (y3 - py) - (x3 - px) * (y2 - py)));
        var area3 = Math.floor(Math.abs((x3 - px) * (y1 - py) - (x1 - px) * (y3 - py)));
        //console.log("areaSum: " + (area1 + area2 + area3));
      
        // if the sum of the three areas equals the original, we're inside the triangle
        if (area1 + area2 + area3 <= areaOrig) {
          return true;
        }
        
        return false;
    }
  }

//Classe do desafio questão
class ChallengeQuestion extends Challenge {
    constructor(question,answer,sucess,fail){
        super(sucess,fail);
        this.question = question;
        this.answer = answer;

        //Botão de confirmação de resposta
        this.triangle = [WIDTH / 2 - 25, HEIGHT / 2 + HEIGHT / 8,
                         WIDTH / 2 - 25, HEIGHT / 2 + HEIGHT / 8 + 50,
                         WIDTH / 2 + 25, HEIGHT / 2 + HEIGHT / 8 + 50/2
                        ]
        
        this.hover = false;
    }
    
    draw(p5) {
        //Desenho do retângulo do desafio principal
        this.drawBackground(p5)
        
        if(this.hover) {
            p5.fill(255,0,0);
        }
        else {
            p5.fill(255);
        }
        p5.triangle(this.triangle[0],this.triangle[1],this.triangle[2],this.triangle[3],this.triangle[4],this.triangle[5])
        
        p5.textSize(this.textSize);
        p5.fill(this.textColor);
        p5.stroke(this.textStrokeColor);
        p5.strokeWeight(this.textStrokeWeight);
        p5.text(this.question, this.background[0] + this.padding, this.background[1] + this.textSize);
    }

    mousePressed(mX,mY,gameState) {
        if (mX >= 0 && mY >= 0 && mX <= WIDTH && mY <= HEIGHT) {
            if (super.rectCollision(mX,mY,this.background)){
                if (super.triangleCollision(mX,mY,this.triangle)){
                    if(gameState.inputElem.value() === this.answer) {
                        return this.sucess;
                    }
                    else {
                        return this.fail;
                    }
                }
            }
            else{
                return 0;
            }
            
        }
        return undefined;      
    }

    mouseMoved(mX,mY){
        if (super.triangleCollision(mX,mY,this.triangle)){
            this.hover = true;
            document.documentElement.style.cursor = 'pointer';
        }
        else {
            this.hover = false;
            document.documentElement.style.cursor = 'default';
        }
    }
}

class ChallengeMultipleChoice extends Challenge {
    constructor(question, multipleChoices, answer, sucess, fail){
        super(sucess,fail);
        this.question = question;
        this.multipleChoices = multipleChoices;

        this.shuffleChoices()

        this.answer = answer;

        this.choiceBoxes = [
            [WIDTH/8+10, HEIGHT/8+10 + 2*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20],
            [WIDTH/8+10, HEIGHT/8+10 + 3*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20],
            [WIDTH/8+10, HEIGHT/8+10 + 4*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20],
            [WIDTH/8+10, HEIGHT/8+10 + 5*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20]
        ]

        this.choiceHover = undefined;
    }

    shuffleChoices() {
        for (var i = this.multipleChoices.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = this.multipleChoices[i];
            this.multipleChoices[i] = this.multipleChoices[j];
            this.multipleChoices[j] = temp;
        }
    }

    draw(p5) {
        // Fundo colorido
        this.drawBigBackground(p5)

        let i = 0
        this.choiceBoxes.forEach(box => {
            if(this.choiceHover != undefined && this.choiceHover === i){  
                p5.fill(255,0,0);
            }
            else {
                p5.fill(this.backgroundColor);
            }

            p5.stroke(this.backgroundStrokeColor);
            p5.strokeWeight(this.backgroundStrokeWeight);
            p5.rect(box[0],box[1],box[2],box[3])
            
            p5.textSize(this.textSize);
            p5.fill(this.textColor)
            p5.stroke(this.textStrokeColor);
            p5.strokeWeight(this.textStrokeWeight);
            p5.text(this.multipleChoices[i],box[0] + 10, box[1] + box[3]/2 + 10);
            i+=1
        })
        
        // Fonte e cor do texto
        p5.textSize(this.textSize);
        p5.fill(this.textColor)
        p5.stroke(this.textStrokeColor);
        p5.strokeWeight(this.textStrokeWeight);
        p5.text(this.question, WIDTH/8 + 10, HEIGHT/8 + 32 + HEIGHT_INV);
    }


    mousePressed(mX,mY,gameState) {
        if (mX >= 0 && mY >= 0 && mX <= WIDTH && mY <= HEIGHT) {
            if (super.rectCollision(mX,mY,this.bigBackground)){
                var i = 0;
                var event = undefined;
                this.choiceBoxes.forEach(box => {
                    if(super.rectCollision(mX,mY,box)){
                        if(this.multipleChoices[i] === this.answer){
                            event = this.sucess;
                        }
                        else {
                            event = this.fail;
                        }
                    }
                    i+=1;
                })
                return event;
            }
            else{
                return 0;
            }
            
        }
        return undefined;      
    }

    mouseMoved(mX,mY){
        var i = 0
        var choiceHover = undefined
        this.choiceBoxes.forEach(box => {
            if(super.rectCollision(mX,mY,box)){
                choiceHover = i;
                document.documentElement.style.cursor = 'pointer';
            }
            i+=1;
        })
        this.choiceHover = choiceHover;
        if (choiceHover == undefined){
            document.documentElement.style.cursor = 'default';
        }
    }

}


class ChallengeSequence extends Challenge {
    constructor(question, sequence, sucess, fail){
        super(sucess,fail);
        this.question = question;
        this.sequence = sequence;
        this.shuffledSequence = [...sequence];
        this.shuffleSequence()

        console.log(this.sequence)
        console.log(this.shuffledSequence)

        this.choice = 0
        this.dones = []


        this.choiceBoxes = [
            [WIDTH/8+10, HEIGHT/8+10 + 2*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20],
            [WIDTH/8+10, HEIGHT/8+10 + 3*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20],
            [WIDTH/8+10, HEIGHT/8+10 + 4*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20],
            [WIDTH/8+10, HEIGHT/8+10 + 5*(3*HEIGHT/4)/6 + HEIGHT_INV, 3*WIDTH/4-20, (3*HEIGHT/4)/6-20]
        ]

        this.choiceHover = undefined;
    }

    shuffleSequence() {
        for (var i = this.shuffledSequence.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = this.shuffledSequence[i];
            this.shuffledSequence[i] = this.shuffledSequence[j];
            this.shuffledSequence[j] = temp;
        }
    }

    draw(p5) {
        // Fundo colorido
        this.drawBigBackground(p5)

        let i = 0
        this.choiceBoxes.forEach(box => {
            if (this.dones.includes(this.shuffledSequence[i])) {
                p5.fill(0,255,0);
            }
            else if(this.choiceHover != undefined && this.choiceHover === i){  
                p5.fill(255,0,0);
            }
            else {
                p5.fill(this.backgroundColor);
            }

            p5.stroke(this.backgroundStrokeColor);
            p5.strokeWeight(this.backgroundStrokeWeight);
            p5.rect(box[0],box[1],box[2],box[3])
            
            p5.textSize(this.textSize);
            p5.fill(this.textColor)
            p5.stroke(this.textStrokeColor);
            p5.strokeWeight(this.textStrokeWeight);
            p5.text(this.shuffledSequence[i],box[0] + 10, box[1] + box[3]/2 + 10);
            i+=1
        })
        
        // Fonte e cor do texto
        p5.textSize(this.textSize);
        p5.fill(this.textColor)
        p5.stroke(this.textStrokeColor);
        p5.strokeWeight(this.textStrokeWeight);
        p5.text(this.question, WIDTH/8 + 10, HEIGHT/8 + 32 + HEIGHT_INV);
    }

    mousePressed(mX,mY,gameState) {
        if (mX >= 0 && mY >= 0 && mX <= WIDTH && mY <= HEIGHT) {
            if (super.rectCollision(mX,mY,this.bigBackground)){
                var i = 0;
                var event = undefined
                this.choiceBoxes.forEach(box => {
                    if(super.rectCollision(mX,mY,box)){
                        if(!this.dones.includes(this.shuffledSequence[i])) {
                            if(this.sequence[this.choice] !== this.shuffledSequence[i]) {
                                event = this.fail
                            }
                            else {
                                this.choice += 1
                                this.dones.push(this.shuffledSequence[i])
                                if (this.choice === 4){
                                    event = this.sucess
                                }
                            }
                        }
                    }
                    i+=1;
                })
                return event
            }
            else{
                return 0;
            }
            
        }
        return undefined;      
    }

    mouseMoved(mX,mY){
        var i = 0
        var choiceHover = undefined
        this.choiceBoxes.forEach(box => {
            if(!this.dones.includes(this.shuffledSequence[i]) && super.rectCollision(mX,mY,box)){
                choiceHover = i;
                document.documentElement.style.cursor = 'pointer';
            }
            i+=1;
        })
        this.choiceHover = choiceHover;
        if (choiceHover == undefined){
            document.documentElement.style.cursor = 'default';
        }
    }
}

class ChallengeConnections extends Challenge{
    constructor(question, list1, list2, sucess, fail){
        super(sucess,fail);
        this.question = question;
        this.list1 = [...list1];
        this.list2 = [...list2];

        this.connections = {}
        for (var i = 0; i <= this.list1.length - 1; i++) {
            this.connections[this.list1[i]] = this.list2[i]
        }
        this.padding = 10

        this.shuffleLists();

        this.leftBoxes = [
            [WIDTH/8+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 2*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2],
            [WIDTH/8+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 3*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2],
            [WIDTH/8+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 4*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2],
            [WIDTH/8+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 5*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2]
        ]

        this.rightBoxes = [
            [WIDTH/2+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 2*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2],
            [WIDTH/2+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 3*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2],
            [WIDTH/2+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 4*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2],
            [WIDTH/2+this.padding, HEIGHT_INV+HEIGHT/8+this.padding + 5*(3*HEIGHT/4)/6, 3*WIDTH/8-this.padding*2, (3*HEIGHT/4)/6-this.padding*2]
        ]

        this.dones = []

        this.leftChoice = undefined
        this.rightChoice = undefined
    }

    shuffleLists() {
        for (var i = this.list1.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var temp = this.list1[i];
            this.list1[i] = this.list1[j];
            this.list1[j] = temp;
        }
        for (i = this.list2.length - 1; i > 0; i--) {
            j = Math.floor(Math.random() * (i + 1));
            temp = this.list2[i];
            this.list2[i] = this.list2[j];
            this.list2[j] = temp;
        }
    }

    draw(p5){
        // Fundo colorido
        this.drawBigBackground(p5)
        

        let i = 0
        this.leftBoxes.forEach(leftBox => {
            if (this.dones.includes(this.connections[this.list1[i]])) {
                p5.fill (0,255,0);
            }
            else if(this.leftChoice === this.list1[i]){
                p5.fill (0,0,255);
            }
            else if(this.choiceHover != undefined && this.choiceHover === i){  
                p5.fill(255,0,0);
            }
            else {
                p5.fill(this.backgroundColor);
            }          

            p5.stroke(this.backgroundStrokeColor);
            p5.strokeWeight(this.backgroundStrokeWeight);
            p5.rect(leftBox[0],leftBox[1],leftBox[2],leftBox[3])
            
            p5.textSize(this.textSize);
            p5.fill(this.textColor)
            p5.stroke(this.textStrokeColor);
            p5.strokeWeight(this.textStrokeWeight);
            p5.text(this.list1[i],leftBox[0] + this.padding, leftBox[1] + leftBox[3]/2 + this.padding);
            i+=1
        })
        i = 0
        this.rightBoxes.forEach(rightBox => {            
            if (this.dones.includes(this.list2[i])) {
                p5.fill (0,255,0);
            }
            else if(this.rightChoice === this.list2[i]){
                p5.fill (0,0,255);
            }
            else if(this.choiceHover != undefined && this.choiceHover === i+4){  
                p5.fill(255,0,0);
            }
            else {
                p5.fill(this.backgroundColor);
            }   
            p5.stroke(this.backgroundStrokeColor);
            p5.strokeWeight(this.backgroundStrokeWeight);
            p5.rect(rightBox[0],rightBox[1],rightBox[2],rightBox[3])
            
            p5.textSize(this.textSize);
            p5.fill(this.textColor)
            p5.stroke(this.textStrokeColor);
            p5.strokeWeight(this.textStrokeWeight);
            p5.text(this.list2[i],rightBox[0] + this.padding, rightBox[1] + rightBox[3]/2 + this.padding);
            i+=1
        })
        
        // Fonte e cor do texto
        p5.textSize(this.textSize);
        p5.fill(this.textColor)
        p5.stroke(this.textStrokeColor);
        p5.strokeWeight(this.textStrokeWeight);
        p5.text(this.question, this.bigBackground[0] + this.padding, this.bigBackground[1] + this.textSize + this.padding);

    }
    mousePressed(mX,mY,gameState) {
        document.documentElement.style.cursor = 'default';
        if (mX >= 0 && mY >= 0 && mX <= WIDTH && mY <= HEIGHT) {
            if (super.rectCollision(mX,mY,this.bigBackground)){
                var i = 0;
                var event = undefined
                this.leftBoxes.forEach(box => {
                    if(super.rectCollision(mX,mY,box)){
                        if(!this.dones.includes(this.connections[this.list1[i]])) {
                            this.leftChoice = this.list1[i]
                            if (this.rightChoice != undefined){
                                console.log(this.rightChoice);
                                console.log(this.leftChoice);
                                if(this.rightChoice === this.connections[this.leftChoice]){
                                    this.dones.push(this.rightChoice);
                                    this.rightChoice = undefined;
                                    this.leftChoice = undefined;
                                    if(this.dones.length === 4) {
                                        event = this.sucess;
                                    }
                                }
                                else{
                                    event = this.fail;
                                }
                            }
                        }
                    }
                    i+=1;
                })
                i = 0;
                this.rightBoxes.forEach(box => {
                    if(super.rectCollision(mX,mY,box)){
                        if(!this.dones.includes(this.list2[i])) {
                            this.rightChoice = this.list2[i]
                            if (this.leftChoice != undefined){
                                if(this.rightChoice === this.connections[this.leftChoice]){
                                    this.dones.push(this.rightChoice);
                                    this.rightChoice = undefined;
                                    this.leftChoice = undefined;
                                    if(this.dones.length === 4) {
                                        event = this.sucess;
                                    }
                                }
                                else{
                                    event = this.fail;
                                }
                            }
                        }
                    }
                    i+=1;
                })
                return event
            }
            else{
                return 0;
            }
            
        }
        return undefined;      
    }

    mouseMoved(mX,mY){
        var i = 0
        var choiceHover = undefined
        this.leftBoxes.forEach(box => {
            if(!this.dones.includes(this.connections[this.list1[i]]) && super.rectCollision(mX,mY,box)){
                choiceHover = i;
                document.documentElement.style.cursor = 'pointer';
            }
            i+=1;
        })
        if (choiceHover == undefined){
            i = 0;
            this.rightBoxes.forEach(box => {
                if(!this.dones.includes(this.list2[i]) && super.rectCollision(mX,mY,box)){
                    choiceHover = i+4;
                    document.documentElement.style.cursor = 'pointer';
                }
                i+=1;
            })
        }
        this.choiceHover = choiceHover;

        if (choiceHover == undefined){
            document.documentElement.style.cursor = 'default';
        }
    }
}