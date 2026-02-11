"""Drawing utilities for text and UI."""

WIDTH = 800
HEIGHT = 480

CHAR_WIDTH = [27, 26, 25, 26, 25, 25, 26, 25, 12, 26, 26, 25, 33, 25, 26,
              25, 27, 26, 26, 25, 26, 26, 38, 25, 25, 25]

def char_width(char):
    index = max(0, ord(char) - 65)
    return CHAR_WIDTH[index]

def draw_text(screen, text, y, x=None):
    if x == None:
        x = (WIDTH - sum([char_width(c) for c in text])) // 2
    for char in text:
        screen.blit("font0"+str(ord(char)), (x, y))
        x += char_width(char)

IMAGE_WIDTH = {"life":44, "plus":40, "health":40}

def draw_status(screen, player, level):
    # Score
    number_width = CHAR_WIDTH[0]
    s = str(player.score)
    draw_text(screen, s, 451, WIDTH - 2 - (number_width * len(s)))
    
    # Level
    draw_text(screen, "LEVEL " + str(level + 1), 451)
    
    # Lives and health
    lives_health = ["life"] * min(2, player.lives)
    if player.lives > 2:
        lives_health.append("plus")
    if player.lives >= 0:
        lives_health += ["health"] * player.health
    
    x = 0
    for image in lives_health:
        screen.blit(image, (x, 450))
        x += IMAGE_WIDTH[image]
