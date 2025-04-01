# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
import heapq
import math

# Constants
TARGET = Coord(0, 0)    # Set a default value for target, which will later be reassigned
BOARD_N = 11
MAX_DIST = 1000         # Max distance is actually smaller than this, but chose a simple number of simplicity
MAX_NUM_MOVES = 250     # maximum distance divided by 4, the tetromino size
P = 0.001               # Used to break ties in the heuristic function
TETROMINO_SIZE = 4 
VISITED = 1
UNVISITED = 0 


# Hardcoded tetrominoes
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
# Stores board and list of previous actions
class Node: 
    def __init__(self, board: dict[Coord, PlayerColor], prevActions: list[PlaceAction]):
        self.board = board
        self.prevActions = prevActions

    # Fixed - might be able to improve on it
    def __lt__(self, other):
        min1 = min(toBeFilled(self.board, TARGET, row=True), toBeFilled(self.board, TARGET, row=False))
        min2 = min(toBeFilled(other.board, TARGET, row=True), toBeFilled(other.board, TARGET, row=False))     
        return min1 < min2



# function that deletes full rows or columns and returns an updated board
def updateRowCol(board: dict[Coord, PlayerColor]):
    row2Replace = []
    col2Replace = []
    
    #find full rows
    for row in range(BOARD_N):
        foundEmpty = True
        for col in range(BOARD_N):
            # If it is empty
            if not board.get(Coord(row, col)): 
                foundEmpty = False
        if foundEmpty:
            row2Replace.append(row)
    
    #find full columns
    for col in range(BOARD_N):
        foundEmpty = True
        for row in range(BOARD_N):
            # If it is empty
            if not board.get(Coord(row, col)): 
                foundEmpty = False
        if foundEmpty:
            col2Replace.append(col)
    
    # If it a square in a full column or row, remove it
    for row in range(BOARD_N):
        for col in range(BOARD_N):
            if row in row2Replace or col in col2Replace:
                board.pop(Coord(row, col))



def search(
    board: dict[Coord, PlayerColor], 
    target: Coord
) -> list[PlaceAction] | None:

    # Set target
    TARGET = target

    # pre-stores distances to empty squares on target row/column
    distancesTo = {}
    for pos in range(BOARD_N):
        if not board.get(Coord(target.r, pos)):
            distancesTo[Coord(target.r, pos)] = bfs(board, Coord(target.r, pos))
        if not board.get(Coord(pos, target.c)):
            distancesTo[Coord(pos, target.c)] = bfs(board, Coord(pos, target.c))

    # If not reachable, enter repeated search
    # If there are no removable blocks, will return no solutions
    # Otherwise will identify another row(s)/column(s) to remove before target row/column
    if remaining_moves(board, target, distancesTo) >= MAX_NUM_MOVES:
            return repeatedSearch(board, target, 0, MAX_NUM_MOVES)
     

    # Create prioirty queue
    priorityQueue = []
    
    # Create starting node and push it to priority queue
    initialNode = Node(board, [])
    heapq.heappush(priorityQueue, (0, initialNode)) 

    # Implementation of A* search    
    while priorityQueue:
        # Pop next node with lowest heuristic value
        expandedNode = heapq.heappop(priorityQueue)
        print(render_board(expandedNode[1].board, target, ansi=True))
        # If target is removed
        if expandedNode and not expandedNode[1].board.get(target): 
            break
       
        adjacents = findAdjacent(expandedNode[1].board)
            
        # Generates all possible moves based on adjacent blocks to red and diffferent tetrominoes
        for adjacent in adjacents:
            for tetromino in tetrominoes: 
                if validMove(expandedNode[1].board, adjacent, tetromino):
                    for item in validMove(expandedNode[1].board, adjacent, tetromino):
                        
                        # Update the board and previous actions list
                        newBoard = updateBoard(expandedNode[1].board, item)
                        newList = expandedNode[1].prevActions.copy()
                        newList.append(item)
                        
                        # Create a new node and add it to the priority queue with its heuristic value
                        newNode = Node(newBoard, newList)
                        heuristicValue = heuristic(newNode, target, distancesTo)
                        heapq.heappush(priorityQueue, (heuristicValue, Node(newBoard, newList)))

    # If target is removed, return the previous actions of that node
    return expandedNode[1].prevActions
   


