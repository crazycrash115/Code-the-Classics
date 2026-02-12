"""Game logic extracted from original cavern.py"""
from random import choice, randint, random, shuffle
from src.entities.player import Player
from src.entities.robot import Robot
from src.entities.orb import Orb
from src.entities.bolt import Bolt
from src.entities.pop import Pop
from src.entities.fruit import Fruit

# Constants
NUM_ROWS = 18
NUM_COLUMNS = 28
LEVEL_X_OFFSET = 50
GRID_BLOCK_SIZE = 25

LEVELS = [
    # Level 1 - 18 rows
    ["XXXXX     XXXXXXXX     XXXXX",
     "", "", "", "",
     "   XXXXXXX        XXXXXXX   ",
     "", "", "",
     "   XXXXXXXXXXXXXXXXXXXXXX   ",
     "", "", "",
     "XXXXXXXXX          XXXXXXXXX",
     "", "", ""],

    # Level 2 - 18 rows
    ["XXXX    XXXXXXXXXXXX    XXXX",
     "", "", "", "",
     "    XXXXXXXXXXXXXXXXXXXX    ",
     "", "", "",
     "XXXXXX                XXXXXX",
     "      X              X      ",
     "       X            X       ",
     "        X          X        ",
     "         X        X         ",
     "", "", ""],

    # Level 3 - 18 rows
    ["XXXX    XXXX    XXXX    XXXX",
     "", "", "", "",
     "  XXXXXXXX        XXXXXXXX  ",
     "", "", "",
     "XXXX      XXXXXXXX      XXXX",
     "", "", "",
     "    XXXXXX        XXXXXX    ",
     "", "", ""]
]


def block(game_grid, x, y):
    """Check if there's a level grid block at these coordinates."""
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if grid_y > 0 and grid_y < NUM_ROWS:
        row = game_grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] != " "
    else:
        return False


class Game:
    """Main game logic for Cavern."""
    
    def __init__(self, player=None, sounds=None):
        self.player = player
        self.sounds = sounds
        self.timer = 0
        self.level = 0
        self.level_colour = 0
        
        # Game object lists
        self.enemies = []
        self.pending_enemies = []
        self.fruits = []
        self.orbs = []
        self.bolts = []
        self.pops = []
        
        # Set up level grid
        self.grid = []
        self.setup_level()
    
    def setup_level(self):
        """Initialize a new level."""
        # Get level grid (17 rows)
        self.grid = LEVELS[self.level % len(LEVELS)]
        # The last row is a copy of the first row (makes 18 total)
        # Create new list to avoid modifying LEVELS
        self.grid = self.grid + [self.grid[0]]
        self.level_colour = self.level % 4
        
        # Clear all game objects
        self.enemies.clear()
        self.pending_enemies.clear()
        self.fruits.clear()
        self.orbs.clear()
        self.bolts.clear()
        self.pops.clear()
        
        # Set up pending enemies for this level
        num_enemies = 4 + self.level
        enemy_types = [0] * num_enemies
        
        # Some enemies will be type 1 (which can drop power-ups)
        num_type1 = (self.level // 3) + 1
        for i in range(num_type1):
            enemy_types[randint(0, num_enemies - 1)] = 1
        
        shuffle(enemy_types)
        self.pending_enemies = enemy_types
        
        # Position player
        if self.player:
            self.player.pos = (400, 100)
            self.player.direction_x = 1
    
    def max_enemies(self):
        """Maximum number of enemies that can be active at once."""
        return min(self.level + 2, 6)
    
    def get_robot_spawn_x(self):
        """Get random x position for spawning a robot."""
        return choice([100, 250, 400, 550, 700])
    
    def next_level(self):
        """Advance to next level."""
        self.level += 1
        if self.player:
            self.player.level_up()
        self.setup_level()
        self.play_sound("level")
    
    def update(self, input_state):
        """Update game state.
        
        Args:
            input_state: InputState object with current frame's input
        """
        self.timer += 1
        
        # Update player
        if self.player:
            self.player.update(input_state, self)
        
        # Update all game objects
        for obj_list in [self.enemies, self.orbs, self.bolts, self.pops, self.fruits]:
            for obj in obj_list:
                obj.update(self)
        
        # Remove inactive objects
        self.bolts = [b for b in self.bolts if b.active]
        self.fruits = [f for f in self.fruits if f.timer < 200]
        self.pops = [p for p in self.pops if p.timer < 12]
        self.orbs = [o for o in self.orbs if o.timer < 250 and o.y > -40]
        
        # Every 100 frames, create random fruit
        if self.timer % 100 == 0 and len(self.pending_enemies + self.enemies) > 0:
            self.fruits.append(Fruit((randint(70, 730), randint(75, 400))))
        
        # Every 81 frames, spawn enemy if possible
        if self.timer % 81 == 0 and len(self.pending_enemies) > 0 and len(self.enemies) < self.max_enemies():
            robot_type = self.pending_enemies.pop()
            pos = (self.get_robot_spawn_x(), -30)
            self.enemies.append(Robot(pos, robot_type))
        
        # Check for level completion
        if len(self.pending_enemies + self.fruits + self.enemies + self.pops) == 0:
            if len([orb for orb in self.orbs if orb.trapped_enemy_type != None]) == 0:
                self.next_level()
    
    def draw(self, screen):
        """Draw the game state.
        
        Args:
            screen: Pygame Zero screen object
        """
        # Draw background
        screen.blit("bg%d" % self.level_colour, (0, 0))
        
        # Draw level blocks
        block_sprite = "block" + str(self.level % 4)
        for row_y in range(NUM_ROWS):
            row = self.grid[row_y]
            if len(row) > 0:
                x = LEVEL_X_OFFSET
                for block_char in row:
                    if block_char != ' ':
                        screen.blit(block_sprite, (x, row_y * GRID_BLOCK_SIZE))
                    x += GRID_BLOCK_SIZE
        
        # Draw all game objects
        all_objs = self.fruits + self.bolts + self.enemies + self.pops + self.orbs
        if self.player:
            all_objs.append(self.player)
        for obj in all_objs:
            if obj:
                obj.draw()
    
    def play_sound(self, name, count=1):
        """Play a sound effect.
        
        Args:
            name: Sound name
            count: Number of sound variations (will pick random)
        """
        if self.player and self.sounds:
            try:
                sound = getattr(self.sounds, name + str(randint(0, count - 1)))
                sound.play()
            except Exception as e:
                print(e)
