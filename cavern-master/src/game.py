from random import choice, randint, random, shuffle
from pgzero.actor import Actor
import pgzero.builtins as pgb

# Set up constants
WIDTH = 800
HEIGHT = 480
TITLE = "Cavern"

NUM_ROWS = 18
NUM_COLUMNS = 28

LEVEL_X_OFFSET = 50
GRID_BLOCK_SIZE = 25

ANCHOR_CENTRE = ("center", "center")
ANCHOR_CENTRE_BOTTOM = ("center", "bottom")

LEVELS = [
    ["XXXXX     XXXXXXXX     XXXXX",
     "", "", "", "",
     "   XXXXXXX        XXXXXXX   ",
     "", "", "",
     "   XXXXXXXXXXXXXXXXXXXXXX   ",
     "", "", "",
     "XXXXXXXXX          XXXXXXXXX",
     "", "", ""],

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

    ["XXXX    XXXX    XXXX    XXXX",
     "", "", "", "",
     "  XXXXXXXX        XXXXXXXX  ",
     "", "", "",
     "XXXX      XXXXXXXX      XXXX",
     "", "", "",
     "    XXXXXX        XXXXXX    ",
     "", "", ""]
]

def sign(x):
    return -1 if x < 0 else 1

# Widths of the letters A to Z in the font images
CHAR_WIDTH = [27, 26, 25, 26, 25, 25, 26, 25, 12, 26, 26, 25, 33, 25, 26,
              25, 27, 26, 26, 25, 26, 26, 38, 25, 25, 25]

def char_width(char):
    index = max(0, ord(char) - 65)
    return CHAR_WIDTH[index]

def draw_text(text, y, x=None, screen=None):
    """Draws text using the game's bitmap font.

    IMPORTANT FIX:
    - Your refactor passes `screen` down (app.draw(screen) -> screen.draw(screen) -> game.draw(screen)).
    - On your pgzero version, pgzero.builtins has NO 'screen', so we must NOT fallback to pgb.screen.
    - If screen is missing, we raise a clear error instead of crashing later.
    """
    if screen is None:
        raise RuntimeError(
            "draw_text() requires a 'screen' argument. "
            "Call it like draw_text('HELLO', y, screen=screen) from a draw(screen) method."
        )

    if x is None:
        x = (WIDTH - sum([char_width(c) for c in text])) // 2

    for char in text:
        screen.blit("font0" + str(ord(char)), (x, y))
        x += char_width(char)

IMAGE_WIDTH = {"life": 44, "plus": 40, "health": 40}

def draw_status(game, screen=None):
    """Draw the HUD (score, level, lives/health).

    IMPORTANT FIX:
    - Same as draw_text(): no pgb.screen fallback.
    """
    if screen is None:
        raise RuntimeError(
            "draw_status() requires a 'screen' argument. "
            "Call it like draw_status(game, screen=screen) from a draw(screen) method."
        )

    number_width = CHAR_WIDTH[0]
    s = str(game.player.score)
    draw_text(s, 451, WIDTH - 2 - (number_width * len(s)), screen=screen)

    draw_text("LEVEL " + str(game.level + 1), 451, screen=screen)

    lives_health = ["life"] * min(2, game.player.lives)
    if game.player.lives > 2:
        lives_health.append("plus")
    if game.player.lives >= 0:
        lives_health += ["health"] * game.player.health

    x = 0
    for image in lives_health:
        screen.blit(image, (x, 450))
        x += IMAGE_WIDTH[image]

def block(game, x, y):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] != " "
    return False


