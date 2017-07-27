description="Compute bolometric luminosity"
usage = "%prog SNname [options]"
#####################################################################
# Compute bolometric luminosity
# version 1.1
# author  EC 
#__________________________________________________________________
# 2008/Oct/7  Start from
# 2012/Ago/31 Updated to numpy and pylab. Accept ABmag in input and upper limits
#             Added options manager
###################################################################

import os,sys
from optparse import OptionParser
from numpy import *
from pylab import *
import alice

if __name__ == "__main__":
   parser = OptionParser(usage=usage,description=description)
   parser.add_option("-m", "--magsys",choices=['vega','ab'],\
            dest='magsys',default='vega',help='Magnitude system\t\t [%default]')
   parser.add_option("-l", "--limit",action="store_true",\
            dest='limit',default=False,\
            help='Include upper limits ? [%default]')
   parser.add_option("-e", "--error",dest='error',type='float',default=0.1,\
          help='Adopted error if error estimate is not available\t [%default]')

   option,args = parser.parse_args()
   if len(args)<1 : sys.argv.append('--help')
   option,args = parser.parse_args()

outfile = 'bol.dat'
sedfile = 'sed.dat'

def smartint(x,y,xref,yref):

   ir = (xref>=min(x))&(xref<=max(x))
   yint = interp((xref[ir]),x[argsort(x)],y[argsort(x)])
   yord = zeros(len(xref),dtype=float)
   ylow = yint[argmin(xref[ir])]-yref[ir][argmin(xref[ir])]+\
          yref[xref<min(x)]
   yup  = yint[argmax(xref[ir])]-yref[ir][argmax(xref[ir])]+\
           yref[xref>max(x)]
   yord[ir] = yint
   yord[xref<min(x)] = ylow
   yord[xref>max(x)] = yup

   return yord

def press(event):
    xr,yr =  event.xdata,event.ydata
    if event.inaxes:
        if event.key=='a':
            xadd.append(xr)
            yadd.append(yr)
        if event.key=='d':
            if len(xadd)>0:   
                ix,iy = argmin(abs(array(xadd)-xr)),argmin(abs(array(yadd)-yr))
                if abs(xadd[ix]-xr) < 3. and abs(yadd[iy]-yr) < 3.: 
                    xadd.pop(ix)
                    yadd.pop(iy)
    clf()
    title('a-dd/d-elete interpolation point for band '+b)
    errorbar(ph[_bandref],mag[_bandref],yerr=mag_err[_bandref],fmt='o',\
             ecolor='b',mfc='b',mec='b',label=_bandref)
    errorbar(ph[b],mag[b],yerr=mag_err[b],fmt='o',ecolor='r',\
                     mfc='r',mec='r',label=b)
    plot(xadd,yadd,'sg',label='_nolegend_')
    magint[b] = smartint(concatenate((ph[b],array(xadd))),\
             concatenate((mag[b],array(yadd))),ph[_bandref],mag[_bandref])
    magint_err[b] = smartint(concatenate((ph[b],array(xadd))),\
             concatenate((mag_err[b],zeros(len(yadd))+_err)),\
                                 ph[_bandref],mag_err[_bandref])

    plot(ph[_bandref],magint[b],'r+',label='_nolegend_')
    ylim(y2+.5,y1-.5)
    legend(numpoints=1)
    draw()


################################################################

if __name__ == "__main__":
   ion()
   sn = args[0]
#sn = raw_input('<< SN ? ')
   if '/' not in sn: sn = alice.alice_dir+sn 
   if not  os.path.isfile(sn+'.dat'):
      print "!!! ERROR: file "+sn+".dat not found !!!"
      print '   Default directory '+alice.alice_dir+\
          ' \n  [prefix ./ for current directory or give path]'
      sys.exit()

   sndata   = alice.leggifile(sn)

   bands = sndata['bands']

   answ =raw_input('<< Bands to integrate? ['+bands+']')
   if answ: bands = answ

   if 'V' in bands: _bandref = 'V'
   else: _bandref = bands[0]
   answ=raw_input('<< reference band ? ['+_bandref+']')
   if answ: _bandref = answ

   _err = option.error

   Rv = 3.1
   if 'Rv' in sndata.keys(): Rv = sndata['Rv']

