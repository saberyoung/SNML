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
import pyfits,dlt40,os,sys,re,string,subprocess,math

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter,MultipleLocator, FormatStrFormatter
import matplotlib.gridspec as gridspec
import pylab as pl

from astropy.io import fits
from astropy.io import fits as pyfits
from astropy import wcs as pywcs

from optparse import OptionParser

import datetime

sys.path.append('lib/')
import read_data
import plot_data
import support

tot = 6
#################################################    
if __name__ == "__main__":
    timenow = datetime.datetime.now()
    datenow = '-'.join([str(timenow.year),str(timenow.month),str(timenow.day)])

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-d",dest="date",default=datenow,\
                      type=str,help='date')
    parser.add_option("-c", "--clobber",action="store_true",\
                  dest='clobber',default=False,help='clobber files')
    option, args = parser.parse_args() 
    if len(args) < 1: 
        sys.argv.append('--help')
   
    classification = args[0]

    # train
    jd = 2457754
    area_factor = 50
    print '\n\n','#'*50,'\n learning from',jd,'images and scaled the images to',area_factor,'*',area_factor,'pixels\n\n'

    X,y=read_data.get_raw_data(str(jd),str(area_factor),option.clobber)    
    X =  X.reshape(X.shape[0], -1)  

    model = DecisionTreeClassifier(max_depth=2)

    clf = clone(model)
    clf = model.fit(X, y)   

    jdcheck = support.date_to_jd(timenow.year,timenow.month,timenow.day)
    print 'visual inspection for images after',datenow,'/',jdcheck

    pl.ion()
    fig = pl.figure(1,figsize=(6,12))
    pl.rcParams['figure.figsize'] = 6, 12
    pl.subplots_adjust(hspace = .01)
    pl.subplots_adjust(wspace = .01)
    pl.subplots_adjust(right=0.93, top=.93,left=.07, bottom=.07)
    gs0 = gridspec.GridSpec(tot, 3, wspace=.01) 

    command = ['select distinct(i.id),c.score from idcandidates as i join candidates as c '+\
               'where i.id = c.targetid and c.classificationid='+\
               str(classification)+' and c.jd > '+str(jdcheck)+' order by jd desc']

    print command
    lista = dlt40.dlt40sql.query(command,dlt40.dlt40sql.conn)   

    lll = 0
    for line0 in lista:
        lll=lll+1
        _id = line0['id']      
        command1 = ['select c.filepath, c.filename, c.xpos, c.ypos, c.fluxrad, c.jd, c.targetid, c.fluxauto, c.score, c.id from candidates as c join idcandidates as i where c.targetid = i.id   and  i.id = '+str(_id)+' ']
        data = dlt40.dlt40sql.query(command1,dlt40.dlt40sql.conn)
        idlist = []
        if len(data):          
            m = 0                    
            for line in data:
                pl.figure(1)
                score = line['score']
                imgdiff =  line['filepath']+line['filename']
                imgref = re.sub('diff.','ref.',line['filepath']+line['filename'])
                img    = re.sub('diff.','',line['filepath']+line['filename'])               
                idlist.append(line['id'])
                if os.path.isfile(img):
                    X0, hdr0 = pyfits.getdata(img, header=True)
                    xx = line['xpos']
                    yy = line['ypos']
                    xx0=max(xx-area_factor,0)
                    xx1=min(xx+area_factor,1024)
                    yy0=max(yy-area_factor,0)
                    yy1=min(yy+area_factor,1024)
                    # find zscale min max on the stamp 
                    _z1,_z2 = dlt40.zscale.zscale(X0[int(yy0):int(yy1),int(xx0):int(xx1)])
                    ax = fig.add_subplot(gs0[m,0])
                    ax.imshow(X0[int(yy0):int(yy1),int(xx0):int(xx1)], cmap='gray_r', aspect='equal', interpolation='nearest', origin='lower',vmin=_z1, vmax=_z2)
                    ax.set_xlim(0,xx1-xx0)
                    ax.set_ylim(0,yy1-yy0)
                    ax.plot(xx-xx0,yy-yy0,'o', markersize = 20, markeredgecolor = 'g', mfc='none',mew=2)
                    ax.set_xticks([])
                    ax.set_yticks([])
                if os.path.isfile(imgref):
                    X0, hdr0 = pyfits.getdata(imgref, header=True)
                    xx = line['xpos']
                    yy = line['ypos']
                    xx0=max(xx-area_factor,0)
                    xx1=min(xx+area_factor,1024)
                    yy0=max(yy-area_factor,0)
                    yy1=min(yy+area_factor,1024)
                    # find zscale min max on the stamp 
                    _z1,_z2 = dlt40.zscale.zscale(X0[int(yy0):int(yy1),int(xx0):int(xx1)])
                    ax = fig.add_subplot(gs0[m,1])
                    ax.imshow(X0[int(yy0):int(yy1),int(xx0):int(xx1)], cmap='gray_r', aspect='equal', interpolation='nearest', origin='lower',vmin=_z1, vmax=_z2)
                    ax.set_xlim(0,xx1-xx0)
                    ax.set_ylim(0,yy1-yy0)
                    ax.plot(xx-xx0,yy-yy0,'o', markersize = 20, markeredgecolor = 'g', mfc='none',mew=2)
                    ax.set_xticks([])
                    ax.set_yticks([])
