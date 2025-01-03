 class Sound {
    constructor(id,src,loop){
        this.id = id;
        this.sound = new Audio(src);
        this.sound.loop = loop;
    }

    play(){
        this.sound.currentTime=0;
        this.sound.play();
    }
}