'''
Created on Oct 4, 2013

@author: kjnether
'''
import unittest
import os.path
import DNETParser
import NeticaData


class NeticaDataTest(unittest.TestCase):


    def setUp(self):
        dataDir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica_data'
        inFile = os.path.join(dataDir, 'Car_Buyer.dnet.txt')
        self.parser = DNETParser.DNETStructParser(inFile)
        self.parser.parseStartEndPoints()
        self.neticaParser = self.parser.populateBayesParams()
        self.neticaObj = self.neticaParser.getBayesDataObj()

    def tearDown(self):
        pass


    def test_getRootNodes(self):
        self.neticaObj.getRootNodeNames()
        neticaLoader = NeticaData.netica2OpenBayes(self.neticaObj)
        neticaLoader.loadData()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    
    testSuite = unittest.TestSuite()
    testSuite.addTest(NeticaDataTest('test_getRootNodes'))
    unittest.TextTestRunner(verbosity=2).run(testSuite)
    
    