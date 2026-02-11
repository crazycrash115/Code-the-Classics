from pgzero.actor import Actor
from random import randint
from math import sin, cos, pi
import pgzero.builtins as pgb

LEVEL_X_OFFSET = 48
GRID_BLOCK_SIZE = 16
NUM_ROWS = 29
NUM_COLUMNS = 44

# In order to keep levels as simple text files, we use characters to represent game objects:
# @ = player, X = block, / or \ = slopes, # = lava, ^ = spikes, + = fruit spawner
# * = key, K = door, E = enemy, F = fireball spawner, = = conveyor, > or < = moving platform
# H = hidden block
# Anything else is treated as empty space

OBJECTS = {
    "X": "block",
    "/": "slope_right",
    "\\": "slope_left",
    "#": "lava",
    "^": "spike",
    "*": "key",
    "K": "door",
    "E": "enemy",
    "F": "fireball",
    "=": "conveyor",
    ">": "moving_platform_right",
    "<": "moving_platform_left",
    "H": "hidden_block",
}


def sign(x):
    return (x > 0) - (x < 0)


def block(game, x, y):
    # NOTE (refactor safety): x/y may be floats (e.g., Actor positions after movement).
    # Using // with floats returns a float, which then breaks list indexing (TypeError).
    # Cast to int so grid lookup matches the original intent.
    grid_x = int((x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE)
    grid_y = int(y // GRID_BLOCK_SIZE)
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] != " "
    return False


def slope_right(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "/"


def slope_left(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "\\"


def lava(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "#"


def spike(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "^"


def key(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "*"


def door(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "K"


def conveyor(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "="


def moving_platform_right(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == ">"


def moving_platform_left(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "<"


def hidden_block(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "H"


def enemy(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "E"


def fireball(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] == "F"


class GameObject(Actor):
    def __init__(self, game, pos, image):
        super().__init__(image, pos)
        self.game = game

    def hit_test(self):
        return self.colliderect(self.game.player)

    def collect(self):
        pass


class Key(GameObject):
    def __init__(self, game, pos):
        super().__init__(game, pos, "key")

    def collect(self):
        self.game.got_key = True
        pgb.sounds.key.play()


class Door(GameObject):
    def __init__(self, game, pos):
        super().__init__(game, pos, "door")

    def update(self):
        if self.game.got_key:
            self.image = "door_open"


class Fruit(GameObject):
    def __init__(self, game, pos):
        super().__init__(game, pos, "fruit")
        self.image = "fruit"  # Match original asset name

    def collect(self):
        self.game.score += 50
        pgb.sounds.pickup.play()


class Enemy(GameObject):
    def __init__(self, game, pos):
        super().__init__(game, pos, "enemy0")
        self.direction = 1
        self.timer = randint(0, 99)

    def update(self):
        self.timer += 1
        if self.timer % 20 == 0:
            if block(self.game, self.x + self.direction * 16, self.y):
                self.direction *= -1
            else:
                self.x += self.direction * 16
        self.image = "enemy" + str((self.timer // 5) % 4)

        if self.hit_test():
            self.game.player.die()


class Fireball(GameObject):
    def __init__(self, game, pos):
        super().__init__(game, pos, "fire0")
        self.timer = randint(0, 99)

    def update(self):
        self.timer += 1
        self.image = "fire" + str((self.timer // 5) % 4)
        if self.hit_test():
            self.game.player.die()


class MovingPlatform(GameObject):
    def __init__(self, game, pos, direction):
        super().__init__(game, pos, "moving_platform")
        self.direction = direction
        self.timer = randint(0, 99)

    def update(self):
        self.timer += 1
        if self.timer % 30 == 0:
            if self.direction == 1:
                if moving_platform_right(self.game, self.x + 16, self.y):
                    self.x += 16
                else:
                    self.direction = -1
            else:
                if moving_platform_left(self.game, self.x - 16, self.y):
                    self.x -= 16
                else:
                    self.direction = 1

        if self.colliderect(self.game.player):
            self.game.player.x += self.direction * 1


class Player(Actor):
    def __init__(self, game, pos):
        super().__init__("player00", pos)
        self.game = game
        self.vx = 0
        self.vy = 0
        self.direction = 1
        self.fire_timer = 0
        self.dead = False

    def die(self):
        if not self.dead:
            self.dead = True
            self.fire_timer = 0
            pgb.sounds.die.play()

    def update(self, input_state):
        if self.dead:
            self.fire_timer += 1
            self.image = "blow" + str(min(3, self.fire_timer // 4))
            if self.fire_timer >= 20:
                self.game.lives -= 1
                if self.game.lives == 0:
                    self.game.game_over = True
                else:
                    self.game.reset_player()
            return

        # Horizontal movement
        self.vx = 0
        if input_state["left"]:
            self.vx = -2
            self.direction = -1
        elif input_state["right"]:
            self.vx = 2
            self.direction = 1

        # Fire
        if input_state["fire"] and self.fire_timer == 0:
            self.fire_timer = 8
            pgb.sounds.fire.play()

        if self.fire_timer > 0:
            self.fire_timer -= 1

        # Gravity
        self.vy += 0.2
        if self.vy > 4:
            self.vy = 4

        # Jump
        if input_state["jump"]:
            if block(self.game, self.x, self.y + 1) or slope_left(self.game, self.x, self.y + 1) or slope_right(self.game, self.x, self.y + 1):
                self.vy = -4
                pgb.sounds.jump.play()

        # Apply movement (step to allow collision resolution)
        self.x += self.vx
        if block(self.game, self.x, self.y) or slope_left(self.game, self.x, self.y) or slope_right(self.game, self.x, self.y):
            self.x -= self.vx

        self.y += self.vy
        if block(self.game, self.x, self.y) or slope_left(self.game, self.x, self.y) or slope_right(self.game, self.x, self.y):
            self.y -= self.vy
            self.vy = 0

        # Slopes
        if slope_right(self.game, self.x, self.y + 8):
            grid_x = (self.x - LEVEL_X_OFFSET) % GRID_BLOCK_SIZE
            self.y = (self.y // GRID_BLOCK_SIZE) * GRID_BLOCK_SIZE + (GRID_BLOCK_SIZE - grid_x) - 1

        if slope_left(self.game, self.x, self.y + 8):
            grid_x = (self.x - LEVEL_X_OFFSET) % GRID_BLOCK_SIZE
            self.y = (self.y // GRID_BLOCK_SIZE) * GRID_BLOCK_SIZE + grid_x - 1

        # Lava/spikes
        if lava(self.game, self.x, self.y + 8) or spike(self.game, self.x, self.y + 8):
            self.die()

        # Conveyor
        if conveyor(self.game, self.x, self.y + 8):
            self.x += 0.6

        # Door
        if door(self.game, self.x, self.y + 8) and self.game.got_key:
            self.game.complete_level()

        # Animation
        direction_idx = "0" if self.direction == 1 else "1"
        walk_frame = str((self.game.timer // 4) % 4)
        self.image = "player" + direction_idx + walk_frame
        if self.fire_timer > 0:
            self.image = "player" + direction_idx + str(5 + (self.fire_timer // 2))


class Game:
    def __init__(self, player=None):
        self.player = player
        self.level = 1
        self.level_colour = 0
        self.grid = []
        self.objects = []
        self.fruits = []
        self.enemies = []
        self.fireballs = []
        self.platforms = []
        self.timer = 0
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.got_key = False
        self.load_level()

    def reset_player(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == "@":
                    self.player = Player(self, (LEVEL_X_OFFSET + x * GRID_BLOCK_SIZE, y * GRID_BLOCK_SIZE))
                    return

    def complete_level(self):
        self.level += 1
        self.load_level()

    def load_level(self):
        filename = f"levels/level{self.level}.txt"
        self.grid = []
        self.objects = []
        self.fruits = []
        self.enemies = []
        self.fireballs = []
        self.platforms = []
        self.timer = 0
        self.got_key = False

        with open(filename, "r") as f:
            for line in f:
                self.grid.append(line.rstrip("\n"))

        self.level_colour = self.level % 4

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pos = (LEVEL_X_OFFSET + x * GRID_BLOCK_SIZE, y * GRID_BLOCK_SIZE)
                if cell == "@":
                    self.player = Player(self, pos)
                elif cell == "*":
                    self.objects.append(Key(self, pos))
                elif cell == "K":
                    self.objects.append(Door(self, pos))
                elif cell == "+":
                    self.fruits.append(Fruit(self, pos))
                elif cell == "E":
                    self.enemies.append(Enemy(self, pos))
                elif cell == "F":
                    self.fireballs.append(Fireball(self, pos))
                elif cell == ">":
                    self.platforms.append(MovingPlatform(self, pos, 1))
                elif cell == "<":
                    self.platforms.append(MovingPlatform(self, pos, -1))

    def update(self, input_state=None):
        self.timer += 1
        if self.game_over:
            return

        self.player.update(input_state)

        for obj in self.objects:
            obj.update()
            if obj.hit_test():
                obj.collect()
                self.objects.remove(obj)

        for obj in self.enemies:
            obj.update()

        for obj in self.fireballs:
            obj.update()

        for obj in self.platforms:
            obj.update()

        # Spawn fruit sometimes from + markers (existing fruit objects are just spawners)
        if self.timer % 120 == 0:
            # Find all + markers
            spawners = []
            for y, row in enumerate(self.grid):
                for x, cell in enumerate(row):
                    if cell == "+":
                        spawners.append((LEVEL_X_OFFSET + x * GRID_BLOCK_SIZE, y * GRID_BLOCK_SIZE))
            if spawners:
                self.fruits.append(Fruit(self, spawners[randint(0, len(spawners) - 1)]))

        for fruit in list(self.fruits):
            if fruit.hit_test():
                fruit.collect()
                self.fruits.remove(fruit)

    def draw(self, screen):
        screen.blit("bg%d" % self.level_colour, (0, 0))

        # Draw blocks etc from the grid
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pos = (LEVEL_X_OFFSET + x * GRID_BLOCK_SIZE, y * GRID_BLOCK_SIZE)
                if cell == "X":
                    screen.blit("block", pos)
                elif cell == "/":
                    screen.blit("slope_right", pos)
                elif cell == "\\":
                    screen.blit("slope_left", pos)
                elif cell == "#":
                    screen.blit("lava", pos)
                elif cell == "^":
                    screen.blit("spike", pos)
                elif cell == "=":
                    screen.blit("conveyor", pos)
                elif cell == "H":
                    screen.blit("hidden_block", pos)

        for obj in self.objects:
            obj.draw()

        for obj in self.enemies:
            obj.draw()

        for obj in self.fireballs:
            obj.draw()

        for obj in self.platforms:
            obj.draw()

        for fruit in self.fruits:
            fruit.draw()

        self.player.draw()

        screen.draw.text("Score: %d" % self.score, (20, 10), color="white")
        screen.draw.text("Lives: %d" % self.lives, (700, 10), color="white")

        if self.game_over:
            screen.draw.text("GAME OVER", center=(400, 240), fontsize=80, color="white")
