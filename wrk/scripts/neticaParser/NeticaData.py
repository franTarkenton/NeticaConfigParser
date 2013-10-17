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
import warnings

import OpenBayes


class neticaNet(object):
    '''
    This is the actual network.  This object will be composed
    of Nodes and Edges.  It contains various methods that should
    make it easy to extract the necessary information.
    
    
    :ivar name: The name of the Bayes Belief Network
    :ivar nodeDict: A dictionary that contains all the nodes that 
                    are members of this network.
    :ivar rootNodes: Contains all the root nodes, (nodes without 
                     parents) This object will get populated the 
                     first time the root nodes are requested.  Then 
                     subsequent requests will just return the contents
                     of this list.
    '''
    def __init__(self):
        self.__initLogging()
        self.name = None
        self.rootNodes = []
        self.nodeDict = {}
        
    def __initLogging(self):
        '''
        sets up logging for this class.
        '''
        # This code is here just cause I like to have my log messages contain
        # Module.Class.Function for each message.  If you don't care too much about what 
        # you log messages look like in the log file, you can bypass this.
        curFile = inspect.getfile(inspect.currentframe())  
        if curFile == '<string>':
            curFile = sys.argv[0]
        logName = os.path.splitext(os.path.basename(curFile))[0] + '.' + self.__class__.__name__
        # and this line creates a log message
        self.logger = logging.getLogger(logName)
    
    
    def setName(self, name):
        '''
        Sets the name of this BBN.
        
        :param  name: the name of the BBN
        :type name: str
        '''
        self.name = name
        
    def getName(self):
        '''
        Returns the name of this BBN.       
        
        :returns: The name of the BBN
        :rtype: str
        '''
        return self.name
        
    def newNode(self, name):
        '''
        creates a new node, and assigns it the given name.  The node
        exists at this point, but it does not contain any information.
        
        :param  name: The name of the NeticaNode that is to be created
                      and added to this network.
        :type name: str
        
        :returns: returns a NeticaNode object that was just created.
        :rtype: NeticaNode
        '''
        nodeObj = neticaNode()
        nodeObj.setName(name)
        self.nodeDict[name] = nodeObj
        return self.nodeDict[name]
        
    def getRootNodeNames(self, recalc=True):
        '''
        Returns a list of the node names that form the start
        of this network.  In other words the nodes that do 
        not have any parents.
        
        :param  recalc: If this value is set to be true, then even 
                        if the rootnodes were previously calculated 
                        it forces the recalculation of them.  You would
                        want to do this if you have previously requested
                        root nodes, and then subsequently added nodes
                        to the dictionary that may be root nodes.
        :type recalc: boolean
        '''
        rootNodes = []
        if not self.rootNodes or recalc:
            for nodekey in self.nodeDict.keys():
                nodeObj = self.nodeDict[nodekey]
                parents = nodeObj.getParentNames()
                #print 'parents are:', parents
                if not nodeObj.getParentNames():
                    #print 'root:',  nodekey
                    rootNodes.append(nodekey)
        return rootNodes
                    
    def getAllNodeNames(self):
        '''
        Returns a list of strings that contains the names 
        of all the nodes that make up this network
        
        :returns: a list of strings that are the names of all the nodes that 
                 make up the this network.
        :rtype: list(str)
        '''
        return self.nodeDict.keys()
    
    def getNonRootNodeNames(self):
        '''
        Returns the name of non root nodes, in other words 
        returns all the nodes from this network that have parents
        
        :returns: a list of strings that contains all the non root nodes 
                  that make up this network
        :rtype: list(str)
        '''
        rootNodeNames = self.getRootNodeNames()
        print 'root nodes:', rootNodeNames
        allNodeNames = self.getAllNodeNames()
        nonRootNodes = [item for item in allNodeNames if item not in rootNodeNames]
        print 'nonRootNodes', nonRootNodes
        return nonRootNodes
                
    def getChildNodeNames(self, nodeName):
        '''
        Give the name of a node, this method will return a list 
        of strings containing the names of the parents to this 
        node.
        
        :param  nodeName: the input node who's parent nodes you would
                          like to retrieve
        :type nodeName: str
        
        :returns: a list of strings that contains the names of the nodes
                  that are parents of the node provided as an arg to this 
                  method
        :rtype: list(str)
        '''
        retNodes = []
        for nodeKey in self.nodeDict.keys():
            nodeObj = self.nodeDict[nodeKey]
            parentNames = nodeObj.getParentNames()
            if nodeName in parentNames:
                retNodes.append(nodeKey)
        return retNodes
                    
    def getChildNodes(self, nodeName):
        '''
        Given the name of a node, this method will return a list of 
        neticaNode objects that are parents to the node name that was 
        provided
        
        :param  nodeName: The name of the node who's parent node objects 
                          you want returned
        :type nodeName: str
        
        :returns: a list of neticaNode objects that are going to be returned.
        :rtype: list(neticaNode)
        '''
        parentNodeName = self.getChildNodeNames(nodeName)
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