######################
                    if 'SECPIX' in hdr0:
                        pixelscale = dlt40.util.readkey3(hdr0, 'SECPIX')
                    else:
                        pixelscale = 0.59
                   
                    _jd = dlt40.util.readkey3(hdr0, 'jd')
                    _wcs = dlt40.util.readkey3(hdr0, 'wcs')
                    if float(_wcs) == 0:
                        if 'PSF_FWHM' in hdr0:
                            seeing = float(dlt40.util.readkey3(hdr0, 'PSF_FWHM'))
                        else:
                            seeing = 3
                    else:
                        sys.exit('astrometry not good')
                    fwhm = seeing / pixelscale 
                   
                    print 'FWHM[header]  ', fwhm, '   in pixel'

#######################                   
                if os.path.isfile(imgdiff):
                    X0, hdr0 = pyfits.getdata(imgdiff, header=True)
                    xx = line['xpos']
                    yy = line['ypos']
                    xx0=max(xx-area_factor,0)
                    xx1=min(xx+area_factor,1024)
                    yy0=max(yy-area_factor,0)
                    yy1=min(yy+area_factor,1024)
                    # find zscale min max on the stamp 
                    _z1,_z2 = dlt40.zscale.zscale(X0[int(yy0):int(yy1),int(xx0):int(xx1)])
                    ax = fig.add_subplot(gs0[m,2])
                    ax.imshow(X0[int(yy0):int(yy1),int(xx0):int(xx1)], cmap='gray_r', aspect='equal', interpolation='nearest', origin='lower',vmin=_z1, vmax=_z2)
                    ax.set_xlim(0,xx1-xx0)
                    ax.set_ylim(0,yy1-yy0)
                    ax.plot(xx-xx0,yy-yy0,'o', markersize = 20, markeredgecolor = 'g', mfc='none',mew=2)
                    ax.set_xticks([])
                    ax.set_yticks([])

                    # machine learning algorithm     
                    X_test = read_data.read_single_fit(imgdiff,xx,yy,area_factor)                    
                    if len(X_test)>0:
                        X_test =  X_test.reshape(1, -1)                     
                        y_pred = clf.predict(X_test)
                        ax.text(20, 2, y_pred[0], fontsize=15, style='italic',color='red')                

                m = m+1
                if m == tot:
                    break                               
            pl.draw()
           
            print '#'*20
            print len(lista),lll
            print '\n######  CANDIDATE = ' + str(_id)
            print '\n###### SCORE = '+ str(score)
            answ = raw_input('\nskip                          [0]'+\
                             '\nexit                          [q]'+\
                             '\nnothing there/bad subtraction [1]'+\
                             '\nbad subtracion bright star    [2]'+\
                             '\ndipole                        [3]'+\
                             '\nreal transient                [4]'+\
                             '\ndefault                       ['+str(classification)+'] ? ')
 
            if answ == 'q':sys.exit()
            if not answ: answ = str(classification)
                
            if not answ in ['0', '1']:
                dictionary = {
                    'targetid':str(_id),
                    'classificationid':str(answ),
                    'imglist':str(idlist)}
                dlt40.dlt40sql.insert_values(dlt40.dlt40sql.conn,'ML_candidates',dictionary)
               
            pl.figure(1)
            pl.clf()  
