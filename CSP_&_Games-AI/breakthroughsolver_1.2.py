#!/usr/bin/env python
import sys, os.path
from time import time
from random import sample, randint, random
from Queue import PriorityQueue
import copy

'''
A 'Breakthrough' simulation using minimax vs. alpha-beta search with various
move ordering heuristics.

We aim to find:
    A. The final state of the board and the winning player.
    B. The total number of game tree nodes expanded by each player.
    C. The avg # nodes expanded per move and avg amount of time per move.
    D. The # of opponent workers captured by each player, as well as the total #
       of moves required till the win.

--------------------------------------------------------------------------------

1. OF1 vs. OF1: VS Code terminal 2

Player A wins!

Total number of nodes expanded by player A: 8088570
Avg number of nodes expanded by player A: 323542
Avg time per move for player A: 137.92012001
Number of workers captured by player A: 1
Number of moves made by player A: 13

Total number of nodes expanded by player B: 1614005
Avg number of nodes expanded by player B: 64560
Avg time per move for player B: 25.8980000019
Number of workers captured by player B: 2
Number of moves made by player B: 12

['A', '_', 'A', 'A', 'A', 'A', 'A', 'A']
['_', 'A', 'A', '_', '_', '_', '_', 'A']
['_', 'A', '_', 'B', 'A', '_', '_', 'A']
['_', '_', '_', 'B', '_', '_', 'A', '_']
['_', '_', '_', '_', '_', '_', '_', 'B']
['_', '_', '_', '_', '_', '_', '_', 'B']
['_', 'B', 'B', 'B', '_', 'B', '_', '_']
['B', 'A', '_', 'B', 'B', 'B', 'B', 'B']

--------------------------------------------------------------------------------

2. OF2 vs. DH1: Harsh terminal 1

Player B wins!

Total number of nodes expanded by player A: 3772816
Avg number of nodes expanded by player A: 37728
Avg time per move for player A: 9.68248753309
Number of workers captured by player A: 10
Number of moves made by player A: 50

Total number of nodes expanded by player B: 6804865
Avg number of nodes expanded by player B: 68048
Avg time per move for player B: 17.2183195233
Number of workers captured by player B: 7
Number of moves made by player B: 50

['B', '_', '_', '_', '_', '_', '_', '_']
['_', '_', 'A', '_', '_', '_', 'A', '_']
['_', '_', '_', '_', '_', '_', '_', 'A']
['_', '_', '_', '_', '_', '_', '_', 'B']
['_', '_', 'B', '_', 'B', '_', 'B', '_']
['_', '_', '_', 'B', 'B', '_', '_', '_']
['A', '_', 'A', 'B', '_', '_', '_', 'A']
['B', '_', '_', '_', '_', '_', '_', '_']

--------------------------------------------------------------------------------

3. DH2 vs. OF1: Powershell Desktop 3

Player A wins!

Total number of nodes expanded by player A: 2509357
Avg number of nodes expanded by player A: 55763
Avg time per move for player A: 18.1448666467
Number of workers captured by player A: 2
Number of moves made by player A: 23

Total number of nodes expanded by player B: 2947741
Avg number of nodes expanded by player B: 65505
Avg time per move for player B: 20.2727777693
Number of workers captured by player B: 5
Number of moves made by player B: 22

['A', 'A', '_', 'A', 'A', 'A', 'A', '_']
['_', 'A', 'A', 'A', '_', '_', '_', '_']
['_', '_', '_', '_', '_', 'A', '_', '_']
['_', 'A', '_', '_', '_', 'B', '_', 'A']
['_', 'B', '_', '_', '_', 'A', '_', 'B']
['_', '_', '_', '_', '_', '_', 'B', '_']
['B', 'B', 'B', 'B', '_', '_', '_', '_']
['B', '_', '_', '_', 'A', '_', 'B', 'B']

--------------------------------------------------------------------------------

4. OF2 vs. OF1: Harsh terminal 2

Player B wins!

Total number of nodes expanded by player A: 5750919
Avg number of nodes expanded by player A: 56381
Avg time per move for player A: 14.1177772447
Number of workers captured by player A: 4
Number of moves made by player A: 51

Total number of nodes expanded by player B: 4161943
Avg number of nodes expanded by player B: 40803
Avg time per move for player B: 11.1679261759
Number of workers captured by player B: 13
Number of moves made by player B: 51

['A', 'A', 'B', 'A', '_', '_', '_', '_']
['_', '_', '_', '_', '_', 'B', '_', '_']
['_', '_', '_', '_', 'A', '_', '_', '_']
['_', '_', '_', '_', '_', '_', '_', '_']
['B', 'A', '_', '_', '_', '_', '_', '_']
['_', '_', '_', '_', '_', '_', '_', 'A']
['A', '_', 'A', 'A', 'A', 'A', '_', 'A']
['_', '_', '_', '_', '_', '_', '_', '_']

--------------------------------------------------------------------------------

5. DH2 vs. DH1: Powershell Desktop 2

Player A wins!

Total number of nodes expanded by player A: 1563926
Avg number of nodes expanded by player A: 50449
Avg time per move for player A: 24.8573225467
Number of workers captured by player A: 0
Number of moves made by player A: 16

Total number of nodes expanded by player B: 2185401
Avg number of nodes expanded by player B: 70496
Avg time per move for player B: 32.6110967436
Number of workers captured by player B: 0
Number of moves made by player B: 15

['A', 'A', '_', 'A', '_', 'A', '_', 'A']
['_', 'A', '_', 'A', 'A', 'A', '_', 'A']
['_', '_', 'A', 'A', '_', '_', 'A', '_']
['A', '_', '_', '_', 'A', '_', 'B', '_']
['B', '_', '_', '_', 'B', '_', '_', 'B']
['_', 'B', '_', 'B', '_', '_', '_', 'B']
['B', 'B', '_', '_', 'B', '_', '_', 'B']
['_', 'B', 'B', 'B', 'B', '_', 'A', 'B']

--------------------------------------------------------------------------------

6. OF2 vs. DH2: Powershell Desktop 3

Player B wins!

Total number of nodes expanded by player A: 4153423
Avg number of nodes expanded by player A: 27325
Avg time per move for player A: 8.96412500582
Number of workers captured by player A: 7
Number of moves made by player A: 76

Total number of nodes expanded by player B: 5427624
Avg number of nodes expanded by player B: 35708
Avg time per move for player B: 11.2609342039
Number of workers captured by player B: 12
Number of moves made by player B: 76

['_', '_', '_', 'B', '_', '_', '_', '_']
['B', '_', '_', '_', '_', '_', 'B', 'B']
['_', '_', '_', '_', '_', '_', '_', '_']
['_', '_', '_', '_', '_', 'A', '_', '_']
['_', '_', '_', '_', '_', '_', '_', '_']
['_', '_', '_', 'A', '_', '_', '_', '_']
['A', 'A', 'A', 'A', 'A', 'A', '_', 'A']
['_', '_', '_', '_', '_', '_', '_', '_']

--------------------------------------------------------------------------------


Authors:                                  Mihir Sherlekar, Harsh Modhera, Ben Li
Revised:                                  10/30/2017
'''


