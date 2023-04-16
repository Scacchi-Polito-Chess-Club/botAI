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

REVERSE_DICTIONARY = {v: k for k, v in DICTIONARY.items()}

TURN_DICTIONARY = {'b': 0, 'w': 1}
REVERSE_TURN_DICTIONARY = {0: 'b', 1: 'w'}

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
        yield (old_board.fen(), board.fen()), move.uci()


def board_to_array(board: chess.Board) -> np.ndarray:
    cells = str(board).split()
    # flip each row to restore the correct cell ordering
    for i in range(8):
        cells[i * 8:i * 8 + 8] = cells[i * 8:i * 8 + 8][::-1]

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
        # compute offset for target ep square based on current player
        s = 1 if board.ep_square < 32 else -1

        cells_encoding[board.ep_square + s * 8] += OFFSET_ENPASSANT

    # True if w, False if b
    turn = str(board.fen()).split()[1]
    half_move = str(board.fen()).split()[4]
    full_move = str(board.fen()).split()[5]

    cells_encoding = np.concatenate((cells_encoding, np.array([TURN_DICTIONARY[turn], int(half_move), int(full_move)])),
                                    dtype=int)

    return cells_encoding


def array_to_board(array: np.ndarray) -> chess.Board:
    castling = ""
    enpassant = None

    for i in range(64):
        if 20 < array[i] < 100:
            array[i] = array[i] - 20
            if i == 0:
                castling += 'q'
            elif i == 7:
                castling += 'k'
            elif i == 56:
                castling += 'Q'
            elif i == 63:
                castling += 'K'

        if array[i] > 100:
            array[i] = array[i] - 100
            s = 1 if i < 32 else -1
            enpassant = i - s * 8

    cells_dict = {i: chess.Piece(*v) for i, v in enumerate(
        map(lambda x: (x, False)
            if x <= OFFSET_COLOR
            else (x - OFFSET_COLOR, True), array[:64]))}

    board = chess.Board()
    board.set_piece_map(cells_dict)
    board.set_castling_fen(''.join(sorted(castling)))
    board.ep_square = enpassant

    board.turn = bool(array[64])
    board.halfmove_clock = array[65]
    board.fullmove_number = array[66]

    return board


def main():
    fen_white = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    fen_black = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
    fen_ep = "rnbqkbnr/ppp2ppp/8/3p4/4pP2/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2"

    board = chess.Board(fen=fen_ep)
    # print(board.fen())
    fen1 = board.fen()
    array = board_to_array(board)
    # print(array)

    board2 = array_to_board(array)
    # print(board2.fen())
    fen2 = board2.fen()

    print(fen1 == fen2)


if __name__ == '__main__':
    main()
