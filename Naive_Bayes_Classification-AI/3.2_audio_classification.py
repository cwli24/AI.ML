import numpy as np
import linecache as lnc
import math, os, sys

### constants
SMOOTH_CONSTANT = 5   # can be any value in range 0.1 and 10, but the higher the better
FEAT_VALUES = 2         # f in {0,1}
SAMP_WIDTH = 10
SAMP_HEIGHT = 25
NUM_CLASSES = 2
NUM_TRAINING_YES = 140
NUM_TRAINING_NO = 131
NUM_TESTING_YES = 50
NUM_TESTING_NO = 50

UNSEGMENTED_LINES = 25
UNSEGMENTED_LINE_LEN = 150

### path variables
audio_data_dpath = os.path.dirname(__file__) + 'yesno/'
train_yes_fpath = audio_data_dpath + 'yes_train.txt'
train_no_fpath = audio_data_dpath + 'no_train.txt'
test_yes_fpath = audio_data_dpath + 'yes_test.txt'
test_no_fpath = audio_data_dpath + 'no_test.txt'

unseg_audio_dpath = os.path.dirname(__file__) + 'yesno2/'
training_ec_dpath = unseg_audio_dpath + 'training/'
yes_ec_dpath = unseg_audio_dpath + 'yes_test/'
no_ec_dpath = unseg_audio_dpath + 'no_test/'

### global data structures
class_train_ct = [NUM_TRAINING_YES, NUM_TRAINING_NO]        # for audio classes 'yes'-0 or 'no'-1
class_priors = [0.0]*NUM_CLASSES                            # (float) P(class)
likelihood_matrices = map(np.matrix, [ [[0.0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)] ]*NUM_CLASSES)    # P(F_{ij} = f | class)
class_guess = [None]*(NUM_TESTING_YES + NUM_TESTING_NO)
confusion_matrix = np.matrix([[0.0]*NUM_CLASSES for _ in range(NUM_CLASSES)])    # careful not to bamboozle yourself

def compute_likelihood_priors(model_matrices, class_ct):
    # go through the features' counts and calculate their likelihood wrt each class with Laplace smoothing
    for class_index in range(NUM_CLASSES):
        model_matrices[class_index] = (model_matrices[class_index] + SMOOTH_CONSTANT) / float(class_ct[class_index] + FEAT_VALUES*SMOOTH_CONSTANT)

        # compute priors
        class_priors[class_index] = class_ct[class_index] / float(sum(class_ct))

def calculate_classes_likelihood(model_matrices, test_matrix, is_ec_columns):
    class_MAP = [None]*NUM_CLASSES

    # figuring out the likelihood that each sample belongs to 'yes' or 'no' classes
    for which_class in range(NUM_CLASSES):
        class_matrix = model_matrices[which_class]

        # to avoid underflow, we work with the log of P(class)*P(f_{1,1}|class)*...*P(f_{25,10}|class)
        posterior_prob = math.log(class_priors[which_class])

        if not is_ec_columns:
            # calculate log P(class)+log P(f_{1,1}|class)+log P(f_{1,2}|class)+...+log P(f_{25,10}|class)
            for row_idx in range(SAMP_HEIGHT):
                for col_idx in range(SAMP_WIDTH):
                    if test_matrix[row_idx, col_idx] == 1:
                        posterior_prob += math.log(class_matrix[row_idx, col_idx])
                    else:
                        posterior_prob += math.log(1 - class_matrix[row_idx, col_idx])
        else:
            for row_idx in range(SAMP_HEIGHT):
                posterior_prob += math.log( test_matrix[row_idx, 0]*class_matrix[row_idx, 0] +
                    (1 - test_matrix[row_idx, 0])*(1 - class_matrix[row_idx, 0]) )

        # save the MAP prob for each class, determine test guess based on argmax of values
        class_MAP[which_class] = posterior_prob
    return class_MAP