# bands sort
   lam = []
   for b in bands: 
      lam.append(alice.bandpar[b][alice.band_label.index('avgwv')])
   _band = ''
   for i in argsort(lam):
      _band += bands[i]

   ph,mag,mag_err = {},{},{}
   for b in _band:
      if option.magsys == 'ab': 
         abvega = alice.bandpar[b][alice.band_label.index('abmag for vega')]
      else: abvega=0.

      if b in 'ugriz':
         print '!!! WARNING:  filter',b,'takes as ABMAG in input' 
         if option.magsys == 'ab': abvega = 0
         else: 
            abvega= alice.bandpar[b][alice.band_label.index('abmag for vega')]


      if option.limit: _nol = array(sndata['source'][b])>=-999
      else: _nol = array(sndata['source'][b])>=0
      mag[b] = array(sndata['mag'][b])[_nol]-abvega
      _mag_err = array(sndata['mag_err'][b])[_nol]
      source = array(sndata['source'][b])[_nol]
      ph[b] = array(sndata['jd'][b])[_nol]-sndata['jdmax'][_bandref]

      mag_err[b] = where(_mag_err>0,_mag_err,_err)

   checkint = False
   answ=raw_input('<< Check interpolation (y/n)? [n] ')
   if answ: 
      if answ =='y': checkint = True

   magint,magint_err = {},{}
   for b in _band:
      xadd,yadd = [],[]
      if b != _bandref and len(mag[b]):
         #print b
         y1,y2 = min(mag[_bandref]),max(mag[_bandref])   
         if y1>min(mag[b]): y1=min(mag[b])
         if y2<max(mag[b]): y2=max(mag[b])
         magint[b] = smartint(ph[b],mag[b],ph[_bandref],mag[_bandref])
         magint_err[b] = smartint(ph[b],mag_err[b],ph[_bandref],zeros(len(mag[_bandref]),dtype=float))
       
         if checkint:
            errorbar(ph[_bandref],mag[_bandref],yerr=mag_err[_bandref],\
                     mfc='b',mec='b',fmt='o',ecolor='b',label=_bandref)
            errorbar(ph[b],mag[b],yerr=mag_err[b],fmt='o',ecolor='r',\
                     mfc='r',mec='r',label=b)
            plot(ph[_bandref],magint[b],'r+',label='_nolegend_')        
            ylim(y2+.5,y1-.5)
            title('a-dd/d-elete interpolation point for band '+b)
            legend(numpoints=1)
            connect('key_press_event',press)
            draw()
            raw_input('.... next band ...')
            clf()
      else:
         phint = ph[b]
         magint[b] = mag[b]
         magint_err[b] = mag_err[b]

   checksed = False
   answ=raw_input('<< Check SED  (a-ll or o-ne by one)? [n] ')
   if answ: 
      if answ in 'ao': checksed = answ

   lam = []
   for b in _band:
      lam.append(alice.bandpar[b][alice.band_label.index('avgwv')])

   logL,logL_err = [],[]
   sedf = open(sedfile,'w')

   iiph = argsort(phint)
   for i in iiph:
      fl,fl_err1,fl_err2 = [],[],[]
      flsum,flsum_err1,flsum_err2 = 0,0,0
      for j in range(len(_band)):
         blam = lam[_band.index(_band[j])]
         abb = alice.AX(_band[j],sndata['ABg'],3.1)+alice.AX(_band[j],\
                                             sndata['ABi'],Rv)
         _fl = alice.bandpar[_band[j]][alice.band_label.index('zpoint')]*\
               10**(-0.4*(magint[_band[j]][i]-abb))
        
         _fl_err1 = (0.4*log(10)*_fl*magint_err[_band[j]][i])**2
         _fl_err2 = 0.4*log(10)*_fl*sqrt((alice.AX(_band[j],sndata['ABg_err'],\
             3.1))**2+(alice.AX(_band[j],sndata['ABi_err'],Rv))**2)

         fl.append(_fl)
         fl_err1.append(_fl_err1)
         fl_err2.append(_fl_err2)
         
         if j==0:
            _flbw = _fl*alice.bandpar[_band[j]]\
                          [alice.band_label.index('equvw')]/2.
            _flbw_err1 = _fl_err1*(alice.bandpar[_band[j]]\
                            [alice.band_label.index('equvw')]/2.)**2
            _flbw_err2 = _fl_err2*alice.bandpar[_band[j]]\
                          [alice.band_label.index('equvw')]/2.
         elif j>0:
            _flbw = (_fl+fl[j-1])*(blam-lam[_band.index(_band[j-1])])/2. 
            _flbw_err1 = (_fl_err1+fl_err1[j-1])*\
                          ((blam-lam[_band.index(_band[j-1])])/2.)**2 
            _flbw_err2 = (_fl_err2+fl_err2[j-1])*\
                          (blam-lam[_band.index(_band[j-1])])/2. 

         flsum += _flbw
        # errors on photometry summed as random
         flsum_err1 += _flbw_err1
        # errors on extinction summed as systematic
         flsum_err2 += _flbw_err2        

    # LAST BAND
      _flbw = _fl*alice.bandpar[_band[-1]][alice.band_label.index('equvw')]/2.
      _flbw_err1 = _fl_err1*(alice.bandpar[_band[-1]][alice.band_label.index('equvw')]/2.)**2
      _flbw_err2 = _fl_err2*alice.bandpar[_band[-1]][alice.band_label.index('equvw')]/2.

      flsum += _flbw
    # errors on photometry summed as random
      flsum_err1 += _flbw_err1
    # errors on extinction summed as systematic
      flsum_err2 += _flbw_err2        

      flsum_err = sqrt(flsum_err1+flsum_err2**2)
      fl_err = sqrt(array(fl_err1)+array(fl_err2)**2)
    
      if checksed:
         plot(lam,log10(array(fl)),'ro')
         plot(lam,log10(array(fl)),'r-')
         xlabel('wavelength')
         ylabel('log(fl)')
         if checksed == 'o':
            errorbar(lam,log10(array(fl)),fl_err/array(fl)/log(10),ecolor='r')
	    text(lam[-1]+150,log10(fl[-1]),str(int(phint[i])),fontsize=12)
            draw()
            raw_input('... next epoch ...')
            clf()
         else: 
            text(lam[-1]+150,log10(fl[-1]),str(int(phint[i])),fontsize=6)
            draw()
            raw_input('... next epoch ...')
            clf

      if i ==0:            #    write SED   ################################
         sedf.write(' ph  ')
         for j in range(len(_band)):
            sedf.write('%16s' % (_band[j]))
         sedf.write(' \n')
      sedf.write('%5.1f' % (phint[i]))
      for j in range(len(_band)):
         sedf.write(' %8.2e %8.2e ' % (fl[j],fl_err[j]))
      sedf.write(' \n')  ###################################################
         
         
      logL.append(log10(flsum)+log10(4*pi)+2*((sndata['mu']+5)/5.+log10(3.08E18)))
      logL_err.append(sqrt((flsum_err/(log(10)*flsum))**2+(2*(sndata['mu_err']/5.))**2))
    
   if checksed and checksed != 'o': show()   # comment to see SED per day

   print '_____________________________________________________'
   print '>>> output file: ',outfile  

   ff = open(outfile,'w')
   ff.write('# SN'+sndata['sn']+'    bands='+_band+' \n')
   ff.write('# mu=%5.2f+/-%4.2f ' % (sndata['mu'],sndata['mu_err']))
   ff.write(' ABg=%4.2f+/-%4.2f' % (sndata['ABg'],sndata['ABg_err']))
   ff.write(' ABi=%4.2f+/-%4.2f' % (sndata['ABi'],sndata['ABi_err']))
   if 'Rv' in sndata.keys(): ff.write(' (R_V='+str(round(sndata['Rv'],2)))
   ff.write(' \n')

   phsort = sorted(phint)
   for i in range(len(phsort)):
      ff.write('%6.2f  %6.3f %6.3f \n' % (phsort[i],logL[i],logL_err[i]))
   ff.close()