# ------------------------------- HEURISTICS --------------------------------- #

def dh1(positions):
    return 2 * len(positions) + random()

def of1(positions):
    return 2 * (30 - len(positions)) + random()

def dh2(positions):
    # we DON'T want to move row 0, cols 1, 3
    value = 50 + random()

    # weight important positions
    if (0, 1) in positions: value += 25
    if (0, 3) in positions: value += 25
    if (1, 1) in positions: value += 10
    if (1, 3) in positions: value += 10

    # weight the overall positions towards your endzone
    for x, y in positions:
        value += (height - x) * 2

    return value

# goal: continued forward movement towards opponent's endzone
def of2(positions):
    captureLeft = captureRight = dist = 0

    for x, y in positions:
        dist = (height - x) * 10
    dist += random()
    '''
    try:
        if matrix[x - 1][y - 1] == 'A': captureLeft = 100 + random()
    except Exception:
        pass

    try:
        if matrix[x - 1][y + 1] == 'A': captureRight = 100 + random()
    except Exception:
        pass
    '''

    return dist


# --------------------------------- HELPERS ---------------------------------- #

# returns actions for a player
def getActions(player, positions):
    # actions = set()
    actions = []

    if player == 'A':
        actions = ['right', 'down', 'left']
        # for x, y in positions:
        #     if x + 1 < height and y + 1 < width:
        #         actions.add('right')
        #     if x + 1 < height:
        #         actions.add('down')
        #     if x + 1 < height and y - 1 >= 0:
        #         actions.add('left')
    elif player == 'B':
        actions = ['right', 'up', 'left']
        # for x, y in positions:
        #     if x - 1 >= 0 and y + 1 < width:
        #         actions.add('right')
        #     if x - 1 >= 0:
        #         actions.add('up')
        #     if x - 1 >= 0 and y - 1 >= 0:
        #         actions.add('left')

    return actions

