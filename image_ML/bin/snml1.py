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
from ini import *

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
    option,args = parser.parse_args()
    if len(args) < 1:sys.argv.append('--help')

    show,clobber,verbose=option.show,option.clobber,option.verbose
    
    params = read_default()  
    jd = params['global']['jd']
    area_factor = params['global']['area_factor'] 
    X,y=read_data.get_raw_data(jd,area_factor,clobber)    

    # if show==True, plot activated    
    plot_data.plot(X,y,show,verbose)
   
    # ?? some parameters for ML
    n_estimators =  int(params['ML']['n_estimators'])
    random_state = int(params['ML']['random_state'])
    max_depth_dt = int(params['ML']['max_depth_dt'])
    max_depth_ab = int(params['ML']['max_depth_ab'])
    test_size = float(params['ML']['test_size'])

    nmodel = params['global']['ml_model']
    models,modelnames = [DecisionTreeClassifier(max_depth=max_depth_dt),
                         RandomForestClassifier(n_estimators=n_estimators),
                         ExtraTreesClassifier(n_estimators=n_estimators),
                         AdaBoostClassifier(DecisionTreeClassifier(max_depth=max_depth_ab),
                         n_estimators=n_estimators)],['DecisionTree','RandomForest',
                         'ExtraTrees','AdaBoost']           
    # flatten data and split
    X =  X.reshape(X.shape[0], -1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size,random_state=random_state)    
    n_samples_train, n_samples_test, n_features = y_train.shape[0], y_test.shape[0],X_train.shape[1]

    flag = 0
    for model,modelname in zip(models,modelnames):       
        flag+=1
        if flag != int(nmodel):continue
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