class neticaNode(object):
    '''
    This class is used to store information about a neticaNode. Most
    of the properties correspond with the properties that define a 
    node inside of a dnet file.  Values of various properties
    get validated using the validation dictionary.
    
    If you are wondering about any of the terms described below
    see the netica glossary.  The terms are all copied directly
    from the netica dnet file.
    
    :ivar chance: Identifies if the node is "Deterministic" or "Nature"
                  meaning its value can only be inferred as a probability 
                  distribution over possible values. 
    :ivar discrete: Boolean value that identifies if a node
                    is discrete or not.
    :ivar funcTable: if the node contains a function table 
                     this is the property that it will get 
                     stored in.!
    :ivar kind: one of the following values:
               ['NATURE', 'DECISION', 'UTILITY', 'CONSTANT']!
    :ivar logger: The logging object
    :ivar name: The nodes name
    :ivar parents: a list of the parent node names
    :ivar probabilityTable: Contains a ProbsValueTable
                            object.
    :ivar states: a list of values containing the possible
                  states that the node can assume.
    :ivar validationDict: a dictionary that is used to verify most
                          most of the properties described above.
    '''
    
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
        self.levels = None
        self.validationDict = self.__getValidationDict()
        self.valueMap = self.__getValueMap()
    
    def __initLogging(self):
        '''
        sets up logging for this class.
        '''
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
        '''
        Gets the parent names for the current node
        
        :returns: a list of strings containing the names of the parent 
                  nodes
        :rtype: list(neticaNode)
        '''
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
        '''
        Sets the name for the node object
        
        :param  name: string containing the name you wish to assign to the 
                      current node object
        :type name: string
        '''
        self.name = name
        self.logger.debug("name is: " + str(name))
        
    def getName(self):
        return self.name
        
    def isDiscrete(self):
        '''
        Returns a boolean value indicating whether the current node is 
        discrete or not.       
        
        :returns: A boolean value indicating whether the current node is 
                  discrete or not
        :rtype: boolean
        '''
        return self.discrete
            
    def getStates(self):
        '''
        Returns the a list containing all the possible states of the
        current node        
        
        :returns: a list containing the different states that this node
                  can take on.
        :rtype: list
        '''
        retVal = None
        if self.states:
            return self.states
        if self.statetitles:
            return self.statetitles
        return self.states
        
    def getLevels(self):
        return self.levels
        
    def __getValueMap(self):
        '''
        It has been discovered that there can be two different names for some
        attributes within a netica node.  At the time of this writing have only
        discovered one, however it is anticipated that more will be comming.
        
        The example is the attribute "states" can also be labelled as "statetitles"
        Both attributes serve the same purpose.  
        
        This method will return an attribute map that describes the input label, 
        and the output attribute.
        '''
        # make sure all values are lower case.
        # TODO: write check that ensures and converts any values in this table to lower case as well as their values
        valueMap = {'states':'states', 
                    'statetitles': 'states'}
        return valueMap
    
    def __getValidationDict(self):
        '''
        returns a dictionary that contains the information used to 
        validate valid attributes of this object.  If the corresponding
        value is a None value it indicates there is no value checking 
        on this attribute type. 
        
        all types are in lower case
        
        :returns: dictionary containing validation information
        :rtype: python dictionary
        '''
        # all keys should be entered in lower case
        # TODO: should write a validation method that converts any non lower case keys to lower case.
        validationDict = {'name': None, 
                          'states': None,
                          'statetitles':None,
                          'kind': ['NATURE', 'DECISION', 'UTILITY', 'CONSTANT'], 
                          'chance': ['DETERMIN', 'CHANCE'], 
                          'parents': None, 
                          'probs': None,
                          'belief': None,
                          'numcases':None,
                          'discrete': [True, False],
                          'title': None, 
                          'functable': None,
                          'levels': None,
                          'comment': None,
                          'whenchanged':None,
                          'eqndirty': [True, False],
                          'measure':['RATIO', 'NOMINAL', 'LOCAL', 'ORDINAL', 'INTERVAL']}
        return validationDict
        
    def setProbabilityTable(self, neticaProbabilityTable):
        '''
        sets the probability table for the current node.  Recieves a ProbsValueTable
        and assigns it to the property probabilityTable
        
        :param  neticaProbabilityTable: a netica probability table
        :type neticaProbabilityTable: ProbsValueTable
        '''
        self.probabilityTable = neticaProbabilityTable
        self.logger.debug("node name is: " + str(self.name))
        self.logger.debug("prob table: " + str(neticaProbabilityTable))
        self.logger.debug("likelyhoods in the table are: " + str(neticaProbabilityTable.getLikelyHoodTable()))
      
    def getProbabilityTable(self):
        '''
        returns the probability table associated with this node.
        
        
        :returns: probability table
        :rtype: ProbsValueTable
        '''
        #print 'kind', self.kind
        if not self.probabilityTable and self.kind.upper() <> 'UTILITY':
            warnMsg = 'There is no probability table for the node "' + \
                      str(self.name) + '" Going to create one with ' + \
                      'equal probabilities for each entry '
            self.logger.warning(warnMsg)
            self.__makeProbabilityTable()
        return self.probabilityTable
    
    def getFunctionTable(self):
        return self.funcTable
    
    def __makeProbabilityTable(self):
        '''
        Creates a probability table with equal probabilities for each 
        of the possible states of that the node can assume.
        '''
        # create the probabiltiy table with an equal value for each
        # state.  
        # think about what to do with parent nodes
        self.probabilityTable = ProbsValueTable(self.states)
        self.probabilityTable.setRootValues()
      
    def setFunctionTableObject(self, funcTable):
        '''
        Recieves a netica function table object.  Drops this information
        into the nodes funcTable parameter.
        
        :param  funcTable: a function table. Function tables are like a 
                           junction tree.  They are used by netica software, at
                           the conclusion of a belief network.  They identify 
                           what the final state is depending on what the parent
                           nodes states are.
        :type funcTable: FuncTable
        '''
        self.funcTable = funcTable
        self.logger.debug('func table is: ' + str(funcTable))
    
    def enterAndValidateSimpleAttribute(self, property, value):
        '''
        Recieves two values.  The first is the name of the property, and the 
        second is the value that is to be assigned to it.  This method will 
        validate the property, and the value against information contained in
        the validation dictionary. (self.validationDict) 
        
        :param  property: name of the property that is to be populated
        :type property: string
        :param  value: the value that goes with the property
        :type value: (various)
        '''
        # TODO: Remove this condition, only in place for debugging
        if property.lower() == 'parents':
            print '(parent debugging) property', property
            print '(parent debugging) value', value
        #property = property.lower()
        #value = value.lower()
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
            #validTypes = self.validationDict[property.lower()]
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
                #if value not in self.validationDict[property.lower()]:
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
                    #print 'value 1: (', value, ')'
                    value = re.split('\s*,\s*', value)
                    if value:
                        value = self.__removeExtraneousQuotes(value)
                    #print 'value 2: ', value
                elif value[len(value) - 1] == '"' and value[0] == '"':
                    value = value[:len(value) - 1]
                    value = value[1:]
            #print 'property:', property
            #print 'value:', value
            self.logger.debug("property: " + str(property))
            self.logger.debug("value: " + str(value))
            setattr(self, property, value)
            
            # if the property has a value in the valueMap
            # then write the value to the other property also
            if self.valueMap.has_key(str(property.lower())):
                newProp = self.valueMap[property]
                setattr(self, newProp, value)
                
    def __removeExtraneousQuotes(self, value):
        '''
        When converting data from the netica file to the neticaData api that has been 
        created, you can wind up in the situation where string values include the quotes
        that were used to define them. For example see the list below: 
        
            ['"None"', '"Low"', '"Moderate-low"', '"Moderate-high"', '"High"']
            
        This method will iterate through each element in the list looking at the 
        first character and the last character in each element.  If they are both
        equal to a quote character then they are removed.
        
        :param  value: Input list which may or may not have quotes embedded into list 
                       elements.
        :type value: list
        
        :returns: a list where embedded quotes in each of the elements have been 
                  removed.  Other than that the list should remain unchanged.
        :rtype: list
        '''
        #print 'startVal:', value
        valCnt = 0
        while valCnt < len(value):
            if len(value[valCnt]) > 0:
                if value[valCnt][0] == '"' or value[valCnt][0] == "'":
                    value[valCnt] = value[valCnt][1:]
                if value[valCnt][len(value[valCnt]) - 1] == '"' or value[valCnt][len(value[valCnt]) - 1] == "'":
                    value[valCnt] = value[valCnt][:len(value[valCnt]) - 1]
            valCnt += 1
        #print 'retVal:', value
        return value
    
