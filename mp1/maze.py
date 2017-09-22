#!/usr/bin/env python
"""Search for the solution to mazes using DFS, BFS, greedy best-first, and A* algorithms."""

import sys
from collections import deque

class Tile:
    '''Data structure object used to create a maze. With this construct, we define:
    "Path cost"         as  number of Tiles in the valid path, marked by value of PATH
    "Nodes expanded"    as  total number of Tiles visited, marked by value of VISITED+PATH
    '''

    # Enumeration for what Tile objects contain
    BLANK, WALL, VISITED, GOAL, PATH = range(5)
    
    def __init__(self, tileDescription):
        self.value = tileDescription
        self.parent = None

class Maze:
    '''Parsing the maze from input text file to data structure'''
    def __init__(self, mazefile):
        self.path_cost = self.nodes_expd = 0
        self.current_x = self.current_y = None
    
        with open(mazefile, 'r') as in_file:
            self.maze_width = len(in_file.readline().strip())
            self.maze_height = 1
    
            # 2-D maze is first initialized, with the first row being always a wall (we assume)
            self.maze = [[Tile(Tile.WALL)] for numTiles in range(self.maze_width)]
            
            # Fill out the rest of the maze structure from parsing input text file
            for line in in_file.readlines():
                for column_idx in range(len(line.strip())):
                    c = line[column_idx]
                    if c == ' ':
                        self.maze[column_idx].append(Tile(Tile.BLANK))
                    elif c == '%':
                        self.maze[column_idx].append(Tile(Tile.WALL))
                    elif c == '.':
                        self.maze[column_idx].append(Tile(Tile.GOAL))
                    else: #c == 'P'
                        self.maze[column_idx].append(Tile(Tile.VISITED))
                        self.current_x = column_idx
                        self.current_y = self.maze_height
                self.maze_height += 1

    # Check if it is possible to travel in a given direction; we go in L,U,R,D order
    def canTravelUp(self):
        next_position = self.maze[self.current_x][self.current_y-1].value
        return 0 if next_position == Tile.WALL or next_position == Tile.VISITED else 1
        
    def canTravelDown(self):
        next_position = self.maze[self.current_x][self.current_y+1].value
        return 0 if next_position == Tile.WALL or next_position == Tile.VISITED else 1
    
    def canTravelLeft(self):
        next_position = self.maze[self.current_x-1][self.current_y].value
        return 0 if next_position == Tile.WALL or next_position == Tile.VISITED else 1
    
    def canTravelRight(self):
        next_position = self.maze[self.current_x+1][self.current_y].value
        return 0 if next_position == Tile.WALL or next_position == Tile.VISITED else 1

    def printMaze(self, output_maze):
        '''Print ccmaze into output text file in original format'''
        with open(output_maze, 'w') as out_file:
            for row in range(self.maze_height):
                for col in range(self.maze_width):
                    if self.maze[col][row].value == Tile.WALL:
                        out_file.write('%c' % '%')
                    elif self.maze[col][row].value == Tile.BLANK or self.maze[col][row].value == Tile.VISITED:
                        out_file.write('%c' % ' ')
                    else:
                        out_file.write('%c' % '.')
                out_file.write('\n')
           
def dfSearch(searchMaze):
    # we use a stack of coords to keep track of our valid path, starting with 'P'
    stack = deque()
    stack.append((searchMaze.current_x, searchMaze.current_y))
    searchMaze.nodes_expd = 1
    # the start Tile is already marked as VISITED when maze was constructed
    
    while stack:
        if searchMaze.canTravelLeft():
            # change respective coordinate to "move"
            searchMaze.current_x -= 1

            # increment our number of nodes expanded counter
            searchMaze.nodes_expd += 1

            # push this new position onto the stack
            stack.append((searchMaze.current_x, searchMaze.current_y))
            current_pos = searchMaze.maze[searchMaze.current_x][searchMaze.current_y]
            
            # stop if we reached the '.' (end), prevent future visit if we didn't
            if current_pos.value == Tile.GOAL: break
            else: current_pos.value = Tile.VISITED
            
        elif searchMaze.canTravelUp():
            searchMaze.current_y -= 1
            searchMaze.nodes_expd += 1
            
            stack.append((searchMaze.current_x, searchMaze.current_y))
            current_pos = searchMaze.maze[searchMaze.current_x][searchMaze.current_y]
            
            if current_pos.value == Tile.GOAL: break
            else: current_pos.value = Tile.VISITED
            
        elif searchMaze.canTravelRight():
            searchMaze.current_x += 1
            searchMaze.nodes_expd += 1
            
            stack.append((searchMaze.current_x, searchMaze.current_y))
            current_pos = searchMaze.maze[searchMaze.current_x][searchMaze.current_y]
            
            if current_pos.value == Tile.GOAL: break
            else: current_pos.value = Tile.VISITED
            
        elif searchMaze.canTravelDown():
            searchMaze.current_y += 1
            searchMaze.nodes_expd += 1
            
            stack.append((searchMaze.current_x, searchMaze.current_y))
            current_pos = searchMaze.maze[searchMaze.current_x][searchMaze.current_y]
            
            if current_pos.value == Tile.GOAL: break
            else: current_pos.value = Tile.VISITED
        
        else:
            # we discard a bad step, and retrace to the previous position to try another path
            stack.pop()
            searchMaze.current_x, searchMaze.current_y = stack[-1]
    
    # our stack holds our valid Tiles path from 'P' to '.', inclusively
    for x, y in stack:
        searchMaze.maze[x][y].value = Tile.PATH

    # count the number of tiles in our solution path
    searchMaze.path_cost = len(stack)
        
    # and we're done!
    
