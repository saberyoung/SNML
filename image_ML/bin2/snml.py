description = ">> machine learning algorithm for images"
usage = "%prog  [options] "

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, ExtraTreesClassifier,
                              AdaBoostClassifier)
from sklearn import clone

from astroML.utils import completeness_contamination

import pandas as pd
import numpy as np
import pyfits,dlt40,os,sys
import matplotlib.pyplot as plt
from astropy.io import fits
from optparse import OptionParser

sys.path.append('lib/')
import read_data
import plot_data

#################################################    
if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-c", "--clobber",action="store_true",\
                  dest='clobber',default=False,help='clobber files')
    parser.add_option("--show", action="store_true",\
                  dest='show', default=False, \
                  help='show candidates one by one \t\t\t [%default]')  
    parser.add_option("-v", "--verbose",action="store_true",\
                  dest='verbose',default=False,help='Show statistics plot')
    parser.add_option("-d",dest="data",default='2457920',\
                    type=str,help='JD')
    parser.add_option("-s", "--size", dest="size",default='10',\
                    type=str,help='area_factor')
    option,args = parser.parse_args()
    if len(args) < 1:sys.argv.append('--help')

    show,clobber,verbose=option.show,option.clobber,option.verbose
    
    # read raw data: select all the data after a specific jd.
    jd = option.data #2457754??
    area_factor = option.size #s 20*20 pixels
    X,y=read_data.get_raw_data(jd,area_factor,clobber)    
    print X.shape,X
    raw_input('...')
    # if show==True, plot activated    
    plot_data.plot(X,y,show,verbose)
   
    # ?? some parameters for ML
    n_estimators =  120
    random_state = 0
    max_depth_dt = None # 2,5,8...
    max_depth_ab = 3

    models,modelnames = [DecisionTreeClassifier(max_depth=max_depth_dt),
                         RandomForestClassifier(n_estimators=n_estimators),
                         ExtraTreesClassifier(n_estimators=n_estimators),
                         AdaBoostClassifier(DecisionTreeClassifier(max_depth=max_depth_ab),
                         n_estimators=n_estimators)],['DecisionTree','RandomForest',
                         'ExtraTrees','AdaBoost']           
    # flatten data and split
    X =  X.reshape(X.shape[0], -1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=random_state)    
    n_samples_train, n_samples_test, n_features = y_train.shape[0], y_test.shape[0],X_train.shape[1]

    for model,modelname in zip(models,modelnames):  
        predictions = []
        clf = clone(model)
        clf = model.fit(X_train, y_train)
        scores = clf.score(X_test, y_test)
        print modelname,'score:',scores
        y_pred = clf.predict(X_test)
        predictions.append(y_pred)
        completeness, contamination = completeness_contamination(predictions, y_test)
        print "completeness", completeness
        print "contamination", contamination

        if verbose:
            # confusion matrix
            cnf_matrix = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=cnf_matrix.shape)
            cllist = []
            for ii,jj in zip(y_test,y_pred):
                cllist.append(ii)
                cllist.append(jj)
            classes=np.unique(cllist)
            plot_data.plot_confusion_matrix(cnf_matrix, classes=classes, normalize=False)            

            # Train error vs Test error
#            plot_data.plot_error(X, y, X_train, X_test, y_train, y_test)
