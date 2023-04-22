from unittest import TestCase
import chess
import numpy as np
from games_from_dataset import file_parser, game_states
import boardarray


class TestBoardArray(TestCase):

    def test_to_board(self):
        array = np.array([30, 0, 9, 11, 12, 9, 0, 30, 7, 7, 0, 0, 0, 0, 7, 7, 0, 0, 8,
                          0, 0, 8, 0, 0, 0, 0, 7, 0, 7, 7, 0, 0, 0, 0, 1, 7, 101, 0,
                          0, 0, 0, 0, 0, 1, 0, 2, 1, 0, 1, 1, 0, 0, 0, 1, 3, 1, 4,
                          2, 3, 5, 0, 4, 6, 0, 1, 0, 8])
        fen = "rnbq1rk1/pp3pbp/3p1np1/2pPp3/2P1PP2/2N2N2/PP4PP/R1BQKB1R w KQ e6 0 8"
        b1 = chess.Board(fen=fen)
        b2 = boardarray.BoardArray(array=array)
        self.assertEqual(b1, b2)

    def test_to_array(self):
        array = np.array([30, 0, 9, 11, 12, 9, 0, 30, 7, 7, 7, 0, 0, 7, 7, 7, 0, 0,
                          8, 0, 0, 8, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 1, 0, 101, 7,
                          0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 3, 1,
                          24, 2, 3, 5, 6, 0, 2, 24, 1, 0, 6])
        fen = "rnbqk1nr/p3ppbp/2p3p1/1p1pP3/3P4/2N2N2/PPP2PPP/R1BQKB1R w KQkq d6 0 6"
        b1 = boardarray.BoardArray(fen=fen)
        b2 = b1.to_array()
        print(b2)
        print(array)
        self.assertEqual(array.tolist(), b2.tolist())

    def test_board_to_array(self):
        # iterate through each game from the dataset
        for i, game in enumerate(file_parser()):
            if i >= 10:
                return
            print(f"******************GAME {i + 1}******************")
            # iterate through states tuples
            for (s1, s2), l in game_states(game):
                fen1 = s1.fen()
                b1 = boardarray.BoardArray(fen=fen1)
                array1 = b1.to_array()
                b2 = boardarray.BoardArray(array=array1)
                fen2 = b2.fen()
                self.assertEqual(fen1, fen2)
