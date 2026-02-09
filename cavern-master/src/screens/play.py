from game import Game, Player, draw_status, draw_text
from screens.game_over import GameOverScreen
from pgzero.builtins import screen

class PlayScreen:
    def __init__(self, app):
        self.app = app
        self.game = Game(player=Player())
        self.paused = False

    def update(self, input_state):
        # Task C: pause only in PlayScreen
        if input_state.pause_pressed:
            self.paused = not self.paused

        if self.paused:
            return

        # Task B: input flows into game -> player, not keyboard direct
        self.game.update(input_state=input_state)

        # Match original: game over when lives < 0
        if self.game.player and self.game.player.lives < 0:
            # Original played die sound when health hits 0; keep game over silent here
            self.app.change_screen(GameOverScreen(self.app, self.game))

    def draw(self):
        self.game.draw()
        draw_status(self.game)

        if self.paused:
            # Overlay only (simulation frozen)
            draw_text("PAUSED", 200)
            draw_text("PRESS P TO RESUME", 260)
