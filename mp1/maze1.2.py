#!/usr/bin/env python
"""Search for the solution to mazes with multiple goals using A* algorithm."""

import sys
from Queue import PriorityQueue

class Tile:
    '''Data structure object used to create a maze. With this construct, we define:
    "Path cost"         as  number of steps in the valid path, marked by value of PATH
    "Nodes expanded"    as  total number of Tiles visits, which includes PATH tiles
    '''

    # Enumeration for what Tile objects contain
    BLANK, WALL, VISITED, GOAL, PATH = range(5)
    
    def __init__(self, tileDescription):
        self.value = tileDescription
        self.parents = [] # a tile can now have multiple parents

class Maze:
    '''Parsing the maze from input text file to data structure'''
    def __init__(self, mazefile):
        self.path_cost = self.nodes_expd = 0
        self.current_x = self.current_y = None
        self.endpts = []
    
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
                        self.endpts.append((column_idx, self.maze_height))
                    else: #c == 'P'
                        self.maze[column_idx].append(Tile(Tile.VISITED))
                        self.current_x = column_idx
                        self.current_y = self.maze_height
                self.maze_height += 1

    # Check if it is possible to travel in a given direction; we go in L,U,R,D order;
    # It's possible to revisit a tile multiple times in this case.
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

    def printMaze(self, output_maze, ordered_endpts):
        '''Print ccmaze into output text file in original format'''
        label = '0'
        for x, y in ordered_endpts:
            self.maze[x][y].value = label
            label = 'a' if label == '9' else 'A' if label == 'z' else chr(ord(label)+1)

        with open(output_maze, 'w') as out_file:
            for row in range(self.maze_height):
                for col in range(self.maze_width):
                    if self.maze[col][row].value == Tile.WALL:
                        out_file.write('%c' % '%')
                    elif self.maze[col][row].value == Tile.BLANK or self.maze[col][row].value == Tile.VISITED:
                        out_file.write('%c' % ' ')
                    elif self.maze[col][row].value == Tile.PATH:
                        out_file.write('%c' % '.')
                    else:
                        out_file.write('%c' % self.maze[col][row].value)
                out_file.write('\n')
           
def lowestManDist((cur_x, cur_y), goals_list):
    '''Manhattan distance formula applied to a list of coordinates'''
    lowest = 999
    for goal_x, goal_y in goals_list:
        if abs(cur_x - goal_x) + abs(cur_y - goal_y) < lowest: lowest = abs(cur_x-goal_x) + abs(cur_y-goal_y)
    return lowest

def clearVisits(maze):
    '''Overwrites all Tiles value of VISITED'''
    for x in range(maze.maze_width):
        for y in range(maze.maze_height):
            if maze.maze[x][y].value == Tile.VISITED: maze.maze[x][y].value = Tile.BLANK

