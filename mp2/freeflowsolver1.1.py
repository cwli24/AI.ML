#!/usr/bin/env python
import sys, os.path

def dumbBacktracking(matrix, colorSet, srcCells, currentEmpty, numEmptyCells):
    if numEmptyCells == 0:
        return 0
  
    for color in colorSet:
        (x, y) = currentEmpty
        matrix[x][y] = color
        result = dumbBacktracking(matrix, colorSet, srcCells, findNextEmpty(currentEmpty), numEmptyCells-1)
 
    # if our assignment met constraints and this still satisfies them, we backtrack check
    if result == 0:
        adjCounter = 0
        if x-1 >= 0 and matrix[x-1][y] == color:
            adjCounter += 1
        if y-1 >=0 and matrix[x][y-1] == color:
            adjCounter += 1
        if x+1 < width and matrix[x+1][y] == color:
            adjCounter += 1
        if y+1 < height and matrix[x][y+1] == color:
            adjCounter += 1
    
        if (adjCounter == 2 and (x, y) not in srcCells) or (adjCounter == 1 and (x, y) in srcCells):
            return 0
      
        matrix[x][y] = '_'
    return -1

def findNextEmpty(currentCellCoord):
    for y in range(currentCellCoord[1], currentCellCoord[1]+2):
        for x in range(currentCellCoord[0], width):
            if matrix[x][y] == '_':
                return (x, y)

def smartBacktracking():
    return

def main():
    if not os.path.exists(sys.argv[1]):
        print 'Input file does not exist'
        sys.exit(1)
  
    # parse input flow free as 2D char matrix
    width, height, matrix = 0
    with open(sys.argv[1], 'r') as flowfree:
        line = flowfree.readline().strip()
        width = len(line)
        height += 1
    
        matrix = [list(line)]
        for line in flowfree.readlines():
            line = line.strip()
            matrix.append(list(line))
            height += 1

    # iterate through matrix line by line to determine colors, end points
    colors = set()
    endpts = set()
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell != '_':
                colors.add(cell)
                endpts.add((x, y))

    if dumbBacktracking(matrix, colors, endpts, findNextEmpty((0, 0)), len(endpts)) == -1:
        print 'No solution to Flow Free puzzle was found!'
        sys.exit(1)
  
    print '\n'.join([''.join([col for col in row]) for row in matrix])
  
if __name__ == "__main__":
    main()