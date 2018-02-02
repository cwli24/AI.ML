"""
Train model and eval model helpers.
"""
from __future__ import print_function

import math
import numpy as np
from models.linear_regression import LinearRegression


def train_model(processed_dataset, model, learning_rate=0.001, batch_size=16,
                num_steps=1000, shuffle=True):
    """Implements the training loop of stochastic gradient descent.

    Performs stochastic gradient descent with the indicated batch_size.
    If shuffle is true:
        Shuffle data at every epoch, including the 0th epoch.
    If the number of example is not divisible by batch_size, the last batch
    will simply be the remaining examples.

    Args:
        processed_dataset(list): Data loaded from io_tools
        model(LinearModel): Initialized linear model.
        learning_rate(float): Learning rate of your choice
        batch_size(int): Batch size of your choise.
        num_steps(int): Number of steps to run the updated.
        shuffle(bool): Whether to shuffle data at every epoch.
    Returns:
        model(LinearModel): Returns a trained model.
    """
    # Perform gradient descent.
    x, y = processed_dataset

    for s in range(num_steps):
        if shuffle:
            p = np.arange(len(x))
            np.random.shuffle(p)
            x = x[p]
            y = y[p]
        rand_batch_num = np.random.randint(0, high=math.ceil(len(x)/float(batch_size)))
        x_batch = x[batch_size*rand_batch_num : batch_size*(rand_batch_num+1)]
        y_batch = y[batch_size*rand_batch_num : batch_size*(rand_batch_num+1)]
        update_step(x_batch, y_batch, model, learning_rate)

    return model


def update_step(x_batch, y_batch, model, learning_rate):
    """Performs on single update step, (i.e. forward then backward).

    Args:
        x_batch(numpy.ndarray): input data of dimension (N, ndims).
        y_batch(numpy.ndarray): label data of dimension (N, 1).
        model(LinearModel): Initialized linear model.
    """
    f = LinearRegression.forward(model, x_batch)
    delwL = LinearRegression.backward(model, f, y_batch)
    model.w = model.w - learning_rate*delwL

def train_model_analytic(processed_dataset, model):
    """Computes and sets the optimal model weights (model.w).

    Args:
        processed_dataset(list): List of [x,y] processed
            from utils.data_tools.preprocess_data.
        model(LinearRegression): LinearRegression model.
    """
    x, y = processed_dataset
    X = np.append(x, [[1]]*x.shape[0], axis=1)
    self.w = np.dot(np.dot(np.linalg.inv(np.dot(X.T, X)), X.T), y)

def eval_model(processed_dataset, model):
    """Performs evaluation on a dataset.

    Args:
        processed_dataset(list): Data loaded from io_tools.
        model(LinearModel): Initialized linear model.
    Returns:
        loss(float): model loss on data.
    """
    x, y = processed_dataset
    f = LinearRegression.forward(model, x)
    loss = LinearRegression.total_loss(model, f, y)

    return loss
