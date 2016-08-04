from rpy2.robjects import r
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

import pandas as pd
#from rpy2.robjects import pandas2ri
#pandas2ri.activate()

import logging
logger = logging.getLogger(__name__)

mdpref = importr('lazy.mdpref')

import time
import datetime

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        logger.debug('%r (%r, %r) %2.2f sec' % \
                     (method.__name__, len(args), len(kw), te - ts))
        return result
    return timed


def rank_ratings(mdpref_result):
    if not mdpref_result or isinstance(mdpref_result, str):
        return None

    print('Result:' + mdpref_result)
    print(type(mdpref_result))

    X = mdpref_result.rx2('X')
    print(X)

    B = mdpref_result.rx2('B')
    print(B)

    #pd.DataFrame()
    #for k in range():
    #    pass

    ranks = pd.DataFrame()
    return ranks.to_html()

@timeit
def mdprefml(f, n, ij, subj, sentence_id):
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
    svg_filename = 'mdprefml-{}-{}.svg'.format(timestamp, sentence_id)
    r('svg("jsrs/media/{}", width=12, height=12)'.format(svg_filename))

    result = None
    try:
        result = mdpref.mdprefml(ro.IntVector(f), ro.IntVector(n), ro.r.matrix(ro.IntVector(ij), nrow=len(f)), ro.IntVector(subj), print=0, plot=1)
    except Exception as e:
        logger.warn('Exception while running mdprefml on sentence {}: {}'.format(sentence_id, e))
        logger.warn('mdprefml input was: {}, {}, {}, {}'.format(tuple(ro.IntVector(f).rclass), tuple(ro.IntVector(n).rclass), tuple(ro.r.matrix(ro.IntVector(ij), nrow=len(f)).rclass), tuple(ro.IntVector(subj).rclass)))
        result = 'Exception while running mdprefml on sentence {}: {}'.format(sentence_id, e)

    r('dev.off()')

    ranks = rank_ratings(result)

    return (result, svg_filename, ranks)
