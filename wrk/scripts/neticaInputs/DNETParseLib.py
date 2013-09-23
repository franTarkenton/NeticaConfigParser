
import linecache


class DNETDataParser():
    
    def __init__(self, dnetFile):
        '''
        Input element is a root level elementObj with the 
        structure of the dnet file contained in it
        '''
        self.dnetFile = dnetFile
        parseObj = DNETStructParser(dnetFile)
        self.struct = parseObj.getElementTreeRootElement()
        print 'struct is:'
        print self.struct
        fh = open(dnetFile, 'r')
        self.dnetMem = fh.readlines()
        fh.close()
    
    def parse(self):
        '''
        at this point we have the information about the start and 
        stop points of various elements contained in the dnet file.
        
        This method will use that information to extract pertinent lines
        required to run the bayes network, with some actual data creating
        a belief surface!
        
        elements to extract:
        bnet - this is the root of all elements
        kind - NATURE      Chance, deterministic node
               DECISION    decison node
               UTILITY     "value" node of influence diagram
               ASSUME      parameter for "what-if" conditions
        discrete - if value discrete or continuous TRUE / FALSE
        chance - either CHANCE or DETERMIN
        
        skip:
            autoupdate
            comment
            whenchanged
            any visual nodes, and all attributes relating to them
            measure - not used in mule deer, can code later.
            
        '''
        rootStart = self.struct.startLine
        
        print 'line:', self.dnetMem[rootStart]
        
        


class DNETStructParser():
    '''
    This class contains the methods necessary to parse out the 
    start and stop points of netica's nested data structures.
    '''
    lineCnt = 1
    defaultLine = [None, None, None, None, []]
    struct = None
    
    startChar = '{'
    endChar = '}'
    
    def __init__(self, dnetFile):
        self.dnetFile = dnetFile
    
    def parseStartEndPoints(self):
        self.fh = open(self.dnetFile, 'r')
        self.struct = self.__parseStructs(self.struct, None)
        self.fh.close()
        
    def getElementTreeRootElement(self):
        if not self.struct:
            self.parseStartEndPoints()
        return self.struct
        
    def __parseStructs(self, curStruct, prevStruct):
        # initial scan which records where the startChar and 
        # endChar's are found.
        startEnd = []
        lineNum = 0
        for line in self.fh:
            charNum = 0
            for char in line:
                if char == self.startChar:
                    startEnd.append(['START', lineNum, charNum])
                elif char == self.endChar:
                    startEnd.append(['END', lineNum, charNum])
                charNum += 1
            lineNum += 1
        print startEnd
        # now that I know where the startChar and endChars are located
        # the next step is to stuff them into a hierarchical data structure
        hierarchDataStruct = self.__restruct(startEnd)
        return hierarchDataStruct
                    
    def __restruct(self, elemList):
        struct = self.defaultLine
        pointer = struct
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
                    curElemObj.setStartAndEnd(startLine, startCol, endLine, endCol)
                    curElemObj.printProperties()
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
                parentObj.printProperties()
                
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
    # TODO: add logging to the module
    
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
        print self.parentPointer
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
    
    def printProperties(self):
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
            print lbl[cnt], ' - ', vals[cnt]
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
    dnetFile = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica\Car_Buyer.dnet.txt'
    dnetTestFile = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica\testdata.txt'
    
    # used to test just the line parser.
    #startEndParse = DNETStructParser(dnetTestFile)
    #startEndParse.parseStartEndPoints()
    

    # used to test the data parser
    dnetDataParser = DNETDataParser(dnetFile)
    dnetDataParser.parse()
    