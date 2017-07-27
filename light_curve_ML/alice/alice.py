import os,shutil,socket,sys,string,re
from numpy import *
from optparse import OptionParser

alice_dir =  os.path.expandvars("$alice_dir")

home = os.getenv('HOME')
host = socket.gethostname()
if 'passto' in host : alice_data ='/home/supern/alice/data/'
elif 'dark' in host : alice_data ='/dark/hal/SNDATABASE/LC/'
else: alice_data = home+'/supern/alice/data/'
    
# Filter parameter
# Zero point vegamag computed with synphot
bandpar={}
band_label= ['bandw','fwhm','avgwv','equvw','zpoint','abmag for vega']
#landolt & johnson buser and kurucz 78
bandpar['U']=[205.79,484.6,3652,542.62,4.327e-9,  0.76] 
bandpar['B']=[352.94,831.11,4448,1010.3,6.09e-9, -0.11] 
bandpar['V']=[351.01,826.57,5505,870.65,3.53e-9,  0.] 
#landolt & cousin bessel 83
bandpar['R']=[589.71,1388.7,6555,1452.2,2.104e-9, 0.18]
bandpar['I']=[381.67,898.77,7900.4,1226,1.157e-9, 0.42]
# HAWK-I filter
bandpar['Y']=[0,1019.4,10226.9,0,5.74e-10, '?'] 
#bessel in bessel and brett 88
bandpar['J']=[747.1,1759.3,12370,2034,3.05e-10, '?'] 
bandpar['H']=[866.55,2040.6,16471,2882.8,1.11e-10, '?'] 
bandpar['K']=[1188.9,2799.6,22126,3664.3,3.83e-11, '?']
# ASIAGO PHOTOMETRIC DATABASE
bandpar['L']=[0.,9000.,34000,0.,8.1e-12, '?'] 
bandpar['M']=[0.,11000.,50000,0.,2.2e-12, '?'] 
bandpar['N']=[0.,60000.,102000,0.,1.23e-13, '?']
# sloan
bandpar['u']=[194.41,457.79, 3561.8, 60.587,3.622e-9, 0.92]
bandpar['g']=[394.17,928.19, 4718.9, 418.52,5.414e-9, -0.11]
bandpar['r']=[344.67,811.65, 6185.2, 546.14,2.472e-9, 0.14]
bandpar['i']=[379.57,893.82, 7499.8, 442.15,1.383e-9, 0.36]
bandpar['z']=[502.45,1183.2, 8961.5, 88.505,8.15e-10, 0.52] 
# SWIFT A-> UW1, D --> UM2, S -> UW2 
bandpar['A']=[0.,693.,2634,0.,4.1e-9, '?'] # Transmission curve from 
bandpar['D']=[0.,498.,2231,0.,4.6e-9, '?'] # Breeveld et al. 2011
bandpar['S']=[0.,657.,2030,0.,5.2e-9, '?']

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-v", "--verbose",dest="verbose",\
                  action="store_true",default=False,
                  help='Print tasks description')
    option,args = parser.parse_args()
   
def aiuto(verbose):   ###################                ####################
    ff = open(alice_dir+'alice.bash')
    righe = ff.readlines()
    print "#"*20+"       ALICE        "+"#"*20
    for r in righe:
        if 'alias ' == r[:6] and 'alice=' not in r:
            prog = r[len('alias '):r.index('=')]
            exec('import '+prog)
            print prog,
            exec('print '+prog+'.usage[6:]')
            if verbose:
                print "      ",
                exec('print '+prog+'.description')
    if verbose:
        print "      "+clean.description
    print "#"*60+"   @enrico"


