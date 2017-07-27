import glob,sys,os,random,re,math
import subprocess

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, ExtraTreesClassifier,
                              AdaBoostClassifier)
from sklearn import clone
from astroML.utils import completeness_contamination
import matplotlib.pyplot as plt

import numpy as np

sys.path.append('lib/')
import read_data_OPS,read_data_alice
import plot_data


# 2 origin for lc: one from the catalogue and one for alice.py
OPS_dir = '/dark/hal/test_sheng/OPS/snlc/'
alice_dir = '/dark/hal/SNDATABASE/LC/'

# restore the lc data
samples_OPS_dir = '/dark/hal/test_sheng/code_sheng/machine-learning/snML/light_curve_ML/SN_samples/OPS_samples/'
samples_alice_dir = '/dark/hal/test_sheng/code_sheng/machine-learning/snML/light_curve_ML/SN_samples/alice_samples/'

# restrore the features extracted for each lc
lib_dir = '/dark/hal/test_sheng/code_sheng/machine-learning/snML/light_curve_ML/memory/'

show = False
clobber = True
verbose = False
band = 'B'

falllist1,falllist2 = glob.glob(alice_dir+'*.dat'),glob.glob(OPS_dir+'*.json')
fdonelist1,fdonelist2,fdonelist3 = glob.glob(samples_alice_dir+'*'),glob.glob(samples_OPS_dir+'*'),glob.glob(lib_dir+'*')
for fdonelist in [fdonelist1,fdonelist2,fdonelist3]:
    fff = ''
    for ff in fdonelist:
        fff+=ff
    if fdonelist == fdonelist1:fdonelist1=fff
    elif fdonelist == fdonelist2:fdonelist2=fff
    elif fdonelist == fdonelist3:fdonelist3=fff
raw_input(fdonelist)
if False:
    # lc from OPS catalogue
    for jsonfile in falllist2:    
        if os.path.basename(jsonfile).replace('.json','') in fdonelist2\
           and not clobber:continue 
        listrec = read_data_OPS.get_json_data(jsonfile)
        source_fetures = read_data_OPS.extract_source_fetures(listrec,band)    
        if source_fetures:
            name,lc_data,ra,dec,transient_type = source_fetures
        else:continue
        read_data_OPS.record_lc(name,lc_data,ra,dec,transient_type,\
                                samples_OPS_dir,clobber) 
        plot_data.show_lc(lc_data,show)

if True:
    featurelist,snlist = [],[]
    # lc from alice
    for datfile in falllist1:   
        if os.path.basename(datfile).replace('.dat','') in fdonelist1\
           and not clobber:continue         
        cls,fpro,sn = read_data_alice.process_lc(datfile,band,samples_alice_dir)
        
        if cls: 
            features = read_data_alice.process_lc_features(fpro)        
            flag=False            
            if features:
                for jj in range(len(features)):
                    if math.isnan(features.values()[jj]):flag=True
                if flag:continue
                featurelist.append(features)
                snlist.append(sn)    
    X,y = read_data_alice.get_raw_data(featurelist,snlist,clobber)

    # do ML
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
#        print "completeness", completeness
#        print "contamination", contamination
        cnf_matrix = confusion_matrix(y_test, y_pred)        
        plt.figure(figsize=cnf_matrix.shape)
        cllist = []
        for ii,jj in zip(y_test,y_pred):
            cllist.append(ii)
            cllist.append(jj)
        classes=np.unique(cllist)
        plot_data.plot_confusion_matrix(cnf_matrix, classes=classes, normalize=False)