def astarSearch(searchMaze, goals_list_ordered):   
    '''Our A* heuristic is the lowest Manhattan distance to any end points from our current
    position at very step of branching.'''

    # we use a priority queue of (f(n)=total, g(n)=cost, coords) to prioritize shortest path to end goal
    pqueue = PriorityQueue()

    # at start, cost is 0 and total cost is to be calculated--so DC
    pqueue.put( (0, 0, (searchMaze.current_x, searchMaze.current_y)) )

    goalsLeft = len(searchMaze.endpts)
    while 0 < goalsLeft:
        # grab lowest total cost coordinate and expand it
        total_cost, cost_so_far, (searchMaze.current_x, searchMaze.current_y) = pqueue.get()
        searchMaze.nodes_expd += 1
        
        # if we can't travel any direction, this value gets trashed, so DW (yay!)
        cost_so_far += 1
        
        if searchMaze.canTravelLeft():
            coord_pair = (searchMaze.current_x-1, searchMaze.current_y)

            # create a path trace as we move
            addTile = searchMaze.maze[searchMaze.current_x-1][searchMaze.current_y]
            #addTile.parents.append((searchMaze.current_x, searchMaze.current_y))

            if addTile.value == Tile.GOAL:
                # mark this next tile as the next reached goal
                searchMaze.current_x -= 1
                goals_list_ordered.append((searchMaze.current_x, searchMaze.current_y))

                # remove it from list of remaining goals
                goalsLeft -= 1
                searchMaze.endpts.remove((searchMaze.current_x, searchMaze.current_y))

                # tree search from this "new" position, effectively treating each end point separately
                # this prevents loop from continuing earlier steps that did not include this end point
                while not pqueue.empty(): pqueue.get()

                # wipes footprints off maze to allow repeated state detection for next goal
                clearVisits(searchMaze)

                # new initial and skip rest of the checks since we moved from original tile
                addTile.value = Tile.VISITED
                pqueue.put( (0, cost_so_far, (searchMaze.current_x, searchMaze.current_y)) )
                continue

            # else update the closest goal from our current position and prioritize it
            addTile.value = Tile.VISITED
            pqueue.put( (cost_so_far + lowestManDist(coord_pair, searchMaze.endpts), cost_so_far, coord_pair) )
                
        if searchMaze.canTravelUp():
            coord_pair = (searchMaze.current_x, searchMaze.current_y-1)

            addTile = searchMaze.maze[searchMaze.current_x][searchMaze.current_y-1]
            #addTile.parents.append((searchMaze.current_x, searchMaze.current_y))

            if addTile.value == Tile.GOAL:
                searchMaze.current_y -= 1
                goals_list_ordered.append((searchMaze.current_x, searchMaze.current_y))

                goalsLeft -= 1
                searchMaze.endpts.remove((searchMaze.current_x, searchMaze.current_y))

                while not pqueue.empty(): pqueue.get()
                clearVisits(searchMaze)
                addTile.value = Tile.VISITED
                pqueue.put( (0, cost_so_far, (searchMaze.current_x, searchMaze.current_y)) )
                continue

            addTile.value = Tile.VISITED
            pqueue.put( (cost_so_far + lowestManDist(coord_pair, searchMaze.endpts), cost_so_far, coord_pair) )
        
        if searchMaze.canTravelRight():
            coord_pair = (searchMaze.current_x+1, searchMaze.current_y)

            addTile = searchMaze.maze[searchMaze.current_x+1][searchMaze.current_y]
            #addTile.parents.append((searchMaze.current_x, searchMaze.current_y))

            if addTile.value == Tile.GOAL:
                searchMaze.current_x += 1
                goals_list_ordered.append((searchMaze.current_x, searchMaze.current_y))

                goalsLeft -= 1
                searchMaze.endpts.remove((searchMaze.current_x, searchMaze.current_y))

                while not pqueue.empty(): pqueue.get()
                clearVisits(searchMaze)
                addTile.value = Tile.VISITED
                pqueue.put( (0, cost_so_far, (searchMaze.current_x, searchMaze.current_y)) )
                continue

            addTile.value = Tile.VISITED
            pqueue.put( (cost_so_far + lowestManDist(coord_pair, searchMaze.endpts), cost_so_far, coord_pair) )
    
        if searchMaze.canTravelDown():
            coord_pair = (searchMaze.current_x, searchMaze.current_y+1)

            addTile = searchMaze.maze[searchMaze.current_x][searchMaze.current_y+1]
            #addTile.parents.append((searchMaze.current_x, searchMaze.current_y))

            if addTile.value == Tile.GOAL:
                searchMaze.current_y += 1
                goals_list_ordered.append((searchMaze.current_x, searchMaze.current_y))

                goalsLeft -= 1
                searchMaze.endpts.remove((searchMaze.current_x, searchMaze.current_y))

                while not pqueue.empty(): pqueue.get()
                clearVisits(searchMaze)
                addTile.value = Tile.VISITED
                pqueue.put( (0, cost_so_far, (searchMaze.current_x, searchMaze.current_y)) )
                continue

            addTile.value = Tile.VISITED
            pqueue.put( (cost_so_far + lowestManDist(coord_pair, searchMaze.endpts), cost_so_far, coord_pair) )

    # notice that even if we backtrack through the 'P' tile multiple times, we'll always
    # reach an end in the parents link because it started with an empty parent list
    # while addTile.parents:
    #     print 'parents for', prevCoord, ':', addTile.parents
    #     prevCoord = addTile.parents.pop()
    #     addTile.value = Tile.PATH
    #     addTile = searchMaze.maze[prevCoord[0]][prevCoord[1]]

    # we've reached our starting point!
    #addTile.value = 'S'
    searchMaze.path_cost = cost_so_far

def main():
    if len(sys.argv) not in (2,3):
        print 'Usage:', sys.argv[0], 'input_maze.txt [output_soln.txt]'
        sys.exit(1)
    
    # Instantiate the required mazes
    searchMaze = Maze(sys.argv[1])

    # Perform the search
    goals_ordered = []
    astarSearch(searchMaze, goals_ordered)
        
    # Output the searched maze
    if len(sys.argv) == 3:
        searchMaze.printMaze(sys.argv[2], goals_ordered)

    print 'Path cost of the solution:', searchMaze.path_cost, 'steps'
    print 'Number of nodes expanded by A* search algorithm:', searchMaze.nodes_expd

if __name__ == "__main__":
    main()