def main():
    ### TRAINING
    with open(train_yes_fpath, 'r') as train_yes, open(train_no_fpath, 'r') as train_no:
        for y_ex in range(class_train_ct[0]):
            train_aud_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
            for row_idx in range(SAMP_HEIGHT):
                row_data = train_yes.readline()
                for col_idx in range(SAMP_WIDTH):
                    if row_data[col_idx] == ' ':
                        train_aud_fvals[row_idx, col_idx] = 1
                    # else, feature value remains 0 for low energy frequency
            #skip three empty lines
            for empty_line in range(3):
                train_yes.readline()

            # accumulate feat val for each frequency-time of this class' global data storage structure
            likelihood_matrices[0] += train_aud_fvals

        for n_ex in range(class_train_ct[1]):
            train_aud_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
            for row_idx in range(SAMP_HEIGHT):
                row_data = train_no.readline()
                for col_idx in range(SAMP_WIDTH):
                    if row_data[col_idx] == ' ':
                        train_aud_fvals[row_idx, col_idx] = 1
                    # else, feature value remains 0 for low energy frequency
            #skip three empty lines
            for empty_line in range(3):
                train_no.readline()

            # accumulate feat val for each frequency-time of this class' global data storage structure
            likelihood_matrices[1] += train_aud_fvals

    compute_likelihood_priors(likelihood_matrices, class_train_ct)

    ### TESTING ###
    with open(test_yes_fpath, 'r') as test_yes, open(test_no_fpath, 'r') as test_no:
        for nth_y_aud in range(NUM_TESTING_YES):
            # grab audio data -> features from this test sample
            test_aud_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
            for row_idx in range(SAMP_HEIGHT):
                row_data = test_yes.readline()
                for col_idx in range(SAMP_WIDTH):
                    if row_data[col_idx] == ' ':
                        test_aud_fvals[row_idx, col_idx] = 1
            for empty_line in range(3):
                test_yes.readline()

            class_MAP = calculate_classes_likelihood(likelihood_matrices, test_aud_fvals, False)

            # closely matching test audio have MAP ~1.0 (due to log)
            class_guess[nth_y_aud] = 0 if class_MAP[0] > class_MAP[1] else 1

        for nth_n_aud in range(NUM_TESTING_NO):
            # grab audio data -> features from this test sample
            test_aud_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
            for row_idx in range(SAMP_HEIGHT):
                row_data = test_no.readline()
                for col_idx in range(SAMP_WIDTH):
                    if row_data[col_idx] == ' ':
                        test_aud_fvals[row_idx, col_idx] = 1
            for empty_line in range(3):
                test_no.readline()

            class_MAP = calculate_classes_likelihood(likelihood_matrices, test_aud_fvals, False)

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
    print 'Part 2.1 Naive Bayes for binarized spectrogram (25x10 features):'
    print confusion_matrix

