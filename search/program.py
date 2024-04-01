# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
import heapq
import math

TARGET = Coord(0, 0)

def manhattan(target, square):
    height = abs(target.r - square.r)
    width = abs(target.c - square.c)
    if height > 5:
        height = 11 - max(target.r, square.r) + min(target.r, square.r)
    if width > 5:
        width = 11 - max(target.c, square.c) + min(target.c, square.c)
    return math.ceil((width + height) / 4.0) 

# For segments, instead of just considering position
def manhattan2(target, square):
    width = abs(target.c - square.c)
    if width > 5:
        width = (target.r - 11) + square.c
    return math.ceil((width) / 4.0)  


# Calculates distance based on obstacles, returns shortest path 
# guaranteed to have a bug 
def bfs(board, square, target):
    queue = []
    defaultV = 0
    defaultC = -1
    coordKeys = [Coord(r,c) for r in range(11) for c in range(11)] #not sure if this works

    visited = dict.fromkeys(coordKeys, defaultV)
    counts = dict.fromkeys(coordKeys, defaultC)

    queue.append(square)
    counts[square] = 0
    while queue: 
        coord = queue.pop(0)
        if coord == target: # stop searching if found target
            return counts
        #printBFS(coord)
        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        # if it hasn't been visited yet
        if visited[coord]==0:
            visited[coord]= 1
            # checking adjacent coords
            for direction in directions: 
                # if it is not visited
                if visited[coord + direction]==0:
                    counts[coord + direction] = 1 + counts[coord]
                    current = coord + direction
                    if isEmpty(board, coord+direction):
                        queue.append(coord + direction)
        #print("current: ")
        #printBFS(counts[coord+direction])
    return counts   

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
        return math.ceil(min1/4.0) - len(self.prevActions) < math.ceil(min2/4.0) - len(other.prevActions)
        #return min1*22 + dist(self.board, TARGET) < min2*22 + dist(other.board, TARGET) 



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
    # Set target
    TARGET = target

    priorityQueue = []
    # To insert into priority queue, 
    # heapq.heappush(priorityQueue, (priority, Node))
    # To remove, heapq.heappop(priorityQueue)[1]

    bfs(board, Coord(2,5), target)

    # Create starting node
    initialNode = Node(board, [])
    heapq.heappush(priorityQueue, (0, initialNode)) 

    # Will clean up this code, just want to get something working first
    count = 0
    # Implementation of search
    # 
    generatedCount = 1
    while priorityQueue:
        expandedNode = heapq.heappop(priorityQueue)
        count += 1
        print(render_board(expandedNode[1].board, target, ansi=False))
        if expandedNode and checkTarget(expandedNode[1].board, target): 
            print(render_board(expandedNode[1].board, target, ansi=True))
            printPlaceAction(expandedNode[1].prevActions)
            print("expanded nodes: " + str(count))
            print("generated nodes: " + str(generatedCount))
            break
        adjacents = findAdjacent(expandedNode[1].board)
        print(heuristic(expandedNode[1], adjacents, target))
        print(toBeFilled(expandedNode[1].board, target, False))
        if not adjacents:
            break
        # Need to fix issue with adjacent squares and tetrominoes loop
        for adjacent in adjacents:
            for tetromino in tetrominoes: 
                if validMove(expandedNode[1].board, adjacent, tetromino):
                    for item in validMove(expandedNode[1].board, adjacent, tetromino):
                        generatedCount += 1
                        newBoard = updateBoard(expandedNode[1].board, item)
                        newList = expandedNode[1].prevActions.copy()
                        newList.append(item)
                        newNode = Node(newBoard, newList)
                        heuristicValue = heuristic(newNode, adjacents, target)
                        heapq.heappush(priorityQueue, (heuristicValue, Node(newBoard, newList)))

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!

    print(render_board(board, target, ansi=False))

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


# This function is very buggy
def find_segments(board, target, row: bool):
    segments = []
    segment = []
    initialSegment = []
    for pos in range(11):
        if row: 
            square = Coord(target.r, pos%11)
            nextSquare = Coord(target.r, (pos+1)%11)
            
        else:
            square = Coord(pos%11, target.c)
            nextSquare = Coord((pos+1)%11, target.c)    
        
        # if this is the first
        if not pos: 
            if not board.get(square):
                initialSegment.append(pos)
            elif not board.get(nextSquare):
                segment.append(pos+1)

         
        if len(initialSegment)==1 and not board.get(square) and board.get(nextSquare):
            initialSegment.append(pos)
        elif pos:
            # if current square is not empty and next square is empty
            if board.get(square) and not board.get(nextSquare):
                segment.append(pos+1)
            # if current square is empty and next square is not empty
            elif not board.get(square) and board.get(nextSquare):
                segment.append(pos)
                segments.append(segment)
                segment = []
            else:
                continue
        else:
            continue        

    if row: 
        firstSquare = Coord(target.r, 0)
        lastSquare = Coord(target.r, 10)
    else:
        firstSquare = Coord(0, target.c)
        lastSquare = Coord(10, target.c) 
    # if first square and last square are both empty 
    if not board.get(firstSquare) and not board.get(lastSquare):
        segment.append(initialSegment[1])
        segments.append(segment)
    elif initialSegment:
        segments.append(initialSegment) 
    

    return segments    


 # for rows and columns
