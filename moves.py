import chess

def GetMoveFEN(fen1, fen2):
    board1 = chess.Board(fen1)
    board2 = chess.Board(fen2)
    return getMove(board1, board2)

def GetMove(board1, board2):
    set1 = set(board1.piece_map().items())
    set2 = set(board2.piece_map().items())
    diff = set1 ^ set2
    move = chess.Move(0, 0)

    # dictionaries of squares that changed their status during the move
    fromPosition = dict((piece.symbol(), square) for square, piece in set1.intersection(diff))
    toPosition = dict((piece.symbol(), square) for square, piece in set2.intersection(diff))

    if len(diff) != 4:
        toTuple = toPosition.popitem()
        piece = toTuple[0]
        toSquare = toTuple[1]
        fromSquare = fromPosition.get(piece)

        if fromSquare == None:
            # it means there's a promotion
            # it means it's not enpassant
            fromTuple = fromPosition.popitem()
            if fromTuple[1] == toSquare:
                fromTuple = fromPosition.popitem()
            fromSquare = fromTuple[1]
            move.promotion = chess.Piece.from_symbol(piece).piece_type
    else:
        # castling
        fromSquare = fromPosition.get('K')
        if fromSquare == None:
            fromSquare = fromPosition.get('k')

        toSquare = toPosition.get('K')
        if toSquare == None:
            toSquare = toPosition.get('k')

    move.from_square = fromSquare
    move.to_square = toSquare

    return move

if __name__ == '__main__':
    # std move
    b1 = chess.Board()
    b2 = chess.Board("rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1")
    print(GetMove(b1, b2))

    # capture
    b1 = chess.Board("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
    b2 = chess.Board("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")
    print(GetMove(b1, b2))

    # enpassant
    b1 = chess.Board("rnbqkbnr/p1pp1ppp/1p6/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3")
    b2 = chess.Board("rnbqkbnr/p1pp1ppp/1p2P3/8/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 3")
    print(GetMove(b1, b2))
    
    # short castle
    b1 = chess.Board("rnbq1bnr/ppppk1pp/4pp2/8/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQ - 2 4")
    b2 = chess.Board("rnbq1bnr/ppppk1pp/4pp2/8/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b - - 3 4")
    print(GetMove(b1, b2))

    # long castle
    b1 = chess.Board("rnbq1bnr/pp2kppp/2ppp3/8/3P4/3QB3/PPPNPPPP/R3KBNR w KQ - 2 5")
    b2 = chess.Board("rnbq1bnr/pp2kppp/2ppp3/8/3P4/3QB3/PPPNPPPP/2KR1BNR b - - 3 5")
    print(GetMove(b1, b2))

    # promotion
    b1 = chess.Board("rnbq1bnr/ppppk1P1/7p/8/8/8/PPP1PPPP/RNBQKBNR w KQ - 1 5")
    b2 = chess.Board("rnbq1bnQ/ppppk3/7p/8/8/8/PPP1PPPP/RNBQKBNR b KQ - 0 5")
    print(GetMove(b1, b2))