import tensorflow as tf
import pandas as pd
import numpy as np
import os

currentUser = os.environ.get('USERNAME')

basePath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence' % currentUser
dataPath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence\\datasets\\2554\\download\\texts' % currentUser
trainPath = os.path.join(basePath, "training.csv")
testPath = os.path.join(basePath, "testing.csv")

columnNames = ["featureTag-2", "featureTag-1", "featureTag1", "featureTag2", "labelTag"]

steps = 10000
batchSize = 128
# logits size [batch_size, n_classes]
# labels size [1(?), batch_size]
# increasing batchSize, increases loss by 100-200


def load_data(path, file):
    data = pd.read_csv(path,
                       names=columnNames,
                       header=0)

    dataFeats = data.drop(columnNames[4], axis=1)
    dataLabel = data.drop((columnNames[i] for i in range(4)), axis=1)

    return dataFeats, dataLabel


# def getID(database):
#     arr = []
#     for i in range(len(columnNames)):
#         for j in range(len(database[columnNames[i]])):
#             word = database[columnNames[i]][j]
#             if word not in arr:
#                 arr.append(word)
#
#     print(arr)
#     return arr


def convertData(dataArr, key, vocab):
    dataArr[key] = dataArr[key].astype('category')
    dataArr[key] = dataArr[key].cat.set_categories(vocab, ordered=True)
    dataArr[key] = dataArr[key].cat.codes
    dataArr[key] = dataArr[key].astype(np.int32)
    return dataArr[key]


def model(features, labels, mode, params):
    net = tf.feature_column.input_layer(features, params['feature_columns'])
    for units in params['hidden_units']:
        net = tf.layers.dense(net, units=units, activation=tf.nn.tanh)

    # Compute logits (1 per class).
    logits = tf.layers.dense(net, params['n_classes'], activation=None)

    # Compute predictions.
    predicted_classes = tf.argmax(logits, 1)
    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {
            'class_ids': predicted_classes[:, tf.newaxis],
            'probabilities': tf.nn.softmax(logits),
            'logits': logits,
        }
        return tf.estimator.EstimatorSpec(mode, predictions=predictions)

    # Compute loss.
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    # Compute evaluation metrics.
    accuracy = tf.metrics.accuracy(labels=labels,
                                   predictions=predicted_classes,
                                   name='acc_op')
    metrics = {'accuracy': accuracy}
    tf.summary.scalar('accuracy', accuracy[1])

    if mode == tf.estimator.ModeKeys.EVAL:
        return tf.estimator.EstimatorSpec(
            mode, loss=loss, eval_metric_ops=metrics)

    # Create training op.
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)


def __train(features, labels, batchSizeP):
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))
    # dataset converts labels to tensor???
    dataset = dataset.shuffle(10000000).repeat().batch(batchSizeP)
    return dataset


def __eval(features, labels, batchSizeP):
    features = dict(features)
    if labels is None:
        inputs = features
    else:
        labels = labels
        inputs = (features, labels)

    dataset = tf.data.Dataset.from_tensor_slices(inputs)

    assert batchSizeP is not None, "batchSizeP must not be None"
    dataset = dataset.batch(batchSizeP)

    return dataset


def main(argv):
    tagVocab = ['NP0', 'NN1', 'AVQ', 'VVZ', 'DT0', 'AT0', 'AJ0', 'NN1-VVB', 'CJT', 'PNP', 'VVB', 'TO0', 'VVI',
                'PRP', 'VBZ', 'VVN-AJ0', 'CJC', 'AV0', 'PUN', 'PNI', 'AJC', 'CJS', 'DPS', 'AJS', 'AJ0-VVG', 'NN2',
                'VVG', 'PRF', 'VM0', 'XX0', 'AJ0-NN1', 'VVN', 'AVQ-CJS', 'VBB', 'AVP', 'VVD-VVN', 'DT0-CJT', 'VHZ',
                'CJS-AVQ', 'VVD', 'VVN-VVD', 'PUL', 'PUR', 'VVB-NN1', 'VBI', 'ORD', 'NN1-AJ0', 'VVZ-NN2', 'NN2-VVZ',
                'PRP-AVP', 'VVG-AJ0', 'CRD', 'DTQ', 'PUQ', 'VHB', 'VBN', 'CJT-DT0', 'NN1-VVG', 'VVG-NN1', 'CJS-PRP',
                'AJ0-VVN', 'VBG', 'EX0', 'VDB', 'AJ0-VVD', 'UNC', 'NN0', 'VBD', 'NP0-NN1', 'VHI', 'NN1-NP0', 'POS',
                'AJ0-AV0', 'VVD-AJ0', 'VDZ','PNQ', 'AV0-AJ0', 'PNX', 'AVP-PRP', 'PRP-CJS', 'ITJ', 'VHD', 'ZZ0', 'VHN',
                'PNI-CRD', 'VDI', 'VDG','VDN', 'VHG', 'VDD', 'CRD-PNI']

    trainFeats, trainLabel = load_data(trainPath, "training.csv")
    testFeats, testLabel = load_data(testPath, "testing.csv")

    featureColumns = []
    for feature in trainFeats.keys():
        trainFeats[feature] = convertData(trainFeats, feature, tagVocab)
        testFeats[feature] = convertData(testFeats, feature, tagVocab)
        categoricalFeat = tf.feature_column.categorical_column_with_identity(key=feature, num_buckets=92)
        embeddingFeat = tf.feature_column.indicator_column(categoricalFeat)
        featureColumns.append(embeddingFeat)

    trainLabel = convertData(trainLabel, columnNames[4], tagVocab)
    testLabel = convertData(testLabel, columnNames[4], tagVocab)

    classifier = tf.estimator.Estimator(
        model_fn=model,
        params={
        'feature_columns': featureColumns,
        'hidden_units': [512, 256, 128, 64],
        'n_classes': 92
        })

    classifier.train(
        input_fn=lambda: __train(trainFeats, trainLabel, batchSize), steps=steps)

    evalResult = classifier.evaluate(
        input_fn=lambda: __eval(testFeats, testLabel, batchSize))

    print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**evalResult))

    # Generate predictions from the model
    expected = pd.DataFrame({
        'expect': ['NN1', 'DTQ', 'VBZ']})
    expected = convertData(expected, 'expect', tagVocab)

    columnNamesPredict = columnNames[:-1]
    predict = pd.DataFrame({
        'featureTag-2': ["nope", "nope", "NN1"],
        'featureTag-1': ["nope", "NN1", "DTQ"],
        'featureTag1': ["DTQ", "VBZ", "NN1"],
        'featureTag2': ["VBZ", "NN1", "PUN"],
    }, columns=columnNamesPredict)

    for i in range(len(columnNamesPredict)):
        predict[columnNamesPredict[i]] = convertData(predict, columnNamesPredict[i], tagVocab)


    predictions = classifier.predict(
        input_fn=lambda: __eval(predict,
                                labels=None,
                                batchSizeP=batchSize))


    for idx, val in enumerate(expected):
        expected[idx] = tagVocab[val]

    for pred_dict, expec in zip(predictions, expected):
        template = '\nPrediction is "{}" ({:.1f}%), expected "{}"'

        class_id = pred_dict['class_ids'][0]
        probability = pred_dict['probabilities'][class_id]

        print(template.format(tagVocab[class_id],
                              100 * probability, expec))


if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)