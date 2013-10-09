'''

This module classes to store the various pieces of information from 
the netica baysian models.  It should also provide an api that 
makes it easy to take the information out of this data model and 
put it into any bayes library / framework.

Created on Sep 23, 2013

@author: kjnether
'''
import re

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
        
    def getRootNodes(self, recalc=True): 
        if not self.rootNodes or recalc:
            for nodekey in self.nodeDict.keys():
                print nodekey

class neticaNode(object):
    
    def __init__(self):
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
    
    def setName(self, name):
        self.name = name
        
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
        
    def setFunctionTableObject(self, funcTable):
        '''
        
        '''
        self.funcTable = funcTable
    
    def enterAndValidateSimpleAttribute(self, property, value):
        property = property.lower()
        value = value.lower()
        valueIsList = False
        print 'property'.upper(), ' = ', str(property)
        print 'value'.upper(), ' = ', str(value)
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
                    print 'Type is boolean'
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
            print 'property:', property
            print 'value:', value
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
    
    def __init__(self, states, parentColumns=None):
        '''
        States are the possible states that are going to be stored
        in this object.  Later on we will assign values to these
        possible states.  The values corresond with probabilities
        of each given state.
        
        The parent columns are the columns that the various parent
        values line up with.
        '''
        self.states = states
        self.parentColumns = parentColumns
        self.valueStruct = []
        self.parentValueStruct = []
        self.struct = {}
        
    def setRootValues(self, likelyHoodTable):
        '''
        This type of probability table has no priors.  It describes only 
        the likelyhoods of each of the states upon initiation of this node.
        
        Examples: 
            probs = 
        // Peach        Lemon        
          (0.8,         0.2);
        '''
        self.valueStruct = likelyHoodTable
            
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
        print 'likelyHoodTable', likelyHoodTable
        print 'parentValuesTable', parentValuesTable
        
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
        
        
        
        
        
        
        
        
        
        
 
        
    