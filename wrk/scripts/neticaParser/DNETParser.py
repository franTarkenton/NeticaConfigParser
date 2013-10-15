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

import datetime
import getpass
import inspect
import logging
import os.path
import re
import sys
import warnings

import numpy

from neticaParser import NeticaData

class DNETStructParser():
    '''
    This class contains the methods necessary to parse out the 
    start and stop points of netica's nested data structures.
    
    Only deals with puttign together the data structures that describe
    the start and end points.  Actual parsing of the data is handled
    by a different class.
    
    
    :ivar defaultLine: Hmm, can't remember what the hell this is!  Likely
                       its fluff.
    :ivar dnetFile: String variable that contains the path to the dnet
                    file that is being parsed.
    :ivar endChar: This is the character that is used by the parser to 
                   describe the end of a structure. (used in parsing multi
                   line objects)
    :ivar fh: The filehandle that points to the dnetFile
    :ivar lineCnt: A counter that keeps track fo the current line
    :ivar startChar: The character that is used to describe the start of a
                     data structure. (used to parse multiline objects)
    :ivar struct:  __restruct will populate this parameter with 
                             an element object.  The element object describes
                             the start and end points of the various objects
                             described in the dnet file.  Element objects
                             are hierarchical.  In that all elements are
                             parents of a root element.  The root element
                             will contain the network.  children of that 
                             element will contain the nodes, etc.
    '''
    lineCnt = 1
    defaultLine = [None, None, None, None, []]
    struct = None
    
    startChar = '{'
    endChar = '}'
    
    logFile = ''
    logObj = None
    
    def __init__(self, dnetFile):
        self.dnetFile = dnetFile
        self.__initLog()
    
    def parseStartEndPoints(self):
        '''
        Opens the netica dnet file that was specified by the the 
        constructor.  Reps through it populating the property struct
        with information about the start and end points of nodes that
        are described in the dnet file.
        
        The struct propert
        '''
        self.logObj.debug("opening the dnet file")
        self.fh = open(self.dnetFile, 'r')
        self.__parseStructs(self.struct, None)
        #print 'self.struct', self.struct
        self.fh.close()
        
    def __initLog(self):
        '''
        This method will inialize a log file.  If the T:\ drive exists
        then it will automatically put the log file there.  If it does not 
        exist then it will put it in the directory that the TEMP var is 
        pointing to.
        '''
        # Calculating the log file name
        defaultLocation = 'T:\\'
        s = inspect.stack()
        module_name = inspect.getmodulename(s[1][1])
        user = getpass.getuser()
        timeString = datetime.datetime.now().strftime("%a%b%d%H%M%S")
        logFile = module_name + '_' + user + '_' + timeString + '.log'
        if os.path.exists(defaultLocation):
            self.logFile = os.path.join(defaultLocation, logFile)
        else:
            self.logFile = os.path.join(os.environ['TEMP'], logFile)
        # create the log object
        self.logObj = logging.getLogger()
        # create a handler
        hndlr = logging.FileHandler(self.logFile)
        # creating a formatter and applying formatting to the formatter 
        formatString = '%(asctime)s %(name)s.%(funcName)s.%(lineno)d %(levelname)s: %(message)s'
        formatr = logging.Formatter( formatString )
        formatr.datefmt = '%m-%d-%Y %H:%M:%S' # set up the date format for log messages
        # apply to formatter to the handler
        hndlr.setFormatter(formatr)
        # Step 5 - tell the log object to use the handler
        self.logObj.addHandler(hndlr)
        # Step 6 - set the log level
        self.logObj.setLevel(logging.DEBUG)
        # Step 7 - create a logging object that this module will use to write its log messages to
        #             the name of the log object will be moduleName.className
        logName = module_name + '.' + self.__class__.__name__
        #print 'logName', logName
        self.logObj = logging.getLogger( logName )
        
        # Step 8 on, write some log messages
        self.logObj.debug('this is my first log message!')
        
    def __parseStructs(self, curStruct, prevStruct):
        # initial scan which records where the startChar and 
        # endChar's are found.
        self.logObj.debug("parsing the file for start and end points.")
        startEnd = []
        lineNum = 0
        for line in self.fh:
            charNum = 0
            for char in line:
                if char == self.startChar:
                    startEnd.append(['START', lineNum, charNum])
                    self.logObj.debug("start line:" + str(lineNum) + ' start char:' + str(charNum))
                elif char == self.endChar:
                    startEnd.append(['END', lineNum, charNum])
                    self.logObj.debug("end line:" + str(lineNum) + ' start char:' + str(charNum))
                charNum += 1
            lineNum += 1
        self.struct = self.__restruct(startEnd)
                    
    def __restruct(self, elemList):
        '''
        This method works in conjunction with the __parseStructs
        method.  __parseStructs will identify the line and character
        postions of data structures contains in the dnet file.  This
        method then uses that information and restructures it into 
        a hierarchical data structure.
        
        What gets returned in an element object.  That element object
        describes the bayes network.  Within that object are the nodes
        that make up the network.
        
        :param  elemList: a python 2d list, each inner item is made up
                          of three entries:
                           1. 'START' | 'END' either of these strings
                              used to describe wether the entry describes
                              the start or end of a structure.
                           2. linenumber
                           3. character position on that line
        :type elemList: python 2d list
        
        :returns: Element Object that contains the start end end positions
                  of various objects that make up the Bayes Network.
        :rtype: Element Object
        '''
        self.logObj.debug("started the __restruct method")
        curElemCnt = 0
        startElemObj = element()
        curElemObj = startElemObj
        
        while curElemCnt < len(elemList):
        
            curElem = elemList[curElemCnt]
            
            if curElemCnt < len(elemList) - 1:
                # if the next element is an ending and the current one is 
                # a starter
                nextElem = elemList[curElemCnt + 1]
                if nextElem[0] == 'END' and curElem[0] == 'START':
                    startLine = elemList[curElemCnt][1]
                    startCol = elemList[curElemCnt][2]
                    endLine = elemList[curElemCnt + 1][1]
                    endCol = elemList[curElemCnt + 1][2]
                    self.logObj.debug("startLine:" + str(startLine))
                    self.logObj.debug("startCol:" + str(startCol))
                    self.logObj.debug("endLine:" + str(endLine))
                    self.logObj.debug("endCol:" + str(endCol))
                    curElemObj.setStartAndEnd(startLine, startCol, endLine, endCol)
                    #curElemObj.printProperties()
                    parentObj = curElemObj.getParent()
                    # now add another child to the parent and set the 
                    # curElemObj to that child
                    curElemObj = parentObj.addChild()
                    #curElemObj = parentObj
                    curElemCnt += 2
                    continue
            if elemList[curElemCnt][0] == 'START':
                # when we find a start, populat the current element
                # then request a new child and set the child to be the
                # curElem
                curElemObj.setStart(elemList[curElemCnt][1], elemList[curElemCnt][2])
                childObj = curElemObj.addChild()
                curElemObj = childObj
            elif elemList[curElemCnt][0] == 'END':
                parentObj = curElemObj.getParent()
                parentObj.setEnd(elemList[curElemCnt][1], elemList[curElemCnt][2])
                #parentObj.printProperties()
                #curElemObj = parentObj
                parentObj = parentObj.getParent()
                if parentObj:
                    childObj = parentObj.addChild()
                    curElemObj = childObj
                else:
                    # if parent retrns none means the current object does not have a parent
                    # which means we are at the end of the data structure
                    childObj = None
                    curElemObj = childObj
            curElemCnt += 1
            
        #print '------------------------888------------------------------'
        #startElemObj.printData(startElemObj)
        return startElemObj
     
    def getNodeStartendLines(self):
        '''
        Checks to see if the self.struct property has been populated, if it 
        has not then methods are run to populate it.  Then returns the contents 
        of that property.  struct will contain an element object that describes
        start and end points of objects that make up the bayes network.        
        
        :returns: An element object that describes where in the dnet file 
                  various aspects are located that make up the bayes network
        :rtype: Element object
        '''
        # returns an element object.  Element objects are a hierarchical 
        # data structure that describes the start and end points of nodes
        # or verticies within the dnet file
        if not self.struct:
            self.parseStartEndPoints()
        return self.struct
    
    def populateBayesParams(self):
        '''
        Checks to see if the struct property has been populated. If it 
        has not been, then calls the various methods that will do that.
        
        Then it calls methods necessary to extract information out of the
        dnet file that describes the bayesnetwork.  Returns an instance of 
        the ParseBayesNet class.
        
        :returns: a ParseBayesNet object that contains the parsed information 
                  from the dnet file.
        :rtype: ParseBayesNet object
        '''        
        if not self.struct:
            self.parseStartEndPoints()
        bayesParseObj = ParseBayesNet(self.struct, self.dnetFile)
        bayesParseObj.parse()
        return bayesParseObj

