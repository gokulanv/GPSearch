# -*- coding: utf-8 -*-
"""GSP-2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BKC3pEr7BakPpPy1SgJXyJ_OFBduLUO_
"""

from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plot
import tensorflow as tf
import skopt
from skopt import gp_minimize, forest_minimize
from skopt.space import Real, Categorical, Integer
from tensorflow.python.keras import backend as K

# from skopt.plots import plot_convergence
# from skopt.plots import plot_objective, plot_evaluations
# from skopt.plots import plot_histogram, plot_objective_2D
from skopt.utils import use_named_args

#mat = loadmat('C:/Users/anikp/Desktop/Data/train_32x32.mat')
mat = loadmat('train_32x32.mat')
trainX = mat['X']
trainY = mat['y']

print(trainX.shape)
trainX = np.transpose(trainX,(3,0,1,2))
print(trainX.shape)
print(trainY.shape)

"""## Choose samples for train, test and validation"""

def create_n_samples(x_original, y_original, no_of_class_samples=100, no_of_classes=10):
    hmap = {}
    nums_list = np.arange(1,no_of_classes+1)
    X = []
    Y = []
    for num in nums_list:
        hmap[num] = 0

    for idx in range(len(x_original)):
        label = y_original[idx][0]
        if hmap[label] < no_of_class_samples:
            Y.append(label)
            hmap[label] = hmap[label] + 1
            X.append(x_original[idx])

    return np.asarray(X), np.asarray(Y)

no_of_training_samples = 1000
no_of_classes = 10
trX, trY = create_n_samples(trainX, trainY, no_of_training_samples, no_of_classes)
trY[trY==10] = 0

trY[trY==0].shape

idx=998
print(trY[idx])
plot.imshow(trX[idx])
plot.show()

plot.rcParams["figure.figsize"] = (20,20)
f, ax = plot.subplots(1, 10)

for i, j in enumerate(np.random.randint(0, trY.shape[0], size=10)):
    ax[i].axis('off')
    ax[i].set_title(trY[j])
    ax[i].imshow(trX[j,:,:,:])

train_data = trX.astype('float32') / 128.0 - 1
f, ax = plot.subplots(1, 10)

for i, j in enumerate(np.random.randint(0, trY.shape[0], size=10)):
    ax[i].axis('off')
    ax[i].set_title(trY[j])
    ax[i].imshow(train_data[j,:,:,:])

from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dense, MaxPooling2D
model = Sequential()

from keras.layers import Dropout
from keras import optimizers


def create_model(learning_rate, mini_batch_size, dropout_layer_1, dropout_layer_2,decay_rate):
  model = Sequential()
  model.add(Conv2D(32,(5,5), strides=(1,1), activation='relu', input_shape=(32, 32, 3)))
  model.add(MaxPooling2D((2, 2)))
  model.add(Conv2D(64,(3,3), strides=(1,1), activation='relu'))
  model.add(MaxPooling2D((2, 2)))
  model.add(Conv2D(128,(3,3), strides=(1,1), activation='relu'))
  model.add(Flatten())
  model.add(Dense(1024, activation='relu'))
  model.add(Dropout(dropout_layer_1))
  model.add(Dense(1024, activation='relu'))
  model.add(Dropout(dropout_layer_2))
  model.add(Dense(10, activation='softmax'))
 # updated_learning_rate = learning_rate/(1 + decay_rate * epochs)
  sgd = optimizers.SGD(lr=learning_rate,decay=decay_rate)
  model.compile(optimizer=sgd,
          loss='sparse_categorical_crossentropy',
          metrics=['accuracy'])
  return model



