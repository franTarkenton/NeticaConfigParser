'''
Created on 2013-08-01

@author: kjnether
'''
# This is an attempt to figure out how to model the mule 
# deer model using the openbayes module.
#
import site
import sys

from OpenBayes import BNet, BVertex, DirEdge, JoinTree # @UnresolvedImport
dir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\scripts\deps\Lib\site-packages'
site.addsitedir(dir)  # @UndefinedVariable



network = BNet('Mule Deer Hazard')  # @UndefinedVariable

# create discrete node for all nodes with 2 states??
road_Density = network.add_v(BVertex('Road Density', True, 3))
unregulated_Hunting_Rate = network.add_v(BVertex('Unregulated Hunting Rate', True, 3))
cougar_risk_level = network.add_v(BVertex('Cougar Risk Level', True, 3))
wolfPresence = network.add_v(BVertex('Wolf Presence', True, 2))
predation_risk = network.add_v(BVertex('Predation Risk', True, 3))
population_hazard = network.add_v(BVertex('Population Hazard', True, 5))
proportion_of_lu_in_UWR = network.add_v(BVertex('Proportion of LU in UWR', True, 4))
uwr_hazard_rating = network.add_v(BVertex('UWR Hazard Rating', True, 5))
habitat_hazard_rating = network.add_v(BVertex('Habitat Hazard Rating', True, 5))
muleDeerHazardRating = network.add_v(BVertex('Mule Deer Hazard Rating', True, 5))
regulated_Hunting_Rate = network.add_v(BVertex('Regulated Hunting Rate', True, 3))
# now describe the connections
# population side of model
network.add_e(DirEdge(len(network.e), road_Density, unregulated_Hunting_Rate))
network.add_e(DirEdge(len(network.e), road_Density, predation_risk))
network.add_e(DirEdge(len(network.e), cougar_risk_level, predation_risk))
network.add_e(DirEdge(len(network.e), wolfPresence, predation_risk))
network.add_e(DirEdge(len(network.e), predation_risk, population_hazard))
network.add_e(DirEdge(len(network.e), unregulated_Hunting_Rate, population_hazard))
network.add_e(DirEdge(len(network.e), regulated_Hunting_Rate, population_hazard))
network.add_e(DirEdge(len(network.e), population_hazard, muleDeerHazardRating))

# habitat side of model
network.add_e(DirEdge(len(network.e), proportion_of_lu_in_UWR, habitat_hazard_rating))
network.add_e(DirEdge(len(network.e), uwr_hazard_rating, habitat_hazard_rating))
network.add_e(DirEdge(len(network.e), habitat_hazard_rating, muleDeerHazardRating))

network.InitDistributions()
#                                         <1km   /  1-2km  /   2-3km
# road_Density.setDistributionParameters([0.3333333,   0.3333333,   0.3333334])
#                                                HIGH  /  MODERATE  /  LOW
cougar_risk_level.setDistributionParameters([0.3333333, 0.3333334, 0.3333333])
#                                    Present /   Not Present
wolfPresence.setDistributionParameters([0.5, 0.5])
#                                                    "0%", "0-10%", "10-20%", "20-100%"
proportion_of_lu_in_UWR.setDistributionParameters([0.25,        0.25,        0.25,        0.25])
#                                         // None         Low          Moderate-low Moderate-high High        
uwr_hazard_rating.setDistributionParameters([0.2,         0.2,         0.2,         0.2,         0.2])

#                                                         low  /  mod  /  High
unregulated_Hunting_Rate.distribution[{'Road Density':0}]=[0.75, 0.25, 0]
unregulated_Hunting_Rate.distribution[{'Road Density':1}]=[0.25, 0.75, 0]
unregulated_Hunting_Rate.distribution[{'Road Density':2}]=[0.25, 0.5, 0.25]

#                                                    None,   / GOS   /   Antlerless
regulated_Hunting_Rate.setDistributionParameters([0.3333334, 0.3333333, 0.3333333])

