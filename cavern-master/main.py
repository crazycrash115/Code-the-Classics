from __future__ import annotations

import os
from pathlib import Path

import pygame
from pgzero import loaders

from src.app import App


# ---------------------------------------------------------------------
# Find the REAL project root (do NOT trust __file__ under pgzero runner)
# ---------------------------------------------------------------------
def _find_project_root() -> Path:
    start = Path.cwd().resolve()

    # Walk up a few levels just in case pgzero changed CWD (rare)
    for p in [start, *start.parents]:
        images_dir = p / "images"
        src_dir = p / "src"
        if images_dir.is_dir() and src_dir.is_dir():
            # Strong signal: bg0 exists in images
            if (images_dir / "bg0.png").exists() or any(images_dir.glob("bg0.*")):
                return p
            # Otherwise still accept it as a project root if it looks right
            return p

    # Fallback: use current working directory
    return start


PROJECT_ROOT = _find_project_root()
IMAGES_DIR = PROJECT_ROOT / "images"

# Force process CWD to the project root so any other relative opens work
os.chdir(str(PROJECT_ROOT))

# Init pygame for reliable image loading
if not pygame.get_init():
    pygame.init()

print(f"[main.py] CWD          = {Path.cwd().resolve()}")
print(f"[main.py] PROJECT_ROOT = {PROJECT_ROOT}")
print(f"[main.py] IMAGES_DIR    = {IMAGES_DIR}  exists={IMAGES_DIR.is_dir()}")


# ---------------------------------------------------------------------
# OG-name compatibility mapping (old code names -> your actual filenames)
# ---------------------------------------------------------------------
def _build_image_alias_map() -> dict[str, str]:
    alias: dict[str, str] = {}

    # Player sprites
    alias["player8"] = "still"

    for dir_idx in (0, 1):
        alias[f"player{dir_idx}1"] = f"run{dir_idx}0"
        alias[f"player{dir_idx}2"] = f"run{dir_idx}1"
        alias[f"player{dir_idx}3"] = f"run{dir_idx}2"
        alias[f"player{dir_idx}4"] = f"jump{dir_idx}"

        # Fire/blow frames: map to blow0 / blow1 (we'll try blow01 too)
        for frame in (5, 6, 7, 8):
            alias[f"player{dir_idx}{frame}"] = f"blow{dir_idx}"

    # Fruit (original code used "fruit")
    alias["fruit"] = "fruit00"

    # Some refactors renamed fruit pickup sprite to "bonus" but your assets do NOT
    # contain bonus.png; they contain fruitXX.png. So map "bonus" to fruit00.
    alias["bonus"] = "fruit00"

    # Pop frames pop0 -> pop00 etc
    for i in range(0, 10):
        alias[f"pop{i}"] = f"pop0{i}"

    # Orb frames (keep these as you had them)
    alias["orb00"] = "orb0"
    alias["orb01"] = "orb1"
    alias["orb02"] = "orb2"
    alias["orb03"] = "orb3"
    alias["orb10"] = "orb4"
    alias["orb11"] = "orb5"
    alias["orb12"] = "orb6"
    alias["orb13"] = "orb6"

    return alias


IMAGE_ALIAS = _build_image_alias_map()


# ---------------------------------------------------------------------
# Filesystem image loader (bypasses pgzero validate_root completely)
# ---------------------------------------------------------------------
def _candidate_image_paths(stem: str) -> list[Path]:
    p = Path(stem)
    if p.suffix:
        return [IMAGES_DIR / p.name]

    exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
    out: list[Path] = []

    # exact stem
    for ext in exts:
        out.append(IMAGES_DIR / f"{stem}{ext}")

    # zero padded variants (blow1 -> blow01 / blow001)
    if stem and stem[-1].isdigit():
        base = stem[:-1]
        d = stem[-1]
        for ext in exts:
            out.append(IMAGES_DIR / f"{base}0{d}{ext}")
            out.append(IMAGES_DIR / f"{base}00{d}{ext}")

    return out


def _load_surface_from_project_images(name: str) -> pygame.Surface:
    mapped = IMAGE_ALIAS.get(name, name)

    for path in _candidate_image_paths(mapped):
        if path.exists() and path.is_file():
            surf = pygame.image.load(str(path))
            try:
                return surf.convert_alpha() if surf.get_alpha() is not None else surf.convert()
            except pygame.error:
                return surf

    tried = "\n".join(str(p) for p in _candidate_image_paths(mapped))
    raise KeyError(
        f"No image found like '{name}' (mapped to '{mapped}'). Tried:\n{tried}"
    )


# Patch pgzero loader to ALWAYS use our filesystem loader
_original_images_load = loaders.images.load  # keep (do not delete)
_original_validate_root = loaders.images.validate_root  # keep (do not delete)

def _patched_validate_root(_name: str) -> None:
    # No-op: we do not use pgzero's root validation
    return

def _patched_images_load(name: str, *args, **kwargs):
    return _load_surface_from_project_images(name)

loaders.images.validate_root = _patched_validate_root
loaders.images.load = _patched_images_load


# ---------------------------------------------------------------------
# Run app
# ---------------------------------------------------------------------
app = App()

def update():
    app.update()

def draw():
    app.draw(screen)