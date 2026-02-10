import pgzero.builtins as pgb

from game import Game, draw_text


class MenuScreen:
    def __init__(self, app):
        self.app = app
        # Matches original: menu has a Game with no player (background only)
        self.game = Game(player=None)

    def update(self, input_state):
        # IMPORTANT: don't run full Game.update() on the menu, because that spawns fruit/enemies.
        # We only tick the timer so the blink animation stays identical.
        self.game.timer += 1

        if input_state.jump_pressed:
            # Lazy import avoids circular imports between screens
            from screens.play import PlayScreen
            self.app.change_screen(PlayScreen(self.app))

    def draw(self, screen):
        self.game.draw(screen)
        screen.blit("title", (150, 50))

        # Original menu overlay: title + animated space prompt
        # NOTE: This second blit was present during refactoring. It is redundant with the line above,
        # but is kept to preserve current behavior exactly.
        pgb.screen.blit("title", (150, 50))

        # Blink effect based on timer (same style as original)
        if (self.game.timer // 30) % 2 == 0:
            draw_text("PRESS SPACE", 320, screen=screen)
            draw_text("TO START", 360, screen=screen)
