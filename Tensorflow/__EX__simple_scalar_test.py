import os
import time

import tensorflow as tf

out_dir = os.path.abspath(os.path.join(os.path.curdir, "runs", str(int(time.time()))))
if not os.path.isdir(out_dir):
  os.makedirs(out_dir)

x = tf.placeholder(tf.float32, name="x")

init_op = tf.global_variables_initializer()

summary_op = tf.summary.scalar("steps", x)

with tf.Session() as sess:
  sess.run(init_op)
  summary_writer = tf.summary.FileWriter(out_dir, sess.graph)
  for step in range(10):
    summary = sess.run(summary_op, feed_dict={x: step})
    summary_writer.add_summary(summary, step)