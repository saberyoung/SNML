description=">> plot light curves for a SN"
usage = "%prog (./)snname [bands] [options] "
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
    parser.add_option("-o", "--offset",dest="offset",default=1,type='float',
                  help='magnitude offset between bands \t\t [%default]')
    parser.add_option("-j", "--juliandate",dest="juliandate",\
                  action="store_true",default=False,
                  help='Use Julian Date  \t [%default]')
    parser.add_option("-x", "--xplosion",dest="xplosion",\
                  action="store_true",default=False,
                  help='Use explosion epoch as reference \t [%default]')
    parser.add_option("-e", "--errorbar",dest="errorbar",\
                  action="store_true",default=False,
                  help='Plot errorbars \t\t [%default]')
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

def snlc(sn,band,xra,yra,off,xjd,xexpl,error,plcolor):

    if '/' not in sn: sn = alice.alice_data+sn 
    if not os.path.isfile(sn+'.dat'):
        print "!!! ERROR: file "+sn+".dat not found !!!"
        return

    sndata   = alice.leggifile(sn)

    _band = sndata['bands']
    if band: _band = band

    _off=float(off)

    pylab.rcParams['font.size']=20
    pylab.rcParams['legend.fontsize']= 14
    pylab.ion()

    if xra: x1,x2 = float(xra.split(',')[0]),float(xra.split(',')[1])
    if yra: y2,y1 = float(yra.split(',')[0])-.25,\
            float(yra.split(',')[1])+.25
    
    if not band: 
        answ = raw_input('<< bands to plot ['+_band+'] ? ')
        if answ: _band =answ
        for b in _band:
            if b not in sndata['bands']:
                print "!!! ERROR: band ",b," not available !!!"
                return    

    if len(_band)==1:            jdmaxref = sndata['jdmax'][_band]
    elif 'B' in sndata['bands']: jdmaxref = sndata['jdmax']['B']
    else:                        jdmaxref = sndata['jdmax'][_band[0]]
        
    if xjd:    jdmaxref = int(jdmaxref/100.)*100
    if xexpl:
        if sndata['jd_expl']: jdmaxref = sndata['jd_expl']
        else:
            print "!! ERROR: Explosion epoch for SN",sndata['sn'],\
                " not found !!!"
            return               
    ib=0
    pylab.axes([0.10,0.15,0.85,0.8])
    for b in _band:
        jd = array(sndata['jd'][b])
        if len(jd)==0: continue
        mag = array(sndata['mag'][b])
        mag_err = array(sndata['mag_err'][b])
        source = array(sndata['source'][b])
        ph = jd-jdmaxref
        if not xra:
            if ib == 0: x1,x2 = min(ph)-10,max(ph)+10
            else: 
                if min(ph)<x1: x1 = min(ph)-10
                if max(ph)>x2: x2 = max(ph)+10
        if not yra:
            ii = where((ph>x1)&(ph<x2))
            if ib == 0: y1,y2 = max(mag[ii])+0.25,min(mag[ii])-0.25
            else:
                if max(mag[ii])-off > y1: y1 = max(mag[ii])-off
                if min(mag[ii])-off < y2: y2 = min(mag[ii])-off    

        if b == _band[-1]: y2 += -(len(_band)-1)*_off
        UpperLimits(ph,mag-ib*_off,source,abs(y2-y1)/10.)

        if len(_band)==1:
            jj = 0
            for _so in unique(abs(source)):
                _is = abs(source) == _so
                p = pylab.plot(ph[_is],mag[_is],SY(plcolor)[jj],\
                                 label=str(_so),alpha=0.5)
                if error:
                    _is = ( abs(source) == _so ) & (source >= 0)
                    if len(_is)>0:
                        pylab.errorbar(ph[_is],mag[_is],yerr=mag_err[_is],\
                            fmt=SY(plcolor)[jj],label='_nolegend_')
                jj += 1
        else:
            p = pylab.plot(ph,mag-ib*_off,SY(plcolor)[_band.index(b)],\
                     label=b+' -'+str(round(ib*_off,1)))
            if error:
                _is = source >= 0
                if len(_is)>0:
                    pylab.errorbar(ph[_is],mag[_is]-ib*_off,yerr=mag_err,\
                         fmt=SY(plcolor)[_band.index(b)],label='_nolegend_')
        if  plcolor :
            pylab.setp(p,markerfacecolor='none')
            pylab.setp(p,markeredgewidth=1)
            pylab.setp(p,markersize=6)
        if ib*_off>0: _of= ' -'+str(round(ib*_off,1))
        ib += 1

    pylab.xlim(x1,x2)
    pylab.ylim(y1+.25,y2-.25)
    pylab.legend(numpoints=1)

    if xjd:     pylab.xlabel('JD +'+str(jdmaxref),size=20)
    elif xexpl: pylab.xlabel('phase [from explosion JD='\
                           +str(round(jdmaxref,1))+']',size=20)
    else:       pylab.xlabel('phase [from maximum JD='\
                           +str(round(jdmaxref,1))+']',size=20)

    raw_input('... quit ....')

if __name__ == "__main__":

    sn = args[0]
    if len(args)>1: bands=args[1]
    else: bands = ''

    snlc(sn,bands,option.rangephase,option.magrange,\
        option.offset,option.juliandate,option.xplosion,\
        option.errorbar,option.whiteblack)
