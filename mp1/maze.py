#!/usr/bin/env python
"""Search for the solution to mazes using DFS, BFS, greedy best-first, and A* algorithms."""

import sys

class Tile:
    'Data structure object used to create a maze'  
    # Enumeration for what Tile objects contain
    BLANK, WALL, VISITED, GOAL = range(4)
    
    def __init__(self, tileDescription):
        self.value = tileDescription

    # Check if it is possible to travel in a given direction
    def canTravelUp(self):
        if(maze[x][y-1].value == WALL):
            return 0
        else:
            return 1
        
    def canTravelDown(self):
        if(maze[x][y+1].value == WALL):
            return 0
        else:
            return 1
    
    def canTravelLeft(self):
        if(maze[x-1][y].value == WALL):
            return 0
        else:
            return 1
    
    def canTravelRight(self):
        if(maze[x+1][y].value == WALL):
            return 0
        else:
            return 1

class Maze:
    'Parsing the maze from input text file to data structure'
    def __init__(self, mazetext):
        self.path_cost = self.nodes_expd = 0
    
        with open(mazetext, 'r') as in_file:
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
   
    def printMaze(self, output_maze):
        '''Print ccmaze into output text file in original format'''
        with open(output_maze, 'w') as out_file:
            for row in range(self.maze_height):
                for col in range(self.maze_width):
                    if(self.maze[col][row].value == Tile.WALL):
                        out_file.write('%c' % '%')
                    elif(self.maze[col][row].value == Tile.BLANK):
                        out_file.write('%c' % ' ')
                    else:
                        out_file.write('%c' % '.')
                out_file.write('\n')
           
def dfSearch():

def bfSearch():

def greedySearch():

def astarSearch():

        
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
    
    # Perform the required searches
    if sys.argv[1] == 1:
        searchAlgorithm = 'Depth-first'
        dfSearch(searchMaze)
    elif sys.argv[1] == 2:
        searchAlgorithm = 'Breadth-first'
        bfSearch(searchMaze)
    elif sys.argv[1] == 3:
        searchAlgorithm = 'Greedy best-first'
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
    