################################# leggi.py ###########################
#########################    WEB FORMAT
def webform(riga):
    
     sndata = {}
     sndata['sn'] = string.split(riga[0])[0]
     sndata['sntype'] = string.split(riga[0])[1]
     sndata['galaxy'] = string.split(riga[1])[0]
     par = ['ABg','ABi','mu','Rv']
     for _par in par:
         _ip = string.find(string.lower(riga[1]),string.lower(_par))
	 if _ip >=0: 
	     sndata[_par]     = float(riga[1][_ip+1:].split()[1])
	     sndata[_par+'_err'] = float(riga[1][_ip+1:].split()[2])

     _bands,instr = [],[]
     jd,mag,mag_err = {},{},{}
     phflag,magtype,source = {},{},{}
     for r in riga[2:]:
         _dd,_jd,f,_magtype,_mag,_err,_phflag,_instr = r.split()
         if f not in jd: 
             _bands.append(f)
             jd[f],mag[f],mag_err[f],phflag[f],magtype[f],source[f] = \
                 [],[],[],[],[],[]
         jd[f].append(float(_jd))
         mag[f].append(float(_mag))
         mag_err[f].append(float(_err))
         phflag[f].append(_phflag)
         magtype[f].append(_magtype)
         source[f].append(_instr)
         instr.append(_instr)

     vega = ['U','B','V','R','I','J','H','K','UW1','UM2','UW2']
     abmag = ['u','g','r','i','z']
     nflt = {'UW1':'A','UM2':'D','UW2':'S'}

     sourcelist = unique(array(instr))

     sndata['bands'] = ''
     for f in _bands:
         if f in vega or f in abmag:
             if f in nflt: sndata['bands'] += nflt[f]
             else: sndata['bands'] += f
         else: print "!!! WARNING: band",f,"not yet implemented !!!"

     sndata['format'] = 'WEB'
     sndata['jd'],sndata['source']=jd,source
     sndata['mag'],sndata['mag_err'] = mag,mag_err

     instr = []
     for f in jd.keys():
         for i,p in enumerate(sndata['jd'][f]):
             ii = where(sourcelist==source[f][i])[0][0]+1
             sndata['source'][f][i] = ii 
             if phflag[f][i]=='U': sndata['source'][f][i] *= -1
             
             if f in vega and magtype[f][i] != 'vega': 
                 print '!!! WARNING: magtype for filter',f,'is not vega as expected TBD!!!'
             elif f in abmag and magtype[f][i] != 'abmag': 
                 print '!!! WARNING: magtype for filter',f,'is not abmag as expected TBD!!!'

     for f in jd.keys():
         if f in nflt:
             sndata['jd'][nflt[f]] = sndata['jd'].pop(f)
             sndata['mag'][nflt[f]] = sndata['mag'].pop(f)
             sndata['mag_err'][nflt[f]] = sndata['mag_err'].pop(f)
             sndata['source'][nflt[f]] = sndata['source'].pop(f)

     for f in sndata['bands']:
         if 'jdmax' not in sndata:
             for s in ['jdmax','jdmax_err','magmax','magmax_err']:sndata[s]= {}
         sndata['jdmax'][f] = min(sndata['jd'][f])
         sndata['jdmax_err'][f] = 0
         sndata['magmax'][f] = min(sndata['mag'][f])
         sndata['magmax_err'][f] = 0

     return sndata

