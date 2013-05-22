"""

About
=========
:synopsis:     a class / api for parsing netica input files 
:moduleauthor: Kevin Netherton
:date:         5-13-2013
:description:  Need to be able to parse netica input .dne or .dnet 
               ascii files.  This class provides a very simple
               api to read a netica file, parse it, and return 
               a python data structure with the information in the 
               file.
      
Dependencies:
-------------------
This script depends on the pyPEG2 library to make parsing the netica files
easier.  The easiest way to install this is with pip.

   pip install pyPEG2
   

:comment:  Yes I could have parsed this file using something like ply, pypeg, 
           pybison, etc.  I did take a look at a number of these parsing libraries
           and was un-able to figure them out.  In the end I was able to write my own 
           parser in way less time then it would have taken to figure out one
           of these frameworks.  :(  I'd be happy to try a different way if someone  
           can get me started quickly with some demo's.
           
API DOC:
===============     
"""

import re
import sys

class parseDNET(object):
    inputDnetFile = ''
    
    # regular expressions used my class
    re_comments = None
    re_propertyAssign = None
    re_startMultiLine = None
    re_structStartMultiLine = None
    
    # variables that are used by objects to help 
    # with the parsing.
    prevLine = ''
    curLine = ''
    fh = None
    
    # used to help with recursive development of the structure.
    struct = {}
    curStruct = None
    prevStruct = None
    
    def __init__(self, inputDnetFile):
        self.inputDnetFile = inputDnetFile
        
    def buildRegularExpressions(self):
        # read through once finding the start and end 
        # of structures, 
        # start = [20, 23, 24, 25, 34...
        # end = [23, 24, 25, 32]
        
        
        self.re_comments = re.compile("^\s*//.*")
        self.re_propertyAssign = re.compile("^\s*\w+\s*=\s*[A-Z]+;")
        self.re_startMultiLine = re.compile("^\s*\w+\s*=\s*$")
        self.re_structStartMultiLine = re.compile("^\s*\w+\s+\w+\s+\{\s*$")
        self.re_multiLineStringStart = re.compile('^\s*\w+\s*=\s*\".*\\$')
        
    def parseLine(self):
        # only called when the structure is initialised, should only happen once
        if self.curStruct == None:
            self.curStruct = self.struct
            
        line = self.fh.readline()
        if line:
            line = line.replace("\n", "")
            if self.re_comments.match(line):
                print 'comment: ', line
                self.parseLine()
            elif self.re_structStartMultiLine.match(line):
                print 'start data sturct:', line
                type = line.split(' ')[0]
                name = line.split(' ')[1]
                self.prevStruct = self.curStruct
                if not self.curStruct.has_key(type):
                    self.curStruct[type] = {}
                if not self.curStruct[type].has_key(name):
                    self.curStruct[type][name] = {}
                self.parseLine(line)
                    
                
                
            # is the line  a comment, if so ignore
            
            # if the line is the start of a struct, 
            
        
    def parse(self):
        bnet = {}
        startStructs, endStructs = self.getStructStartEnds()
        fh = open(self.inputDnetFile, 'r')
        linecnt = 1
        struct = {}
        prevStruct = None
        started = False
        for line in fh:
            
            line = line.replace("\n", '')
            print 'line -', line
            # everything needs to be part of a struct, so 
            # don't even bother with a line until it indicates 
            # that its part of the start of a struct
            if startStructs.count(linecnt) and endStructs.count(linecnt):
                # single line struct, need to treat a little different
                # syntax is type{atrib=val; atrib=val; attrib=;}
                key, singleLineStruct = self.parseSingleLineStruct(line)
                
            if startStructs.count(linecnt):
                started = True
                # started a struct, now parse it.
                # is it a one line struct?
                structName = line.split(' ')[1]
                print '  structName is: ', structName
                structType = line.split(' ')[0]
                prevStruct = struct
                struct[structName] = {}
                struct = struct[structName]
            if endStructs.count(linecnt):
                # structure ends!
                pass
                
            if started:
                pass
                
            linecnt += 1
    
    def parseSingleLineStruct(self, line):
        
        # parse a line like
        # nodefont = font {shape= "Arial"; size= 10;}; 2
        #
        # return as a key nodefont and a dictionary 
        # that lookes like:
        # dict['font'] = { 'shape':'Arial', 
        #                  'size': 10 }
        #
        line = line.strip()
        key = line.split('=')[0]
        # pull out everyting to the right of the first = sign
        rest = line[line.find('=') + 1:]
        
        secondKey = rest[0:rest.find('{')]
        print 'second key is:', secondKey
        propertyList = rest[rest.find('{'):]
        propertyList = propertyList.strip(';')
        print 'propertyList is:', propertyList
        #print 
        rest = line.split('=')[1].replace('{', '').replace('}', '').strip().split(';')
        print rest
        sys.exit()
        
    def getStructStartEnds(self):
        fh = open(self.inputDnetFile, 'r')
        lineNum = 1
        structStarts = []
        structEnds = []
        for line in fh:
            if line.count('{'):
                structStarts.append(lineNum)
            if line.count('}'):
                structEnds.append(lineNum)
            lineNum += 1
        
        structStarts.sort()
        structEnds.sort()
        print 'startKeys:', structStarts, len(structStarts)
        print 'endKeys:', structEnds, len(structEnds)
        return structStarts, structEnds
        
if __name__ == '__main__':
    dnetFile = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica\Car_Buyer.dnet.txt'
    parser = parseDNET(dnetFile)
    parser.parse()
    
    