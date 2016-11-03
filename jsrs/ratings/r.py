from rpy2.robjects import r
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

import pandas as pd
import numpy as np
from rpy2.robjects import pandas2ri, numpy2ri
pandas2ri.activate()

import rpy2.rinterface as ri
ri.initr()

from ..audio.models import Audio, Reader
from jsrs.users.models import User

import logging
logger = logging.getLogger(__name__)

mdpref = importr('lazy.mdpref')
graphics = importr('graphics') # Needed by biplot.

rlist = ri.baseenv["list"]

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


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    return np.dot(v1, v2)/np.linalg.norm(v1)/np.linalg.norm(v2)


def magnitude(x):
    return np.sqrt(x[0]**2 + x[1]**2)


def scalar_projection(a, b):
    '''Returns the scalar projection of vector a onto b defined as:
    s = \|a\|\cos{\theta} = \frac{a\cdot b}{\|b\|}'''
    return magnitude(a) * angle_between(a, b)


def rank_ratings(mdpref_result):
    if not mdpref_result or isinstance(mdpref_result, str):
        return (None, None)

    B = mdpref_result.rx2('B')
    B_rater_ids = ro.r['rownames'](B)
    B_df = pd.DataFrame(pandas2ri.ri2py(B), index=B_rater_ids, columns=['b1', 'b2'])
    B_df['magnitude'] = np.sqrt(B_df['b1'].pow(2) + B_df['b2'].pow(2))
    B_df['rater'] = B_rater_ids # ['{} {}'.format(b, User.objects.get(id=b).username) for b in B_rater_ids]
    B_df.sort_values(by='magnitude', ascending=False, inplace=True)

    X = mdpref_result.rx2('X')
    X_audio_ids = ro.r['rownames'](X)
    X_df = pd.DataFrame(pandas2ri.ri2py(X), index=X_audio_ids, columns=['x1', 'x2'])
    X_df['magnitude'] = np.sqrt(X_df['x1'].pow(2) + X_df['x2'].pow(2))
    X_df['reader'] = X_audio_ids # [Audio.objects.get(id=audio_id).reader for audio_id in X_audio_ids]

    for i, rater in enumerate(B_df['rater']):
        b_normalized_x = [scalar_projection(np.array([row.x1, row.x2]), np.array(B_df.iloc[i, 0:2])) for row in X_df[['x1', 'x2']].itertuples()]
        X_df[rater] = b_normalized_x

    X_df.sort_values(by=[b for b in B_df['rater']], ascending=[False for b in B_df['rater']], inplace=True)

    rater_ranks = B_df.to_html()
    reader_ranks = X_df.to_html()
    return (reader_ranks, rater_ranks)


def c5ml(f, n, ij):

    c5ml_result = None

    try:
        c5ml_result = mdpref.c5ml(ro.IntVector(f), ro.IntVector(n), ro.r.matrix(ro.StrVector(ij), nrow=len(f)), print=0)
        c5ml_xs = c5ml_result.rx2('xs')
        c5ml_names = ro.r['names'](c5ml_xs)
        c5ml_result = dict(zip(c5ml_names, c5ml_xs))
        c5ml_result = sorted(c5ml_result.items(), key = lambda x: x[1], reverse = True)
    except Exception as e:
        msg = 'Exception while running c5ml: {}'.format(e)
        c5ml_result = msg
        logger.warn(msg)

    return c5ml_result


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

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')
    svg_filename = 'mdprefml-{}-{}.svg'.format(timestamp, sentence_id)
    r('svg("jsrs/media/{}", width=12, height=12)'.format(svg_filename))

    mdpref_result = None

    try:
        mdpref_result = mdpref.mdprefml(ro.IntVector(f), ro.IntVector(n), ro.r.matrix(ro.StrVector(ij), nrow=len(f)), ro.StrVector(subj), ndim=2, lmax=500, print=0, plot=1)

    except Exception as e:
        msg = 'Exception while running mdprefml on sentence {}: {}'.format(sentence_id, e)
        mdpref_result = msg
        logger.warn(msg)

    r('dev.off()')

    c5ml_result = c5ml(f, n, ij)

    reader_ranks, rater_ranks = rank_ratings(mdpref_result)

    return (mdpref_result, c5ml_result, svg_filename, reader_ranks, rater_ranks)


def biplot(data, labels=None, type='sentence'):

    readers = list(set(reader for result in data for reader, _ in result))

    m = np.matrix([[dict(result).get(reader, ro.NA_Real) for reader in readers] for result in data])

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')
    svg_filename = 'c5ml-{}-{}.svg'.format(type, timestamp)
    r('svg("jsrs/media/{}", width=12, height=12)'.format(svg_filename))

    m = np.asarray(m) # Convert back to ndarray as rpy2 blows the recursion stack with matrices.
    nc, nr = m.shape # Flipped because of transpose below:
    rm = ro.FloatVector(m.transpose().reshape((m.size)))
    rm = ro.r.matrix(rm, nrow=nr, ncol=nc)
    ro.globalenv["rm"] = rm

    if labels:
        ro.globalenv["col.labels"] = ro.StrVector(labels)
    else:
        ro.globalenv["col.labels"] = ro.StrVector(list('s' + str(i) for i in range(1, nc + 1)))

    ro.globalenv["row.labels"] = ro.StrVector(readers)

    r('colnames(rm) <- col.labels')
    r('rownames(rm) <- row.labels')
    r('library(pcaMethods)')
    try:
        r('pca <- pca(completeObs(rm), method="ppca")') # Deals with NAs better using nipalsPca.
        #r('pca <- prcomp(~., data=as.data.frame(rm), na.action=na.omit, scale=TRUE)') # center=FALSE, scale=TRUE
        r('biplot(pca)')
    except Exception as e:
        msg = 'Exception while running pca: {}'.format(e)
        logger.warn(msg)

    r('dev.off()')

    return svg_filename
