import chess
import chess.pgn
import numpy as np

FILENAME = "dataset.pgn"

# uppercase white, lowercase black
DICTIONARY = {
    '.': 0,
    'p': 1,
    'n': 2,
    'b': 3,
    'r': 4,
    'q': 5,
    'k': 6,
    'P': 7,
    'N': 8,
    'B': 9,
    'R': 10,
    'Q': 11,
    'K': 12,
}


TURN_DICTIONARY = {'b': 0, 'w': 1}
REVERSE_TURN_DICTIONARY = {0: 'b', 1: 'w'}

CASTLING_INDICES = {0: 'Q', 7: 'K', 56: 'q', 63: 'k'}

OFFSET_COLOR = 6
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
    i = 0
    with open(fname) as f:
        while True:
            try:
                game = chess.pgn.read_game(f)
                if game:
                    i += 1
                    print(i)
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


if __name__ == '__main__':
    # main()
    file_parser()