#***************************************************************************************************************#
# Heuristic-related functions
#***************************************************************************************************************#

# Calculates the heuristic function
def heuristic(node: Node, target: Coord, distancesTo):
    # If target is gone
    if not (node.board).get(target):
        return len(node.prevActions)
    
    #Estimates number of moves to fill in row/column
    movesLeft = remaining_moves(node.board, target, distancesTo)

    # Returns minimum number of moves to fill in row or column and adds to 
    # number of previous actions. The "P" value is used to break ties, 
    # and ensure that boards with fewer moves to complete are prioritised.   
    return (1+P)*movesLeft + len(node.prevActions) 

# predict remaining moves
def remaining_moves(board, target, distancesTo={}):
    # If distances to squares on target and row were not previously computed
    if not distancesTo:
        distancesTo = {}
        for pos in range(BOARD_N):
            distancesTo[Coord(target.r, pos)] = bfs(board, Coord(target.r, pos))
            distancesTo[Coord(pos, target.c)] = bfs(board, Coord(pos, target.c))   
    
    # Calculates estimated number of moves to fill in row/column
    rowValue = estimate_move(board, target, distancesTo, True)
    colValue = estimate_move(board, target, distancesTo, False)
    return min(rowValue, colValue)

# Calculates estimated minimum number of moves to fill in row/column
def estimate_move(board, target: Coord, distancesTo, isRow):
    # If target is gone
    if not board.get(target):
        return 0
    value = 0 
    # If filling in row     
    if isRow: 
        rowSegments = find_segments(board, target, row=True)
        for rowSegment in rowSegments:
            if rowSegment:
                value += dist_to_segment(board, target, rowSegment, True, distancesTo)    
    # If filling in column
    else:
        colSegments = find_segments(board, target, row=False)
        for colSegment in colSegments:
            if colSegment: 
                value += dist_to_segment(board, target, colSegment, False, distancesTo)
    return value            

# Completes bfs on the board and tracks shortest distance of every coordinate to a square
def bfs(board, square):
    visited = {}
    distances = {}
    for row in range(BOARD_N):
        for col in range(BOARD_N):
            visited[Coord(row,col)] = UNVISITED
            if (square.r==row and square.c==col):
                distances[Coord(row,col)] = 0
            else:
                distances[Coord(row,col)] = MAX_DIST   

    queue = []
    queue.append(square)
    visited[square] = VISITED
    while queue: 
        # pop first in queue
        coord = queue.pop(0)
        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        for direction in directions: 
            # If it is empty and unvisited
            if not board.get(coord + direction) and not visited[coord + direction] and 1 + distances[coord] < distances[coord + direction]:
                distances[coord + direction] = 1 + distances[coord]
                visited[coord + direction] = VISITED
                queue.append(coord + direction)  
    return distances              

#***************************************************************************************************************#
# Segments-related functions
#***************************************************************************************************************#

