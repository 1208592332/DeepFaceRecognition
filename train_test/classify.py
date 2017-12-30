from __future__ import division, print_function, absolute_import

import os
import numpy as np
from sklearn.svm import SVC
from sklearn.externals import joblib

where_to_dump_model = '/Users/sam/All-Program/App-DataSet/DeepFaceRecognition/data_models/classification_model'

class SVM():
    '''
    # The embeddings in a nutshell are features. The face image goes through a complex network and results in
    # embeddings that captures complex features of a face. SVM's are good at classifying small datasets.
    # SVM are also robust to over fitting. The idea here is that we would wanna learn a SVM classifier using the
    # embeddings as the feature space and see for the given embedding, how many times we are able to predict the
    # correct class
    '''
    
    def __init__(self):
        pass
    
    def train(self, embeddings, labels, iter_num=None):
        '''
        :param embeddings:   Embeddings of the image
        :param labels:       labels
        :return:
        '''
        model = SVC(kernel='linear', probability=True)
        model.fit(embeddings, labels)
        joblib.dump(model, os.path.join(where_to_dump_model, iter_num+"_svm.sav"))
        
    def classify(self, embeddings, iter_num=None):
        '''
        :param embeddings:
        :param iter_num:
        :return:
        '''
        model = joblib.load(os.path.join(where_to_dump_model, iter_num+"_svm.sav"))
        predLabels = model.predict_proba(embeddings)
        best_label_idx = np.argmax(predLabels, axis=1)
        print (predLabels)
        