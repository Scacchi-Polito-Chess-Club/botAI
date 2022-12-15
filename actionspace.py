from itertools import product
from utils import *
from itertools import chain
import json

def main(): 
    # creating the grid
    letters = list("abcdefgh")
    numbers = list("12345678")
    # assigning to each element of the grid an integer from 0 to 63
    cells = sorted(map(lambda tuple: tuple[0]+tuple[1], product(letters, numbers)))
    position_dictionary = {
        cell: idx for idx, cell in enumerate(cells)
    }
    # there are 8 different paws. Initial position of pawn matters.
    pawns = []
    for letter in letters:
        pawns.append(Piece(name=f"pawn_{letter}"))
    # two different knights. Again, initial position of knight matters.
    knights = []
    for letter in ["b", "g"]:
        knights.append(Piece(name=f"knight_{letter}"))
    # two different bishops. Again, initial position of knight matters.
    bishops = []
    for letter in ["c", "f"]: 
        bishops.append(Piece(name=f"bishop_{letter}"))
    # two different rooks. Again, initial position of knight matters.
    rooks = []
    for letter in ["a", "h"]: 
        rooks.append(Piece(name=f"rook_{letter}"))
    # only one king and one queen
    king, queen = [Piece(name="king")], [Piece(name="queen")]
    # the whole set of 16 pieces each player is given at the beginning
    pieces16 = chain(
        pawns, knights, bishops, rooks, king, queen
    )
    # mapping all possible pieces in all possible positions (64 cells * 16 pieces = 1024 configs)
    piece_cell = map(
        lambda tup: (tup[0].name, tup[1]) , product(pieces16, cells)
        )
    # mapping each combination (piece/cell) to an integer from 0 to 1023
    actionspace = map(lambda tup: tup[0]+"/"+tup[1], piece_cell)
    actionspace = {
        action: idx for idx, action in enumerate(actionspace)
    }  
    # saving action space to a json file
    with open("actionspace.txt", "w") as output_file: 
        output_file.write(json.dumps(actionspace))

if __name__ == "__main__":
    main()