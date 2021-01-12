This RESTful API was written and tested on a Windows machine.
The API was written to support a web based implementation of the game Tower of Hanoi.


Usage:
-----
    pip install -e .
    set FLASK_APP=tower
    flask run


Testing:
-------
    Run tests:
        python -m unittest discover tests

    Show coverage:
        coverage run -m unittest discover tests
        coverage report -m


Available Routes:
----------------
route("/new", methods=["GET"]) - Adds a new game to the sqlite database and returns it back as a response.
    expected data: None

route("/reset", methods=["PATCH"]) - Resets an existing games state to its default state.
    expected data: Param id: Integer

route("/game_state", methods=["GET"]) - Gets information related to the state of the game.
    expected data: Param id: Integer

route("/board_state", methods=["GET"]) - Gets the state of the board for any game.
    expected data: Param id: Integer

route("/delete", methods=["DELETE"]) - Deletes an game from the database.
    expected data: Param id: Integer

route("/delete_all", methods=["DELETE"]) - Deletes all games from the database.
    expected data: None

route("/move", methods=["PATCH"]) - Performs a move (if valid) by id, from src to dst.
    expected data: Json {"id": Integer, "src": Integer Range(1-3), "dst": Integer Range(1-3)}

route("/undo", methods=["PATCH"]) - Undo perviously performed moves, in order.
    expected data: Param id: Integer

route("/solved", methods=["GET"]) - Gets a response determining whether the game was solved or not.
    expected data: Param id: Integer


Examples Directory:
------------------
    Contains my own implementations of the game. 
    This is what I used to drive the implementation details of my RESTful API.
    These files are included only show a small part of the development process.

    local_example.py - Demonstrates a LOCAL implementation of the game 
                       excluding the usage of a REST API
    local_example.py - Demonstrates a REMOTE implementation of the game
                       including the usage of a REST API 

list anything additional beyond the requirements: not yet done
