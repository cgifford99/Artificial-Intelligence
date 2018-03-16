import tensorflow as tf
import pandas as pd
import os

currentUser = os.environ.get('USERNAME')

basePath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence' % currentUser
dataPath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence\\datasets\\2554\\download\\texts' % currentUser
trainPath = os.path.join(basePath, "training.csv")
testPath = os.path.join(basePath, "testing.csv")

columnNames = ["featureTag-2", "featureTag-1", "featureTag1", "featureTag2", "labelTag"]

steps = 10000
batchSize = 1

def load_data(path, file):
    data = pd.read_csv(path,
                       names = columnNames,
                       header = 0)
    dataFeats, dataLabel = data, data.drop([columnNames[0], columnNames[1], columnNames[2], columnNames[3]], axis=1)

    return dataFeats, dataLabel



def __model(features, labels, mode, params):
    net = tf.feature_column.input_layer(features, params['feature_columns'])
    labelsInt = tf.feature_column.input_layer(labels, params['labels'])
    for units in params['hidden_units']:
        net = tf.layers.dense(net, units=units, activation=tf.nn.relu)

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
    loss = tf.nn.softmax_cross_entropy_with_logits_v2(labels=labelsInt, logits=logits)

    # Compute evaluation metrics.
    labelsInt = tf.transpose(labelsInt)
    accuracy = tf.metrics.accuracy(labels=labelsInt,
                                   predictions=predicted_classes,
                                   name='acc_op')
    metrics = {'accuracy': accuracy}
    tf.summary.scalar('accuracy', accuracy[1])

    if mode == tf.estimator.ModeKeys.EVAL:
        return tf.estimator.EstimatorSpec(
            mode, loss=loss, eval_metric_ops=metrics)

    # Create training op.
    assert mode == tf.estimator.ModeKeys.TRAIN

    optimizer = tf.train.AdagradOptimizer(learning_rate=0.1)
    train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())


    return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

def __train(features, labels, batchSizeP):
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), dict(labels)))
    dataset = dataset.shuffle(1000000).repeat().batch(batchSizeP)
    return dataset

def __eval(features, labels, batchSizeP):
    features = dict(features)
    if labels is None:
        inputs = features
    else:
        labels = dict(labels)
        inputs = (features, labels)

    dataset = tf.data.Dataset.from_tensor_slices(inputs)

    assert batchSizeP is not None, "batchSizeP must not be None"
    dataset = dataset.batch(batchSizeP)

    return dataset

def main(argv):
    trainFeats, trainLabel = load_data(trainPath, "training.csv")
    testFeats, testLabel = load_data(testPath, "testing.csv")



    tagVocab =  ["AJ0", "AJ0-AV0", "AJ0-NN1", "AJ0-VVD", "AJ0-VVG", "AJ0-VVN", "AJC", "AJS", "AT0",
                 "AV0", "AV0-AJ0", "AVP", "AVP-PRP", "AVQ", "AVQ-CJS", "CJC", "CJS", "CJS-AVQ",
                 "CJS-PRP", "CJT", "CJT-DT0", "CRD", "CRD-PNI", "DPS", "DT0", "DT0-CJT", "DTQ",
                 "EX0", "ITJ", "NN0", "NN1", "NN1-AJ0", "NN1-NP0", "NN1-VVB", "NN1-VVG", "NN2",
                 "NN2-VVZ", "NP0", "NP0-NN1", "ORD", "PNI", "PNI-CRD", "PNP", "PNQ", "PNX", "POS",
                 "PRF", "PRP", "PRP-AVP", "PRP-CJS", "TO0", "UNC", "VBB", "VBD", "VBG", "VBI", "VBN",
                 "VBZ", "VDB", "VDD", "VDG", "VDI", "VDN", "VDZ", "VHB", "VHD", "VHG", "VHI", "VHN",
                 "VHZ", "VM0", "VVB", "VVB-NN1", "VVD", "VVD-AJ0", "VVD-VVN", "VVG", "VVG-AJ0",
                 "VVG-NN1", "VVI", "VVN", "VVN-AJ0", "VVN-VVD", "VVZ", "VVZ-NN2", "XX0", "ZZ0"]

    featureColumns = []
    for feature in trainFeats.keys():
        categoricalColumn = tf.feature_column.categorical_column_with_vocabulary_list(key=feature,
                                                                            vocabulary_list=tagVocab)
        embeddingColumn = tf.feature_column.embedding_column(categoricalColumn, dimension=3)
        featureColumns.append(embeddingColumn)

    labelColumn = []
    for key in trainLabel.keys():
        labelCategoricalColumn = tf.feature_column.categorical_column_with_vocabulary_list(key=key,
                                                                                vocabulary_list=tagVocab)
        labelEmbeddingColumn = tf.feature_column.indicator_column(labelCategoricalColumn)
        labelColumn.append(labelEmbeddingColumn)

    classifier = tf.estimator.Estimator(
        model_fn=__model,
        params={
            'feature_columns': featureColumns,
            'labels': labelColumn,
            'hidden_units': [10, 10],
            'n_classes': 87,
        })

    # print(trainFeats)
    # print(trainLabel)

    classifier.train(
        input_fn=lambda:__train(trainFeats, trainLabel, batchSize),
        steps=steps)

    evalResult = classifier.evaluate(
        input_fn=lambda:__eval(testFeats, testLabel, batchSize))

    print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**evalResult))

    # Generate predictions from the model
    expected = ['NN1', 'DTQ', 'VBZ']
    predict_x = {
        'featureTag-2': ["none", "none", "NN1"],
        'featureTag-1': ["none", "NN1", "DTQ"],
        'featureTag1': ["DTQ", "VBZ", "NN1"],
        'featureTag2': ["VBZ", "NN1", "PUN"],
    }

    predictions = classifier.predict(
        input_fn=lambda: __eval(predict_x,
                                 labels=None,
                                 batchSizeP=batchSize))

    for pred_dict, expec in zip(predictions, expected):
        template = ('\nPrediction is "{}" ({:.1f}%), expected "{}"')

        class_id = pred_dict['class_ids'][0]
        probability = pred_dict['probabilities'][class_id]

        print(template.format(tagVocab[class_id],
                              100 * probability, expec))

if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)