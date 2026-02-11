"""Player entity with refactored input handling."""
from random import randint
from src.entities.base import GravityActor, WIDTH

class Player(GravityActor):
    def __init__(self):
        super().__init__((0, 0))
        self.lives = 2
        self.score = 0
        self.reset()
    
    def reset(self):
        self.pos = (WIDTH / 2, 100)
        self.vel_y = 0
        self.direction_x = 1
        self.fire_timer = 0
        self.hurt_timer = 100
        self.health = 3
        self.blowing_orb = None
    
    def level_up(self):
        """Called when advancing to next level."""
        self.reset()
    
    def hit_test(self, other):
        if self.collidepoint(other.pos) and self.hurt_timer < 0:
            self.hurt_timer = 200
            self.health -= 1
            self.vel_y = -12
            self.landed = False
            self.direction_x = other.direction_x
            return True
        return False
    
    def update(self, input_state, game):
        """Update player - now uses InputState instead of keyboard directly."""
        # Apply gravity
        self.update_gravity(game, self.health > 0)
        
        self.fire_timer -= 1
        self.hurt_timer -= 1
        
        if self.landed:
            self.hurt_timer = min(self.hurt_timer, 100)
        
        if self.hurt_timer > 100:
            if self.health > 0:
                self.move(self.direction_x, 0, 4, game.grid)
            else:
                if self.top >= 480*1.5:
                    self.lives -= 1
                    self.reset()
        else:
            # Handle movement using InputState
            dx = 0
            if input_state.left:
                dx = -1
            elif input_state.right:
                dx = 1
            
            if dx != 0:
                self.direction_x = dx
                if self.fire_timer < 10:
                    self.move(dx, 0, 4, game.grid)
            
            # Fire orb using InputState
            if input_state.fire_pressed and self.fire_timer <= 0 and len(game.orbs) < 5:
                from src.entities.orb import Orb
                x = min(730, max(70, self.x + self.direction_x * 38))
                y = self.y - 35
                self.blowing_orb = Orb((x,y), self.direction_x)
                game.orbs.append(self.blowing_orb)
                game.play_sound("blow", 4)
                self.fire_timer = 20
            
            # Jump using InputState
            if input_state.jump_pressed and self.vel_y == 0 and self.landed:
                self.vel_y = -16
                self.landed = False
                game.play_sound("jump")
        
        # Blow orb further if holding fire
        if input_state.fire_held:
            if self.blowing_orb:
                self.blowing_orb.blown_frames += 4
                if self.blowing_orb.blown_frames >= 120:
                    self.blowing_orb = None
        else:
            self.blowing_orb = None
        
        # Set sprite
        self.image = "blank"
        if self.hurt_timer <= 0 or self.hurt_timer % 2 == 1:
            dir_index = "1" if self.direction_x > 0 else "0"
            if self.hurt_timer > 100:
                if self.health > 0:
                    self.image = "recoil" + dir_index
                else:
                    self.image = "fall" + str((game.timer // 4) % 2)
            elif self.fire_timer > 0:
                self.image = "blow" + dir_index
            elif dx == 0:
                self.image = "still"
            else:
                self.image = "run" + dir_index + str((game.timer // 8) % 4)
