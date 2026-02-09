from screens.menu import MenuScreen
from game import draw_status
from pgzero.builtins import screen

class GameOverScreen:
    def __init__(self, app, game):
        self.app = app
        # Keep showing the final play scene behind the overlay like original
        self.game = game

    def update(self, input_state):
        if input_state.jump_pressed:
            self.app.change_screen(MenuScreen(self.app))

    def draw(self):
        self.game.draw()
        if self.game.player:
            draw_status(self.game)
        screen.blit("over", (200, 150))
