"""Pop animation entity."""
from pgzero.actor import Actor

class Pop(Actor):
    def __init__(self, pos, type):
        super().__init__("blank", pos)
        self.type = type
        self.timer = -1
    
    def update(self, game):
        self.timer += 1
        self.image = "pop" + str(self.type) + str(self.timer // 2)
