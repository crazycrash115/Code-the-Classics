"""Base actor classes."""
from pgzero.actor import Actor

ANCHOR_CENTRE = ("center", "center")
ANCHOR_CENTRE_BOTTOM = ("center", "bottom")
GRID_BLOCK_SIZE = 25
LEVEL_X_OFFSET = 50
NUM_ROWS = 18
NUM_COLUMNS = 28
HEIGHT = 480
WIDTH = 800

def sign(x):
    return -1 if x < 0 else 1

def block(game_grid, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if grid_y > 0 and grid_y < NUM_ROWS:
        row = game_grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] != " "
    return False

class CollideActor(Actor):
    def __init__(self, pos, anchor=ANCHOR_CENTRE):
        super().__init__("blank", pos, anchor)
    
    def move(self, dx, dy, speed, game_grid):
        new_x, new_y = int(self.x), int(self.y)
        for i in range(speed):
            new_x, new_y = new_x + dx, new_y + dy
            if new_x < 70 or new_x > 730:
                return True
            if ((dy > 0 and new_y % GRID_BLOCK_SIZE == 0 or
                 dx > 0 and new_x % GRID_BLOCK_SIZE == 0 or
                 dx < 0 and new_x % GRID_BLOCK_SIZE == GRID_BLOCK_SIZE-1)
                and block(game_grid, new_x, new_y)):
                    return True
            self.pos = new_x, new_y
        return False

class GravityActor(CollideActor):
    MAX_FALL_SPEED = 10
    
    def __init__(self, pos):
        super().__init__(pos, ANCHOR_CENTRE_BOTTOM)
        self.vel_y = 0
        self.landed = False
    
    def update_gravity(self, game, detect=True):
        self.vel_y = min(self.vel_y + 1, GravityActor.MAX_FALL_SPEED)
        if detect:
            if self.move(0, sign(self.vel_y), abs(self.vel_y), game.grid):
                self.vel_y = 0
                self.landed = True
            if self.top >= HEIGHT:
                self.y = 1
        else:
            self.y += self.vel_y
