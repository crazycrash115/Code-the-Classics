"""Orb/bubble entity."""
from random import randint
from src.entities.base import CollideActor

class Orb(CollideActor):
    MAX_TIMER = 250
    
    def __init__(self, pos, dir_x):
        super().__init__(pos)
        self.direction_x = dir_x
        self.floating = False
        self.trapped_enemy_type = None
        self.timer = -1
        self.blown_frames = 6
    
    def hit_test(self, bolt):
        collided = self.collidepoint(bolt.pos)
        if collided:
            self.timer = Orb.MAX_TIMER - 1
        return collided
    
    def update(self, game):
        self.timer += 1
        
        if self.floating:
            self.move(0, -1, randint(1, 2), game.grid)
        else:
            if self.move(self.direction_x, 0, 4, game.grid):
                self.floating = True
        
        if self.timer == self.blown_frames:
            self.floating = True
        elif self.timer >= Orb.MAX_TIMER or self.y <= -40:
            from src.entities.pop import Pop
            from src.entities.fruit import Fruit
            game.pops.append(Pop(self.pos, 1))
            if self.trapped_enemy_type != None:
                game.fruits.append(Fruit(self.pos, self.trapped_enemy_type))
            game.play_sound("pop", 4)
        
        if self.timer < 9:
            self.image = "orb" + str(self.timer // 3)
        else:
            if self.trapped_enemy_type != None:
                self.image = "trap" + str(self.trapped_enemy_type) + str((self.timer // 4) % 8)
            else:
                self.image = "orb" + str(3 + (((self.timer - 9) // 8) % 4))
