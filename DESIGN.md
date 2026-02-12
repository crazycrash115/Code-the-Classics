# Design Document

## Screens Architecture

### Overview
The refactored codebase uses the **State Pattern** to manage different game states (Menu, Play, Game Over). Instead of global branching on a state enum, each state is encapsulated in its own screen class.

### App Class
The `App` class serves as the screen manager:
- **Responsibilities**: Hold current screen, manage screen transitions, provide access to Pygame Zero objects
- **Key Method**: `change_screen(new_screen)` - Single point of control for all screen transitions
- **State Storage**: Stores reference to current screen object

### Screen Classes
All screens implement a common interface:
- `on_enter()` - Called when transitioning to this screen
- `update(input_state)` - Called every frame with current input
- `draw()` - Renders the screen

**MenuScreen**:
- Creates a background Game object (without player) for visual effects
- Transitions to PlayScreen when SPACE is pressed
- Renders title screen and animated "Press SPACE" prompt

**PlayScreen**:
- Creates new Game with Player on entry
- Manages pause state (Task C)
- Transitions to GameOverScreen when player runs out of lives
- Renders game, status bar, and pause overlay (if paused)

**GameOverScreen**:
- Receives Game object to display final score/state
- Transitions back to MenuScreen when SPACE is pressed
- Renders final game state with "Game Over" overlay

### Key Design Decisions

1. **Game Creation in Screens**: The `Game` object is created inside screen transitions, not in global update(). This ensures clean state management and follows Task A requirements.

2. **Thin Delegates**: Global `update()` and `draw()` functions are minimal wrappers that call `app.update()` and `app.draw()`. This satisfies Pygame Zero's callback requirements while keeping logic in the App.

3. **Single Transition Method**: All screen changes use `app.change_screen()`, making state flow easy to trace and debug.

## Input Design

### Problem with Original
The original code had:
- Global `space_down` variable tracking space bar state
- `space_pressed()` function with side effects
- Direct `keyboard.*` access scattered throughout Player class
- No centralized input handling

### Solution: Input Snapshot Pattern

**InputState** (dataclass):
```python
@dataclass
class InputState:
    left: bool           # Level: is left pressed?
    right: bool          # Level: is right pressed?
    jump_pressed: bool   # Edge: just pressed this frame?
    fire_pressed: bool   # Edge: just pressed this frame?
    fire_held: bool      # Level: is space held?
    pause_pressed: bool  # Edge: just pressed this frame?
```

**InputManager**:
- Captures input once per frame
- Performs edge detection by comparing current frame to previous
- Returns immutable InputState snapshot

**Benefits**:
- No global state
- Input captured centrally (easier to test/modify)
- Player logic is pure - takes InputState, doesn't access keyboard
- Clear separation: level detection (currently pressed) vs edge detection (just pressed)

### Edge Detection Implementation
```python
# In InputManager.capture_input():
space_pressed = keyboard.space and not self._space_was_down
self._space_was_down = keyboard.space
```

Tracks previous frame's state to detect the rising edge (transition from not-pressed to pressed).

### Integration
1. App captures input each frame: `input_state = self.input_manager.capture_input(self.keyboard)`
2. Passes to current screen: `self.current_screen.update(input_state)`
3. Screen passes to entities: `self.game.player.update(input_state, game)`
4. Player uses input_state fields instead of `keyboard.*` directly

## Pause Implementation

### Requirements
- Toggle pause with P key
- Freeze game simulation (no movement/spawns/timers)
- Continue rendering current state
- Display "PAUSED" overlay

### Design

**State Management**:
- `PlayScreen.paused` boolean tracks pause state
- Input Manager detects P key edges via `pause_pressed`

**Update Logic**:
```python
def update(self, input_state):
    if input_state.pause_pressed:
        self.paused = not self.paused
    
    if not self.paused:
        self.game.update(input_state)  # Only update when not paused
```

**Rendering**:
```python
def draw(self):
    self.game.draw(self.app.screen)  # Always draw game state
    draw_status(...)  # Always draw UI
    
    if self.paused:
        draw_text("PAUSED", ...)  # Overlay when paused
```

### Why This Works
- Game state is frozen by skipping `game.update()` call
- Rendering continues normally, showing frozen state
- Pause toggle is separate from game logic (belongs to screen)
- No changes needed to Game class itself

### Scope Limitation
Pause is only available in `PlayScreen`. Menu and GameOver screens don't implement pause handling, as it's not meaningful for those states.

## Summary of Patterns Used

| Pattern | Application | Benefit |
|---------|-------------|---------|
| **State** | Screen objects | Eliminates global state branching |
| **Command** | InputState snapshots | Decouples input from game logic |
| **Manager** | App coordinates screens | Single responsibility for transitions |
| **Data Transfer Object** | InputState dataclass | Immutable input snapshot |

This architecture makes the code more testable, maintainable, and easier to extend with new screens or input modes.
