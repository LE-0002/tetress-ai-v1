# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
import heapq
import math

TARGET = Coord(0, 0)

visited1 = []
firstTarget = 0
TARGET1 = Coord(0,0)
firstBoard = {}

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
# Might need modifications
def djikstra(board, square):
    dist = {}
    visited = {}
   
    for i in range(11):
        for j in range(11):
            dist[Coord(i, j)] = 1000
            if Coord(i,j) in board.keys():
                visited[Coord(i,j)]=1
            else: 
                visited[Coord(i,j)] = 0    

    dist[square] = 0
    pq = []
    # initialise the heap
    for i in range(11):
        for j in range(11):
            heapq.heappush(pq, (dist[Coord(i, j)], Coord(i, j)))

    
    while pq:
        coord = heapq.heappop(pq)[1]
        if not visited[coord]:
            visited[coord] = 1
            directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
            for direction in directions:
                newSquare = coord + direction
                # If square is empty and coord also empty
                if ((not board.get(newSquare)) and (not board.get(coord)) and dist[coord] + 1 < dist[newSquare]): 
                    dist[newSquare] = dist[coord] + 1
                    heapq.heappush(pq, (dist[newSquare], newSquare))
                
    return dist


# function that deletes full rows or columns and returns an updated board
def updateRowCol(board: dict[Coord, PlayerColor]):
    row2Replace = []
    col2Replace = []
    
    #find full rows
    for row in range(11):
        foundEmpty = True
        for col in range(11):
            # If it is empty
            if not board.get(Coord(row, col)): 
                foundEmpty = False
        if foundEmpty:
            row2Replace.append(row)
    
    #find full columns
    for col in range(11):
        foundEmpty = True
        for row in range(11):
            # If it is empty
            if not board.get(Coord(row, col)): 
                foundEmpty = False
        if foundEmpty:
            col2Replace.append(col)
    
    for row in range(11):
        for col in range(11):
            if row in row2Replace or col in col2Replace:
                board.pop(Coord(row, col))
               
    
times = 0
current = 0  
minimum = 1000  

def search(
    board: dict[Coord, PlayerColor], 
    target: Coord
) -> list[PlaceAction] | None:
    
    board11 = djikstra(board, Coord(0,0))
    board12 = bfs(board, Coord(0,0))

    checker = True
    for i in range(11):
        for j in range(11):
            if board11[Coord(i,j)]==board12[Coord(i,j)]:
                # Add comment
                checker = True
            else:
                print(False) 
                return
    print(True)
    return         
            
    
    for key1, value1 in djikstra(board, target):
        print(str(key1) + ":" + str(value1))
    return    
    
    for key, value in bfs2(board, target).items():
        print(str(key) + ":" + str(board11[key]) + " vs " + str(value))  
    return     
    
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
    print("map11111111111111111111111111")
    print(render_board(board, ansi=True))
    print("map22222222222222222222222222")
    
    # Set target
    TARGET = target
    print(TARGET)


    distancesTo = {}
    for pos in range(11):
        distancesTo[Coord(target.r, pos)] = djikstra(board, Coord(target.r, pos))
        distancesTo[Coord(pos, target.c)] = djikstra(board, Coord(pos, target.c))
    

    # Will make this more efficient, can change it, leaving it now to test

    
    # If not reachable
    if remaining_moves(board, target, distancesTo) >= 250:
        removableList = removeableBlueSquares(board)
        if not len(removableList):
            return None
        global minimum
        sequence = []
        for square in removableList:
            global current
            print("Mannnnnnnnnnnnnnnnnn")
            print(current)
            print(square)
            if remaining_moves(board, square) <= minimum:
                actions = search(board, square)
                newBoard2 = board.copy()
                for action in actions: 
                    newBoard2 = updateBoard(newBoard2, action)  
                numMoves = remaining_moves(newBoard2, target) 
                current += numMoves + len(actions)
                print("numMoves" + str(numMoves))  
                # If predicted next moves are less than current minimum
                if current < minimum:
                    if numMoves <= 250:
                        current = 0
                    newActions = actions + search(newBoard2, target)
                    if len(newActions) < minimum: 
                        minimum = len(newActions)
                        sequence = newActions
        print("*********************")
        board5 = board.copy()
        print(render_board(board, ansi=True))
        for action in sequence: 
            board5 = updateBoard(board5, action)
            print(render_board(updateBoard(board5, action), ansi=True))
        
        return sequence        
    
    


    priorityQueue = []


    # Create starting node
    initialNode = Node(board, [])
    heapq.heappush(priorityQueue, (0, initialNode)) 

    count = 0
    # Implementation of search
    
     
    generatedCount = 1
    while priorityQueue:
        expandedNode = heapq.heappop(priorityQueue)
        count += 1
        print(render_board(expandedNode[1].board, target, ansi=True))
        if expandedNode and checkTarget(expandedNode[1].board, target): 
            print("expanded nodes: " + str(count))
            print("generated nodes: " + str(generatedCount))
            break
        adjacents = findAdjacent(expandedNode[1].board)
       
        if not adjacents:
            break
            

        for adjacent in adjacents:
            for tetromino in tetrominoes: 
                if validMove(expandedNode[1].board, adjacent, tetromino):
                    for item in validMove(expandedNode[1].board, adjacent, tetromino):
                        generatedCount += 1
                        newBoard = updateBoard(expandedNode[1].board, item)
                        newList = expandedNode[1].prevActions.copy()
                        newList.append(item)
                        newNode = Node(newBoard, newList)
                        heuristicValue = heuristic(newNode, target, distancesTo)
                        heapq.heappush(priorityQueue, (heuristicValue, Node(newBoard, newList)))
       
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

    if checkTarget(expandedNode[1].board, target):
        return expandedNode[1].prevActions
    else:
        return None    


