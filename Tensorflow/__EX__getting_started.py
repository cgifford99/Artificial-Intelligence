import tensorflow as tf

# Model parameters
W = tf.Variable([0], dtype=tf.float32)
b = tf.Variable([0], dtype=tf.float32)
# Model input and output
x = tf.placeholder(tf.float32)
y = tf.placeholder(tf.float32)
linear_model = W * x + b

# Loss
loss = tf.reduce_sum(tf.square(linear_model - y)) # sum of squares
# Optimizer
optimizer = tf.train.GradientDescentOptimizer(0.01) #changing 0.01 to 0.029 lowers loss?
train = optimizer.minimize(loss)

# Training data
x_train = [1, 2, 3, 4]
y_train = [0, 0.25, 0.5, 0.75]
# Training loop
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)
for i in range(1000):
    sess.run(train, {x: x_train, y: y_train})

# Evaluation
curr_W, curr_b, curr_loss = sess.run([W, b, loss], {x: x_train, y: y_train})
print("W: %s b: %s loss: %s" % (curr_W, curr_b, curr_loss))
