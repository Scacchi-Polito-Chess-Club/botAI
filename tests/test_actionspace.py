import pytest
import logging
from games_from_dataset import file_parser
from actionspace import ActionSpace

@pytest.fixture
def games_dataset():
    yield file_parser('dataset.pgn')

def test_promotion_exceptions():
    pass

def test_real_games_consistency(games_dataset):
    a = ActionSpace()
    game_count = 0
    for game in games_dataset:
        for i, move in enumerate(game.mainline_moves()):
            try:
                encoded_move = a.encode_move(move)
                decoded_move = a.decode_action(encoded_move)
            except Exception as err:
                logging.error(f'Raised exception at move: {i}, game: {game_count}\n\tMove: from_square {move.from_square} to_square {move.to_square} uci {move.uci()}\n\tAction space index of move element: {encoded_move.index(1)}')
                raise err
            assert decoded_move == move, f'Dataset move: \n\tfrom_square {move.from_square}\n\t to_square{move.to_square}\nDecoded Move:\n\tfrom_square {decoded_move.from_square}\n\tto_square {decoded_move.to_square}'
        game_count += 1
    logging.info(f'Tests passed for {game_count} games')
