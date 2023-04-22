import chess


def get_move(board1, board2):
    # set1 and set2 contain the sets of the position before and after the move. The itmes look like this:
    # (square1, piece1), (square2, piece2), ...:
    # (1, r), (2, n), (3, b), ...
    # 
    # diff contains the xor between the two sets that correspond to the squares that changed between the two positions.
    # For example after pawn from e2 to e4 diff will be a set that contains:
    # (e2, p), (e4, p) 
    set1 = set(board1.piece_map().items())
    set2 = set(board2.piece_map().items())
    diff = set1 ^ set2
    move = chess.Move(0, 0)

    # dictionaries of squares that changed their status after the move
    # from_posiition contains the intersection between the difference and the starting position, this will
    # generate a dictionary that contains the squares of the starting position that changed after the move
    # to_position contains the intersection between the difference and the arriving position, this will
    # generate a dictionary that contains the squares of the arriving position that changed after the move
    # the dictionaries are of the type: 
    # (key, value): (piece, square)
    from_position = dict((piece.symbol(), square) for square, piece in set1.intersection(diff))
    to_position = dict((piece.symbol(), square) for square, piece in set2.intersection(diff))

    # here we separate two big cases:
    # if the squares that changed between the two positions are 4 it means that the only possible move which was
    # played has to be a castle (long or short). Otherwise we can assure that the move was not a castle.
    if len(diff) != 4:
        # to_position contains only one square, which is the one on which the piece arrives after the move
        # since we know the type of the piece type now we can search for the specific piece into the
        # starting_position so that we know then the square from where it starts.
        to_tuple = to_position.popitem()
        piece = to_tuple[0]
        to_square = to_tuple[1]
        from_square = from_position.get(piece)

        # since the from_square is retrieved by looking at the piece type it is possible that from_square
        # is None, in this case it means a promotion happened, which also implies that this is not an enpassant
        if from_square == None:
            # it means there's a promotion
            # it means it's not enpassant

            # here we can say the followings:
            # we are in a case in which the move is a simple move from a square to another or a capture
            # in this cases from_position just contains two squares (the start and the arrive)
            # we proceed to pop the items until the square is different from the arrive, we can then
            # be sure that we get the starting square
            from_tuple = from_position.popitem()
            if from_tuple[1] == to_square:
                from_tuple = from_position.popitem()
            from_square = from_tuple[1]

            # we assign the promotion
            move.promotion = chess.Piece.from_symbol(piece).piece_type
    else:
        # in this case we're handling castling.
        # in both from_square and to_square there are just two squares, in which one of them contains a king (k)
        from_square = from_position.get('K')
        to_square = to_position.get('K')

    move.from_square = from_square
    move.to_square = to_square

    return move

if __name__ == '__main__':
    # std move
    b1 = chess.Board()
    b2 = chess.Board("rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1")
    print(get_move(b1, b2))

    # capture
    b1 = chess.Board("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
    b2 = chess.Board("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")
    print(get_move(b1, b2))

    # enpassant
    b1 = chess.Board("rnbqkbnr/p1pp1ppp/1p6/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3")
    b2 = chess.Board("rnbqkbnr/p1pp1ppp/1p2P3/8/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 3")
    print(get_move(b1, b2))
    
    # short castle
    b1 = chess.Board("rnbq1bnr/ppppk1pp/4pp2/8/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQ - 2 4")
    b2 = chess.Board("rnbq1bnr/ppppk1pp/4pp2/8/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b - - 3 4")
    print(get_move(b1, b2))

    # long castle
    b1 = chess.Board("rnbq1bnr/pp2kppp/2ppp3/8/3P4/3QB3/PPPNPPPP/R3KBNR w KQ - 2 5")
    b2 = chess.Board("rnbq1bnr/pp2kppp/2ppp3/8/3P4/3QB3/PPPNPPPP/2KR1BNR b - - 3 5")
    print(get_move(b1, b2))

    # promotion
    b1 = chess.Board("rnbq1bnr/ppppk1P1/7p/8/8/8/PPP1PPPP/RNBQKBNR w KQ - 1 5")
    b2 = chess.Board("rnbq1bnQ/ppppk3/7p/8/8/8/PPP1PPPP/RNBQKBNR b KQ - 0 5")
    print(get_move(b1, b2))