# get positions for A and B
def getPositions(matrix):
    posA = []
    posB = []

    for x, row in enumerate(matrix):
        for y, val in enumerate(row):
            if val == 'A':
                posA.append((x, y))
            elif val == 'B':
                posB.append((x, y))

    return posA, posB


# --------------------------------- MINIMAX ---------------------------------- #

# returns a utility value for MAX
def maxVal(matrix, depth, positionsA, positionsB):
    global nodesExpdA

    # if state is a terminal state, then return the utility at that state
    # if depth == 3:
    #     return

    if len(positionsA) == 0 or len(positionsB) == 0 or (depth - 1) == 3:
        return of1(positionsA)

    if 'A' in matrix[height - 1] or 'B' in matrix[0]:
        return of1(positionsA)

    # v = utility = -infinity
    # v = float('-inf')
    v = -1000000 # -1 * (2**20)
    # depth += 1
    actions = getActions('A', positionsA)

    # for each action in the world state,
    # result = world state after action
    # v = max(v, minVal(result))
    for x, y in positionsA:
        for action in actions: # actionsA:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x + 1 < height and y + 1 < width:
                    if result[x + 1][y + 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y + 1] == 'B':
                        newPositionsB.remove((x + 1, y + 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'down':
                if x + 1 < height:
                    if result[x + 1][y] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y))
                        result[x][y] = '_'
                        result[x + 1][y] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x + 1 < height and y - 1 >= 0:
                    if result[x + 1][y - 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y - 1] == 'B':
                        newPositionsB.remove((x + 1, y - 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue

            if (depth - 1) < 3:
                val = minVal(result, depth + 1, newPositionsA, newPositionsB)
            else:
                # newDepth = depth
                # val = randint(1, 10)
                val = of1(newPositionsA)

            # choose the move with the max value
            if val > v:
                v = val

    return v # , newDepth

# returns a utility value for MIN
def minVal(matrix, depth, positionsA, positionsB):
    global nodesExpdA

    # if state is a terminal state, then return the utility at that state
    # if depth == 3:
    #     return
    # print depth

    if len(positionsA) == 0 or len(positionsB) == 0 or (depth - 1) == 3:
        return of1(positionsA)

    if 'A' in matrix[height - 1] or 'B' in matrix[0]:
        return of1(positionsA)

    # if either positionsA or positionsB are empty, then return heuristic val

    # v = utility = +infinity
    # v = float('inf')
    v = 1000000 # 2**20
    # depth += 1
    actions = getActions('B', positionsB)

    # for each action in the world state,
    # result = world state after action
    # v = min(v, maxVal(result))
    for x, y in positionsB:
        for action in actions: # actionsB:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x - 1 >= 0 and y + 1 < width:
                    if result[x - 1][y + 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdA += 1
                    elif result[x - 1][y + 1] == 'A':
                        newPositionsA.remove((x - 1, y + 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'up':
                if x - 1 >= 0:
                    if result[x - 1][y] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y))
                        result[x][y] = '_'
                        result[x - 1][y] = 'B'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x - 1 >= 0 and y - 1 >= 0:
                    if result[x - 1][y - 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdA += 1
                    elif result[x - 1][y - 1] == 'A':
                        newPositionsA.remove((x - 1, y - 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue

            if (depth - 1) < 3:
                val = maxVal(result, depth + 1, newPositionsA, newPositionsB)
            else:
                # newDepth = depth
                # val = randint(1, 10)
                val = of1(newPositionsA)

            # choose the move with the min value
            if val < v:
                v = val

    return v # , newDepth

# returns an action arg max_(a in ACTIONS(state)) minVal(result(state, a))
def minimaxSearch(matrix, depth, positionsA, positionsB):
    global nodesExpdA
    player = 'A'

    # action = default action
    # actions = getActions(matrix, player, positionsA)
    # move = ('down', (1, 0))
    v = -1000000
    # depth += 1
    actions = getActions('A', positionsA)

    # for each action in the world state,
    # result = world state after action
    # v = minVal(result)
    for x, y in positionsA:
        for action in actions: # actionsA:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x + 1 < height and y + 1 < width:
                    if result[x + 1][y + 1] == '_':
                        newPositionsA.remove((x,y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y + 1] == 'B':
                        newPositionsB.remove((x + 1, y + 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'down':
                if x + 1 < height:
                    if result[x + 1][y] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y))
                        result[x][y] = '_'
                        result[x + 1][y] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x + 1 < height and y - 1 >= 0:
                    if result[x + 1][y - 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y - 1] == 'B':
                        newPositionsB.remove((x + 1, y - 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue

            val = minVal(result, depth + 1, newPositionsA, newPositionsB)

            # val = randint(1, 10)
            # choose the move with the max value
            # print val, v, action, x, y
            if val >= v:
                v = val
                move = (action, (x, y))

            # if depth =


    # print depth + 1 # newDepth
    # print move
    return move


# ------------------------------- ALPHA BETA --------------------------------- #

# returns a utility value for MAX
def minValAB(matrix, depth, positionsA, positionsB, alpha, beta):
    global nodesExpdB

    # if state is a terminal state, then return the utility at that state
    # if depth == 3:
    #     return

    if len(positionsA) == 0 or len(positionsB) == 0 or (depth - 1) == 3:
        return dh2(positionsB)

    if 'A' in matrix[height - 1] or 'B' in matrix[0]:
        return dh2(positionsB)

    # v = utility = +infinity
    # v = float('+inf')
    v = 1000000 # 2**20
    actions = getActions('A', positionsA)

    # for each action in the world state,
    # result = world state after action
    # v = min(v, maxVal(result))
    for x, y in positionsA:
        for action in actions:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x + 1 < height and y + 1 < width:
                    if result[x + 1][y + 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdB += 1
                    elif result[x + 1][y + 1] == 'B':
                        newPositionsB.remove((x + 1, y + 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'down':
                if x + 1 < height:
                    if result[x + 1][y] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y))
                        result[x][y] = '_'
                        result[x + 1][y] = 'A'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x + 1 < height and y - 1 >= 0:
                    if result[x + 1][y - 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdB += 1
                    elif result[x + 1][y - 1] == 'B':
                        newPositionsB.remove((x + 1, y - 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue

            if (depth - 1) < 4:
                val = maxValAB(result, depth + 1, newPositionsA, newPositionsB, alpha, beta)
            else:
                # newDepth = depth
                # val = randint(1, 10)
                val = dh2(newPositionsB)

            # choose the move with the min value
            if val < v:
                v = val
            if v <= alpha:
                return v
            if v < beta:
                beta = v

    return v  # newDepth

# returns a utility value for MIN
def maxValAB(matrix, depth, positionsA, positionsB, alpha, beta):
    global nodesExpdB

    # if state is a terminal state, then return the utility at that state
    # if depth == 3:
    #     return

    if len(positionsA) == 0 or len(positionsB) == 0 or (depth - 1) == 3:
        return dh2(positionsB)

    if 'A' in matrix[height - 1] or 'B' in matrix[0]:
        return dh2(positionsB)

    # v = utility = -infinity
    # v = float('-inf')
    v = -1000000 # -1 * (2**20)
    actions = getActions('B', positionsB)

    # for each action in the world state,
    # result = world state after action
    # v = max(v, minVal(result))
    for x, y in positionsB:
        for action in actions:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x - 1 >= 0 and y + 1 < width:
                    if result[x - 1][y + 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdB += 1
                    elif result[x - 1][y + 1] == 'A':
                        newPositionsA.remove((x - 1, y + 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'up':
                if x - 1 >= 0:
                    if result[x - 1][y] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y))
                        result[x][y] = '_'
                        result[x - 1][y] = 'B'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x - 1 >= 0 and y - 1 >= 0:
                    if result[x - 1][y - 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdB += 1
                    elif result[x - 1][y - 1] == 'A':
                        newPositionsA.remove((x - 1, y - 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue

            if (depth - 1) < 4:
                val = minValAB(result, depth + 1, newPositionsA, newPositionsB, alpha, beta)
            else:
                # newDepth = depth
                # val = randint(1, 10)
                val = dh2(newPositionsB)

            # choose the move with the min value
            if val > v:
                v = val
            if v >= beta:
                return v
            if v > alpha:
                alpha = v

    return v  # , newDepth

# returns an action arg max_(a in ACTIONS(state)) minVal(result(state, a))
def alphaBetaSearch(matrix, depth, positionsA, positionsB):
    global nodesExpdB
    player = 'B'
    v = -1000000

    actions = getActions(player, positionsB)

    # for each action in the world state,
    # result = world state after action
    # v = maxVal(result)
    for x, y in positionsB:
        for action in actions:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x - 1 >= 0 and y + 1 < width:
                    if result[x - 1][y + 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdB += 1
                    elif result[x - 1][y + 1] == 'A':
                        newPositionsA.remove((x - 1, y + 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'up':
                if x - 1 >= 0:
                    if result[x - 1][y] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y))
                        result[x][y] = '_'
                        result[x - 1][y] = 'B'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x - 1 >= 0 and y - 1 >= 0:
                    if result[x - 1][y - 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdB += 1
                    elif result[x - 1][y - 1] == 'A':
                        newPositionsA.remove((x - 1, y - 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdB += 1
                    else:
                        continue
                else:
                    continue

            val = maxValAB(result, depth + 1, newPositionsA, newPositionsB, (-1) * 2**20, 2**20)

            # choose the move with the max value
            if val >= v:
                v = val
                move = (action, (x, y))

    print move
    return move


# ---------------------------- ALPHA BETA for A ------------------------------ #

# returns a utility value for MAX
def maxValAB_A(matrix, depth, positionsA, positionsB, alpha, beta):
    global nodesExpdA

    # if state is a terminal state, then return the utility at that state
    # if depth == 3:
    #     return

    if len(positionsA) == 0 or len(positionsB) == 0 or (depth - 1) == 3:
        return of2(positionsA)

    if 'A' in matrix[height - 1] or 'B' in matrix[0]:
        return of2(positionsA)

    # v = utility = +infinity
    # v = float('+inf')
    v = -1000000  # 2**20
    actions = getActions('A', positionsA)

    # for each action in the world state,
    # result = world state after action
    # v = min(v, maxVal(result))
    for x, y in positionsA:
        for action in actions:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x + 1 < height and y + 1 < width:
                    if result[x + 1][y + 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y + 1] == 'B':
                        newPositionsB.remove((x + 1, y + 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'down':
                if x + 1 < height:
                    if result[x + 1][y] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y))
                        result[x][y] = '_'
                        result[x + 1][y] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x + 1 < height and y - 1 >= 0:
                    if result[x + 1][y - 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y - 1] == 'B':
                        newPositionsB.remove((x + 1, y - 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue

            if (depth - 1) < 4:
                val = minValAB_A(result, depth + 1, newPositionsA, newPositionsB, alpha, beta)
            else:
                # newDepth = depth
                # val = randint(1, 10)
                val = of2(newPositionsA)

            # choose the move with the max value
            if val > v:
                v = val
            if v >= beta:
                return v
            if v > alpha:
                alpha = v

    return v  # newDepth


# returns a utility value for MIN
def minValAB_A(matrix, depth, positionsA, positionsB, alpha, beta):
    global nodesExpdA

    # if state is a terminal state, then return the utility at that state
    # if depth == 3:
    #     return

    if len(positionsA) == 0 or len(positionsB) == 0 or (depth - 1) == 3:
        return of2(positionsA)

    if 'A' in matrix[height - 1] or 'B' in matrix[0]:
        return of2(positionsA)

    # v = utility = -infinity
    # v = float('-inf')
    v = 1000000  # -1 * (2**20)
    actions = getActions('B', positionsB)

    # for each action in the world state,
    # result = world state after action
    # v = max(v, minVal(result))
    for x, y in positionsB:
        for action in actions:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x - 1 >= 0 and y + 1 < width:
                    if result[x - 1][y + 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdA += 1
                    elif result[x - 1][y + 1] == 'A':
                        newPositionsA.remove((x - 1, y + 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y + 1))
                        result[x][y] = '_'
                        result[x - 1][y + 1] = 'B'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'up':
                if x - 1 >= 0:
                    if result[x - 1][y] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y))
                        result[x][y] = '_'
                        result[x - 1][y] = 'B'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x - 1 >= 0 and y - 1 >= 0:
                    if result[x - 1][y - 1] == '_':
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdA += 1
                    elif result[x - 1][y - 1] == 'A':
                        newPositionsA.remove((x - 1, y - 1))
                        newPositionsB.remove((x, y))
                        newPositionsB.append((x - 1, y - 1))
                        result[x][y] = '_'
                        result[x - 1][y - 1] = 'B'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue

            if (depth - 1) < 4:
                val = maxValAB_A(result, depth + 1, newPositionsA,
                               newPositionsB, alpha, beta)
            else:
                # newDepth = depth
                # val = randint(1, 10)
                val = of2(newPositionsA)

            # choose the move with the min value
            if val < v:
                v = val
            if v <= alpha:
                return v
            if v < beta:
                beta = v

    return v  # , newDepth


# returns an action arg max_(a in ACTIONS(state)) minVal(result(state, a))
def alphaBetaSearchA(matrix, depth, positionsA, positionsB):
    global nodesExpdA
    player = 'A'
    v = -1000000

    actions = getActions(player, positionsA)

    # for each action in the world state,
    # result = world state after action
    # v = maxVal(result)
    for x, y in positionsA:
        for action in actions:
            result = copy.deepcopy(matrix)
            newPositionsA = copy.deepcopy(positionsA)
            newPositionsB = copy.deepcopy(positionsB)

            if action == 'right':
                if x + 1 < height and y + 1 < width:
                    if result[x + 1][y + 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y + 1] == 'B':
                        newPositionsB.remove((x + 1, y + 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y + 1))
                        result[x][y] = '_'
                        result[x + 1][y + 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'down':
                if x + 1 < height:
                    if result[x + 1][y] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y))
                        result[x][y] = '_'
                        result[x + 1][y] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue
            elif action == 'left':
                if x + 1 < height and y - 1 >= 0:
                    if result[x + 1][y - 1] == '_':
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    elif result[x + 1][y - 1] == 'B':
                        newPositionsB.remove((x + 1, y - 1))
                        newPositionsA.remove((x, y))
                        newPositionsA.append((x + 1, y - 1))
                        result[x][y] = '_'
                        result[x + 1][y - 1] = 'A'
                        nodesExpdA += 1
                    else:
                        continue
                else:
                    continue

            val = maxValAB_A(result, depth + 1, newPositionsA, newPositionsB, -1000000, 1000000)

            # choose the move with the max value
            if val >= v:
                v = val
                move = (action, (x, y))

    print move
    return move


# ---------------------------------- MAIN ------------------------------------ #

def main():
    if not os.path.exists(sys.argv[1]):
        print 'Input file does not exist'
        sys.exit(1)

    # parse input board as 2D char matrix
    global width, height, actionsA, actionsB, nodesExpdA, nodesExpdB
    actionsA = ['left', 'down', 'right']
    actionsB = ['left', 'up', 'right']

    width = height = 0
    matrix = []
    with open(sys.argv[1], 'r') as flowfree:
        for line in flowfree:
            line = line.strip()
            matrix.append(list(line))
            height += 1
        width = len(matrix[0])

    # for l in matrix: print l
    # print width, height

    # top player (black) = A, bottom player (white) = B

    # test minimax search
    '''
    start = time()
    action, (x, y) = minimaxSearch(matrix, 0, posA, posB)
    print (time() - start) * 1000

    if action == 'right':
        matrix[x][y] = '_'
        matrix[x + 1][y + 1] = 'A'
    elif action == 'down':
        matrix[x][y] = '_'
        matrix[x + 1][y] = 'A'
    elif action == 'left':
        matrix[x][y] = '_'
        matrix[x + 1][y - 1] = 'A'

    for l in matrix: print l
    '''

    # test alpha-beta search
    '''
    start = time()
    action, (x, y) = alphaBetaSearch(matrix, 0, posA, posB)
    print (time() - start) * 1000

    if action == 'right':
        matrix[x][y] = '_'
        matrix[x - 1][y + 1] = 'B'
    elif action == 'up':
        matrix[x][y] = '_'
        matrix[x - 1][y] = 'B'
    elif action == 'left':
        matrix[x][y] = '_'
        matrix[x - 1][y - 1] = 'B'

    for l in matrix: print l
    '''

    turn = countA = countB = 0
    timeA = timeB = avgTimeA = avgTimeB = 0
    nodesExpdA = nodesExpdB = totalNodesExpdA = totalNodesExpdB = avgNodesA = avgNodesB = 0
    winner = None
    posA, posB = getPositions(matrix)
    origPosA, origPosB = [copy.deepcopy(posA), copy.deepcopy(posB)]

    while(1):
        print 'turn: ' + str(turn)
        depth = 0

        # check if game is complete
        if 'A' in matrix[height - 1] or len(posB) == 0:
            winner = 'A'
            break
        elif 'B' in matrix[0] or len(posA) == 0:
            winner = 'B'
            break

        if turn == 0:
            # player A's turn
            timeA = time()
            action, (x, y) = alphaBetaSearchA(matrix, depth, posA, posB)
            # action, (x, y) = minimaxSearch(matrix, depth, posA, posB)
            if action == 'right':
                matrix[x][y] = '_'
                matrix[x + 1][y + 1] = 'A'
            elif action == 'down':
                matrix[x][y] = '_'
                matrix[x + 1][y] = 'A'
            elif action == 'left':
                matrix[x][y] = '_'
                matrix[x + 1][y - 1] = 'A'
            avgTimeA += (time() - timeA)
        elif turn == 1:
            # player B's turn
            timeB = time()
            action, (x, y) = alphaBetaSearch(matrix, depth, posA, posB)
            if action == 'right':
                matrix[x][y] = '_'
                matrix[x - 1][y + 1] = 'B'
            elif action == 'up':
                matrix[x][y] = '_'
                matrix[x - 1][y] = 'B'
            elif action == 'left':
                matrix[x][y] = '_'
                matrix[x - 1][y - 1] = 'B'
            avgTimeB += (time() - timeB)

        # calculate new positions
        posA, posB = getPositions(matrix)

        if turn == 0: countA += 1
        if turn == 1: countB += 1
        print 'Total moves: ' + str(countA + countB)

        # next turn
        turn = turn ^ 1

        totalNodesExpdA += nodesExpdA
        totalNodesExpdB += nodesExpdB
        nodesExpdA = nodesExpdB = 0

        # for l in matrix: print l

    avgNodesA = totalNodesExpdA / (countA + countB)
    avgNodesB = totalNodesExpdB / (countA + countB)
    avgTimeA /= countA + countB
    avgTimeB /= countA + countB

    print '\n----------------------------------------------------------------\n'
    print 'Player ' + winner + ' wins!\n'

    print 'Total number of nodes expanded by player A: ' + str(totalNodesExpdA)
    print 'Avg number of nodes expanded by player A: ' + str(avgNodesA)
    print 'Avg time per move for player A: ' + str(avgTimeA)
    print 'Number of workers captured by player A: ' + str(len(origPosA) - len(posA))
    print 'Number of moves made by player A: ' + str(countA) + '\n'

    print 'Total number of nodes expanded by player B: ' + str(totalNodesExpdB)
    print 'Avg number of nodes expanded by player B: ' + str(avgNodesB)
    print 'Avg time per move for player B: ' + str(avgTimeB)
    print 'Number of workers captured by player B: ' + str(len(origPosB) - len(posB))
    print 'Number of moves made by player B: ' + str(countB) + '\n'

    for l in matrix: print l


if __name__ == "__main__":
    main()
