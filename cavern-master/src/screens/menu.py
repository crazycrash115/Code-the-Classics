"""Menu screen implementation."""
from src.game import Game
from src.entities.player import Player


class MenuScreen:
    """Main menu screen."""
    
    def __init__(self, app):
        """Initialize menu screen.
        
        Args:
            app: App instance for screen transitions
        """
        self.app = app
        self.game = None
    
    def on_enter(self):
        """Called when entering this screen."""
        # Create a game without a player for menu animations
        self.game = Game(player=None, sounds=self.app.sounds)
    
    def update(self, input_state):
        """Update menu screen.
        
        Args:
            input_state: InputState object with current frame's input
        """
        if input_state.menu_start:
            # Start game - import here to avoid circular dependency
            from src.screens.play import PlayScreen
            self.app.change_screen(PlayScreen(self.app))
        else:
            # Update game timer for animations
            self.game.timer += 1
    
    def draw(self):
        """Draw menu screen."""
        # Draw game background
        self.game.draw(self.app.screen)
        
        # Draw title
        self.app.screen.blit("title", (0, 0))
        
        # Draw "Press SPACE" animation
        anim_frame = min(((self.game.timer + 40) % 160) // 4, 9)
        self.app.screen.blit("space" + str(anim_frame), (130, 280))