class neticaEdge(object):
    '''
    Created this class as it may be useful down the road.  For now it is 
    not used.  Instead edges are derived from parent values of each node / 
    vertex in the network
    
    '''
    def __init__(self):
        pass
    
class FuncTable(object):
    
    def __init__(self, parentColumns, outcomeValues, parentValues, levels, states):
        self.parentColumns = parentColumns
        self.outcomeValues = outcomeValues
        self.parentValues = parentValues
        self.levels = levels
        
    def getLikelyHoodTable(self):
        '''
        atribLoL ([], ['LU_hazard', 'Population_risk'])
        parentColumns ['LU_hazard', 'Population_risk']
        outcomeValues ['#0', '#1', '#2', '#3', '#4', '#1', '#1', '#2', '#3', '#4', '#2', '#2', '#2', '#3', '#4', '#3', '#3', '#3', '#3', '#4', '#4', '#4', '#4', '#4', '#4']
        parentValues [['None', 'None'], ['None', 'Low'], ['None', 'Moderate-low'], ['None', 'Moderate-high'], ['None', 'High'], ['Low', 'None'], ['Low', 'Low'], ['Low', 'Moderate-low'], ['Low', 'Moderate-high'], ['Low', 'High'], ['Moderate-low', 'None'], ['Moderate-low', 'Low'], ['Moderate-low', 'Moderate-low'], ['Moderate-low', 'Moderate-high'], ['Moderate-low', 'High'], ['Moderate-high', 'None'], ['Moderate-high', 'Low'], ['Moderate-high', 'Moderate-low'], ['Moderate-high', 'Moderate-high'], ['Moderate-high', 'High'], ['High', 'None'], ['High', 'Low'], ['High', 'Moderate-low'], ['High', 'Moderate-high'], ['High', 'High']]
        '''
        # characters to remove
        leadingCharsToDel = ['#']
        skipVals = ['@imposs']
        allProbs = []
        for outcome in self.outcomeValues:
            for char2Del in leadingCharsToDel:
                if outcome[0] == char2Del:
                    outcome = outcome[1:]
                    break
            skip = False
            for skipVal in skipVals:
                if skipVal == outcome:
                    skip = True
                    break
            if skip:
                continue
            # if there is a levels value then the values indicate levels
            # otherwise they are something else
            # ASSUMING THE SOURCE NODE IS NATURE, MORE CODE REQUIRED HERE.  FUNCTION TABLE
            # COULD ALSO BE UTILIITY
            print 'outcome', outcome
            probs = [0] * len(self.levels)
            probs[int(outcome)] = 1
            allProbs.append(probs)
        return allProbs
    
    def getParentValuesTable(self):
        return self.parentValues
        
    def printTable(self):
        print 'parentColumns', self.parentColumns
        print 'outcomeValues', self.outcomeValues
        print 'parentValues', self.parentValues
           
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
#         self.struct = {}
        
    def __initLogging(self):
        '''
        Sets up logging for the current method.
        '''
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
        This method is used to assign probability tables that have no 
        priors / parents.
        
        It describes only the likelyhoods of each of the states upon initiation
        of this node.
        
        Examples: 
            probs = 
        // Peach        Lemon        
          (0.8,         0.2);
        
        :param  likelyHoodTable: a python list containing the probabilities of 
                                 each state associated with the the node.  If 
                                 no likelyhood table is provided then the method
                                 will assign equal probabilities for each possible
                                 state of the node.
        :type likelyHoodTable: list
        '''
        if likelyHoodTable:
            self.valueStruct = likelyHoodTable
        else:
            probValue =  1.0 / len(self.states)
            self.valueStruct = [probValue]
            self.valueStruct = self.valueStruct * len(self.states)
            #print 'valueStruct', self.valueStruct
        
    def getLikelyHoodTable(self):
        '''
        Returns the probability table
        
        
        :returns: a probability table
        :rtype: 2d list
        '''
#         if not self.valueStruct:
        return self.valueStruct
    
    def getParentValuesTable(self):
        '''
        Returns the parent values for the probability table.  parent values are a
        2d list.  Each internal list describes one set of possible values from the 
        parent values.
        
        The number of elements in each internal list should be the same as the number
        of values contained in the nodes parent property.  The number of inner lists 
        should be the same as the number of inner lists in the likelyhood table.
        
        :returns: a 2d list containing all the possible parent input values
        :rtype: 2d list
        '''
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
        
        :param  likelyHoodTable: a 2d list containing the likelyhoods of various
                                 states of the current node, given a set of values
                                 in the parent nodes.
        :type likelyHoodTable: 2d list
        :param  parentValuesTable: a 2d list containing the possible parent values
        :type parentValuesTable: 2d list
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
    
    :ivar OpenBayesNetwork: This is an OpenBayes.BNet object.  When 
                            the loadData method is complete it should contain
                            the information that was described in the NeticaNet 
                            object that was provided to the constructor.
    :ivar OpenBayesNodesDict: This is a dictionary that contains references to all
                              the various netica verticies.  Makes it easier to 
                              populate them with information by storing them in 
                              this dictionary.
    :ivar logger: The logging object.  Where log messages should be written to.
    :ivar neticaNetwork: The neticaNet object that contains the bayes network 
                         information.  The information contains in this object
                         will be extracted and entered into the openbayes object
    '''
    
    def __init__(self, neticaNetObj):
        self.__initLogging()
        self.neticaNetwork = neticaNetObj
        self.OpenBayesNetwork = None
        self.OpenBayesNodesDict = {}
        
    def __initLogging(self):
        '''
        setting up the logging environement for the method.
        '''
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
        '''
        This method will extrac the information out of the neticaNet object
        and create an OpenBayes Bayes net object.  To retrieve the openbayes
        object use the method getOpenBayesNetwork(
        '''
        self.__createNetwork()
        self.__loadVerticies()
        self.__loadEdges()
        self.OpenBayesNetwork.InitDistributions()
        self.__loadDistributions()
        
    def __loadDistributions(self):
        '''
        When this method is called the OpenBayes network will have been created, 
        The nodes will have been created, and the edges will have been defined.  This
        method will take the likelyhood values parse them and load them to the 
        openbayes network.
        
        Once this is complete the network should have the necessary values to 
        allow you to perform the various bayesian inferences, and other statistical
        methods on it.
        '''
        # entering distributions for root nodes is different than
        # how you enter nodes that have parents.
        for rootNodeName in self.neticaNetwork.getRootNodeNames():
            self.logger.debug("RootNodeName: " + str(rootNodeName))
            neticaNode = self.neticaNetwork.getNode(rootNodeName)
            self.logger.debug("neticaNode: " + str(neticaNode))
            # now get the type.  If the type is 'DECISION' 
            # then assume equal proability across all values.
            
            
            probTab = neticaNode.getProbabilityTable()
            self.logger.debug("Probability Table - parentColumns:" + str(probTab.parentColumns))
            self.logger.debug("Probability Table - valueStruct:" + str(probTab.valueStruct))
            self.logger.debug("Probability Table - parentValueStruct:" + str(probTab.parentValueStruct))
            self.logger.debug("Probability Table - states:" + str(probTab.states))

            likelyHoodTable = probTab.getLikelyHoodTable()
            openBayesVertex = self.OpenBayesNodesDict[rootNodeName]
            openBayesVertex.setDistributionParameters(likelyHoodTable)
        
        # Entering the distribution tables for non root nodes.
        nonRootNodeNames = self.neticaNetwork.getNonRootNodeNames()
        #print 'nonRootNodeNames:', nonRootNodeNames
        for nodeName in nonRootNodeNames:
            neticaNode = self.neticaNetwork.getNode(nodeName)
            openBayesVertex = self.OpenBayesNodesDict[nodeName]
            parentLookup = self.__assembleParentLookup(neticaNode)
            parentNames = neticaNode.getParentNames()
            probTab = neticaNode.getProbabilityTable()
            funcTab = neticaNode.getFunctionTable()
            print 'nodeName:', nodeName
            if funcTab:
                print 'loading the func table'
                likelyhoods = funcTab.getLikelyHoodTable()
                parentValues = funcTab.getParentValuesTable()
            elif probTab:
                likelyhoods = probTab.getLikelyHoodTable()
                parentValues = probTab.getParentValuesTable()
            
            else:
                likelyhoods = None
                parentValues = None
