import pgzero.builtins as pgb
from game import draw_status

class GameOverScreen:
    def __init__(self, app, game):
        self.app = app
        self.game = game

    def update(self, input_state):
        if input_state.jump_pressed:
            # Lazy import avoids circular dependency
            from screens.menu import MenuScreen
            self.app.change_screen(MenuScreen(self.app))

    def draw(self):
        self.game.draw()
        if self.game.player:
            draw_status(self.game)
        pgb.screen.blit("over", (200, 150))
