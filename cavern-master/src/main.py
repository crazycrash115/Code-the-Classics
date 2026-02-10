import os
import sys
from pathlib import Path
import pgzero.loaders

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # cavern-master/
pgzero.loaders.set_root(str(PROJECT_ROOT))

import pgzero
import pgzrun
# NOTE:
# Pygame Zero injects `screen`, `keyboard`, `sounds`, etc. into this module at runtime.
# Importing `screen` directly can fail on newer pgzero versions, so we don't import it.

# Ensure Pygame Zero loads assets from the project root (where images/ and sounds/ live)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(PROJECT_ROOT)

from src.app import App
from src.game import WIDTH as _WIDTH, HEIGHT as _HEIGHT, TITLE as _TITLE

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
    app.update()

def draw():
    # `screen` is provided by Pygame Zero at runtime.
    app.draw(screen)

if __name__ == "__main__":
    # Allows running `python src/main.py` too, but recommended is:
    #   py -3.11 -m pgzero src/main.py
    pgzrun.go()