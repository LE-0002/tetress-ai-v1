# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
import heapq
import math

TARGET = Coord(9, 8)

# With wrapping included now
def manhattan(target, square):
    height = abs(target.r - square.r)
    width = abs(target.c - square.c)
    if abs(target.r - square.r) > 5:
        height = (target.r - 11) + square.r
    if width > 5:
        width = (target.c - 11) + square.c
    return math.ceil((width + height) / 4.0) 

# For segments, instead of just considering position
def manhattan2(target, square):
    width = abs(target.c - square.c)
    if width > 5:
        width = (target.r - 11) + square.c
    return math.ceil((width) / 4.0)              


# Hardcoded the tetrominoes - not sure if this is best practice or whether
# I should use rotation instead
tetrominoes = [
    [Coord(0,0), Coord(0,1), Coord(0, 2), Coord(0, 3)], # I
    [Coord(0,0), Coord(1, 0), Coord(2, 0), Coord(3, 0)], # I
    [Coord(0, 0), Coord(0, 1), Coord(1, 0), Coord(1, 1)], # O
    [Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(1, 1)], # T
    [Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(1, 10)], # T
    [Coord(1, 0), Coord(1, 1), Coord(1, 2), Coord(0, 1)], # T
    [Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(1, 1)], # T
    [Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(2, 10)], # J
    [Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(1, 2)], # J
    [Coord(0, 0), Coord(0, 1), Coord(1, 0), Coord(2, 0)], # J
    [Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(1, 2)], # J
    [Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(2, 1)], # L
    [Coord(0, 0), Coord(0, 1), Coord(0, 2), Coord(1, 0)], # L
    [Coord(0, 0), Coord(0, 1), Coord(1, 1), Coord(2, 1)], # L
    [Coord(0, 2), Coord(1, 0), Coord(1, 1), Coord(1, 2)], # L
    [Coord(0, 0), Coord(0, 1), Coord(1, 1), Coord(1, 2)], # Z
    [Coord(0, 1), Coord(1, 0), Coord(1, 1), Coord(2, 0)], # Z
    [Coord(0, 1), Coord(0, 2), Coord(1, 0), Coord(1, 1)], # S
    [Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(2, 1)] # S
]

# Basic structure of a node to be added to priority queue
# Still to be modified as going along
class Node: 
    def __init__(self, board: dict[Coord, PlayerColor], prevActions: list[PlaceAction]):
        self.board = board
        self.prevActions = prevActions

    # Fixed - might be able to improve on it
    def __lt__(self, other):
        min1 = min(toBeFilled(self.board, TARGET, True), toBeFilled(self.board, TARGET, False))
        min2 = min(toBeFilled(other.board, TARGET, True), toBeFilled(other.board, TARGET, False))
        return min1 < min2


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
    initialNode = Node(board, [])
    heapq.heappush(priorityQueue, (0, initialNode)) 

    # Will clean up this code, just want to get something working first
    count = 0
    # Implementation of search
    # 
    while priorityQueue:
        expandedNode = heapq.heappop(priorityQueue)
        count += 1
        #print(render_board(expandedNode[1].board, target, ansi=True)) 
        if expandedNode and checkTarget(expandedNode[1].board, target, False): 
            #print(render_board(expandedNode[1].board, target, ansi=True))
            printPlaceAction(expandedNode[1].prevActions)
            print(count)
            break
        adjacents = findAdjacent(expandedNode[1].board)
        if not adjacents:
            break
        # Need to fix issue with adjacent squares and tetrominoes loop
        for adjacent in adjacents:
            for tetromino in tetrominoes: 
                if validMove(expandedNode[1].board, adjacent, tetromino):
                    for item in validMove(expandedNode[1].board, adjacent, tetromino):
                        newBoard = updateBoard(expandedNode[1].board, item)
                        heuristicValue = heuristic(expandedNode[1], adjacents, target)
                        newList = expandedNode[1].prevActions.copy()
                        newList.append(item)
                        heapq.heappush(priorityQueue, (heuristicValue, Node(newBoard, newList)))
    
    # This is just for debugging
    #print(validMove(board, Coord(7, 0), tetrominoes[0]))
    #for tetromino in tetrominoes:
       # if validMove(board, Coord(7, 0), tetromino):
       #     for item in validMove(board, Coord(7, 0), tetromino):
       #         newBoard = updateBoard(board, item)
      #          heapq.heappush(priorityQueue, (0, Node(newBoard, [])))
      #          print(render_board(newBoard, target, ansi=True))
    #print(len(priorityQueue))
   
    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    #print(render_board(board, target, ansi=True))

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


def find_segments(board, target, row: bool):
    segments = []
    segment = []
    # Default value

    # will fix magic numbers
    for pos in range(22):
        if row: 
            square = Coord(target.r, pos%11)
            prevSquare = Coord(target.r, (pos-1)%11)
        else:
            square = Coord(pos%11, target.c)
            prevSquare = Coord((pos-1)%11, target.c)    
        # if square is empty and previous square is not empty
        if not board.get(square) and board.get(prevSquare):
            segment.append(pos%11)
        # if previous square was empty and current square is not empty
        elif board.get(square) and not board.get(prevSquare):
            segment.append((pos-1)%11)
            if segment not in segments:
                segments.append(segment)
            segment = []    
        else:
            continue
    return segments                   


 # for rows and columns
