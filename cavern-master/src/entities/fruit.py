"""Fruit/powerup entity."""
from random import choice
from src.entities.base import GravityActor
from src.entities.robot import Robot

class Fruit(GravityActor):
    APPLE = 0
    RASPBERRY = 1
    LEMON = 2
    EXTRA_HEALTH = 3
    EXTRA_LIFE = 4
    
    def __init__(self, pos, trapped_enemy_type=0):
        super().__init__(pos)
        
        if trapped_enemy_type == Robot.TYPE_NORMAL:
            self.type = choice([Fruit.APPLE, Fruit.RASPBERRY, Fruit.LEMON])
        else:
            types = 10 * [Fruit.APPLE, Fruit.RASPBERRY, Fruit.LEMON]
            types += 9 * [Fruit.EXTRA_HEALTH]
            types += [Fruit.EXTRA_LIFE]
            self.type = choice(types)
        
        self.timer = 0
    
    def update(self, game):
        self.update_gravity(game)
        
        if game.player and game.player.collidepoint(self.center):
            from src.entities.pop import Pop
            if self.type == Fruit.EXTRA_HEALTH:
                game.player.health = min(3, game.player.health + 1)
                game.play_sound("bonus")
            elif self.type == Fruit.EXTRA_LIFE:
                game.player.lives += 1
                game.play_sound("bonus")
            else:
                game.player.score += (self.type + 1) * 100
                game.play_sound("score")
            self.timer = 200
            game.pops.append(Pop((self.x, self.y - 27), 0))
        else:
            self.timer += 1
        
        if self.timer >= 200:
            from src.entities.pop import Pop
            game.pops.append(Pop((self.x, self.y - 27), 0))
        
        anim_frame = str([0, 1, 2, 1][(game.timer // 6) % 4])
        self.image = "fruit" + str(self.type) + anim_frame
