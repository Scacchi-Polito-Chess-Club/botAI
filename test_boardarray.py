from unittest import TestCase
import chess
import numpy as np
from games_from_dataset import file_parser, game_states
import boardarray


class TestBoardArray(TestCase):
    ARRAY1 = [30, 0, 9, 11, 12, 9, 0, 30, 7, 7, 0, 0, 0, 0, 7, 7, 0, 0, 8,
              0, 0, 8, 0, 0, 0, 0, 7, 0, 7, 7, 0, 0, 0, 0, 1, 7, 101, 0,
              0, 0, 0, 0, 0, 1, 0, 2, 1, 0, 1, 1, 0, 0, 0, 1, 3, 1, 4,
              2, 3, 5, 0, 4, 6, 0]
    INFO1 = [1, 0, 8]
    FEN1 = "rnbq1rk1/pp3pbp/3p1np1/2pPp3/2P1PP2/2N2N2/PP4PP/R1BQKB1R w KQ e6 0 8"

    ARRAY2 = [30, 0, 9, 11, 12, 9, 0, 30, 7, 7, 7, 0, 0, 7, 7, 7, 0, 0,
              8, 0, 0, 8, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 1, 0, 101, 7,
              0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 3, 1,
              24, 2, 3, 5, 6, 0, 2, 24]
    INFO2 = [1, 0, 6]
    FEN2 = "rnbqk1nr/p3ppbp/2p3p1/1p1pP3/3P4/2N2N2/PPP2PPP/R1BQKB1R w KQkq d6 0 6"

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

    def test_board_to_array(self):
        array = np.array(self.ARRAY2)
        info = np.array(self.INFO2)
        b1 = boardarray.BoardArray(fen=self.FEN2)
        b2_array, b2_info = b1.to_low_level(mode='array')
        self.assertEqual(array.tolist(), b2_array.tolist())
        self.assertEqual(info.tolist(), b2_info.tolist())

    def test_board_to_matrix(self):
        array = np.array(self.ARRAY2)
        info = np.array(self.INFO2)
        b1 = boardarray.BoardArray(fen=self.FEN2)
        b2_array, b2_info = b1.to_low_level(mode='matrix')
        self.assertEqual(array.tolist(), b2_array.flatten().tolist())
        self.assertEqual(info.tolist(), b2_info.tolist())

    def test_matrix(self):
        # iterate through each game from the dataset
        for i, game in enumerate(file_parser()):
            if i >= 10:
                return
            print(f"******************GAME {i + 1}******************")
            # iterate through states tuples
            for (s1, s2), l in game_states(game):
                fen1 = s1.fen()
                b1 = boardarray.BoardArray(fen=fen1)
                array1 = b1.to_low_level(mode='matrix')
                b2 = boardarray.BoardArray(low_level=array1)
                fen2 = b2.fen()
                self.assertEqual(fen1, fen2)
