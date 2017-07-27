description=">> plot light curve in absolute magnitude for SN(e)"
usage = "%prog (./)snname1[,snmane2,...] [bands] [options] "
###############
import os,shutil,sys
from numpy import *
from optparse import OptionParser
import pylab
import alice


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-r", "--rangephase",dest="rangephase",default='',
                  help='Phase range (eg. 0,100)')
    parser.add_option("-m", "--magrange",dest="magrange",default='',
                  help='Magnitude range (eg. 12,20)')
    parser.add_option("-e", "--extcorr",dest="extcorr",\
                  choices=['a','g','n'],default='a',
      help='Extinction correction (a-ll,g-alactic or n-one) \t [%default]')
    parser.add_option("-x", "--xplosion",dest="xplosion",\
                  action="store_true",default=False,
                  help='Use explosion epoch as reference \t [%default]')
    parser.add_option("-w", "--whiteblack",dest="whiteblack",\
                  action="store_true",default=False,
                  help='Plot in B/W \t\t [%default]')
    option,args = parser.parse_args()
    if len(args)<1 : sys.argv.append('--help')
    option,args = parser.parse_args()

def SY(plcolor):  ###################################    define plot symbol
    sym = 'osDdhHpx+<>^v1234' # simboli
    col = 'rbgcmyk'            # colori
    _sy = []
    if not plcolor: colrange = col
    else:     colrange = 'k'
    for s in sym:
        for c in colrange:      
            _sy.append(c+s)
    return _sy

def UpperLimits(ph,mag,source,size):  ################ plot upper limits
    _il = source < 0
    if any(_il):
        z = zeros(len(ph[_il]))
        pylab.errorbar(ph[_il],mag[_il],[z-size, z],lolims=True,fmt=None,\
             ecolor='k')   


def am(snlist,band,extc,xra,yra,xexpl,plcolor):

    for _s in snlist:
        if '/' not in _s: _s = alice.alice_data+_s
        if not os.path.isfile(_s+'.dat'):
            print "!!! ERROR: file "+_s+".dat not found !!!"
            return

    _band = 'B'
    if band: _band = band 
    if xra: x1,x2 = float(xra.split(',')[0]),float(xra.split(',')[1])
    if yra: y1,y2 = float(yra.split(',')[0]),float(yra.split(',')[1])
 
    pylab.rcParams['font.size']=20
    pylab.rcParams['legend.fontsize']= 14
#    pylab.ion()

    if not band:
        answ = raw_input('<< bands to plot ['+_band+'] ? ')
        if answ: _band=answ

    pylab.axes([0.15,0.15,0.8,0.8])
    i = 0
    jsn = range(len(snlist))[::-1]
    for j in jsn:
        _s = snlist[j]
        if '/' not in _s: _s = alice.alice_data+_s
        sndata = alice.leggifile(_s)

        if _band not in sndata['bands']:
            print "!!! ERROR: band ",_band," not available for sn",\
                sndata['sn']," !!!"
            sys.exit()
                
        if 'B'  in sndata['bands']: jdmaxref = sndata['jdmax']['B']
        else:
            _refb = sndata['bands'][0]
            print '>> WARNING: B maximum not available: use ',_refb
            jdmaxref = sndata['jdmax'][_refb]

        if xexpl:
            if sndata['jd_expl']: jdmaxref = sndata['jd_expl']
            else:
                print "!! ERROR: Explosion epoch for SN",sndata['sn'],\
                        " not found !!!"
                sys.exit()

          # extinction correction
        Rv = 3.1
        if 'Rv' in sndata.keys(): Rv = sndata['Rv'] 
        if sndata['ABi'] > 99:
            print '!!! WARNING: for SN',_sn,'ABi=',str(sndata['ABi']),\
                    ' (not available) ==> set to 0'
            sndata['ABi'] = 0.0
        abx = 0
        if extc =='g': abx = alice.AX(_band,sndata['ABg'])
        if extc =='a': abx = alice.AX(_band,sndata['ABg'])+\
                alice.AX(_band,sndata['ABi'],R_V=Rv)
        if extc =='n': abx = 0.

        jd,mag,mag_err,source = array(sndata['jd'][_band]),\
                                    array(sndata['mag'][_band]),\
                                    array(sndata['mag_err'][_band]),\
                                    array(sndata['source'][_band])  
        ph = jd-jdmaxref

        absmag = mag-sndata['mu']-abx

#        p = pylab.plot(ph,absmag,SY(plcolor)[j],label=sndata['sn'])
        if  plcolor :
                pylab.setp(p,markerfacecolor='none')
                pylab.setp(p,markeredgewidth=1)
                pylab.setp(p,markersize=6)
        if not xra:
            if i == 0:  x1,x2 = min(ph)-10,max(ph)+10
            else:
                if min(ph)-10<x1:      x1 = min(ph)-10
                if max(ph)+10>x2:      x2 = max(ph)+10

        if not yra:
            ii = where((ph>x1)&(ph<x2))
            if i == 0: y1,y2 = max(absmag[ii])+0.5,min(absmag[ii])-0.5
            else:
                if max(absmag[ii])+0.5>y1: y1 = max(absmag[ii])+0.5
                if min(absmag[ii])-0.5<y2: y2 = min(absmag[ii])-0.5

        UpperLimits(ph,absmag,source,abs(y2-y1)/10.)
        print '>>> ',sndata['sn']+' - A_'+_band+'='+str(round(abx,2))+' <<<'
        i += 1
    
    if xexpl: pylab.xlabel('phase [from explosion]',size=20)
    else:     pylab.xlabel('phase [from maximum]',size=20)

    pylab.xlim(x1,x2)
    pylab.ylim(y1,y2)
    pylab.ylabel(_band+' absolute magnitude',size=20)
    pylab.legend(numpoints=1)

#    raw_input('... quit ....')
    return ph,absmag,mag_err

if __name__ == "__main__":

    snlist = args[0].split(',')
    if len(args)>1: bands=args[1]
    else: bands = ''

    am(snlist,bands,option.extcorr,option.rangephase,\
         option.magrange,option.xplosion,option.whiteblack)

