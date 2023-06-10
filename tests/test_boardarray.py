import os.path
from unittest import TestCase
import chess
import numpy as np

from constants import PROJECT_PATH
from games_from_dataset import file_parser, game_states
import boardarray


class TestBoardArray(TestCase):
    TENSOR1 = np.array((((0, 0, 0, 0, 0, 0, 0, 0),
                       (1, 1, 0, 0, 0, 0, 1, 1),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 1, 0, 1, 1, 0, 0),
                       (0, 0, -1, 1, -2, 0, 0, 0),
                       (0, 0, 0, -1, 0, 0, -1, 0),
                       (-1, -1, 0, 0, 0, -1, 0, -1),
                       (0, 0, 0, 0, 0, 0, 0, 0)),

                      ((0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 1, 0, 0, 1, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, -1, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, -1, 0, 0, 0, 0, 0, 0)),

                      ((0, 0, 1, 0, 0, 1, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, -1, 0),
                       (0, 0, -1, 0, 0, 0, 0, 0)),

                      ((2, 0, 0, 0, 0, 0, 0, 2),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (-1, 0, 0, 0, 0, -1, 0, 0)),

                      ((0, 0, 0, 1, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, -1, 0, 0, 0, 0)),

                      ((0, 0, 0, 0, 1, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, 0, 0),
                       (0, 0, 0, 0, 0, 0, -1, 0))))

    ARRAY1 = [30, 0, 9, 11, 12, 9, 0, 30,
              7, 7, 0, 0, 0, 0, 7, 7,
              0, 0, 8, 0, 0, 8, 0, 0,
              0, 0, 7, 0, 7, 7, 0, 0,
              0, 0, 1, 7, 101, 0, 0, 0,
              0, 0, 0, 1, 0, 2, 1, 0,
              1, 1, 0, 0, 0, 1, 3, 1,
              4, 2, 3, 5, 0, 4, 6, 0]
    INFO1 = [1, 0, 8]
    FEN1 = "rnbq1rk1/pp3pbp/3p1np1/2pPp3/2P1PP2/2N2N2/PP4PP/R1BQKB1R w KQ e6 0 8"

    ARRAY2 = [30, 0, 9, 11, 12, 9, 0, 30, 7, 7, 7, 0, 0, 7, 7, 7, 0, 0,
              8, 0, 0, 8, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 1, 0, 101, 7,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 3, 1,
              24, 2, 3, 5, 6, 0, 2, 24]
    INFO2 = [1, 0, 6]
    FEN2 = "rnbqk1nr/p3ppbp/2p3p1/1p1pP3/3P4/2N2N2/PPP2PPP/R1BQKB1R w KQkq d6 0 6"

    # ------------------------------------------- TEST TO BOARD --------------------------------------------------------
    def test_array_to_board(self):
        array = np.concatenate((np.array(self.ARRAY1), np.array(self.INFO1)))
        b1 = chess.Board(fen=self.FEN1)
        b2 = boardarray.BoardArray(low_level=(array, None))
        self.assertEqual(b1, b2)

    def test_matrix_to_board(self):
        array = np.array(self.ARRAY1).reshape((8, 8))
        info = np.array(self.INFO1)
        b1 = chess.Board(fen=self.FEN1)
        b2 = boardarray.BoardArray(low_level=(array, info))
        self.assertEqual(b1, b2)

    def test_tensor_to_board(self):
        tensor = self.TENSOR1.copy()
        info = np.array(self.INFO1)
        b1 = chess.Board(fen=self.FEN1)
        b2 = boardarray.BoardArray(low_level=(tensor, info))
        self.assertEqual(b1, b2)

    # ------------------------------------------- TEST FROM BOARD ------------------------------------------------------

    def test_board_to_array(self):
        array = np.concatenate((np.array(self.ARRAY1), np.array(self.INFO1)))
        b1 = boardarray.BoardArray(fen=self.FEN1)
        b2_array, b2_info = b1.to_low_level(mode='array', additional_info=True)
        self.assertEqual(array.tolist(), b2_array.tolist())

    def test_board_to_matrix(self):
        array = np.array(self.ARRAY1)
        info = np.array(self.INFO1)
        b1 = boardarray.BoardArray(fen=self.FEN1)
        b2_array, b2_info = b1.to_low_level(mode='matrix', additional_info=True)
        self.assertEqual(array.tolist(), b2_array.flatten().tolist())
        self.assertEqual(info.tolist(), b2_info.tolist())

    def test_board_to_tensor(self):
        tensor = self.TENSOR1.copy()
        info = np.array(self.INFO1)
        b1 = boardarray.BoardArray(fen=self.FEN1)
        b2_array, b2_info = b1.to_low_level(mode='tensor', additional_info=True)
        self.assertEqual(tensor.tolist(), b2_array.tolist())
        self.assertEqual(info.tolist(), b2_info.tolist())

    # ------------------------------------------- COMPLETE TEST --------------------------------------------------------

    def test_array(self):
        # iterate through each game from the dataset
        for i, game in enumerate(file_parser(os.path.join(PROJECT_PATH, 'dataset.pgn'))):
            if i >= 10:
                return
            print(f"******************GAME {i + 1}******************")
            # iterate through states tuples
            for (s1, s2), l in game_states(game):
                fen1 = s1.fen()
                b1 = boardarray.BoardArray(fen=fen1)
                array1 = b1.to_low_level(mode='array', additional_info=True)
                b2 = boardarray.BoardArray(low_level=array1)
                fen2 = b2.fen()
                self.assertEqual(fen1, fen2)

    def test_matrix(self):
        # iterate through each game from the dataset
        for i, game in enumerate(file_parser(os.path.join(PROJECT_PATH, 'dataset.pgn'))):
            if i >= 10:
                return
            print(f"******************GAME {i + 1}******************")
            # iterate through states tuples
            for (s1, s2), l in game_states(game):
                fen1 = s1.fen()
                b1 = boardarray.BoardArray(fen=fen1)
                array1 = b1.to_low_level(mode='matrix', additional_info=True)
                b2 = boardarray.BoardArray(low_level=array1)
                fen2 = b2.fen()
                self.assertEqual(fen1, fen2)

    def test_tensor(self):
        # iterate through each game from the dataset
        for i, game in enumerate(file_parser(os.path.join(PROJECT_PATH, 'dataset.pgn'))):
            if i >= 10:
                return
            print(f"******************GAME {i + 1}******************")
            # iterate through states tuples
            for (s1, s2), l in game_states(game):
                fen1 = s1.fen()
                b1 = boardarray.BoardArray(fen=fen1)
                array1 = b1.to_low_level(mode='tensor', additional_info=True)
                b2 = boardarray.BoardArray(low_level=array1)
                fen2 = b2.fen()
                self.assertEqual(fen1, fen2)

    # ------------------------------------------- TEST VALIDATION ------------------------------------------------------
    # in boardarray.py 13 calls to 'raise' -> need to implement 13 test cases
    # first tests created in the same order as encountered in the code

    # 1. TEST RUNTIME_ERROR --------------------------------------------------------------------------------------------

    def test_board_shape(self):
        with self.assertRaises(RuntimeError):
            boardarray.BoardArray(low_level=((np.ones((9, 8), dtype=int), None)))

    def test_info_shape(self):
        with self.assertRaises(RuntimeError):
            boardarray.BoardArray(low_level=((np.ones((8, 8), dtype=int), np.ones(2, dtype=int))))

    def test_low_level_shape(self):
        with self.assertRaises(RuntimeError):
            boardarray.BoardArray(low_level=((np.ones((8, 8), dtype=int),
                                              np.ones(3, dtype=int), np.ones(2, dtype=int))))

    # 2. TEST TYPE_ERROR -----------------------------------------------------------------------------------------------

    def test_board_is_ndarray(self):
        with self.assertRaises(TypeError):
            boardarray.BoardArray(low_level=({}, np.empty((0,))))

    def test_board_is_int(self):
        with self.assertRaises(TypeError):
            boardarray.BoardArray(low_level=(np.ones((8, 8), dtype=float), np.empty((0,))))

    def test_info_is_ndarray(self):
        with self.assertRaises(TypeError):
            boardarray.BoardArray(low_level=(np.ones((8, 8), dtype=int), (3)))

    def test_info_is_int(self):
        with self.assertRaises(TypeError):
            boardarray.BoardArray(low_level=(np.ones((8, 8), dtype=int), np.ones(3, dtype=float)))

    def test_low_level_is_tuple(self):
        with self.assertRaises(TypeError):
            boardarray.BoardArray(low_level=(np.ones((8, 8), dtype=int)))

    # 3. TEST VALUE_ERROR ----------------------------------------------------------------------------------------------

    def test_array_boundaries(self):
        array = np.concatenate((np.array(self.ARRAY1), np.array(self.INFO1)))
        array[6] -= 120
        with self.assertRaises(ValueError):
            boardarray.BoardArray(low_level=(array, None))

    def test_matrix_boundaries(self):
        matrix = np.array(self.ARRAY1).reshape((8,8))
        matrix[3][3] -= 120
        with self.assertRaises(ValueError):
            boardarray.BoardArray(low_level=(matrix, None))

    def test_tensor_boundaries(self):
        tensor = self.TENSOR1.copy()
        tensor[3][3][3] += 3
        with self.assertRaises(ValueError):
            boardarray.BoardArray(low_level=(tensor, None))

    def test_info_boundaries(self):
        with self.assertRaises(ValueError):
            boardarray.BoardArray(low_level=(np.zeros((8, 8), dtype=int), np.array((1, -4, 0))))

    def test_to_low_level_modes(self):
        with self.assertRaises(ValueError):
            b = boardarray.BoardArray(fen=self.FEN1)
            b.to_low_level(mode='matrice', additional_info=True)
