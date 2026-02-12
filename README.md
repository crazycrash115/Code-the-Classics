# Cavern - Refactored

Refactored PyGame Zero Bubble Bobble clone with improved architecture.

## How to Run the Game

### Prerequisites
- Python 3.5 or higher
- Pygame Zero 1.2 or higher

### Installation
```bash
# Install Pygame Zero
pip install pgzero

# Or with pip3
pip3 install pgzero
```

### Running
```bash
# From the project root directory
pgzrun main.py

# Or with python3
python3 main.py
```

## How to Run Tests

Currently no automated tests are included. Manual testing checklist:

- [ ] Game starts at menu screen
- [ ] Pressing SPACE starts game
- [ ] Player movement (LEFT/RIGHT arrows) works
- [ ] Player can jump (UP arrow)
- [ ] Player can fire orbs (SPACE)
- [ ] Holding SPACE blows orb further
- [ ] Enemies spawn and move
- [ ] Enemies fire bolts
- [ ] Orbs trap enemies
- [ ] Collecting fruit increases score
- [ ] Pause works (P key) - freezes game but still renders
- [ ] Unpause works (P again)
- [ ] Game over screen appears when lives run out
- [ ] Returning to menu from game over works

## Architecture Summary

### Key Changes from Original

**Task A - Screen Objects (State Pattern)**
- Replaced global state branching with screen objects
- Created `App` class to manage screen transitions
- Implemented `MenuScreen`, `PlayScreen`, and `GameOverScreen`
- Global `update()` and `draw()` are thin delegates to `app.update()` and `app.draw()`
- Game object creation happens inside screen transitions via `change_screen()`

**Task B - Input Snapshot + Edge Detection (Command Pattern)**
- Removed global `space_down` and `space_pressed()` function
- Created `InputState` dataclass with edge-detected inputs
- Created `InputManager` to centralize input capture
- Player no longer accesses `keyboard` directly
- Edge detection handles: menu start, orb firing, jumping, pausing

**Task C - Pause Functionality**
- Added pause toggle with P key in `PlayScreen`
- Paused state freezes game updates but continues rendering
- Pause overlay displays "PAUSED" and "PRESS P TO RESUME"
- Pause only available in PlayScreen (not menu or game over)

### Project Structure
```
cavern-refactored/
├── main.py                 # Entry point, thin Pygame Zero delegates
├── images/                 # Game sprites (copied from original)
├── sounds/                 # Sound effects (copied from original)
├── music/                  # Background music (copied from original)
├── src/
│   ├── app.py             # App class managing screens
│   ├── input.py           # InputState and InputManager
│   ├── game.py            # Core game logic
│   ├── screens/
│   │   ├── menu.py        # MenuScreen
│   │   ├── play.py        # PlayScreen (with pause)
│   │   └── game_over.py   # GameOverScreen
│   └── entities/
│       ├── base.py        # CollideActor, GravityActor
│       ├── player.py      # Player (uses InputState)
│       ├── robot.py       # Enemy
│       ├── orb.py         # Bubble
│       ├── bolt.py        # Projectile
│       ├── pop.py         # Pop animation
│       ├── fruit.py       # Collectibles
│       └── draw_utils.py  # Text/UI drawing
├── README.md              # This file
└── DESIGN.md              # Detailed design documentation
```

## Controls

- **LEFT/RIGHT ARROWS**: Move player
- **UP ARROW**: Jump
- **SPACE**: Fire orb / Start game / Continue from game over
- **HOLD SPACE**: Blow orb further
- **P**: Pause/Unpause (during gameplay only)

## Gameplay

Trap enemies in orbs, then pop them to clear levels. Collect fruit for points and power-ups. Avoid enemy bolts or you'll lose health!

## AI usage

This was fully done with AI, first i used GPT pro and genuinly had the WORST expirence with it, it kept going in loops then not even joking 2 prompts to Claude and it PERFECTLY (minus missing one bug) did it. works more than fine