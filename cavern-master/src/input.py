from dataclasses import dataclass
from pgzero.builtins import keyboard

@dataclass
class InputState:
    left: bool
    right: bool
    up: bool

    jump_pressed: bool   # edge - used for menu start (SPACE)
    fire_pressed: bool   # edge - orb creation (SPACE press)
    fire_held: bool      # level - blow further (SPACE held)

    pause_pressed: bool  # edge - toggle pause (P)

class InputManager:
    def __init__(self):
        self._prev_space = False
        self._prev_p = False

    def build(self) -> InputState:
        space_now = bool(keyboard.space)
        p_now = bool(keyboard.p)

        space_edge = space_now and not self._prev_space
        p_edge = p_now and not self._prev_p

        state = InputState(
            left=bool(keyboard.left),
            right=bool(keyboard.right),
            up=bool(keyboard.up),

            jump_pressed=space_edge,
            fire_pressed=space_edge,
            fire_held=space_now,

            pause_pressed=p_edge,
        )

        self._prev_space = space_now
        self._prev_p = p_now
        return state
