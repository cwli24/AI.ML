import numpy as np
import sys

# constants
NUM_TRAIN_GAMES = 50000
NUM_TEST_GAMES = 1000
GRID_DIM = (12, 12)     # columns x rows
ALPHAS_CONST = 10000    # the C of the learning rate: C/(C+N(s,a)) in [0,1]
GAMMA = 0.9             # discount factor in [0,1]
EPSILON = 0.05          # epsilon-greedy action selection policy

PADDLE_HEIGHT = 0.2
(BALL_X_MIN, BALL_X_MAX) = (0*GRID_DIM[0], 1*GRID_DIM[0]-1)   # paddle_x = ball_x_max
(BALL_Y_MIN, BALL_Y_MAX) = (0*GRID_DIM[1], 1*GRID_DIM[1]-1)
DEFAULT_STATE = (0.5, 0.5, 0.03, 0.01, 0.5-PADDLE_HEIGHT/2)

# global variables
ball_x = ball_y = velo_x = velo_y = paddle_y = None
game_over_state = (0,0,0,0,0)

def update_ball():
    '''Handles ball movements and logic for a single iteration in game loop. Returns reward value:
    -1  if update causes ball to passed agent's paddle (termination state);
    +1  if update results in a rebound by the paddle;
    0   otherwise (nothing significant happens).'''
    global ball_x, ball_y, velo_x, velo_y

    ball_x += velo_x
    ball_y += velo_y

    if ball_y < 0:
        # ball is below "screen" so flip pos & velo about y=0 line
        ball_y = -ball_y; velo_y = -velo_y
    elif ball_y > 1:
        # likewise, when above "screen", flip about y=MAX_Y line
        ball_y = 2 - ball_y; velo_y = -velo_y

    if ball_x < 0:
        ball_x = -ball_x; velo_x = -velo_x
    #elif ball_x >= 1:

def check_collision():
    if ball_x >= 1:
        if ball_y >= paddle_y and ball_y <= paddle_y+PADDLE_HEIGHT and ball_x == 1:
            # notice this is after y pos is fully determined; rebound case
            velo_y = velo_y + np.random.uniform(-0.03, np.nextafter(0.03, 1))
            velo_x = -velo_x + np.random.uniform(-0.015, np.nextafter(0.015, 1))

            # make sure that |velocity_x| > 0.03 and that it moves in opposite direction next
            # also limit velocities to < 1 in magnitude
            if velo_x > -0.03:  velo_x = -0.03
            elif velo_x < -1:   velo_x = -0.95
            if abs(velo_y) > 1:
                velo_y = 0.95 if velo_y > 0 else -0.95
            return 1
        else:
            return -1   #ball is either passed paddle or not at the same y pos

    return 0    #nothing exciting happened

def discretize_state():
    '''Transform all state variables to discrete versions'''
    disc_ball_x = int(ball_x*(GRID_DIM[0]-1))
    disc_ball_y = int(ball_y*(GRID_DIM[1]-1))
    disc_velo_x = np.sign(velo_x)
    disc_velo_y = np.sign(velo_y) if abs(velo_y) >= 0.015 else 0
    disc_pad_y = int(GRID_DIM[1] * paddle_y / (1 - PADDLE_HEIGHT)) if paddle_y != 1-PADDLE_HEIGHT else GRID_DIM[1]-1
    return (disc_ball_x, disc_ball_y, disc_velo_x, disc_velo_y, disc_pad_y)

def move_paddle(action):
    global paddle_y
    if action == 'up':
        paddle_y = paddle_y - 0.04 if paddle_y - 0.04 >= 0 else 0.0
    elif action == 'down':
        paddle_y = paddle_y + 0.04 if paddle_y + 0.04 <= 1-PADDLE_HEIGHT else 1-PADDLE_HEIGHT

def print_layout():
    bx, by, _, _, py = discretize_state()
    print '-------------------------------------------------'
    for j in range(GRID_DIM[1]):
        for i in range(GRID_DIM[0]):
            if i == bx and j == by:
                if i == 11 and j == py:
                    print '|oP',
                else:
                    print '| o',
            elif i == 11 and j == py:
                print '| P',
            else:
                print '|  ',
        print '|'
        print '-------------------------------------------------'

def main():
    Q_sa = {}   # (ball_x, ball_y, velo_x, velo_y, paddle_y) : [stay,pad_up,pad_down] utility values + ~ N(s,a)
    # initialize all Q value estimates to 0
    for col in range(GRID_DIM[0]):
        for row in range(GRID_DIM[1]):
            for vx in range(-1, 2, 2):      #{-1, 1}
                for vy in range(-1, 2):     #{-1, 0, 1}
                    for pad_y in range(GRID_DIM[1]):
                        Q_sa[(col, row, vx, vy, pad_y)] = [0.0]*3 + [0]*3
    Q_sa[game_over_state] = [-1.0]
    global ball_x, ball_y, velo_x, velo_y, paddle_y

    ### TRAINING ###
    for game in range(NUM_TRAIN_GAMES):
        ball_x, ball_y, velo_x, velo_y, paddle_y = DEFAULT_STATE

        while True:
            # discretize continuous global vars each step since dict keys is tuple of discretes
            # and save state to update its Q-val after ball update
            pre_state = discretize_state()

            r = check_collision()
            update_ball()

            post_state = discretize_state() if r != -1 else game_over_state

            if np.random.random() < EPSILON:
                # with a small probability, an action is selected at random
                a = np.random.randint(0, 3)
            else:
                # most of the time the action with the highest estimated reward (utility val) is chosen
                a = np.argmax(Q_sa[pre_state][:3])

            # take the determined action, then calculate post state & reward; a in {0,1,2} == {stay,up,down}
            if a == 1:
                move_paddle('up')
            elif a == 2:
                move_paddle('down')

            # perform TD learning by adjusting original state's Q value
            ALPHA = 0.3 #ALPHAS_CONST / float(ALPHAS_CONST + Q_sa[pre_state][3 + a])
            Q_sa[pre_state][a] += ALPHA*(r + GAMMA*max(Q_sa[post_state][:3]) - Q_sa[pre_state][a])
            Q_sa[pre_state][3 + a] += 1     #increment corresponding count N(s,a) after previous formula

            # check if we've reached terminal state
            if r == -1:
                break

    # with open('Q_sa.pickle', 'wb') as trained_Q_file:
    #     pickle.dump(Q_sa, trained_Q_file, protocol=pickle.HIGHEST_PROTOCOL)
    for k, v in Q_sa.iteritems():
        if sum(v) != 0:
            print k, v
    #sys.exit(0)

    ### TESTING ###
    total_consecutive_rebounds = 0.0
    for game in range(NUM_TEST_GAMES):
        ball_x, ball_y, velo_x, velo_y, paddle_y = DEFAULT_STATE
        consecutive_rebounds = 0

        while True:
            reward = check_collision()
            update_ball()
            state = discretize_state()
            best_action = np.argmax(Q_sa[state][:3])    #in {0,1,2}

            if best_action == 1:
                move_paddle('up')
            elif best_action == 2:
                move_paddle('down')

            if reward == -1:
                total_consecutive_rebounds += consecutive_rebounds
                print 'Consecutive rebounds before game over for game #%d: %d' % (game+1, consecutive_rebounds)
                break
            elif reward == 1:
                consecutive_rebounds += 1
    print 'The average number of times the ball rebounds in %d games: %f' % (NUM_TEST_GAMES, 
        total_consecutive_rebounds/NUM_TEST_GAMES) 

if __name__ == "__main__":
    main()