def extra_credit():
    class_train_ct = [0, 0]
    likelihood_matrices_columns = map(np.matrix, [ [[0.0] for _ in range(SAMP_HEIGHT)] ]*NUM_CLASSES)

    ### train the Part 2.1 classifier using an unsegmented version of the same data (bullet 1)
    for rawtext in os.listdir(training_ec_dpath):
        training_segments = []
        for char in rawtext:
            if char == '0' or char == '1':
                training_segments.append(int(char))
        with open(training_ec_dpath + rawtext, 'r') as textfile:
            rawdata = textfile.readlines()

        sum_of_cols = [0]*UNSEGMENTED_LINE_LEN
        for line in rawdata:
            for char_idx in range(UNSEGMENTED_LINE_LEN):
                if line[char_idx] == ' ':
                    sum_of_cols[char_idx] += 1

        current_range = []
        tuples_of_ranges = []
        i = 0
        while i < UNSEGMENTED_LINE_LEN:
            if sum_of_cols[i] == 0:
                if current_range:
                    tuples_of_ranges.append( (sum(current_range), i-len(current_range), i) )
                    current_range = []
            else:
                if len(current_range) < SAMP_WIDTH:
                    current_range.append(sum_of_cols[i])
                else:
                    tuples_of_ranges.append( (sum(current_range), i-SAMP_WIDTH, i) )
                    current_range.pop(0)
                    current_range.append(sum_of_cols[i])
            i += 1
        if current_range:
            tuples_of_ranges.append( (sum(current_range), UNSEGMENTED_LINE_LEN-len(current_range), UNSEGMENTED_LINE_LEN) )

        found_sample_ranges = []
        disjoint_ranges = set()
        tuples_of_ranges.sort()
        while tuples_of_ranges:
            _, start_col, end_col = tuples_of_ranges.pop()    # largest sum, [start, end) range
            if start_col not in disjoint_ranges and end_col-1 not in disjoint_ranges:
                found_sample_ranges.append((start_col, end_col))
                disjoint_ranges.update(range(start_col, end_col))

                if len(found_sample_ranges) == len(training_segments):
                    break
        assert len(found_sample_ranges) == len(training_segments), 'Algorithm did not find as many training samples as supposed to in file!'

        found_sample_ranges.sort()
        for sample_rangei in range(len(found_sample_ranges)):
            lbi, rbe = found_sample_ranges[sample_rangei]
            which_class = training_segments[sample_rangei]
            lb_offset = (SAMP_WIDTH - (rbe-lbi))/2 if rbe - lbi < SAMP_WIDTH else 0

            training_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
            for line_no, line in enumerate(rawdata):
                for char_no, char in enumerate(line[lbi:rbe]):
                    if char == ' ':     training_fvals[line_no, char_no + lb_offset] = 1
            likelihood_matrices[which_class] += training_fvals
            class_train_ct[which_class] += 1

    ## this snippet is for bullet 3 ##
    for corpus in range(NUM_CLASSES):
        for row in range(SAMP_HEIGHT):
            for col in range(SAMP_WIDTH):
                likelihood_matrices_columns[corpus][row, 0] += likelihood_matrices[corpus][row, col]
        likelihood_matrices_columns[corpus] /= SAMP_WIDTH
    ##################################

    compute_likelihood_priors(likelihood_matrices, class_train_ct)

    yes_tests = 0
    for yestext in os.listdir(yes_ec_dpath):
        yes_tests += 1

        testing_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
        with open(yes_ec_dpath + yestext, 'r') as yesfile:
            for row in range(SAMP_HEIGHT):
                line = yesfile.readline()
                for col in range(SAMP_WIDTH):
                    if line[col] == ' ':    testing_fvals[row, col] = 1

        class_MAP = calculate_classes_likelihood(likelihood_matrices, testing_fvals, False)
        if class_MAP[0] > class_MAP[1]:
            confusion_matrix[0, 1] += 1     # columns (guesses) are flipped because we map 0 to 'yes' but data maps it to 1
        else:
            confusion_matrix[0, 0] += 1
    for j in range(NUM_CLASSES):
        confusion_matrix[0, j] /= float(yes_tests)

    no_tests = 0
    for notext in os.listdir(no_ec_dpath):
        no_tests += 1

        testing_fvals = np.matrix([[0]*SAMP_WIDTH for _ in range(SAMP_HEIGHT)])
        with open(no_ec_dpath + notext, 'r') as nofile:
            for row in range(SAMP_HEIGHT):
                line = nofile.readline()
                for col in range(SAMP_WIDTH):
                    if line[col] == ' ':    testing_fvals[row, col] = 1

        class_MAP = calculate_classes_likelihood(likelihood_matrices, testing_fvals, False)
        if class_MAP[0] > class_MAP[1]:
            confusion_matrix[1, 1] += 1
        else:
            confusion_matrix[1, 0] += 1
    for j in range(NUM_CLASSES):
        confusion_matrix[1, j] /= float(no_tests)

    # TO PRINT FOR REPORT, UNCOMMENT THESE:
    print 'Part 2.1 EC Naive Bayes classification for binarized spectrogram (25x10 features):'
    print confusion_matrix

    ### classifying each test image by first computing the average column (bullet 3)
    compute_likelihood_priors(likelihood_matrices_columns, class_train_ct)  # again, keep in mind matrix[0] <-> no, [1] <-> yes
    confusion_matrix.fill(0)

    for yestext in os.listdir(yes_ec_dpath):
        testing_fvals = np.matrix([[0.0] for _ in range(SAMP_HEIGHT)])
        with open(yes_ec_dpath + yestext, 'r') as yesfile:
            for row in range(SAMP_HEIGHT):
                line = yesfile.readline()
                for col in range(SAMP_WIDTH):
                    if line[col] == ' ':    testing_fvals[row, 0] += 1
        testing_fvals /= SAMP_WIDTH

        class_MAP = calculate_classes_likelihood(likelihood_matrices_columns, testing_fvals, True)
        if class_MAP[0] > class_MAP[1]:
            confusion_matrix[0, 1] += 1
        else:
            confusion_matrix[0, 0] += 1
    for j in range(NUM_CLASSES):
        confusion_matrix[0, j] /= yes_tests

    for notext in os.listdir(no_ec_dpath):
        testing_fvals = np.matrix([[0.0] for _ in range(SAMP_HEIGHT)])
        with open(no_ec_dpath + notext, 'r') as nofile:
            for row in range(SAMP_HEIGHT):
                line = nofile.readline()
                for col in range(SAMP_WIDTH):
                    if line[col] == ' ':    testing_fvals[row, 0] += 1
        testing_fvals /= SAMP_WIDTH

        class_MAP = calculate_classes_likelihood(likelihood_matrices_columns, testing_fvals, True)
        if class_MAP[0] > class_MAP[1]:
            confusion_matrix[1, 1] += 1
        else:
            confusion_matrix[1, 0] += 1
    for j in range(NUM_CLASSES):
        confusion_matrix[1, j] /= no_tests

    # TO PRINT FOR REPORT, UNCOMMENT THESE:
    print 'Part 2.1 EC Naive Bayes classification for binarized spectrogram thru averaged columns (25x1 features):'
    print confusion_matrix

# only run one of these at a time
main()
# extra_credit()
