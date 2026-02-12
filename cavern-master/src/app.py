"""App class managing screen transitions."""
from src.input import InputManager


class App:
    """Application manager handling screen state and transitions."""
    
    def __init__(self, screen, keyboard, sounds):
        """Initialize the app.
        
        Args:
            screen: Pygame Zero screen object
            keyboard: Pygame Zero keyboard object
            sounds: Pygame Zero sounds object
        """
        self.screen = screen
        self.keyboard = keyboard
        self.sounds = sounds
        self.current_screen = None
        self.input_manager = InputManager()
    
    def change_screen(self, new_screen):
        """Change to a new screen.
        
        Args:
            new_screen: Screen object to switch to
        """
        self.current_screen = new_screen
        self.current_screen.on_enter()
    
    def update(self):
        """Update the current screen."""
        if self.current_screen:
            input_state = self.input_manager.capture_input(self.keyboard)
            self.current_screen.update(input_state)
    
    def draw(self):
        """Draw the current screen."""
        if self.current_screen:
            self.current_screen.draw()
