# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from jsrs.users.models import User
from jsrs.audio.models import Audio, Reader, Sentence
from .r import mdprefml
from .thurstone import thurstone
import numpy as np
from collections import defaultdict

from django.utils.translation import ugettext_lazy as _
BOOL_CHOICES = ((True, _('Yes')), (False, _('No')))

class Ratings(models.Model):
    audio_a   = models.ForeignKey(Audio, related_name='audio_a_fk', on_delete=models.CASCADE)
    audio_b   = models.ForeignKey(Audio, related_name='audio_b_fk', on_delete=models.CASCADE)
    reader_a  = models.ForeignKey(Reader, related_name='reader_a_fk', on_delete=models.CASCADE)
    reader_b  = models.ForeignKey(Reader, related_name='reader_b_fk', on_delete=models.CASCADE)
    sentence  = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    a_gt_b    = models.BooleanField(verbose_name='AがBより良い', choices=BOOL_CHOICES, db_index=True) # True/1 -> a is better; False/0 -> b is better
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.audio_a, self.audio_b, self.user, self.a_gt_b)

from django.db import connection

def get_all_ratings_by_sentence():
    cursor = connection.cursor()
    cursor.execute('''
SELECT
  rl.n AS n, -- total number of comparisons between a and b
  COUNT(r.a_gt_b) AS f, -- number of times a was greater than b
  re_a.name AS i,
  re_b.name AS j,
  rl.subject,
  r.sentence_id
FROM
  ratings_ratings AS r,
  audio_reader AS re_a,
  audio_reader AS re_b,
  LATERAL (
    SELECT
      user_id AS subject,
      count(*) AS n,
      audio_a_id,
      audio_b_id,
      sentence_id
    FROM ratings_ratings
    GROUP BY audio_a_id, audio_b_id, user_id, sentence_id
  ) AS rl
WHERE
  r.a_gt_b IS TRUE AND
  r.audio_a_id = rl.audio_a_id AND
  r.audio_b_id = rl.audio_b_id AND
  r.sentence_id = rl.sentence_id AND
  r.reader_a_id = re_a.id AND
  r.reader_b_id = re_b.id
GROUP BY
  r.sentence_id,
  rl.n,
  i,
  j,
  rl.subject
ORDER BY
  r.sentence_id,
  i,
  j,
  rl.subject''')
    return cursor.fetchall()

def get_all_ratings():
    cursor = connection.cursor()
    cursor.execute('''
SELECT
  rl.n AS n, -- total number of comparisons between a and b
  COUNT(r.a_gt_b) AS f, -- number of times a was greater than b
  re_a.name || '.' || r.sentence_id AS i,
  re_b.name || '.' || r.sentence_id AS j,
  rl.subject
FROM
  ratings_ratings AS r,
  audio_reader AS re_a,
  audio_reader AS re_b,
  LATERAL (
    SELECT
      user_id AS subject,
      count(*) AS n,
      audio_a_id,
      audio_b_id
    FROM ratings_ratings
    GROUP BY audio_a_id, audio_b_id, user_id
  ) AS rl
WHERE
  r.a_gt_b IS TRUE AND
  r.audio_a_id = rl.audio_a_id AND
  r.audio_b_id = rl.audio_b_id AND
  r.reader_a_id = re_a.id AND
  r.reader_b_id = re_b.id
GROUP BY
  i,
  j,
  rl.n,
  rl.subject
ORDER BY
  i,
  j,
  rl.subject''')
    return cursor.fetchall()


def get_all_ratings_per_sentence(sentence_id):
    cursor = connection.cursor()
    cursor.execute('''
SELECT
  rl.n,
  COUNT(r.a_gt_b) AS f, -- reason for lateral query: need to sum over only TRUE a_gt_b
  rl.reader_a_id,
  rl.reader_b_id,
  rl.subject
FROM
  ratings_ratings AS r,
  LATERAL (
    SELECT
      rr.user_id AS subject,
      count(a_gt_b) AS n,
      rr.reader_a_id,
      rr.reader_b_id
    FROM
      ratings_ratings AS rr
    WHERE
      rr.sentence_id = %s
    GROUP BY
      reader_a_id, reader_b_id, rr.user_id
  ) AS rl
WHERE
  r.sentence_id = %s AND
  r.a_gt_b IS TRUE AND
  r.user_id = rl.subject AND
  r.reader_a_id = rl.reader_a_id AND
  r.reader_b_id = rl.reader_b_id
GROUP BY
  rl.subject,
  rl.n,
  rl.reader_a_id,
  rl.reader_b_id
ORDER BY
  rl.subject,
  rl.reader_a_id,
  rl.reader_b_id''', [sentence_id, sentence_id])
    return cursor.fetchall()


