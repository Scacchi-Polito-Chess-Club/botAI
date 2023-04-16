from unittest import TestCase

from games_from_dataset import file_parser, game_states
import boardarray


class TestBoardArray(TestCase):

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