predation_risk.distribution[{'Road Density': 0, 'Cougar Risk Level': 0, 'Wolf Presence':0}] = [0.75, 0.25, 0]
predation_risk.distribution[{'Road Density': 0, 'Cougar Risk Level': 0, 'Wolf Presence':1}] = [1, 0, 0]
predation_risk.distribution[{'Road Density': 0, 'Cougar Risk Level': 1, 'Wolf Presence':0}] = [0.25, 0.75, 0]
predation_risk.distribution[{'Road Density': 0, 'Cougar Risk Level': 1, 'Wolf Presence':1}] = [0.5, 0.5, 0]
predation_risk.distribution[{'Road Density': 0, 'Cougar Risk Level': 2, 'Wolf Presence':0}] = [0, 0.5, 0.5]
predation_risk.distribution[{'Road Density': 0, 'Cougar Risk Level': 2, 'Wolf Presence':1}] = [0.25, 0.75, 0]

predation_risk.distribution[{'Road Density': 1, 'Cougar Risk Level': 0, 'Wolf Presence':0}] = [0.5, 0.5, 0]
predation_risk.distribution[{'Road Density': 1, 'Cougar Risk Level': 0, 'Wolf Presence':1}] = [1,   0,   0]
predation_risk.distribution[{'Road Density': 1, 'Cougar Risk Level': 1, 'Wolf Presence':0}] = [0,   1,   0]
predation_risk.distribution[{'Road Density': 1, 'Cougar Risk Level': 1, 'Wolf Presence':1}] = [0.5,0.5,  0]
predation_risk.distribution[{'Road Density': 1, 'Cougar Risk Level': 2, 'Wolf Presence':0}] = [0,0.25,0.75]
predation_risk.distribution[{'Road Density': 1, 'Cougar Risk Level': 2, 'Wolf Presence':1}] = [0.25,0.75,0]

predation_risk.distribution[{'Road Density': 2, 'Cougar Risk Level': 0, 'Wolf Presence':0}] = [0.25, 0.75, 0]
predation_risk.distribution[{'Road Density': 2, 'Cougar Risk Level': 0, 'Wolf Presence':1}] = [1,  0,     0 ]
predation_risk.distribution[{'Road Density': 2, 'Cougar Risk Level': 1, 'Wolf Presence':0}] = [0,0.75, 0.25 ]
predation_risk.distribution[{'Road Density': 2, 'Cougar Risk Level': 1, 'Wolf Presence':1}] = [0.5,0.5,  0]
predation_risk.distribution[{'Road Density': 2, 'Cougar Risk Level': 2, 'Wolf Presence':0}] = [0,0,1 ]
predation_risk.distribution[{'Road Density': 2, 'Cougar Risk Level': 2, 'Wolf Presence':1}] = [0.25,0.75,0 ]

population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 0, 'Regulated Hunting Rate':0}] = [0,           1,           0,           0,           0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 0, 'Regulated Hunting Rate':1}] = [0,           1,           0,           0,           0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 0, 'Regulated Hunting Rate':2}] = [0,           0.75,        0.25,        0,           0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 1, 'Regulated Hunting Rate':0}] = [0,           0.85,        0.15,        0,           0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 1, 'Regulated Hunting Rate':1}] = [0,           0.75,        0.25,        0,           0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 1, 'Regulated Hunting Rate':2}] = [0,           0.5,         0.25,        0.25,        0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 2, 'Regulated Hunting Rate':0}] = [0,           0.6,         0.25,        0.15,        0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 2, 'Regulated Hunting Rate':1}] = [0,           0.5,         0.25,        0.25,        0] 
population_hazard.distribution[{'Unregulated Hunting Rate':0, 'Predation Risk': 2, 'Regulated Hunting Rate':2}] = [0,           0.25,        0.5,         0.25,        0]

