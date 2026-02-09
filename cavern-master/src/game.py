from random import choice, randint, random, shuffle
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

def draw_text(text, y, x=None):
    if x is None:
        x = (WIDTH - sum([char_width(c) for c in text])) // 2
    for char in text:
        pgb.screen.blit("font0" + str(ord(char)), (x, y))
        x += char_width(char)

IMAGE_WIDTH = {"life": 44, "plus": 40, "health": 40}

def draw_status(game):
    number_width = CHAR_WIDTH[0]
    s = str(game.player.score)
    draw_text(s, 451, WIDTH - 2 - (number_width * len(s)))

    draw_text("LEVEL " + str(game.level + 1), 451)

    lives_health = ["life"] * min(2, game.player.lives)
    if game.player.lives > 2:
        lives_health.append("plus")
    if game.player.lives >= 0:
        lives_health += ["health"] * game.player.health

    x = 0
    for image in lives_health:
        pgb.screen.blit(image, (x, 450))
        x += IMAGE_WIDTH[image]


class CollideActor(pgb.Actor):
    def __init__(self, game, pos, anchor=ANCHOR_CENTRE):
        super().__init__("blank", pos, anchor)
        self.game = game

    def move(self, dx, dy, speed):
        new_x, new_y = int(self.x), int(self.y)

        for _ in range(speed):
            new_x, new_y = new_x + dx, new_y + dy

            if new_x < 70 or new_x > 730:
                return True

            if ((dy > 0 and new_y % GRID_BLOCK_SIZE == 0 or
                 dx > 0 and new_x % GRID_BLOCK_SIZE == 0 or
                 dx < 0 and new_x % GRID_BLOCK_SIZE == GRID_BLOCK_SIZE - 1)
                and self.game.block_at(new_x, new_y)):
                return True

            self.pos = new_x, new_y

        return False


