from src.game import Game, Player, draw_status, draw_text


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
            # Lazy import avoids circular imports between screens
            from src.screens.game_over import GameOverScreen
            self.app.change_screen(GameOverScreen(self.app, self.game))

    def draw(self, screen):
        self.game.draw(screen)
        draw_status(self.game, screen=screen)

        if self.paused:
            # Overlay only (simulation frozen)
            draw_text("PAUSED", 200, screen=screen)
            draw_text("PRESS P TO RESUME", 260, screen=screen)
