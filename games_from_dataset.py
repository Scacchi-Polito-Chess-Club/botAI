import chess
import chess.pgn

FILENAME = "dataset.pgn"


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
        # yield str(old_board), str(board)
        yield (old_board.fen(), board.fen()), move.uci()


def main():

    # iterate through each game from the dataset
    for i, game in enumerate(file_parser()):

        print(f"******************GAME {i+1}******************")

        # iterate through states tuples
        for s in game_states(game):
            print(s)

        # for debug purpose, stop at first iteration
        # if i == 0:
        #     break


if __name__ == '__main__':
    main()
