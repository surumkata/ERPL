 class View {
  constructor(p5,id, srcImages, size, position, timeSprite, repeate,turn,hitboxes,hitboxesType) {
    this.id = id;
    this.position = position;
    this.size = size;
    this.srcImages = srcImages;
    this.timeSprite = timeSprite;
    this.images = [];
    this.currentSprite = 0;
    this.currentTimeSprite = 0;
    this.repeateInit = repeate;
    this.repeate = this.repeateInit;
    this.turnX = turn.x;
    this.turnY = turn.y;
    this.hitboxes = hitboxes;
    this.hitboxesType = hitboxesType;
    this.hover = false;
    this.rect = new Rect(id,this.position.x,this.position.y,this.size.x,this.size.y,0,0,0,0);
    this.showHitboxes = false;


    for (let i in this.srcImages){
      //TODO: colocar assets para funcionar :)
      this.images[i] = p5.loadImage(this.srcImages[i]);
    }
  }

  changeSize(scale) {
    let position = new Position(this.position.x,this.position.y);
    
    this.position.x *= scale.x;
    this.position.y *= scale.y;
    this.size.x *= scale.x;
    this.size.y *= scale.y;


    this.hitboxes.forEach(hitbox => {
      hitbox.scale(scale.x,scale.y)
    })

    this.makeHitboxesBBox();

    this.changePosition(position);
  }

  changePosition(position) {
    this.position.x = position.x;
    this.position.y = position.y;
    let translateX = position.x-this.hitboxbb.xmin;
    let translateY = position.y-this.hitboxbb.ymin;
    this.hitboxes.forEach(hitbox => {
      hitbox.translate(translateX,translateY);
    })
    this.makeHitboxesBBox();
  } 

  changeSprite() {
      this.currentTimeSprite += 1;
      if (this.currentTimeSprite === this.timeSprite) {
          this.currentTimeSprite = 0;
          this.currentSprite += 1;
          if (this.currentSprite === this.images.length) {
              this.repeate -= 1;
              this.currentSprite = this.repeate === 0 ? this.currentSprite - 1 : 0;
          }
      }
  }

  collide(px,py){
    var collide = false;
    this.hitboxes.forEach(hitbox => {
      collide = collide || hitbox.collide(px,py);
    })
    return collide;
  }

  viewCollision(mx,my){
    let width = this.size.x;
    let height = this.size.y;
    let posX = this.position.x;
    let posY = this.position.y;
    if (width < 0){
      posX += width;
      width = -width;
    }
    if (height < 0){
      posY += height;
      height = -height;
    }
    if(posX <= mx && mx <= posX + width && posY <= my && my <= posY  + height){
        return true;
    }
    return false;
  }

  drawHitboxes(p5){
    this.hitboxes.forEach(hitbox => {
      hitbox.draw(p5);
    })
  }

  draw(p5, semi_opacity =false){
    if(this.size.x === 0 || this.size.y === 0){
      return
    }

    
    var posX = this.position.x
    var posY = this.position.y
    var width = this.size.x
    var height = this.size.y
    var scaleX = 1;
    var scaleY = 1;

    if(this.turnX){
      posX *= -1;
      posX -= width;
      scaleX = -1;
    }
    if(this.turnY){
      posY *= -1
      posY -= height
      scaleY = -1;
    }

    p5.push();
    p5.scale(scaleX,scaleY);
    if(semi_opacity){
      p5.tint(255, 127);
    }
    p5.image(this.images[this.currentSprite],posX,posY,width,height);
    p5.pop();
    if(this.hover){
      p5.push();
      p5.stroke(255,0,0);
      p5.strokeWeight(2);
      p5.fill(100,100,100,0);
      p5.rect(this.position.x,this.position.y,this.size.x,this.size.y);
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.position.x,this.position.y,10);
      p5.circle(this.position.x+this.size.x,this.position.y,10);
      p5.circle(this.position.x,this.position.y+this.size.y,10);
      p5.circle(this.position.x+this.size.x,this.position.y+this.size.y,10);
      p5.pop();
    }


    if (this.showHitboxes){
      p5.push();
      let alpha = 0.5;
      if(semi_opacity){
        alpha*=0.5;
      }
      p5.fill(`rgba(0, 255, 0, ${alpha})`);
      this.drawHitboxes(p5);
      p5.pop();
    }

    if (this.repeate > 0){
      this.changeSprite()
    } 
  }

  mouseMoved(mX,mY) {
    if(!this.showHitboxes){
      if(this.rect.mouseMoved(mX,mY)){
        this.hover = true;
      }
      else {
        this.hover = false;
      }
    }
    else{
      this.hover = false;
      if(this.hitboxesType === 'ADVANCED'){
        for (var index in this.hitboxes){
          let hitbox = this.hitboxes[index];
          if(hitbox.mouseMoved(mX,mY)){
            return true;
          }
        }
      }
      return false;
    }
    return this.hover;
  }

  mousePressed(mX,mY) {
    if(!this.showHitboxes){
      return this.rect.mousePressed(mX,mY);
    }
    else{
      if(this.hitboxesType === 'ADVANCED'){
        for (var index in this.hitboxes){
          let hitbox = this.hitboxes[index];
          if(hitbox.mousePressed(mX,mY)){
            return true;
          }
        }
      }
      return false;
    }
  }
  mouseDragged(mX,mY) {
    if(!this.showHitboxes){
      this.rect.mouseDragged(mX,mY);
      this.position.x = this.rect.x;
      this.position.y = this.rect.y;
      this.size.x = this.rect.w;
      this.size.y = this.rect.h;
    }
    else{
      for (var index in this.hitboxes){
        let hitbox = this.hitboxes[index];
        hitbox.mouseDragged(mX,mY)
      }
    }
  }
  mouseReleased() {
    if(!this.showHitboxes){
      return this.rect.mouseReleased();
    }
    else{
      for (var index in this.hitboxes){
        let hitbox = this.hitboxes[index];
        if(hitbox.mouseReleased()){
          return true;
        }
      }
      return false;
    }
  }

  shiftPressed(){
    if(!this.showHitboxes){
      this.rect.shiftPressed();
    }
    else{

    }
  }

  shiftReleased(){
    if(!this.showHitboxes){
      this.rect.shiftReleased();
    }
    else{
      //TODO: shiftReleased hitboxes
    }
  }

  makeHitboxesBBox(){
    let xmin = WIDTH;
    let ymin = HEIGHT;
    let xmax = 0;
    let ymax = 0;

    this.hitboxes.forEach(hitbox => {
        let hitbox_xmin = WIDTH;
        let hitbox_ymin = HEIGHT;
        let hitbox_xmax = 0;
        let hitbox_ymax = 0;
        switch(hitbox.constructor) {
            case HitboxRect:
                hitbox_xmin = hitbox.x;
                hitbox_ymin = hitbox.y;
                hitbox_xmax = hitbox.x+hitbox.w;
                hitbox_ymax = hitbox.y+hitbox.h;
                break;
            case HitboxPolygon:
                let xs = []
                let ys = []
                for (let i in hitbox.points){
                  let point = hitbox.points[i]
                  xs.push(point.x)
                  ys.push(point.y)
                }

                hitbox_xmin = Math.min(...xs);
                hitbox_ymin = Math.min(...ys);
                hitbox_xmax = Math.max(...xs);
                hitbox_ymax = Math.min(...ys);
                break;
            case HitboxSquare:
                hitbox_xmin = hitbox.x;
                hitbox_ymin = hitbox.y;
                hitbox_xmax = hitbox.x + hitbox.s;
                hitbox_ymax = hitbox.y + hitbox.s;
                break;
            case HitboxTriangle:
                hitbox_xmin = Math.min(hitbox.x1,hitbox.x2,hitbox.x3);
                hitbox_ymin = Math.min(hitbox.y1,hitbox.y2,hitbox.y3);
                hitbox_xmax = Math.max(hitbox.x1,hitbox.x2,hitbox.x3);
                hitbox_ymax = Math.min(hitbox.y1,hitbox.y2,hitbox.y3);
                break;
            case HitboxLine:
                hitbox_xmin = Math.min(hitbox.x1,hitbox.x2);
                hitbox_ymin = Math.min(hitbox.y1,hitbox.y2);
                hitbox_xmax = Math.max(hitbox.x1,hitbox.x2);
                hitbox_ymax = Math.min(hitbox.y1,hitbox.y2);
                break;
            case HitboxArc:
                hitbox_xmin = hitbox.x - hitbox.w/2;
                hitbox_ymin = hitbox.y - hitbox.h/2;
                hitbox_xmax = hitbox.x + hitbox.w/2;
                hitbox_ymax = hitbox.y + hitbox.h/2;
                break;
            case HitboxCircle:
                hitbox_xmin = hitbox.x - hitbox.d/2;
                hitbox_ymin = hitbox.y - hitbox.d/2;
                hitbox_xmax = hitbox.x + hitbox.d/2;
                hitbox_ymax = hitbox.y + hitbox.d/2;
                break;
            case HitboxEllipse:
                hitbox_xmin = hitbox.x - hitbox.w/2;
                hitbox_ymin = hitbox.y - hitbox.h/2;
                hitbox_xmax = hitbox.x + hitbox.w/2;
                hitbox_ymax = hitbox.y + hitbox.h/2;
                break;
            default:
                break;
        }
        xmin = Math.min(xmin,hitbox_xmin);
        ymin = Math.min(ymin,hitbox_ymin);
        xmax = Math.max(xmax,hitbox_xmax);
        ymax = Math.max(ymax,hitbox_ymax);
    })

    this.hitboxbb = {
        xmin : xmin,
        ymin : ymin,
        xmax : xmax,
        ymax : ymax
    }
  }
}

 class ViewSketch {
  constructor(id,hitboxes,hitboxesType){
    this.id = id;
    this.draws = [];
    this.hitboxes = hitboxes;
    this.hitboxesType = hitboxesType;
    this.showHitboxes = false;
  }

  makeBBox(){
    let xmin = WIDTH;
    let ymin = HEIGHT;
    let xmax = 0;
    let ymax = 0;

    this.draws.forEach(draw => {
        let draw_xmin = WIDTH;
        let draw_ymin = HEIGHT;
        let draw_xmax = 0;
        let draw_ymax = 0;
        switch(draw.constructor) {
            case Rect:
                draw_xmin = draw.x;
                draw_ymin = draw.y;
                draw_xmax = draw.x+draw.w;
                draw_ymax = draw.y+draw.h;
                break;
            case Polygon:
                let xs = []
                let ys = []
                for (let i in draw.points){
                  let point = draw.points[i]
                  xs.push(point.x)
                  ys.push(point.y)
                }

                draw_xmin = Math.min(...xs);
                draw_ymin = Math.min(...ys);
                draw_xmax = Math.max(...xs);
                draw_ymax = Math.min(...ys);
                break;
            case Square:
                draw_xmin = draw.x;
                draw_ymin = draw.y;
                draw_xmax = draw.x + draw.w;
                draw_ymax = draw.y + draw.h;
                break;
            case Triangle:
                draw_xmin = Math.min(draw.x1,draw.x2,draw.x3);
                draw_ymin = Math.min(draw.y1,draw.y2,draw.y3);
                draw_xmax = Math.max(draw.x1,draw.x2,draw.x3);
                draw_ymax = Math.min(draw.y1,draw.y2,draw.y3);
                break;
            case Line:
                draw_xmin = Math.min(draw.x1,draw.x2);
                draw_ymin = Math.min(draw.y1,draw.y2);
                draw_xmax = Math.max(draw.x1,draw.x2);
                draw_ymax = Math.min(draw.y1,draw.y2);
                break;
            case Arc:
                draw_xmin = draw.x - draw.w/2;
                draw_ymin = draw.y - draw.h/2;
                draw_xmax = draw.x + draw.w/2;
                draw_ymax = draw.y + draw.h/2;
                break;
            case Circle:
                draw_xmin = draw.x - draw.w/2;
                draw_ymin = draw.y - draw.h/2;
                draw_xmax = draw.x + draw.w/2;
                draw_ymax = draw.y + draw.h/2;
                break;
            case Ellipse:
                draw_xmin = draw.x - draw.w/2;
                draw_ymin = draw.y - draw.h/2;
                draw_xmax = draw.x + draw.w/2;
                draw_ymax = draw.y + draw.h/2;
                break;
            default:
                break;
        }
        xmin = Math.min(xmin,draw_xmin);
        ymin = Math.min(ymin,draw_ymin);
        xmax = Math.max(xmax,draw_xmax);
        ymax = Math.max(ymax,draw_ymax);
    })

    this.bb = {
        xmin : xmin,
        ymin : ymin,
        xmax : xmax,
        ymax : ymax
    }
    
  }

  changePosition(position){
    let translateX = (position.x-this.bb.xmin);
    let translateY = (position.y-this.bb.ymin);
    this.translate(translateX,translateY);
  }

  changeSize(scale){

    let pos = new Position(this.bb.xmin,this.bb.ymin)

    this.draws.forEach(draw => {
      draw.scale(scale.x,scale.y);
    })

    this.hitboxes.forEach(hitbox => {
      hitbox.scale(scale.x,scale.y);
    });
    
    this.makeBBox();
    this.changePosition(pos);
  }

  draw(p5, semi_opacity=false){
    p5.push();
    p5.noStroke();
    p5.fill(0);
    if(semi_opacity){
      p5.fill(0, 127);
    }
    this.draws.forEach(draw => {
      draw.draw(p5,semi_opacity);
    })
    p5.pop()

    if (this.showHitboxes){
      p5.push();
      let alpha = 0.5;
      if(semi_opacity){
        alpha*=0.5;
      }
      p5.fill(`rgba(0, 255, 0, ${alpha})`);
      this.drawHitboxes(p5);
      p5.pop();
    }
    //debug 
    //p5.push();
    //p5.fill(0,255,0);
    //p5.quad(this.bb.xmin,this.bb.ymin,this.bb.xmax,this.bb.ymin,this.bb.xmax,this.bb.ymax,this.bb.xmin,this.bb.ymax);
    //p5.pop();
  }

  drawHitboxes(p5){
    this.hitboxes.forEach(hitbox => {
      hitbox.draw(p5);
    })
  }

  addDraw(draw){
    this.draws.push(draw);
  }

  translate(tx,ty){
    this.draws.forEach(draw => {
      draw.translate(tx,ty);
    })
    this.hitboxes.forEach(hitbox => {
      hitbox.translate(tx,ty);
    });
    this.makeBBox();
  }

  collide(px,py){
    var collide = false;
    this.hitboxes.forEach(hitbox => {
      collide = collide || hitbox.collide(px,py);
    })
    return collide;
  }

  mouseMoved(mX,mY) {
    let hover = false;
    if(!this.showHitboxes){
      for (let index = this.draws.length - 1; index >= 0; --index) {
        if(hover){
          this.draws[index].setHoverFalse();
        }
        else {
          hover = this.draws[index].mouseMoved(mX,mY);
        }
      }
    }
    else{
      for (let index = this.draws.length - 1; index >= 0; --index) {
        this.draws[index].setHoverFalse();
      }
      if(this.hitboxesType === 'ADVANCED'){
        for (let index = this.hitboxes.length - 1; index >= 0; --index) {
          let hitbox = this.hitboxes[index];
          if(hitbox.mouseMoved(mX,mY)){
            return true;
          }
        }
      }
      return false;
    }
    return hover;
  }

  mousePressed(mX,mY) {
    if(!this.showHitboxes){
      for (let index = this.draws.length - 1; index >= 0; --index) {
        var pressed = this.draws[index].mousePressed(mX,mY);
        if(pressed){
          return true;
        }
      }
    }
    else{
      if(this.hitboxesType === 'ADVANCED'){
        for (let index = this.hitboxes.length - 1; index >= 0; --index) {
          let hitbox = this.hitboxes[index];
          if(hitbox.mousePressed(mX,mY)){
            return true;
          }
        }
      }
      return false;
    }
  }

  mouseDragged(mX,mY) {
    if(!this.showHitboxes){
      for (var draw in this.draws){
        this.draws[draw].mouseDragged(mX,mY);
      }
    }
    else{
      for (var index in this.hitboxes){
        let hitbox = this.hitboxes[index];
        hitbox.mouseDragged(mX,mY)
      }
    }
  }

  mouseReleased() {
    if(!this.showHitboxes){
      for (var draw in this.draws){
        var released = this.draws[draw].mouseReleased();
        if(released){
          return true;
        }
      }
    }
    else{
      for (var index in this.hitboxes){
        let hitbox = this.hitboxes[index];
        if(hitbox.mouseReleased()){
          return true;
        }
      }
      return false;
    }
  }

  shiftReleased(){
    for (var draw in this.draws){
      this.draws[draw].shiftReleased();
    }
  }

  shiftPressed(){
    for (var draw in this.draws){
      this.draws[draw].shiftPressed();
    }
  }
}


 class DrawP5 {
  constructor(id){
    this.id = id;
    this.hover = false;
  }

  draw(p5){
    // Abstract method to be implemented in subclasses
  }
  translate(tx,ty){}
  scale(scaleX,scaleY){}

  mouseMoved(mX,mY) {return false;}
  mousePressed(mX,mY) {return false;}
  mouseDragged(mX,mY) {}
  mouseReleased() {return false;}
  shiftReleased(){}
  shiftPressed(){}
  setHoverFalse(){
    this.hover = false;
  }
}

 class Rect extends DrawP5 {
  constructor(id,x,y,w,h,tl,tr,br,bl){
    super(id);
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.tl = tl;
    this.tr = tr;
    this.br = br;
    this.bl = bl;
    this.hover = false;
    this.isDragging = false;
    this.isResizing = false;
    this.lastPosition = new Position(0,0);
    this.typeResizing = "";
    this.hover = false;
    this.shift = false;
  }

  shiftPressed(){
    this.shift = true;
  }

  shiftReleased(){
    this.shift = false;
  }

  draw(p5){
    p5.rect(this.x,this.y,this.w, this.h, this.tl,this.tr,this.br, this.bl);

    if(this.hover){
      p5.push();
      p5.stroke(255,0,0);
      p5.strokeWeight(2);
      p5.fill(100,100,100,0);
      p5.rect(this.x,this.y,this.w,this.h);
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x,this.y,10);
      p5.circle(this.x+this.w,this.y,10);
      p5.circle(this.x,this.y+this.h,10);
      p5.circle(this.x+this.w,this.y+this.h,10);
      p5.pop();
    }
  }

  scale(scaleX,scaleY){
    this.x *= scaleX;
    this.y *= scaleY;
    this.w *=scaleX;
    this.h *=scaleY;
  }

  translate(tx,ty){
    this.x += tx
    this.y += ty
  }
  
  mouseMoved(mX,mY) {
    let width = this.w;
    let height = this.h;
    let posX = this.x;
    let posY = this.y;
    if (width < 0){
      posX += width;
      width = -width;
    }
    if (height < 0){
      posY += height;
      height = -height;
    }
    if(collidePointCircle(mX,mY,posX,posY,11)){
      this.hover = true
      document.documentElement.style.cursor = 'nwse-resize';
    }
    else if(collidePointCircle(mX,mY,posX+width,posY,11)){
      this.hover = true
      document.documentElement.style.cursor = 'nesw-resize';
    }
    else if(collidePointCircle(mX,mY,posX,posY+height,11)){
      this.hover = true
      document.documentElement.style.cursor = 'nesw-resize';
    }
    else if(collidePointCircle(mX,mY,posX+width,posY+height,11)){
      this.hover = true
      document.documentElement.style.cursor = 'nwse-resize';
    }
    else if(collidePointLine(mX,mY,posX,posY,posX+width,posY)){
      this.hover = true
      document.documentElement.style.cursor = 'ns-resize';
    }
    else if(collidePointLine(mX,mY,posX,posY+height,posX+width,posY+height)){
      this.hover = true
      document.documentElement.style.cursor = 'ns-resize';
    }
    else if(collidePointLine(mX,mY,posX,posY,posX,posY+height)){
      this.hover = true
      document.documentElement.style.cursor = 'ew-resize';
    }
    else if(collidePointLine(mX,mY,posX+width,posY,posX+width,posY+height)){
      this.hover = true
      document.documentElement.style.cursor = 'ew-resize';
    }
    else if (collidePointRect(mX,mY,posX,posY,width,height)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x,this.y,11)){ //CIRCULO ESQUERDO CIMA
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "CIRCULO_ESQUERDA_CIMA"
    }
    else if(collidePointCircle(mX,mY,this.x+this.w,this.y,11)){ //CIRCULO DIREITA CIMA
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "CIRCULO_DIREITA_CIMA"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.h,11)){ //CIRCULO ESQUERDA BAIXO
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "CIRCULO_ESQUERDA_BAIXO"
    }
    else if(collidePointCircle(mX,mY,this.x+this.w,this.y+this.h,11)){ //CIRCULO DIREITA BAIXO
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "CIRCULO_DIREITA_BAIXO"
    }
    else if(collidePointLine(mX,mY,this.x,this.y,this.x+this.w,this.y)){ //RETA CIMA
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "RETA_CIMA"
    }
    else if(collidePointLine(mX,mY,this.x,this.y+this.h,this.x+this.w,this.y+this.h)){ //RETA BAIXO
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "RETA_BAIXO"
    }
    else if(collidePointLine(mX,mY,this.x,this.y,this.x,this.y+this.h)){ //RETA ESQUERDA
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "RETA_ESQUERDA"
    }
    else if(collidePointLine(mX,mY,this.x+this.w,this.y,this.x+this.w,this.y+this.h)){ //RETA DIREITA
      this.isResizing = true
      this.setLastPosition(mX,mY);
      this.typeResizing = "RETA_DIREITA"
    }
    else if (collidePointRect(mX,mY,this.x,this.y,this.w,this.h)){
      this.isDragging = true
      this.setLastPosition(mX,mY);
    }
    return this.isDragging || this.isResizing;
  }

  leaningRight(){
    return this.x + this.w >= WIDTH*SCALE_EDIT;
  }

  leaningLeft(){
    return this.x <= 0;
  }

  leaningDown(){
    return this.y + this.h >= (HEIGHT+HEIGHT_INV)*SCALE_EDIT;
  }

  leaningTop(){
    return this.y <= HEIGHT_INV*SCALE_EDIT;
  }

  fixPosition(){
    if(this.w >= 0){
      if (this.leaningRight()){
        this.x = WIDTH*SCALE_EDIT - this.w;
      }
      if (this.leaningLeft()){
        this.x = 0;
      }
    }
    else {
      if (this.x >= WIDTH*SCALE_EDIT){
        this.x = WIDTH*SCALE_EDIT;
      }
      if (this.x + this.w <= 0){
        this.x = -this.w;
      }
    }
    
    if(this.h >= 0){
      if (this.leaningDown()){
        this.y = (HEIGHT+HEIGHT_INV)*SCALE_EDIT - this.h;
      }
      if (this.leaningTop()){
        this.y = HEIGHT_INV*SCALE_EDIT;
      }
    }
    else {
      if (this.y >= (HEIGHT+HEIGHT_INV)*SCALE_EDIT){
        this.y = (HEIGHT+HEIGHT_INV)*SCALE_EDIT;
      }
      if (this.y + this.h <= HEIGHT_INV*SCALE_EDIT){
        this.y = -this.h + HEIGHT_INV*SCALE_EDIT;
      }
    }
  }

  setLastPosition(x,y){
    this.lastPosition = new Position(x,y);
  }

  setX(x){
    this.x = x;
  }

  setY(y){
    this.y = y;
  }

  dragViewX(x){
    this.x += x;
  }

  dragViewY(y){
    this.y += y;
  }

  resizeX(x){
    this.w = x;
  }

  resizeY(y){
    this.h = y;
  }

  resizeRight(mX,mY,changeX){
    if(!(this.leaningRight() && changeX > 0)){ //Não dou resize se tiver a tocar a borda da direita e o movimento for para a direita (changeX positivo)
      let touched_limits = false;
      
      this.resizeX(Math.max(0,this.w + changeX));
      if(this.leaningRight()){
        this.resizeX(WIDTH*SCALE_EDIT - this.x);
        touched_limits = true;
      }
      if (this.w !== 0 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeDown(mX,mY,changeY){
    if(!(this.leaningDown() && changeY > 0)){ //Não dou resize se tiver a tocar a borda de baixo e o movimento for para baixo (changeY positivo)
      let touched_limits = false;
      this.resizeY(Math.max(0,this.h + changeY));
      if(this.leaningDown()){ //Se tiver passado da borda de baixo ajusta-se para ficar em encostado a ela.
        this.resizeY((HEIGHT+HEIGHT_INV)*SCALE_EDIT - this.y);
        touched_limits = true;
      }
      if (this.h !== 0 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeLeft(mX,mY,changeX){
    if(!(this.leaningLeft() && changeX < 0)){ //Não dou resize se tiver a tocar a borda da esquerda e o movimento for para a esquerda (changeX negativo)
      let touched_limits = false;
      this.dragViewX(changeX);
      this.resizeX(this.w - changeX);
      if(this.leaningLeft()){ //Se tiver passado da borda da esquerda ajusta-se para ficar em encostado a ela.
        this.resizeX(this.w + this.x);
        this.setX(0);
        touched_limits = true;
      }
      if(this.w < 0){
        this.dragViewX(this.w);
        this.resizeX(0);
      }
      
      if (this.w !== 0 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeTop(mX,mY,changeY){
    if(!(this.leaningTop() && changeY < 0)){ //Não dou resize se tiver a tocar a borda de cima e o movimento for para cima (changeY negativo).
      let touched_limits = false;
      this.dragViewY(changeY);
      this.resizeY(this.h - changeY);
      if (this.leaningTop()){ //Se tiver passado da borda de cima ajusta-se para ficar em encostado a ela.
        this.resizeY(this.h - (HEIGHT_INV*SCALE_EDIT - this.y));
        this.setY(HEIGHT_INV*SCALE_EDIT);
        touched_limits = true;
      }
      
      if(this.h < 0){
        this.dragViewY(this.h);
        this.resizeY(0);
      }

      if (this.h !== 0 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeDownRight(mX,mY,changeX, changeY,relXY,relYX){
    if(!((this.leaningDown() && changeY > 0) || (this.leaningRight() && changeX > 0))){
      let touched_limits = false;
      if(relXY > relYX){
        //right
        this.resizeX(Math.max(0.1,this.w + changeY*relXY));
        //down
        this.resizeY(Math.max(0.1,this.h + changeY));
      }
      else{
        //right
        this.resizeX(Math.max(0.1,this.w + changeX));
        //down
        this.resizeY(Math.max(0.1,this.h + changeX*relYX));
      }

      if(this.leaningDown()){ //Se tiver passado da borda de baixo ajusta-se para ficar em encostado a ela.
        this.resizeY((HEIGHT+HEIGHT_INV)*SCALE_EDIT - this.y);
        this.resizeX(this.h*relXY);
        touched_limits = true;
      }
      if(this.leaningRight()){
        this.resizeX(WIDTH*SCALE_EDIT - this.x);
        this.resizeY(this.w*relYX);
        touched_limits = true;
      }

      if (this.w !== 0.1 && this.h !== 0.1 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeTopRight(mX,mY,changeX, changeY,relXY,relYX){
    if(!((this.leaningTop() && changeY < 0) || (this.leaningRight() && changeX > 0))){
      let touched_limits = false;
      if(relXY > relYX){
        //right
        this.resizeX(Math.max(0.1,this.w - changeY*relXY));
        //top
        this.dragViewY(changeY);
        this.resizeY(this.h - changeY);
      }
      else{
        //right
        this.resizeX(Math.max(0.1,this.w + changeX));
        //top
        this.dragViewY(-changeX*relYX);
        this.resizeY(this.h + changeX*relYX);
      }


      if (this.leaningTop()){ //Se tiver passado da borda de cima ajusta-se para ficar em encostado a ela.
        let dif = (HEIGHT_INV*SCALE_EDIT - this.y);
        this.resizeY(this.h - dif);
        this.setY(HEIGHT_INV*SCALE_EDIT);

        this.resizeX(this.w - dif*relXY);
        touched_limits = true;
      }

      if(this.h < 0.1){
        this.dragViewY(this.h-0.1);
        this.resizeY(0.1);
      }

      if(this.leaningRight()){
        let dif = this.w - (WIDTH*SCALE_EDIT - this.x)
        this.resizeX(WIDTH*SCALE_EDIT - this.x);

        this.dragViewY(dif*relYX);
        this.resizeY(this.h - dif*relYX);
        touched_limits = true;
      }

      if (this.w !== 0.1 && this.h !== 0.1 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeDownLeft(mX,mY,changeX, changeY,relXY,relYX){
    if(!((this.leaningDown() && changeY > 0) || (this.leaningLeft() && changeX < 0))){
      let touched_limits = false;
      if(relXY > relYX){
        //left
        this.dragViewX(-changeY*relXY);
        this.resizeX(this.w + changeY*relXY);
        //down
        this.resizeY(Math.max(0.1,this.h + changeY));
      }
      else{
        //left
        this.dragViewX(changeX);
        this.resizeX(this.w - changeX);
        //down
        this.resizeY(Math.max(0.1,this.h - changeX*relYX));
      }


      if(this.leaningDown()){ //Se tiver passado da borda de baixo ajusta-se para ficar em encostado a ela.
        let dif = this.h - ((HEIGHT+HEIGHT_INV)*SCALE_EDIT - this.y)
        this.resizeY((HEIGHT+HEIGHT_INV)*SCALE_EDIT - this.y);

        
        this.dragViewX(dif*relXY);
        this.resizeX(this.w - dif*relXY);
        touched_limits = true;
      }
      if(this.leaningLeft()){ //Se tiver passado da borda da esquerda ajusta-se para ficar em encostado a ela.
        let dif = -this.x
        this.resizeX(this.w - dif);
        this.setX(0);

        this.resizeY(this.h - dif*relYX);
        touched_limits = true;
      }

      

      if(this.w < 0.1){
        this.dragViewX(this.w-0.1);
        this.resizeX(0.1);
      }

      if (this.w !== 0.1 && this.h !== 0.1 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  resizeTopLeft(mX,mY,changeX, changeY,relXY,relYX){
    if(!((this.leaningTop() && changeY < 0) || (this.leaningLeft() && changeX < 0))){
      let touched_limits = false;
      if(relXY > relYX){
        //left
        this.dragViewX(changeY*relXY);
        this.resizeX(this.w - changeY*relXY);
        //top
        this.dragViewY(changeY);
        this.resizeY(this.h - changeY);
      }
      else{
        //left
        this.dragViewX(changeX);
        this.resizeX(this.w - changeX);
        //top
        this.dragViewY(changeX*relYX);
        this.resizeY(this.h - changeX*relYX);
      }

      if (this.leaningTop()){ //Se tiver passado da borda de cima ajusta-se para ficar em encostado a ela.
        let dif = (HEIGHT_INV*SCALE_EDIT - this.y);
        this.resizeY(this.h - dif);
        this.setY(HEIGHT_INV*SCALE_EDIT);

        this.dragViewX(dif*relXY);
        this.resizeX(this.w - dif*relXY);
        touched_limits = true;
      }
      
      if(this.h < 0.1){
        this.dragViewY(this.h-0.1);
        this.resizeY(0.1);
      }

      if(this.leaningLeft()){ //Se tiver passado da borda da esquerda ajusta-se para ficar em encostado a ela.
        let dif = -this.x
        this.resizeX(this.w - dif);
        this.setX(0);

        this.dragViewY(dif*relYX);
        this.resizeY(this.h - dif*relYX);
        touched_limits = true;
      }
      if(this.w < 0.1){
        this.dragViewX(this.w-0.1);
        this.resizeX(0.1);
      }

      if (this.w !== 0.1 && this.h !== 0.1 && !touched_limits) {
        this.setLastPosition(mX,mY);
      }
    }
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;
    let relXY = this.w / this.h;
    let relYX = this.h / this.w;

    if (this.isDragging) {
      this.dragViewX(changeX);
      this.dragViewY(changeY);
      this.setLastPosition(mX,mY);
      this.fixPosition()
    }
    else if(this.isResizing) {
      if(this.typeResizing === "RETA_DIREITA"){
        this.resizeRight(mX,mY,changeX);
      }
      else if(this.typeResizing === "RETA_BAIXO"){
        this.resizeDown(mX,mY,changeY);
      }
      else if(this.typeResizing === "RETA_ESQUERDA"){
        this.resizeLeft(mX,mY,changeX);
      }
      else if(this.typeResizing === "RETA_CIMA"){
        this.resizeTop(mX,mY,changeY);
      }
      else if(this.typeResizing === "CIRCULO_DIREITA_BAIXO"){ //RETA_BAIXO + RETA_DIREITA
        if(this.shift){
          this.resizeDownRight(mX,mY,changeX, changeY,relXY,relYX);
        }
        else{
          this.resizeRight(mX,mY,changeX);
          this.resizeDown(mX,mY,changeY);
        }
      }
      else if(this.typeResizing === "CIRCULO_DIREITA_CIMA"){ //RETA_CIMA + RETA_DIREITA
        if(this.shift){
          this.resizeTopRight(mX,mY,changeX,changeY,relXY,relYX);
        }
        else{
          this.resizeRight(mX,mY,changeX);
          this.resizeTop(mX,mY,changeY);
        }
      }
      else if(this.typeResizing === "CIRCULO_ESQUERDA_BAIXO"){ //RETA_BAIXO + RETA_ESQUERDA
        if(this.shift){
          this.resizeDownLeft(mX,mY,changeX,changeY,relXY,relYX);
        }
        else{
          this.resizeLeft(mX,mY,changeX);
          this.resizeDown(mX,mY,changeY);
        }
        
      }
      else if(this.typeResizing === "CIRCULO_ESQUERDA_CIMA"){ //RETA_CIMA + RETA_ESQUERDA
        if(this.shift){
          this.resizeTopLeft(mX,mY,changeX,changeY,relXY,relYX);
        }
        else{
          this.resizeLeft(mX,mY,changeX);
          this.resizeTop(mX,mY,changeY);
        }
      }
    }
  }

  mouseReleased() {
    if (this.isDragging || this.isResizing){
      this.isDragging = false;
      this.isResizing = false;
      return true;
    }
    return false;
  }
}


 class Polygon extends DrawP5 {
  constructor(id,points){
    super(id);
    this.points = points;
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
  }

  draw(p5){
    // Start drawing the shape.
    p5.beginShape();
    
    for(var i in this.points){
      var point = this.points[i]
      p5.vertex(point.x, point.y);
    }
    
    // Stop drawing the shape.
    p5.endShape(p5.CLOSE);
    if(this.hover){
      p5.push();
      p5.fill(255,0,0);
      p5.noStroke();

      for(var i in this.points){
        var point = this.points[i]
        p5.circle(point.x, point.y,10);
      }

      p5.pop();
    }
  }

  scale(scaleX,scaleY){
    for(var i in this.points){
      var point = this.points[i]
      point.x *= scaleX;
      point.y *= scaleY;
    }
  }

  translate(tx,ty){
    for(var i in this.points){
      var point = this.points[i]
      point.x += tx;
      point.y += ty;
    }
  }

  mouseMoved(mX,mY) {
    let pointHover = false;
    for(var i in this.points){
      var point = this.points[i]
      if(collidePointCircle(mX,mY,point.x,point.y,11)){
        this.hover = true;
        document.documentElement.style.cursor = 'grab';
        pointHover = true;
        break;
      }
    }
    if(!pointHover && collidePointPoly(mX,mY,this.points)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else if(!pointHover){
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    let pointPressed = false;
    for(var i in this.points){
      var point = this.points[i]
      if(collidePointCircle(mX,mY,point.x,point.y,11)){
        document.documentElement.style.cursor = 'grabbing';
        this.pressed = true;
        this.typePressed = i
        pointPressed = true;
        break;
      }
    }
    if (!pointPressed && collidePointPoly(mX,mY,this.points)){
      this.pressed = true;
      this.typePressed = "polygon"
    }

    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;

    if (this.pressed) {
      if (this.typePressed === 'polygon'){
        for(var i in this.points){
          var point = this.points[i]
          point.x += changeX;
          point.y += changeY;
        }
      }
      else if(this.typePressed!==null){
        var point = this.points[this.typePressed]
        point.x += changeX;
        point.y += changeY;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }
}

 class Square extends DrawP5 {
  constructor(id,x,y,s,tl,tr,br,bl){
    super(id);
    this.x = x;
    this.y = y;
    this.w = s;
    this.h = s;
    this.tl = tl;
    this.tr = tr;
    this.br = br;
    this.bl = bl;
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
  }

  draw(p5){
    p5.rect(this.x,this.y,this.w, this.h, this.tl,this.tr,this.br, this.bl);
    if(this.hover){
      p5.push();
      p5.stroke(255,0,0);
      p5.strokeWeight(2);
      p5.fill(100,100,100,0);
      p5.rect(this.x,this.y,this.w,this.h);
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x,this.y,10);
      p5.circle(this.x+this.w,this.y+this.h,10);
      p5.pop();
    }
  }

  mouseMoved(mX,mY) {
    if(collidePointCircle(mX,mY,this.x,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'nwse-resize';
    }
    else if(collidePointCircle(mX,mY,this.x+this.w,this.y+this.h,11)){
      this.hover = true
      document.documentElement.style.cursor = 'nwse-resize';
    }
    else if (collidePointRect(mX,mY,this.x,this.y,this.w,this.h)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x,this.y,11)){ //CIRCULO ESQUERDO CIMA
      this.pressed = true
      this.typePressed = "CIRCULO_ESQUERDA_CIMA"
    }
    else if(collidePointCircle(mX,mY,this.x+this.w,this.y+this.h,11)){ //CIRCULO DIREITA BAIXO
      this.pressed = true
      this.typePressed = "CIRCULO_DIREITA_BAIXO"
    }
    else if (collidePointRect(mX,mY,this.x,this.y,this.w,this.h)){
      this.pressed = true;
      this.typePressed = "square"
    }
    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;
    console.log(changeX,changeY)

    if (this.pressed) {
      switch(this.typePressed){
        case 'CIRCULO_ESQUERDA_CIMA':
          if(Math.abs(changeX) > Math.abs(changeY)){
            this.x += changeX;
            this.y += changeX;
            this.w -= changeX;
            this.h -= changeX;
          }
          else{
            this.x += changeY;
            this.y += changeY;
            this.w -= changeY;
            this.h -= changeY;
          }
          break;
        case 'CIRCULO_DIREITA_BAIXO':
          if(Math.abs(changeX) > Math.abs(changeY)){
            this.w += changeX;
            this.h += changeX;
          }
          else{
            this.w += changeY;
            this.h += changeY;
          }
          break;  
        default:
          this.x += changeX;
          this.y += changeY;
          break;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }


  scale(scaleX,scaleY){
    this.x *= scaleX
    this.y *= scaleY
    this.w *= scaleX
    this.h *= scaleY
  }

  translate(tx,ty){
    this.x += tx
    this.y += ty
  }
}

 class Triangle extends DrawP5 {
  constructor(id,x1,y1,x2,y2,x3,y3){
    super(id);
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;
    this.x3 = x3;
    this.y3 = y3; 
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
  }

  draw(p5){
    p5.triangle(this.x1, this.y1, this.x2, this.y2, this.x3, this.y3);
    if(this.hover){
      p5.push();
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x1,this.y1,10);
      p5.circle(this.x2,this.y2,10);
      p5.circle(this.x3,this.y3,10);
      p5.pop();
    }
  }

  scale(scaleX,scaleY){
    this.x1 *= scaleX
    this.y1 *= scaleY
    this.x2 *= scaleX
    this.y2 *= scaleY
    this.x3 *= scaleX
    this.y3 *= scaleY
  }

  translate(tx,ty){
    this.x1 += tx;
    this.y1 += ty;
    this.x2 += tx;
    this.y2 += ty;
    this.x3 += tx;
    this.y3 += ty;
  }

  mouseMoved(mX,mY) {
    if(collidePointCircle(mX,mY,this.x1,this.y1,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x2,this.y2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x3,this.y3,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if (collidePointTriangle(mX,mY,this.x1,this.y1,this.x2,this.y2,this.x3,this.y3)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x1,this.y1,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "point1"
    }
    else if(collidePointCircle(mX,mY,this.x2,this.y2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "point2"
    }
    else if(collidePointCircle(mX,mY,this.x3,this.y3,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "point3"
    }
    else if (collidePointTriangle(mX,mY,this.x1,this.y1,this.x2,this.y2,this.x3,this.y3)){
      this.pressed = true;
      this.typePressed = "triangle"
    }
    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;

    if (this.pressed) {
      switch(this.typePressed){
        case "point1":
          this.x1 += changeX;
          this.y1 += changeY;
          break;
        case "point2":
          this.x2 += changeX;
          this.y2 += changeY;
          break;
        case "point3":
          this.x3 += changeX;
          this.y3 += changeY;
          break;
        default:
          this.x1 += changeX;
          this.y1 += changeY;
          this.x2 += changeX;
          this.y2 += changeY;
          this.x3 += changeX;
          this.y3 += changeY;
          break;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }
}

 class Arc extends DrawP5 {
  constructor(id,x,y,w,h,start,stop){
    super(id);
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.start = start;
    this.stop = stop;
    this.mode = 'default';
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
    this.p1 = this.pointOfEllipse(this.start);
    this.p2 = this.pointOfEllipse(this.stop);
  }

  draw(p5){
    p5.arc(this.x, this.y, this.w, this.h, this.start, this.stop);
    if(this.hover){
      p5.push();
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x+this.w/2,this.y,10);
      p5.circle(this.x,this.y+this.h/2,10);
      p5.circle(this.x-this.w/2,this.y,10);
      p5.circle(this.x,this.y-this.h/2,10);
      p5.stroke(255,0,0);
      p5.strokeWeight(2);
      p5.line(this.x,this.y,this.x+this.w/2,this.y);
      p5.line(this.x,this.y,this.x,this.y+this.h/2);
      p5.line(this.x,this.y,this.x-this.w/2,this.y);
      p5.line(this.x,this.y,this.x,this.y-this.h/2);
      p5.pop();
    }
  }

  scale(scaleX,scaleY){
    this.x *=scaleX;
    this.y +=scaleY;
    this.w *=scaleX;
    this.h *=scaleY;
  }

  translate(tx,ty){
    this.x += tx;
    this.y += ty;
  }

  pointOfEllipse(angle) {
    // Semi-eixos da elipse
    const a = this.w / 2; // Semi-eixo maior
    const b = this.h / 2; // Semi-eixo menor

    // Coordenadas do ponto na elipse
    const x = this.x + a * Math.cos(angle);
    const y = this.y + b * Math.sin(angle);

    return { x: x, y: y };
  }

  collide(px, py){
    const inside = collidePointEllipse(px,py,this.x,this.y,this.w,this.h);
    if (!inside){return false;}
  
    const angle = (Math.atan2(py - this.y, px - this.x) + 2*Math.PI) % (2*Math.PI);
    let insideSlice;
    if(this.stop < this.start){
        const angle2 = angle+2*Math.PI;
        insideSlice = ((angle > this.start) && (angle < this.stop+2*Math.PI) || (angle2 > this.start) && (angle2 < this.stop+2*Math.PI)) ;
    }
    else {
        insideSlice = (angle > this.start) && (angle < this.stop);
    }

    if (inside && (this.mode == 'chord' || this.mode == 'open')){
        let p1 = this.pointOfEllipse(this.start);
        let p2 = this.pointOfEllipse(this.stop);
        
        let insideTriangle = collidePointTriangle(px,py,this.x,this.y,p1.x,p1.y,p2.x,p2.y);

        let angStop = this.stop
        if (angStop < this.start){
            angStop += Math.PI*2;
        }
        let difAngle = angStop - this.start;
        if(difAngle < Math.PI){
            return (inside && insideSlice && !insideTriangle)
        }
        else{
            return (inside && (insideSlice || insideTriangle))
        }
    }
  
    return (inside && insideSlice);
  }

  mouseMoved(mX,mY) {
    if(collidePointCircle(mX,mY,this.x+this.w/2,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.h/2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x-this.w/2,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x,this.y-this.h/2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if (this.collide(mX,mY)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x+this.w/2,this.y,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "width"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.h/2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "height"
    }
    else if(collidePointCircle(mX,mY,this.x-this.w/2,this.y,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "-width"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y-this.h/2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "-height"
    }
    else if (this.collide(mX,mY)){
      this.pressed = true;
      this.typePressed = "arc"
    }
    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;

    if (this.pressed) {
      switch(this.typePressed){
        case "width":
          this.w += changeX;
          break;
        case "height":
          this.h += changeY;
          break;
        case "-width":
          this.w -= changeX;
          break;
        case "-height":
          this.h -= changeY;
          break;
        default:
          this.x += changeX;
          this.y += changeY;
          break;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }


}

 class Circle extends DrawP5 {
  constructor(id,x,y,r){
    super(id);
    this.x = x;
    this.y = y;
    this.w = r*2;
    this.h = r*2;
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
  }

  draw(p5){
    p5.ellipse(this.x, this.y, this.w, this.h);
    if(this.hover){
      p5.push();
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x+this.w/2,this.y,10);
      p5.circle(this.x,this.y+this.w/2,10);
      p5.circle(this.x-this.w/2,this.y,10);
      p5.circle(this.x,this.y-this.w/2,10);
      p5.stroke(255,0,0);
      p5.strokeWeight(2);
      p5.line(this.x,this.y,this.x+this.w/2,this.y);
      p5.line(this.x,this.y,this.x,this.y+this.w/2);
      p5.line(this.x,this.y,this.x-this.w/2,this.y);
      p5.line(this.x,this.y,this.x,this.y-this.w/2);
      p5.pop();
    }
  }

  scale(scaleX, scaleY){
    this.x *=scaleX;
    this.y *=scaleY;
    this.w *=scaleX;
    this.h *=scaleY;
  }

  translate(tx,ty){
    this.x += tx;
    this.y += ty;
  }

  mouseMoved(mX,mY) {
    if(collidePointCircle(mX,mY,this.x+this.w/2,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.w/2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x-this.w/2,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x,this.y-this.w/2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if (collidePointCircle(mX,mY,this.x,this.y,this.w)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x+this.w/2,this.y,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "width"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.w/2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "height"
    }
    else if(collidePointCircle(mX,mY,this.x-this.w/2,this.y,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "-width"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y-this.w/2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "-height"
    }
    else if (collidePointCircle(mX,mY,this.x,this.y,this.w)){
      this.pressed = true;
      this.typePressed = "circle"
    }
    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;

    if (this.pressed) {
      switch(this.typePressed){
        case "width":
          if(Math.abs(changeX) > Math.abs(changeY)){
            this.w += changeX;
            this.h += changeX;
          }
          else{
            this.w += changeY;
            this.h += changeY;
          }
          break;
        case "height":
          if(Math.abs(changeX) > Math.abs(changeY)){
            this.w += changeX;
            this.h += changeX;
          }
          else{
            this.w += changeY;
            this.h += changeY;
          }
          break;
        case "-width":
          this.w = Math.max(0,this.w-changeX);
          this.h = Math.max(0,this.h-changeX);
          break;
        case "-height":
          this.w = Math.max(0,this.w-changeY);
          this.h = Math.max(0,this.h-changeY);
          break;
        default:
          this.x += changeX;
          this.y += changeY;
          break;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }
}

 class Ellipse extends DrawP5 {
  constructor(id,x,y,rw,rh){
    super(id);
    this.x = x;
    this.y = y;
    this.w = rw*2;
    this.h = rh*2;
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
  }

  draw(p5){
    p5.ellipse(this.x, this.y, this.w, this.h);
    if(this.hover){
      p5.push();
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x+this.w/2,this.y,10);
      p5.circle(this.x,this.y+this.h/2,10);
      p5.circle(this.x-this.w/2,this.y,10);
      p5.circle(this.x,this.y-this.h/2,10);
      p5.stroke(255,0,0);
      p5.strokeWeight(2);
      p5.line(this.x,this.y,this.x+this.w/2,this.y);
      p5.line(this.x,this.y,this.x,this.y+this.h/2);
      p5.line(this.x,this.y,this.x-this.w/2,this.y);
      p5.line(this.x,this.y,this.x,this.y-this.h/2);
      p5.pop();
    }
  }

  scale(scaleX, scaleY){
    this.x *= scaleX;
    this.y *= scaleY;
    this.w *= scaleX;
    this.h *= scaleY;
  }

  translate(tx,ty){
    this.x += tx;
    this.y += ty;
  }

  mouseMoved(mX,mY) {
    if(collidePointCircle(mX,mY,this.x+this.w/2,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.h/2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x-this.w/2,this.y,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x,this.y-this.h/2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if (collidePointEllipse(mX,mY,this.x,this.y,this.w,this.h)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x+this.w/2,this.y,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "width"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y+this.h/2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "height"
    }
    else if(collidePointCircle(mX,mY,this.x-this.w/2,this.y,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "-width"
    }
    else if(collidePointCircle(mX,mY,this.x,this.y-this.h/2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "-height"
    }
    else if (collidePointEllipse(mX,mY,this.x,this.y,this.w,this.h)){
      this.pressed = true;
      this.typePressed = "ellipse"
    }
    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;

    if (this.pressed) {
      switch(this.typePressed){
        case "width":
          this.w += changeX;
          break;
        case "height":
          this.h += changeY;
          break;
        case "-width":
          this.w -= changeX;
          break;
        case "-height":
          this.h -= changeY;
          break;
        default:
          this.x += changeX;
          this.y += changeY;
          break;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }

}

 class Line extends DrawP5 {
  constructor(id,x1,y1,x2,y2){
    super(id);
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;
    this.hover = false;
    this.pressed = false;
    this.typePressed = null;
    this.lastPosition = new Position(0,0);
  }

  draw(p5){
    p5.line(this.x1, this.y1, this.x2, this.y2);
    if(this.hover){
      p5.push();
      p5.fill(255,0,0);
      p5.noStroke();
      p5.circle(this.x1,this.y1,10);
      p5.circle(this.x2,this.y2,10);
      p5.pop();
    }
  }

  scale(scaleX,scaleY){
    this.x1 *= scaleX
    this.y1 *= scaleY
    this.x2 *= scaleX
    this.y2 *= scaleY
  }

  translate(tx,ty){
    this.x1 += tx;
    this.y1 += ty;
    this.x2 += tx;
    this.y2 += ty;
  }

  mouseMoved(mX,mY) {
    if(collidePointCircle(mX,mY,this.x1,this.y1,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if(collidePointCircle(mX,mY,this.x2,this.y2,11)){
      this.hover = true
      document.documentElement.style.cursor = 'grab';
    }
    else if (collidePointLine(mX,mY,this.x1,this.y1,this.x2,this.y2)){
      this.hover = true
      document.documentElement.style.cursor = 'move';
    }
    else {
      this.hover = false
      document.documentElement.style.cursor = 'default';
    }
    return this.hover
  }

  mousePressed(mX,mY) {
    if(collidePointCircle(mX,mY,this.x1,this.y1,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "point1"
    }
    else if(collidePointCircle(mX,mY,this.x2,this.y2,11)){
      document.documentElement.style.cursor = 'grabbing';
      this.pressed = true;
      this.typePressed = "point2"
    }
    else if (collidePointLine(mX,mY,this.x1,this.y1,this.x2,this.y2)){
      this.pressed = true;
      this.typePressed = "line"
    }
    if(this.pressed){
      this.lastPosition = new Position(mX,mY);
    }
    return this.pressed;
  }

  mouseDragged(mX,mY) {
    let changeX = mX-this.lastPosition.x;
    let changeY = mY-this.lastPosition.y;

    if (this.pressed) {
      switch(this.typePressed){
        case "point1":
          this.x1 += changeX;
          this.y1 += changeY;
          break;
        case "point2":
          this.x2 += changeX;
          this.y2 += changeY;
          break;
        default:
          this.x1 += changeX;
          this.y1 += changeY;
          this.x2 += changeX;
          this.y2 += changeY;
          break;
      }
      this.lastPosition = new Position(mX,mY);
    }
  }

  mouseReleased() {
    if (this.pressed){
      this.pressed = false;
      this.typePressed = null;
      return true;
    }
    return false;
  }
}

 class Fill extends DrawP5 {
  constructor(hexcode, alpha){
    super("Fill");
    this.color = hexcode;
    this.alpha = alpha;
  }

  draw(p5,semi_opacity=false){
    let color = p5.color(this.color);
    console.log(color)
    if(!semi_opacity){
      color.setAlpha(this.alpha);
    }
    else{
      color.setAlpha(this.alpha*0.5);
    }
    p5.fill(color);
  }
}

 class NoFill extends DrawP5 {
  constructor(){
    super("NoFill")
  }

  draw(p5){
    p5.noFill();
  }
}

 class Stroke extends DrawP5 {
  constructor(hexcode,w, alpha){
    super("Stroke");
    this.color = hexcode;
    this.w = w;
    this.alpha = alpha;

  }

  draw(p5,semi_opacity=false){
    let color = p5.color(this.color);
    if(!semi_opacity){
      color.setAlpha(this.alpha);
    }
    else{
      color.setAlpha(this.alpha*0.5);
    }
    p5.stroke(color);
    p5.strokeWeight(this.w);
  }
}

 class NoStroke extends DrawP5 {
  constructor(){
    super("NoStroke")
  }

  draw(p5){
    p5.noStroke();
  }
}