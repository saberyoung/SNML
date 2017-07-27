import os,sys
sys.path.append('lib/')
from ini import *

#####################################
params = read_default()
answ = params['global']['run']
jd = params['global']['jd']
area_factor = params['global']['area_factor']
show_list(params)

#####################################
if int(answ)==1:
    answ1 = raw_input('1.judge or 2.check')
    if int(answ1) == 1:
        os.system('python bin/snml1.py')
    elif int(answ1) == 2:
        os.system('python bin/snpre1.py 1')
    else:print 'no task!!'
elif int(answ)==2:
    os.system('python bin/eyeballcandidate.py 1')
    answ1 = raw_input('1.judge or 2.check')
    if int(answ1) == 1:
        os.system('python bin/snml2.py')
    elif int(answ1) == 2:
        os.system('python bin/snpre2.py 1')
    else:print 'no task!!'
else:
    print 'wrong option for ini/run param!'
