from input import InputManager
from screens.menu import MenuScreen

class App:
    def __init__(self):
        self.input_manager = InputManager()
        self.screen = MenuScreen(self)

    def change_screen(self, new_screen):
        # Single method for screen transitions (Task A)
        self.screen = new_screen

    def update(self):
        input_state = self.input_manager.build()
        self.screen.update(input_state)

    def draw(self):
        self.screen.draw()
