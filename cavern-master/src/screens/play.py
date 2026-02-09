from game import Game, Player, draw_status, draw_text

class PlayScreen:
    def __init__(self, app):
        self.app = app
        self.game = Game(player=Player())
        self.paused = False

    def update(self, input_state):
        if input_state.pause_pressed:
            self.paused = not self.paused

        if self.paused:
            return

        self.game.update(input_state=input_state)

        if self.game.player and self.game.player.lives < 0:
            # Lazy import avoids circular dependency
            from screens.game_over import GameOverScreen
            self.app.change_screen(GameOverScreen(self.app, self.game))

    def draw(self):
        self.game.draw()
        if self.game.player:
            draw_status(self.game)

        if self.paused:
            draw_text("PAUSED", 200)
            draw_text("PRESS P TO RESUME", 260)
