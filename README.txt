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
/new
    Description: Adds a new game to the sqlite database and returns it back as a response
    Accepted methods: GET
    Paramters: None

/reset
    Description: Resets an existing games state to its default state
    Accepted methods: PATCH
    Paramters: 
        id: integer - ID of game in progress

/game_state
    Description: Gets information related to the state of the game
    Accepted methods: GET
    Paramters: 
        id: integer - ID of game in progress

/board_state
    Description: Gets the state of the board for any game
    Accepted methods: GET
    Paramters: 
        id: integer - ID of game in progress

/delete
    Description: Deletes an game from the database
    Accepted methods: DELETE
    Paramters: 
        id: integer - ID of game in progress

/delete_all
    Description: Deletes all games from the database
    Accepted methods: DELETE
    Paramters: None

/move
    Description: Performs a move (if valid) by id, from src to dst
    Accepted methods: PATCH
    Paramters: 
        Json: {"id": integer, "src": integer range(1-3), "dst": integer range(1-3)}

/undo
    Description: Undo perviously performed moves, in order
    Accepted methods: PATCH
    Paramters: 
        id: integer - ID of game in progress

/solved
    Description: Gets a response determining whether the game was solved or not
    Accepted methods: GET
    Paramters: 
        id: integer - ID of game in progress


Examples Directory:
------------------
    Contains my own implementations of the game. 
    This is what I used to drive the implementation details of my RESTful API.
    These files are included only show a small part of the development process.

    local_example.py - Demonstrates a LOCAL implementation of the game 
                       excluding the usage of a REST API
    remove_example.py - Demonstrates a REMOTE implementation of the game
                       including the usage of a REST API 
