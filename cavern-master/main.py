from src.app import App
from src.game import WIDTH, HEIGHT, TITLE

app = App()

def update():
    app.update()

def draw():
    app.draw(screen)