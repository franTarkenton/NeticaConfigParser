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


if __name__ == "__main__":
    # run all the tests
    #unittest.main()
    
    # run selected tests that are added using addTest
    testSuite = unittest.TestSuite()
    #testSuite.addTest(TestParser('testCommentRegExpr'))
    #testSuite.addTest(TestParser('testPropertyAssignment'))
    #testSuite.addTest(TestParser('testMultiline'))
    testSuite.addTest(TestParser('testStartStruct'))
    unittest.TextTestRunner(verbosity=2).run(testSuite)
    
    
    