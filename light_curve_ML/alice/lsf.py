description=">> Measure decline rates or light curve maximum"
usage = "%prog (./)snname [band] [options] "
###############
import os,shutil,sys
from numpy import *
from optparse import OptionParser
import pylab
import alice

if 'keymap.yscale' in pylab.rcParams.keys(): 
    pylab.rcParams['keymap.yscale']=''
if 'keymap.fullscreen' in pylab.rcParams.keys(): 
    pylab.rcParams['keymap.fullscreen']=''

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--decline",dest="decline",action='store_true',
            default=False,help='Measure decline rate \t\t [%default]')
    parser.add_option("-p", "--peak",dest="peak",action='store_true',
            default=False,help='Measure peak magnitude \t\t [%default]')
    parser.add_option("-s", "--show",dest="show",action='store_true',
            default=False,help='Show PSF output \t\t [%default]')
    parser.add_option("-r", "--rangephase",dest="rangephase",default='',
                  help='Phase range (eg. 0,100)')
    parser.add_option("-m", "--magrange",dest="magrange",default='',
                  help='Magnitude range (eg. 12,20)')
    parser.add_option("-o", "--order",dest="order",default=5,type='int',
                  help='Polinomial fit order \t\t [%default]')
    option,args = parser.parse_args()
    if len(args)<1 : sys.argv.append('--help')
    option,args = parser.parse_args()
    if option.decline and option.peak:
        print "!!! ERROR: choose only one between  -d(ecline) and -p(eak) !!!"
        sys.exit()
    if not option.decline and not option.peak:
        print "!!! ERROR: choose one between  -d(ecline) and -p(eak) !!!"
        sys.exit()
    
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
             ecolor='k',label='_nolegend_')   

def onclick(event):
    global ph,mag,source,_band,xrfit,x1,x2,y1,y2,isel,_task,_order
    dx,dy = x2-x1,y1-y2
    yrfit =[]
    if event.key=='d':
        _dist =sqrt(((ph-event.xdata)/dx)**2+((mag-event.ydata)/dy)**2)
	ix = argmin(_dist)
        if ix not in isel: isel.append(ix)
    
    if event.key=='u':
        _dist =sqrt(((ph-event.xdata)/dx)**2+((mag-event.ydata)/dy)**2)
	ix = argmin(_dist)
        if ix in isel: isel.remove(ix)

    elif event.key=='l': xrfit[0] = event.xdata

    elif event.key=='r': xrfit[1] = event.xdata

    elif event.key=='f':
        _ph = [p for i,p in enumerate(ph) if i not in isel]
        _mag = [m for i,m in enumerate(mag) if i not in isel]
        xx = compress((_ph>=xrfit[0])&(_ph<=xrfit[1]),_ph)
        yy = compress((_ph>=xrfit[0])&(_ph<=xrfit[1]),_mag)
        if _task == 'd': _ord =1
        elif _task=='p': _ord = _order    
        pfit = polyfit(xx,yy,_ord,full=True)
        _xrfit = arange(xrfit[0],xrfit[-1]+.1,.1)
        yrfit = polyval(pfit[0],_xrfit)
        
    pylab.clf()
    pylab.axes([0.15,0.15,0.8,0.75])
    jj = 0
    _source = abs(source)
    for _so in unique(_source):
        _is = where(_source == _so)
        p= pylab.plot(ph[_is],mag[_is],SY(False)[jj],label=str(_so))
        jj +=1

        UpperLimits(ph,mag,source,abs(y2-y1)/10.)

    pylab.plot([ph[isel]],[mag[isel]],'kx',lw=2,markersize=15)

    pylab.axvline(xrfit[0])
    pylab.axvline(xrfit[1])
    pylab.title( "d-elete, u-ndelete, l,r to select range, "+\
                 "f-it",fontsize=14)
    pylab.xlabel('phase [days]',size=20)
    pylab.ylabel(_band,size=20)

    if len(yrfit)>0:
        pylab.plot(_xrfit,yrfit,'k:',lw=1)
        sigmay = sqrt(pfit[1]/float(len(xx)  -2))
        if _task =='d':
            sigmab = sigmay*sqrt(1/sum((xx-mean(xx))**2))

            pylab.figtext(.4,.85,\
              "slope=%5.2f +/- %5.2f mag/100d" % (pfit[0][0]*100,sigmab*100),\
                           fontsize=14)
            pylab.figtext(5,.8,\
              "(range=%d-%dd)" % (xrfit[0],xrfit[1]),fontsize=14)
        elif _task =='p':
            ii = argmin(yrfit)
            pylab.figtext(.4,.85,"max=%5.2f+/-%5.2f mag (%.1fd)" \
               % (yrfit[ii],sigmay/sqrt(len(yrfit)-_ord),_xrfit[ii]),fontsize=14)

    pylab.xlim(x1,x2)
    pylab.ylim(y1,y2)
    pylab.legend(numpoints=1,markerscale=1.5)

