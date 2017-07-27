#!/usr/bin/env python
description = ">> eyeball candidates from terminal"
usage = "%prog candidates type  [options  1 eye, 2 artifact, 3 stars] "

import dlt40
import numpy as np
import pylab as pl
import os
import sys
import re
import string
from astropy.io import fits as pyfits
from astropy import wcs as pywcs
import math
from matplotlib.ticker import NullFormatter,MultipleLocator, FormatStrFormatter
import matplotlib.gridspec as gridspec
from optparse import OptionParser
import subprocess

def runsex(img, fwhm, thresh, pix_scale, mina=5.):  ## run_sextractor  fwhm in pixel
    import dlt40

    seeing = fwhm * pix_scale

    cdef = open(dlt40.__path__[0] + '/standard/sex/default2.param')
    riga = cdef.readlines()
    cparam = []
    for r in riga:
        if r[0] != '#' and len(r.strip()) > 0: \
                cparam.append(r.split()[0])

    pid = subprocess.Popen("sex " + img + " -catalog_name tmp.cat" + \
                           " -c  " + dlt40.__path__[0] + '/standard/sex/default2.sex' \
                                                       " -PARAMETERS_NAME " + dlt40.__path__[
                               0] + "/standard/sex/default2.param" + \
                           " -STARNNW_NAME " + dlt40.__path__[0] + "/standard/sex/default2.nnw" + \
                           " -PSF_NAME     " + dlt40.__path__[0] + "/standard/sex/default2.psf" + \
                           " -PIXEL_SCALE " + str(pix_scale) + \
                           " -DETECT_MINAREA " + str(mina) + \
                           " -DETECT_THRESH  " + str(thresh) + \
                           " -ANALYSIS_THRESH  " + str(thresh) + \
                           " -PHOT_FLUXFRAC 0.5" + \
                           " -SEEING_FWHM " + str(seeing),
                           stdout=subprocess.PIPE, shell=True)

    output, error = pid.communicate()

    csex = open("tmp.cat")
    tab = {}
    riga = csex.readlines()
    for k in cparam: tab[k] = []
    for r in riga:
        if r[0] != '#':
            for i in range(len(cparam)):
                tab[cparam[i]].append(float(r.split()[i]))
    for k in cparam: tab[k] = np.array(tab[k])

    return tab


####################################################################################################
if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description)
    option, args = parser.parse_args()
    if len(args) < 1: 
        sys.argv.append('--help')
    option, args = parser.parse_args() 

    classification = args[0]
    JD = 2457390.6

    command = ['select distinct(i.id),c.score from idcandidates as i join candidates as c '+\
               'where i.id = c.targetid and c.classificationid='+\
               str(classification)+' and c.jd > '+str(JD-500)+' and c.jd < '+str(JD+500.)+' order by jd desc']
    print command
    lista = dlt40.dlt40sql.query(command,dlt40.dlt40sql.conn)    

    lll = 0
    for line0 in lista:
        lll=lll+1
        _id = line0['id']
       
        command1 = ['select c.filepath, c.filename, c.xpos, c.ypos, c.fluxrad, c.jd, c.targetid, c.fluxauto, c.score, c.magabs from candidates as c join idcandidates as i where c.targetid = i.id   and  i.id = '+str(_id)+' ']
        data = dlt40.dlt40sql.query(command1,dlt40.dlt40sql.conn)       
        if len(data):                  
            fflux,ffrad,maglist=[],[],[]
            jd = []
            for line in data:
                pl.figure(1)
                score = line['score']
                imgdiff =  line['filepath']+line['filename']
                imgref = re.sub('diff.','ref.',line['filepath']+line['filename'])
                img    = re.sub('diff.','',line['filepath']+line['filename'])
      
                fflux.append(line['fluxauto'])
                ffrad.append(line['fluxrad'])
                jd.append(line['jd'])
                maglist.append(line['magabs'])

            pl.plot(jd,maglist,'*')                   
            print '#'*20
            print len(lista),lll
            print '\n######  CANDIDATE = ' + str(_id)
            print '\n###### SCORE = '+ str(score)
            answ = raw_input('\nskip                          [0]'+\
                            '\nnothing there/bad subtraction [2]'+\
                            '\nbad subtracion bright star    [3]'+\
                            '\ndipole                        [4]'+\
                            '\nreal transient                [5]'+\
                            '\nedge of the chip              [7]'+\
                            '\nartifact                      [8]'+\
                            '\ndefault                       ['+str(classification)+'] ? ')
            if not answ:
                answ = int(classification)
      
            if answ != '0':
                dlt40.dlt40sql.updatevalue('candidates','classificationid',answ,_id,'dlt40','targetid')

            pl.show()
            pl.clf()
           
