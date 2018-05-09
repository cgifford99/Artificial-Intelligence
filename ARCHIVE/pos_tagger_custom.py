import tensorflow as tf
import numpy as np
import pandas as pd
import os
import argparse

currentUser = os.environ.get('USERNAME')

basePath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence' % currentUser
dataPath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence\\datasets\\2554\\download\\texts' % currentUser
trainPath = os.path.join(basePath, "training.csv")
testPath = os.path.join(basePath, "testing.csv")

columnNames = ["featureTag-2", "featureTag-1", "featureTag1", "featureTag2", "labelTag"]

# def parseArgs():
#     parser = argparse.ArgumentParser()
#
#     # parser.add_argument("--embedding dims")
#     # steps
#     # batch size
#     # data path

def load_data(path, file):
    if file == "training.csv":
        global tagVocab
    data = pd.read_csv(path,
                       names=columnNames,
                       header=0)

    for i in range(len(columnNames)):
        data[columnNames[i]] = data[columnNames[i]].astype('category')

        tagVocab = data[columnNames[i]].cat.categories.tolist()

    dataBackup = data
    dataFeats = data.drop(columnNames[4], axis=1)
    dataLabel = dataBackup.drop((columnNames[i] for i in range(4)), axis=1)

    return dataFeats, dataLabel

def debug(tensor):
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    print(sess.run(tensor))

def embed(tensor):
    vocabularySize = len(tagVocab)
    embeddingSize = 91
    tagId = np.arange(0, 91)

    wordEmbeddings = tf.Variable(tensor, [91, 1])
    return tf.nn.embedding_lookup(wordEmbeddings, tagId)

trainFeats, trainLabel = load_data(trainPath, "training.csv")
testFeats, testLabel = load_data(testPath, "testing.csv")

embeddings = embed(trainLabel)

