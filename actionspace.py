import chess
from itertools import product
from itertools import chain
import json
import logging
import numpy as np


BOARD_SIZE = 64
BOARD_ROWS = 8
EDGE_COLUMNS = 2
COLUMNS = list('abcdefgh')
ROWS = list('12345678')
PIECE_SYMBOLS = [None, "p", "n", "b", "r", "q", "k"] # python-chess notation

BOARD_MOVES = BOARD_SIZE * BOARD_SIZE
PROMOTION_MOVES_PER_SIDE = ((BOARD_ROWS - EDGE_COLUMNS)*3 + EDGE_COLUMNS * 2)
PROMOTION_MOVES =  PROMOTION_MOVES_PER_SIDE * (len(PIECE_SYMBOLS)-1) * 2 # `* 2` is the number of sides
ACTION_SPACE_SIZE = BOARD_MOVES + PROMOTION_MOVES 

square_to_letter = {i+1: x for i, x in enumerate(COLUMNS)}

def _from_square_to_uci(square: int) -> str:
    # 1 => 'a' ... 8 => 'h'
    column_square = (square % BOARD_ROWS) + 1
    # 1 ... 8
    row_square = (square // BOARD_ROWS) + 1
    # 'a1' ... 'h8'
    square_uci = f'{square_to_letter[column_square]}{row_square}'
    return square_uci

def decode_move(action: list[int]|np.ndarray, output_in_uci: bool = True) -> chess.Move|str:
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
    
    if index_move < BOARD_MOVES: # NOT a promotion move
        # 0 => 'a1' ... 63 => 'h8'
        from_square = index_move // BOARD_SIZE
        # 0 => 'a1' ... 63 => 'h8'
        to_square = index_move % BOARD_SIZE
        # a1a1, c6c6, f9f9, etc..
        if from_square == to_square:
            if output_in_uci:
                return '0000'
            return chess.Move.null()

        from_square_uci = _from_square_to_uci(from_square)
        to_square_uci = _from_square_to_uci(to_square)
        move_string = f'{from_square_uci}{to_square_uci}'
    else: # Promotion move (quite trickier)
        index_move = index_move - BOARD_MOVES
        index_promotion = index_move // (PROMOTION_MOVES_PER_SIDE * 2)
        promotion_piece = PIECE_SYMBOLS[index_promotion + 1] # +1 because of the None piece
        index_move = index_move - index_promotion * (PROMOTION_MOVES_PER_SIDE * 2)
        # 0 => white, 1 => black
        side = index_move // PROMOTION_MOVES_PER_SIDE
        if side == 0: # White
            from_row_square = BOARD_ROWS - 1
            to_row_square = BOARD_ROWS
        elif side == 1: # Black
            from_row_square = 2
            to_row_square = 1
        else:
            raise AssertionError(f"side should be 0 or 1 but it's {side}")
        # Computing the columns: it is independent from the side
        index_move = index_move % PROMOTION_MOVES_PER_SIDE
        if index_move < 2: # Left edge cell
            from_column_square = COLUMNS[0] # a
            to_column_square =  COLUMNS[index_move] # a || b
        elif index_move > PROMOTION_MOVES_PER_SIDE - 2: # Right edge cell
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
    if output_in_uci:
        return move.uci()
    return move

def encode_move(move: chess.Move|str, output_in_numpy: bool = True) -> list[int]|np.ndarray:
    if isinstance(move, str):
        move = chess.Move.from_uci(move)
    action = [0 for _ in range(ACTION_SPACE_SIZE)]
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
        index_move += side * PROMOTION_MOVES_PER_SIDE
        from_square_column = move.from_square % BOARD_ROWS # Column
        to_square_column = move.to_square % BOARD_ROWS # Column
        if from_square_column == 0: # Left edge cell
            assert to_square_column < 2, f'Promotion from column {from_square_column} to column {to_square_column}!!'
            index_move += to_square_column
        elif from_square_column == BOARD_ROWS-1: # Right edge cell
            assert to_square_column > BOARD_ROWS-3, f'Promotion from column {from_square_column} to column {to_square_column}!!'
            index_move += PROMOTION_MOVES_PER_SIDE - 2 + (to_square_column%2)
        else:
            index_move += 2 + ((from_square_column - 1) * 3) + (to_square_column - from_square_column + 1) # (from_square_column - to_square_column + 1) 
        index_move += (move.promotion - 1) * (PROMOTION_MOVES_PER_SIDE * 2) # Offset of the promotion piece
        index_move += BOARD_MOVES # Offset of all moves that are not promotions
    action[index_move] = 1
    assert sum(action) == 1
    return np.array(action)

def main():
    logging.basicConfig(level = logging.INFO)
    action = [0 for _ in range(ACTION_SPACE_SIZE)]
    action[4096] = 1 # one-hot-encoded vector

    move = decode_action(action)
    logging.info(move.uci())

    action_from_move = encode_move(move)
    logging.info(action_from_move.index(1))
    assert action == action_from_move

    move_from_action = decode_action(action_from_move)
    assert move.from_square == move_from_action.from_square
    assert move.to_square == move_from_action.to_square

if __name__ == "__main__":
    main()