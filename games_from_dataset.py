import chess
import chess.pgn
import numpy as np
# np.set_printoptions(formatter={'int': hex})

FILENAME = "dataset.pgn"

DICTIONARY = {
    '.': 0x0,
    'p': 0x1,
    'r': 0x2,
    'b': 0x3,
    'n': 0x4,
    'q': 0x5,
    'k': 0x6,
    'P': 0x7,
    'R': 0x8,
    'B': 0x9,
    'N': 0xa,
    'Q': 0xb,
    'K': 0xc,
}


def file_parser(fname: str = FILENAME) -> chess.pgn.Game:
    """
    This function yields one game at a time, taken from the file @fname.

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
    castling = str(board.fen).split()[6]
    castling_encoding = np.array(list(map(lambda x: CASTLING[x], castling)))
    if board.ep_square is not None:
        enpassant = (board.ep_square + 1) % 8
        if enpassant == 0:
            enpassant = 8
    else:
        enpassant = 0
    board_encoding = np.hstack((cells_encoding, castling_encoding, enpassant))
    print(board_encoding)


CASTLING = {
    'K': 1,
    'Q': 1,
    'k': 1,
    'q': 1,
    '-': 0,
}


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
            board_to_array(s1)
            break

        # for debug purpose, stop at first iteration
        if i == 0:
            break


if __name__ == '__main__':
    main()
