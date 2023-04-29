import chess
import numpy as np

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


class BoardArray(chess.Board):
    def __init__(self, *args, array: np.ndarray = None, **kwargs):
        if array is not None:
            castling = ""
            enpassant = None

            for i in range(64):
                if OFFSET_CASTLING < array[i] < OFFSET_ENPASSANT:
                    array[i] = array[i] - OFFSET_CASTLING
                    castling += CASTLING_INDICES[i]

                if array[i] > OFFSET_ENPASSANT:
                    array[i] = array[i] - OFFSET_ENPASSANT
                    s = 1 if i < 32 else -1
                    enpassant = i - s * 8

            cells_dict = {i: chess.Piece(*v) for i, v in enumerate(
                map(lambda x: (x, False)
                    if x <= OFFSET_COLOR
                    else (x - OFFSET_COLOR, True), array[:64]))}

            super().__init__(*args, **kwargs)
            self.set_piece_map(cells_dict)
            self.set_castling_fen(''.join(sorted(castling)))
            self.ep_square = enpassant

            self.turn = bool(array[64])
            self.halfmove_clock = array[65]
            self.fullmove_number = array[66]
        else:
            super().__init__(*args, **kwargs)

    def to_array(self) -> tuple[np.ndarray, np.ndarray]:
        cells = str(self).split()
        # flip each row to restore the correct cell ordering
        for i in range(8):
            cells[i * 8:i * 8 + 8] = cells[i * 8:i * 8 + 8][::-1]

        cells_encoding = np.array(list(map(lambda x: DICTIONARY[x], reversed(cells))))
        castling = str(self.fen()).split()[2]

        if 'k' in castling:
            cells_encoding[63] += OFFSET_CASTLING
        if 'q' in castling:
            cells_encoding[56] += OFFSET_CASTLING
        if 'K' in castling:
            cells_encoding[7] += OFFSET_CASTLING
        if 'Q' in castling:
            cells_encoding[0] += OFFSET_CASTLING

        if self.ep_square is not None:
            # compute offset for target ep square based on current player
            s = 1 if self.ep_square < 32 else -1

            cells_encoding[self.ep_square + s * 8] += OFFSET_ENPASSANT

        # True if w, False if b
        turn = str(self.fen()).split()[1]
        half_move = str(self.fen()).split()[4]
        full_move = str(self.fen()).split()[5]

        # additional state information
        additional = np.array([TURN_DICTIONARY[turn], int(half_move), int(full_move)])

        return cells_encoding.reshape((8, 8)), additional


if __name__ == "__main__":
    fen_white = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    ba = BoardArray(fen=fen_white)
    print(*ba.to_array())
