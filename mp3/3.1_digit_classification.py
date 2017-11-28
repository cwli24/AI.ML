import sys
import os.path as osp
import numpy as np
import linecache as lnc
import math

# constants
SMOOTH_CONSTANT = 0.75   # can be any value in range 0.1 and 10, but the higher the better
FEAT_VALUES = 2         # f in {0,1}
IMG_WIDTH = 28
IMG_HEIGHT = 28
EC_IMG_WIDTH = 60
EC_IMG_HEIGHT = 70
NUM_CLASSES = 10
EC_NUM_CLASSES = 2
NUM_TRAINING_EXEMPLARS = 5000
NUM_TESTING_EXEMPLARS = 1000
EC_NUM_TRAINING_EXEMPLARS = 451
EC_NUM_TESTING_EXEMPLARS = 150

# path variables
digit_data_dpath = osp.dirname(__file__) + 'digitdata/'
train_data_fpath = digit_data_dpath + 'trainingimages.txt'
train_labels_fpath = digit_data_dpath + 'traininglabels.txt'
test_data_fpath = digit_data_dpath + 'testimages.txt'
test_labels_fpath = digit_data_dpath + 'testlabels.txt'

# global data structures
class_train_ct = [0]*NUM_CLASSES       # for digit classes 0-9
class_priors = [0.0]*NUM_CLASSES       # (float) P(class)
likelihood_matrices = map(np.matrix, [ [[0.0]*IMG_HEIGHT for _ in range(IMG_WIDTH)] ]*NUM_CLASSES)    # P(F_{ij} = f | class)
ec_likelihood_matrices = map(np.matrix, [ [[0.0]*EC_IMG_WIDTH for _ in range(EC_IMG_HEIGHT)] ]*NUM_CLASSES)    # P(F_{ij} = f | class)

class_guess = [None]*NUM_TESTING_EXEMPLARS
ec_class_guess = [None]*EC_NUM_TESTING_EXEMPLARS
class_test_ct = [0]*NUM_CLASSES
classification_rate = [0.0]*NUM_CLASSES
confusion_matrix = np.matrix([[0.0]*NUM_CLASSES for _ in range(NUM_CLASSES)])    # careful not to bamboozle yourself
prototypical_img_loc = [ (float('inf'), 0, float('-inf'), 0) ]*NUM_CLASSES    # minMAP, minIdx, maxMAP, maxIdx


# For main()
def compute_likelihood():
    # go through the features' counts and calculate their likelihood wrt each class with Laplace smoothing
    for class_index in range(len(class_train_ct)):
        likelihood_matrices[class_index] = (likelihood_matrices[class_index] + SMOOTH_CONSTANT) / float(class_train_ct[class_index] + FEAT_VALUES*SMOOTH_CONSTANT)

    # compute priors
    for class_index in range(len(class_train_ct)):
        class_priors[class_index] = class_train_ct[class_index] / float(NUM_TRAINING_EXEMPLARS)

def print_highest_lowest_MAP_images():
    for digit in range(len(prototypical_img_loc)):
        _, min_MAP_img_idx, _, max_MAP_img_idx = prototypical_img_loc[digit]

        print 'Test example with lowest posterior probability for class %d:' % digit
        for line_no in range(min_MAP_img_idx*IMG_HEIGHT, (min_MAP_img_idx + 1)*IMG_HEIGHT):
            print lnc.getline(test_data_fpath, line_no).strip('\n')

        print 'Test example with highest posterior probability for class %d:' % digit
        for line_no in range(max_MAP_img_idx*IMG_HEIGHT, (max_MAP_img_idx + 1)*IMG_HEIGHT):
            print lnc.getline(test_data_fpath, line_no).strip('\n')

def get_confusing_idx(confusion_matrix):
    # get row, col for cells with max confusion rate
    most_confusing = []

    for i in range(NUM_CLASSES): confusion_matrix[i, i] = 0.0

    # flatten matrix, get top 4 indices
    flat = (np.asarray(confusion_matrix)).flatten()
    idx = flat.argsort()[-4:]

    # convert the 1D indices back into 2D indices
    x_idx, y_idx = np.unravel_index(idx, (np.asarray(confusion_matrix)).shape)

    for x, y in zip(x_idx, y_idx):
        most_confusing.append((x, y))

    return most_confusing


