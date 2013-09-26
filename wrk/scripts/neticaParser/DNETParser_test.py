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
        testData2 = 'probs =  // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    \n' + \
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
    
    def testMultiLineAttributeParser(self):
        '''
        some parameters in a dnet file can take on one of these two looks:
        
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
        multilineString1 = 'probs = \n // Peach        Lemon\n (0.8,         0.2);'
        multilineString2 = 'probs =  // NoResult     NoDefects    OneDefect    TwoDefects      // T1           CC    \n' + \
                           '(((1,           0,           0,           0),             // NoTest       Peach \n' + \
                           '(1,           0,           0,           0)),            // NoTest       Lemon \n' + \
                           '((0,           0.9,         0.1,         0),             // Steering     Peach \n' + \
                           '(0,           0.4,         0.6,         0)),            // Steering     Lemon \n' + \
                           '((0,           0.8,         0.2,         0),             // Fuel_Elect   Peach \n' + \
                           '(0,           0.1333333,   0.5333334,   0.3333333)),    // Fuel_Elect   Lemon \n' + \
                           '((0,           0.9,         0.1,         0),             // Transmission Peach \n' + \
                           '(0,           0.4,         0.6,         0)));           // Transmission Lemon ;'
        nodeObj = parseBayesNet.getBayesDataObj()
        retVal = parseBayesNet._ParseBayesNet__getPositions(multilineString1, 'comment')
        print 'retVal is', retVal
#         sys.exit()
#         parseBayesNet._ParseBayesNet__parseAndEnterMultiLineString(multilineString1, nodeObj)
#         parseBayesNet._ParseBayesNet__parseAndEnterMultiLineString(multilineString2, nodeObj)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    
    
    
    # run a single test
        # run selected tests that are added using addTest
    testSuite = unittest.TestSuite()
    testSuite.addTest(TestBayesParser('test__ParseBayesNet__getPositions'))
    unittest.TextTestRunner(verbosity=2).run(testSuite)