#########################    LAST FORMAT
def lastform(riga):
     sndata = {}
     sndata['sn'] = string.split(riga[0])[0]
     sndata['sntype'] = string.split(riga[0])[1]
     sndata['galaxy'] = string.split(riga[1])[0]
     par = ['ABg','ABi','mu','Rv']
     for _par in par:
         _ip = string.find(string.lower(riga[1]),string.lower(_par))
	 if _ip >=0: 
	     sndata[_par]     = float(riga[1][_ip+1:].split()[1])
	     sndata[_par+'_err'] = float(riga[1][_ip+1:].split()[2])

     sndata['jd_expl'] = False
     if 'jd_expl=' in riga[0]:
         _ir = string.index(riga[0],'=')+1
         sndata['jd_expl'] = float(string.split(riga[0][_ir:])[0])

     jdmax,magmax,jdmax_err,magmax_err = {},{},{},{}

     iband = []
     for i in range(2,len(riga)):
          _r = string.strip(riga[i])
          if _r:
              if _r[0] in 'ugriz' and  'jd_max' in string.lower(_r): 
                  iband.append(i)
              if _r[0] in 'YJHKLMN' and  'jd_max' in string.lower(_r): 
                  iband.append(i)
              if _r[0] in 'ASD' and  'jd_max' in string.lower(_r): 
                  iband.append(i)
     iband.append(len(riga))

     riri = [[3,iband[0]-1]]
     for i in range(1,len(iband)):
         riri.append([riri[i-1][1]+1,iband[i]-1])

     bands = ''
     jd,mag,mag_err,source ={},{},{},{}
     for ri in riri:
         _bands = string.split(riga[ri[0]])[0]
         if _bands not in bands: bands += _bands
         for b in _bands:
             c = string.index(_bands,b)*2+2
             jdmax[b]     = float(string.split(riga[ri[0]])[c])
             jdmax_err[b] = float(string.split(riga[ri[0]])[c+1])
             magmax[b]    = float(string.split(riga[ri[0]+1])[c-1])
             magmax_err[b]= float(string.split(riga[ri[0]+1])[c])
             jd[b],mag[b],mag_err[b],source[b] = [],[],[],[]
             for i in range(ri[0]+3,ri[1]):
                 if len(string.strip(riga[i])) > 0:
                     if string.lstrip(riga[i])[0] != '#':
                         _mag = float(string.split(riga[i])[c])
                         if _mag<999:
                             jd[b].append(float(string.split(riga[i])[1]))
                             mag[b].append(float(string.split(riga[i])[c]))  
                             mag_err[b].append(float(string.split(riga[i])[c+1]))
                             source[b].append(float(string.split(riga[i])[len(_bands)*2+2]))
     # bands sort
     lam = []
     for b in bands: 
         lam.append(bandpar[b][band_label.index('avgwv')])
     _bands = ''
     for i in argsort(lam):
         _bands += bands[i]
          
     sndata['bands'] = _bands
     sndata['jdmax'],sndata['jdmax_err']=jdmax,jdmax_err
     sndata['magmax'],sndata['magmax_err'] = magmax,magmax_err 
     sndata['format'] = 'LAST'
     sndata['jd'],sndata['source']=jd,source
     sndata['mag'],sndata['mag_err'] = mag,mag_err

     return sndata

##################################  NEW FORM    
def newform(riga):

     sndata = {}
     sndata['sn'] = string.split(riga[0])[0]
     sndata['sntype'] = string.split(riga[1])[0]
     sndata['galaxy'] = string.split(riga[3])[0]
     par = ['ABg','ABi','mu','Rv']
     for _par in par:
         _ip = string.find(riga[3],_par)
	 if _ip >=0: 
	     sndata[_par]     = float(riga[3][_ip+1:].split()[1])
	     sndata[_par+'_err'] = float(riga[3][_ip+1:].split()[2])

     sndata['jd_expl'] = False
     if 'jd_expl=' in riga[0]:
         _ir = string.index(riga[0],'=')+1
         sndata['jd_expl'] = float(string.split(riga[0][_ir:])[0])

     jdmax,magmax,jdmax_err,magmax_err = {},{},{},{}
     bands = string.split(riga[4])[0]
     jd,mag,mag_err,source ={},{},{},{}
     for b in bands: 
         c = string.index(bands,b)*2+1
         jdmax[b]     = float(string.split(riga[0])[c])
         jdmax_err[b] = float(string.split(riga[0])[c+1])
         magmax[b]    = float(string.split(riga[1])[c])
         magmax_err[b]= float(string.split(riga[1])[c+1])
         c += 1
         jd[b],mag[b],mag_err[b],source[b] = [],[],[],[]
         for i in range(6,len(riga)):
             if len(string.strip(riga[i])) > 0:
               if string.lstrip(riga[i])[0] != '#':
                   _mag = float(string.split(riga[i])[c])
                   if _mag < 999:
                       jd[b].append(float(string.split(riga[i])[1]))
                       mag[b].append(_mag)
                       mag_err[b].append(float(string.split(riga[i])[c+1]))
                       source[b].append(float(string.split(riga[i])[len(bands)*2+2]))
  
     sndata['bands'] = bands
     sndata['jdmax'],sndata['jdmax_err']=jdmax,jdmax_err
     sndata['magmax'],sndata['magmax_err'] = magmax,magmax_err 
     sndata['format'] = 'NEW'
     sndata['jd'],sndata['source']=jd,source
     sndata['mag'],sndata['mag_err'] = mag,mag_err

     return sndata

