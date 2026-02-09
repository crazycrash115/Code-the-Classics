import pgzero.builtins as pgb
from game import Game, draw_text

class MenuScreen:
    def __init__(self, app):
        self.app = app
        self.game = Game(player=None)

    def update(self, input_state):
        self.game.update(input_state=None)

        if input_state.jump_pressed:
            # Lazy import avoids circular dependency
            from screens.play import PlayScreen
            self.app.change_screen(PlayScreen(self.app))

    def draw(self):
        self.game.draw()

        pgb.screen.blit("title", (150, 50))

        if (self.game.timer // 30) % 2 == 0:
            draw_text("PRESS SPACE", 320)
            draw_text("TO START", 360)
