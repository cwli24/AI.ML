import os.path as osp
import numpy as np
import linecache as lnc
import math

# constants
SMOOTH_CONSTANT = 0.1   # can be any value in range 0.1 and 10, but the higher the better
FEAT_VALUES = 2         # f in {0,1}
IMG_WIDTH = 10
IMG_HEIGHT = 25
NUM_CLASSES = 2
NUM_TRAINING_YES = 140
NUM_TRAINING_NO = 131
NUM_TESTING_YES = 50
NUM_TESTING_NO = 50

# path variables
audio_data_dpath = osp.dirname(__file__) + 'yesno/'
train_yes_fpath = audio_data_dpath + 'yes_train.txt'
train_no_fpath = audio_data_dpath + 'no_train.txt'
test_yes_fpath = audio_data_dpath + 'yes_test.txt'
test_no_fpath = audio_data_dpath + 'no_test.txt'

# global data structures
class_train_ct = [NUM_TRAINING_YES, NUM_TRAINING_NO]        # for audio classes 'yes'-0 or 'no'-1
class_priors = [0.0]*NUM_CLASSES                            # (float) P(class)
likelihood_matrices = map(np.matrix, [ [[0.0]*IMG_WIDTH for _ in range(IMG_HEIGHT)] ]*NUM_CLASSES)    # P(F_{ij} = f | class)

class_guess = [None]*(NUM_TESTING_YES + NUM_TESTING_NO)
confusion_matrix = np.matrix([[0.0]*NUM_CLASSES for _ in range(NUM_CLASSES)])    # careful not to bamboozle yourself
    
def compute_likelihood_priors():
    # go through the features' counts and calculate their likelihood wrt each class with Laplace smoothing
    for class_index in range(NUM_CLASSES):
        likelihood_matrices[class_index] = (likelihood_matrices[class_index] + SMOOTH_CONSTANT) / float(class_train_ct[class_index] + FEAT_VALUES*SMOOTH_CONSTANT)
    
    # compute priors
    for class_index in range(NUM_CLASSES):
        class_priors[class_index] = class_train_ct[class_index] / float(NUM_TRAINING_YES + NUM_TRAINING_NO)
            
# main():
### TRAINING
with open(train_yes_fpath, 'r') as train_yes, open(train_no_fpath, 'r') as train_no:
    for y_ex in range(class_train_ct[0]):
        train_aud_fvals = np.matrix([[0]*IMG_WIDTH for _ in range(IMG_HEIGHT)])
        for row_idx in range(IMG_HEIGHT):
            row_data = train_yes.readline()
            for col_idx in range(IMG_WIDTH):
                if row_data[col_idx] == ' ':
                    train_aud_fvals[row_idx, col_idx] = 1
                # else, feature value remains 0 for low energy frequency
        #skip three empty lines
        for empty_line in range(3):
            train_yes.readline()
        
        # accumulate feat val for each frequency-time of this class' global data storage structure
        likelihood_matrices[0] += train_aud_fvals
        
    for n_ex in range(class_train_ct[1]):
        train_aud_fvals = np.matrix([[0]*IMG_WIDTH for _ in range(IMG_HEIGHT)])
        for row_idx in range(IMG_HEIGHT):
            row_data = train_no.readline()
            for col_idx in range(IMG_WIDTH):
                if row_data[col_idx] == ' ':
                    train_aud_fvals[row_idx, col_idx] = 1
                # else, feature value remains 0 for low energy frequency
        #skip three empty lines
        for empty_line in range(3):
            train_no.readline()
        
        # accumulate feat val for each frequency-time of this class' global data storage structure
        likelihood_matrices[1] += train_aud_fvals

compute_likelihood_priors()

