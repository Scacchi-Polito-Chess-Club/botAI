import chess
from itertools import product
from itertools import chain
import json
import logging

BOARD_SIZE = 64
BOARD_ROWS = 8

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
# add promotion
class ActionSpace():
    def __init__(self):
        self.index_to_letter = self._get_index_to_letter()

    def _get_index_to_letter(self) -> str:
        letters = list('abcdefgh')
        return {i+1: x for i, x in enumerate(letters)}

    def _from_index_to_uci(self, index_square: int):
        # 1 => 'a' ... 8 => 'h'
        column_square = (index_square // BOARD_ROWS) + 1
        # 1 ... 8
        row_square = (index_square % BOARD_ROWS) + 1
        # 'a1' ... 'h8'
        square = f'{self.index_to_letter[column_square]}{row_square}'
        return square

    def decode_action(self, action) -> chess.Move:
        # 64 x 64
        try:
            # index_move = action.one_hot_list.index(1)
            index_move = action.index(1)
        except Exception as err:
            logging.error('The one hot encoded list in the action object has no element equal to 1!')
            raise err

        # 0 => 'a0' ... 63 => 'h7'
        index_from_square = index_move // BOARD_SIZE
        # 0 => 'a0' ... 63 => 'h7'
        index_target_square = index_move % BOARD_SIZE
        # a0a0, c6c6, f9f9, etc..
        if index_from_square == index_target_square:
            return chess.Move.null()
        from_square = self._from_index_to_uci(index_from_square)
        target_square = self._from_index_to_uci(index_target_square)
        move_string = f'{from_square}{target_square}'
        try:
            move = chess.Move.from_uci(move_string)
        except chess.InvalidMoveError as err:
            logging.error(f"Move {move_string} is not a valid UCI string")
            raise err
        return move

    def encode_move(self, move: chess.Move):
        pass

def main():
    a = ActionSpace()
    action_space_test = [0 for _ in range(BOARD_SIZE*BOARD_SIZE)]
    action_space_test[2] = 1
    move = a.decode_action(action_space_test)
    logging.info(move.uci())

if __name__ == "__main__":
    main()