def get_comparison_matrix(sentence_id):
    cursor = connection.cursor()
    cursor.execute('''
SELECT
  rl.n AS n, -- total number of comparisons between a and b
  COUNT(r.a_gt_b) AS f, -- number of times a was greater than b
  r.reader_a_id AS a_reader,
  r.reader_b_id AS b_reader
FROM
  ratings_ratings AS r,
  LATERAL (
    SELECT
      count(*) AS n,
      audio_a_id,
      audio_b_id
    FROM ratings_ratings
    WHERE sentence_id = %s
    GROUP BY audio_a_id, audio_b_id
  ) AS rl
WHERE
  r.sentence_id = %s AND
  r.a_gt_b IS TRUE AND
  r.audio_a_id=rl.audio_a_id AND
  r.audio_b_id=rl.audio_b_id
GROUP BY
  rl.n,
  a_reader,
  b_reader
ORDER BY
  a_reader,
  b_reader''', [sentence_id, sentence_id])
    return cursor.fetchall()


def get_all_ratings_summary():
    return Ratings.objects.all()

# 1.0 両方あるいは片方の評定データのない任意２名の２センテンスを選ぶ。
# 1.1 判定。
# 1.2 データベース登録。
# 1.3 すべてのデータIDに少なくとも1つの判定データがある場合は、2.0.にいく。
# 1.4 その他、すべてのデータIDに評定がつくまでは、1.0.にいく。
#
# 2.1 能力推定値/項目推定値の隣り合った任意２名の同じセンテンスIDのペアを選ぶ。
# 2.2 判定。
# 2.3 データベース登録。
# 2.4 mdpref計算。
# 2.5 2.1 に戻る。

def get_audio_summary():
    cursor = connection.cursor()
    cursor.execute(
'''
SELECT
  a.path AS audio_path,
  a.disabled AS audio_disabled,
  r.name AS reader_name,
  r.native_speaker AS reader_native_speaker,
  r.gender AS reader_gender,
  r.set AS reader_set,
  r.disabled AS reader_disabled,
  s.number AS sentence_number,
  s.order AS sentence_order,
  s.text AS sentence_text,
  s.set AS sentence_set,
  s.disabled AS sentence_disabled
FROM audio_audio AS a
JOIN audio_reader AS r
  ON a.reader_id=r.id
JOIN audio_sentence AS s
  ON a.sentence_id=s.id
ORDER BY
  r.id,
  s.order''')
    return cursor.fetchall()


def get_unrated_pair(user_id, limit=1):
    '''Gets the next optimal pair for given user.'''
    cursor = connection.cursor()
    cursor.execute('''
WITH user_ratings AS (
  SELECT
    s.id AS sentence_id,
    s.order AS sentence_order,
    count(r.id) AS id_n,
    s.set AS sentence_set,
    sum(count(r.id)) OVER (PARTITION BY s.set) AS set_n
  FROM
    audio_sentence AS s
  JOIN
    audio_audio AS a
    ON
          s.disabled IS FALSE
      AND a.disabled IS FALSE
      AND a.sentence_id = s.id
  LEFT OUTER JOIN
    ratings_ratings AS r
    ON
          r.audio_a_id = a.id
      AND r.user_id    = %s -- param_1
  GROUP BY
    s.set,
    s.id
  ORDER BY
    set_n DESC,
    id_n ASC,
    s.set ASC
), top_set AS ( -- adds set ordering column
  SELECT
    ur.sentence_id,
    ur.id_n,
    ur.sentence_set,
    ur.set_n,
    -- div(ur.set_n, (SELECT count(*) FROM audio_reader WHERE disabled IS FALSE)) AS set_n_times
    div(ur.set_n, 5000) AS set_n_times
  FROM
    user_ratings AS ur
  ORDER BY
    set_n_times ASC,
    --set_n DESC,
    ur.sentence_set ASC
  LIMIT 5 -- only return the sentences from top-scoring set
)
SELECT
  aa.id AS a,
  ab.id AS b,
  ra.name AS a_reader,
  rb.name AS b_reader,
  s.id AS sentence_id,
  (SELECT count(*) FROM ratings_ratings AS rr
   WHERE (    rr.audio_a_id = aa.id
          AND rr.a_gt_b IS TRUE)
      OR (    rr.audio_b_id = aa.id
          AND rr.a_gt_b IS FALSE)) AS w_a,
  (SELECT count(*) FROM ratings_ratings AS rr
   WHERE (    rr.audio_b_id = ab.id
          AND rr.a_gt_b IS FALSE)
      OR (    rr.audio_a_id = ab.id
          AND rr.a_gt_b IS TRUE)) AS w_b,
  (SELECT count(*) FROM ratings_ratings AS rr
   WHERE rr.audio_a_id = aa.id
      OR rr.audio_b_id = aa.id) AS n_a,
  (SELECT count(*) FROM ratings_ratings AS rr
   WHERE rr.audio_b_id = ab.id
      OR rr.audio_a_id = ab.id) AS n_b
FROM
  top_set AS ts,
  audio_sentence AS s,
  audio_audio AS aa,
  audio_audio AS ab,
  audio_reader AS ra,
  audio_reader AS rb
WHERE
      s.set = ts.sentence_set -- from a set of 5 sentences
  AND s.id  = ts.sentence_id
  AND aa.sentence_id = s.id
  AND ab.sentence_id = s.id
  AND ra.id < rb.id
  AND ra.id = aa.reader_id
  AND rb.id = ab.reader_id
  AND NOT (    ra.native_speaker IS TRUE
           AND rb.native_speaker IS TRUE)
  AND  s.disabled IS FALSE
  AND aa.disabled IS FALSE
  AND ab.disabled IS FALSE
  AND ra.disabled IS FALSE
  AND rb.disabled IS FALSE
ORDER BY
  --w_a::float / n_a::float DESC, -- would need this defined top-level
  ts.id_n ASC,
  n_a ASC,
  n_b ASC,
  w_a DESC,
  w_b DESC,
  s.order ASC
LIMIT %s''', [user_id, limit])
    return cursor.fetchall()


