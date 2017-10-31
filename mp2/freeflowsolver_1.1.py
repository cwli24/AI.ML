#!/usr/bin/env python
import sys, os.path, copy, operator
from random import sample
from Queue import PriorityQueue

# ----------- HELPER FUNCTIONS ----------------------- #

def resetGrid(matrix, srcCells, x, y):
    for i in range(y * width + x, width * height):
            if (i % width, int(i / width)) not in srcCells:
               matrix[int(i / width)][i % width] = '_'

# find the next empty space in the matrix
# note that the matrix is indexed by (y,x)
def findNextEmpty(matrix):
    for row in range(0, height):
        for col in range(0, width):
            if matrix[row][col] == '_':
                return (col, row)
    return (0, 0)

def findNeighborsColors(matrix, cmpColor, curX, curY):
    emptyNeighbors = []
    sameColorNeighbors = []
    if curX - 1 >= 0:
        if matrix[curY][curX-1] == '_': 
            emptyNeighbors.append((curX - 1, curY))
        elif matrix[curY][curX-1] == cmpColor: 
            sameColorNeighbors.append((curX - 1, curY))
        # else NOT same color as cmpColor (do nothing here)
    if curY - 1 >= 0:
        if matrix[curY-1][curX] == '_': 
            emptyNeighbors.append((curX, curY - 1))
        elif matrix[curY-1][curX] == cmpColor: 
            sameColorNeighbors.append((curX, curY - 1))
    if curX + 1 < width:
        if matrix[curY][curX+1] == '_': 
            emptyNeighbors.append((curX + 1, curY))
        elif matrix[curY][curX+1] == cmpColor:
            sameColorNeighbors.append((curX + 1, curY))
    if curY + 1 < height:
        if matrix[curY+1][curX] == '_': 
            emptyNeighbors.append((curX, curY + 1))
        elif matrix[curY+1][curX] == cmpColor: 
            sameColorNeighbors.append((curX, curY + 1))
    return (emptyNeighbors, sameColorNeighbors)

# ----------- BACKTRACKING FUNCTIONS ----------------- #

def dumbBacktracking(matrix, colorSet, srcCells, currentEmpty, numEmptyCells):
    if numEmptyCells == 0:
        return 0

    # try each color in the colorset
    for color in sample(colorSet, len(colorSet)):
        x, y = currentEmpty
        matrix[y][x] = color
        count += 1

        # print '\n'.join([''.join([col for col in row]) for row in matrix])
        # print '---------'

        result = dumbBacktracking(matrix, colorSet, srcCells, findNextEmpty(matrix), numEmptyCells-1)

        # if our assignment met constraints and this still satisfies them, we backtrack check
        if result == 0:
            adjCounter = 0
            if x-1 >= 0 and matrix[y][x-1] == color:
                adjCounter += 1
            if y-1 >=0 and matrix[y-1][x] == color:
                adjCounter += 1
            if x+1 < width and matrix[y][x+1] == color:
                adjCounter += 1
            if y+1 < height and matrix[y+1][x] == color:
                adjCounter += 1

            if (adjCounter == 2 and (x, y) not in srcCells) or (adjCounter == 1 and (x, y) in srcCells):
                return 0

        # if current color does not work, clear everything
        # from this position to the end of the matrix and try
        # a new color
        resetGrid(matrix, srcCells, x, y)

    return -1

