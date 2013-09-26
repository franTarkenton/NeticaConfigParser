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
        

class neticaNode(object):
    
    def __init__(self):
        self.name = ''
        #self.type = None  # Node, Vertex, network, edge
        self.states = [] # These are the values associated with the node
        self.kind = None # Nature, Decision, Utility, Constant
        self.chance = None # deterministic probabilistic
        self.parents = [] # dependent nodes.  Root level will not have any parents, ie the bottom of the tree or the start of the network
        self.probabilityTable = []
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
                          'title': None}
        return validationDict
        
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
    
    
    