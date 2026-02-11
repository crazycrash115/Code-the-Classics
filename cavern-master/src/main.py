import os
import sys
from pathlib import Path
import pgzero.loaders

# ---------------------------------------------------------------------------
# Asset name compatibility layer
#
# The original Cavern code expects player sprites named like 'player15'.
# Your repo's image files are named like 'run10', 'jump1', 'blow1', etc.
#
# Instead of renaming files, we patch pgzero's image loader so
# requests for 'player..' sprites fall back to these assets.
# ---------------------------------------------------------------------------

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


def _install_image_aliases() -> None:
    """Map original sprite names to the actual asset filenames.

    This keeps your game logic intact (it can keep setting Actor.image to
    'player..' sprites), while allowing the repo to use the provided assets.
    """

    # Import here so the root is already set up.
    from pgzero import loaders

    alias: dict[str, str] = {}

    # Death / fallback
    alias["player8"] = "still"

    # Movement + blowing frames
    for dir_idx in (0, 1):
        # Running: only frames 1..3 are used (see Player.update in game.py)
        alias[f"player{dir_idx}1"] = f"run{dir_idx}0"
        alias[f"player{dir_idx}2"] = f"run{dir_idx}1"
        alias[f"player{dir_idx}3"] = f"run{dir_idx}2"

        # Jumping
        alias[f"player{dir_idx}4"] = f"jump{dir_idx}"

        # Blowing (original expects 5..8)
        for frame in (5, 6, 7, 8):
            alias[f"player{dir_idx}{frame}"] = f"blow{dir_idx}"

    original_load = loaders.images.load

    def patched_load(name: str, *args, **kwargs):
        try:
            return original_load(name, *args, **kwargs)
        except KeyError:
            mapped = alias.get(name)
            if mapped is None:
                raise
            return original_load(mapped, *args, **kwargs)

    loaders.images.load = patched_load


_install_image_aliases()

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
