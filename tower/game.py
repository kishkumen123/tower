from flask import Blueprint, request, Response, g, current_app
import sqlite3
import json

bp = Blueprint("game", __name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config["DATABASE"])
    return db

def get_src_pos(board, src_col_index):
    for i, row in enumerate(board):
        src_value = row[src_col_index]
        if src_value is not None:
            return src_col_index, i
    return None, None

def get_dst_pos(board, dst_col_index):
    insertion_row = None
    for i, row in enumerate(board):
        dst_value = row[dst_col_index]
        if dst_value is None:
            insertion_row = i
    return dst_col_index, insertion_row

def valid_move(board, src_pos, dst_pos):
    if None in src_pos or None in dst_pos:
        return False
    if dst_pos[1] < 3:
        dst_value = board[dst_pos[1] + 1][dst_pos[0]] 
        src_value = board[src_pos[1]][src_pos[0]]
        if dst_value is None or src_value is None:
            return False
        return dst_value > src_value
    return True

def perform_move(data, src_col_index, dst_col_index, increment):
    src_pos = get_src_pos(data["board"], src_col_index - 1)
    dst_pos = get_dst_pos(data["board"], dst_col_index - 1)
    if valid_move(data["board"], src_pos, dst_pos):
        value = data["board"][src_pos[1]][src_pos[0]]
        data["board"][dst_pos[1]][dst_pos[0]] = value
        data["board"][src_pos[1]][src_pos[0]] = None
        data["move_buffer_size"] += increment
        data["total_move_count"] += 1
        if increment > 0:
            data["valid_move_count"] += 1
        return True
    return False

def check_solved(data, position):
    for i, row in enumerate(data["board"]):
        if row[position] != (i + 1):
            return False

    return True

def get_selection(cursor, _id):
    selection = {"error": None, "selection": None}
    try:
        cursor.execute("select * from game where id == ?",str(_id))
    except sqlite3.OperationalError as e:
        selection["error"] = e.args[0]
        return selection

    selection["selection"] = cursor.fetchone()
    if selection["selection"] is None:
        selection["error"] = ("id: %s does not exist" % _id)
        return selection
    return selection

def app_response(res, status):
    return Response(response=json.dumps(res), status=status, content_type="application/json")

def get_default_board_state(_id=None):
    data = {"id": _id,
            "solved": False,
            "move_buffer": {"src": [], "dst": []},
            "move_buffer_size": 0,
            "total_move_count": 0,
            "valid_move_count": 0,
            "board": [[1, None, None], [2, None, None], [3, None, None], [4, None, None]]}

    return data

def undo(selection_data):
    src = selection_data["move_buffer"]["dst"][-1]
    dst = selection_data["move_buffer"]["src"][-1]
    result = perform_move(selection_data, src, dst, -1)
    selection_data["move_buffer"]["src"].pop()
    selection_data["move_buffer"]["dst"].pop()

def valid_data(_id, src, dst):
    if _id is None or src is None or dst is None:
        return False

    if src > 3 or src < 1 or dst > 3 or dst < 1:
        return False

    return True

# creates a new game
@bp.route("/new", methods=["GET"])
def game_new():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("create table if not exists game (id integer primary key autoincrement, data json)")
    default_board_state = get_default_board_state()
    try:
        cursor.execute("insert into game(data) values (?)", (json.dumps(default_board_state),))
    except sqlite3.OperationalError as e:
        res = {"error": e.args[0]}
        return app_response(res, 400)

    default_board_state["id"] = cursor.lastrowid
    db.commit()
    cursor.close()
    return app_response(default_board_state, 200)


# resets an existing game
@bp.route("/reset", methods=["PATCH"])
def game_reset():
    db = get_db()
    cursor = db.cursor()

    _id = request.args.get("id", default=None, type=int)
    if _id is None:
        res = {"error": "must have parameter id with integer value"}
        return app_response(res, 400)

    result = get_selection(cursor, _id)
    if result["error"] is not None:
        res = {"error": result["error"]}
        return app_response(res, 400)

    selection = result["selection"]
    selection_data = json.loads(selection[1])
    selection_data = get_default_board_state(selection[0])

    cursor.execute("update game set data = ? where id == ?", (json.dumps(selection_data), str(_id)))
    db.commit()
    cursor.close()
    return app_response(selection_data, 200)


# returns the state of an existing game
@bp.route("/game_state", methods=["GET"])
def game_state():
    db = get_db()
    cursor = db.cursor()
    _id = request.args.get("id", default=None, type=int)

    if _id is None:
        res = {"error": "must have parameter id with integer value"}
        return app_response(res, 400)

    result = get_selection(cursor, _id)
    if result["error"] is not None:
        res = {"error": result["error"]}
        return app_response(res, 400)

    selection = result["selection"]
    selection_data = json.loads(selection[1])
    del selection_data["id"]

    cursor.close()
    return app_response(selection_data, 200)

