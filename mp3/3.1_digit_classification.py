import os.path as osp

digit_data_dpath = osp.dirname(__filename__) + 'digitdata/'
train_data_fpath = digit_data_dpath + 'trainingimages'
train_labels_fpath = digit_data_dpath + 'traininglabels'
test_data_fpath = digit_data_dpath + 'testimages'
test_labels_fpath = digit_data_dpath + 'testlabels'