class ParseBayesNet():
    '''
    This class will extract the information contained in the dnet file
    and place it into a BayesData object.  The BayesData object is 
    designed to make it easy to extract the information for use with 
    other bayesian libraries.  This class contains the methods used 
    to extract that information, while the BayesData module contains
    the classes used to store and then subsequently access that 
    information from.
    
    :ivar bayesDataObj: a netica network object.
    :ivar dnetFile: A string that describes the source dnet file
    :ivar dnetFileMem: The dnet file that has been read into memory.
                       this is the reference to that in memory data
                       structure.
    :ivar struct: This is the element object that was calculated by 
                  the DNETStructParser class.
    '''
    
    logger = None
    
    # This is the parser which will populate a BayesData object below
    def __init__(self, struct, dnetFile):
        self.__initLogging()
        self.struct = struct
        self.dnetFile = dnetFile
        
        # other class variable declarations
        self.dnetFileMem = None
        self.bayesDataObj = NeticaData.neticaNet()
    
    def __initLogging(self):
        # This code is here just cause I like to have my log messages contain
        # Module.Class.Function for each message.  If you don't care too much about what 
        # you log messages look like in the log file, you can bypass this.
        curFile = inspect.getfile(inspect.currentframe())  
        if curFile == '<string>':
            curFile = sys.argv[0]
        logName = os.path.splitext(os.path.basename(curFile))[0] + '.' + self.__class__.__name__
        # and this line creates a log message
        self.logger = logging.getLogger(logName)
    
    def getBayesDataObj(self):
        '''
        returns the netica data object that this 
        method is going to create and populate with the 
        contents from a file.
        
        :returns: Returns the a NeticaData.neticaNet object, or in 
                  english a reference to a NeticaData, Netica network 
                  object that contains all the information parsed from 
                  the netica dnet file, with a nice easy to use api 
                  wrapped around it.
        :rtype: NeticaData.neticaNet object
        '''
        return self.bayesDataObj
        
    def parse(self):
        '''
        This method rips through the dnet file, extracting information from it and
        putting it into the NeticaData.neticaNet object.  Once this is complete it 
        becomes much easier to access that information
        '''
        #print '-------------------- Populating Bayes Params --------------------'
        self.logger.debug("starting the parse of the dnet file...")
        # assume the first element in the structure is the bayes network values.
        self.__readFileIntoMemory()
        firstLine = True
        curLine = 0
        skip = False
        skipEndLine = 0
        for elem in self.struct:
            curLine = elem.getStartLine()
            #elem.printProperties('     ')
            if firstLine:
                self.__parseFirstLine(elem)
                firstLine = False
            else:
                if skip:
                    if curLine >= skipEndLine:
                        skip = False
                        skipEndLine = 0
                    else:
                        continue
                # element type is the type of object that is being 
                # described.  Could be NODE, or VISUAL or BNET
                elemType = self.__getElemType(elem)
                if elemType.upper() == 'VISUAL':
                    # skip visual elements
                    skip = True
                    skipEndLine = elem.getEndLine()
                    #elem.printProperties()
                elif elemType.upper() == 'NODE':
                    self.__parseNode(elem)
                else:
                    #elem.printProperties()
                    startLineNum = elem.getStartLine()
                    startLine = self.__getLine(startLineNum)
                    message = 'The following is the declaration line of a data structure '  + \
                              '(' + str(startLine) + '...) it contains a type that the parser ' + \
                              'is going to ignore!  It occurs on line: ' + str(startLineNum)
                    warnings.warn(message)
                    
    def __parseNode(self, elem):
        '''
        Recieves and element object that describes a node.
        This method will create a node in the bayesDataObject
        along with all the various attributes.
        '''
        startLine = elem.getStartLine()
        curLineNum = startLine
        endLine = elem.getEndLine()
        elemName = self.__getElemName(elem)
        nodeObj = self.bayesDataObj.newNode(elemName)
        # now increment the line:
        curLineNum += 1
        #print 'endLine:', endLine
        self.logger.debug("endline: " + str(endLine))
        while curLineNum <= endLine:
            curLineNum = self.__parseAttributeLine(curLineNum, nodeObj, endLine)
            self.logger.debug("curLineNum:" + str(curLineNum))
            #print 'curLineNum is:', curLineNum
                    
        #print startLine, ' of node'
        self.logger.debug("startLine: " + str(startLine))
        
    def __parseAttributeLine(self, lineNum, nodeObj, endOfNodeLine ):
        '''
        Recieve an integer that corresponds with the line number
        that is being read.  The script will read that line, and 
        dump the data in that line into a NeticaData NodeObject 
        attribute.  The method will then return the next line to 
        read.  
        
        This method will also check to see if a line number corresponds
        with the start of a defined structure. (ie an element that 
        is enclosed by parethases.)  If it finds a defined structure
        it will skip by it, assuming that it is not relevant, as most
        encloing data structures in the dnet file contain visual 
        information that is not applicable to the bayes model. 
        
        '''
        line = self.__getLine(lineNum)
        line = line.strip()
        # is it a single line assignement, ie does it 
        # look like 
        # atttribute = value
        if line[len(line) - 1] == ';':
            # single line attribute assignment, pulls the attribute, 
            # parses it, and enters into the node object
            line = line[:len(line) - 1]
            lineList = re.split('\s+=\s+', line)
            nodeObj.enterAndValidateSimpleAttribute(lineList[0], lineList[1])
            lineNum += 1
        # its a multiline value, ie its a prob or a functable
        else:
            # multiline statements need to be handled differently from 
            # single line statements.  This is the logic for mulitline 
            # statements, like:
            #  a) embedded nodes
            #  b) probability tables
            #  c) function tables
            #            
            # need to check that this is not part of an 
            # element already
            multiLine = ''
            while True:
                # __getElemEnd is going to return null, if the current
                # lineNum is not part of a struct (ie a data structure
                # that is enclosed with '{' and '}'.  If the current 
                # line is the start of a struct it will return the line
                # that corresponds with the end of that struct.
                if lineNum == endOfNodeLine:
                    lineNum += 1
                    break
                endLine = self.__getElemEnd(lineNum)
                if endLine:
                    # in other words if the current line points to a struct
                    # skip over it...
                    #print 'lines: ', lineNum, 'to', endLine, 'are part of a struct'
                    lineNum = endLine + 1
                    continue
                # retrieve the line for the current lineNum
                line = self.__getLine(lineNum)
                line = line.strip() # strip off concluding lines.
                #print 'line:', line
                self.logger.debug("line: " + str(line))
                if multiLine:
                    multiLine = multiLine + '\n ' + line
                else:
                    multiLine = line
                if line[len(line) - 1] == ';':
                    #print 'MULTILINE:', multiLine
                    #print 'lineNum', lineNum
                    self.logger.debug("MULTILINE: " + str(multiLine))
                    lineNum += 1
                    self.__parseAndEnterMultiLineString(multiLine, nodeObj);
                    break
                lineNum += 1
        return lineNum
    
    def __parseAndEnterMultiLineString(self, multiLine, nodeObj):
        '''
        This method receives a string that is made up of multiple lines.
        It will parse it into either a list or a dictionary.  If the 
        multiline string starts by declaring the column headers then it 
        will convert it into a dictionary.  
        
        If it only contains a list of values then it will convert it into
        a list.
        
        structure should look something like this:
        var = // col1     col2   (
        
        '''
        #print 'multiLine:'
        #print multiLine
        self.logger.debug("multiLine: " + str(multiLine))
        atribType = self.__getAtribType(multiLine)
        
        # first parse the comments that are embedded in the multiline
        # statement.  Multilines are expected to have comments embedded
        # in them that describe what the values are inside the string
        # comments are prefaced with the characters //
        commentPositionList = self.__getPositions(multiLine, 'comment')
        # There are not any comments in this line,  throw error.
