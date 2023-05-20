import chess
from itertools import product
from itertools import chain
import json
import logging

BOARD_SIZE = 64
BOARD_ROWS = 8
EDGE_COLUMNS = 2
COLUMNS = list('abcdefgh')
ROWS = list('12345678')

# python-chess notation
PIECE_SYMBOLS = [None, "p", "n", "b", "r", "q", "k"]
PieceType = int

class ActionSpace():
    def __init__(self):
        self.square_to_letter = self._get_square_to_letter()
        self.board_moves = BOARD_SIZE * BOARD_SIZE
        self.promotion_moves_per_side = ((BOARD_ROWS - EDGE_COLUMNS)*3 + EDGE_COLUMNS * 2)
        self.promotion_moves =  self.promotion_moves_per_side * (len(PIECE_SYMBOLS)-1) * 2 # `* 2` is the number of sides
        self.action_space_size = self.board_moves + self.promotion_moves 

    def _get_square_to_letter(self) -> str:
        letters = list('abcdefgh')
        return {i+1: x for i, x in enumerate(letters)}

    def _from_square_to_uci(self, square: int):
        # 1 => 'a' ... 8 => 'h'
        column_square = (square % BOARD_ROWS) + 1
        # 1 ... 8
        row_square = (square // BOARD_ROWS) + 1
        # 'a1' ... 'h8'
        square = f'{self.square_to_letter[column_square]}{row_square}'
        return square

    def decode_action(self, action) -> chess.Move:
        # 64 * 64 + {[(8-2)*3 + 2*2]*6}*2
        # BOARD_SIZE * BOARD_SIZE + [(BOARD_ROWS-EDGE_COLUMNS)*3 + EDGE_COLUMNS * len(PIECE_SYMBOLS)] * 2
        # The second term refers to the promotion moves
        # The last `*2` refers to both white and black

        try:
            # index_move = action.one_hot_list.index(1)
            index_move = action.index(1) # action is a one hot encoded vector
        except Exception as err:
            logging.error('The one hot encoded list in the action object has no element equal to 1!')
            raise err
        
        if index_move < (self.board_moves): # NOT a promotion move
            # 0 => 'a1' ... 63 => 'h8'
            from_square = index_move // BOARD_SIZE
            # 0 => 'a1' ... 63 => 'h8'
            to_square = index_move % BOARD_SIZE
            # a1a1, c6c6, f9f9, etc..
            if from_square == to_square:
                return chess.Move.null()

            from_square_uci = self._from_square_to_uci(from_square)
            to_square_uci = self._from_square_to_uci(to_square)
            move_string = f'{from_square_uci}{to_square_uci}'
        else: # Promotion move (quite trickier)
            index_move = index_move - self.board_moves
            index_promotion = index_move // (self.promotion_moves_per_side * 2)
            promotion_piece = PIECE_SYMBOLS[index_promotion + 1] # +1 because of the None piece
            index_move = index_move - index_promotion * (self.promotion_moves_per_side * 2)
            # 0 => white, 1 => black
            side = index_move // self.promotion_moves_per_side
            if side == 0: # White
                from_row_square = BOARD_ROWS - 1
                to_row_square = BOARD_ROWS
            elif side == 1: # Black
                from_row_square = 2
                to_row_square = 1
            else:
                raise AssertionError(f"side should be 0 or 1 but it's {side}")
            # Computing the columns: it is independent from the side
            index_move = index_move % self.promotion_moves_per_side
            if index_move < 2: # Left edge cell
                from_column_square = COLUMNS[0] # a
                to_column_square =  COLUMNS[index_move] # a || b
            elif index_move > self.promotion_moves_per_side - 2: # Right edge cell
                from_column_square = COLUMNS[-1] # h
                to_column_square = COLUMNS[BOARD_ROWS-(index_move%2)] # g || h
            else:
                from_column_index = ((index_move - 2) // 3) + 1 # -2 => `- left edge promotion moves`
                from_column_square = COLUMNS[from_column_index] # b ... e
                to_column_offset = ((index_move -2) % 3) - 1 # -2 => `- left edge promotion moves`
                to_column_index = from_column_index + to_column_offset
                to_column_square = COLUMNS[to_column_index]
            from_square_uci = f'{from_column_square}{from_row_square}'
            to_square_uci = f'{to_column_square}{to_row_square}'
            assert from_square_uci != to_square_uci
            move_string = f'{from_square_uci}{to_square_uci}{promotion_piece}'
            
        try:
            move = chess.Move.from_uci(move_string)
        except chess.InvalidMoveError as err:
            logging.error(f"Move {move_string} is not a valid UCI string")
            raise err
        return move

    def encode_move(self, move: chess.Move):
        action = [0 for _ in range(self.action_space_size)]
        # The logic is more understandable looking at `decode_move`
        # here I just reverse the operations
        if not move.promotion:
            index_move = move.from_square * BOARD_SIZE
            index_move = index_move + move.to_square
        else:
            index_move = 0 # Initialized
            to_square_row = move.to_square // BOARD_ROWS # Row
            if to_square_row == BOARD_ROWS - 1:
                side = 0 # White
            elif to_square_row == 0:
                side = 1 # Black
            else:
                raise AssertionError('Promotion from row {from_square_row} to row {to_square_row}!!')
            index_move += side * self.promotion_moves_per_side
            from_square_column = move.from_square % BOARD_ROWS # Column
            to_square_column = move.to_square % BOARD_ROWS # Column
            if from_square_column == 0: # Left edge cell
                assert to_square_column < 2, f'Promotion from column {from_square_column} to column {to_square_column}!!'
                index_move += to_square_column
            elif from_square_column == BOARD_ROWS-1: # Right edge cell
                assert to_square_column > BOARD_ROWS-3, f'Promotion from column {from_square_column} to column {to_square_column}!!'
                index_move += self.promotion_moves_per_side - 2 + (to_square_column%2)
            else:
                index_move += 2 + ((from_square_column - 1) * 3) + (to_square_column - from_square_column + 1) # (from_square_column - to_square_column + 1) 
            index_move += (move.promotion - 1) * (self.promotion_moves_per_side * 2) # Offset of the promotion piece
            index_move += self.board_moves # Offset of all moves that are not promotions
        action[index_move] = 1
        assert sum(action) == 1
        return action

def main():
    logging.basicConfig(level = logging.INFO)
    a = ActionSpace()
    action_space_test = [0 for _ in range(a.action_space_size)]
    action_space_test[4096] = 1

    move = a.decode_action(action_space_test)
    logging.info(move.uci())

    action_space_output_test = a.encode_move(move)
    logging.info(action_space_output_test.index(1))
    assert action_space_output_test == action_space_test

    move_output = a.decode_action(action_space_output_test)
    assert move.from_square == move_output.from_square
    assert move.to_square == move_output.to_square

if __name__ == "__main__":
    main()