import configparser

def read_default():       #  read parameter file ###################
    config = configparser.ConfigParser()
    config.read('ini.default')
    optlist = {}
    for s in config.sections():
        optlist[s] = {}
        for o in config.options(s):
            optlist[s][o] = config.get(s,o)
    return optlist

def show_list(optlist):
    print '#'*10,'\n'
    print 'NOTE: 1.default; 2.bad subtraction/bright 3.dipole 4.real 5.nothing/limit 0.skip /n'
    print '#'*10,'\n'
    for key in optlist:
        print 'params read as:\n','#'*10,key
        for key1 in optlist[key]:
            print key1,': ',optlist[key][key1]
