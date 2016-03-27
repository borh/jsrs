from rpy2.robjects import r
import rpy2.robjects as ro
from rpy2.robjects.packages import importr

importr('lazy.mdpref')

# base = importr('base')
# from rpy2.robjects import NA_Real
# m = base.matrix(NA_Real, nrow=100, ncol=10)

# print(r('help(mdprefmx)'))

mdprefmx_r = ro.r['mdprefmx']

def mdprefmx(f, n, ij, subj):
    '''Parameters:
        f   : vector consisting of the # of times that the left stimuli was chosen out of n trials.
        n   : vector consisting of the # of trials.
        ij  : matrix indicating the stimulus pair.
        subj: vector indicating the subject.
    The quartet ( subj, n, f, ij ) contains the result of the paired comparison data.
    These four objects have the same length or # of rows.
    The k-th elements of the quartet indicate that subj[k] preferred stimulus ij[k,1] over ij[k,2] f[k] times when exposed to the pair n[k] times.
    The paired comparison for each subject does no have to be complete.'''
    print(ro.r.matrix(ro.IntVector(ij), ncol=2, byrow=True))
    mdprefmx_r(ro.IntVector(f), ro.IntVector(n), ro.r.matrix(ro.IntVector(ij), nrow=len(f)), ro.IntVector(subj))
