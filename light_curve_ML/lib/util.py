import socket
import sys

host = socket.gethostname()
if host in ['dark']:
   host = 'dark'
   workingdirectory = '/dark/hal/test_sheng/code_sheng/machine-learning/snML/light_curve_ML/lib/'
#   execdirectory = '/'
#   rawdata = '/'
   realpass = 'configure'
else:
   sys.exit('system '+str(host)+' not recognize')

####################################################
def readpasswd(directory,_file):
    from numpy import genfromtxt
    data=genfromtxt(directory+_file,str)
    gg={}
    for i in data:
        try:
            gg[i[0]]=eval(i[1])
        except:
            gg[i[0]]=i[1]
    return gg

readpass = readpasswd(workingdirectory,realpass)
#print readpass
