description=">> verify SN.dat format"
usage = "%prog (./)snname  "
###############
import os,shutil,sys
from numpy import *
from optparse import OptionParser
import alice

if __name__ == "__main__":
    parser = OptionParser()
    option,args = parser.parse_args()
    if len(args)<1 : sys.argv.append('--help')
    option,args = parser.parse_args()


def verify(sn):
 
    if '/' not in sn: sn = alice.alice_data+sn 
    if not  os.path.isfile(sn+'.dat'):
        print "!!! ERROR: file "+sn+".dat not found !!!"
        return

    sndata   = alice.leggifile(sn)
        
    print '-----------------------------------------------------------------'
    print 'SN=',sndata['sn'],'   type=',sndata['sntype'],'   galaxy=',sndata['galaxy'],' (format=',sndata['format'],')'
    print ' abg=',round(sndata['ABg'],2),'+/-',round(sndata['ABg_err'],2),\
          ' abi=',round(sndata['ABi'],2),'+/-',round(sndata['ABi_err'],2),\
          ' mu=',round(sndata['mu'],2),'+/-',round(sndata['mu_err'],2), 
    if 'Rv' in sndata.keys(): print ' Rv=',round(sndata['Rv'],2),'+/-',round(sndata['Rv_err'],2)
    else: print
    _jd,_source = [],[]
    for b in sndata['bands']:
        _jd += sndata['jd'][b]
        _source += sndata['source'][b]
    print 'phase range ',round(max(_jd)-min(_jd),0),'days',
    if sndata['jd_expl']: print '   JD(explosion)=',round(sndata['jd_expl'],2)
    else: print
    print 'band    jd_max         m_max            mag range '
    for b in sndata['bands']:
        print '%8.2f+/-%4.2f    %6.3f+/-%5.3f   %6.3f - %6.3f' % \
             (sndata['jdmax'][b],sndata['jdmax_err'][b],\
              sndata['magmax'][b],sndata['magmax_err'][b],\
              min(sndata['mag'][b]),max(sndata['mag'][b]))
    print 'Sources:', unique(abs(array(_source))).tolist()
    print '-----------------------------------------------------------------'
    
    return sndata    

if __name__ == "__main__":

    sn = args[0]
   
    verify(sn)
