#!/usr/bin/env python
import sys, os.path
from random import sample

def dumbBacktracking(matrix, colorSet, srcCells, currentEmpty, numEmptyCells):
    if numEmptyCells == 0:
        return 0
    
    # try each color in the colorset
    for color in sample(colorSet, len(colorSet)):
        x, y = currentEmpty
        matrix[y][x] = color

        #print '\n'.join([''.join([col for col in row]) for row in matrix])
        #print '---------'
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
        for i in range(y*width+x, width*height):
            if (i%width, int(i/width)) not in srcCells:
               matrix[int(i/width)][i%width] = '_'

    return -1

# find the next empty space in the matrix
# note that the matrix is indexed by (y,x)
def findNextEmpty(matrix):
    for row in range(0, height):
        for col in range(0, width):
            if matrix[row][col] == '_':
                return (col, row)
    return (0,0)

def smartBacktracking():
    return

def main():
    if not os.path.exists(sys.argv[1]):
        print 'Input file does not exist'
        sys.exit(1)
  
    # parse input flow free as 2D char matrix
    global width, height

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


    # -- replace the dumb algorithm with smart algorithm here --
    # initial call to the recursive backtracking
    if dumbBacktracking(matrix, colors, endpts, findNextEmpty(matrix), width*height-len(endpts)) == -1:
        print 'No solution to Flow Free puzzle was found!'

    print '\n'.join([''.join([col for col in row]) for row in matrix])
  
if __name__ == "__main__":
    main()