def smartBacktracking(matrix, coordColor, srcCellsSet):
    global count 
    # if our priority queue has no variable left to assign, the puzzle must be solved
    if len(coordColor) == 0:
        return True

    origCoordColor = copy.deepcopy(coordColor)
    print coordColor

    for cellX, cellY, cellColor in [(x, y, matrix[y][x]) for y in range(height) for x in range(width)]:
        if cellColor == '_':
            continue

        emptyNbs, sameColNbs = findNeighborsColors(matrix, cellColor, cellX, cellY)

        if (cellX, cellY) in srcCellsSet:
            if len(sameColNbs) == 0:
                if len(emptyNbs) == 0:
                    return False
                elif len(emptyNbs) == 1:
                    coordColor[emptyNbs[0]] = set(cellColor)
                # else 2 or more empty neighbors
            elif len(sameColNbs) == 1:
                for xy in emptyNbs:
                    coordColor[xy].discard(cellColor)
            else: # 2, 3, or 4 same color neighbors
                return False
        else:
            if len(emptyNbs) == 0:
                if len(sameColNbs) != 2:
                    return False
                # else exactly 2 same color neighbors

            elif len(emptyNbs) == 1:
                if len(sameColNbs) == 1:
                    # empty neighbor must be restricted to same color
                    coordColor[emptyNbs[0]] = set(cellColor)
                elif len(sameColNbs) == 2:
                    # empty neighbor cannot be same color
                    coordColor[emptyNbs[0]].discard(cellColor)
                else: # sameColorNeighborCt == 0 or sameColorNeighborCt == 3:
                    return False

            elif len(emptyNbs) == 2:
                if len(sameColNbs) == 0:
                    for xy in emptyNbs:
                        coordColor[xy] = set(cellColor)
                elif len(sameColNbs) == 2:
                    for xy in emptyNbs:
                        coordColor[xy].discard(cellColor)
                # else, number of sameColorNbs is 1

            # else, empty neighbors is 3 or 4

    for colorset in coordColor.values():
        if len(colorset) == 0:
            return False

    sortedConstVars = sorted(coordColor.items(), key=operator.itemgetter(1))
    mostConstVar = copy.deepcopy(sortedConstVars[0])   # ((x,y), set(['r',...]))
    (x, y), mCVDomain = mostConstVar
    del coordColor[(x,y)]

    for color in mCVDomain:
        matrix[y][x] = color
        count += 1

        print '(x, y):', x, y, ' domain:', mCVDomain
        print '\n'.join([''.join([col for col in row]) for row in matrix])
        print '-----------'

        if smartBacktracking(matrix, coordColor, srcCellsSet) is True:
            return True
        else:
            continue

    matrix[y][x] = '_'
    coordColor = origCoordColor

    return False

def main():
    if not os.path.exists(sys.argv[1]):
        print 'Input file does not exist'
        sys.exit(1)

    # parse input flow free as 2D char matrix
    global width, height
    global count

    width = height = 0
    matrix = []
    with open(sys.argv[1], 'r') as flowfree:
        for line in flowfree:
            line = line.strip()
            matrix.append(list(line))
            height += 1
        width = len(matrix[0])

    # iterate through matrix line by line to determine colors, end points
    colors = set()
    endpts = set()
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell != '_':
                colors.add(cell)
                endpts.add((x, y))

    # set up most constrained variable data structure 
    cellDict = {}   # variable, domain pairs

    # ---- THIS EXTRA CHECK MAKES THE 5x5 PUZZLE WORK ----- #
    # Some how need to do something like this at the beginning of the recursion
    # coordColorOptions = []
    # for y, row in enumerate(matrix):
    #     for x, cell in enumerate(row):
    #         empty = []
    #         if cell != '_':
    #             print x, y
    #             if x - 1 >= 0:
    #                 if matrix[y][x-1] == '_': 
    #                     empty.append((x - 1, y))
    #             if y - 1 >= 0:
    #                 if matrix[y-1][x] == '_': 
    #                     empty.append((x, y - 1))
    #             if x + 1 < width:
    #                 if matrix[y][x+1] == '_': 
    #                     empty.append((x + 1, y))
    #             if y + 1 < height:
    #                 if matrix[y+1][x] == '_': 
    #                     empty.append((x, y + 1))
    #             if len(empty) == 1:
    #                 i, j = (empty[0][0], empty[0][1])
    #                 coordColorOptions.append((empty[0][0], empty[0][1]))
    #                 # colorOptions.put(([cell], empty[0][0], empty[0][1]))
    #                 matrix[j][i] = cell
    #                 print colorOptions.queue, empty

    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell == '_':
                cellDict[(x,y)] = colors

    #sum = 0
    #max = 0
    #iters = 1000
    #for i in range(iters):
    #    count = 0
    #    if dumbBacktracking(matrix, colors, endpts, findNextEmpty(
    #        matrix), width * height - len(endpts)) == -1:
    #        print 'No solution to Free Flow puzzle was found!'
    #    else:
    #        # print 'num assignments: ' + str(count)
    #        sum += count
    #        if count > max: max = count

    # print '\n'.join([''.join([col for col in row]) for row in matrix])

    # initial call to the dumb backtracking
    
    #count = 0
    #if dumbBacktracking(SET PARAMS HERE) == -1:
    #    print 'No solution to Flow Free puzzle was found!'
    #else:
    #    print 'Solution to the Free Flow puzzle\n'
    #    print '\n'.join([''.join([col for col in row]) for row in matrix])
    #    print '\nnum assignments: ' + str(count)      
    
    # initial call to the smart backtracking
    
    count = 0
    if smartBacktracking(matrix, cellDict, endpts) is False:
        print 'No solution to Flow Free puzzle was found!'
    else:
        print 'Solution to the Free Flow puzzle\n'
        print '\n'.join([''.join([col for col in row]) for row in matrix])
        print '\nnum assignments: ' + str(count)  
    
if __name__ == "__main__":
    main()