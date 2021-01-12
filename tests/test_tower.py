import sys
import os
import unittest

from tower import create_app, init_db


TEST_DB = "test_database.db"


class TestGame(unittest.TestCase):
    def setUp(self):
        app = create_app({"TESTING": True, "DATABASE": TEST_DB})
        self.app = app.test_client()
        self.default_game = data = {
            "id": 1,
            "solved": False,
            "move_buffer": {"src": [], "dst": []},
            "move_buffer_size": 0,
            "total_move_count": 0,
            "valid_move_count": 0,
            "board": [
                [1, None, None],
                [2, None, None],
                [3, None, None],
                [4, None, None],
            ],
        }
        self.solution_third = [
            [None, None, 1],
            [None, None, 2],
            [None, None, 3],
            [None, None, 4],
        ]
        self.solution_second = [
            [None, 1, None],
            [None, 2, None],
            [None, 3, None],
            [None, 4, None],
        ]

        with app.app_context():
            db = init_db(TEST_DB)
            cursor = db.cursor()
            cursor.execute("delete from game")
            cursor.execute("drop table if exists game")
            cursor.execute(
                "create table if not exists game (id integer primary key autoincrement, data json)"
            )

    def tearDown(self):
        os.remove(TEST_DB)

    def test_new_game_default_values(self):
        expected = self.default_game
        response = self.app.get("http://127.0.0.1:5000/new")
        self.assertEqual(self.default_game, response.json)

        response = self.app.get("http://127.0.0.1:5000/new")
        expected["id"] += 1
        self.assertEqual(self.default_game, response.json)

        response = self.app.get("http://127.0.0.1:5000/new")
        expected["id"] += 1
        self.assertEqual(self.default_game, response.json)

        response = self.app.get("http://127.0.0.1:5000/new")
        expected["id"] += 1
        self.assertEqual(self.default_game, response.json)

    def test_game_state(self):
        response = self.app.get("http://127.0.0.1:5000/new")
        response = self.app.get("http://127.0.0.1:5000/game_state?id=1")

        expected = self.default_game
        del expected["id"]
        self.assertEqual(expected, response.json)

    def test_board_state(self):
        response = self.app.get("http://127.0.0.1:5000/new")
        response = self.app.get("http://127.0.0.1:5000/board_state?id=1")

        expected = {"board": self.default_game["board"]}
        self.assertEqual(expected, response.json)

        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )

        response = self.app.get("http://127.0.0.1:5000/board_state?id=1")
        expected = {
            "board": [
                [None, None, None],
                [None, None, None],
                [3, None, 1],
                [4, None, 2],
            ]
        }
        self.assertEqual(expected, response.json)

    def test_delete_game(self):
        response = self.app.get("http://127.0.0.1:5000/new")
        response = self.app.get("http://127.0.0.1:5000/game_state?id=1")
        expected = self.default_game
        del expected["id"]
        self.assertEqual(expected, response.json)

        response = self.app.delete("http://127.0.0.1:5000/delete?id=1")
        response = self.app.get("http://127.0.0.1:5000/game_state?id=1")
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response.json)

    def test_delete_game_all(self):
        response = self.app.get("http://127.0.0.1:5000/new")
        response = self.app.get("http://127.0.0.1:5000/new")
        response = self.app.get("http://127.0.0.1:5000/new")
        response = self.app.get("http://127.0.0.1:5000/new")
        response1 = self.app.get("http://127.0.0.1:5000/game_state?id=1")
        response2 = self.app.get("http://127.0.0.1:5000/game_state?id=2")
        response3 = self.app.get("http://127.0.0.1:5000/game_state?id=3")
        response4 = self.app.get("http://127.0.0.1:5000/game_state?id=4")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response4.status_code, 200)
        response = self.app.delete("http://127.0.0.1:5000/delete_all")

        response1 = self.app.get("http://127.0.0.1:5000/game_state?id=1")
        response2 = self.app.get("http://127.0.0.1:5000/game_state?id=2")
        response3 = self.app.get("http://127.0.0.1:5000/game_state?id=3")
        response4 = self.app.get("http://127.0.0.1:5000/game_state?id=4")
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response1.json)
        expected = {"error": "id: 2 does not exist"}
        self.assertEqual(expected, response2.json)
        expected = {"error": "id: 3 does not exist"}
        self.assertEqual(expected, response3.json)
        expected = {"error": "id: 4 does not exist"}
        self.assertEqual(expected, response4.json)

    def test_valid_move(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")

        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = [[None, None, None], [2, None, None], [3, None, None], [4, 1, None]]
        self.assertEqual(expected, response.json["board"])

        body = {"id": 1, "src": 1, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = [[None, None, None], [None, None, None], [3, None, None], [4, 1, 2]]
        self.assertEqual(expected, response.json["board"])

        body = {"id": 1, "src": 2, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = [[None, None, None], [None, None, None], [3, None, 1], [4, None, 2]]
        self.assertEqual(expected, response.json["board"])

    def test_invalid_move(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")

        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = [[None, None, None], [2, None, None], [3, None, None], [4, 1, None]]
        self.assertEqual(expected, response.json["board"])

        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = {"error": "invalid move", "src": 1, "dst": 2}
        self.assertEqual(expected, response.json)

        body = {"id": 1, "src": 1, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = [[None, None, None], [None, None, None], [3, None, None], [4, 1, 2]]
        self.assertEqual(expected, response.json["board"])

        body = {"id": 1, "src": 1, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = {"error": "invalid move", "src": 1, "dst": 3}
        self.assertEqual(expected, response.json)

    def test_undo_move_success(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")

        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        board = [[None, None, None], [2, None, None], [3, None, None], [4, 1, None]]
        self.assertEqual(1, response.json["id"])
        self.assertEqual(board, response.json["board"])
        self.assertEqual({"dst": [2], "src": [1]}, response.json["move_buffer"])
        self.assertEqual(1, response.json["move_buffer_size"])
        self.assertEqual(False, response.json["solved"])
        self.assertEqual(1, response.json["total_move_count"])
        self.assertEqual(1, response.json["valid_move_count"])

        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        self.assertEqual(1, response.json["id"])
        self.assertEqual(self.default_game["board"], response.json["board"])
        self.assertEqual(self.default_game["move_buffer"], response.json["move_buffer"])
        self.assertEqual(
            self.default_game["move_buffer_size"], response.json["move_buffer_size"]
        )
        self.assertEqual(self.default_game["solved"], response.json["solved"])
        self.assertEqual(2, response.json["total_move_count"])
        self.assertEqual(1, response.json["valid_move_count"])

    def test_undo_move_fail(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        self.assertEqual({"error": "move buffer empty: cannot undo"}, response.json)

        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        body = {"id": 1, "src": 1, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        body = {"id": 1, "src": 2, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        self.assertEqual(200, response.status_code)

        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        self.assertEqual({"error": "move buffer empty: cannot undo"}, response.json)

    def test_reset(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")

        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        body = {"id": 1, "src": 1, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        body = {"id": 1, "src": 2, "dst": 3}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)

        response = self.app.patch("http://127.0.0.1:5000/reset?id=1")
        self.assertEqual(self.default_game, response.json)

    def test_move_buffer(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")
        self.assertEqual(self.default_game["move_buffer"], response.json["move_buffer"])

        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )

        expected = {"dst": [2, 3, 3, 2, 1, 2, 2], "src": [1, 1, 2, 1, 3, 3, 1]}
        self.assertEqual(expected, response.json["move_buffer"])

        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")

        expected = {
            "dst": [2, 3, 3, 2],
            "src": [1, 1, 2, 1],
        }
        self.assertEqual(expected, response.json["move_buffer"])

        # invalid moves - no change to buffer
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )

        response = self.app.get("http://127.0.0.1:5000/game_state?id=1")
        self.assertEqual(expected, response.json["move_buffer"])

    def test_invalid_id_state(self):
        response = self.app.get("http://127.0.0.1:5000/game_state?id=1")
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response.json)

    def test_invalid_id_undo(self):
        response = self.app.patch("http://127.0.0.1:5000/undo?id=1")
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response.json)

    def test_invalid_id_move(self):
        body = {"id": 1, "src": 1, "dst": 2}
        response = self.app.patch("http://127.0.0.1:5000/move", json=body)
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response.json)

    def test_invalid_id_reset(self):
        response = self.app.patch("http://127.0.0.1:5000/reset?id=1")
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response.json)

    def test_invalid_id_solved(self):
        response = self.app.get("http://127.0.0.1:5000/solved?id=1")
        expected = {"error": "id: 1 does not exist"}
        self.assertEqual(expected, response.json)

    def test_solved_third_pillar(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")

        self.assertNotEqual(self.solution_third, response.json["board"])

        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        self.assertNotEqual(self.solution_third, response.json["board"])
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )

        self.assertNotEqual(self.solution_third, response.json["board"])

        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )
        self.assertEqual(self.solution_third, response.json["board"])
        self.assertTrue(response.json["solved"])

    def test_solved_second_pillar(self):
        response = self.app.get("ttp://127.0.0.1:5000/new")

        self.assertNotEqual(self.solution_second, response.json["board"])
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        self.assertNotEqual(self.solution_second, response.json["board"])
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 2, "dst": 1}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 2}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 3}
        )
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 1, "dst": 2}
        )
        self.assertNotEqual(self.solution_second, response.json["board"])
        response = self.app.patch(
            "http://127.0.0.1:5000/move", json={"id": 1, "src": 3, "dst": 2}
        )
        self.assertEqual(self.solution_second, response.json["board"])
        self.assertTrue(response.json["solved"])


if __name__ == "__main__":
    unittest.main()