#history = model.fit(trX, trY, epochs=10, batch_size = 32)
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
import numpy as np
from keras.wrappers.scikit_learn import KerasClassifier
from keras.callbacks import LearningRateScheduler
import time
# epochs = 2
# model = KerasClassifier(create_model)
# hyperparameters = {'learning_rate' : [1e-5, 1e-4], 'mini_batch_size' : [32, 64],
#                   'dropout_layer_1':[0.1, 0.9],
#                   'dropout_layer_2':[ 0.5, 0.7], 'decay_rate': [0.01, 0.00005]}
# classifier_grid = GridSearchCV(model, hyperparameters, scoring = 'accuracy')
# tvX, tvY = create_n_samples(trainX, trainY, 50, 10)
# tvY[tvY==10] = 0
# start_time = time.time()
# classifier_grid.fit(trX, trY,epochs = 2)
# p = classifier_grid.predict(tvX)
# end_time = time.time()
# print(" The Optimal parameters combinations are : ", classifier_grid.best_params_)
# print(" The Best Accuracy achieved is : ", classifier_grid.best_score_ * 100.0, "%")
# print(" The time taken to run Grid Search is : ", end_time - start_time, "seconds")



range_learning_rate = Real(low=1e-6, high=1e-2, prior='log-uniform',name='learning_rate')
range_batch_size = Integer(low=32, high=512, name='batch_size')
range_dropout1 = Real(low = 0.1, high = 0.99, name = 'dropout1')
range_dropout2 = Real(low = 0.1, high = 0.99, name = 'dropout2')
range_decay_rate = Real(low=1e-5, high = 0.1, prior='log-uniform', name ='decay_rate')

dimensions = [range_learning_rate,range_batch_size,range_dropout1,range_dropout2,range_decay_rate]




path_best_model = '19_best_model.keras'
best_accuracy = 0.0
@use_named_args(dimensions=dimensions)
def fitness(learning_rate, batch_size,
            dropout1, dropout2, decay_rate):


    # Print the hyper-parameters.
    print('learning rate: {0:.1e}'.format(learning_rate))
    print('batch_size:', batch_size)
    print('dropout1:', dropout1)
    print('dropout2:', dropout2)
    print('Decay Rate: ', decay_rate)
    print()

    # Create the neural network with these hyper-parameters.
    model = create_model(learning_rate=learning_rate,
                         mini_batch_size =batch_size , dropout_layer_1 =dropout1 , dropout_layer_2 = dropout2, decay_rate = decay_rate)

    # Dir-name for the TensorBoard log-files.
    # log_dir = log_dir_name(learning_rate, batch_size,
    #             dropout1, dropout2, decay_rate)
    #
    # # Create a callback-function for Keras which will be
    # # run after each epoch has ended during training.
    # # This saves the log-files for TensorBoard.
    # # Note that there are complications when histogram_freq=1.
    # # It might give strange errors and it also does not properly
    # # support Keras data-generators for the validation-set.
    # callback_log = TensorBoard(
    #     log_dir=log_dir,
    #     histogram_freq=0,
    #     batch_size=32,
    #     write_graph=True,
    #     write_grads=False,
    #     write_images=False)

    # Use Keras to train the model.
    tvX, tvY = create_n_samples(trainX, trainY, 50, 10)
    tvY[tvY==10] = 0
    history = model.fit(x=trX,
                        y=trY,
                        epochs=3,
                        validation_data=(tvX,tvY))

    # Get the classification accuracy on the validation-set
    # after the last training-epoch.
    accuracy = history.history['val_accuracy'][-1]

    # Print the classification accuracy.
    print()
    print("Accuracy: {0:.2%}".format(accuracy))
    print()

    # Save the model if it improves on the best-found performance.
    # We use the global keyword so we update the variable outside
    # of this function.
    global best_accuracy

    # If the classification accuracy of the saved model is improved ...
    if accuracy > best_accuracy:
        # Save the new model to harddisk.
        model.save(path_best_model)

        # Update the classification accuracy.
        best_accuracy = accuracy

    # Delete the Keras model with these hyper-parameters from memory.
    del model

    # Clear the Keras session, otherwise it will keep adding new
    # models to the same TensorFlow graph each time we create
    # a model with a different set of hyper-parameters.
    K.clear_session()

    # NOTE: Scikit-optimize does minimization so it tries to
    # find a set of hyper-parameters with the LOWEST fitness-value.
    # Because we are interested in the HIGHEST classification
    # accuracy, we need to negate this number so it can be minimized.
    return -accuracy


search_result = gp_minimize(func=fitness,
                            dimensions=dimensions,
                            acq_func='EI', # Expected Improvement.
                            n_calls=40)
print('Found the best hyperparameters')
print(search_result.x)
print(search_result.fun)
