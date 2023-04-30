import itertools

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
REVERSE_CASTLING_INDICES = {'Q': 0, 'K': 7, 'q': 56, 'k': 63}

CHANNEL_DICTIONARY = {
    'p': 0,
    'n': 1,
    'b': 2,
    'r': 3,
    'q': 4,
    'k': 5
}

REVERSE_CHANNEL_DICTIONARY = {
    0: 'p',
    1: 'n',
    2: 'b',
    3: 'r',
    4: 'q',
    5: 'k',
}

OFFSET_COLOR = 6
OFFSET_CASTLING = 20
OFFSET_ENPASSANT = 100

MIN_ARRAY_LEGAL_VALUE = 0
MAX_ARRAY_LEGAL_VALUE = OFFSET_ENPASSANT + 7
MIN_INFO_LEGAL_VALUE = 0
MAX_INFO_LEGAL_VALUE = np.inf


def validate_low_level_arg(low_level: tuple) -> tuple[np.ndarray, np.ndarray, str]:
    def validate_first():
        arr = low_level[0]
        info = None
        if type(arr) is not np.ndarray:
            raise TypeError("Error: the first element of argument `low_level` must be a numpy ndarray")
        if arr.dtype != int:
            raise TypeError("Error: the first element of argument `low_level` must have integer elements")

        if arr.shape == (67,):
            info = arr[64:]
            arr = arr[:64]
            m = 'array'
            if not np.all(MIN_ARRAY_LEGAL_VALUE <= arr <= MAX_ARRAY_LEGAL_VALUE):
                raise ValueError("Error: the first array of argument `low_level` cannot have the first 64 values "
                                 f"outside the range [{MIN_ARRAY_LEGAL_VALUE},{MAX_ARRAY_LEGAL_VALUE}]")

        elif arr.shape == (8, 8):
            m = 'matrix'
            if not np.all(MIN_ARRAY_LEGAL_VALUE <= arr <= MAX_ARRAY_LEGAL_VALUE):
                raise ValueError("Error: the matrix of argument `low_level` cannot have values outside the "
                                 f"range [{MIN_ARRAY_LEGAL_VALUE},{MAX_ARRAY_LEGAL_VALUE}]")
        elif arr.shape == (6, 8, 8):
            m = 'tensor'
            if not np.all(arr in [-1, 0, 1]):
                raise ValueError("Error: the tensor of argument `low_level` cannot have values different from -1, 0, 1")
        else:
            raise RuntimeError("Error: the first element of argument `low_level` must have either shape (67,), (8,8) or"
                               "(6, 8, 8)")
        return arr, info, m

    def validate_info(info):
        add_info = info if info else low_level[1]
        if add_info is None:
            add_info = np.array([1, 0, 0])
        if type(add_info) is not np.ndarray:
            raise TypeError("Error: the second element of argument `low_level` must be either None or a numpy "
                            "ndarray")
        if add_info.shape != (3,):
            raise RuntimeError("Error: the second element of argument `low_level` must be either None or have "
                               "shape (3,)")
        if add_info.dtype != int:
            raise ValueError("Error: the second element of argument `low_level` must be either None or have "
                             "integer elements")
        if not (np.all(MIN_INFO_LEGAL_VALUE <= add_info <= MAX_INFO_LEGAL_VALUE)):
            raise ValueError("Error: the second element of argument `low_level` must be either None or have values "
                             f"in the range [{MIN_INFO_LEGAL_VALUE},{MAX_INFO_LEGAL_VALUE}]")
        return add_info

    if type(low_level) is tuple:
        if len(low_level) == 2:
            array, add_inf, mode = validate_first()
            additional_info = validate_info(add_inf)

        else:
            raise RuntimeError("Error: argument `low_level` must have 2 elements. If you just want to pass the 8x8 "
                               "matrix, pass a tuple of the form (matrix, None): the next player is assumed to be W "
                               "and the counters are set to 0.")
    else:
        raise TypeError("Error: the argument `low_level` must be a tuple of 2 numpy arrays.")

    return array, additional_info, mode


class BoardArray(chess.Board):
    def __init__(self, *args, low_level: tuple = None, **kwargs):
        if low_level is not None:
            castling = ""
            enpassant = None

            array, additional_info, mode = validate_low_level_arg(low_level)

            if mode == 'tensor':
                for i in range(64):
                    # set castling possibility
                    if array[CHANNEL_DICTIONARY['r']][i] in [2, -2]:
                        castling += CASTLING_INDICES[i]
                    # set enpassant possibility
                    if array[CHANNEL_DICTIONARY['p']][i] in [2, -2]:
                        s = 1 if i < 32 else -1
                        enpassant = i - s * 8

                array[array == 2] = 1
                for i in range(6):
                    array[i][array == 1] = i + 1
                array = np.sum(array, axis=0)
                cells_dict = {i: chess.Piece(*v) for i, v in enumerate(
                    map(lambda x: (x, False)
                        if x <= OFFSET_COLOR
                        else (x - OFFSET_COLOR, True), array[:64]))}

            else:
                if mode == 'matrix':
                    array = array.flatten()

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

            self.turn = bool(additional_info[0])
            self.halfmove_clock = additional_info[1]
            self.fullmove_number = additional_info[2]
        else:
            super().__init__(*args, **kwargs)

    def to_low_level(self, mode='array') -> tuple[np.ndarray, np.ndarray]:
        modes = ['array', 'matrix', 'tensor']
        if mode not in modes:
            raise RuntimeError(f"Error: argument mode must be one of {modes}")

        cells = str(self).split()
        # flip each row to restore the correct cell ordering
        for i in range(8):
            cells[i * 8:i * 8 + 8] = cells[i * 8:i * 8 + 8][::-1]

        # True if w, False if b
        turn = str(self.fen()).split()[1]
        half_move = str(self.fen()).split()[4]
        full_move = str(self.fen()).split()[5]

        # additional state information
        additional = np.array([TURN_DICTIONARY[turn], int(half_move), int(full_move)])

        if mode == 'tensor':
            arr = np.zeros((6, 8, 8), dtype=int)
            for i in range(64):
                ch = cells[i]
                if ch == '.':
                    continue
                if ch == ch.lower():
                    # black
                    n = -1
                else:
                    # white
                    n = 1
                    ch = ch.lower()
                arr[CHANNEL_DICTIONARY[ch], i // 8, i % 8] = n

            castling = str(self.fen()).split()[2]

            for ch in "kqKQ":
                if ch in castling:
                    i = REVERSE_CASTLING_INDICES[ch] // 8
                    j = REVERSE_CASTLING_INDICES[ch] % 8
                    k = CHANNEL_DICTIONARY['r']
                    arr[k, i, j] *= 2

            if self.ep_square is not None:
                s = 1 if self.ep_square < 32 else -1
                n = self.ep_square + s * 8
                i = n // 8
                j = n % 8
                k = CHANNEL_DICTIONARY['p']
                arr[k, i, j] *= 2

        else:
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

            if mode == 'array':
                arr = np.concatenate((cells_encoding, additional))
                additional = None
            else:
                arr = cells_encoding.reshape((8, 8))

        return arr, additional


def main():
    fen_white = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    ba = BoardArray()
    # ba = BoardArray(fen=fen_white)
    print(*ba.to_low_level(mode='tensor'))


if __name__ == "__main__":
    main()
