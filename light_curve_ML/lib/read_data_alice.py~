import os,sys
import glob
import dlt40
import json
import glob
from pprint import pprint
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from extract_features import Features
import pandas as pd
sys.path.append('lib/')
import sqlconn

def process_lc(datfile,band,lib):     
    sys.path.append('alice/')
    import am,verify
    snlist = os.path.basename(datfile).replace('.dat','').split(',')
    try:
        ff = open(lib+os.path.basename(datfile).replace('.dat',''),'w')
        ph,absmag,mag_err = am.am(snlist,band,'a','','',False,False)        
        sndata = verify.verify(snlist[0])            
        for ii in range(len(ph)):           
            ff.write(str(ph[ii])+','+str(absmag[ii])+','+str(mag_err[ii])+'\n')
        ff.close()
        # record sntype to database
        snlist = []
        command = ['select * from supernova_types']    
        if False:
            data = sqlconn.query(command,sqlconn.conn)
        else:
            data= dlt40.dlt40sql.query(command, dlt40.dlt40sql.conn)
        for ii in data:
            snlist.append(ii['SN'])    
        if not str(sndata['sn']) in snlist:        
            dictionary = {'SN':str(sndata['sn']),'type':str(sndata['sntype'])}
            if False:
                sqlconn.insert_values(sqlconn.conn,'supernova_types',dictionary)
            else:
                dlt40.dlt40sql.insert_values(dlt40.dlt40sql.conn,\
                                        'supernova_types',dictionary)
        return True,lib+os.path.basename(datfile).replace('.dat',''),\
            sndata['sn']
    except:return False,'',''

def process_lc_features(ff):
    series = pd.read_csv(ff,header=None, sep=',')        
    series.columns = ['MJD','Mag','Mag_err']        
    try:
        f = Features(series, mag_err=False)               
        f.call_all_features()
        return f.feature_list
    except:return False
    
def get_raw_data(featurelist,snlist,clobber):
    """Get the image data without any pre-processing"""
    directory = 'memory/'
    Xy_raw_file_name = directory + 'Xy_raw_alice.npz'
    if os.path.exists(Xy_raw_file_name) and not clobber:
        print("Restoring X and y from {}".format(Xy_raw_file_name))
        npz_file = np.load(Xy_raw_file_name)
        X = npz_file['X']        
        y = npz_file['y']         
        print("Done")
    else:            
        if os.path.exists(Xy_raw_file_name):os.remove(Xy_raw_file_name)
        print("Creating X and y for {}".format(Xy_raw_file_name)) 
        Xlist,ylist = [],[]
        for ii in range(len(featurelist)):
            X,y=[],[]
            features,sn = featurelist[ii],snlist[ii]
            for key in sorted(features.keys()):X.append(features[key])
            command = ['select type from supernova_types where SN="'+\
                       str(sn)+'"']
            if False:
                data = sqlconn.query(command,sqlconn.conn)
            else:
                data= dlt40.dlt40sql.query(command, dlt40.dlt40sql.conn)
            y = data[0].values()[0]
            Xlist.append(X)
            ylist.append(y)
        X,y = np.array(Xlist),np.array(ylist)
        np.savez(Xy_raw_file_name, X=Xlist, y=ylist)
        print("Done")
    return X, y
