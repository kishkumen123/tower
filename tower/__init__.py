from flask import Flask
from tower.game import game_blueprint

app = Flask(__name__)
app.register_blueprint(game_blueprint)