class CollideActor(pgb.Actor):
    def __init__(self, game, pos, anchor=ANCHOR_CENTRE):
        self.game = game
        super().__init__("blank", pos, anchor)

    def move(self, dx, dy, speed):
        new_x, new_y = int(self.x), int(self.y)

        for _ in range(speed):
            new_x, new_y = new_x + dx, new_y + dy

            if new_x < 70 or new_x > 730:
                return True

            if ((dy > 0 and new_y % GRID_BLOCK_SIZE == 0 or
                 dx > 0 and new_x % GRID_BLOCK_SIZE == 0 or
                 dx < 0 and new_x % GRID_BLOCK_SIZE == GRID_BLOCK_SIZE - 1)
                and block(self.game, new_x, new_y)):
                return True

        self.pos = (new_x, new_y)
        return False


class Bolt(CollideActor):
    def __init__(self, game, pos, direction_x):
        super().__init__(game, pos, ANCHOR_CENTRE)
        self.direction_x = direction_x
        self.active = True
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer > 30:
            self.active = False
        self.x += self.direction_x * 10
        self.image = "bolt" + ("1" if self.direction_x > 0 else "0") + str((self.timer // 4) % 2)

        if self.x < 0 or self.x > WIDTH:
            self.active = False

        for enemy in self.game.enemies:
            if enemy.alive and self.colliderect(enemy):
                enemy.health -= 1
                self.active = False
                break


class Fruit(CollideActor):
    def __init__(self, game, pos):
        super().__init__(game, pos, ANCHOR_CENTRE)
        self.image = "fruit"
        self.time_to_live = 400

    def update(self):
        self.time_to_live -= 1
        self.y += 1


class Pop(CollideActor):
    def __init__(self, game, pos):
        super().__init__(game, pos, ANCHOR_CENTRE)
        self.timer = 0

    def update(self):
        self.timer += 1
        self.image = "pop" + str(self.timer // 2)


class Orb(CollideActor):
    def __init__(self, game, pos, direction_x):
        super().__init__(game, pos, ANCHOR_CENTRE)
        self.direction_x = direction_x
        self.timer = 0
        self.trapped_enemy_type = None
        self.floating = False

    def update(self):
        self.timer += 1

        if self.timer <= 12:
            self.image = "blow" + str(self.timer // 2)

        if self.trapped_enemy_type is not None:
            self.image = "orb" + str(self.trapped_enemy_type) + str((self.timer // 4) % 4)

        if self.floating:
            self.y -= 1

        else:
            self.move(self.direction_x, 0, 1)

        if self.timer >= 250:
            if self.trapped_enemy_type is not None:
                self.game.pops.append(Pop(self.game, self.pos))
                self.game.play_sound("pop", 4)
                if self.game.player:
                    self.game.player.score += 500
                    self.game.player.health = min(5, self.game.player.health + 1)

            self.trapped_enemy_type = None


class Character(CollideActor):
    def __init__(self, game, pos, anchor=ANCHOR_CENTRE_BOTTOM):
        super().__init__(game, pos, anchor)
        self.vel_y = 0
        self.landed = False

    def update(self):
        self.vel_y += 1
        self.y += self.vel_y

        if self.y % GRID_BLOCK_SIZE == 0:
            if block(self.game, self.x, self.y):
                while block(self.game, self.x, self.y):
                    self.y -= 1

                self.vel_y = 0
                self.landed = True

            else:
                self.landed = False


class Player(Character):
    def __init__(self):
        super().__init__(None, (WIDTH / 2, HEIGHT - 8), ANCHOR_CENTRE_BOTTOM)
        self.score = 0
        self.lives = 2
        self.health = 5
        self.direction_x = 1
        self.hurt_timer = 0
        self.fire_timer = 0

    def attach_game(self, game):
        self.game = game

    def reset(self):
        self.pos = (WIDTH / 2, HEIGHT - 8)
        self.vel_y = 0
        self.landed = False
        self.health = 5
        self.hurt_timer = 0
        self.fire_timer = 0

    def hurt(self):
        if self.hurt_timer <= 0:
            self.hurt_timer = 60
            self.health -= 1
            if self.health <= 0:
                self.game.play_sound("die", 1)
            else:
                self.game.play_sound("hurt", 1)

    def update(self, input_state):
        self.hurt_timer -= 1
        self.fire_timer += 1

        super().update()

        if self.health <= 0:
            self.image = "player8"
            if self.top > HEIGHT * 1.5:
                self.lives -= 1
                self.reset()
            return

        dx = 0
        if input_state.left:
            dx = -1
        elif input_state.right:
            dx = 1

        if dx != 0:
            self.direction_x = dx
            self.move(dx, 0, 3)

        if input_state.up and self.landed:
            self.vel_y = -14
            self.landed = False
            self.game.play_sound("jump", 1)

        if input_state.fire_pressed and self.fire_timer >= 10:
            self.fire_timer = 0
            self.game.play_sound("blow", 4)
            self.game.orbs.append(Orb(self.game, (self.x + (self.direction_x * 15), self.y - 25), self.direction_x))

        direction_idx = "1" if self.direction_x > 0 else "0"

        if self.fire_timer < 8:
            self.image = "player" + direction_idx + str(5 + (self.fire_timer // 2))
        elif not self.landed:
            self.image = "player" + direction_idx + "4"
        else:
            self.image = "player" + direction_idx + str(1 + ((self.game.timer // 4) % 4))

        for fruit in self.game.fruits:
            if fruit.colliderect(self):
                fruit.time_to_live = 0
                self.score += 100
                self.game.play_sound("fruit", 4)

        for enemy in self.game.enemies:
            if enemy.alive and enemy.colliderect(self):
                self.hurt()


class Robot(Character):
    TYPE_NORMAL = 0
    TYPE_AGGRESSIVE = 1

    def __init__(self, game, pos, robot_type):
        super().__init__(game, pos, ANCHOR_CENTRE_BOTTOM)
        self.type = robot_type
        self.direction_x = choice([-1, 1])
        self.speed = 2 if robot_type == Robot.TYPE_NORMAL else 3
        self.health = 1 if robot_type == Robot.TYPE_NORMAL else 2
        self.alive = True

        self.change_dir_timer = randint(100, 250)
        self.fire_timer = randint(0, 24)

    def update(self):
        if not self.alive:
            self.vel_y += 1
            self.y += self.vel_y
            self.image = "robot" + str(self.type) + "00"
            return

        super().update()

        self.change_dir_timer -= 1
        self.fire_timer += 1

        if self.move(self.direction_x, 0, self.speed):
            self.change_dir_timer = 0

        if self.change_dir_timer <= 0:
            directions = [-1, 1]
            if self.game.player:
                directions.append(sign(self.game.player.x - self.x))
            self.direction_x = choice(directions)
            self.change_dir_timer = randint(100, 250)

        if self.type == Robot.TYPE_AGGRESSIVE and self.fire_timer >= 24:
            for orb in self.game.orbs:
                if orb.y >= self.top and orb.y < self.bottom and abs(orb.x - self.x) < 200:
                    self.direction_x = sign(orb.x - self.x)
                    self.fire_timer = 0
                    break

        if self.fire_timer >= 12:
            fire_probability = self.game.fire_probability()
            if self.game.player and self.top < self.game.player.bottom and self.bottom > self.game.player.top:
                fire_probability *= 10
            if random() < fire_probability:
                self.fire_timer = 0
                self.game.play_sound("laser", 4)

        elif self.fire_timer == 8:
            self.game.bolts.append(Bolt(self.game, (self.x + self.direction_x * 20, self.y - 38), self.direction_x))

        for orb in self.game.orbs:
            if orb.trapped_enemy_type is None and self.collidepoint(orb.center):
                self.alive = False
                orb.floating = True
                orb.trapped_enemy_type = self.type
                self.game.play_sound("trap", 4)
                break

        direction_idx = "1" if self.direction_x > 0 else "0"
        image = "robot" + str(self.type) + direction_idx
        if self.fire_timer < 12:
            image += str(5 + (self.fire_timer // 4))
        else:
            image += str(1 + ((self.game.timer // 4) % 4))
        self.image = image


class Game:
    def __init__(self, player=None):
        self.player = player
        self.level_colour = -1
        self.level = -1

        self.next_level()

    def fire_probability(self):
        return 0.001 + (0.0001 * min(100, self.level))

    def max_enemies(self):
        return min((self.level + 6) // 2, 8)

    def next_level(self):
        self.level_colour = (self.level_colour + 1) % 4
        self.level += 1

        self.grid = LEVELS[self.level % len(LEVELS)]
        self.grid = self.grid + [self.grid[0]]

        self.timer = -1

        if self.player:
            self.player.attach_game(self)
            self.player.reset()

        self.fruits = []
        self.bolts = []
        self.enemies = []
        self.pops = []
        self.orbs = []

        num_enemies = 10 + self.level
        num_strong_enemies = 1 + int(self.level / 1.5)
        num_weak_enemies = num_enemies - num_strong_enemies

        self.pending_enemies = num_strong_enemies * [Robot.TYPE_AGGRESSIVE] + num_weak_enemies * [Robot.TYPE_NORMAL]
        shuffle(self.pending_enemies)

        self.play_sound("level", 1)

    def get_robot_spawn_x(self):
        r = randint(0, NUM_COLUMNS - 1)

        for i in range(NUM_COLUMNS):
            grid_x = (r + i) % NUM_COLUMNS
            if self.grid[0][grid_x] == " ":
                return GRID_BLOCK_SIZE * grid_x + LEVEL_X_OFFSET + 12

        return WIDTH / 2

    def update(self, input_state=None):
        self.timer += 1

        if self.player:
            self.player.update(input_state)

        for obj in self.fruits + self.bolts + self.enemies + self.pops + self.orbs:
            if obj:
                obj.update()

        self.fruits = [f for f in self.fruits if f.time_to_live > 0]
        self.bolts = [b for b in self.bolts if b.active]
        self.enemies = [e for e in self.enemies if e.alive]
        self.pops = [p for p in self.pops if p.timer < 12]
        self.orbs = [o for o in self.orbs if o.timer < 250 and o.y > -40]

        if self.timer % 100 == 0 and len(self.pending_enemies + self.enemies) > 0:
            self.fruits.append(Fruit(self, (randint(70, 730), randint(75, 400))))

        if self.timer % 81 == 0 and len(self.pending_enemies) > 0 and len(self.enemies) < self.max_enemies():
            robot_type = self.pending_enemies.pop()
            pos = (self.get_robot_spawn_x(), -30)
            self.enemies.append(Robot(self, pos, robot_type))

        if len(self.pending_enemies + self.fruits + self.enemies + self.pops) == 0:
            if len([orb for orb in self.orbs if orb.trapped_enemy_type is not None]) == 0:
                self.next_level()

    def draw(self, screen=None):
        """Draw the game scene.

        IMPORTANT FIX:
        - No pgb.screen fallback. Your refactor always passes `screen`.
        """
        if screen is None:
            raise RuntimeError(
                "Game.draw() requires a 'screen' argument. "
                "Call it like self.game.draw(screen) from a draw(screen) method."
            )

        screen.blit("bg%d" % self.level_colour, (0, 0))

        block_sprite = "block" + str(self.level % 4)

        for row_y in range(NUM_ROWS):
            row = self.grid[row_y]
            if len(row) > 0:
                x = LEVEL_X_OFFSET
                for blk in row:
                    if blk != " ":
                        screen.blit(block_sprite, (x, row_y * GRID_BLOCK_SIZE))
                    x += GRID_BLOCK_SIZE

        all_objs = self.fruits + self.bolts + self.enemies + self.pops + self.orbs
        if self.player:
            all_objs.append(self.player)

        for obj in all_objs:
            if obj:
                obj.draw()

    def play_sound(self, name, count=1):
        if self.player:
            try:
                sound = getattr(pgb.sounds, name + str(randint(0, count - 1)))
                sound.play()
            except Exception as e:
                print(e)
