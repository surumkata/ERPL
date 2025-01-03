 class Scenario {
  constructor(id) {
      this.id = id;
      this.currentView = null;
      this.views = {};
      this.sounds = {};
      this.hitboxes = {};
      this.texts = {};
 }

  changeCurrentView(viewId) {
      this.currentView = viewId;
      this.views[viewId].repeate = this.views[viewId].repeateInit;
      this.views[viewId].currentSprite = 0;
  }

  addView(view, initial = false) {
      this.views[view.id] = view;
      if (initial) {
          this.currentView = view.id;
      }
  }

  addSound(sound) {
      this.sounds[sound.id] = sound;
  }

  addHitboxes(hitboxes){
      hitboxes.forEach(hitbox => {
        this.hitboxes[hitbox.id] = hitbox
      });
  }

  addTexts(texts){
    texts.forEach(text => {
      this.texts[text.id] = text
    });
}

  collide(px,py,hitboxId){
      if (!this.hitboxes.hasOwnProperty(hitboxId)){
          return False
      }
      else{
          return this.hitboxes[hitboxId].collide(px,py)
      }
   }

  draw(p5, variables){
    if (this.currentView != null && this.currentView in this.views){
      this.views[this.currentView].draw(p5);
      
      for (const [key, text] of Object.entries(this.texts)) {
        text.draw(p5,variables);
        }

    }
  }
}