def dist_to_segment2(board, target, segment, row):
    distances = []
    # WIll be a bug here
    for pos in range(segment[0], segment[1] + 1):
        if row:
            square = Coord(target.r, pos)
        else: 
            square = Coord(pos, target.c)
        distances.append(closestSquare(board, square))
    return (min(distances) + segment[1] - segment[0] + 1)//4 + (min(distances) + segment[1] - segment[0] + 1)%4
   




# Returns number to be filled in row or column
def toBeFilled(board, target, row):
    count = 0
    for pos in range(11):
        if row:
            square = Coord(target.r, pos)
        else: 
            square = Coord(pos, target.c)
        if not board.get(square):
            count += 1
    return count        
     


def heuristic(node: Node, adjacentSpaces: [Coord], target: Coord):
    segments = find_segments(node.board, target, False)
    value = 0
    for segment in segments:
        value += dist_to_segment2(node.board, target, segment, False)
    return value + len(node.prevActions)    
    
    
    #segments = find_col_segments(node.board, target)
    #value = 0
    #for segment in segments:
    #    value += dist_to_segment(node.board, target, segment)
    #return value + len(node.prevActions)
    #return closestSquare2(node.board, target) + len(node.prevActions) + numInColFilled(node.board, target) // 4
    #return closestSquare(node.board, target) + len(node.prevActions) #+ numInColFilled(node.board, target) #1128
    
# Finds distance between closest adjacent square to red and target
# Not yet considering wrapping of board for simplicity    
def closestSquare(board: dict[Coord, PlayerColor], target: Coord):
    adjacents = findAdjacent(board) 
    # Will fix this later to not use an array, but keeping it here bcuz it's quick and easy
    distances = []
    for square in adjacents:
        distances.append(manhattan(square, target))
    return math.ceil(min(distances) / 4.0)


## different version
## more efficient, currently only for column
def closestSquare2(board, target):
    adjacents = findAdjacent(board)
    distances = []
    for square in adjacents: 
        distances.append(manhattan2(square, target))
    return math.ceil(min(distances) / 4.0)

# Checks if target is removed or entire row or column is filled
def checkTarget(board: dict[Coord, PlayerColor], target: Coord, row: bool):
    # If target is removed
    if not board.get(target):
        return True
    
    for pos in range(11):
        # If it is empty
        if row:
            if not board.get(Coord(target.r, pos)):
                return False
        else: 
            if not board.get(Coord(pos, target.c)):
                return False        

    return True    




# Function to find all adjacent spaces to red tokens on board
# Returns a list of Coords, if there are no adjacent spaces to a red token returns None
def findAdjacent(board: dict[Coord, PlayerColor]):
    redSpaces = [] 
    adjacentSpaces = []

    # find all red tokens in board
    for coord, playercolor in board.items(): 
        if board.get(coord, None) and playercolor == PlayerColor.RED: 
            redSpaces.append(coord) 
            
    # find all adjacent spaces to red tokens
    for coord in redSpaces:
        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        for direction in directions: 
            if (isEmpty(board, coord + direction)) and coord + direction not in adjacentSpaces:
                adjacentSpaces.append(coord + direction)
    return adjacentSpaces           



def updateBoard(board, actions: PlaceAction):
    newBoard = board.copy()
    newBoard[actions.c1] = newBoard[actions.c2] = PlayerColor.RED
    newBoard[actions.c3] = newBoard[actions.c4] = PlayerColor.RED
    return newBoard 

# Returns all possible positions that tetromino can be placed on square. Returns a 2D array. 
# Can change it to contain PlaceActions later. Keeping it as a 2D array so it's easier to print and debug.
def validMove(board, square: Coord, tetromino: [Coord]):
    total = []
    # If square is occupied, return
    if not isEmpty(board, square):
        return []
    # Check if tetromino can be placed   
    # i represents orientation
    # j represents piece filled   
    for i in range(4):
        valid = True
        actions = []
        for j in range(4):
            # Checks if block is filled. If filled, sets it to false
            if not isEmpty(board, square - tetromino[i] + tetromino[j]):
                valid = False
            # If block is blue, set it to false    
            elif board.get(square - tetromino[i] + tetromino[j]) == PlayerColor.BLUE:
                valid = False
            else: 
                actions.append(square - tetromino[i] + tetromino[j])
        if valid:
            total.append(PlaceAction(actions[0], actions[1], actions[2], actions[3]))        
    return total
                



# Checks if square on board is unoccupied
def isEmpty(board: dict[Coord, PlayerColor], square: Coord):
    # If occupied
    if board.get(square, None):
        return False
    else: 
        return True



# For debugging - prints out a list of placeActions, easier to read
def printPlaceAction(items: [PlaceAction]):
    for item in items: 
        print(item.c1, item.c2, item.c3, item.c4)

# For debugging
def printAdjacentSquares(values):
    for coord in values:
        print(coord)



# 26 nodes now explored for test case 1, takes less than 3 seconds 
