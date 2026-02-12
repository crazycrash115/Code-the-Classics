"""Play screen implementation with pause support."""
from src.game import Game
from src.entities.player import Player
from src.entities.draw_utils import draw_status, draw_text


class PlayScreen:
    """Active gameplay screen."""
    
    def __init__(self, app):
        """Initialize play screen.
        
        Args:
            app: App instance for screen transitions
        """
        self.app = app
        self.game = None
        self.paused = False
    
    def on_enter(self):
        """Called when entering this screen."""
        # Create new game with player
        player = Player()
        self.game = Game(player=player, sounds=self.app.sounds)
        self.paused = False
    
    def update(self, input_state):
        """Update play screen.
        
        Args:
            input_state: InputState object with current frame's input
        """
        # Handle pause toggle
        if input_state.pause_pressed:
            self.paused = not self.paused
        
        # Only update game if not paused
        if not self.paused:
            self.game.update(input_state)
            
            # Check for game over
            if self.game.player.lives < 0:
                self.game.play_sound("over")
                from src.screens.game_over import GameOverScreen
                self.app.change_screen(GameOverScreen(self.app, self.game))
    
    def draw(self):
        """Draw play screen."""
        # Draw game
        self.game.draw(self.app.screen)
        
        # Draw status
        draw_status(self.app.screen, self.game.player, self.game.level)
        
        # Draw pause overlay if paused
        if self.paused:
            # Semi-transparent overlay effect - just draw text for simplicity
            draw_text(self.app.screen, "PAUSED", 200)
            draw_text(self.app.screen, "PRESS P TO RESUME", 250)
