import sqlite3
from flask import Flask, g
from . import game


class Config:
    DATABASE = "database.db"
    TESTING = False


def init_db(database):
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(database, isolation_level=None)
    return db


def create_app(config=None):
    app = Flask(__name__)
    if config is None:
        app.config.from_object(Config)
    else:
        app.config["DATABASE"] = config["DATABASE"]
        app.config["TESTING"] = config["TESTING"]
    app.register_blueprint(game.bp)

    with app.app_context():
        db = init_db(app.config["DATABASE"])
        cursor = db.cursor()
        cursor.execute(
            "create table if not exists game (id integer primary key autoincrement, data json)"
        )

    return app
