import os
import unittest
 
from tower import game
from tower import create_app, init_db
 
 
class TestGame(unittest.TestCase):


    def setUp(self):
        self.default_game = data = {"id": 1,
                                    "solved": False,
                                    "move_buffer": {"src": [], "dst": []},
                                    "move_buffer_size": 0,
                                    "total_move_count": 0,
                                    "valid_move_count": 0,
                                    "board": [[1, None, None], [2, None, None], [3, None, None], [4, None, None]]}
        self.solution_third = [[None, None, 1], [None, None, 2], [None, None, 3], [None, None, 4]]
        self.solution_second = [[None, 1, None], [None, 2, None], [None, 3, None], [None, 4, None]]

    def test_valid_data_true(self):
        result = game.valid_data(1, 1, 1)
        self.assertTrue(result)

    def test_valid_data_false(self):
        result = game.valid_data(None, 1, 1)
        self.assertFalse(result)

        result = game.valid_data(1, 4, 1)
        self.assertFalse(result)

        result = game.valid_data(1, 2, 0)
        self.assertFalse(result)

    def test_get_default_board_state(self):
        result = game.get_default_board_state()
        board = {"id": None,
                "solved": False,
                "move_buffer": {"src": [], "dst": []},
                "move_buffer_size": 0,
                "total_move_count": 0,
                "valid_move_count": 0,
                "board": [[1, None, None], [2, None, None], [3, None, None], [4, None, None]]}

        self.assertEqual(board, result)

        result = game.get_default_board_state(14)
        board["id"] = 14
        self.assertEqual(board, result)

    def test_check_solved_false(self):
        board = {"board": self.solution_third}
        result = game.check_solved(board, 1)
        self.assertFalse(result)

        board = {"board": self.solution_second}
        result = game.check_solved(board, 2)
        self.assertFalse(result)

        board = {"board": self.default_game["board"]}
        result = game.check_solved(board, 2)
        self.assertFalse(result)

        board = {"board": self.default_game["board"]}
        result = game.check_solved(board, 1)
        self.assertFalse(result)

    def test_check_solved_true(self):
        board = {"board": self.solution_third}
        result = game.check_solved(board, 2)
        self.assertTrue(result)

        board = {"board": self.solution_second}
        result = game.check_solved(board, 1)
        self.assertTrue(result)

    def test_get_src_pos(self):
        result = game.get_src_pos(self.default_game["board"], 0)
        self.assertEqual((0, 0), result)

        result = game.get_src_pos(self.default_game["board"], 1)
        self.assertEqual((None, None), result)

    def test_get_dst_pos(self):
        result = game.get_dst_pos(self.default_game["board"], 0)
        self.assertEqual((0, None), result)

        result = game.get_dst_pos(self.default_game["board"], 1)
        self.assertEqual((1, 3), result)

    def test_valid_move_false(self):
        result = game.valid_move(self.default_game["board"], (1, None), (1, None))
        self.assertFalse(result)

        result = game.valid_move(self.default_game["board"], (1, 1), (1, 1))
        self.assertFalse(result)

    def test_valid_move_true(self):
        result = game.valid_move(self.default_game["board"], (0, 0), (1, 3))
        self.assertTrue(result)

        result = game.valid_move(self.solution_third, (0, 2), (1, 3))
        self.assertTrue(result)

        result = game.valid_move(self.solution_second, (0, 1), (2, 3))
        self.assertTrue(result)

    def test_perform_move_true(self):
        result = game.perform_move(self.default_game, 1, 3, 1)
        self.assertTrue(result)
        result = game.perform_move(self.default_game, 1, 2, 1)
        self.assertTrue(result)
        self.assertEqual(self.default_game["move_buffer_size"], 2)
        self.assertEqual(self.default_game["total_move_count"], 2)
        self.assertEqual(self.default_game["valid_move_count"], 2)

    def test_perform_move_false(self):
        result = game.perform_move(self.default_game, 2, 3, 1)
        self.assertFalse(result)
        result = game.perform_move(self.default_game, 3, 2, 1)
        self.assertFalse(result)
        result = game.perform_move(self.default_game, 1, 3, 1)
        result = game.perform_move(self.default_game, 1, 3, 1)
        self.assertFalse(result)
        self.assertEqual(self.default_game["move_buffer_size"], 1)
        self.assertEqual(self.default_game["total_move_count"], 1)
        self.assertEqual(self.default_game["valid_move_count"], 1)


if __name__ == "__main__":
    unittest.main()