# Finds segments of row or column that are empty 
# Returns segments in a 2D array, with each 1D array storing starting pos and ending pos of segment
def find_segments(board, target, row: bool):
    segments = []
    segment = []
    count = 0
    # Loops through row or column twice to make sure we identify segments correctly
    for pos in range(BOARD_N*2):
        if row: 
            square = Coord(target.r, pos%BOARD_N)
            nextSquare = Coord(target.r, (pos+1)%BOARD_N)
            prevSquare = Coord(target.r, (pos-1)%BOARD_N)
        else:
            square = Coord(pos%11, target.c)
            nextSquare = Coord((pos+1)%BOARD_N, target.c)
            prevSquare = Coord((pos-1)%BOARD_N, target.c)
        if board.get(square):
            count += 1     
        # If previous square is filled and current square is not filled
        if board.get(prevSquare) and (not board.get(square)):
            segment.append(pos%BOARD_N)
        # if current square is not filled and next square is filled
        if not board.get(square) and board.get(nextSquare) and segment:
            segment.append(pos%BOARD_N)
            if segment not in segments:
                segments.append(segment)
            segment = []           
    
    # if completely filled for some reason
    if count==BOARD_N*2:
        return []   
    
    # If completely empty, return a segment representing entire row/column
    if not segments: 
        return [[1,0]]
    else: 
        return segments       


 # finds shortest distances to segments
def dist_to_segment(board, target, segment, row, distancesTo):
    if not segment: 
        return 0
    
    distances = []

    upperBound = segment[1] 
    lowerBound = segment[0]
    if segment[0] > segment[1]:
        upperBound = segment[1] + BOARD_N

    for pos in range(lowerBound, upperBound + 1):
        if row:
            square = Coord(target.r, pos%BOARD_N)
        else: 
            square = Coord(pos%BOARD_N, target.c)
        if not distancesTo.get(square):
            distancesTo[square] = bfs(board, square)    
        distances.append(closestSquare(board, square, distancesTo))
   
    return math.ceil((min(distances) + upperBound - lowerBound + 1)/float(TETROMINO_SIZE))   


# Finds distance between closest adjacent square to red and square on a segment on target row/column 
def closestSquare(board: dict[Coord, PlayerColor], target: Coord, distancesTo):
    adjacents = findAdjacent(board) 
    distances = []
    # Tracks distances between adjacent squares to red and square on target row or column
    for square in adjacents:
        distances.append((distancesTo[target])[square])
    # If there were no distances
    if not distances: 
        return 0    
    return min(distances)


#***************************************************************************************************************#
# Functions related to validity of moves and possible next moves to make from a board
#***************************************************************************************************************#

# Function to find all adjacent spaces to red tokens on board
# Returns a list of Coords, if there are no adjacent spaces to a red token returns None
def findAdjacent(board: dict[Coord, PlayerColor]):
    redSpaces = [] 
    adjacentSpaces = []

    # find all red tokens in board
    for coord, playercolor in board.items(): 
        if board.get(coord) and playercolor == PlayerColor.RED: 
            redSpaces.append(coord) 
            
    # find all adjacent spaces to red tokens
    for coord in redSpaces:
        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        for direction in directions: 
            if (not board.get(coord + direction)) and coord + direction not in adjacentSpaces:
                adjacentSpaces.append(coord + direction)
    return adjacentSpaces           


# Returns all possible positions that tetromino can be placed on square. Returns a 2D array. 
# Can change it to contain PlaceActions later. Keeping it as a 2D array so it's easier to print and debug.
def validMove(board, square: Coord, tetromino: [Coord]):
    total = []
    # If square is occupied, return
    if board.get(square):
        return []
    # Check if tetromino can be placed     
    for orientation in range(TETROMINO_SIZE):
        valid = True
        actions = []
        for piece in range(TETROMINO_SIZE):
            # Checks if block is filled. If filled, sets it to false
            if board.get(square - tetromino[orientation] + tetromino[piece]):
                valid = False
            else: 
                actions.append(square - tetromino[orientation] + tetromino[piece])
        if valid:
            total.append(PlaceAction(actions[0], actions[1], actions[2], actions[3]))        
    return total
                    

# Updates board based on tetrominos placed on board
def updateBoard(board, actions: PlaceAction):
    newBoard = board.copy()
    newBoard[actions.c1] = newBoard[actions.c2] = PlayerColor.RED
    newBoard[actions.c3] = newBoard[actions.c4] = PlayerColor.RED
    # Will remove a row or column if filled
    updateRowCol(newBoard)
    return newBoard  

