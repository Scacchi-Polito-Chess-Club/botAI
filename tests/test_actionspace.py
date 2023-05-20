import pytest
import logging
from games_from_dataset import file_parser
from actionspace import decode_move, encode_move

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
                action = encode_move(move, output_in_numpy=False)
                decoded_move = decode_move(action, output_in_uci=False)
            except Exception as err:
                logging.error(f'Raised exception at move: {i}, game: {game_count}\n\tMove: from_square {move.from_square} to_square {move.to_square} uci {move.uci()}\n\tAction space index of move element: {action.index(1)}')
                raise err
            assert decoded_move == move, f'Dataset move: \n\tfrom_square {move.from_square}\n\t to_square{move.to_square}\nDecoded Move:\n\tfrom_square {decoded_move.from_square}\n\tto_square {decoded_move.to_square}'
        game_count += 1
    logging.info(f'Tests passed for {game_count} games')