def lsf(sn,band,task,xra,yra,order):
    global ph,mag,source,_band,xrfit,x1,x2,y1,y2,isel,_task,_order
    _task = task
    _order = order
    if '/' not in sn: sn = alice.alice_data+sn 
    if not os.path.isfile(sn+'.dat'):
        print "!!! ERROR: file "+sn+".dat not found !!!"
        return
    
    sndata   = alice.leggifile(sn)
    _band = sndata['bands'][0]
    if band: _band = band

    if xra: x1,x2 = float(xra.split(',')[0]),float(xra.split(',')[1])
    if yra: y2,y1 = float(yra.split(',')[0]),float(yra.split(',')[1])

    pylab.rcParams['font.size']=20
    pylab.rcParams['legend.fontsize']= 14
    pylab.ion()

    pylab.axes([0.15,0.15,0.8,0.75])
    if not band:
        answ = raw_input('<< band to plot ('+sndata['bands']+\
                             ') ['+_band+'] ? ')
        if answ: _band =answ
        for b in _band:
            if b not in sndata['bands']:
                print "!!! ERROR: band ",b," not available !!!"
                return    

    if len(_band)==1: jdmaxref= sndata['jdmax'][_band]
    elif 'B' in sndata['bands']: jdmaxref = sndata['jdmax']['B']
    elif 'g' in sndata['bands']: jdmaxref = sndata['jdmax']['g']

    jd,mag,mag_err,source = array(sndata['jd'][_band]),\
        array(sndata['mag'][_band]),\
        array(sndata['mag_err'][_band]),array(sndata['source'][_band])
    ph = jd-jdmaxref
    jj = 0
    _source = abs(source)
    for _so in unique(_source):
        _is = where(_source == _so)
        p= pylab.plot(ph[_is],mag[_is],SY(False)[jj],label=str(_so))
        jj +=1
        
        if not xra: x1,x2 = min(ph)-10,max(ph)+10
        if not yra:
                ii = where((ph>x1)&(ph<x2))
                y1,y2 = max(mag[ii])+0.5,min(mag[ii].tolist())-0.5

        UpperLimits(ph,mag,source,abs(y2-y1)/10.)

    _band = band
    pylab.xlabel('phase [days]',size=20)
    pylab.ylabel(_band,size=20)
    
    pylab.xlim(x1,x2)
    pylab.ylim(y1,y2)
    pylab.legend(numpoints=1,markerscale=1.5)

    if not xra:   
        answ  = raw_input('phase range  ['+str(int(x1))+' '+\
                                  str(int(x2))+'] ?')
        if answ: x1,x2 = float(answ.split()[0]),\
                             float(answ.split()[1])
    if not yra:
        answ  = raw_input('mag range ['+str(round(y2,1))+\
                              ' '+str(round(y1,1))+'] ?')
        if answ: y2,y1 = float(answ.split()[0]),\
                             float(answ.split()[1])

    pylab.xlim(x1,x2)
    pylab.ylim(y1,y2)

    isel,xrfit = [],[x1,x2]
    pylab.title( "d-elete, u-ndelete, l,r to select range, "+\
                 "f-it",fontsize=14)
    cid = pylab.connect('key_press_event',onclick)
        
    raw_input('..... FIT ....')

if __name__ == "__main__":

    sn = args[0]
    if len(args)>1: band=args[1]
    else: band = 'B'

    if option.decline: task = 'd'
    elif option.peak: task = 'p'

    lsf(sn,band,task,option.rangephase,option.magrange,option.order)


