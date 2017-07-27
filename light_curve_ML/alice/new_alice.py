description='''
input alice file into mysql database
By default sloan filters are set to ab, all other vega. All record are set to private
'''
from numpy import *
import os,string,re,sys
import pymysql as mdb
import argparse

luser = {'enrico':'enrico','apasto':'andrea','benetti':'stefano',\
          'toma':'lina','ner':'nancy'}

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

swiftfilt ={'A':'UW1', 'D':'UM2', 'S':'UW2'}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description,\
         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("sn",help="sn name")

    parser.add_argument("-j", "--jd",action="store_true",\
           dest='jdinp',default=False,help='input are jd')
    parser.add_argument("-p", "--public",action="store_true",\
           dest='kpublic',default=False,help='data are to be set public')

    args = parser.parse_args()    

def lastform(riga):
     sndata = {}
     sndata['sn'] = string.split(riga[0])[0]
     sndata['sntype'] = string.split(riga[0])[1]
     sndata['galaxy'] = string.split(riga[1])[0]
     par = ['ABg','ABi','mu','Rv']
     for _par in par:
          _ip = string.find(string.lower(riga[1]),string.lower(_par))
          if _ip >=0:
               sndata[_par] = float(riga[1][_ip+1:].split()[1])
               sndata[_par+'_err'] = float(riga[1][_ip+1:].split()[2])

     sndata['jd_expl'],sndata['jd_expl_err'] = False,False
     if 'jd_expl=' in riga[0]:
         _ir = string.index(riga[0],'=')+1
         sndata['jd_expl'] = float(string.split(riga[0][_ir:])[0])
         sndata['jd_expl_err'] = float(string.split(riga[0][_ir:])[1])

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
     jd,mag,mag_err,source,notes ={},{},{},{},{}
     for ri in riri:
         _bands = string.split(riga[ri[0]])[0]
         if _bands not in bands: bands += _bands
         for b in _bands:
             c = string.index(_bands,b)*2+2
             jdmax[b]     = float(string.split(riga[ri[0]])[c])
             jdmax_err[b] = float(string.split(riga[ri[0]])[c+1])
             magmax[b]    = float(string.split(riga[ri[0]+1])[c-1])
             magmax_err[b]= float(string.split(riga[ri[0]+1])[c])
             jd[b],mag[b],mag_err[b],source[b],notes[b] = [],[],[],[],[]
             for i in range(ri[0]+3,ri[1]):
                 if len(string.strip(riga[i])) > 0:
                     if string.lstrip(riga[i])[0] != '#':
                         _mag = float(string.split(riga[i])[c])
                         if _mag<999:
                             jd[b].append(float(string.split(riga[i])[1]))
                             mag[b].append(float(string.split(riga[i])[c]))  
                             mag_err[b].append(float(string.split(riga[i])[c+1]))
                             source[b].append(float(string.split(riga[i])[len(_bands)*2+2]))
                             if len(riga[i].split())>len(_bands)*2+3:
                                 notes[b].append(' '.join(\
                                   riga[i].split()[len(_bands)*2+3:]))
                             else: notes[b].append('')
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
     sndata['jd'],sndata['source'],sndata['notes']=jd,source,notes
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
              sndata[_par] = float(riga[3][_ip+1:].split()[1])
              sndata[_par+'_err'] = float(riga[3][_ip+1:].split()[2])

     sndata['jd_expl'],sndata['jd_expl_err'] = False,False
     if 'jd_expl=' in riga[0]:
         _ir = string.index(riga[0],'=')+1
         sndata['jd_expl'] = float(string.split(riga[0][_ir:])[0])

     jdmax,magmax,jdmax_err,magmax_err = {},{},{},{}
     bands = string.split(riga[4])[0]
     jd,mag,mag_err,source,notes ={},{},{},{},{}
     for b in bands: 
         c = string.index(bands,b)*2+1
         jdmax[b]     = float(string.split(riga[0])[c])
         jdmax_err[b] = float(string.split(riga[0])[c+1])
         magmax[b]    = float(string.split(riga[1])[c])
         magmax_err[b]= float(string.split(riga[1])[c+1])
         c += 1
         jd[b],mag[b],mag_err[b],source[b],notes[b] = [],[],[],[],[]
         for i in range(6,len(riga)):
             if len(string.strip(riga[i])) > 0:
               if string.lstrip(riga[i])[0] != '#':
                   _mag = float(string.split(riga[i])[c])
                   if _mag < 999:
                       jd[b].append(float(string.split(riga[i])[1]))
                       mag[b].append(_mag)
                       mag_err[b].append(float(string.split(riga[i])[c+1]))
                       source[b].append(float(string.split(riga[i])[len(bands)*2+2]))
                       if len(string.split(riga[i]))>len(_bands)*2+3:
                              notes[b].append(' '.join(riga[i].split()[len(_bands)*2+3:]))
                       else: notes[b].append('')
  
     sndata['bands'] = bands
     sndata['jdmax'],sndata['jdmax_err']=jdmax,jdmax_err
     sndata['magmax'],sndata['magmax_err'] = magmax,magmax_err 
     sndata['format'] = 'NEW'
     sndata['jd'],sndata['source'],sndata['notes']=jd,source,notes
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

    bibl = {}
    for r in riga:
        if '#' == r[0] and len(r.split())>=2:
            try:
                ii = int(r.split()[1])
                if ii>1000:continue
                bibl[ii] = ' '.join(r.split()[2:]).replace("=","").lstrip()
            except:
                pass

    if re.search('[a-zA-Z]',check1):
        #print snfile,'LAST',
         return lastform(riga),bibl
    elif re.search('[a-zA-Z]',check2):
        #print snfile,'NEW',
        return newform(riga),bibl            
    else:
        #print snfile,'OLD',
        return oldform(riga),bibl



