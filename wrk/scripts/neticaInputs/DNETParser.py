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
        self.re_comments = re.compile(r"^\s*//.*")
        self.re_startMultiLine = re.compile(r"^\s*\w+\s*=\s*$")
        self.re_structStartMultiLine = re.compile(r"^\s*\w+\s+\w+\s+\{\s*$")
        self.re_multiLineStringStart = re.compile(r'^\s*\w+\s*={1}\s*\"{1}.+\\{1}$')
        self.re_multiLineStringEnd = re.compile(r'^\s*.*\"{1}\s*\;{1}$')
        self.re_singleLineString = re.compile(r'^\s*\w+\s*=\s*\".+\"\;{1}$')
        self.re_singleLineProperty = re.compile(r'^\s*\w+\s*=\s*(?!TRUE|FALSE)[a-zA-Z]+\;{1}$')
        self.re_singleLineBooleanProperty = re.compile('^\s*\w+\s*=\s*(TRUE|FALSE){1}\;{1}$')
        self.re_singleLineNumericProperty = re.compile('^\s*\w+\s*=\s*\d+\.*\d*\;{1}$')
        self.re_singleLineListNumbers = re.compile(r'^\s*\w+\s*={1}\s*\({1}\s*[0-9]+(\s*,{1}\s*[0-9]+)*\s*\){1}\s*\;{1}\s*$')
        self.re_singleLineListProperties = re.compile(r'^\s*\w+\s*={1}\s*\({1}\s*(?![0-9]+)[0-9a-zA-Z]+(\s*,{1}\s*(?![0-9]+)[0-9a-zA-Z]+)*\s*\){1}\s*\;{1}\s*$')
        self.re_startMultiLineDataStruct = re.compile(r'^\s*\w+\s*=\s*$')
        # TODO: the re_startMultiLineDataStruct matches 'var = ' followed by nothing.  May need to 
        #       create another regex to detect the start of a multiline data struct that looks for the 
        #       // column headers on the following line.
                
    def parseLine(self):
        # only called when the structure is initialised, should only happen once
        if self.curStruct == None:
            self.curStruct = self.struct
        # think about reading the whole thing into memory first! then iterating
        # through.
        line = self.fh.readline()
        if line:
            # TODO: Need to only strip \n characters from the very end of the line.
            line = line.replace("\n", "")
            if self.re_comments.match(line):
                # a commented out line, skip it!
                print 'comment: ', line
                self.parseLine()
            elif self.re_structStartMultiLine.match(line):
                # start of a struct, like 'bnet Car_Buyer {'
                print 'start data sturct:', line
                type = line.split(' ')[0]
                name = line.split(' ')[1]
                self.prevStruct = self.curStruct
                if not self.curStruct.has_key(type):
                    self.curStruct[type] = {}
                if not self.curStruct[type].has_key(name):
                    self.curStruct[type][name] = {}
                self.prevStruct = self.curStruct
                self.curStruct = self.curStruct[type][name]
                self.parseLine(line)
            elif self.re_multiLineStringStart.match(line):
                # detected the start of a multiline string 
                # entry.  Should now call a different method
                # that will iterate through the filehandle 
                # until it gets to the end of the multiline 
                # string.
                # TODO: Should move the line parsing to another method so that it can be tested
                varName = line.split('=')[0].strip()
                firstLineVal = line.split('=')[1].strip()
                # remvoe the trailing \ line continuation character
                # then remove any trailing spaces.
                firstLineVal = firstLineVal.rstrip(r'\\', ).strip()
                rest = self.getRestOfMultiLineComments()
                # append the values together
                value = firstLineVal + ' ' + rest
                # enter it into the structure
                self.curStruct[varName] = value
            elif self.re_singleLineString.match(line):
                varName, value = self.singleLineStringParser(line)
                self.curStruct[varName] = value
            elif self.re_singleLineProperty.match(line):
                varName, value = self.singleLineStringParser()
                self.curStruct[varName] = value
            elif self.re_singleLineBooleanProperty.match(line):
                varName, value = self.singleLineStringParser()
                if value.upper() == 'TRUE':
                    self.curStruct[varName] = True
                elif value.upper() == 'FALSE':
                    self.curStruct[varName] = False
                else:
                    msg = 'while iterating through the DNET file came accross ' + \
                          'this line: (' + str(line) + '). The regular expressions ' + \
                          'detected it as a boolean value, however it does not ' + \
                          'contain a true, or false value.'
                    raise TypeError, msg
            elif self.re_singleLineNumericProperty(line):
                varName, value = self.singleLineStringParser()
                if '.' in value:
                    self.curStruct[varName] = float(value)
                else:
                    self.curStruct[varName] = int(value)
            elif self.re_singleLineListNumbers.match(line):
                varName, value = self.singleLineListParser()
                self.curStruct[varName] = value
            elif self.re_singleLineListProperties.match(line):
                # down the road may want to look into putting a 
                # special flag as these properties reference other
                # nodes.  Maybe maintain a parent list or something, 
                # maybe not, we'll see once we start working with it
                varName, value = self.singleLineListParser()
                self.curStruct[varName] = value
            elif self.re_startMultiLineDataStruct.match(line):
                # once the startline is detected need to:
                #  a) get the rest of the data into memory
                #  b) get the 
                # rest of
                
                
                pass
            # next is the multiline multidimension data structure!
            # step1 detect start of a multiline / tabular data struct!
            #       these tend to start with 'var = ' followed by 
            #       nothing!
            
            
                
            

            
            # list of lists, exeample:
            # path = ((111, 51), (168, 18), (42,....
            # end of a struct
            
    def readRestOfMultiLineStruct(self, line):
        '''
        multiline data structures look like this:
        
            probs = 
        // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    
        (((1,           0,           0,           0),             // NoTest       Peach 
          (1,           0,           0,           0)),            // NoTest       Lemon 
         ((0,           0.9,         0.1,         0),             // Steering     Peach 
          (0,           0.4,         0.6,         0)),            // Steering     Lemon 
         ((0,           0.8,         0.2,         0),             // Fuel_Elect   Peach 
          (0,           0.1333333,   0.5333334,   0.3333333)),    // Fuel_Elect   Lemon 
         ((0,           0.9,         0.1,         0),             // Transmission Peach 
          (0,           0.4,         0.6,         0)));           // Transmission Lemon ;


        The structure is:
            probs = (This is the name of the variable or the declaration of the property)
            // NoResult NoDefects ... // NODE  NODE (describes the order of the states 
            // ((( 1,0,0,0), // NoTest  Peach (Describes the probability for NoTest Peach combination
                 ( 1,0,0,0)), // NoTest Lemon (Describes the probaility for NoTest Lemon combination
                                 the 1 indicates that the result of this combination will always 
                                 result in a NoResult state.  Lower down (3rd row) the .9 indicates
                                 a 90% probability for NoDefects when T1= Steering and CC = Peach
                                 and 10% probability for OneDefect when T1=Steering and CC = Peach
                 
        
        '''
            
    def singleLineListParser(self, line):
        '''
        recieves a line for the dnet file that contains a 
        list of values. The input line will look similar to
        one of the following:
        
        parents = (T1, R1)
        states = (NoTest, Differential)
        center = (306, 60)
        
        This method will return the variable 
        name as the first arg and a python list as the second.
        If the list is made up of numbers the method will 
        handle the type conversions (string to int), and will
        return a list of numbers.
        
        If the list is made up of a list of property names
        then it will return just that, a list of properties 
        as strings.
        '''
        varName = line.split('=')[0].strip()
        value = line.split('=')[1].strip()
        if value[0] == '(':
            value = value[1:]
        if value[len(value) - 1] == ')':
            value = value[0:len(value) - 1]
        valList = value.split(',')
        cnt = 0
        for val in valList:
            val = val.strip()
            # is the val a number?
            if val.isdigit():
                val = int(val)
            elif val.replace('.', '').isdigit():
                val = float(val)
            valList[cnt] = val
            cnt += 1
        # TODO: need to write a test for this method
        # var = (1,2,3) should return [1,2,3]
        # var = (once, twice) should return ['once', 'twice')
        # var = (1.1, 23.23423) should return [1.1, 23.23423]
        # test should verify the type conversion as well as the 
        # conversion to the list.
        return varName, valList
        
            
    def singleLineStringParser(self, line):
        '''
        receives a line from a dnet file that contains a single 
        line string value.  Returns the name of the property that 
        is being set and the associated value.  The value will have 
        any carriage returns removed as well as the line termination
        character ';' leading and trailing spaces and the quotes
        that surround the value,
        '''
        varName = line.split('=')[0].strip()
        value = line.split('=')[1].strip()
        # remove the semi colon
        if value[len(value) - 1] == ';':
            value = value[0:len(value) - 1]
        # remove leading and ending " characters
        value = value.strip('"')
        return varName, value
                
    def getRestOfMultiLineComments(self):
        values = []  # list that will be returned!
        breakLoop = False
        while True:
            line = self.fh.readline()
            # only want to remove the carriage return at the end of the line
            if line[len(line) - 1] == '\n':
                print 'removing carriage return'
                line = line[0:len(line) - 1]
            print 'line:', line
            if not line:
                break
            if self.re_multiLineStringEnd.match(line):
                breakLoop = True
            line = line.rstrip(r'\\', ).strip()
            values.append(line)
            if breakLoop:
                break
        return ' '.join(values)
        
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
    
    