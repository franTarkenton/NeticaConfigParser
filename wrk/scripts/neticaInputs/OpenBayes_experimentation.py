'''
Created on 2013-08-01

@author: kjnether
'''


import site
import numpy
import numpy.numarray

dir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\scripts\deps\Lib\site-packages'
site.addsitedir(dir)  # @UndefinedVariable

import OpenBayes  # @UnresolvedImport

G = OpenBayes.bayesnet.BNet('Water Sprinkler Bayesian Network')
c, s, r, w = [G.add_v(OpenBayes.bayesnet.BVertex(name, True, 2)) for name in 'c s r w'.split()]
for ep in [(c, r), (c, s), (r, w), (s, w)]:
    G.add_e(OpenBayes.graph.DirEdge(len(G.e), *ep))
##        G.InitCPTs()
##        c.setCPT([0.5, 0.5])
##        s.setCPT([0.5, 0.9, 0.5, 0.1])
##        r.setCPT([0.8, 0.2, 0.2, 0.8])
##        w.setCPT([1, 0.1, 0.1, 0.01, 0.0, 0.9, 0.9, 0.99])

G.InitDistributions()

c.setDistributionParameters([0.5, 0.5])
s.setDistributionParameters([0.5, 0.9, 0.5, 0.1])
r.setDistributionParameters([0.8, 0.2, 0.2, 0.8])
w.setDistributionParameters([1, 0.1, 0.1, 0.01, 0.0, 0.9, 0.9, 0.99])

# self.c = c
# self.s = s
# self.r = r
# self.w = w
# self.BNet = G
# self.c = c
# self.s = s
# self.r = r
# self.w = w
# self.BNet = G