from collections import defaultdict
def get_sentence_sets():
    cursor = connection.cursor()
    cursor.execute('''SELECT sentence, set FROM audio_sentence''')
    id2set = {row[0]: row[1] for row in cursor.fetchall()}
    sets = set([v for v in id2set.vals()])
    set2ids = defaultdict(set)
    for k, v in id2set.items():
        set2ids[k].add(v)
    return set2ids

def get_readers():
    cursor = connection.cursor()
    cursor.execute('''SELECT DISTINCT reader FROM audio_audio ORDER BY reader''')
    return [row[0] for row in cursor.fetchall()]

def get_ratings_per_sentence():
    cursor = connection.cursor()
    cursor.execute('''SELECT count(DISTINCT sentence) FROM audio_audio WHERE s.id=%s''', [ _ ])
    number_of_sentences = cursor.fetchone()[0]

from itertools import chain
def get_mdpref_results(sentence_id):
    ratings = get_all_ratings_per_sentence(sentence_id)

    f = [r[0] for r in ratings]
    n = [r[1] for r in ratings]
    ij = list(chain.from_iterable([str(Reader.objects.get(id=r_id)) for r_id in r[2:4]] for r in ratings))
    subj = [User.objects.get(id=r[4]).username for r in ratings]

    return mdprefml(f, n, ij, subj, sentence_id)

def get_thurstone_results(sentence_id):
    '''Retrieves comparison trails data from the database and converts it into a comparison matrix as a Numpy array for calculation by the Thurstone method:
 n  | f | a_reader | b_reader
----+---+----------+----------
  2 | 2 |        7 |        8
  4 | 2 |        7 |       11
  3 | 3 |        7 |       22
  5 | 2 |        7 |       30
  2 | 2 |        7 |       36
  5 | 4 |        7 |       44
  4 | 1 |        8 |       22
  4 | 3 |        8 |       35
  2 | 2 |        8 |       36
  7 | 3 |        8 |       44

    Readers not having comparisons are excluded from the calculation.'''
    d = get_comparison_matrix(sentence_id)

    readers = set([r[2] for r in d])
    readers |= set([r[3] for r in d])
    readers = sorted(readers)

    # n = len(readers)

    comparisons = defaultdict(dict)
    for n, f, a_reader, b_reader in d: # Difference from reference implementation: we don't have an equal number of comparisons per item, so we have to normalize on a case-by-case basis.
        comparisons[a_reader][b_reader] = f / n
        comparisons[b_reader][a_reader] = (n - f) / n

    m = [[comparisons[ri][ro] if (ri != ro and ri in comparisons and ro in comparisons[ri]) else 0.5
          for ri in readers]
         for ro in readers]

    r = dict(zip([Reader.objects.get(id=reader_id) for reader_id in readers], thurstone(np.array(m))))

    return sorted(r.items(), key = lambda x: x[1], reverse = True)

def get_next_rating(user_id):
    audio_files = get_unrated_pair(user_id)

    a_model = Audio.objects.get(id=audio_files[0][0])
    b_model = Audio.objects.get(id=audio_files[0][1])
    ab = [a_model, b_model]
    # random.shuffle(ab) # FIXME need a order-stable algo to make this safe
    a, b = ab

    try:
        sentence = Sentence.objects.get(id=a_model.sentence.id)
    except Exception as e:
        print('Exception getting sentence id="{}"'.format(a_model.sentence))
        sentence = Sentence(id=a_model.id, text='')

    return (a, b, sentence.text)

def ratings_done(user_id):
    return Ratings.objects.filter(user_id=user_id).count()