# For extra_credit()
def ec_compute_likelihood():
    # go through the features' counts and calculate their likelihood wrt each class with Laplace smoothing
    for class_index in range(len(class_train_ct)):
        ec_likelihood_matrices[class_index] = (ec_likelihood_matrices[class_index] + SMOOTH_CONSTANT) / float(class_train_ct[class_index] + FEAT_VALUES*SMOOTH_CONSTANT)

    # compute priors
    for class_index in range(len(class_train_ct)):
        class_priors[class_index] = class_train_ct[class_index] / float(EC_NUM_TRAINING_EXEMPLARS)

def ec_print_highest_lowest_MAP_images():
    for digit in range(len(prototypical_img_loc)):
        _, min_MAP_img_idx, _, max_MAP_img_idx = prototypical_img_loc[digit]

        print 'Test example with lowest posterior probability for class %d:' % digit
        for line_no in range(min_MAP_img_idx*EC_IMG_HEIGHT, (min_MAP_img_idx + 1)*EC_IMG_HEIGHT):
            print lnc.getline('facedata/facedatatest', line_no).strip('\n')

        print 'Test example with highest posterior probability for class %d:' % digit
        for line_no in range(max_MAP_img_idx*EC_IMG_HEIGHT, (max_MAP_img_idx + 1)*EC_IMG_HEIGHT):
            print lnc.getline('facedata/facedatatest', line_no).strip('\n')

def ec_get_confusing_idx(confusion_matrix):
    # get row, col for cells with max confusion rate
    most_confusing = []

    for i in range(NUM_CLASSES): confusion_matrix[i, i] = 0.0

    # flatten matrix, get top 4 indices
    flat = (np.asarray(confusion_matrix)).flatten()
    idx = flat.argsort()[-4:]

    # convert the 1D indices back into 2D indices
    x_idx, y_idx = np.unravel_index(idx, (np.asarray(confusion_matrix)).shape)

    for x, y in zip(x_idx, y_idx):
        most_confusing.append((x, y))

    return most_confusing