# This function is very buggy
def find_segments(board, target, row: bool):
    segments = []
    segment = []
    count = 0

    for pos in range(22):
        if row: 
            square = Coord(target.r, pos%11)
            nextSquare = Coord(target.r, (pos+1)%11)
            prevSquare = Coord(target.r, (pos-1)%11)
        else:
            square = Coord(pos%11, target.c)
            nextSquare = Coord((pos+1)%11, target.c)
            prevSquare = Coord((pos-1)%11, target.c)
        if board.get(square):
            count += 1     
        # If previous square is filled and current square is not filled
        if board.get(prevSquare) and (not board.get(square)):
            segment.append(pos%11)
        # if current square is not filled and next square is filled
        if not board.get(square) and board.get(nextSquare) and segment:
            segment.append(pos%11)
            if segment not in segments:
                segments.append(segment)
            segment = []           
    if count==22:
        return []   
    
    if not segments: 
        return [[1,0]]
    else: 
        return segments       


 # for rows and columns
def dist_to_segment2(board, target, segment, row, distancesTo):
    if not segment: 
        return 0
    
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
        distances.append(closestSquare(board, square, distancesTo))
    result = min(distances) + 1 + upperBound - lowerBound     
    return math.ceil((min(distances) + upperBound - lowerBound + 1)/4.0)   





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
     


def heuristic(node: Node, target: Coord, distancesTo):
    # If target is gone
    if not (node.board).get(target):
        return len(node.prevActions)
    
    rowValue = estimate_move(node.board, target, distancesTo, True)
    colValue = estimate_move(node.board, target, distancesTo, False)
      
    return 1.001*min(rowValue, colValue) + len(node.prevActions)    

# predict remaining moves
def remaining_moves(board, target, distancesTo={}):
    if not distancesTo:
        distancesTo = {}
        for pos in range(11):
            distancesTo[Coord(target.r, pos)] = djikstra(board, Coord(target.r, pos))
            distancesTo[Coord(pos, target.c)] = djikstra(board, Coord(pos, target.c))   

    rowValue = estimate_move(board, target, distancesTo, True)
    colValue = estimate_move(board, target, distancesTo, False)
    return min(rowValue, colValue)


def estimate_move(board, target: Coord, distancesTo, isRow):
    # If target is gone
    if not board.get(target):
        return 0
    value = 0      
    if isRow: 
        rowSegments = find_segments(board, target, row=True)
        for rowSegment in rowSegments:
            if rowSegment:
                value += dist_to_segment2(board, target, rowSegment, True, distancesTo)
                #rows.append(dist_to_segment2(node.board, target, rowSegment, True, distancesTo))       
    else:
        colSegments = find_segments(board, target, row=False)
        for colSegment in colSegments:
            if colSegment: 
                value += dist_to_segment2(board, target, colSegment, False, distancesTo)
    return value            
    
# Finds distance between closest adjacent square to red and target   
def closestSquare(board: dict[Coord, PlayerColor], target: Coord, distancesTo):
    adjacents = findAdjacent(board) 
    # Will fix this later to not use an array, but keeping it here bcuz it's quick and easy
    distances = []
    for square in adjacents:
        distances.append((distancesTo[target])[square])
    if not distances: 
        return 0    
    return min(distances)



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
    updateRowCol(newBoard)
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
        print(coord, end=",")

# Given a board and placeactions, returns the updated board
def newBoard2(board, placeactions: [PlaceAction]):
    new = board
    for action in placeactions: 
        new = updateBoard(new, action)
        updateRowCol(new)
    return new    

# Find blue squares
def findBlueSquares(board):
    blueSquares = []
    for key, colour in board.items():
        if colour==PlayerColor.BLUE:
            blueSquares.append(key)
    return blueSquares        

# Give me a list of the removable blue squares
def removeableBlueSquares(board):
    blueSquares = findBlueSquares(board)
    removableList = []
    distance2 = {}
    for blueSquare in blueSquares:
        for pos in range(11):
            distance2[Coord(blueSquare.r, pos)] = djikstra(board, Coord(blueSquare.r, pos))
            distance2[Coord(pos, blueSquare.c)] = djikstra(board, Coord(pos, blueSquare.c))
        if remaining_moves(board, blueSquare, distance2) < 250:
            removableList.append(blueSquare)
    return removableList

# Cannot run on squares that are full
def bfs(board, square):
    visited = {}
    distances = {}
    for i in range(11):
        for j in range(11):
            visited[Coord(i,j)] = 0
            if (square.r==i and square.c==j):
                distances[Coord(i,j)] = 0
            else:
                distances[Coord(i,j)] = 1000    

    queue = []
    queue.append(square)
    while queue: 
        coord = queue.pop(0)
        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        for direction in directions: 
            # If it is empty and unvisited
            if not board.get(coord + direction) and not visited[coord + direction] and 1 + distances[coord] < distances[coord + direction]:
                distances[coord + direction] = 1 + distances[coord]
                visited[coord + direction] = 1
                queue.append(coord + direction)  
    return distances              


