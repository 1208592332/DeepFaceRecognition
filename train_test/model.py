from __future__ import division, print_function, absolute_import
from nn.loss import loss
from nn.network import *
from config import myNet, vars
import tensorflow as tf


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
                'Initializing the last layer weights with inception pre-trained weight but the parameters are '
                'trainable')
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
    return dict(inpTensor=inpTensor, embeddings=X)


def getEmbeddings(imgShape, params):
    inpTensor = tf.placeholder(dtype=tf.float32, shape=[None, imgShape[0], imgShape[1], imgShape[2]])
    logging.info('GET EMBEDDINGS: SHAPE: inpTensor %s', str(inpTensor.shape))
    
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
    return dict(inpTensor=inpTensor, embeddings=X)


def trainEmbeddings(weightDict, init_wght_type):
    logging.info('INITIALIZING THE NETWORK !! ...............................')
    
    with tf.name_scope("learning_rate"):
        global_step = tf.Variable(0, trainable=False)
        learning_rate = tf.train.exponential_decay(myNet['learning_rate'],
                                                   global_step * vars['batchSize'],  # Used for decay computation
                                                   vars['trainSize'],  # Decay steps
                                                   myNet['learning_rate_decay_rate'],  # Decay rate
                                                   staircase=True)
    tf.summary.scalar('learning_rate', learning_rate)
    
    embeddingDict = trainModel_FT(myNet['image_shape'], params=weightDict,
                                  init_wght_type=init_wght_type)
    
    embeddingDict['triplet_loss'] = loss(embeddingDict['embeddings'])
    
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(
            embeddingDict['triplet_loss'], global_step=global_step
    )
    embeddingDict['optimizer'] = optimizer
    
    embeddingDict['learning_rate'] = learning_rate
    return embeddingDict


def summaryBuilder(sess, outFilePath):
    mergedSummary = tf.summary.merge_all()
    writer = tf.summary.FileWriter(outFilePath)
    writer.add_graph(sess.graph)
    return mergedSummary, writer