################################   OLD FORM
def oldform(riga):
     sn      = string.split(riga[0])[0]
     sntype  = string.split(riga[1])[3]
     galaxy  = string.split(riga[0])[3]
     abg     = float(string.split(riga[0])[4])
     abg_err = 0.
     abi     = float(string.split(riga[1])[4])
     abi_err = 0.
     mu      = float(string.split(riga[0])[5])
     mu_err  = 0. 
     jd_expl = False
     if 'jd_expl=' in riga[0]:
         _ir = string.index(riga[0],'=')+1
         jd_expl = float(string.split(riga[0][_ir:])[0])

     jdmax,magmax,jdmax_err,magmax_err = {},{},{},{}
     jdmax['B']     = float(string.split(riga[0])[1])
     jdmax_err['B'] = 0.
     magmax['B']    = float(string.split(riga[0])[2])
     magmax_err['B']= 0.

     _bands = string.split(riga[3])[3:-1]
     _jd,_mag,_source = {},{},{}
     for b in _bands:
         _jd[b],_mag[b],_source[b] = [],[],[]
     for i in range(4,len(riga)):
         for c in range(len(_bands)):
             b = _bands[c]
             if len(string.strip(riga[i])) > 0:
                 if string.lstrip(riga[i])[0] != '#':
                     if string.find(string.split(riga[i])[c+3],':') > 0:
                         _mm = float(string.split(riga[i])[c+3][:-1])
                     else:
                         _mm = float(string.split(riga[i])[c+3])
                     if _mm > 0:
                         _jd[b].append(float(string.split(riga[i])[2]))
                         _mag[b].append(_mm)
                         _str = string.split(riga[i])[len(_bands)+3]
                         try: _strf = float(_str)
                         except:
                             if 'lim' in _str: _strf = -1
                             else: _strf = 1
                         _source[b].append(_strf)

     for b in _bands:
         if 'lim' in b:
             if b[:-3] in _bands:
                 _jd[b[:-3]] +=_jd[b]
                 _mag[b[:-3]] += _mag[b]
                 _source[b[:-3]] += (zeros(len(_source[b]))-1).tolist()
             else:
                 _jd[b[:-3]] =_jd[b]
                 _mag[b[:-3]] = _mag[b]
                 _source[b[:-3]] = (zeros(len(_source[b]))-1).tolist()
                 _bands += b[:-3]
                 
     for b in _bands:
         if b == 'Mpg':
             if 'B' in _bands:
                 _jd['B'] += _jd[b]
                 _mag['B'] += (array(_mag[b])+0.29).tolist()
                 _source['B'] += _source[b]
             else:    
                 _jd['B'] = _jd[b]
                 _mag['B'] = (array(_mag[b])+0.29).tolist()
                 _source['B'] = _source[b]
             _bands += 'B'
         if b == 'Mpv' or b == 'vis':
             if 'V' in _bands:
                 _jd['V'] += _jd[b]
                 _mag['V'] += _mag[b]
                 _source['V'] += _source[b]
             else:
                 _jd['V'] = _jd[b]
                 _mag['V'] = _mag[b]
                 _source['V'] = _source[b]
             _bands += 'V'
         if b == 'CCD':
             if 'R' in _bands:
                 _jd['R'] += _jd[b]
                 _mag['R'] += _mag[b]
                 _source['R'] += _source[b]
             else:
                 _jd['R'] = _jd[b]
                 _mag['R'] = _mag[b]
                 _source['R'] = _source[b]
             _bands += 'R'

     bands =''
     jd,mag,mag_err,source = {},{},{},{}
     for b in _bands:
         if b in ['U','B','V','R','I','J','H','K']:
            bands += b
            jdmax[b]     =  jdmax['B']
            jdmax_err[b] =  jdmax_err['B']
            magmax[b]    =  magmax['B']
            magmax_err[b]=  magmax_err['B']
            jd[b] = _jd[b]                                      
            mag[b] = _mag[b]
            mag_err[b] = (zeros(len(mag[b]))).tolist()
            source[b] = _source[b]
                                                
     sndata = {'sn':sn, 'sntype':sntype, 'galaxy':galaxy, 'bands':bands,
               'ABg':abg, 'ABg_err':abg_err, 'ABi':abi, 'ABi_err':abi_err,\
               'mu':mu, 'mu_err':mu_err, 'jd_expl':jd_expl, \
               'jdmax':jdmax, 'jdmax_err':jdmax_err, 'magmax':magmax,\
               'magmax_err':magmax_err, 'format':'OLD',\
               'jd':jd, 'mag':mag, 'mag_err':mag_err, 'source':source}
     return sndata