population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 0, 'Regulated Hunting Rate':0}] = [0,           0.35,        0.5,         0.15,        0] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 0, 'Regulated Hunting Rate':1}] = [0,           0.25,        0.5,         0.25,        0] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 0, 'Regulated Hunting Rate':2}] = [0,           0,           0.5,         0.5,         0] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 1, 'Regulated Hunting Rate':0}] = [0,           0,           0.6,         0.4,         0] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 1, 'Regulated Hunting Rate':1}] = [0,           0,           0.5,         0.5,         0] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 1, 'Regulated Hunting Rate':2}] = [0,           0,           0.5,         0.25,        0.25] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 2, 'Regulated Hunting Rate':0}] = [0,           0,           0.6,         0.25,        0.15] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 2, 'Regulated Hunting Rate':1}] = [0,           0,           0.5,         0.25,        0.25] 
population_hazard.distribution[{'Unregulated Hunting Rate':1, 'Predation Risk': 2, 'Regulated Hunting Rate':2}] = [0,           0,           0.25,        0.5,         0.25]

population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 0, 'Regulated Hunting Rate':0}] = [ 0,           0,           0.35,        0.5,         0.15  ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 0, 'Regulated Hunting Rate':1}] = [ 0,           0,           0.25,        0.5,         0.25 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 0, 'Regulated Hunting Rate':2}] = [ 0,           0,           0,           0.5,         0.5 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 1, 'Regulated Hunting Rate':0}] = [ 0,           0,           0,           0.6,         0.4 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 1, 'Regulated Hunting Rate':1}] = [ 0,           0,           0,           0.5,         0.5 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 1, 'Regulated Hunting Rate':2}] = [ 0,           0,           0,           0.25,        0.75 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 2, 'Regulated Hunting Rate':0}] = [ 0,           0,           0,           0.35,        0.65 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 2, 'Regulated Hunting Rate':1}] = [ 0,           0,           0,           0.25,        0.75 ] 
population_hazard.distribution[{'Unregulated Hunting Rate':2, 'Predation Risk': 2, 'Regulated Hunting Rate':2}] = [ 0,           0,           0,           0,           1 ]

habitat_hazard_rating.distribution[{'UWR Hazard Rating': 0, 'Proportion of LU in UWR':0}] = [1,           0,           0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 0, 'Proportion of LU in UWR':1}] = [1,           0,           0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 0, 'Proportion of LU in UWR':2}] = [1,           0,           0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 0, 'Proportion of LU in UWR':3}] = [1,           0,           0,           0,           0]

habitat_hazard_rating.distribution[{'UWR Hazard Rating': 1, 'Proportion of LU in UWR':0}] = [1,           0,           0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 1, 'Proportion of LU in UWR':1}] = [0.75,        0.25,        0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 1, 'Proportion of LU in UWR':2}] = [0.5,         0.5,         0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 1, 'Proportion of LU in UWR':3}] = [0,           1,           0,           0,           0]

habitat_hazard_rating.distribution[{'UWR Hazard Rating': 2, 'Proportion of LU in UWR':0}] = [1,           0,           0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 2, 'Proportion of LU in UWR':1}] = [0,           0.75,        0.25,        0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 2, 'Proportion of LU in UWR':2}] = [0,           0.5,         0.5,         0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 2, 'Proportion of LU in UWR':3}] = [0,           0,           1,           0,           0]

habitat_hazard_rating.distribution[{'UWR Hazard Rating': 3, 'Proportion of LU in UWR':0}] = [1,           0,           0,           0,           0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 3, 'Proportion of LU in UWR':1}] = [0,           0,           0.75,        0.25,        0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 3, 'Proportion of LU in UWR':2}] = [0,           0,           0.5,         0.5,         0]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 3, 'Proportion of LU in UWR':3}] = [0,           0,           0,           1,           0]

habitat_hazard_rating.distribution[{'UWR Hazard Rating': 4, 'Proportion of LU in UWR':0}] = [1,           0,           0,           0,           0 ]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 4, 'Proportion of LU in UWR':1}] = [0,           0,           0,           0.75,        0.25]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 4, 'Proportion of LU in UWR':2}] = [0,           0,           0,           0.5,         0.5]
habitat_hazard_rating.distribution[{'UWR Hazard Rating': 4, 'Proportion of LU in UWR':3}] = [0,           0,           0,           0,           1]

