from rpy2.robjects import r
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

import pandas as pd
import numpy as np
from rpy2.robjects import pandas2ri
pandas2ri.activate()

from ..audio.models import Audio, Reader
from jsrs.users.models import User

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
        result = mdpref.mdprefml(ro.IntVector(f), ro.IntVector(n), ro.r.matrix(ro.StrVector(ij), nrow=len(f)), ro.StrVector(subj), print=0, plot=1)
    except Exception as e:
        msg = 'Exception while running mdprefml on sentence {}: {}'.format(sentence_id, e)
        result = msg
        logger.warn(msg)
        logger.warn('mdprefml input was: {}, {}, {}, {}'.format(tuple(ro.IntVector(f).rclass), tuple(ro.IntVector(n).rclass), tuple(ro.r.matrix(ro.StrVector(ij), nrow=len(f)).rclass), tuple(ro.StrVector(subj).rclass)))

    r('dev.off()')

    reader_ranks, rater_ranks = rank_ratings(result)

    return (result, svg_filename, reader_ranks, rater_ranks)
