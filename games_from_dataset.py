import chess
import chess.pgn
import numpy as np

FILENAME = "dataset.pgn"


# uppercase white, lowercase black
DICTIONARY = {
    '.': 0,
    'p': 1,
    'r': 2,
    'b': 3,
    'n': 4,
    'q': 5,
    'k': 6,
    'P': 7,
    'R': 8,
    'B': 9,
    'N': 10,
    'Q': 11,
    'K': 12,
}

inverse_dict = {v: k for k, v in DICTIONARY.items()}

CASTLING = {
    'K': 13,
    'Q': 14,
    'k': 15,
    'q': 16,
    '-': 0,
}

OFFSET_CASTLING = 20
OFFSET_ENPASSANT = 100


def file_parser(fname: str = FILENAME) -> chess.pgn.Game:
    """
    This function yields one game at a time, taken from the file @fname.

    Args:
    :param fname: the name of the pgn dataset file
    :type fname: str
    :return: one game at a time
    :rtype: chess.pgn.Game
    """
    with open(fname) as f:
        while True:
            try:
                game = chess.pgn.read_game(f)
                if game:
                    yield game
                else:
                    return
            except Exception as e:
                print(e)


def game_states(game: chess.pgn.Game) -> tuple[tuple[str, str], str]:
    """
    This function yields one tuple at a time in the form (s_t, s_t+1)

    :param game: the game taken from the database (class chess.pgn.Game)
    :type game: chess.pgn.Game
    :return: the tuple (s_t, s_t+1) and the ground truth (the move that led from s_t to s_t+1)
    :rtype: tuple
    """
    # create a new board
    board = chess.Board()
    # iterate through the moves of @param game
    for i, move in enumerate(game.mainline_moves()):
        # save copy before executing move
        old_board = board.copy(stack=False)
        board.push(move)
        # yield the result one at a time
        yield (old_board, board), move.uci()


def board_to_array(board: chess.Board) -> np.ndarray:

    cells = str(board).split()
    cells_encoding = np.array(list(map(lambda x: DICTIONARY[x], reversed(cells))))
    castling = str(board.fen()).split()[2]

    if 'K' in castling:
        cells_encoding[63] += OFFSET_CASTLING
    if 'Q' in castling:
        cells_encoding[56] += OFFSET_CASTLING
    if 'k' in castling:
        cells_encoding[7] += OFFSET_CASTLING
    if 'q' in castling:
        cells_encoding[0] += OFFSET_CASTLING

    if board.ep_square is not None:
        # compute target square index inside cells_encoding
        ts = board.ep_square - 2*(board.ep_square % 8) + 7
        # compute offset for ts based on current player
        s = 1 if ts < 32 else -1

        cells_encoding[ts + s*8] += OFFSET_ENPASSANT

    return cells_encoding


def array_to_board(array: np.ndarray) -> chess.Board:
    cells_encoding = list(map(lambda x: inverse_dict[x], array))
    print(cells_encoding)


def main():
    pass


if __name__ == '__main__':
    main()