def bfSearch(searchMaze):
    # we use a queue of coords to keep track of our visited nodes, starting with 'P'
    queue = deque()
    queue.append((searchMaze.current_x, searchMaze.current_y))
    
    while queue:
        # we expand the next Tile node on the queue...
        searchMaze.current_x, searchMaze.current_y = queue.pop()
        searchMaze.nodes_expd += 1
        
        # and add each valid step from current position onto it
        if searchMaze.canTravelLeft(): 
            queue.append((searchMaze.current_x-1, searchMaze.current_y))
            addTile = searchMaze.maze[searchMaze.current_x-1][searchMaze.current_y]
            
            # we link the expansions to track possible paths...
            addTile.parent = (searchMaze.current_x, searchMaze.current_y)
            
            # and set this Tile as the next node, if it is the end point
            if addTile.value == Tile.GOAL:
                searchMaze.current_x -= 1
                searchMaze.nodes_expd += 1
                break
            # or mark it to reduce duplication on queue, if it's a blank space
            else:
                addTile.value = Tile.VISITED
            
        if searchMaze.canTravelUp(): 
            queue.append((searchMaze.current_x, searchMaze.current_y-1))
            addTile = searchMaze.maze[searchMaze.current_x][searchMaze.current_y-1]
           
            addTile.parent = (searchMaze.current_x, searchMaze.current_y)
            if addTile.value == Tile.GOAL:
                searchMaze.current_y -= 1
                searchMaze.nodes_expd += 1
                break
            else:
                addTile.value = Tile.VISITED
            
        if searchMaze.canTravelRight(): 
            queue.append((searchMaze.current_x+1, searchMaze.current_y))
            addTile = searchMaze.maze[searchMaze.current_x+1][searchMaze.current_y]
            
            addTile.parent = (searchMaze.current_x, searchMaze.current_y)
            if addTile.value == Tile.GOAL:
                searchMaze.current_x += 1
                searchMaze.nodes_expd += 1
                break
            else:
               addTile.value = Tile.VISITED
       
        if searchMaze.canTravelDown(): 
            queue.append((searchMaze.current_x, searchMaze.current_y+1))
            addTile = searchMaze.maze[searchMaze.current_x][searchMaze.current_y+1]
            
            addTile.parent = (searchMaze.current_x, searchMaze.current_y)
            if addTile.value == Tile.GOAL:
                searchMaze.current_y += 1
                searchMaze.nodes_expd +=1
                break
            else:
                addTile.value = Tile.VISITED
    # addTile would be our "current position" tile, or rather, the end '.' tile upon break
    
    # backtrace from '.' to 'P', building our solution path
    while addTile.parent != None:
        searchMaze.path_cost += 1
        addTile.value = Tile.PATH
        addTile = searchMaze.maze[addTile.parent[0]][addTile.parent[1]]
            
    # the starting tile is not included in the loop above
    searchMaze.path_cost += 1
    addTile.value = Tile.PATH        
            
    # and we're done!
   
def greedySearch(searchMaze):
    return
    
def astarSearch(searchMaze):   
    return    
    
def main():
    if len(sys.argv) != 4:
        print 'Usage:', sys.argv[0], '{1,2,3,4} input_maze.txt output_soln.txt'
        print '        1 = Depth-first search'
        print '        2 = Breadth-first search'
        print '        3 = Greedy best-first search'
        print '        4 = A* search'
        sys.exit(1)
    
    # Instantiate the required mazes
    searchMaze = Maze(sys.argv[2])
    searchType = int(sys.argv[1])

    # Perform the required searches
    if searchType == 1:
        searchAlgorithm = 'Depth-First'
        dfSearch(searchMaze)
    elif searchType == 2:
        searchAlgorithm = 'Breadth-First'
        bfSearch(searchMaze)
    elif searchType == 3:
        searchAlgorithm = 'Greedy Best-First'
        greedySearch(searchMaze)
    else:
        searchAlgorithm = 'A*'
        astarSearch(searchMaze)
        
    # Output the searched maze    
    searchMaze.printMaze(sys.argv[3])
    print 'Path cost of the solution:', searchMaze.path_cost, 'steps'
    print 'Number of nodes expanded by', searchAlgorithm, 'search algorithm:', searchMaze.nodes_expd

if __name__ == "__main__":
    main()