def dist_to_segment2(board, target, segment, row):
    distances = []

    upperBound = segment[1] 
    lowerBound = segment[0]
    if segment[0] > segment[1]:
        upperBound = segment[1] + 11

    for pos in range(lowerBound, upperBound + 1):
        if row:
            square = Coord(target.r, pos%11)
        else: 
            square = Coord(pos%11, target.c)
        distances.append(closestSquare(board, square))
    return math.ceil((min(distances) + upperBound - lowerBound+1)/4.0) 




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
    rowSegments = find_segments(node.board, target, row=True)
    colSegments = find_segments(node.board, target, row=False)
    rowValue, colValue = 0, 0
    for rowSegment in rowSegments:
        if rowSegment:
            rowValue += dist_to_segment2(node.board, target, rowSegment, True)
    for colSegment in colSegments:
        if colSegment: 
           colValue += dist_to_segment2(node.board, target, colSegment, False)
    
    return min(rowValue, colValue) + len(node.prevActions)    
    
    
    #segments = find_col_segments(node.board, target)
    #value = 0
    #for segment in segments:
    #    value += dist_to_segment(node.board, target, segment)
    #return value + len(node.prevActions)
    #return closestSquare2(node.board, target) + len(node.prevActions) + numInColFilled(node.board, target) // 4
    #return closestSquare(node.board, target) + len(node.prevActions) #+ numInColFilled(node.board, target) #1128
    
# Finds distance between closest adjacent square to red and target   
def closestSquare(board: dict[Coord, PlayerColor], target: Coord):
    adjacents = findAdjacent(board) 
    # Will fix this later to not use an array, but keeping it here bcuz it's quick and easy
    distances = []
    for square in adjacents:
        distances.append(manhattan(square, target))
    if not distances: 
        return 0    
    return math.ceil(min(distances) / 4.0)


## different version
## more efficient, currently only for column
def closestSquare2(board, target):
    adjacents = findAdjacent(board)
    distances = []
    for square in adjacents: 
        distances.append(manhattan2(square, target))
    return math.ceil(min(distances) / 4.0)


def checkTarget(board: dict[Coord, PlayerColor], target: Coord):
    # If target is removed
    if not board.get(target):
        return True
    row = True
    column = True
    for pos in range(11):
        # If it is empty
        if not board.get(Coord(target.r, pos)):
            row = False
        if not board.get(Coord(pos, target.c)):
            column = False    
    return column or row
        



# Function to find all adjacent spaces to red tokens on board
# Returns a list of Coords, if there are no adjacent spaces to a red token returns None
def findAdjacent(board: dict[Coord, PlayerColor]):
    redSpaces = [] 
    adjacentSpaces = []

    # find all red tokens in board
    for coord, playercolor in board.items(): 
        if board.get(coord) and playercolor.RED == PlayerColor.RED: 
            redSpaces.append(coord) 
            
    # find all adjacent spaces to red tokens
    for coord in redSpaces:
        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        for direction in directions: 
            if board.get(coord + direction) and coord + direction not in adjacentSpaces:
                adjacentSpaces.append(coord + direction)
    return adjacentSpaces 


# function that deletes full rows or columns and returns an updated board
# ROUGH DRAFT function is very tedious
def updateRowCol(board: dict[Coord, PlayerColor]):
    foundEmpty = False
    row2Replace = []
    col2Replace = []
    
    #find full rows
    for row in range(11):
        for col in range(11):
            if isEmpty(board, Coord(row,col)): 
                foundEmpty = True
                continue 
        if not foundEmpty and row not in row2Replace: 
            row2Replace.append(row)
            foundEmpty = False

    foundEmpty = False # reset

    # need to somehow combine finding full row and columns so only one nested loop in function
    # find full columns
    for col in range(11):
        for row in range(11):
            if isEmpty(board, Coord(row,col)):
                foundEmpty = True
                continue 
        if not foundEmpty and col not in col2Replace: 
            col2Replace.append(col)
            foundEmpty = False

    # delete full columns and rows in board
    for coord, playercolor in board.items():
        if coord.r in row2Replace or coord.c in col2Replace:
            board.pop(coord)
    

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
# Using this function in findAdjacent so adding it in this branch
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

# for debugging
def printBFS(square):
    print(square)

# more debugging
def printDict(board):
    print(board)

# 26 nodes now explored for test case 1, takes less than 3 seconds 