#         if not commentPositionList:
#             # did not write the parser to deal with this situation
#             msg = 'The multiline parameter is as follows:\n' + \
#                   multiLine + '\n\n This multiline statemment does' + \
#                   'not have any comment characters, ie \'//\' charcters ' + \
#                   'and this method is expecting it to.  FYI there is a ' + \
#                   'unittest that was created to help with the development ' +\
#                   'of this method.  It will likely be useful in adding this ' + \
#                   'additional behaviour.  Its in the module DNETParser_test ' +\
#                   'and the test is called : ' + \
#                   'test__ParseBayesNet__parseAndEnterMultiLineString' 
#             raise ValueError, msg
        
        # second determine what atribType of attribute this multi line is.
        # if its a prob then send to the prob parser.  
        # if its a functable then send to the functable parser.
        # Otherwise throw an error as these are the only two types
        # of attributes that I have currently come accross.  The comment 
        # positions are also passed to these methods as they help
        # with the parsing.
        if atribType == 'probs':
            # if its a probability, there are two types.  Root nodes who's probabilities only describe the starting probabilities fo the nodes state, and junction nodes that define the state depending on the state of parents.
            if len(commentPositionList) == 1:
                neticaProbabilityTable = self.__parseSingleListMultiLineProbAttribute(multiLine)
            else:
                neticaProbabilityTable = self.__parseProbMultiLineAttribute(multiLine, commentPositionList)
            # TODO: the neticaProbabilityTable now needs to be attached to the nodeObject
            nodeObj.setProbabilityTable(neticaProbabilityTable)
        elif atribType == 'functable':
            neticafuncTableObj = self.__parseFuncTableMultiLineAttribute(multiLine)
            nodeObj.setFunctionTableObject(neticafuncTableObj)
        elif atribType == 'comment':
            # don't need comments so skip over
            self.logger.warn("found a comment string, ignoring it")
            pass
        else:
            msg = 'Found a multiline attribute with the atribType:(' + str(atribType) + \
                  ') This parser does not recognize that atribType.  Throwing an ' + \
                  'error here so you are aware that this atribType has been found.' + \
                  'could probably safely comment out the error, or catch it and ' + \
                  'proceed!'
            raise ValueError, msg
            
    def __parseFuncTableMultiLineAttribute(self, multiLine):
        '''
        recieves a multiline string that contains a function table.
        parses the function table, creates a function table object
        enters the information correctly into the function table object
        and returns the function table object
        '''
        parents = self.__getParentValuesFromTable(multiLine, 1)
        #print 'parents:'
        self.logger.debug("parents : " + str(parents))
        retVal = self.__parseMultilineValues(multiLine)
        #columnList, ParentColumnList = self.__getAttributeHeaders(multiLine)
        atribLoL = self.__getAttributeHeaders(multiLine)
        neticaFuncTable = NeticaData.FuncTable(atribLoL[1], retVal, parents)
        self.logger.debug("netica func table: " + str(neticaFuncTable))
        #print neticaFuncTable
            
    def __parseProbMultiLineAttribute(self, multiLine, commentPositionList):
        '''
        Recieves a multiline attribute value containing a probability
        table.  This method will parse the probability table into a data
        structure.
        '''
        if len(commentPositionList) == 1:
            neticaProbabilityTable = self.__parseSingleListMultiLineProbAttribute(multiLine)
        else:
            probTable = self.__parseMultilineValues(multiLine)
            neticaProbabilityTable = self.__getNeticaProbabilityObject(probTable, multiLine)
        return neticaProbabilityTable
    
    def __getNeticaProbabilityObject(self, probTable, multiLine):
        # get the comment  lists first!
        columnList, ParentColumnList = self.__getAttributeHeaders(multiLine)
        neticaProbsTable = NeticaData.ProbsValueTable(columnList, ParentColumnList)
        # now need to get extract the parent values that line up with the 
        # propability table
        parentValues = self.__getParentValuesFromProbsTable(multiLine)
        # now enter these values into a probability table
        neticaProbsTable.setValues(probTable, parentValues)
        self.logger.debug("probTable: " + str(probTable))
        self.logger.debug("parentValues: " + str(parentValues))
        return neticaProbsTable
        
    def __getParentValuesFromTable(self, multiLine, numberOfHeaderComments=2):
        '''
        used to parse out the parent values that go into either a probability
        table or a function table.
        
        For probability tables set the numberOfHeaderComments to 2.  This number
        is used to identify that there are two sets of comments before the 
        comments that represent the parent values.  The second set of comments
        is used to determine the width of the columns.
        
        For function tables use numberOfHeaderComments = 1.  This number
        represents the fact that there is only one comment demarkation.  it 
        identifies the column names and their widths for subsequent parent 
        values.
        '''
        # getting the positions in the multiline string for the start
        # of each comment.  (comments prefaced by //)
        commentPositions = self.__getPositions(multiLine, 'comment')
        
        valueList = []
        
        # get the position of the second set of comments - this is the header
        # for the current 
        startPosition = commentPositions[numberOfHeaderComments - 1]
        # now get the end position
        matchObj = re.match('//.*', multiLine[startPosition:] )
        endPos = matchObj.end() + startPosition
        justFirstColumns = multiLine[startPosition:endPos]
        #print 'headers:', multiLine[startPosition:endPos]
        self.logger.debug("Headers: " + str(multiLine[startPosition:endPos]))
        # now need to find the number of spaces over for each additional 
        # comment.  The first will always be 0.
        findIterObj = re.finditer('\S+\s*', justFirstColumns)
        columnPositions = []
        for mtch in findIterObj:
            columnPositions.append( mtch.start() )
        #print 'columnPositions', columnPositions
        self.logger.debug("columnPositions: " + str(columnPositions))
        # now remove the first value as it only identifies the start of the 
        # comment followed by the white space.  ie // followed by a space that 
        # preceds the first comment.
        columnPositions.pop(0)
        #print 'columnPositions', columnPositions
        self.logger.debug("columnPositions: " + str(columnPositions))
        parentValuePositions = commentPositions[numberOfHeaderComments:]
        #print len(multiLine)
        self.logger.debug("length of multiline ( len(multiLine) ): " + str(len(multiLine)))
        for position in parentValuePositions:
            #print 'position', position
            # set the initial line end position
            self.logger.debug("position: " + str(position))
            lineEndPos = len(multiLine)
            # create an iterator that finds the newline positions in front 
            # of the current comment string
            iterObj = re.finditer('\n',multiLine[position:] )
            # find out how many values are in the iterator
            iterCnt = sum(1 for _ in iterObj)
            # because iterators cannot be reset the only way to 
            # set the iterator back to 0 is to recreate so...
            iterObj = re.finditer('\n',multiLine[position:] )
            #print 'iterCnt', iterCnt
            self.logger.debug("iterCnt: " + str(iterCnt))
            if iterCnt:
                firstReObj = iterObj.next()
                lineEndPos = firstReObj.start() + position
            #print 'lineEndPos', lineEndPos
            self.logger.debug("lineEndPos: " + str(lineEndPos))
            #print 'comment is', multiLine[position:lineEndPos]
            self.logger.debug("comment is:" + str(multiLine[position:lineEndPos]))
            comment = multiLine[position:lineEndPos]
            #print 'comment', comment
            self.logger.debug("comment: " + str(comment))
            innerList = []
            cnt = 0
            while cnt < len(columnPositions):
                if cnt + 1 >= len(columnPositions):
                    valueToAdd = comment[columnPositions[cnt]:]
                else:
                    valueToAdd = comment[columnPositions[cnt]:columnPositions[cnt + 1]]
                valueToAdd = valueToAdd.replace("//", '').replace(";", '').strip()
                #print valueToAdd
                self.logger.debug("valueToAdd: " + str(valueToAdd))
                innerList.append(valueToAdd)
                cnt += 1
            #for colPos in columnPositions:
                
            
            # at this point comment var contains only a comment part
            # of the what ever comment is being processed.  Next step 
            # is to remove the // characters and trailing spaces, and 
            # parse the string into a list.  Stuff that list into another
            # list
            #comment = comment.replace("//", '').replace(";", '').strip()
            #commentList = re.split('\s{2,}', comment)
            #print 'commentList', commentList
            #valueList.append(commentList)
            valueList.append(innerList)
        #print valueList
        self.logger.debug("valueList:" + str(valueList))
        return valueList
    
    def __getParentValuesFromProbsTable(self, multiLine):
        '''
        This method takes a multiline string and returns a 
        list of lists containing the parent values that 
        correspond with the various likelyhood distribution
        that are described in the table.
        
        In a nutshell it will take this:
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
        
        and turn it into this:
          [['NoTest', 'Peach'],
           ['NoTest', 'Lemon'],
           ['Steering', 'Peach'], 
           ['Steering', 'Lemon'], 
           ['Fuel_Elect', 'Peach'], 
           ['Fuel_Elect', 'Lemon'], 
           ['Transmission', 'Peach'], 
           ['Transmission', 'Lemon']]

        
        '''
        valueList = self.__getParentValuesFromTable(multiLine, 2)
        return valueList
    
    def __getAttributeHeaders(self, multiLine):
        '''
        data structs in the dnet file can take on the following 
        organizations:
        
        probs = 
        //   NoResult     NoDefects    OneDefect         // T1           R1         T2           CC    
        (((((1,           0,           0),               // NoTest       NoResult   NoTest       Peach 
            (1,           0,           0)),              // NoTest       NoResult   NoTest       Lemon 
            ...
        or 
            probs = 
        // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    
        (((1,           0,           0,           0),             // NoTest       Peach 
          (1,           0,           0,           0)),            // NoTest       Lemon
          ...
        
        or  

            functable = 
                            // T1           T2           B             CC    
        ((((0,               // NoTest       NoTest       DontBuy       Peach 
            0),              // NoTest       NoTest       DontBuy       Lemon 
           (60,              // NoTest       NoTest       Buy           Peach 
            ...
            
        
        This method will parse the first line, and return:
        (in order of the examples)
        
        ['NoResult', 'NoDefects', 'OneDefect'], ['T1', 'R1', 'T2', 'CC']
        '''
        #print '\nmultiLine', multiLine
        self.logger.debug("multiLine: " + str(multiLine))
        firstList = []
        commentPositions = self.__getPositions(multiLine, 'comment')
        newLine = self.__getPositions(multiLine[commentPositions[0]:], 'new_line')
        #print 'newLine', newLine
        self.logger.debug("newLine:" + str(newLine))
        # determine if the first line of comments contains two 
        # dimensions of comments, ie, 
        # // var var var //var var
        # as opposed to 
        # // var var var
        if ( len(commentPositions) > 1 ) and \
            commentPositions[0] < newLine[0] and \
            commentPositions[1] < newLine[0]:
            # Extracting and converting the first set of comments into
            # lists.
            firstString = multiLine[commentPositions[0]:commentPositions[1]]
            firstString = firstString.replace('//','').replace('\n','').strip()
            firstList = re.split('\s+', firstString)
            #print 'firstList', firstList
            self.logger.debug("firstList:" + str(firstList))
            
            # Extracting and converting the second set of comments
            secString = multiLine[commentPositions[1]:newLine[0] + commentPositions[0]]
            secString = secString.replace('//','').replace('\n','').strip()
            secList = re.split('\s+', secString)
            self.logger.debug("secList: " + str(secList))
            #print 'secList', secList
        else:
            secString = multiLine[commentPositions[0]: newLine[0] + commentPositions[0]]
            secString = secString.replace('//','').replace('\n','').strip()
            secList = re.split('\s+', secString)
            #print 'secList', secList
            self.logger.debug("secList: " + str(secList))
        return firstList, secList
    
    def __parseMultilineValues(self, multiLine):
        '''
        This method is designed to parse a multiline probability / junction table.
        The table is expected to link input values against output states with 
        probabilities.  Examples of what the strings that need to be parsed might 
        look like:
        
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

        In the example above the line: 
        // NoResult     NoDefects    OneDefect    TwoDefects, identifies the column headers
        or the possible output states. The values under each of these columns idenfies the 
        likelyhood of a particular state given the inputs.
        
        so the second set of comments on the first line is // T1           CC   
        T1 and CC are the columns descriging the parent or source values  
        values under each of these columns describe the combinations of 
        possible values from these parents.
        
        This method parses this into a probability table 
        
        '''
        atribType = self.__getAtribType(multiLine)
        #print 'atribType', atribType
        self.logger.debug("atribType:" + str(atribType))
        equalPosList = self.__getPositions(multiLine, 'equal')
        atribList1, atribList2 = self.__getAttributeHeaders(multiLine)
        #print 'atribList1', atribList1
        self.logger.debug("atribList1: " + str(atribList1))
        #print 'atribList2', atribList2
        self.logger.debug("atribList2: " + str(atribList2))
        # These lines are extracting the actual data from the
        # multiline attribute.
        dataStructString = ''
        arrayType = 'float'
        for oneLine in multiLine.split('\n'):
            probabilityValues = oneLine
            equalPosList = self.__getPositions(oneLine, 'equal')
            if equalPosList:
                probabilityValues = probabilityValues[equalPosList[0] + 1:]
            commentPosList = self.__getPositions(probabilityValues, 'comment')
            if commentPosList:
                probabilityValues = probabilityValues[:commentPosList[0]]
            probabilityValues = probabilityValues.strip()
            #if not self.__is_number(probabilityValues):
            probabilityValues, arrayType = self.__getJustValue(probabilityValues, arrayType)
                
            #print 'probabilityValues', probabilityValues
            self.logger.debug("probabilityValues: " + str(probabilityValues))
            if probabilityValues:
                dataStructString = dataStructString + ' ' + probabilityValues
        
        if dataStructString[len(dataStructString)-1] == ';':
            dataStructString = dataStructString[:len(dataStructString)-1]