# This next step is my attempt at implmenting a decision tree into the 
# distribution model that openbayes uses.                    # None, Low, Mod-low, mod-high, high
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':0, 'Population Hazard':0}] = [1,0,0,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':0, 'Population Hazard':1}] = [0,1,0,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':0, 'Population Hazard':2}] = [1,0,1,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':0, 'Population Hazard':3}] = [1,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':0, 'Population Hazard':4}] = [1,0,0,0,1]

muleDeerHazardRating.distribution[{'Habitat Hazard Rating':1, 'Population Hazard':0}] = [0,1,0,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':1, 'Population Hazard':1}] = [0,1,0,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':1, 'Population Hazard':2}] = [0,0,1,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':1, 'Population Hazard':3}] = [0,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':1, 'Population Hazard':4}] = [0,0,0,0,1]

muleDeerHazardRating.distribution[{'Habitat Hazard Rating':2, 'Population Hazard':0}] = [0,0,1,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':2, 'Population Hazard':1}] = [0,0,1,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':2, 'Population Hazard':2}] = [0,0,1,0,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':2, 'Population Hazard':3}] = [0,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':2, 'Population Hazard':4}] = [0,0,0,0,1]

muleDeerHazardRating.distribution[{'Habitat Hazard Rating':3, 'Population Hazard':0}] = [0,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':3, 'Population Hazard':1}] = [0,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':3, 'Population Hazard':2}] = [0,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':3, 'Population Hazard':3}] = [0,0,0,1,0]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':3, 'Population Hazard':4}] = [0,0,0,0,1]

muleDeerHazardRating.distribution[{'Habitat Hazard Rating':4, 'Population Hazard':0}] = [0,0,0,0,1]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':4, 'Population Hazard':1}] = [0,0,0,0,1]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':4, 'Population Hazard':2}] = [0,0,0,0,1]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':4, 'Population Hazard':3}] = [0,0,0,0,1]
muleDeerHazardRating.distribution[{'Habitat Hazard Rating':4, 'Population Hazard':4}] = [0,0,0,0,1]


# when reading in models, if CHANCE = DETERMIN for a 
# deterministic node, it basically indicates we are now
# dealing with a decision network node.
# we will need to implement the logic associated with the last decision node.
#muleDeerHazardRating.distribution[{'Habitat Hazard Rating':, 'Population Hazard':,}] = []

print network.topological_sort()
print network.src_v
# for vert in network.src_v:
for vert in network.topological_sort():
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

print network
jTree = JoinTree(network)

# marginalize: Given a joint distribution, we can compute the distributions of each variable
#independently, which are called the marginal distributions.
margResults = jTree.MarginaliseAll()
jTree.Print()

print '=============================================================='
print 'Without evidence:\n'
for n, r in margResults.items():
    print n, r, '\n'

sys.exit()

# ----------------- THIS STUFF WORKS -----------------
jTree = JoinTree(network)
jTree.MarginaliseAll()
# print jTree
print predation_risk.distribution.cpt
print '***********************************'
for parent in predation_risk.distribution.parents:
    print '   name:', parent.name
    print '   cpt:', parent.distribution.cpt
    print '   jcpt:', jTree.ExtractCPT(parent.name)

# ----------------- END -----------------

sys.exit()

jTree.Print()
# jTree.SetObs({'Cougar Risk Level':1})
# jTree.SetObs({'Road Density':2, 'Cougar Risk Level': 2, 'Wolf Presence':1})
print 'probs are:'
# print jTree.Marginalise('Population Hazard') 
print jTree.Marginalise('Mule Deer Hazard Rating') # 
jTree.Print()
#print 'dist is', population_hazard.distribution

# 0.30339703,  0.34649783,  0.35010514
# 0.30339703,  0.34649783,  0.35010514
# 0.30339703,  0.34649783,  0.35010514
# 0.30265871,  0.3474687 ,  0.34987262