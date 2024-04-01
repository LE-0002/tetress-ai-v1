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

def bfs(board, square, target):
    queue = []
    defaultV = 0
    defaultC = -1
    coordKeys = []
    for r in range(11):
        for c in range(11):
            coordKeys.append(Coord(r, c))

    visited = dict.fromkeys(coordKeys, defaultV)
    counts = dict.fromkeys(coordKeys, defaultC)

    queue.append(square)
    counts[square] = 0
    while queue: 
        coord = queue.pop(0)
        if coord == target: # stop searching if found target
            break

        directions = [Direction.Down, Direction.Up, Direction.Left, Direction.Right]
        # if it hasn't been visited yet
        if visited[coord]==0:
            visited[coord]= 1
            # checking adjacent coords
            for direction in directions: 
                # if it is not visited
                if visited[coord + direction]==0:
                    if isEmpty(board, (coord + direction)):
                        counts[coord + direction] = 1 + counts[coord]
                        queue.append(coord + direction)
    return counts   

# With wrapping included now
def manhattan(board, target, square):
    height = abs(target.r - square.r)
    width = abs(target.c - square.c)
    if height > 5:
        height = 11 - max(target.r, square.r) + min(target.r, square.r)  
        row = (min(target.r, square.r)-1)%11
        pos1 = square.c
        pos2 = (square.c+1)%11
        while (pos1!=pos2):
            if board.get(Coord(row, pos1))==PlayerColor.BLUE:
                pos1 = (pos1-1)%11
            elif (board.get(Coord(row, pos2))==PlayerColor.BLUE):
                pos2 = (pos2+1)%11
            else:
                break    
        pos1 = (pos1+1)%11
        pos2 = (pos2+1)%11
        if pos1==pos2:
            additional = 0    
    if width > 5:
        width = 11 - max(target.c, square.c) + min(target.c, square.c)
    return math.ceil((width + height) / 4.0)



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
    print(TARGET)
    coords = []
    global firstTarget  
    firstTarget += 1

    #for i in range(11):
     #   for j in range(11):
      #      if Coord(i, j) not in board.keys():
       #         coords.append(Coord(i, j))
    #for coord in coords: 
     #   djikstra(board, coord, target)  
    #print(render_board(board, target, ansi=True))
    distancesTo = {}
    for pos in range(11):
        distancesTo[Coord(target.r, pos)] = djikstra(board, Coord(target.r, pos))
        distancesTo[Coord(pos, target.c)] = djikstra(board, Coord(pos, target.c))
    #print((distancesTo[Coord(8, 4)])[Coord(6,3)])
    #for key, value in distancesTo[Coord(8, 4)].items():
    #    print(str(key) + ":" + str(value))
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
    #for key, value in bfs(board, target, Coord(0, 0)).items():
    #    print(str(key) + ":" + str(value))

#    test = {}
#    for i in range(9):
#       test[Coord(0, i)] = PlayerColor.BLUE
#    for j in range(1, 7):
#       test[Coord(j, 4)] = PlayerColor.RED
#       if 1<=j<=3:
#        test[Coord(i, 5)] = PlayerColor.RED 
#    test[Coord(1, 7)] = PlayerColor.BLUE
#    list1 = []
#    for i in range(3):
#        list1.append(PlaceAction(Coord(0,0), Coord(0, 1), Coord(0, 2), Coord(0, 3)))
#    render_board(test, Coord(1, 7), ansi=True)
#    adjacents1 = findAdjacent(test)
#    print(heuristic(Node(test, list1), adjacents1, target, distancesTo)) 
    
    # Can loop through every blue node not in target row or column and do it
    if (heuristic(initialNode, target, distancesTo) > 250):
        print("dog")
        if target not in visited1 and firstTarget==1:
            print("meow")
            visited1.append(target)
            previousActions = []
            lenpreviousActions = 250
            actions = []
            print(TARGET1)
            print(blueSquares(initialNode.board, TARGET1, visited1))
            for blueSquare in blueSquares(initialNode.board, TARGET1, visited1):
                print("pad")
                print(visited1)
                print(blueSquare)
                if blueSquare not in visited1:
                    print("boo")
                    actions = search(initialNode.board, blueSquare)
                    print("asdfasd")
                if actions and len(actions) < lenpreviousActions:
                    print("bad")
                    lenpreviousActions = len(actions)
                    previousActions = actions
            print("doo")        
            new = newBoard2(initialNode.board, previousActions)
            if search(new, target):
                return previousActions + search(new, target)
            
            
        return None
    print("moo")       
    generatedCount = 1
    while priorityQueue:
        expandedNode = heapq.heappop(priorityQueue)
        count += 1
        print(render_board(expandedNode[1].board, target, ansi=True))
        #print(find_segments(expandedNode[1].board, target, False))
        #print(dist_to_segment2(expandedNode[1].board, target, [8,10], False, distancesTo))
        if expandedNode and checkTarget(expandedNode[1].board, target): 
            #print(render_board(expandedNode[1].board, target, ansi=True))
            #printPlaceAction(expandedNode[1].prevActions)
            print("expanded nodes: " + str(count))
            print("generated nodes: " + str(generatedCount))
            break
        adjacents = findAdjacent(expandedNode[1].board)

        print(heuristic(expandedNode[1], target, distancesTo))
        # Need to fix this
            
        print("cat")        
        #if (heuristic(expandedNode[1], target, distancesTo)==4.0009999999999994):
         #   print("map")
#          #  row = False
#            distances = []
#            segment = [8,10]
#            upperBound = segment[1] 
#            lowerBound = segment[0]
#            if segment[0] > segment[1]:
#                upperBound = segment[1] + 11

#            for pos in range(lowerBound, upperBound + 1):
#                if row:
#                    square = Coord(target.r, pos%11)
#                else: 
#                    square = Coord(pos%11, target.c)
#                distances.append(closestSquare(expandedNode[1].board, square, distancesTo))
#            print(distances)    
#            print(math.ceil((min(distances)+1 + upperBound - lowerBound)/4.0))      
#            print("map")
#        printAdjacentSquares(adjacents)
        #print(toBeFilled(expandedNode[1].board, target, False))
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
                        heuristicValue = heuristic(newNode, target, distancesTo)
                        #print(heuristicValue)
                        #print(dist_to_segment2(newNode.board, target, [8, 10], False, distancesTo))
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
    
    rowSegments = find_segments(node.board, target, row=True)
    colSegments = find_segments(node.board, target, row=False)
    adjacentSpaces = findAdjacent(node.board)
    rowValue, colValue = 0, 0
    #rows = []
    #cols = []
    for rowSegment in rowSegments:
        if rowSegment:
            rowValue += dist_to_segment2(node.board, target, rowSegment, True, distancesTo)
            #rows.append(dist_to_segment2(node.board, target, rowSegment, True, distancesTo))
    for colSegment in colSegments:
        if colSegment: 
            colValue += dist_to_segment2(node.board, target, colSegment, False, distancesTo)
            #cols.append(dist_to_segment2(node.board, target, rowSegment, True, distancesTo))
    #print(rows, cols)       
    return 1.001*min(rowValue, colValue) + len(node.prevActions)    
    
    
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
    updateRowCol(board)
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

def blueSquares(board, target, visited1):
    blueSquares = []
    for key, colour in board.items():
        if colour==PlayerColor.BLUE and not (key.c==target.c or key.r==target.r) and key not in visited1:
            blueSquares.append(key)
    return blueSquares        