### TESTING ###
with open(test_yes_fpath, 'r') as test_yes, open(test_no_fpath, 'r') as test_no:
    for nth_y_aud in range(NUM_TESTING_YES):
        class_MAP = [None]*NUM_CLASSES
    
        # grab audio data -> features from this test sample
        test_aud_fvals = np.matrix([[0]*IMG_WIDTH for _ in range(IMG_HEIGHT)])
        for row_idx in range(IMG_HEIGHT):
            row_data = test_yes.readline()
            for col_idx in range(IMG_WIDTH):
                if row_data[col_idx] == ' ':
                    test_aud_fvals[row_idx, col_idx] = 1
        for empty_line in range(3):
            test_yes.readline()
        
        # figuring out the likelihood that each sample belongs to 'yes' or 'no' classes
        for which_class in range(NUM_CLASSES):
            class_matrix = likelihood_matrices[which_class]
        
            # to avoid underflow, we work with the log of P(class)*P(f_{1,1}|class)*...*P(f_{25,10}|class)
            posterior_prob = math.log(class_priors[which_class])
            
            # calculate log P(class)+log P(f_{1,1}|class)+log P(f_{1,2}|class)+...+log P(f_{25,10}|class)
            for row_idx in range(IMG_HEIGHT):
                for col_idx in range(IMG_WIDTH):
                    if test_aud_fvals[row_idx, col_idx] == 1:
                        posterior_prob += math.log(class_matrix[row_idx, col_idx])
                    else:
                        posterior_prob += math.log(1 - class_matrix[row_idx, col_idx])
                        
            # save the MAP prob for each class, determine test guess based on argmax of values
            class_MAP[which_class] = posterior_prob
            
        # closely matching test audio have MAP ~1.0 (due to log)
        class_guess[nth_y_aud] = 0 if class_MAP[0] > class_MAP[1] else 1

    for nth_n_aud in range(NUM_TESTING_NO):
        class_MAP = [None]*NUM_CLASSES
    
        # grab audio data -> features from this test sample
        test_aud_fvals = np.matrix([[0]*IMG_WIDTH for _ in range(IMG_HEIGHT)])
        for row_idx in range(IMG_HEIGHT):
            row_data = test_no.readline()
            for col_idx in range(IMG_WIDTH):
                if row_data[col_idx] == ' ':
                    test_aud_fvals[row_idx, col_idx] = 1
        for empty_line in range(3):
            test_no.readline()
        
        # figuring out the likelihood that each sample belongs to 'yes' or 'no' classes
        for which_class in range(NUM_CLASSES):
            class_matrix = likelihood_matrices[which_class]
        
            # to avoid underflow, we work with the log of P(class)*P(f_{1,1}|class)*...*P(f_{25,10}|class)
            posterior_prob = math.log(class_priors[which_class])
            
            # calculate log P(class)+log P(f_{1,1}|class)+log P(f_{1,2}|class)+...+log P(f_{25,10}|class)
            for row_idx in range(IMG_HEIGHT):
                for col_idx in range(IMG_WIDTH):
                    if test_aud_fvals[row_idx, col_idx] == 1:
                        posterior_prob += math.log(class_matrix[row_idx, col_idx])
                    else:
                        posterior_prob += math.log(1 - class_matrix[row_idx, col_idx])
                        
            # save the MAP prob for each class, determine test guess based on argmax of values
            class_MAP[which_class] = posterior_prob
            
        # closely matching test audio have MAP ~1.0 (due to log)
        class_guess[nth_n_aud + NUM_TESTING_YES] = 0 if class_MAP[0] > class_MAP[1] else 1
        
### EVALUATION ###
# confusion_matrix:
#
#    real\guesses |    yes    |    no    |
#    -------------------------------------
#        yes      |  (0, 0)   |  (0, 1)  |
#    -------------------------------------
#        no       |  (1, 0)   |  (1, 1)  |
#    -------------------------------------
for guess_idx in range(len(class_guess)):
    if guess_idx < NUM_TESTING_YES:
        # real = yes, guess = yes
        if class_guess[guess_idx] == 0:    confusion_matrix[0, 0] += 1
        # real = yes, guess = no
        else:    confusion_matrix[0, 1] += 1
    else:
        # real = no, guess = yes
        if class_guess[guess_idx] == 0:    confusion_matrix[1, 0] += 1
        # real = no, guess = no
        else:    confusion_matrix[1, 1] += 1

for row_idx in range(NUM_CLASSES):
    for col_idx in range(NUM_CLASSES):
        # assumption here is that the number of yes & no test samples are the same
        confusion_matrix[row_idx, col_idx] /= float(NUM_TESTING_YES)

# TO PRINT FOR REPORT, UNCOMMENT THESE: 
print confusion_matrix
