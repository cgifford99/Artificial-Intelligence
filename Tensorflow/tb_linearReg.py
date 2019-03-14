from __future__ import print_function

import tensorflow as tf # imports the tensorflow library as 'tf'

# Model parameters
weight = tf.Variable(tf.zeros([], dtype=tf.float32), name="weight") # creates a tensorflow variable (a type of tensor) and adds it to the graph
bias = tf.Variable(tf.zeros([], dtype=tf.float32), name="bias") # creates another tensorflow variable
# Model input and output
x = tf.placeholder(tf.float32, name="x") # creates a tensorflow placeholder. Similar to a variable, but gets fed data later on
y = tf.placeholder(tf.float32, name="y") # creates another tensorflow placeholder.
linear_model = (weight * x) + bias # just a simple linear model to use for training

# Loss
loss = tf.reduce_sum(tf.square(linear_model - y))  # sum of squares
# Optimizer
optimizer = tf.train.GradientDescentOptimizer(0.01)  # changing 0.01 to 0.029 lowers loss?
# Implements gradient descent algorithm and constructs a gradient descent optimizer with a learning rate of 0.01
train = optimizer.minimize(loss) # computes gradients of 'loss' and applies them to the "train" variable

# Training data
x_train = [1, 2, 3, 4] # training data
y_train = [0, 1, 2, 3] # training data

# Training loop
init = tf.global_variables_initializer() # initializes all tensorflow elements
sess = tf.Session() # tensorflow session: required to run anything tensorflow

# Scalar definition
weightScalar = tf.summary.scalar("weights", weight) # Invalid argument error: tags and values not the same shape: [] != [1] (tag 'weights')
biasScalar = tf.summary.scalar("Bias", bias)
lossScalar = tf.summary.scalar("Loss", loss)

# Graph definition
writer = tf.summary.FileWriter("output", sess.graph)
summary_op = tf.summary.merge_all()
sess.run(init) # executes variable initialization

# Run session
for i in range(1000):
    sess.run(train, {x: x_train, y: y_train})
    summaryWeight = sess.run(weightScalar, {x: x_train, y: y_train})
    summaryBias = sess.run(biasScalar, {x: x_train, y: y_train})
    summaryLoss = sess.run(lossScalar, {x: x_train, y: y_train})
    writer.add_summary(summaryWeight, i)
    writer.add_summary(summaryBias, i)
    writer.add_summary(summaryLoss, i)

# Evaluation
curr_W, curr_b, curr_loss = sess.run([weight, bias, loss], {x: x_train, y: y_train})
# changes final values of tf.variables to regular variables
print("W: %s b: %s loss: %s" % (curr_W, curr_b, curr_loss)) # prints results