def mdb_conn():           ####################   connect to mysql database  
    conn = mdb.connect('localhost', 'sngroup', 'bakkiglione','asnc')
    return conn
 
def fill_from_alice(sndata,ruser,jdinp,kpublic):

    _magmax = {}
    for m in sndata['magmax']:
        filt = m
        if m in swiftfilt: filt=swiftfilt[m]
        _magmax[filt]= (sndata['magmax'][m],sndata['magmax_err'][m])

    jdoff = 0.
    if jdinp: jdoff = -0.5
    _jdmax ={}
    for m in sndata['jdmax']:
        filt = m
        if m in swiftfilt: filt=swiftfilt[m]
        _jdmax[filt]= (sndata['jdmax'][m]+jdoff,sndata['jdmax_err'][m])

    try:
        conn = mdb_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT sn FROM alice WHERE sn=%s",sndata['sn'])
        _riga = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if _riga: 
         print "!!! WARNING: sn already in database. Skip insert"
         return

    try:
        conn = mdb_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT obj FROM impostor WHERE obj=%s",sndata['sn'])
        _riga = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    objins=True
    if _riga: 
         print "!!! WARNING: obj already in impostor database. Skip insert"
         objins = False

    _public = 'N'
    if kpublic: _public='Y'
    try:
        conn = mdb_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alice(sn,galaxy,sntype,abg,abi,mu,\
              magmax,jdmax,jdexpl,public,ruser) "+\
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
             (sndata['sn'],sndata['galaxy'],\
           sndata['sntype'],'%5.2f,%5.2f'%(sndata['ABg'],sndata['ABg_err']),\
              '%5.2f,%5.2f'% (sndata['ABi'],sndata['ABi_err']),\
              '%5.2f,%5.2f'% (sndata['mu'],sndata['mu_err']),str(_magmax),\
              str(_jdmax),'%.2f,%.2f' % (sndata['jd_expl'],\
             sndata['jd_expl_err']),_public,ruser))
        conn.commit()
        cursor.close()
        conn.close()

    except mdb.Error,e:
        return "Error= %d: %s" % (e.args[0],e.args[1])
 
    if not objins or 'impostor' not in sndata['sntype']: return 'DONE'

    try:
        conn = mdb_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO impostor(obj,galaxy,public,ruser) "+\
            "VALUES(%s,%s,%s,%s)",
             (sndata['sn'],sndata['galaxy'],_public,ruser))
        conn.commit()
        cursor.close()
        conn.close()


    except mdb.Error,e:
        return "Error= %d: %s" % (e.args[0],e.args[1])

    return 'DONE'

def fill_from_alice2(sndata,bibl,ruser,jdinp):

    try:
        conn = mdb_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT sn FROM lightcurves WHERE sn=%s",sndata['sn'])
        _righe = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if _righe: 
         print "!!! WARNING: sn photometry already in database. Skip insert photometry"
         return

    jdoff = 0.
    if jdinp: jdoff = -0.5

    conn = mdb_conn()
    cursor = conn.cursor()
    for m in sndata['jd']:
        for i in range(len(sndata['jd'][m])):
            if int(sndata['source'][m][i]) < 0: phflag = 'U'
            else: phflag = 'F' 
            ii = abs(int(sndata['source'][m][i]))
            if ii in bibl: _bibl=bibl[ii]
            else: _bibl=''
            filt = m
            magtype = 'vega'
            if m in swiftfilt: 
                 filt=swiftfilt[m]
            if m in 'ugriz':
                 magtype ='ab'
            cursor.execute('INSERT INTO lightcurves(sn,MJD,filter,magtype,mag,\
                   err,phflag,instrument,reference,notes,ruser) '+\
                "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sndata['sn'],\
                 '%10.4f' % (sndata['jd'][m][i]+jdoff),\
                   filt,magtype,'%7.3f' % sndata['mag'][m][i],\
                 '%7.3f' % sndata['mag_err'][m][i],\
                   phflag,str(ii),_bibl,sndata['notes'][m][i],ruser))
                   
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":

     snfile = args.sn
     sndata,bibl = leggifile(snfile)
     ruser = luser[os.getlogin()]
     xx = fill_from_alice(sndata,ruser,args.jdinp,args.kpublic)
     xx = fill_from_alice2(sndata,bibl,ruser,args.jdinp)

     
