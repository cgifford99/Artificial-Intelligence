from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import pandas as pd
import os

currentUser = os.environ.get('USERNAME')

basePath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence' % currentUser
dataPath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence\\datasets\\2554\\download\\texts' % currentUser
outputPath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence\\tensorboard output' % currentUser
trainPath = os.path.join(basePath, "training.csv")
testPath = os.path.join(basePath, "testing.csv")

columnNames = ["featureTag-2", "featureTag-1", "featureTag1", "featureTag2", "labelTag"]

tagVocab =  ["AJ0", "AJ0-AV0", "AJ0-NN1", "AJ0-VVD", "AJ0-VVG", "AJ0-VVN", "AJC", "AJS", "AT0",
                 "AV0", "AV0-AJ0", "AVP", "AVP-PRP", "AVQ", "AVQ-CJS", "CJC", "CJS", "CJS-AVQ",
                 "CJS-PRP", "CJT", "CJT-DT0", "CRD", "CRD-PNI", "DPS", "DT0", "DT0-CJT", "DTQ",
                 "EX0", "ITJ", "NN0", "NN1", "NN1-AJ0", "NN1-NP0", "NN1-VVB", "NN1-VVG", "NN2",
                 "NN2-VVZ", "NP0", "NP0-NN1", "ORD", "PNI", "PNI-CRD", "PNP", "PNQ", "PNX", "POS",
                 "PRF", "PRP", "PRP-AVP", "PRP-CJS", "TO0", "UNC", "VBB", "VBD", "VBG", "VBI", "VBN",
                 "VBZ", "VDB", "VDD", "VDG", "VDI", "VDN", "VDZ", "VHB", "VHD", "VHG", "VHI", "VHN",
                 "VHZ", "VM0", "VVB", "VVB-NN1", "VVD", "VVD-AJ0", "VVD-VVN", "VVG", "VVG-AJ0",
                 "VVG-NN1", "VVI", "VVN", "VVN-AJ0", "VVN-VVD", "VVZ", "VVZ-NN2", "XX0", "ZZ0"]

def load_data(path):
    data = pd.read_csv(path,
                       names = columnNames,
                       header = 0)
    dataFeats, dataLabel = data, data.pop(columnNames[4])

    return dataFeats, dataLabel

def set_sparse():
    # code for sparse features:
        # input feature column
        # check if present
        # return (dict??) with sparse 0/1
    dogs = 5


# questions:
# how are features interpreted?
# how are weights and biases incorporated?
# what is the output (in numeric terms)?


trainFeats, trainLabel = load_data(trainPath)
testFeats, testLabel = load_data(testPath)