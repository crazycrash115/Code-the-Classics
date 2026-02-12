"""Input handling with edge detection for Cavern game."""
from dataclasses import dataclass


@dataclass
class InputState:
    """Snapshot of input state for a single frame."""
    left: bool = False
    right: bool = False
    jump_pressed: bool = False  # Edge detection - UP arrow
    fire_pressed: bool = False  # Edge detection - SPACE key
    fire_held: bool = False      # Level detection - SPACE held
    pause_pressed: bool = False  # Edge detection - P key
    menu_start: bool = False     # Edge detection - SPACE in menu


class InputManager:
    """Manages input state and edge detection."""
    
    def __init__(self):
        self._space_was_down = False
        self._up_was_down = False
        self._p_was_down = False
    
    def capture_input(self, keyboard) -> InputState:
        """Capture current input state with edge detection.
        
        Args:
            keyboard: Pygame Zero keyboard object
            
        Returns:
            InputState object with current frame's input
        """
        # Detect space bar edge (just pressed)
        space_pressed = keyboard.space and not self._space_was_down
        self._space_was_down = keyboard.space
        
        # Detect UP arrow edge (just pressed)
        up_pressed = keyboard.up and not self._up_was_down
        self._up_was_down = keyboard.up
        
        # Detect P key edge (just pressed)
        p_pressed = keyboard.p and not self._p_was_down
        self._p_was_down = keyboard.p
        
        return InputState(
            left=keyboard.left,
            right=keyboard.right,
            jump_pressed=up_pressed,          # UP arrow for jumping
            fire_pressed=space_pressed,       # SPACE for firing orbs
            fire_held=keyboard.space,         # SPACE held to blow further
            pause_pressed=p_pressed,
            menu_start=space_pressed          # SPACE also starts game from menu
        )
