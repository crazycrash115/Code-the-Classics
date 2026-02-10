import pgzero.builtins as pgb

from src.game import draw_status


class GameOverScreen:
    def __init__(self, app, game):
        self.app = app
        # Keep showing the final play scene behind the overlay like original
        self.game = game

    def update(self, input_state):
        if input_state.jump_pressed:
            # Lazy import avoids circular imports between screens
            from src.screens.menu import MenuScreen
            self.app.change_screen(MenuScreen(self.app))

    def draw(self, screen):
        self.game.draw(screen)
        draw_status(self.game, screen=screen)
        screen.blit("over", (200, 150))
