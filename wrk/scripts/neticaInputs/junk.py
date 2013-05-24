'''
Created on 2013-05-22

@author: kjnether
'''
line = 'comment = "An example influence diagram for Joe, who has to decide \\'
tmpList = line.split('=')
startNum = tmpList[1].index('"')
entry = tmpList[1][startNum + 1:].rstrip(r'\\').strip()
print entry

var = '2342342.2342342'
print 'var is:', var, 'is number?', var.isdigit()