"""Bolt/projectile entity."""
from src.entities.base import CollideActor

class Bolt(CollideActor):
    SPEED = 7
    
    def __init__(self, pos, dir_x):
        super().__init__(pos)
        self.direction_x = dir_x
        self.active = True
    
    def update(self, game):
        if self.move(self.direction_x, 0, Bolt.SPEED, game.grid):
            self.active = False
        else:
            for obj in game.orbs + [game.player]:
                if obj and obj.hit_test(self):
                    self.active = False
                    break
        
        direction_idx = "1" if self.direction_x > 0 else "0"
        anim_frame = str((game.timer // 4) % 2)
        self.image = "bolt" + direction_idx + anim_frame
