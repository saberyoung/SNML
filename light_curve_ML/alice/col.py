description=">> plot color curve for SN(e)"
usage = "%prog (./)snname1[,snmane2,...] [color] [options] "
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
    parser.add_option("-i", "--interphase",dest="interphase",default=.1,
              type='float',help='interpolation range (days) \t\t [%default]')
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


def col(sn,color,extc,phinterp,xra,yra,xexpl,plcolor):
    
    for _s in snlist:
        if '/' not in _s: _s = alice.alice_data+_s
        if not os.path.isfile(_s+'.dat'):
            print "!!! ERROR: file "+_s+".dat not found !!!"
            sys.exit()

    b1,b2 = '',''
    if color: b1,b2 = color[0],color[1] 

    if xra: x1,x2 = float(xra.split(',')[0]),float(xra.split(',')[1])
    if yra: y1,y2 = float(yra.split(',')[0]),float(yra.split(',')[1])

    pylab.rcParams['font.size']=20
    pylab.rcParams['legend.fontsize']= 14
    pylab.ion()

    if not color:
        answ = raw_input('<< color ['+b1+b2+'] ?')
        if answ: b1,b2 = answ[0],answ[1]
        
    pylab.axes([0.15,0.15,0.8,0.8])
    i = 0
    jsn = range(len(snlist))[::-1]
    for j in jsn:
        _s = snlist[j]
        if '/' not in _s: _s = alice.alice_data+_s 
        print _s
        sndata = alice.leggifile(_s)

        if b1 not in sndata['bands'] or b2 not in sndata['bands']:
            print "!!! ERROR: band ",b1," or ",b2,"not available for sn",\
                     sndata['sn'],' !!!'
            sys.exit()

        if 'B'  in sndata['bands']: jdmaxref = sndata['jdmax']['B']
        else:
            print '>> WARNING: B maximum not available for',sndata['sn'],\
                      ': use ',b1
            jdmaxref = sndata['jdmax'][b1]

        if xexpl:
            if sndata['jd_expl']: jdmaxref = sndata['jd_expl']
            else:
                print "!! ERROR: Explosion epoch for SN",sndata['sn'],\
                    " not found !!!"
                sys.exit()

        if b1 not in sndata['bands'] or b2 not in sndata['bands']: 
		print  '################################################################'+'\n!!! ERROR: band '+b1+ ' or '+b2+' not available for SN'+_sn+ '   ['+sndata['bands']+']\n'+'################################################################'
                sys.exit()     
   # extinction correction
        Rv = 3.1
        if 'Rv' in sndata.keys(): Rv = sndata['Rv'] 
        if sndata['ABi'] > 99:
            print '!!! WARNING: for SN',_sn,'ABi=',str(sndata['ABi']),\
                    ' (not available) ==> set to 0'
            sndata['ABi'] = 0.0
            abx1, abx2 = 0,0
        if extc =='g':
            abx1 = alice.AX(b1,sndata['ABg'])
            abx2 = alice.AX(b2,sndata['ABg'])
        elif extc =='n':
            abx1 = 0.
            abx2 = 0.
        elif extc =='a':
            abx1 = alice.AX(b1,sndata['ABg'])+\
                alice.AX(b1,sndata['ABi'],R_V=Rv)
            abx2 = alice.AX(b2,sndata['ABg'])+\
                    alice.AX(b2,sndata['ABi'],R_V=Rv) 
 
        ph1 = compress((array(sndata['source'][b1])>=0),\
                               array(sndata['jd'][b1])-jdmaxref)
        mmag1 =  compress((array(sndata['source'][b1])>=0),\
                                  sndata['mag'][b1])    
        ph2 = compress((array(sndata['source'][b2])>=0),\
                               array(sndata['jd'][b2])-jdmaxref)
        mmag2 =  compress((array(sndata['source'][b2])>=0),\
                                  sndata['mag'][b2])
    
        o2,oph2 = -1,phinterp
        ph,col = [],[]

        for i1 in argsort(ph1):
            _phclose= abs(ph2 - ph1[i1])
            i2 = argmin(_phclose)
            if _phclose[i2] <= phinterp:
                if i2 == o2 and _phclose[i2]<oph2:
                    ph[-1] = ph1[i1]
                    col[-1] = mmag1[i1]-abx1-mmag2[i2]+abx2
                else:
                    ph.append(ph1[i1])
                    col.append(mmag1[i1]-abx1-mmag2[i2]+abx2)
                    o2,oph2 = i2,_phclose[i2]
        if len(ph) == 0:
                print  '################################################################'+'\n!!! ERROR: possibly, observations of the two bands are not at \n!!! coincident epochs for SN'+sndata['sn']+'. Try interpolating.\n'+ '################################################################'
                sys.exit()
                
        p = pylab.plot(ph,col,SY(plcolor)[j],label=sndata['sn'])
        if plcolor:
            pylab.setp(p,markerfacecolor='none')
            pylab.setp(p,markeredgewidth=1)
            pylab.setp(p,markersize=6)
        if not  xra:
            if i == 0: x1,x2 = min(ph)-10,max(ph)+10
            else:
                if min(ph)-10<x1: x1 = min(ph)-10
                if max(ph)+10>x2: x2 = max(ph)+10

        if not  yra:
            if i == 0: y1,y2 = min(col)-0.5,max(col)+0.5
            else:
                if min(col)-0.5<y1: y1 = min(col)-0.5
                if max(col)+0.5>y2: y2 = max(col)+0.5
        i += 1        
        print '>>> ',sndata['sn']+' - A_'+b1+'='+str(round(abx1,2))+'  <<<'

    if xexpl: pylab.xlabel('phase [from explosion]',size=20)
    else:     pylab.xlabel('phase [from '+b1+' maximum]',size=20)

    pylab.ylabel(b1+'-'+b2,size=20)
    pylab.xlim(x1,x2)
    pylab.ylim(y1,y2)
    pylab.legend(numpoints=1)

    raw_input('... quit ....')

if __name__ == "__main__":

    snlist = args[0].split(',')
    if len(args)>1: color=args[1]
    else: color = ''

    col(snlist,color,option.extcorr,option.interphase,option.rangephase,\
      option.magrange,option.xplosion,option.whiteblack)