#######################################   x input al modelling
   ff = open('bol_fit_input.dat','w')
   ff.write('# SN'+sndata['sn']+'    bands='+_band+' \n')
   ff.write('# mu=%5.2f+/-%4.2f ' % (sndata['mu'],sndata['mu_err']))
   ff.write(' ABg=%4.2f+/-%4.2f' % (sndata['ABg'],sndata['ABg_err']))
   ff.write(' ABi=%4.2f+/-%4.2f' % (sndata['ABi'],sndata['ABi_err']))
   if 'Rv' in sndata.keys(): ff.write(' (R_V='+str(round(sndata['Rv'],2)))
   ff.write(' \n')

   for i in range(len(phsort)):
      ff.write('%6.2f  %8.2f  %6.3f  %6.3f \n' % (phsort[i],phsort[i]+sndata['jdmax'][_bandref],\
                              10**(logL[i]-40.),10**(logL[i]-40.)*log(10)*logL_err[i]))
   ff.close()
#############################################

   close()
   errorbar(phsort,logL,fmt='o',yerr=logL_err)
   xlabel('phase [d]')
   ylabel('log L_BOL')
   title('SN '+sndata['sn'],fontsize=18)
   figtext(0.7,0.85,_band)
   figtext(0.7,0.8,'mu='+str(round(sndata['mu'],2))+'+/-'+str(round(sndata['mu_err'],2)))
   figtext(0.7,0.75,'ABg='+str(round(sndata['ABg'],2))+'+/-'+str(round(sndata['ABg_err'],2)))
   figtext(0.7,0.7,'ABi='+str(round(sndata['ABi'],2))+'+/-'+str(round(sndata['ABi_err'],2)))
   if 'Rv' in sndata.keys(): figtext(0.75,0.65,'R_V='+str(round(sndata['Rv'],2)))
   
   raw_input('.... return to close....')
