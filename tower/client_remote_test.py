import requests
import json


# delete one
# delete all
# reset by id


def new_game():
    game = requests.get("http://127.0.0.1:5000/new").json()
    return game

def show_game_state(_id):
    result = requests.get("http://127.0.0.1:5000/state", params={"id": _id})
    board = result.json()["board"]
    for row in board:
        print("[{:<6s}{:<6s}{:<4s}]".format(str(row[0]), str(row[1]), str(row[2])))
    print("")

def move(_id, src, dst):
    move = {"id": _id, "src": src, "dst": dst}
    result = requests.patch("http://127.0.0.1:5000/move", json=move)
    return result

def undo(_id):
    result = requests.patch("http://127.0.0.1:5000/undo", params={"id": _id})
    return result

def solved(_id):
    result = requests.get("http://127.0.0.1:5000/solved", params={"id": _id})
    return result.json()

def delete_one(_id):
    result = requests.get("http://127.0.0.1:5000/delete", params={"id": _id})
    return result

def delete_all():
    result = requests.get("http://127.0.0.1:5000/delete_all")
    return result

game = new_game()
game_id = game["id"]
board = game["board"]
show_game_state(game_id)

# solved = false
solved_result = solved(game_id)
print("game solved: %s" % solved_result["solved"])


move(game_id, 1, 2)
show_game_state(game_id)
# invalid move - no change to board
move(game_id, 1, 2)
show_game_state(game_id)

move(game_id, 1, 3)
show_game_state(game_id)
# invalid move - no change to board
move(game_id, 1, 3)
show_game_state(game_id)

move(game_id, 2, 3)
move(game_id, 1, 2)
move(game_id, 3, 1)
move(game_id, 3, 2)
move(game_id, 1, 2)
move(game_id, 1, 3)
move(game_id, 2, 3)
move(game_id, 2, 1)
move(game_id, 3, 1)
move(game_id, 2, 3)
move(game_id, 1, 2)

# solved = false
move(game_id, 1, 3)
solved_result = solved(game_id)
print("game solved: %s" % solved_result["solved"])
show_game_state(game_id)

# solved = true
move(game_id, 2, 3)
solved_result = solved(game_id)
print("game solved: %s" % solved_result["solved"])
show_game_state(game_id)

# undo test
# solved = false
undo(game_id)
solved_result = solved(game_id)
print("game solved: %s" % solved_result["solved"])
show_game_state(game_id)

undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)
show_game_state(game_id)
undo(game_id)

# invalid undo
undo(game_id)
show_game_state(game_id)
solved_result = solved(game_id)
print("game solved: %s" % solved_result["solved"])
