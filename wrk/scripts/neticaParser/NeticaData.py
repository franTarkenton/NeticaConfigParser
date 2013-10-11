'''

This module classes to store the various pieces of information from 
the netica baysian models.  It should also provide an api that 
makes it easy to take the information out of this data model and 
put it into any bayes library / framework.

Created on Sep 23, 2013

@author: kjnether
'''
import inspect
import logging
import os
import re
import sys
import OpenBayes


class neticaNet(object):
    '''
    This is the actual network.  This object will be composed
    of Nodes and Edges.
    '''
    def __init__(self):
        self.name = None
        self.rootNodes = []
        self.nodeDict = {}
        
        # nature, decision, utility, constant
        # 
        
        # chance - deterministic probableistic
        # deterministic - no randomness involved in determining future state
        # probablistic - likelyhood of something happening.
        
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
        
    def newNode(self, name):
        '''
        creates a new node.  Does not attach it to this network, 
        but does store it in a dictionary that allows it to be 
        easily retrieved.
        '''
        nodeObj = neticaNode()
        nodeObj.setName(name)
        self.nodeDict[name] = nodeObj
        return self.nodeDict[name]
        
    def getRootNodeNames(self, recalc=True):
        '''
        Returns a list of the node names that form the start
        of this network.  In other words the nodes that do 
        not have any children.
        
        :param  recalc: param description
        :type recalc: enter type
        '''
        rootNodes = []
        if not self.rootNodes or recalc:
            for nodekey in self.nodeDict.keys():
                nodeObj = self.nodeDict[nodekey]
                parents = nodeObj.getParentNames()
                #print 'parents are:', parents
                if not nodeObj.getParentNames():
                    print 'root:',  nodekey
                    rootNodes.append(nodekey)
        return rootNodes
                    
    def getAllNodeNames(self):
        '''
        Returns a list of strings that contains the names 
        of all the nodes that make up this network
        
        :returns: a list of strings, the names of all the nodes that 
                 make up the netica network
        :rtype: list(str)
        '''
        return self.nodeDict.keys()
    
    def getNonRootNodeNames(self):
        rootNodeNames = self.getRootNodeNames()
        allNodeNames = self.getAllNodeNames()
        nonRootNodes = [item for item in allNodeNames if item not in rootNodeNames]
        return nonRootNodes
                
    def getParentNodeNames(self, nodeName):
        retNodes = []
        for nodeKey in self.nodeDict.keys():
            nodeObj = self.nodeDict[nodeKey]
            parentNames = nodeObj.getParentNames()
            for parentName in parentNames:
                if parentName == nodeName:
                    retNodes.append(parentName)
        return retNodes
                    
    def getParentNodes(self, nodeName):
        parentNodeName = self.getParentNodeNames(nodeName)
        retNodes = []
        for parentName in parentNodeName:
            retNodes.append(self.getNode(parentName))
        return retNodes
                    
    def getNode(self, name):
        '''
        Returns a neticaNode object that corresponds with the 
        name provided.  If the name does not exist then it will 
        raise a ValueError.
        
        :param  name: The name of the node that you would like 
                      to have returned
        :type name: string
        
        :returns: a netica node object that corresponds with the name
                  supplied as an arguement.
        :rtype: neticaNode
        '''
        if not self.nodeDict.has_key(name):
            errMsg = 'You requested a node by the name of (' + str(name) + ') ' + \
                     'however there are not any nodes by this name in this network. ' + \
                     'Nodes that exist are: (' + ','.join(self.nodeDict.keys())
            raise ValueError, errMsg
        return self.nodeDict[name]
                
    def printReport(self):
        '''
        creates a printout that describes the bayesNet
        '''
        pass