def main():
    ### TRAINING
    with open(train_data_fpath, 'r') as train_images, open(train_labels_fpath, 'r') as train_labels:
        for class_lbl in train_labels:
            class_num = int(class_lbl)

            # compute the feature values for this example training image
            train_img_fvals = np.matrix([[0]*IMG_HEIGHT for _ in range(IMG_WIDTH)])
            for row_idx in range(IMG_HEIGHT):
                row_data = train_images.readline()
                for col_idx in range(IMG_WIDTH):
                    if row_data[col_idx] == '+' or row_data[col_idx] == '#':
                        train_img_fvals[row_idx, col_idx] = 1
                    # else, feature value remains 0 for background pixel

            # accumulate feat val for each pixel of this class' global data storage structure
            likelihood_matrices[class_num] += train_img_fvals
            class_train_ct[class_num] += 1

    compute_likelihood()

    ### TESTING ###
    with open(test_data_fpath, 'r') as test_images:

        for nth_img in range(NUM_TESTING_EXEMPLARS):
            class_MAP = [None]*NUM_CLASSES

            # grab pixel data -> features from this test image
            test_img_fvals = np.matrix([[0]*IMG_HEIGHT for _ in range(IMG_WIDTH)])
            for row_idx in range(IMG_HEIGHT):
                row_data = test_images.readline()
                for col_idx in range(IMG_WIDTH):
                    if row_data[col_idx] == '+' or row_data[col_idx] == '#':
                        test_img_fvals[row_idx, col_idx] = 1

            # figuring out the likelihood that each image belongs to a certain class
            for class_no in range(len(class_train_ct)):
                class_matrix = likelihood_matrices[class_no]

                # to avoid underflow, we work with the log of P(class)*P(f_{1,1}|class)*...*P(f_{28,28}|class)
                posterior_prob = math.log(class_priors[class_no])

                # calculate log P(class)+log P(f_{1,1}|class)+log P(f_{1,2}|class)+...+log P(f_{28,28}|class)
                for row_idx in range(IMG_HEIGHT):
                    for col_idx in range(IMG_WIDTH):
                        if test_img_fvals[row_idx, col_idx] == 1:
                            posterior_prob += math.log(class_matrix[row_idx, col_idx])
                        else:
                            posterior_prob += math.log(1 - class_matrix[row_idx, col_idx])

                # save the MAP prob for each class, determine test label guess based on argmax of values in array
                class_MAP[class_no] = posterior_prob

                # update the most and least "prototypical" instances of each digit class
                class_min_prob, min_idx, class_max_prob, max_idx = prototypical_img_loc[class_no]
                if posterior_prob < class_min_prob:
                    prototypical_img_loc[class_no] = (posterior_prob, nth_img, class_max_prob, max_idx)
                if posterior_prob > class_max_prob:
                    prototypical_img_loc[class_no] = (class_min_prob, min_idx, posterior_prob, nth_img)

            # closely matching test images have MAP ~1.0, which corresponds to (-) near 0 while MAP ~0 -> (-inf)
            class_guess[nth_img] = class_MAP.index(max(class_MAP))

    ### EVALUATION ###
    with open(test_labels_fpath, 'r') as test_labels:
        for nth_lbl in range(NUM_TESTING_EXEMPLARS):
            actual_class = int(test_labels.readline())

            if actual_class == class_guess[nth_lbl]:
                classification_rate[actual_class] += 1

            class_test_ct[actual_class] += 1
            confusion_matrix[actual_class, class_guess[nth_lbl]] += 1

    for idx in range(len(classification_rate)):
        # calculate the percentage of all test images of a given digit correctly classified
        classification_rate[idx] /= float(class_test_ct[idx])

        # entry in row r and column c is the percentage of test images from class r that are classified as class c
        for confusion_col in range(len(class_test_ct)):
            confusion_matrix[idx, confusion_col] /= float(class_test_ct[idx])

    # TO PRINT FOR REPORT, UNCOMMENT THESE:
    np.set_printoptions(precision=3)
    print classification_rate
    print confusion_matrix
    print_highest_lowest_MAP_images()

    def print_odds(matrix):
        for row_idx in range(IMG_HEIGHT):
            for col_idx in range(IMG_WIDTH):
                temp = math.log(matrix[row_idx, col_idx])
                if temp > -0.75 and temp < 1.25: print ' ',
                elif temp > 0: print '+',
                else: print '-',
            print ''

    def print_class(matrix):
        for row_idx in range(IMG_HEIGHT):
            for col_idx in range(IMG_WIDTH):
                temp = math.log(matrix[row_idx, col_idx])
                if temp > -1.1 and temp < -0.9: print ' ',
                elif temp > -1: print '+',
                else: print '-',
            print ''

    ### ODDS RATIO ###
    most_confusing_indices = get_confusing_idx(confusion_matrix)

    # for each pair of the 4 chosen pairs with highest confusion probability
    for c1, c2 in most_confusing_indices:
        class_1 = likelihood_matrices[c1]
        class_2 = likelihood_matrices[c2]
        class_odds = np.matrix([[0.0]*IMG_HEIGHT for _ in range(IMG_WIDTH)])
        for row_idx in range(IMG_HEIGHT):
            for col_idx in range(IMG_WIDTH):
                class_odds[row_idx, col_idx] = class_1[row_idx, col_idx]/class_2[row_idx, col_idx]

        print c1, c2
        print_class(class_1)
        print '\n'
        print_class(class_2)
        print '\n'
        print_odds(class_odds)
        print '\n'


