import os.path,sys
import glob
import dlt40
from astropy.io import fits
import numpy as np

def get_img_list(jd):    
    imglist,flaglist,cxlist,cylist,flaglist1 = [],[],[],[],[]
    command = ['select c.filename,c.filepath,c.ra0,c.dec0,c.xpos,c.ypos,c.classificationid,l.classification from candidates as c join classification as l where c.classificationid=l.id and c.jd>='+jd]
    data= dlt40.dlt40sql.query(command, dlt40.dlt40sql.conn)
    total = len(data)
    for nn,ii in enumerate(data):
        # skip eyeball object
        if ii['classificationid'] in [1,7,8,10,12,13]:continue
        img = ii['filepath']+ii['filename']
        imglist.append(img)
        flaglist.append(ii['classificationid'])
        flaglist1.append(ii['classification'])
        cxlist.append(ii['xpos'])
        cylist.append(ii['ypos'])  
        print float(nn)/total*100,'% imglist read'
    return imglist,flaglist,cxlist,cylist,np.unique(flaglist1)

def classify_flags(flaglist):
    flaglist1 = []
    for ff in flaglist:
        if ff in [2,3]:flaglist1.append('2')
        elif ff in [4]:flaglist1.append('3')
        elif ff in [5,6,9,11,14]:flaglist1.append('4')
        elif ff in [15]:flaglist1.append('5')
        else:raw_input(ff)   
    return flaglist1

def read_fits(imglist,flaglist,cxlist,cylist,area_factor):
    X, y, area_factor = [], [], int(area_factor)
    if len(imglist) == 0:
        raise Exception("No fits files found")
    else:raw_input(str(len(imglist))+' found.')

    for num,file_name in enumerate(imglist):
        with fits.open(file_name) as hdulist:
            for hdu in hdulist:                
                cx,cy = int(cxlist[num]),int(cylist[num])
                cxmax = cx+area_factor
                cxmin = cx-area_factor
                cymax = cy+area_factor
                cymin = cy-area_factor
                limx,limy = hdu.data.shape
                if cxmin>=0 and cxmax<=limx and cymin>=0 and cymax<=limy:pass
                else:continue
                X.append(np.array([hdu.data[cymin:cymax,cxmin:cxmax]]))
                y.append(flaglist[num])             
        print float(num)/len(imglist)*100,'% imglist append' 
    return np.array(X), np.array(y, dtype=np.int8)

def get_raw_data(jd,area_factor,clobber):
    """Get the image data without any pre-processing"""
    directory = 'memory/'
    Xy_raw_file_name = directory + 'Xy_raw_'+str(jd)+'_'+str(area_factor)+'.npz'
    if os.path.exists(Xy_raw_file_name) and not clobber:
        print("Restoring X and y from {}".format(Xy_raw_file_name))
        npz_file = np.load(Xy_raw_file_name)
        X = npz_file['X']        
        y = npz_file['y']       
        print("Done")
    else:            
        if os.path.exists(Xy_raw_file_name):os.remove(Xy_raw_file_name)
        print("Creating X and y for jd>"+jd+" in {}".format(Xy_raw_file_name))
        imglist,flaglist,cxlist,cylist,flags = get_img_list(jd)
        flaglist = classify_flags(flaglist)
        X,y = read_fits(imglist,flaglist,cxlist,cylist,area_factor)
        np.savez(Xy_raw_file_name, X=X, y=y)
        print("Done")
    return X, y

def read_single_fit(file_name,cx,cy,area_factor):
    area_factor = int(area_factor)
    with fits.open(file_name) as hdulist:        
        for hdu in hdulist:                    
            cx,cy = int(cx),int(cy)
            cxmax = cx+area_factor
            cxmin = cx-area_factor
            cymax = cy+area_factor
            cymin = cy-area_factor
            limx,limy = hdu.data.shape
            if cxmin>=0 and cxmax<=limx and cymin>=0 and cymax<=limy:
                X = np.array([hdu.data[cymin:cymax,cxmin:cxmax]])
            else:X=''          
    return X

