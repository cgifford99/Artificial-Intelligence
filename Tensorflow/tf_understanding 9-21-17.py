import tensorflow as tf

#tf.constant is essentially a variable in tensorflow
node1 = tf.constant(3.0, dtype=tf.float32)
node2 = tf.constant(4.0, dtype=tf.float32)
print(node1, node2)
#It ends up printing data information about the nodes, not the values

#To print the values of the nodes, run the computational graph within tf.session()
sess = tf.Session()
print("Node1:", sess.run(node1))
print("Node2:", sess.run(node2))

#To add two tf.constants, use tf.add
node3 = tf.add(node1, node2)
print("Node3:", sess.run(node3))

#Here we're just adding two values, just using a different method
a = tf.placeholder(tf.float32)
b = tf.placeholder(tf.float32)
adder_node = a + b
print("Adder_Node:", sess.run(adder_node, {a: 3, b: 4.5}))
print("Adder_Node:", sess.run(adder_node, {a: 6, b: 24}))

#Now we're just multiplying adder_node by 3 and printing it with multiple
#values of 'a' and 'b'
triple_adder_node = adder_node * 3
print("Triple_Adder_Node:", sess.run(triple_adder_node, {a: [2, 6], b: [4, 12]}))

#Now we're creating a trainable model. Why? I'm not exactly sure.
W = tf.Variable([8], dtype=tf.float32)
b = tf.Variable([-4], dtype=tf.float32)
x = tf.placeholder(tf.float32)
linear_model = W * x + b

#We need to initialize all tf.Variables() before printing anything
#in order for variables to work.
sess.run(tf.global_variables_initializer())
#Now we're running the trainable model with some test data
print(sess.run(linear_model, {x: [1, 2, 3, 4]}))

#This will create a loss function
#It will measure how far apart our model is from the provided data
#Although I'm not sure why the loss function works
y = tf.placeholder(tf.float32)
squared_deltas = tf.square(linear_model - y)
loss = tf.reduce_sum(squared_deltas)
print(sess.run(loss, {x: [1, 2, 3, 4], y: [0, -1, -2, -3]}))

#This is optimizing some stuff or something
optimizer = tf.train.GradientDescentOptimizer(0.001)
train = optimizer.minimize(loss)
for i in range(1000):
    sess.run(train, {x: [1, 2, 3, 4], y: [0, -1, -2, -3]})

print(sess.run([W, b]))
#Now the loss is 0


    
