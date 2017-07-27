description=">> list available data in archive"
usage = "%prog [Ia,II,Ibc,IIn,all] [band] "
###############
import os,shutil,sys,glob
from numpy import *
from optparse import OptionParser
import alice

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--noskip",dest="noskip",\
                  action="store_true",default=False,
                  help='Do not skip errors \t\t [%default]')
    option,args = parser.parse_args()
    if len(args)<1 : sys.argv.append('--help')
    option,args = parser.parse_args()


def alist(sntype,band,noskip):

    alice_file = glob.glob(alice.alice_data+'1*.dat')
    alice_file += glob.glob(alice.alice_data+'2*.dat')

    isel = 0
    for _s in alice_file:
        #print _s
        try: sndata = alice.leggifile(_s[:-4])
        except:
            print "!!! ERROR Reading file ",_s,"    !!!"
            if noskip: verify(_s[:-4])

     # SN TYPE
        selsn = False
        if sntype in ['Ia','II'] and sntype == sndata['sntype'][:2]: \
           selsn = True            
        elif sntype == 'Ibc' and ('Ib' == sndata['sntype'][:2] or\
                           'Ic' == sndata['sntype'][:2]): selsn = True         
        elif sntype == 'IIn' and sntype == sndata['sntype'][:3]:\
             selsn = True
        elif sntype == 'all': selsn = True
     # BANDS
        selb = True
        for b in band:
            if band == 'any': selb = True
            elif b in sndata['bands']: selb *= True
            else: selb *= False

        b = 'B'
        if b not in sndata['bands']: b = sndata['bands'][0]
        jds = compress(array(sndata['source'][b])>=0,array(sndata['jd'][b]))    
        if selsn and selb:
            if len(jds)>1: phrange = int(max(jds)-min(jds))
            else: phrange = 0
            print '%-12s %-8s %-20s   %dd' % \
                 (sndata['sn'],sndata['sntype'],sndata['bands'],phrange)
            isel += 1
    print ' There are light curves for ',isel,' SN'       
##########################################################################

if __name__ == "__main__":

    sntype=args[0]
    if len(args)>1: band=args[1]
    else: band = 'any'

    alist(sntype,band,option.noskip)