# 451 training images
def extra_credit():
    ### TRAINING
    with open('facedata/facedatatrain', 'r') as train_images, open('facedata/facedatatrainlabels', 'r') as train_labels:
        for class_lbl in train_labels:
            class_num = int(class_lbl)

            # compute the feature values for this example training image
            train_img_fvals = np.matrix([[0]*EC_IMG_WIDTH for _ in range(EC_IMG_HEIGHT)])
            for row_idx in range(EC_IMG_HEIGHT):
                row_data = train_images.readline()
                for col_idx in range(EC_IMG_WIDTH):
                    if row_data[col_idx] == '#':
                        train_img_fvals[row_idx, col_idx] = 1
                    # else, feature value remains 0 for background pixel

            # accumulate feat val for each pixel of this class' global data storage structure
            ec_likelihood_matrices[class_num] += train_img_fvals
            class_train_ct[class_num] += 1

    ec_compute_likelihood()

    ### TESTING ###
    with open('facedata/facedatatest', 'r') as test_images:

        for nth_img in range(EC_NUM_TESTING_EXEMPLARS):
            class_MAP = [None]*NUM_CLASSES

            # grab pixel data -> features from this test image
            test_img_fvals = np.matrix([[0]*EC_IMG_WIDTH for _ in range(EC_IMG_HEIGHT)])
            for row_idx in range(EC_IMG_HEIGHT):
                row_data = test_images.readline()
                for col_idx in range(EC_IMG_WIDTH):
                    if row_data[col_idx] == '#':
                        test_img_fvals[row_idx, col_idx] = 1

            # figuring out the likelihood that each image belongs to a certain class
            for class_no in range(len(class_train_ct)):
                class_matrix = ec_likelihood_matrices[class_no]

                # to avoid underflow, we work with the log of P(class)*P(f_{1,1}|class)*...*P(f_{28,28}|class)
                try:
                    posterior_prob = math.log(class_priors[class_no])
                except ValueError:
                    print class_priors[class_no]
                    sys.exit()

                # calculate log P(class)+log P(f_{1,1}|class)+log P(f_{1,2}|class)+...+log P(f_{28,28}|class)
                for row_idx in range(EC_IMG_HEIGHT):
                    for col_idx in range(EC_IMG_WIDTH):
                        if test_img_fvals[row_idx, col_idx] == 1:
                            posterior_prob += math.log(class_matrix[row_idx, col_idx])
                        else:
                            posterior_prob += math.log(1 - class_matrix[row_idx, col_idx])

                # save the MAP prob for each class, determine test label guess based on argmax of values in array
                class_MAP[class_no] = posterior_prob

                # update the most and least "prototypical" instances of each digit class
                class_min_prob, min_idx, class_max_prob, max_idx = prototypical_img_loc[class_no]
                if posterior_prob < class_min_prob:
                    prototypical_img_loc[class_no] = (posterior_prob, nth_img, class_max_prob, max_idx)
                if posterior_prob > class_max_prob:
                    prototypical_img_loc[class_no] = (class_min_prob, min_idx, posterior_prob, nth_img)

            # closely matching test images have MAP ~1.0, which corresponds to (-) near 0 while MAP ~0 -> (-inf)
            ec_class_guess[nth_img] = class_MAP.index(max(class_MAP))

    ### EVALUATION ###
    with open('facedata/facedatatestlabels', 'r') as test_labels:
        for nth_lbl in range(EC_NUM_TESTING_EXEMPLARS):
            actual_class = int(test_labels.readline())

            if actual_class == ec_class_guess[nth_lbl]:
                classification_rate[actual_class] += 1

            class_test_ct[actual_class] += 1
            confusion_matrix[actual_class, ec_class_guess[nth_lbl]] += 1

    for idx in range(len(classification_rate)):
        # calculate the percentage of all test images of a given digit correctly classified
        classification_rate[idx] /= float(class_test_ct[idx])

        # entry in row r and column c is the percentage of test images from class r that are classified as class c
        for confusion_col in range(len(class_test_ct)):
            confusion_matrix[idx, confusion_col] /= float(class_test_ct[idx])

    # TO PRINT FOR REPORT, UNCOMMENT THESE:
    np.set_printoptions(precision=3)
    print classification_rate
    print confusion_matrix
    ec_print_highest_lowest_MAP_images()

    def print_odds(matrix):
        for row_idx in range(EC_IMG_HEIGHT):
            for col_idx in range(EC_IMG_WIDTH):
                temp = math.log(matrix[row_idx, col_idx])
                if temp > -0.75 and temp < 1.25: print ' ',
                elif temp > 0: print '+',
                else: print '-',
            print ''

    def print_class(matrix):
        for row_idx in range(EC_IMG_HEIGHT):
            for col_idx in range(EC_IMG_WIDTH):
                temp = math.log(matrix[row_idx, col_idx])
                if temp > -1.1 and temp < -0.9: print ' ',
                elif temp > -1: print '+',
                else: print '-',
            print ''

    ### ODDS RATIO ###
    most_confusing_indices = ec_get_confusing_idx(confusion_matrix)

    # for each pair of the 4 chosen pairs with highest confusion probability
    for c1, c2 in most_confusing_indices:
        class_1 = ec_likelihood_matrices[c1]
        class_2 = ec_likelihood_matrices[c2]
        class_odds = np.matrix([[0.0]*EC_IMG_WIDTH for _ in range(EC_IMG_HEIGHT)])
        for row_idx in range(EC_IMG_HEIGHT):
            for col_idx in range(EC_IMG_WIDTH):
                class_odds[row_idx, col_idx] = class_1[row_idx, col_idx]/class_2[row_idx, col_idx]

        print c1, c2
        print_class(class_1)
        print '\n'
        print_class(class_2)
        print '\n'
        print_odds(class_odds)
        print '\n'


def run():
    options = [0, 1, 2]
    while(True):
        input = raw_input('Choose main (0), extra credit (1), or exit (2): ')
        try:
            option = int(input)
        except Exception:
            print 'Not a number'
            continue

        if option in options:
            break
        else:
            print 'Try harder'

    if option == 0: main()
    elif option == 1: extra_credit()
    elif option == 2: sys.exit()


run()
