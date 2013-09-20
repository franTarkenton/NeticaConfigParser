



import site
dir = r'W:\ilmb\vic\geobc\bier\p14\p14_0053_BBN_CumEffects\wrk\scripts\deps\Lib\site-packages'
site.addsitedir(dir)  # @UndefinedVariable

from thinkbayes.thinkbayes import Pmf
print 'got here!'


def example1():
    pmf = Pmf()
    for x in [1,2,3,4,5,6]:
        pmf.Set(x, 1)
    pmf.Print()
    pmf.Normalize()
    pmf.Print()
    
def cookieExample():
    pmf = Pmf()
    pmf.Set('Bowl 1', .5)
    pmf.Set('Bowl 2', .5)
    pmf.Mult('Bowl 1', .75)
    pmf.Mult('Bowl 2', .5)
    pmf.Normalize()
    print pmf.Prob('Bowl 1')
    
def example2():
    pmf = Pmf()
    pmf.Set('High', 33.3)
    pmf.Set('Moderate', 33.3)
    pmf.Set("Low", 33.3)
    pmf.Normalize()
    pmf.Print()
    
if __name__ == '__main__':
    example2()
    
