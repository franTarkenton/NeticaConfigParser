'''
Created on Oct 4, 2013

@author: kjnether
'''
import datetime
import getpass
import inspect
import logging
import os.path
import unittest

import DNETParser
import NeticaData


class NeticaDataTest(unittest.TestCase):


    def setUp(self):
        # setting up logging here
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
        self.logger = logging.getLogger()
        # create a handler
        hndlr = logging.FileHandler(self.logFile)
        # creating a formatter and applying formatting to the formatter 
        formatString = '%(asctime)s %(name)s.%(funcName)s.%(lineno)d %(levelname)s: %(message)s'
        formatr = logging.Formatter( formatString )
        formatr.datefmt = '%m-%d-%Y %H:%M:%S' # set up the date format for log messages
        # apply to formatter to the handler
        hndlr.setFormatter(formatr)
        # Step 5 - tell the log object to use the handler
        self.logger.addHandler(hndlr)
        # Step 6 - set the log level
        self.logger.setLevel(logging.INFO)
        # Step 7 - create a logging object that this module will use to write its log messages to
        #             the name of the log object will be moduleName.className
        logName = module_name + '.' + self.__class__.__name__
        #print 'logName', logName
        self.logger = logging.getLogger( logName )
        # Step 8 on, write some log messages
        self.logger.debug('this is my first log message!')
        
        
        
        
        
        dataDir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica_data'
        inFile = os.path.join(dataDir, 'Car_Buyer.dnet.txt')
        self.parser = DNETParser.DNETStructParser(inFile)
        self.parser.parseStartEndPoints()
        self.neticaParser = self.parser.populateBayesParams()
        self.neticaObj = self.neticaParser.getBayesDataObj()
        
        
        
        

    def tearDown(self):
        pass


    def test_verifyDataParse(self):
        rootNodeNames = self.neticaObj.getAllNodeNames()
        for nodeName in rootNodeNames:
            print 'node name is: ' , nodeName
            node = self.neticaObj.getNode(nodeName)
            print 'node kind is :', node.kind

            print 'states: ', node.getStates()
            print 'parents: ', node.getParentNames()
            probTable = node.getProbabilityTable()
            if probTable:
                likleyHood = probTable.getLikelyHoodTable()
                parentVals = probTable.getParentValuesTable()
                print 'likleyHood:', likleyHood
        

    def test_getRootNodes(self):
        
        self.neticaObj.getRootNodeNames()
        neticaLoader = NeticaData.netica2OpenBayes(self.neticaObj)
        neticaLoader.loadData()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    
    testSuite = unittest.TestSuite()
    #testSuite.addTest(NeticaDataTest('test_getRootNodes'))
    testSuite.addTest(NeticaDataTest('test_getRootNodes'))
    unittest.TextTestRunner(verbosity=2).run(testSuite)
    
    