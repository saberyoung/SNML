import os.path,sys
import glob
import dlt40
import json
import glob
from pprint import pprint
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord

def HMS2deg(ra,dec):    
    c = SkyCoord(ra.split(':')[0]+' '+ra.split(':')[1]+' '+ra.split(':')[2]+' '+dec.split(':')[0]+' '+dec.split(':')[1]+' '+dec.split(':')[2], unit=(u.hourangle, u.deg))
    return c.ra.degree,c.dec.degree

def get_json_data(jsonfile):
    listrec,keylist = {},[]    
    readfile = open(jsonfile)
    data = json.load(readfile)
    for ii in data.keys():
        for jj in data[ii]:
            jj = str(jj)
            listrec[jj] = data[ii][jj]
            keylist.append(jj)
#    print jsonfile,keylist
    return listrec

def extract_source_fetures(listrec,band):
    ra,dec = listrec['ra'][0]['value'],listrec['dec'][0]['value']
    ra,dec = HMS2deg(ra,dec)
    name = listrec['name']
    transient_type = listrec['claimedtype'][0]['value']

    lcdata = {}
    for ii in listrec['photometry']:        
        try: ii['band']
        except: 
            print 'no keywords "band"!'           
            return False
        if ii['band']==band:
            try:
                lcdata[ii['time']]=ii['magnitude'],ii['e_magnitude']
            except:
                try:lcdata[ii['time']]=ii['magnitude'],'NULL'
                except:return False                
    if len(lcdata)==0:print 'no data select!'        
    return name,lcdata,ra,dec,transient_type

def record_lc(name,lc_data,ra,dec,transient_type,lib,clobber):       
    if os.path.exists(lib+name) and clobber:os.remove(lib+name)
    elif os.path.exists(lib+name) and not clobber:return
    ff = open(lib+name,'w')
#    try:
#        fdone = open('type.asc').readlines()
#        fff = open('type.asc','a')       
#    except:
#        fdnoe = []
#        fff = open('type.asc','w')
#    raw_input(fdone)
    for ii in range(len(lc_data)):       
        ff.write(str(name)+','+lc_data.keys()[ii]+','+\
                 lc_data.values()[ii][0]+','+\
                 lc_data.values()[ii][1]+','+str(ra)+','+str(dec)+'\n')
#    fff.write(name+':'+transient_type+'\n')
    ff.close() 
#    fff.close()

def read_lc_fetures(flist):
    print flist
    raw_input()

    
def get_raw_data(lc_type,clobber):
    """Get the image data without any pre-processing"""
    directory = 'memory/'
    Xy_raw_file_name = directory + 'Xy_raw_'+str(lc_type)+'.npz'
    if os.path.exists(Xy_raw_file_name) and not clobber:
        print("Restoring X and y from {}".format(Xy_raw_file_name))
        npz_file = np.load(Xy_raw_file_name)
        X = npz_file['X']        
        y = npz_file['y']
        flags =  npz_file['flags']
        print("Done")
    else:            
        if os.path.exists(Xy_raw_file_name):os.remove(Xy_raw_file_name)
        print("Creating X and y for {}".format(Xy_raw_file_name))
        imglist,flaglist,cxlist,cylist,flags = get_img_list(jd)
        X,y = read_fits(imglist,flaglist,cxlist,cylist,area_factor)
        np.savez(Xy_raw_file_name, X=X, y=y, flags=flags)
        print("Done")
    return X, y,flags
