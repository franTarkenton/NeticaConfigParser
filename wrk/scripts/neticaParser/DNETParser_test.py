'''
Created on Sep 25, 2013

@author: kjnether
'''
import DNETParser
import os
import unittest


class TestBayesParser(unittest.TestCase):


    def setUp(self):
        dataDir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica_data'
        justFile = r'Car_Buyer.dnet.txt'
        self.testFile = os.path.join(dataDir, justFile)
        self.dnetParser = DNETParser.DNETStructParser(self.testFile)
        self.multilineString1 = 'probs = \n // Peach        Lemon\n (0.8,         0.2);'
        self.multilineString2 = 'probs = \n // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    \n' + \
                           '(((1,           0,           0,           0),             // NoTest       Peach \n' + \
                           '(1,           0,           0,           0)),            // NoTest       Lemon \n' + \
                           '((0,           0.9,         0.1,         0),             // Steering     Peach \n' + \
                           '(0,           0.4,         0.6,         0)),            // Steering     Lemon \n' + \
                           '((0,           0.8,         0.2,         0),             // Fuel_Elect   Peach \n' + \
                           '(0,           0.1333333,   0.5333334,   0.3333333)),    // Fuel_Elect   Lemon \n' + \
                           '((0,           0.9,         0.1,         0),             // Transmission Peach \n' + \
                           '(0,           0.4,         0.6,         0)));           // Transmission Lemon ;'
                           
        self.multilineString3 = '    probs = \n' + \
                                '// Low          Moderate     High           // Density_roads \n' + \
                                '((0.75,        0.25,        0),            // <1 km/km2     \n' + \
                                '(0.25,        0.75,        0),            // 1-2 km/km2    \n' + \
                                '(0.25,        0.5,         0.25));    // 2-3 km/km2    ;'
                                
        self.multilineString4 = '    probs = \n' + \
                                ' //  Low          Moderate     High             // Density_roads Cougar_risk B \n' + \
                                '((((0.75,        0.25,        0),              // <1 km/km2     High        Present  \n' + \
                                '(1,           0,           0)),             // <1 km/km2     High        Not present \n' + \
                                '((0.25,        0.75,        0),              // <1 km/km2     Moderate    Present     \n' + \
                                '(0.5,         0.5,         0)),             // <1 km/km2     Moderate    Not present \n' + \
                                '((0,           0.5,         0.5),            // <1 km/km2     Low         Present     \n' + \
                                '(0.25,        0.75,        0))),            // <1 km/km2     Low         Not present \n' + \
                                '(((0.5,         0.5,         0),              // 1-2 km/km2    High        Present     \n' + \
                                '(1,           0,           0)),             // 1-2 km/km2    High        Not present \n' + \
                                '((0,           1,           0),              // 1-2 km/km2    Moderate    Present     \n' + \
                                '(0.5,         0.5,         0)),             // 1-2 km/km2    Moderate    Not present \n' + \
                                '((0,           0.25,        0.75),           // 1-2 km/km2    Low         Present     \n' + \
                                '(0.25,        0.75,        0))),            // 1-2 km/km2    Low         Not present \n' + \
                                '(((0.25,        0.75,        0),              // 2-3 km/km2    High        Present     \n' + \
                                '(1,           0,           0)),             // 2-3 km/km2    High        Not present \n' + \
                                '((0,           0.75,        0.25),           // 2-3 km/km2    Moderate    Present     \n' + \
                                '(0.5,         0.5,         0)),             // 2-3 km/km2    Moderate    Not present \n' + \
                                '((0,           0,           1),              // 2-3 km/km2    Low         Present     \n' + \
                                '(0.25,        0.75,        0))));           // 2-3 km/km2    Low         Not present '

        self.simpleLine1 = '    defdispform = LABELBOX; '
        self.simpleLine2 = '    states = (Peach, Lemon);'


    def tearDown(self):
        pass

    def test__ParseBayesNet__getPositions(self):
        '''
        verifies the __getPositions method is working.  This test verifies
        that it can accurately find the various search strings it needs to 
        find in various dnet multiline strings.
        '''
        testData1 = 'probs = \n // Peach        Lemon\n (0.8,         0.2);'
        expectedResults1 = [7]
        testData2 = 'probs = \n // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    \n' + \
                           '(((1,           0,           0,           0),             // NoTest       Peach \n' + \
                           '(1,           0,           0,           0)),            // NoTest       Lemon \n' + \
                           '((0,           0.9,         0.1,         0),             // Steering     Peach \n' + \
                           '(0,           0.4,         0.6,         0)),            // Steering     Lemon \n' + \
                           '((0,           0.8,         0.2,         0),             // Fuel_Elect   Peach \n' + \
                           '(0,           0.1333333,   0.5333334,   0.3333333)),    // Fuel_Elect   Lemon \n' + \
                           '((0,           0.9,         0.1,         0),             // Transmission Peach \n' + \
                           '(0,           0.4,         0.6,         0)));           // Transmission Lemon ;'
        # first arg is dummy data.
        parseBayesNet = DNETParser.ParseBayesNet([[0,0]], self.testFile)
        
        retVal = parseBayesNet._ParseBayesNet__getPositions(testData1, 'equal')
        msg = 'The class ParseBayesNet method __getPositions is not finding the ' + \
              'correct locations the \'=\' string'
        self.assertEqual(retVal, [6], msg)
        retVal = parseBayesNet._ParseBayesNet__getPositions(testData2, 'equal')
        self.assertEqual(retVal, [6], msg)

        
        msg = 'The class ParseBayesNet method __getPositions is not finding the ' + \
              'correct locations the \'//\' string'
        retVal = parseBayesNet._ParseBayesNet__getPositions(testData1, 'comment')
        self.assertEqual(retVal, [10], msg)
        retVal = parseBayesNet._ParseBayesNet__getPositions(testData2, 'comment')
        self.assertEqual(retVal, [9, 67, 148, 227, 307, 386, 466, 545, 625, 704], msg)
        print 'retVal:', retVal
    
    def test__ParseBayesNet__parseAndEnterMultiLineString(self):
        '''
        The test above, test__ParseBayesNet__getPositions returns the positions of 
        various key features from the data structures described below.  This test usees
        those parameters to help with the parsing of these data stuctures.
            
        A)
        probs =  // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    
        (((1,           0,           0,           0),             // NoTest       Peach 
          (1,           0,           0,           0)),            // NoTest       Lemon 
         ((0,           0.9,         0.1,         0),             // Steering     Peach 
          (0,           0.4,         0.6,         0)),            // Steering     Lemon 
         ((0,           0.8,         0.2,         0),             // Fuel_Elect   Peach 
          (0,           0.1333333,   0.5333334,   0.3333333)),    // Fuel_Elect   Lemon 
         ((0,           0.9,         0.1,         0),             // Transmission Peach 
          (0,           0.4,         0.6,         0)));           // Transmission Lemon ;
        
        B) 
        probs = // Peach        Lemon
            ( 0.8,         0.2)
            
        Need to be able to write a parser for each of these.
        
        '''
        struct = self.dnetParser.getNodeStartendLines()
        parseBayesNet = DNETParser.ParseBayesNet(struct, self.testFile)
        #print dir(parseBayesNet)
        # Note to test hidden method, use the method name:
        # _ParseBayesNet__<hidden method name>
        #print '--------------------'
        # testing the multiline parser:
        nodeObj = parseBayesNet.getBayesDataObj()
        parseBayesNet._ParseBayesNet__parseAndEnterMultiLineString(self.multilineString1, nodeObj)
        parseBayesNet._ParseBayesNet__parseAndEnterMultiLineString(self.multilineString2, nodeObj)

    def test__ParseBayesNet__getAttributeHeaders(self):
        expected1_1 = []
        expected1_2 = ['Peach', 'Lemon']
        
        expected2_1 = ['NoResult', 'NoDefects', 'OneDefect', 'TwoDefects']
        expected2_2 = ['T1', 'CC']

        struct = self.dnetParser.getNodeStartendLines()
        parseBayesNet = DNETParser.ParseBayesNet(struct, self.testFile)
        mutlti1_l1, mutlti1_l2 = parseBayesNet._ParseBayesNet__getAttributeHeaders(self.multilineString1)
        mutlti2_l1, mutlti2_l2 = parseBayesNet._ParseBayesNet__getAttributeHeaders(self.multilineString2)
        
        # assertions
        for comparisonList in [[expected1_1, mutlti1_l1], \
                               [expected1_2, mutlti1_l2], \
                               [expected2_1, mutlti2_l1], \
                               [expected2_2, mutlti2_l2]]:
            retmsg = 'expected values: ' + str(comparisonList[0]) + '\n' + \
                  'returned values: ' + str(comparisonList[1]) + '\n' + \
                  'Method __getAttributeHeaders not returning expected results!'
            self.assertEqual(comparisonList[0], comparisonList[1], retmsg)
    
    
    def test__ParseBayesNet__parseMultiListMultiLineProbAttribute(self):
        struct = self.dnetParser.getNodeStartendLines()
        parseBayesNet = DNETParser.ParseBayesNet(struct, self.testFile)
        parseBayesNet._ParseBayesNet__parseMultiListMultiLineProbAttribute(self.multilineString4)
        #parseBayesNet._ParseBayesNet__parseMultiListMultiLineProbAttribute(self.multilineString3)
        
    def test__ParseBayesNet__getAtribType(self):
        struct = self.dnetParser.getNodeStartendLines()
        parseBayesNet = DNETParser.ParseBayesNet(struct, self.testFile)
        testData = [[self.multilineString1, 'probs'], \
                    [self.multilineString2, 'probs'], \
                    [self.simpleLine1, 'defdispform'], \
                    [self.simpleLine2, 'states']]
        for testRow in testData:
            retVal = parseBayesNet._ParseBayesNet__getAtribType(testRow[0])
            errMsg = 'The method __getAtribType returned: (' + str(retVal) + \
                     ') for the submitted line: (' + str(testRow[0]) + \
                     ') expecting the value: ' + str(testRow[1])
            self.assertEqual(retVal, testRow[1], errMsg)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    
    # run a single test
        # run selected tests that are added using addTest
    testSuite = unittest.TestSuite()
    
#     testSuite.addTest(TestBayesParser('test__ParseBayesNet__getAttributeHeaders'))
    testSuite.addTest(TestBayesParser('test__ParseBayesNet__parseMultiListMultiLineProbAttribute'))
    unittest.TextTestRunner(verbosity=2).run(testSuite)
