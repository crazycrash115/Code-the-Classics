"""Robot enemy entity."""
from random import choice, randint, random
from src.entities.base import GravityActor, sign

class Robot(GravityActor):
    TYPE_NORMAL = 0
    TYPE_AGGRESSIVE = 1
    
    def __init__(self, pos, type):
        super().__init__(pos)
        self.type = type
        self.speed = randint(1, 3)
        self.direction_x = 1
        self.alive = True
        self.change_dir_timer = 0
        self.fire_timer = 100
    
    def update(self, game):
        self.update_gravity(game)
        self.change_dir_timer -= 1
        self.fire_timer += 1
        
        if self.move(self.direction_x, 0, self.speed, game.grid):
            self.change_dir_timer = 0
        
        if self.change_dir_timer <= 0:
            directions = [-1, 1]
            if game.player:
                directions.append(sign(game.player.x - self.x))
            self.direction_x = choice(directions)
            self.change_dir_timer = randint(100, 250)
        
        if self.type == Robot.TYPE_AGGRESSIVE and self.fire_timer >= 24:
            for orb in game.orbs:
                if orb.y >= self.top and orb.y < self.bottom and abs(orb.x - self.x) < 200:
                    self.direction_x = sign(orb.x - self.x)
                    self.fire_timer = 0
                    break
        
        if self.fire_timer >= 12:
            fire_probability = 0.01 + game.level * 0.001
            if game.player and self.top < game.player.bottom and self.bottom > game.player.top:
                fire_probability *= 10
            if random() < fire_probability:
                self.fire_timer = 0
                game.play_sound("laser", 4)
        elif self.fire_timer == 8:
            from src.entities.bolt import Bolt
            game.bolts.append(Bolt((self.x + self.direction_x * 20, self.y - 38), self.direction_x))
        
        dir_index = "1" if self.direction_x > 0 else "0"
        anim_frame = str((game.timer // 6) % 8)
        self.image = "robot" + str(self.type) + dir_index + anim_frame