class neticaNode(object):
    
    logger = None
    
    def __init__(self):
        self.__initLogging()
        self.name = ''
        #self.type = None  # Node, Vertex, network, edge
        self.states = [] # These are the values associated with the node
        self.kind = None # Nature, Decision, Utility, Constant
        self.chance = None # deterministic probabilistic
        self.parents = [] # dependent nodes.  Root level will not have any parents, ie the bottom of the tree or the start of the network
        self.probabilityTable = None
        self.funcTable = None
        self.discrete = None # True or False
        
        self.validationDict = self.getValidationDict()
    
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
    
    def getParentNames(self):
        # There is a flaw in how the parents are populated.  In a rush to get this 
        # working, so instead of findign the flaw I am patching up this data when
        # it gets requested.
        newList = []
        for i in self.parents:
            if i:
                newList.append(i)
        self.parents = newList
        return self.parents
    
    def setName(self, name):
        self.name = name
        self.logger.debug("name is: " + str(name))
        
    def isDiscrete(self):
        
        return self.discrete
            
    def getStates(self):
        '''
        Returns the a list containing all the possible states of the
        current node        
        
        :returns: a list containing the different states that this node
                  can take on.
        :rtype: list
        '''
        return self.states
        
    def getValidationDict(self):
        '''
        returns a dictionary that contains the information used to 
        validate valid attributes of this object.  If the corresponding
        value is a None value it indicates there is no value checking 
        on this attribute type. 
        
        all types are in lower case.
        '''
        validationDict = {'name': None, 
                          'states': None, 
                          'kind': ['nature', 'decision', 'utility', 'constant'], 
                          'chance': ['determin', 'chance'], 
                          'parents': None, 
                          'probs': None, 
                          'discrete': [True, False],
                          'title': None, 
                          'functable': None,
                          'measure':['ratio', 'nominal', 'local', 'ordinal', 'interval']}
        return validationDict
        
    def setProbabilityTable(self, neticaProbabilityTable):
        '''
        Enters a ProbsValueTable to the current nodes
        probs attribute
        '''
        self.probabilityTable = neticaProbabilityTable
        self.logger.debug("prob table: " + str(neticaProbabilityTable))
      
    def getProbabilityTable(self):
        if not self.probabilityTable:
            warnMsg = 'There is no probability table for the node "' + \
                      str(self.name) + '" Going to create one with ' + \
                      'equal probabilities for each entry '
            self.logger.warning(warnMsg)
            self.__makeProbabilityTable()
        return self.probabilityTable
    
    def __makeProbabilityTable(self):
        # create the probabiltiy table with an equal value for each
        # state.  
        # think about what to do with parent nodes
        self.probabilityTable = ProbsValueTable(self.states)
        self.probabilityTable.setRootValues()
      
    def setFunctionTableObject(self, funcTable):
        '''
        
        '''
        self.funcTable = funcTable
        self.logger.debug('func table is: ' + str(funcTable))
    
    def enterAndValidateSimpleAttribute(self, property, value):
        property = property.lower()
        value = value.lower()
        valueIsList = False
        #print 'property'.upper(), ' = ', str(property)
        #print 'value'.upper(), ' = ', str(value)
        self.logger.debug("property: " + str(property))
        self.logger.debug("value: " + str(value))
        # first make sure the property is a valid one.
        if property.lower() not in self.validationDict.keys():
            msg = 'Trying to populate the attribute: (' + str(property) + \
                  ') to the current neticaNode.  Unfortunatly this is ' + \
                  'not a valid property!  Valid properties are:' + \
                  ','.join(self.validationDict.keys()) 
            raise ValueError, msg
        else:
            validTypes = self.validationDict[property.lower()]
            if validTypes:
                # doing type conversion of the value if the property
                # contains boolean values
                if type(validTypes[0]) is bool and type(value) is str:
                    #print 'Type is boolean'
                    self.logger.debug("Type is boolean")
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                if value not in self.validationDict[property.lower()]:
                    msg = 'Trying to populate the property: (' + str(property) + \
                          ') with the value: (' + str(value) + ').  Unfortunatly ' +\
                          'this is not a valid value for this property!  ' + \
                          'valid values include: ('  + \
                          ','.join(map(str, self.validationDict[property.lower()])) + ')'
                    raise ValueError, msg
            else:
                if value[len(value) - 1] == ')' and value[0] == '(':
                    value = value[:len(value) - 1]
                    value = value[1:]
                    value = re.split('\s*,\s*', value)
                elif value[len(value) - 1] == '"' and value[0] == '"':
                    value = value[:len(value) - 1]
                    value = value[1:]
            #print 'property:', property
            #print 'value:', value
            self.logger.debug("property: " + str(property))
            self.logger.debug("value: " + str(value))
            setattr(self, property, value)
    
class neticaEdge(object):
    
    def __init__(self):
        pass
    
class FuncTable(object):
    
    def __init__(self, parentColumns, outcomeValues, parentValues):
        self.parentColumns = parentColumns
        self.outcomeValues = outcomeValues
        self.parentValues = parentValues
           
