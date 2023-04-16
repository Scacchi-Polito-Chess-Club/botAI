import chess
import chess.pgn
import numpy as np
# np.set_printoptions(formatter={'int': hex})

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
        # yield (str(old_board), str(board)), move.uci()
        # yield (old_board.fen(), board.fen()), move.uci()
        yield (old_board, board), move.uci()


def board_to_array(board: chess.Board):
    cells = str(board).split()
    cells_encoding = np.array(list(map(lambda x: DICTIONARY[x], cells)))
    castling = str(board.fen()).split()[2]
    castling_encoding = np.array(list(map(lambda x: CASTLING[x], castling)))
    enpassant = 0 if board.ep_square is None else (board.ep_square % 8) + 1

    board_encoding = np.hstack((cells_encoding, castling_encoding, enpassant))
    print(board_encoding)


def board_to_array2(board: chess.Board):
    cells = str(board).split()
    cells_encoding = np.array(list(map(lambda x: DICTIONARY[x], reversed(cells))))
    castling = str(board.fen()).split()[2]

    if 'K' in castling:
        # cells_encoding[60] += OFFSET_CASTLING
        cells_encoding[63] += OFFSET_CASTLING
    if 'Q' in castling:
        cells_encoding[56] += OFFSET_CASTLING
        # cells_encoding[60] += OFFSET_CASTLING
    if 'k' in castling:
        # cells_encoding[4] += OFFSET_CASTLING
        cells_encoding[7] += OFFSET_CASTLING
    if 'q' in castling:
        cells_encoding[0] += OFFSET_CASTLING
        # cells_encoding[4] += OFFSET_CASTLING

    if board.ep_square is not None:

        ts = board.ep_square - 2*(board.ep_square % 8) + 7
        print(ts)

        s = 1 if ts < 32 else -1

        cells_encoding[ts + s*8] += OFFSET_ENPASSANT

        print(cells_encoding)
        print(len(cells_encoding))


def main():

    # iterate through each game from the dataset
    for i, game in enumerate(file_parser()):

        print(f"******************GAME {i+1}******************")

        # iterate through states tuples
        for (s1, s2), l in game_states(game):
            # print(l)
            # print()
            # print(s1)
            # print()
            # print(s2)
            # print()
            board_to_array2(s1)
            break

        # for debug purpose, stop at first iteration
        if i == 0:
            break


if __name__ == '__main__':
    # main()

    fen_white = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    fen_black = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"

    board1 = chess.Board(fen=fen_black)
    print(board1)
    board_to_array2(board1)
