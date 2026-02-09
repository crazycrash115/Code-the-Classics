import os
import sys
import pgzero

# Ensure assets load from the project root (where images/ and sounds/ live)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_ROOT)

from app import App
from game import WIDTH as _WIDTH, HEIGHT as _HEIGHT, TITLE as _TITLE

WIDTH = _WIDTH
HEIGHT = _HEIGHT
TITLE = _TITLE

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
    app.update()

def draw():
    app.draw()