#########################################################################
def leggifile(snfile):

    lcf = open(snfile+'.dat','r')
    riga = lcf.readlines()
    check1 = string.split(riga[0])[1]
    check2 = string.split(riga[1])[0]

    if riga[0][0]=='*':
        return webform(riga)
    elif re.search('[a-zA-Z]',check1):
        #print snfile,'LAST',
         return lastform(riga)
    elif re.search('[a-zA-Z]',check2):
        #print snfile,'NEW',
        return newform(riga)            
    else:
        #print snfile,'OLD',
        return oldform(riga)

def cardelli(lam,Rv):
# CARDELLI LAW (Cardelli et al. 1989, ApJ 345, 245)
  x = 10000./lam
  # CARDELLI start from 0.3, but NED extends it to L band 
  if x>=0.1 and x<=1.1:
      y = x**1.61
      a = 0.574*y
      b = -0.527*y
  
  if x>1.1 and x <3.3:
      y = x-1.82 
      a = 1+y*(0.17699 + y * (-0.50447 + y * (-0.02427 +y * (0.72085 + y * (0.01979 + y * (-0.77530 + y * 0.32999))))))
      b = y * (1.41338 + y * (2.28305 + y * (1.07233 + y * (-5.38434 + y * (-0.62251 + y * (5.30260 +y * (-2.09002)))))))

  if x>=3.3 and x <8.0:
      y = (x - 4.67)**2 
      a = 1.752 - 0.316 * x - 0.104 / (y + 0.341)
      b = -3.090 + 1.825 *x + 1.206 / (y + 0.263) 

      if x>=5.9 and x<8.0:
          y = x - 5.9
          a +=  - 0.04473 * y**2 - 0.009779 * y**3
          b +=  + 0.2130 * y**2 + 0.1207 * y**3

  if x>=8.0:	
      y = x - 8. 
      a = -1.073 - 0.628 * y + 0.137 * y**2 - 0.070 * y**3
      b = 13.670 + 4.257 * y - 0.420 * y**2 + 0.374 * y**3

  Al_AV = a + b/ Rv
  return Al_AV

def AX(band='',AB='',R_V=3.1):

    if not band: band = raw_input('<<  Band ? ')
    if AB=='': AB = float(raw_input('<<  Ab absorption ? '))
    
    abfac = cardelli(bandpar[band][band_label.index('avgwv')],R_V)\
            /cardelli(bandpar['B'][band_label.index('avgwv')],R_V)
    return AB*abfac

if __name__ == "__main__":
    aiuto(option.verbose)

