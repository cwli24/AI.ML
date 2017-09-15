#!/usr/bin/env python

import sys

class Tile :
    'Data structure object used to create a maze'
    
    # Enumeration for what Tile objects contain
    BLANK, WALL, VISITED, GOAL = range(4)
    
    def __init__(self, tileDescription):
        self.value = tileDescription

    # Check if it is possible to travel in a given direction
    # def canTravelUp(self):
    #     if (maze[x-1][y].value == WALL)
    #         return -1
    #     else
    #         return 0
        
    # def canTravelDown(self):
    #     if (maze[x+1][y].value == WALL)
    #         return -1
    #     else
    #         return 0
    
    # def canTravelLeft(self):
    #     if (maze[x][y-1].value == WALL)
    #         return -1
    #     else
    #         return 0
    
    # def canTravelRight(self):
    #     if (maze[x][y+1].value == WALL)
    #         return -1
    #     else
    #        return 0

def main():
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], 'input_maze.txt'
        sys.exit(1)
    
    maze_width = maze_height = 0
    
    # Parsing the maze from input text file to data structure
    with open(sys.argv[1], 'r') as in_file:
        maze_width = len(in_file.readline().strip())
        maze_height += 1

        # 2-D maze is first initialized, with the first row being always a wall (we assume)
        maze = [[Tile(Tile.WALL)] for numTiles in range(maze_width)]
        
        # Fill out the rest of the maze structure from parsing input text file
        for line in in_file.readlines():
            for column_idx in range(len(line.strip())):
                c = line[column_idx]
                if c == ' ':
                    maze[column_idx].append(Tile(Tile.BLANK))
                elif c == '%':
                    maze[column_idx].append(Tile(Tile.WALL))
                elif c == '.':
                    maze[column_idx].append(Tile(Tile.GOAL))
                else: #c == 'P'
                    maze[column_idx].append(Tile(Tile.VISITED))
                    current_x = column_idx
                    current_y = maze_height

            maze_height += 1

        print 'maze width, height:', maze_width, maze_height
     
    # test via printing out maze
    # for row in range(maze_height):
    #     for col in range(maze_width):
    #         sys.stdout.write('%d' % maze[col][row].value)
    #     print ''         

if __name__ == "__main__":
    main()