"""
Cavern - Refactored PyGame Zero Bubble Bobble Clone
Main entry point that delegates to App (Task A requirement)
"""
import pygame
import pgzero
import pgzrun
import sys

# Check Python version
if sys.version_info < (3,5):
    print("This game requires at least version 3.5 of Python")
    sys.exit()

# Check Pygame Zero version
pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split('.')]
if pgzero_version < [1,2]:
    print(f"This game requires at least version 1.2 of Pygame Zero. You have {pgzero.__version__}")
    sys.exit()

# Game constants
WIDTH = 800
HEIGHT = 480
TITLE = "Cavern"

# Import app after constants are set
from src.app import App
from src.screens.menu import MenuScreen

# Global app instance
app = None

def init_app():
    """Initialize the app with required Pygame Zero objects."""
    global app
    app = App(screen, keyboard, sounds)
    app.change_screen(MenuScreen(app))

# Pygame Zero callbacks - THIN DELEGATES (Task A requirement)
def update():
    """Global update - thin delegate to app.update()"""
    if app is None:
        init_app()
    app.update()

def draw():
    """Global draw - thin delegate to app.draw()"""
    if app:
        app.draw()

# Set up sound system
try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)
    music.play("theme")
    music.set_volume(0.3)
except:
    pass

pgzrun.go()
