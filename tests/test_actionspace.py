import pytest
import logs
from games_from_dataset import file_parser
from actionspace import decode_move, encode_move, TO_REDUCED_PROMOTION_MAP, PIECE_PROMOTION_SYMBOLS

@pytest.fixture
def games_dataset():
    yield file_parser('dataset.pgn')

def test_promotion_exceptions():
    pass

def test_dataset_games_consistency(games_dataset):
    game_count = 0
    for game in games_dataset:
        for i, move in enumerate(game.mainline_moves()):
            try:
                if move.promotion is not None:
                    TO_REDUCED_PROMOTION_MAP[move.promotion]
            except KeyError:
                logs.warning(f"The move {move.uci()} promote to a piece outside of {PIECE_PROMOTION_SYMBOLS}. It will be skipped by the test. Generally it will be treated as a queen promotion.")
                action = encode_move(move, output_in_numpy=False)
                decoded_move = decode_move(action, output_in_uci=False)
                assert decoded_move.uci()[-1] == "q"
                continue
            try:
                action = encode_move(move, output_in_numpy=False)
                decoded_move = decode_move(action, output_in_uci=False)
            except Exception as err:
                logs.error(f'Raised exception at move: {i}, game: {game_count}\n\tMove: from_square {move.from_square} to_square {move.to_square} uci {move.uci()}\n\tAction space index of move element: {action.index(1)}')
                raise err
            assert decoded_move == move, f'Dataset move: \n\tfrom_square {move.from_square}\n\t to_square{move.to_square}\nDecoded Move:\n\tfrom_square {decoded_move.from_square}\n\tto_square {decoded_move.to_square}'
        game_count += 1
    logs.info(f'Tests passed for {game_count} games')
