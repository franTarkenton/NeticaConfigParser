'''

This module classes to store the various pieces of information from 
the netica baysian models.  It should also provide an api that 
makes it easy to take the information out of this data model and 
put it into any bayes library / framework.

Created on Sep 23, 2013

@author: kjnether
'''

class neticaNet(object):
    '''
    This is the actual network.  This object will be composed
    of Nodes and Edges.
    '''
    def __init__(self):
        self.name = None
        self.rootNodes = []
        
        
        # nature, decision, utility, constant
        # 
        
        # chance - deterministic probableistic
        # deterministic - no randomness involved in determining future state
        # probablistic - likelyhood of something happening.
        
    def setName(self, name):
        self.name = name

class neticaNode(object):
    
    def __init__(self):
        self.type = None  # Node, Vertex, network, edge
        self.states = [] # These are the values associated with the node
        self.kind = None # Nature, Decision, Utility, Constant
        self.chance = None # deterministic probabilistic
        self.parents = [] # dependent nodes.  Root level will not have any parents, ie the bottom of the tree or the start of the network
        self.probabilityTable = []
        self.discrete = None # True or False
        pass
    
class neticaEdge(object):
    
    def __init__(self):
        pass
    
    
    