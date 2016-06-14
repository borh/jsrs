from rpy2.robjects import r
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

importr('lazy.mdpref')

# base = importr('base')
# from rpy2.robjects import NA_Real
# m = base.matrix(NA_Real, nrow=100, ncol=10)

# print(r('help(mdprefmx)'))

mdprefml_r = ro.r['mdprefml']

import time

def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % \
              (method.__name__, len(args), len(kw), te - ts))
        return result

    return timed

import datetime

@timeit
def mdprefml(f, n, ij, subj):
    '''Parameters:
        f   : vector consisting of the # of times that the left stimuli was chosen out of n trials.
        n   : vector consisting of the # of trials.
        ij  : matrix indicating the stimulus pair.
        subj: vector indicating the subject.
    The quartet ( subj, n, f, ij ) contains the result of the paired comparison data.
    These four objects have the same length or # of rows.
    The k-th elements of the quartet indicate that subj[k] preferred stimulus ij[k,1] over ij[k,2] f[k] times when exposed to the pair n[k] times.
    The paired comparison for each subject does no have to be complete.'''
    #print(ro.r.matrix(ro.IntVector(ij), ncol=2, byrow=True))

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')
    svg_filename = 'mdprefml-{}.svg'.format(timestamp)
    r('svg("{}", width=7, height=7)'.format(svg_filename))

    result = mdprefml_r(ro.IntVector(f), ro.IntVector(n), ro.r.matrix(ro.IntVector(ij), nrow=len(f)), ro.IntVector(subj), print=0, plot=1)

    r('dev.off()')

    return (result, svg_filename)
