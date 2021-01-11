move_count = 0
board = None


def start_game():
    data = [[1, None, None], 
            [2, None, None], 
            [3, None, None], 
            [4, None, None]]
    return data


def show_game_state(board):
    for row in board:
        print("[{:<6s}{:<6s}{:<4s}]".format(str(row[0]), str(row[1]), str(row[2])))
    print("")

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
        result = board[dst_pos[1] + 1][dst_pos[0]] > board[src_pos[1]][src_pos[0]]
        return result
    return True


def move(board, src_col_index, dst_col_index):
    src_pos = get_src_pos(board, src_col_index - 1)
    dst_pos = get_dst_pos(board, dst_col_index - 1)
    if valid_move(board, src_pos, dst_pos):
        global move_count
        move_count += 1
        value = board[src_pos[1]][src_pos[0]]
        board[dst_pos[1]][dst_pos[0]] = value
        board[src_pos[1]][src_pos[0]] = None
        print("valid move - move count: %s\nvalue: %s, from col: %s, to col: %s" %
                (move_count, value, src_col_index, dst_col_index))
        show_game_state(board)
    else:
        value = board[src_pos[1]][src_pos[0]]
        print("invalid move - move count: %s\nvalue: %s, from col: %s, to col: %s" %
                (move_count, value, src_col_index, dst_col_index))
        show_game_state(board)


board = start_game()
show_game_state(board)
move(board, 1, 2)
move(board, 1, 2)
move(board, 1, 3)
move(board, 1, 3)
move(board, 2, 3)
move(board, 1, 2)
move(board, 3, 1)
move(board, 3, 2)
move(board, 1, 2)
move(board, 1, 3)
move(board, 2, 3)
move(board, 2, 1)
move(board, 3, 1)
move(board, 2, 3)
move(board, 1, 2)
move(board, 1, 3)
move(board, 2, 3)