#         print dataStructString
        self.logger.debug("dataStructString: " + str(dataStructString))
        rawvar = eval(dataStructString)
        if arrayType == 'float':
            var = numpy.array(rawvar, numpy.double)
        else:
            var = numpy.array(rawvar)
        dim = var.shape
        if len(dim) > 2:
            # Needs to be reshaped down to a two dimensional structure
            newShapeParam = 1
            cnter = 0
            #print 'dim', dim
            self.logger.debug("dim: " + str(dim))
            while cnter < len(dim) - 1:
                newShapeParam = newShapeParam * dim[cnter]
                
                cnter += 1
            self.logger.debug("newShapeParam: " + str(newShapeParam))
            self.logger.debug("len(atribList1): " + str(len(atribList1)))
            self.logger.debug("len(atribList2): " + str(len(atribList2)))

            #print 'newShapeParam', newShapeParam
            #print 'len(atribList1)', len(atribList1)
            #print 'len(atribList2)', len(atribList2)
            if atribType == 'functable':
                var = var.reshape(newShapeParam, dim[len(dim) - 1])
            else:
                var = var.reshape(newShapeParam, len(atribList1))
        var = var.tolist()
        self.logger.debug("var: " + str(var))
        #print 'var is:'
        #print var
        return var
    
    def __getJustValue(self, value, atribType):
        '''
        Recieves a value, removes the characters '(', ')', ',', ';' and 
        then tests to see if its a number.  If its not a valid number then
        it will wrap the value in quotes and return it.
        
        '''
        self.logger.debug("input: " + str(value) + ' atribType: ' + str(atribType))
        tmpVal = value[0:]
        tmpVal = tmpVal.replace('\n', '').replace('(', '').replace(')', '').replace(',','').replace(';', '')
        if not self.__is_number(tmpVal) and tmpVal:
            newVal = "'" + tmpVal + "'"
            value = value.replace(tmpVal, newVal)
            atribType = 'str'
        self.logger.debug("output: " + str(value) + ' atribType: ' + str(atribType))
        return value, atribType
    
    def __is_number(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def __parseSingleListMultiLineProbAttribute(self, multiLine):
        '''
        This method will take a data structure described in a string
        like this:
        
        probs = 
                 // Peach        Lemon
                 (0.8,         0.2);
                 
        and converts it into this:
        
        {'Lemon': 0.2, 'Peach': 0.8}
        '''
        
        #TODO: 10-3-2013 current this method parses up this data structure into a dictionary.  We need to get that entered as a NeticaProabilityTable.  in the module NeticaData
        commentPositionList = self.__getPositions(multiLine, 'comment')

        #print 'commentPos', commentPositionList
        self.logger.debug("commentPositionList: " + str(commentPositionList))
        leftPosList = self.__getPositions(multiLine, 'left_paren')
        rightPosList = self.__getPositions(multiLine, 'right_paren')
        #print 'left', leftPosList
        self.logger.debug("left: " + str(leftPosList))
        columnString = multiLine[commentPositionList[0]:leftPosList[0]]
        columnString = columnString.replace('//', '').strip()
        columnList = re.split('\s+', columnString)
        
        dataString = multiLine[leftPosList[0] + 1:rightPosList[0]].strip()
        dataList = re.split('\s*,\s*', dataString)
                    
        if all(self.__isNum(v) for v in dataList):
            dataList = [ float(x) for x in dataList ]
        #TODO: should verify that there is only one value and raise an error if not
#         returnDict = dict(zip(columnList, dataList))
        
        neticaProbabilityTable = NeticaData.ProbsValueTable(columnList)
        neticaProbabilityTable.setRootValues(dataList)
        return neticaProbabilityTable
    
    def __isNum(self, numString):
        try:
            float(numString)
            return True
        except ValueError:
            return False
        
    def __getPositions(self, inString, stringType):
        '''
        stringType needs to be equal to either 
        equal or comment.  
        
        will return a list of where these parameters
        have been found in the inString.  If none are 
        found then will return an empty list.
        '''
        retList = []
        regexDict = {'equal':'=',
                     'comment':'//', 
                     'left_paren': '\(',
                     'right_paren': '\)', 
                     'new_line': '\n'}
        stringType = stringType.lower()
        if stringType not in regexDict.keys():
            msg = 'This methods second argument must be either: ' + \
                  '(' +  ','.join(regexDict.keys()) + ') you provided ' + \
                  'the value: ' + str(stringType)
            raise ValueError, msg
        
        for matchObj in re.finditer(regexDict[stringType], inString):
            retList.append(matchObj.start())
        return retList
    
    def __getElemEnd(self, lineNum):
        '''
        iterates through all the elements.  If it finds 
        an element that starts with the line number 
        supplied as an arguement it will return the 
        endline of that element.
        
        If the linenumber does not correspond with the 
        start of an element then it will return a null.
        '''
        tmpStruct = self.struct
        for elem in tmpStruct:
            startLine = elem.getStartLine()
            if startLine == lineNum:
                return elem.getEndLine()
        return None
        
    def __getLine(self, lineNumber):
        return self.dnetFileMem[lineNumber]
        
    def __getElemType(self, elem):
        '''
        takes a line line like:
            visual V1 {
              or
            node LU_hazard {
        
        and returns the type.  In the first case that would be 'visual',
        in the second case it would be 'node'
        '''

        curLine = self.__getLine(elem.getStartLine())
        elemList = self.__parseDeclarationLine(curLine)
        return elemList[0]
    
    def __getAtribType(self, curLine):
        ''' 
        Recieves something like 
        var = some set of values
        
        returns 'var'
        '''
        elemList = self.__parseDeclarationLine(curLine)
        return elemList[0]
    
    def __getElemName(self, elem):
        ''' 
        recieves an element object, returns the name of that
        element by glueing together the info in the element object
        with the information from the dnet file that is stored in 
        memory.
        '''
        curLine = self.__getLine(elem.getStartLine())
        elemList = self.__parseDeclarationLine(curLine)
        return elemList[1]
    
    def __parseFirstLine(self, elem):
        curLine = self.__getLine(elem.getStartLine())
        elemList = self.__parseDeclarationLine(curLine)
        # expecting the first element in the self.struct to be the bnet element, ie
        # the element that describes the bayes network.  Next line is verifying that 
        # this is the case!
        if elemList[0].upper() <> 'BNET':
            msg = 'expecting the first element in the struct to be a ' + \
                  'BNET type.  There is either a problem with the ' + \
                  'parser or the file! the line that was parsed as' + \
                  'the first element line is (' + curLine + ')'
            raise ValueError, msg
        self.bayesDataObj.setName(elemList[1])
        #print elemList
        
    def __readFileIntoMemory(self):
        '''
        reads the dnet file into an in memory data structure to allow 
        random access to various positions in the file.
        '''
        fh = open(self.dnetFile, 'r')
        self.dnetFileMem = fh.readlines()
        fh.close()
        
    def __parseDeclarationLine(self, line):
        '''
        takes a line line like:
            visual V1 {
              or
            node LU_hazard {
        '''
        line = line.strip()
        partList = re.split('\s+', line)
        return partList[:2]
        
class element():
    '''
    This class is used to store hierarchical data structures
    that are found in the netica .dnet files.  These files contain
    information that describes the baysian belief network.
    
    7-30-2013 - At the moment the only information that is stored is the 
                start end end points of the data structures.  the next step 
                will be to extend this class to allow for the storing of 
                actual information from the netica file.
    
    :ivar childPointer: This is an integer that points to the index position 
                        of the current child.
    :ivar children: This is a list made up of elementObjects (like this one
                    that is being described here) that are children of the 
                    current object
    :ivar endCol: Marks the column in the text file that the end of the 
                  current data structure occurs on.
    :ivar endLine: Marks the line in the text file that corresponds with the
                   end of the current data structure.
    :ivar parentPointer:  a pointer to the current parent.  This could probably
                          be removed down the road seeing as any one object
                          can only have one parent.
    :ivar parents: This is a list (only made up of one element, which is the parent
                   of the current object.
    :ivar startCol: The start column of the current data structure
    :ivar startLine: The start line of the current data structure.
    '''
    
    # TODO: add an iterable interface! Add some tests
    # TODO: add a printable interface!
    
    def __init__(self):
        '''
        The constructor, initializes the class variables to null's
        '''
        # instantiate instance vars
        self.startLine = None
        self.startCol = None
        self.endLine = None
        self.endCol = None
        
        self.parents = []
        self.children = []
        
        self.childPointer = None
        self.parentPointer = None
        
        # will eventually contain a reference to a bayesElement object that
        # contains additional attributes about the node's structure.
        self.bayesAttribs = None
             
        # these properties are used for 
        # iteration.
        self.curIterCnt = 0
        self.maxIter = None
        self.iterStarted = False
        self.ObjList = []
        
    def __iter__(self):
        return self
    
    def spiderStruct(self, obj=None):
        '''
        iterates starting with a root, going through every
        child there is and stuffing them all into a list
        '''
        if obj==None:
            obj = self
        self.ObjList.append(obj)
        children = obj.getChildren()
        for child in children:
            self.spiderStruct(child)
    
    def next(self):
        '''
        An iteration inteface that will return an 
        element, starting with the current
        object then spidering through the children 
        of this object.
        '''
        retVal = None
        if not self.iterStarted:
            self.iterStarted = True
            self.spiderStruct(self)
            self.curIterCnt = 0
            self.maxIter = len(self.ObjList)
        
        if  self.curIterCnt < self.maxIter:
            retVal = self.ObjList[self.curIterCnt]
            self.curIterCnt += 1
            if self.ObjectIsNull(retVal):
                retVal = self.next()
        else:
            # reset the parameters used for iteration so 
            # we can iterate anther time
            self.iterStarted = False
            self.curIterCnt = 0
            self.ObjList = []
            self.maxIter = None
            raise StopIteration
        
        return retVal
    
    def ObjectIsNull(self, obj):
        '''
        parsing of the data structure can result in children of 
        some objects being made up of entirely null values, or in 
        other words a null object that should not be there. This 
        method will test for those types of objects.  Returns true if 
        the object provided as an arg is null, and false if the object
        provided as an arg is true.
        
        :param  obj: The input object that is to be tested
        :type obj: element
        
        :returns: boolean value indicating if the supplied object is null.
        :rtype: boolean
        '''
        if obj.startLine == None and \
           obj.startCol == None and \
           obj.endCol == None and \
           obj.endLine == None:
            retVal = True
        else:
            retVal = False
        return retVal
    
    def setStart(self, line, col):
        '''
        receives the start line and column for the current data 
        structure that is described by this object.
        
        :param  line: an integer that identifies the start line of the
                      data structure that is described by this object.
        :type line: integer
        :param  col: an integer that identifies the start column of the 
                     data structure that is described by this object.
        :type col: integer
        '''
        self.startLine = line
        self.startCol = col
        
    def getStartLine(self):
        return self.startLine
        
    def setEnd(self, line, col):
        '''
        Sets the end column and line for the data structure that is 
        described by this object.
                
        :param  line: an integer that identifies the end line of the 
                     data structure that is described by this object.
        :type line: integer
        :param  col: an integer that identifies the end column of the 
                     data structure that is described by this object.
        :type col: integer
        '''
        self.endLine = line
        self.endCol = col
        
    def getEndLine(self):
        return self.endLine
        
    def getChildren(self):
        '''
        Returns a list of element's that are children
        of the current object.
       
        :returns: a list of elementObjects that are children of the 
                  current object.
        :rtype: list of elementObjects
        '''
        return self.children
        
    def getParent(self):
        '''
        returns the parent of the current object
        
        :returns: an elementObjects that is the parent of the current 
                  object
        :rtype: elementObjects
        '''
        self.parentPointer = len(self.parents) - 1
        #print self.parentPointer
        if self.parentPointer > 0:
            raise 'There are multiple parents, should only ever be one!'
        elif self.parentPointer == 0:
            retObj = self.parents[self.parentPointer]
        else:
            retObj = None
        #self.parentPointer -= 1
        return retObj
    
    def getChild(self):
        '''
        Returns the current child of this element.
       
        :returns: an elementObjects that is the child of the current
                  object.
        :rtype: elementObjects
        '''
        retObj = self.children[self.childPointer]
        self.childPointer -= 1
        return retObj
    
    def addParent(self, parentObj):
        '''
        Receives an element that is the parent of the 
        current object and stores this in a property of the current
        object
        
        :param  parentObj: elementObjects that is the parent of the 
                           the current object.
        :type parentObj: elementObjects
        '''
        # need to verify whether this parent already exists
        self.parents.append(parentObj)
        self.parentPointer = len(self.parents) - 1
        
    def addChild(self):
        '''
        Adds a child element to the current object and returns the
        child element that was just created.        
        
        :returns: an element object that is a child of the current object
        :rtype: element
        '''
        childObj = element()
        childObj.addParent(self)
        self.children.append(childObj)
        self.childPointer = len(self.children) - 1
        return childObj
                
    def setStartAndEnd(self, startLine, startCol, endLine, endCol):
        '''
        This method sets the start line, start column, end line and end
        column for the current element.
                
        :param  startLine: the line the structure that is being described 
                           starts on.
        :type startLine: integer
        :param  startCol: the column that the data sturcture starts on.
        :type startCol: integer
        :param  endLine: the end line
        :type endLine: integer
        :param  endCol: the end column 
        :type endCol: integer
        '''
        self.startLine = startLine
        self.startCol = startCol
        self.endLine = endLine
        self.endCol = endCol
        
    def printProperties(self, indentChar=''):
        '''
        Prints the:
            - start line
            - start column
            - end line
            - end column
        
        for the current object.
        '''
        lbl = ['startline', 'startcol', 'endline', 'endcol']
        vals = []
        cnt = 0
        print '----------------------------'
        for num in [self.startLine, self.startCol, self.endLine, self.endCol]:
            if num <> None:
                vals.append(num + 1)
            else:
                vals.append('NONE')
            print indentChar + lbl[cnt], ' - ', vals[cnt]
            cnt += 1        
        
    def printData(self, startObj):
        '''
        recursively prints the children of the current object.  Prints
        the current object as well as any child objects
        
        :param  startObj: the object that is to be printed
        :type startObj: element
        '''
        startObj.printProperties()
        for child in startObj.getChildren():
            #child.printProperties()
            child.printData(child)
    
if __name__ == '__main__':
    neticaDataDir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica_data'
    dnetFile = os.path.join(neticaDataDir, r'Car_Buyer.dnet.txt')
    dnetTestFile = os.path.join(neticaDataDir, r'testdata.txt')
    
    startEndParse = DNETStructParser(dnetFile)
    startEndParse.parseStartEndPoints()
    parseBayes = startEndParse.populateBayesParams()
    
    #parser = parseDNET(dnetFile)
    #parser.parse()
    
    