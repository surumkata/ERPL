class Sound:
    def __init__(self, id : str, src_sound : str, loop : bool = False):
        self.sound = src_sound
        self.id = id
        self.loop = loop

    def serialize(self):
        return {
            "id" : self.id,
            "sources" : [['PATH', self.src_sound]],
            "loop" : self.loop
        }