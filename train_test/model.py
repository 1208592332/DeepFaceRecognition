from __future__ import division, print_function, absolute_import
from nn.network import *

def trainModel_FT(imgShape, params, init_wght_type='random'):
    inpTensor = tf.placeholder(dtype=tf.float32, shape=[None, imgShape[0], imgShape[1], imgShape[2]])
    logging.info('SHAPE: inpTensor %s', str(inpTensor.shape))
    
    # Pad the input to make of actual size
    X = tf.pad(inpTensor, paddings=[[0, 0], [3, 3], [3, 3], [0, 0]])
    X = conv1(X, params)
    X = conv2(X, params)
    X = conv3(X, params)
    X = inception3a(X, params, trainable=False)
    X = inception3b(X, params, trainable=False)
    X = inception3c(X, params, trainable=False)
    X = inception4a(X, params, trainable=False)
    X = inception4e(X, params, trainable=False)
    if init_wght_type == 'pretrained':
        logging.info(
            'Initializing the last layer weights with inception pre-trained weight but the parameters are trainable')
        X = inception5a(X, params, trainable=True)
        X = inception5b(X, params, trainable=True)
        X = fullyConnected(X, params, trainable=True)
    elif init_wght_type == 'random':
        logging.info('Initializing the last layer weights with random values and the parameter is trainable')
        X = inception5a_FT(X)
        X = inception5b_FT(X)
        X = fullyConnected_FT(X, [736, 128])
    else:
        raise ValueError('Provide a valid weight initialization type')
    return dict(inpTensor=inpTensor, output=X)


def getInceptionEmbedding(imgShape, params):  # , which_model='inception', use_wght_type='random'):
    inpTensor = tf.placeholder(dtype=tf.float32, shape=[None, imgShape[0], imgShape[1], imgShape[2]])
    logging.info('SHAPE: inpTensor %s', str(inpTensor.shape))
    
    # Pad the input to make of actual size
    X = tf.pad(inpTensor, paddings=[[0, 0], [3, 3], [3, 3], [0, 0]])
    X = conv1(X, params)
    X = conv2(X, params)
    X = conv3(X, params)
    X = inception3a(X, params, trainable=False)
    X = inception3b(X, params, trainable=False)
    X = inception3c(X, params, trainable=False)
    X = inception4a(X, params, trainable=False)
    X = inception4e(X, params, trainable=False)
    X = inception5a(X, params, trainable=False)
    X = inception5b(X, params, trainable=False)
    X = fullyConnected(X, params, trainable=False)
    return dict(inpTensor=inpTensor, output=X)


# encodingDict = getEmbeddings([96, 96, 3], params=weightDict)

def getFineTunedEmbeddings(imgShape, params, trainableVars, sess):
    inpTensor = tf.placeholder(dtype=tf.float32, shape=[None, imgShape[0], imgShape[1], imgShape[2]])
    logging.info('SHAPE: inpTensor %s', str(inpTensor.shape))
    
    # Pad the input to make of actual size
    X = tf.pad(inpTensor, paddings=[[0, 0], [3, 3], [3, 3], [0, 0]])
    X = conv1(X, params)
    X = conv2(X, params)
    X = conv3(X, params)
    X = inception3a(X, params, trainable=False)
    X = inception3b(X, params, trainable=False)
    X = inception3c(X, params, trainable=False)
    X = inception4a(X, params, trainable=False)
    X = inception4e(X, params, trainable=False)
    for var in trainableVars:
        scope, name = var.name.split(':')[0].split('/')
        if len(params[scope][name]) != 0:
            var_ = sess.run(var)
            logging.info('Updating param with scope %s and name %s and shape %s with shape %s',
                         str(scope), str(name), str(params[scope][name].shape), str(var_.shape))
            params[scope][name] = var_
        else:
            print('It seems that the scope %s or variable %s didnt exist in the dictionary ' % (str(scope), str(name)))
    X = inception5a(X, params, trainable=False)
    X = inception5b(X, params, trainable=False)
    X = fullyConnected(X, params, trainable=False)
    return dict(inpTensor=inpTensor, output=X)


def trainEmbeddings(weightDict, init_wght_type):
    logging.info('INITIALIZING THE NETWORK !! ...............................')
    
    img_per_label = 6
    num_labels = 3
    alpha = 0.01
    learning_rate = 0.0001
    embeddingDict = trainModel_FT([96, 96, 3], params=weightDict,
                                  init_wght_type=init_wght_type)
    embeddingDict = loss(embeddingDict, img_per_label, num_labels, alpha)
    embeddingDict = optimize(embeddingDict, learning_rate)
    return embeddingDict

def summaryBuilder(sess, outFilePath):
    mergedSummary = tf.summary.merge_all()
    writer = tf.summary.FileWriter(outFilePath)
    writer.add_graph(sess.graph)
    return mergedSummary, writer