class ProbsValueTable(object):
    '''
    This class is designed to store a junction table.  A junction
    takes all the possible values from a source or parent table and
    identifies how these different combinations of values translate
    into probabilities for a new set of values.  
    
    So a parent table (table 1.) might look like this:
    
    rating  |  type
    ------------------
    High    | Caribou
    High    | Moose
    Medium  | Caribou
    Medium  | Moose
    Low     | Caribou
    Low     | Moose
    
    The junction table is used to help describe how a set of 
    values above might impact Predator Density.  So that said
    the possible outcomes are described below:
    
    Predator Density:
    (High, Moderate, Low)
    
    so a junction table could end up looking like this:
    
    rating    | type    ->    PredDensity (high) | PredDensity (moderate) | PredDensity (low)
    ------------------------------------------------------------------------------------------
    High      | Caribou ->        70%            |          10%           |   20%
    High      | Moose   ->        60%            |          20%           |   20%
    Medium    | Caribou ->        60%            |          30%           |   10%
    etc...
    
    This class is an object model to help store this information.
        
    :ivar parentColumns: This is a list of the parent columns.  When 
                         values are added to this object references to 
                         input parent values will have the same order
                         as the columns described here.
    :ivar states: This is a list of the different values the node
                  that contains this table may take on.  When values
                  are added to this table they will include the probabiliitis
                  of these different states being realized.  The order
                  of the values added to this table must be in the same
                  order as the states are in when they are assigned in 
                  the constructor.
    :ivar valueStruct: 
    '''
    logger = None
    
    def __init__(self, states, parentColumns=None):
        '''
        States are the possible states that are going to be stored
        in this object.  Later on we will assign values to these
        possible states.  The values corresond with probabilities
        of each given state.
        
        The parent columns are the columns that the various parent
        values line up with.
        '''
        self.__initLogging()
        self.states = states
        self.parentColumns = parentColumns
        self.valueStruct = []
        self.parentValueStruct = []
        self.struct = {}
        
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
        
    def setRootValues(self, likelyHoodTable=None):
        '''
        This type of probability table has no priors.  It describes only 
        the likelyhoods of each of the states upon initiation of this node.
        
        Examples: 
            probs = 
        // Peach        Lemon        
          (0.8,         0.2);
        '''
        if likelyHoodTable:
            self.valueStruct = likelyHoodTable
        else:
            probValue =  1.0 / len(self.states)
            self.valueStruct = [probValue]
            self.valueStruct = self.valueStruct * len(self.states)
            print 'valueStruct', self.valueStruct
        
    def getLikelyHoodTable(self):
#         if not self.valueStruct:
            
        return self.valueStruct
    
    def getParentValuesTable(self):
        return self.parentValueStruct
            
    def setValues(self, likelyHoodTable, parentValuesTable):
        '''
        Takes a likelyhood table that is a list of lists, and the 
        parent values table that is also a list of lists and enters
        them into a data structure in this class.  This class then 
        has methods and properties that make retrieval of this 
        information into a bayesian framework easier.
        
        If information exists in the struct it gets over 
        written
        '''
        # first verify that they both contain the same number of
        # rows
        self.logger.debug("likelyHoodTable: " + str(likelyHoodTable))
        self.logger.debug("parentValuesTable: " + str(parentValuesTable))

        #print 'likelyHoodTable', likelyHoodTable
        #print 'parentValuesTable', parentValuesTable
        
        likelyHoodLength = len(likelyHoodTable)
        parentValLength = len(parentValuesTable)
        
        if likelyHoodLength <> parentValLength:
            errMsg = 'The number of values in the probability table need ' + \
                     'to the identical to the number of values in the ' + \
                     'parent value table.\n Parent Values Length: ' + \
                     str(parentValLength) + '\n Probability Tables Length: ' + \
                     str(likelyHoodLength) + ' '
            raise ValueError, errMsg
        
        self.valueStruct = likelyHoodTable
        self.parentValueStruct = parentValuesTable
        # end here!  but leaving the code below which allows you 
        # to create a dictionary for rapid access of probabilites 
        # for a given set of parent values.
        
        # now combine these values into a dictionary
#         rowCnt = 0
#         while rowCnt < len(likelyHoodTable):
#             dictKeyList = parentValuesTable[rowCnt]
#             probsForKey = likelyHoodTable[rowCnt]
#             startDict = self.struct
#             print 'startDict', startDict
#             for key in parentValuesTable[rowCnt]:
#                 print 'key', key
#                 if not startDict.has_key(key):
#                     startDict[key] = {}
#                 # is this the last key?
#                 if key == parentValuesTable[rowCnt][len( parentValuesTable[rowCnt]) - 1]:
#                     startDict[key] = likelyHoodTable[rowCnt]
#                 else:
#                     startDict = startDict[key]
#             
#             rowCnt += 1
#         print 'self.struct', self.struct
        self.logger.debug("finished")
        
 
            