# returns the state of an existing game
@bp.route("/board_state", methods=["GET"])
def game_board_state():
    db = get_db()
    cursor = db.cursor()
    _id = request.args.get("id", default=None, type=int)

    if _id is None:
        res = {"error": "must have parameter id with integer value"}
        return app_response(res, 400)

    result = get_selection(cursor, _id)
    if result["error"] is not None:
        res = {"error": result["error"]}
        return app_response(res, 400)

    selection = result["selection"]
    selection_data = json.loads(selection[1])
    result = {"board": selection_data["board"]}

    cursor.close()
    return app_response(result, 200)

# deletes an existing game
@bp.route("/delete", methods=["DELETE"])
def game_delete():
    db = get_db()
    cursor = db.cursor()
    _id = request.args.get("id", default=None, type=int)
    if _id is None:
        res = {"error": "must have parameter id with integer value"}
        return app_response(res, 400)

    try:
        cursor.execute("delete from game where id == ?", str(_id))
    except sqlite3.OperationalError as e:
        res = {"error": e.args[0]}
        return app_response(res, 400)

    db.commit()
    cursor.close()
    return app_response({}, 200)


# deletes all games
@bp.route("/delete_all", methods=["DELETE"])
def game_delete_all():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("delete from game")
        cursor.execute("drop table if exists game")
        cursor.execute("create table if not exists game (id integer primary key autoincrement, data json)")
    except sqlite3.OperationalError as e:
        res = {"error": e.args[0]}
        return app_response(res, 400)

    db.commit()
    cursor.close()
    return app_response({}, 200)


# performs a valid move
@bp.route("/move", methods=["PATCH"])
def game_move():
    db = get_db()
    cursor = db.cursor()

    if not request.is_json:
        res = {"error": "Expecting json body {'id': int, 'src': int, 'dst': int}"}
        return app_response(res, 400)

    _id = request.json.get("id")
    src = request.json.get("src")
    dst = request.json.get("dst")

    if not valid_data(_id, src, dst):
        res = {"error": "Expecting json body {'id': int, 'src': int, 'dst': int} where src and dst are in range of (1 - 3)"}
        return app_response(res, 400)

    result = get_selection(cursor, _id)
    if result["error"] is not None:
        res = {"error": result["error"]}
        return app_response(res, 400)

    selection = result["selection"]
    selection_data = json.loads(selection[1])
    selection_data["id"] = selection[0]
    selection_data["move_buffer"]["src"].append(src)
    selection_data["move_buffer"]["dst"].append(dst)

    result = perform_move(selection_data, src, dst, 1)
    if not result:
        cursor.close()
        res = {"error": "invalid move", "src": src, "dst": dst}
        return app_response(res, 400)

    result = check_solved(selection_data, 1) or check_solved(selection_data, 2)
    if result != selection_data["solved"]:
        selection_data["solved"] = result

    cursor.execute("update game set data = ? where id == ?", (json.dumps(selection_data), str(_id)))
    db.commit()
    cursor.close()
    return app_response(selection_data, 200)


# undos a move stored in the move_buffer
@bp.route("/undo", methods=["PATCH"])
def game_undo():
    db = get_db()
    cursor = db.cursor()

    _id = request.args.get("id", default=None, type=int)
    if _id is None:
        res = {"error": "must have parameter id with integer value"}
        return app_response(res, 400)

    result = get_selection(cursor, _id)
    if result["error"] is not None:
        res = {"error": result["error"]}
        return app_response(res, 400)

    selection = result["selection"]
    selection_data = json.loads(selection[1])
    if selection_data["move_buffer_size"] < 1:
        res = {"error": "move buffer empty: cannot undo"}
        return app_response(res, 400)

    selection_data["id"] = selection[0]
    undo(selection_data)

    cursor.execute("update game set data = ? where id == ?", (json.dumps(selection_data), str(_id)))
    db.commit()
    cursor.close()
    return app_response(selection_data, 200)


# checks if an existing game is solved
@bp.route("/solved", methods=["GET"])
def game_solved():
    db = get_db()
    cursor = db.cursor()

    _id = request.args.get("id", default=None, type=int)
    if _id is None:
        res = {"error": "must have parameter id with integer value"}
        return app_response(res, 400)

    result = get_selection(cursor, _id)
    if result["error"] is not None:
        res = {"error": result["error"]}
        return app_response(res, 400)

    selection = result["selection"]
    selection_data = json.loads(selection[1])
    result = check_solved(selection_data, 1) or check_solved(selection_data, 2)
    if result != selection_data["solved"]:
        selection_data["solved"] = result
        cursor.execute("update game set data = ? where id == ?", (json.dumps(selection_data), str(_id)))
    db.commit()
    cursor.close()
    return app_response({"solved": result}, 200)
