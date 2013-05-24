'''
Created on 2013-05-14

@author: kjnether




'''
import unittest
import DNETParser
from numpy.testing.utils import assert_equal
from numpy.ma.testutils import assert_not_equal
import re


class TestParser(unittest.TestCase):
    
    def setUp(self):
        dnetFile = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica\Car_Buyer.dnet.txt'
        self.parseObj = DNETParser.parseDNET(dnetFile)
        self.testData = ["node T2 {",
                   "     kind = DECISION;",
                   "     discrete = TRUE;",
                   "     testFalse = FALSE;",
                   "     chance = DETERMIN;",
                   "     states = (NoTest, Differential);",
                   "     parents = (T1, R1);",
                   '     title = "Do Test 2?";',
                   "     visual V1 {",
                   "            center = (306, 60);",
                   "            height = 4;",
                   "            };",
                   "     height = 5980;", 
                   "     testfloatValueThatICreated = 5.5;",
                   " };"]



    def testCommentRegExpr(self):
        self.parseObj.buildRegularExpressions()
        inputCommentLines = [r'// blah blah blah ', r' //blah blah', r' // //', 
                             r'// blah blah / ']
        for testLine in inputCommentLines:
            retVal = self.parseObj.re_comments.match(testLine)
            print 'testline-' + testLine
            print 'retval is', retVal
            print str(type(retVal))
            assert_not_equal(retVal, None)
            # should put in an assertion that verifies the type of the 
            # return value to be certain that things worked here. But 
            # can't figure the syntax.
            pass
        
    def testPropertyAssignment(self):
        self.parseObj.buildRegularExpressions()
        # different property type = title = "Condition"; title = "Do Test 2?";
        inputLinesPass = ['autoupdate = TRUE;',
                      'defdispform = LABELBOX;',
                      'showpagebreaks = FALSE;',
                      'kind = NATURE;', 
                      'chance = CHANCE;',
                      'chance = DETERMIN;', 
                      'measure = RATIO;']
        
        inputLinesFail = ['height = 7;',
                          'center = (504, 174);',
                          'title = "Condition";',
                          'title = "Do Test 2?";']
        
        for line2pass in inputLinesPass:
            retVal = self.parseObj.re_propertyAssign.match(line2pass)
            errMsg = 'input line (' +  line2pass + ') is not matched by the regular expression but it should be'
            self.assertNotEqual(retVal, None, errMsg)
        
        for line2Fail in inputLinesFail:
            retVal = self.parseObj.re_propertyAssign.match(line2Fail)
            errMsg = 'input line (' +  line2Fail + ') is  matched by the regular expression but it should not be'
            self.assertIsNone(retVal, errMsg)
            
    def testMultiline(self):
        self.parseObj.buildRegularExpressions()
        
        testListPass = ['    probs = ', 
                        '    functable = ']
        
        testListFail = ['   defdispform = LABELBOX;',
                        'visual V1 {',
                        'nodefont = font {shape= "Arial"; size= 10;};',
                        '    windowposn = (40, 22, 676, 387);',
                        'resolution = 72;',
                        '    };']
                        
        for line2pass in testListPass:
            retVal = self.parseObj.re_startMultiLine.match(line2pass)
            errMsg = 'input line (' +  line2pass + ') is not matched by the regular expression but it should be'
            self.assertNotEqual(retVal, None, errMsg)
        
        for line2Fail in testListFail:
            retVal = self.parseObj.re_startMultiLine.match(line2Fail)
            errMsg = 'input line (' +  line2Fail + ') is  matched by the regular expression but it should not be'
            self.assertIsNone(retVal, errMsg)
            
    def testStartStruct(self):
        self.parseObj.buildRegularExpressions()
        testListPass = ['visual V1 {',
                        'node CC {', 
                        '   node V { ',
                        '    visual V1 {',
                        '    visual V1 {' ]
        
        testListFail = ['    probs = ', 
                        '    functable = ',
                        '   defdispform = LABELBOX;',
                        'nodefont = font {shape= "Arial"; size= 10;};',
                        '    windowposn = (40, 22, 676, 387);',
                        'resolution = 72;',
                        '    };']
        for line2pass in testListPass:
            retVal = self.parseObj.re_structStartMultiLine.match(line2pass)
            errMsg = 'input line (' +  line2pass + ') is not matched by the regular expression but it should be'
            self.assertNotEqual(retVal, None, errMsg)
            
        for line2Fail in testListFail:
            retVal = self.parseObj.re_structStartMultiLine.match(line2Fail)
            errMsg = 'input line (' +  line2Fail + ') is  matched by the regular expression but it should not be'
            self.assertIsNone(retVal, errMsg)
            
    def testMultiLineStringStart(self):
        self.parseObj.buildRegularExpressions()
        # test 1, this version is used to get things working and verify the regular expression 
        #         is correct, or at least provide a starting point in the debugging of this 
        #         regular expresssion.
        #self.re_multiLineStringStart = re.compile(r'^\s*\w+\s*={1}\s*\"{1}.+\\{1}$')
        
        startTestLine = 'comment = "An example influence diagram for Joe, who has to decide \\'
        #print 'startTestLine:', startTestLine
        #retVal = self.re_multiLineStringStart.match(startTestLine)
        retVal = self.parseObj.re_multiLineStringStart.match(startTestLine)
        errMsg = "Re expression did not match the line when it should have!"
        self.assertNotEqual(retVal, None, errMsg)
        
        inputData = ['comment = "An example influence diagram for Joe, who has to decide \\',
                     'whether to buy a certain used car which may be a \'peach\' or a \\',
                     '\'lemon\'.  He has the option of doing some tests beforehand, \\',
                     'and of buying it with a guarantee or not.\n\\',
                     'This is the classic example of an influence diagram derived \\',
                     'from a decision problem with a very asymmetric decision tree, \\',
                     'since if Joe decides not to test then the test results have \\',
                     'no meaning, etc.\n\\',
                     'This problem was posed (in decision tree representation) by \\',
                     'Howard62, and is described as an influence diagram in Qi94 \\',
                     'and in SmithHM93.";']
        
        linesThatShouldMatch = [0]
        
        lineCnt = 0
        for line in inputData:
            retVal = self.parseObj.re_multiLineStringStart.match(line)
            if linesThatShouldMatch.count(lineCnt):
                errMsg = 'Should have matched this line! (', line, ')'
                self.assertNotEqual(retVal, None, errMsg)
            else:
                errMsg = 'Shouldn\'t have matched this line! (', line, ')'
                self.assertIsNone(retVal, errMsg)
            lineCnt += 1
                
    def testMultiLineStringEnd(self):
        self.parseObj.buildRegularExpressions()
        startTestLine = '        and in SmithHM93.";'
        retVal = self.parseObj.re_multiLineStringEnd.match(startTestLine)
        errMsg = "The following line was not matched as the end of a multiline" + \
                 " string: (" + str(startTestLine) + ")"
        self.assertNotEqual(retVal, None, errMsg)
        inputData = ['comment = "An example influence diagram for Joe, who has to decide \\',
                     'whether to buy a certain used car which may be a \'peach\' or a \\',
                     '\'lemon\'.  He has the option of doing some tests beforehand, \\',
                     'and of buying it with a guarantee or not.\n\\',
                     'This is the classic example of an influence diagram derived \\',
                     'from a decision problem with a very asymmetric decision tree, \\',
                     'since if Joe decides not to test then the test results have \\',
                     'no meaning, etc.\n\\',
                     'This problem was posed (in decision tree representation) by \\',
                     'Howard62, and is described as an influence diagram in Qi94 \\',
                     'and in SmithHM93.";']
        
        linesThatShouldMatch = [len(inputData) - 1]
        lineCnt = 0
        for line in inputData:
            #print line
            retVal = self.parseObj.re_multiLineStringEnd.match(line)
            if linesThatShouldMatch.count(lineCnt):
                errMsg = 'Should have matched this line! (', line, ')'
                self.assertNotEqual(retVal, None, errMsg)
            else:
                errMsg = 'Shouldn\'t have matched this line! (', line, ')'
                self.assertIsNone(retVal, errMsg)
            lineCnt += 1
            
    def testGetRestOfMultiLineComments(self):
        self.parseObj.buildRegularExpressions();
        # now read to the line where the comment is:
        fh = open(self.parseObj.inputDnetFile, 'r')
        lineCnt = 0
        while lineCnt <> 6:
             line = fh.readline()
             lineCnt += 1
        self.parseObj.fh = fh
        retVal = self.parseObj.getRestOfMultiLineComments()
        print 'retVal:', retVal
        
    def testSingleLineString(self):
        self.parseObj.buildRegularExpressions();
        testData = ["node T2 {",
                   "     kind = DECISION;",
                   "     discrete = TRUE;",
                   "     chance = DETERMIN;",
                   "     states = (NoTest, Differential);",
                   "     parents = (T1, R1);",
                   '     title = "Do Test 2?";',
                   "     visual V1 {",
                   "            center = (306, 60);",
                   "            height = 4;",
                   "            };",
                   " };"]
        lineCnt = 0
        successLine = [6]
        for line in testData:
            retVal = self.parseObj.re_singleLineString.match(line)
            if successLine.count(lineCnt):
                errMsg = "Should have matched this line (" + str(line) + ')'
                self.assertNotEqual(retVal, None, errMsg)
            else:
                errMsg = "This line should not have matched! (" + str(line) + ')'
                self.assertIsNone(retVal, errMsg)
            lineCnt += 1
        
    def testSingleLineStringParser(self):
        inputLine = 'title = "Do Test 2?";'
        expectedVarName = 'title'
        expectedValue = 'Do Test 2?'
        retVarName, retValue = self.parseObj.singleLineStringParser(inputLine)
        
        # verify the returned variable name
        msg = "input string is: " + inputLine + '\n' + \
              "expected variable name is: " + str(expectedVarName) + '\n' \
              "returned variable name is: " + str(retVarName)
        self.assertEquals(expectedVarName, retVarName, msg)
        
        # verify the returned value
        msg = "input string is: " + inputLine + '\n' + \
              "expected value is: " + str(expectedValue) + '\n' \
              "returned value is: " + str(retValue)
        self.assertEquals(expectedValue, retValue, msg)
        
    def testSingleLineProperty(self):
        self.parseObj.buildRegularExpressions();
        matchLines = [1, 4]
        lineNum = 0
        for line in self.testData:
            retVal = self.parseObj.re_singleLineProperty.match(line)
            if lineNum in matchLines:
                msg = 'This line should have matched! (' + str(line) + ')' 
                self.assertNotEqual(retVal, None, msg)
            else:
                msg = 'This line should not have matched but it did (' + str(line) + ')'
                self.assertIsNone(retVal, msg)
            lineNum += 1
    
    def testSingleLineBooleanProperty(self):
        '''
        tests to see if the line is a boolean property
        '''
        self.parseObj.buildRegularExpressions()
        matchLines = [2,3]
        lineNum = 0
        for line in self.testData:
            retVal = self.parseObj.re_singleLineBooleanProperty.match(line)
            if lineNum in matchLines:
                 msg = 'This line should have matched! (' + str(line) + ')' 
                 self.assertNotEqual(retVal, None, msg)
            else:
                msg = 'This line should not have matched but it did (' + str(line) + ')'
                self.assertIsNone(retVal, msg)
            lineNum += 1
            
    def testSingleLineNumericProperty(self):
        self.parseObj.buildRegularExpressions()
        matchLines = [10,12,13]
        lineNum = 0
        for line in self.testData:
            retVal = self.parseObj.re_singleLineNumericProperty.match(line)
            if lineNum in matchLines:
                 msg = 'This line should have matched! (' + str(line) + ')' 
                 self.assertNotEqual(retVal, None, msg)
            else:
                msg = 'This line should not have matched but it did (' + str(line) + ')'
                self.assertIsNone(retVal, msg)
            lineNum += 1
            
    def testSingleLineListNumbers(self):
        self.parseObj.buildRegularExpressions()
        matchLines = [5,6,9]
        lineNum = 0
        for line in self.testData:
            retVal = self.parseObj.re_singleLineListNumbers.match(line)
            if lineNum in matchLines:
                 msg = 'This line should have matched! (' + str(line) + ')' 
                 self.assertNotEqual(retVal, None, msg)
            else:
                msg = 'This line should not have matched but it did (' + str(line) + ')'
                self.assertIsNone(retVal, msg)
            lineNum += 1
            
        

        
    

if __name__ == "__main__":
    # run all the tests
    #unittest.main()
    
    # run selected tests that are added using addTest
    testSuite = unittest.TestSuite()
    #testSuite.addTest(TestParser('testCommentRegExpr'))
    #testSuite.addTest(TestParser('testPropertyAssignment'))
    #testSuite.addTest(TestParser('testMultiline'))
    testSuite.addTest(TestParser('testSingleLineListNumbers'))
    unittest.TextTestRunner(verbosity=2).run(testSuite)
    
    
    