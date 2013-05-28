'''
Created on 2013-05-22

@author: kjnether
'''



def playregex():
    import re
    
    #regex =  re.compile('^\s*\w+\s*=\s*\({1}([0-9],)+\;{1}$')
    # regex =  re.compile('^\s*\w+\s*=\s*\({1}[0-9]+(,[0-9]+)*\){1}\;{1}$')
    # regex =  re.compile('^\s*\w+\s*=\s*\({1}[0-9]+(\s*,{1}\s*[0-9])+\){1}\;{1}$')
    #regex =  re.compile(r'^\s*\w+\s*=\s*\({1}\s*[0-9]+(\s*,{1}\s*[0-9]+)+')
    
    # simple list
    regex =  re.compile(r'^\s*\w+\s*={1}\s*\({1}\s*[0-9]+(\s*,{1}\s*[0-9]+)*\s*\){1}\s*\;{1}\s*$')
    line = '   center = (306, 60, 23);'
    line = '   center = (306, 60, 23'
    line = 'somevar = ( 23, 342  ) ;  '
    
    
    if regex.match(line):
        print 'matched'
    else:
        print 'Nope'
        
def playTypes():
    print 'test'
    var = 2
    print type(var)
    if type(var) is int:
        print 'yup its int'
        
    var = 'test'
    print type(var)
        
        
if __name__ == '__main__':
    #playregex()
    playTypes()
    
    
    