class Orb(CollideActor):
    MAX_TIMER = 250

    def __init__(self, game, pos, dir_x):
        super().__init__(game, pos)
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

    def update(self):
        self.timer += 1

        if self.floating:
            self.move(0, -1, randint(1, 2))
        else:
            if self.move(self.direction_x, 0, 4):
                self.floating = True

        if self.timer == self.blown_frames:
            self.floating = True
        elif self.timer >= Orb.MAX_TIMER or self.y <= -40:
            self.game.pops.append(Pop(self.game, self.pos, 1))
            if self.trapped_enemy_type is not None:
                self.game.fruits.append(Fruit(self.game, self.pos, self.trapped_enemy_type))
            self.game.play_sound("pop", 4)

        if self.timer < 9:
            self.image = "orb" + str(self.timer // 3)
        else:
            if self.trapped_enemy_type is not None:
                self.image = "trap" + str(self.trapped_enemy_type) + str((self.timer // 4) % 8)
            else:
                self.image = "orb" + str(3 + (((self.timer - 9) // 8) % 4))


class Bolt(CollideActor):
    SPEED = 7

    def __init__(self, game, pos, dir_x):
        super().__init__(game, pos)
        self.direction_x = dir_x
        self.active = True

    def update(self):
        if self.move(self.direction_x, 0, Bolt.SPEED):
            self.active = False
        else:
            for obj in self.game.orbs + [self.game.player]:
                if obj and obj.hit_test(self):
                    self.active = False
                    break

        direction_idx = "1" if self.direction_x > 0 else "0"
        anim_frame = str((self.game.timer // 4) % 2)
        self.image = "bolt" + direction_idx + anim_frame


class Pop(pgb.Actor):
    def __init__(self, game, pos, type):
        super().__init__("blank", pos)
        self.game = game
        self.type = type
        self.timer = -1

    def update(self):
        self.timer += 1
        self.image = "pop" + str(self.type) + str(self.timer // 2)


class GravityActor(CollideActor):
    MAX_FALL_SPEED = 10

    def __init__(self, game, pos):
        super().__init__(game, pos, ANCHOR_CENTRE_BOTTOM)
        self.vel_y = 0
        self.landed = False

    def update(self, detect=True):
        self.vel_y = min(self.vel_y + 1, GravityActor.MAX_FALL_SPEED)

        if detect:
            if self.move(0, sign(self.vel_y), abs(self.vel_y)):
                self.vel_y = 0
                self.landed = True

            if self.top >= HEIGHT:
                self.y = 1
        else:
            self.y += self.vel_y


class Fruit(GravityActor):
    APPLE = 0
    RASPBERRY = 1
    LEMON = 2
    EXTRA_HEALTH = 3
    EXTRA_LIFE = 4

    def __init__(self, game, pos, trapped_enemy_type=0):
        super().__init__(game, pos)

        if trapped_enemy_type == Robot.TYPE_NORMAL:
            self.type = choice([Fruit.APPLE, Fruit.RASPBERRY, Fruit.LEMON])
        else:
            types = 10 * [Fruit.APPLE, Fruit.RASPBERRY, Fruit.LEMON]
            types += 9 * [Fruit.EXTRA_HEALTH]
            types += [Fruit.EXTRA_LIFE]
            self.type = choice(types)

        self.time_to_live = 500

    def update(self):
        super().update()

        if self.game.player and self.game.player.collidepoint(self.center):
            if self.type == Fruit.EXTRA_HEALTH:
                self.game.player.health = min(3, self.game.player.health + 1)
                self.game.play_sound("bonus")
            elif self.type == Fruit.EXTRA_LIFE:
                self.game.player.lives += 1
                self.game.play_sound("bonus")
            else:
                self.game.player.score += (self.type + 1) * 100
                self.game.play_sound("score")
            self.time_to_live = 0
        else:
            self.time_to_live -= 1

        if self.time_to_live <= 0:
            self.game.pops.append(Pop(self.game, (self.x, self.y - 27), 0))

        anim_frame = str([0, 1, 2, 1][(self.game.timer // 6) % 4])
        self.image = "fruit" + str(self.type) + anim_frame


class Player(GravityActor):
    def __init__(self):
        super().__init__(game=None, pos=(0, 0))  # game attached later
        self.lives = 2
        self.score = 0

        self.direction_x = 1
        self.fire_timer = 0
        self.hurt_timer = 0
        self.health = 3
        self.blowing_orb = None

    def attach_game(self, game):
        self.game = game

    def reset(self):
        self.pos = (WIDTH / 2, 100)
        self.vel_y = 0
        self.direction_x = 1
        self.fire_timer = 0
        self.hurt_timer = 100
        self.health = 3
        self.blowing_orb = None

    def hit_test(self, other):
        if self.collidepoint(other.pos) and self.hurt_timer < 0:
            self.hurt_timer = 200
            self.health -= 1
            self.vel_y = -12
            self.landed = False
            self.direction_x = other.direction_x
            if self.health > 0:
                self.game.play_sound("ouch", 4)
            else:
                self.game.play_sound("die")
            return True
        return False

    def update(self, input_state):
        super().update(self.health > 0)

        self.fire_timer -= 1
        self.hurt_timer -= 1

        if self.landed:
            self.hurt_timer = min(self.hurt_timer, 100)

        dx = 0

        if self.hurt_timer > 100:
            if self.health > 0:
                self.move(self.direction_x, 0, 4)
            else:
                if self.top >= HEIGHT * 1.5:
                    self.lives -= 1
                    self.reset()
        else:
            dx = 0
            if input_state.left:
                dx = -1
            elif input_state.right:
                dx = 1

            if dx != 0:
                self.direction_x = dx
                if self.fire_timer < 10:
                    self.move(dx, 0, 4)

            if input_state.fire_pressed and self.fire_timer <= 0 and len(self.game.orbs) < 5:
                x = min(730, max(70, self.x + self.direction_x * 38))
                y = self.y - 35
                self.blowing_orb = Orb(self.game, (x, y), self.direction_x)
                self.game.orbs.append(self.blowing_orb)
                self.game.play_sound("blow", 4)
                self.fire_timer = 20

            if input_state.up and self.vel_y == 0 and self.landed:
                self.vel_y = -16
                self.landed = False
                self.game.play_sound("jump")

        if input_state.fire_held:
            if self.blowing_orb:
                self.blowing_orb.blown_frames += 4
                if self.blowing_orb.blown_frames >= 120:
                    self.blowing_orb = None
        else:
            self.blowing_orb = None

        self.image = "blank"
        if self.hurt_timer <= 0 or self.hurt_timer % 2 == 1:
            dir_index = "1" if self.direction_x > 0 else "0"
            if self.hurt_timer > 100:
                if self.health > 0:
                    self.image = "recoil" + dir_index
                else:
                    self.image = "fall" + str((self.game.timer // 4) % 2)
            elif self.fire_timer > 0:
                self.image = "blow" + dir_index
            elif dx == 0:
                self.image = "still"
            else:
                self.image = "run" + dir_index + str((self.game.timer // 8) % 4)


class Robot(GravityActor):
    TYPE_NORMAL = 0
    TYPE_AGGRESSIVE = 1

    def __init__(self, game, pos, type):
        super().__init__(game, pos)
        self.type = type
        self.speed = randint(1, 3)
        self.direction_x = 1
        self.alive = True
        self.change_dir_timer = 0
        self.fire_timer = 100

    def update(self):
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

        if self.player:
            self.player.attach_game(self)

        self.next_level()

    def block_at(self, x, y):
        grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
        grid_y = y // GRID_BLOCK_SIZE
        if 0 < grid_y < NUM_ROWS:
            row = self.grid[grid_y]
            return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] != " "
        return False

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

        for obj in self.fruits + self.bolts + self.enemies + self.pops + self.orbs:
            obj.update()

        if self.player:
            self.player.update(input_state)

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

    def draw(self):
        pgb.screen.blit("bg%d" % self.level_colour, (0, 0))
        block_sprite = "block" + str(self.level % 4)

        for row_y in range(NUM_ROWS):
            row = self.grid[row_y]
            if len(row) > 0:
                x = LEVEL_X_OFFSET
                for block in row:
                    if block != " ":
                        pgb.screen.blit(block_sprite, (x, row_y * GRID_BLOCK_SIZE))
                    x += GRID_BLOCK_SIZE

        all_objs = self.fruits + self.bolts + self.enemies + self.pops + self.orbs
        if self.player:
            all_objs.append(self.player)
        for obj in all_objs:
            obj.draw()

    def play_sound(self, name, count=1):
        if self.player:
            try:
                sound = getattr(pgb.sounds, name + str(randint(0, count - 1)))
                sound.play()
            except Exception as e:
                print(e)