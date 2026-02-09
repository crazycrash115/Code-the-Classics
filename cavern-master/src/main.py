import sys
import pgzero
import pgzrun

from app import App
from game import WIDTH as _WIDTH, HEIGHT as _HEIGHT, TITLE as _TITLE

# Pygame Zero reads these constants from the main module
WIDTH = _WIDTH
HEIGHT = _HEIGHT
TITLE = _TITLE

# Version checks preserved (from original)
if sys.version_info < (3, 5):
    print("This game requires at least version 3.5 of Python. Please download it from www.python.org")
    sys.exit()

pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split(".")]
if pgzero_version < [1, 2]:
    print(
        "This game requires at least version 1.2 of Pygame Zero. You have version {0}. "
        "Please upgrade using the command 'pip3 install --upgrade pgzero'".format(pgzero.__version__)
    )
    sys.exit()

app = App()

def update():
    # Thin delegate required by Task A
    app.update()

def draw():
    # Thin delegate required by Task A
    app.draw()

if __name__ == "__main__":
    pgzrun.go()
