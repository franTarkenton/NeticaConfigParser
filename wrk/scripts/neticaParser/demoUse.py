'''
Created on Oct 15, 2013

@author: kjnether
'''
import datetime
import getpass
import inspect
import logging
import os

import OpenBayes
from neticaParser import DNETParser, NeticaData


class Dnet2OpenBayes(object):
    logger = None
    rootLog = None
    
    def __init__(self):
        self.__initLog()
    
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
        if __name__ == '__main__':
            module_name = inspect.getmodulename(s[1][1])
        else:
            module_name = __name__
        user = getpass.getuser()
        timeString = datetime.datetime.now().strftime("%a%b%d%H%M%S")
        logFile = module_name + '_' + user + '_' + timeString + '.log'
        if os.path.exists(defaultLocation):
            self.logFile = os.path.join(defaultLocation, logFile)
        else:
            self.logFile = os.path.join(os.environ['TEMP'], logFile)
        print 'logfile:', self.logFile
        print 'modname:', module_name
        # create the log object
        rootLog = logging.getLogger()
        # create a handler
        hndlr = logging.FileHandler(self.logFile)
        # creating a formatter and applying formatting to the formatter 
        formatString = '%(asctime)s %(name)s.%(funcName)s.%(lineno)d %(levelname)s: %(message)s'
        formatr = logging.Formatter( formatString )
        formatr.datefmt = '%m-%d-%Y %H:%M:%S' # set up the date format for log messages
        # apply to formatter to the handler
        hndlr.setFormatter(formatr)
        # Step 5 - tell the log object to use the handler
        rootLog.handlers = [] # make sure that there are not any existing handlers
        rootLog.addHandler(hndlr)
        # Step 6 - set the log level
        rootLog.setLevel(logging.DEBUG)
        # Step 7 - create a logging object that this module will use to write its log messages to
        #             the name of the log object will be moduleName.className
        logName = module_name + '.' + self.__class__.__name__

        #logName = module_name + '.' + self.__class__.__name__
        #print 'logName', logName
        
        self.logger = logging.getLogger(logName)
        
        # Step 8 on, write some log messages
        self.logger.debug('this is my first log message Damn it!')
    
    def translate(self, dnetFile):
        self.parser = DNETParser.DNETStructParser(dnetFile)
        self.neticaParser = self.parser.populateBayesParams()
        self.neticaObj = self.neticaParser.getBayesDataObj()
        neticaLoader = NeticaData.netica2OpenBayes(self.neticaObj)
        neticaLoader.loadData()
        self.openBayesObj = neticaLoader.getOpenBayesNetwork()
        
    def reportOnOpenBayesNetwork(self):
        for vert in self.openBayesObj.topological_sort():
            print '---------------------'
            print vert.name
            print vert.distribution.cpt
            if len(vert.distribution.parents) > 0:
                names = []
                for vert in vert.distribution.parents:
                    names.append(vert.name)
                print 'Edges:', ','.join(names)
            else:
                print 'Edges: None'

        
if __name__ == '__main__':
    dnetFile = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\netica_data\Mule deer model 6.dnet.txt.dne'
    tranlateObj = Dnet2OpenBayes()
    tranlateObj.translate(dnetFile)
    tranlateObj.reportOnOpenBayesNetwork()
    

    
    