#             print 'nodeName', nodeName
#             print 'parentNames', parentNames
#             print 'likelyhoods', likelyhoods
#             print 'parentValues', parentValues
#             print 'lut:', parentLookup
            if parentValues and likelyhoods:
                counter = 0
                for parentList in parentValues:
                    parentValCnter = 0
                    dictRef = parentLookup
                    dict2Make = {}
                    for parentVal in parentList:
                        #print 'parentVal:', parentVal
                        #print 'srcColumn:', parentNames[parentValCnter]
                        #print 'position:', parentLookup[ parentNames[parentValCnter]][parentVal]
                        dict2Make[parentNames[parentValCnter]] = parentLookup[ parentNames[parentValCnter]][parentVal]
                        #dictRef = dictRef[parentVal]
                        parentValCnter += 1
                    #print 'dict2Make', dict2Make, likelyhoods[counter]
                    #print 'position:', dictRef
                    #print 'likelyhood', likelyhoods[counter][dictRef]
                    
                    # now enter into openbayes node
                    openBayesVertex.distribution[dict2Make] = likelyhoods[counter]
                    counter += 1
            '''
            Entering distributions for nodes/verticies that have them.  Netica supports
            decision nodes / utility nodes.  For these types of entries if there are no 
            parents then assume an equal distribution accross the possbile states.  
            
            If has parents, I think its just ignored.  Entered as a vertex in openbayes
            but no probabilities are assigned.  I think openbayes will autocalculate them
            for us?  Not sure though?
            
            the networks that are being modelled for cumulative effects are unlikely to 
            have decision nodes.
            
            '''
             
    def __assembleParentLookup(self, neticaNode):
        '''
        The neticaNet object is made up of nodes.  Nodes contain probability
        tables (ProbsValueTable).  The probability tables are made up of two
        lists of information:
        
        The first is 2d list containing the likelyhoods of the various states
        that the node can be in, given various values from the parent nodes.
        example:
        
        [[1.0, 0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0, 0.0],
         [0.0, 0.9, 0.1, 0.0],
         [0.0, 0.4, 0.6, 0.0],
         [0.0, 0.8, 0.2, 0.0],
         [0.0, 0.1333333, 0.5333334, 0.3333333],
         [0.0, 0.9, 0.1, 0.0],
         [0.0, 0.4, 0.6, 0.0]]
        
        The second is a 2d list containing the parent values. example:
        
        [['NoTest', 'Peach'], 
         ['NoTest', 'Lemon'], 
         ['Steering', 'Peach'], 
         ['Steering', 'Lemon'], 
         ['Fuel_Elect', 'Peach'], 
         ['Fuel_Elect', 'Lemon'], 
         ['Transmission', 'Peach'], 
         ['Transmission', 'Lemon']]
        
        Probability tables also have a property called parentColumns,
        example:
        
        [T1, CC]
        
        And finally there are the states associated with the node:
        [NoResult, NoDefects, OneDefect, TwoDefects]
        
        So putting this together the first element in the likelyhood table:
        [1.0, 0.0, 0.0, 0.0] and the first element in the parent value
        table ['NoTest', 'Peach'] tells us there is a 100% likelyhood that this
        nodes state is equal to NoResult if the parent T1 is equal to 'NoTest',
        and the parent CC is equal to 'Peach'
        
        So to get this information into the openBayes framework we need to
        forget about the actual values comming from the parents and instead 
        figure out what the position of that value is in the state property of
        that node.  
        
        This object will construct a dictionary.  The first value of the dictionary
        is the name of the parent, the second element is the possible value from the
        parent, and the value that is associated with the name of the parent and
        the possible state value is the index positon of that state.
        
        Thus given the parent 'CC' and the state 'Lemon' the dictionary should 
        have a value of 1.   
        
        This dictionary makes it easy to put assemble the probability tables 
        into the openbayes framework.
        
        :param  neticaNode: the neticaNode object that we want to extract the probability
                            information from.
        :type neticaNode: neticaNode
        
        :returns: a python dictionary that can be used as a lookup to figure out a 
                  states index position given its parent and the state value.
        :rtype: python dictionary
        '''
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
        spiders its way through the netica nodes adding the 
        connections / relationships between nodes (edges)
        
        Uses the nodes parent property to determine what nodes
        / verticies the edge should connect.
        '''
        #nodeNames = self.neticaNetwork.getRootNodeNames()
        nodeNames = self.neticaNetwork.getAllNodeNames()
        self.logger.debug("root nodes in __loadEdges (" + str(nodeNames) + ')')
        #self.logger.debug("nodeNames: " + str(nodeNames))
        for nodeName in nodeNames:
            node = self.neticaNetwork.getNode(nodeName)
            childNodeNames = self.neticaNetwork.getChildNodeNames(nodeName)
            self.logger.debug("child of (" + str(nodeName) + ") are " + str(childNodeNames))
            for childNodeName in childNodeNames:
                #parentNode = self.neticaNetwork.getNode(parentNodeName)
                self.logger.debug("Adding an Edge from node (" + str(nodeName) + ") to node (" + str(childNodeName) + ')')
                srcVertex = self.OpenBayesNodesDict[nodeName]
                destVertex = self.OpenBayesNodesDict[childNodeName]
                edge = OpenBayes.DirEdge(len(self.OpenBayesNetwork.e), srcVertex, destVertex)
                self.OpenBayesNetwork.add_e(edge)
        
    def __loadVerticies(self):
        '''
        Iterates through the nodes that have been extract from the 
        netica network object and creates OpenBayes network nodes 
        from that information.
        '''
        for nodeName in self.neticaNetwork.getAllNodeNames():
            nodeObj = self.neticaNetwork.getNode(nodeName)
            isDiscrete = nodeObj.isDiscrete()
            if not isDiscrete:                
                warnMessage = 'The netica file has labelled the node (' + str(nodeName) + ') as not discrete however' + \
                              'it is likely being treated by netica as discrete and not continuous data. ' + \
                              'Going to treat it as if it is discrete data when it is loaded '  + \
                              'into the OpenBayes framework.  If this is an error, you should ' + \
                              'edit this portion of the loader module!' 
                              
                self.logger.warn(warnMessage)
                warnings.warn(warnMessage)
                isDiscrete = True
            if isDiscrete:
                states = len(nodeObj.getStates())
            else:
                states = 0 # this value is not used if the data is not discrete.
            self.logger.debug("states: " + str(states))
            self.logger.debug("nodeName: " + str(nodeName))
            self.logger.debug("isDiscrete: " + str(isDiscrete) )
            openBayesVertex = OpenBayes.BVertex(nodeName, isDiscrete, states)
            self.OpenBayesNodesDict[nodeName] = self.OpenBayesNetwork.add_v(openBayesVertex)
    
    def getOpenBayesNetwork(self):
        '''
        Returns an openbayes network object.  This is an bayesian
        belief network object that is derived from the patched version of
        the OpenBayes library which is available here:
        
        https://github.com/abyssknight/OpenBayes-Fork
        
        You likely want to run the loadData method first as that 
        method will populate the openbayes library with the information 
        contained in the DNET netica file.
               
        :returns: an OpenBayes BBN object
        :rtype: OpenBayes.BNet
        '''
        return self.OpenBayesNetwork
    
    def __createNetwork(self):
        '''
        Extracts the network name from the neticaNetwork 
        object and creates an openBayes network from it.
        '''
        netName = self.neticaNetwork.getName()
        self.OpenBayesNetwork = OpenBayes.BNet(netName)
        
        
        
        
        
    



        
        
        
        
        
 
        
    