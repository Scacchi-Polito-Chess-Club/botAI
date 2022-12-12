import chess
import chess.pgn

FILENAME = "dataset.pgn"


def file_parser(fname: str = FILENAME) -> chess.pgn.Game:
    """
    This function yields one game at a time, taken from the file @fname.

    :param fname: the name of the pgn dataset file
    :return: one game at a time
    """
    with open(fname) as f:
        while True:
            try:
                game = chess.pgn.read_game(f)
                yield game
            except Exception as e:
                print(e)


def game_states(game: chess.pgn.Game) -> tuple[str, str]:
    """
    This function yields one tuple at a time in the form (s_t, s_t+1)

    :param game: the game taken from the database (class chess.pgn.Game)
    :return: the tuple (s_t, s_t+1)
    """
    board = chess.Board()
    for i, move in enumerate(game.mainline_moves()):
        old_board = board.copy(stack=False)
        board.push(move)
        # yield str(old_board), str(board)
        yield old_board.fen(), board.fen()


def main():
    for i, game in enumerate(file_parser()):

        print(f"******************GAME {i+1}******************")

        for s in game_states(game):
            print(s)

        if i == 0:
            break


if __name__ == '__main__':
    main()