# Returns number to be filled in row or column
def toBeFilled(board, target, row):
    count = 0
    for pos in range(BOARD_N):
        if row:
            square = Coord(target.r, pos)
        else: 
            square = Coord(pos, target.c)
        if not board.get(square):
            count += 1
    return count 



#***************************************************************************************************************#
# Functions for recursive case, where a different row/column has to be removed before the target row/column
# and where there is no solution
#***************************************************************************************************************#
def repeatedSearch(
    board: dict[Coord, PlayerColor], 
    target: Coord, count, depth
) -> list[PlaceAction] | None:
    if count > depth:
        return []

    removableList = uniqueBlueSquares(board)
    # If none can be removed, there is no solution
    if not removableList:
        return None

    queue = []
    for square in removableList:
    # If it is minimum moves then do it
        actions = search(board, square)
        newBoard2 = board.copy()
        
        # Update the board
        for action in actions: 
            newBoard2 = updateBoard(newBoard2, action) 
        newNode = Node(newBoard2, actions)
        numMoves = remaining_moves(newBoard2, target) 
        heapq.heappush(queue, (numMoves + len(newNode.prevActions) + 0.001*manhattan(target, square), newNode))

    
    while queue: 
        output = heapq.heappop(queue)
        if output[0] < MAX_NUM_MOVES: 
            return output[1].prevActions + search(output[1].board, target)
        else:
            if count < depth:
                if repeatedSearch(output[1].board, target, count+1, depth):
                    return output[1].prevActions + repeatedSearch(output[1].board, target, count+1, depth)
            else:
                return []       

# Find blue squares
def findBlueSquares(board):
    blueSquares = []
    for key, colour in board.items():
        if colour==PlayerColor.BLUE:
            blueSquares.append(key)
    return blueSquares        

# Generates a list of removable blue squares
def removeableBlueSquares(board, distance):
    blueSquares = findBlueSquares(board)
    removableList = []
    for blueSquare in blueSquares:
        for pos in range(BOARD_N):
            distance[Coord(blueSquare.r, pos)] = bfs(board, Coord(blueSquare.r, pos))
            distance[Coord(pos, blueSquare.c)] = bfs(board, Coord(pos, blueSquare.c))
        if remaining_moves(board, blueSquare, distance) < MAX_NUM_MOVES:
            removableList.append(blueSquare)
    return removableList

# Finds squares in rows or columns that require fewest moves to remove, as opposed to using all squares
def uniqueBlueSquares(board):
    distancesTo = {}
    removableList = removeableBlueSquares(board, distancesTo)
    if not removableList:
        return []
    minimum = MAX_NUM_MOVES
    newList = []
    square = Coord(0,0)
    # for rows find easiest blue squares to remove
    for row in range(BOARD_N):
        valid = False
        for col in range(BOARD_N):
            if Coord(row, col) in removableList:
                value = estimate_move(board, Coord(row, col), distancesTo, True)
                if value < minimum:
                    minimum = value
                    square = Coord(row, col)
                    valid = True
        if valid: 
            newList.append(square)

    # For columns, find easiest ones to remove
    for col in range(BOARD_N):
        valid = False
        for row in range(BOARD_N):
            if Coord(row, col) in removableList:
                value = estimate_move(board, Coord(row, col), distancesTo, False)
                if value < minimum:
                    minimum = value
                    square = Coord(row, col)
                    valid = True
        if valid: 
            newList.append(square) 
    return newList           

# Calculates manhattan distance between two squares taking into account wrapping of board
def manhattan(target, square):
    height = abs(target.r - square.r)
    width = abs(target.c - square.c)
    if height > BOARD_N//2:
        height = BOARD_N- max(target.r, square.r) + min(target.r, square.r)
    if width > BOARD_N//2:
        width = BOARD_N - max(target.c, square.c) + min(target.c, square.c)
    return math.ceil((width + height) / float(TETROMINO_SIZE)) 


