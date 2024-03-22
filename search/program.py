# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction
from .utils import render_board
import heapq


tetromino = [(0,0), (1, 0), (2, 0), (3, 0)]
# Basic structure of a node to be added to priority queue
# Still to be modified as going along
class Node: 
    def __init__(self, board: dict[Coord, PlayerColor], prevActions: list[PlaceAction]):
        self.board = board
        self.prevActions = prevActions



def search(
    board: dict[Coord, PlayerColor], 
    target: Coord
) -> list[PlaceAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `PlayerColor` instances.  
        `target`: the target BLUE coordinate to remove from the board.
    
    Returns:
        A list of "place actions" as PlaceAction instances, or `None` if no
        solution is possible.
    """
    priorityQueue = []
    # To insert into priority queue, 
    # heapq.heappush(priorityQueue, (priority, Node))
    # To remove, heapq.heappop(priorityQueue)[1]

    # Create starting node
    initialNode = Node(board, 4)
    heapq.heappush(priorityQueue, (0, initialNode)) 

    print(isEmpty(board, Coord(1, 0)))

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, target, ansi=True))


    # Do some impressive AI stuff here to find the solution...
    # ...
    # ... (your solution goes here!)
    # ...
    
    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return [
        PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
        PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
        PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    ]

# Needs to be fixed, currently only doing it for one type of tetromino
# Checks if tetromino can be placed on a particular square in board
def validMove(board, square: Coord):
    # If square is occupied, return
    if not isEmpty(board, square):
        return False 
    # Check if tetromino can be placed      
    for i in range(4):
        for j in range(4):
            if i==j: 
                continue
            elif isEmpty(board, square.__sub__tetromino[i]):
                return True
    return True
                



# Checks if square on board is unoccupied
def isEmpty(board: dict[Coord, PlayerColor], square: Coord):
    # If occupied
    if board.get(square, None):
        return False
    else: 
        return True



