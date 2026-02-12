"""Game over screen implementation."""
from src.entities.draw_utils import draw_status


class GameOverScreen:
    """Game over screen."""
    
    def __init__(self, app, game):
        """Initialize game over screen.
        
        Args:
            app: App instance for screen transitions
            game: Game instance to display final state
        """
        self.app = app
        self.game = game
    
    def on_enter(self):
        """Called when entering this screen."""
        pass
    
    def update(self, input_state):
        """Update game over screen.
        
        Args:
            input_state: InputState object with current frame's input
        """
        if input_state.menu_start:
            # Return to menu
            from src.screens.menu import MenuScreen
            self.app.change_screen(MenuScreen(self.app))
    
    def draw(self):
        """Draw game over screen."""
        # Draw final game state
        self.game.draw(self.app.screen)
        
        # Draw status
        draw_status(self.app.screen, self.game.player, self.game.level)
        
        # Draw "Game Over" image
        self.app.screen.blit("over", (0, 0))
