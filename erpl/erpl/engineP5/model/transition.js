 class Transition {
    constructor(id,background,story,nextScenario,nextTransition,formatStory) {
        this.id = id;
        this.background = background;
        this.story = story;
        this.nextScenario = nextScenario;
        this.nextTransition = nextTransition;
        this.formatStory = formatStory;

        this.WHITE = 255
        this.GRAY = 128
        this.BLACK = 0

        this.textSize = 26
        this.textColor = this.WHITE
        this.textStrokeColor = this.BLACK
        this.textStrokeWeight = 1

        this.padding = 10
    }

    draw(p5,variables){

        this.background.draw(p5);
        var i = 1;
        let textSize = this.textSize;
        let textColor = this.textColor;
        let textStrokeColor = this.textStrokeColor;
        let textStrokeWeight = this.textStrokeWeight;
        let padding = this.padding;

        let formatStory = this.formatStory

        this.story.forEach(function(line){
            let displayText = line;
            if (formatStory) {
                displayText = replaceVariables(displayText,variables);
              }

            p5.textSize(textSize);
            p5.fill(textColor);
            p5.stroke(textStrokeColor);
            p5.strokeWeight(textStrokeWeight);
            p5.text(displayText, padding, HEIGHT_INV+textSize*i);
            i++;
        })
        
    }


}