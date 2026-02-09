from game import Game, draw_text
from screens.play import PlayScreen
from pgzero.builtins import screen

class MenuScreen:
    def __init__(self, app):
        self.app = app
        # Matches original: menu has a Game with no player
        self.game = Game(player=None)

    def update(self, input_state):
        # Keep original menu animation timing: tick game timer
        self.game.update(input_state=None)

        if input_state.jump_pressed:
            self.app.change_screen(PlayScreen(self.app))

    def draw(self):
        # Match original: draw the level background/blocks even on menu
        self.game.draw()

        # Original menu overlay: title + animated space prompt
        screen.blit("title", (150, 50))

        # Blink effect based on timer (same style as original)
        if (self.game.timer // 30) % 2 == 0:
            draw_text("PRESS SPACE", 320)
            draw_text("TO START", 360)