class netica2OpenBayes(object):
    '''
    This class provides the glue between the neticaNet class and the 
    data that will be stored in that object and the movement of that
    data out of that object into the openBayes bbn classes.
    '''
    
    def __init__(self, neticaNetObj):
        self.__initLogging()
        self.neticaNetwork = neticaNetObj
        self.OpenBayesNetwork = None
        self.OpenBayesNodesDict = {}
        
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

        
    def loadData(self):
        self.__createNetwork()
        self.__loadVerticies()
        self.__loadEdges()
        self.OpenBayesNetwork.InitDistributions()
        self.__loadDistributions()
        
    def __loadDistributions(self):
        '''
        This is where things start to get a bit tricky!
        
        Step 1. Load get the root nodes, they have no dependencies
                so its just a matter of loading the probability 
                tables to the network
                
        Step 2. 
        '''
        for rootNodeName in self.neticaNetwork.getRootNodeNames():
            self.logger.debug("RootNodeName: " + str(rootNodeName))
            neticaNode = self.neticaNetwork.getNode(rootNodeName)
            self.logger.debug("neticaNode: " + str(neticaNode))
            # now get the type.  If the type is 'DECISION' 
            # then assume equal proability across all values.
            
            
            probTab = neticaNode.getProbabilityTable()
            self.logger.debug("Probability Table:" + str(probTab))
            likelyHoodTable = probTab.getLikelyHoodTable()
            openBayesVertex = self.OpenBayesNodesDict[rootNodeName]
            openBayesVertex.setDistributionParameters(likelyHoodTable)
        
        for nodeName in self.neticaNetwork.getNonRootNodeNames():
            neticaNode = self.neticaNetwork.getNode(rootNodeName)
            openBayesVertex = self.OpenBayesNodesDict[nodeName]
            parentLookup = self.__assembleParentLookup(neticaNode)
            parentNames = neticaNode.getParentNames()
            probTab = neticaNode.getProbabilityTable()
            likelyhoods = probTab.getLikelyHoodTable()
            parentValues = probTab.getParentValuesTable()
            distributionDict = {}
            for parentName in parentNames:
                
                openBayesVertex.distribution[{}]
            
        
        for nodeName in self.OpenBayesNodesDict.keys():
            neticaNode = self.neticaNetwork.getNode(nodeName)
                        
    def __assembleParentLookup(self, neticaNode):
        lut = {}
        parentNames = neticaNode.getParentNames()
        for parentName in parentNames:
            parentNode = self.neticaNetwork.getNode(parentName)
            values = parentNode.getStates()
            if not lut.has_key(parentName):
                lut[parentName] = {}
            valueCnt = 0 
            for value in values:
                lut[parentName][value] = valueCnt
                valueCnt += 1
        return lut
               
    def __loadEdges(self):
        '''
        spiders its way through the nodes adding the 
        connections / relationships between nodes (edges)
        '''
        nodeNames = self.neticaNetwork.getRootNodeNames()
        self.logger.debug("nodeNames: " + str(nodeNames))
        for nodeName in nodeNames:
            node = self.neticaNetwork.getNode(nodeName)
            parentNodeNames = node.getParentNames()
            for parentNodeName in parentNodeNames:
                #parentNode = self.neticaNetwork.getNode(parentNodeName)
                srcVertex = self.OpenBayesNodesDict[nodeName]
                destVertex = self.OpenBayesNodesDict[parentNodeName]
                edge = OpenBayes.DirEdge(len(self.OpenBayesNetwork.e), srcVertex, destVertex)
                self.OpenBayesNetwork.add_e(edge)
        
    def __loadVerticies(self):
        '''
        Iterates through the nodes contained by the 
        netica network object and creates OpenBayes 
        network nodes
        '''
        for nodeName in self.neticaNetwork.getAllNodeNames():
            nodeObj = self.neticaNetwork.getNode(nodeName)
            isDiscrete = nodeObj.isDiscrete()
            if isDiscrete:
                states = len(nodeObj.getStates())
            else:
                states = 0 # this value is not used if the data is not discrete.
            self.logger.debug("states: " + str(states))
            self.logger.debug("nodeName: " + str(nodeName))
            self.logger.debug("isDiscrete: " + str(isDiscrete) )
            openBayesVertex = OpenBayes.BVertex(nodeName, isDiscrete, states)
            self.OpenBayesNodesDict[nodeName] = self.OpenBayesNetwork.add_v(openBayesVertex)
        
        
    def __createNetwork(self):
        '''
        Extracts the network name from the neticaNetwork 
        object and creates an openBayes network from it.
        '''
        netName = self.neticaNetwork.getName()
        self.OpenBayesNetwork = OpenBayes.BNet(netName)
        
        
        
        
        
    



        
        
        
        
        
 
        
    