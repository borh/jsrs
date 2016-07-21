# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from jsrs.users.models import User
from jsrs.audio.models import Audio, Reader, Sentence
from .r import mdprefml

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

def get_all_ratings(sentence_id):
    cursor = connection.cursor()
    cursor.execute('''
SELECT
  rl.n,
  COUNT(r.a_gt_b) AS f, -- reason for lateral query: need to sum over only TRUE a_gt_b
  rl.audio_a_id,
  rl.audio_b_id,
  rl.subject
FROM
  ratings_ratings AS r,
  LATERAL (
    SELECT
      user_id AS subject,
      count(a_gt_b) AS n,
      audio_a_id,
      audio_b_id
    FROM ratings_ratings
    WHERE sentence_id = %s
    GROUP BY audio_a_id, audio_b_id, user_id
  ) AS rl
WHERE
  r.sentence_id = %s AND
  r.a_gt_b IS TRUE AND
  r.user_id=rl.subject AND
  r.audio_a_id=rl.audio_a_id AND
  r.audio_b_id=rl.audio_b_id
GROUP BY
  rl.subject,
  rl.n,
  rl.audio_a_id,
  rl.audio_b_id
ORDER BY
  rl.subject,
  rl.audio_a_id,
  rl.audio_b_id''', [sentence_id, sentence_id])
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


def get_unrated_pair(user_id):
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
    div(ur.set_n, (SELECT count(*) FROM audio_reader WHERE disabled IS FALSE)) AS set_n_times
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
LIMIT 1''', [user_id])
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
    mdpref_results = None
    mdpref_svg = None
    try:
        ratings = get_all_ratings()
        #print('ratings = {}'.format(ratings))
        f = [r[0] for r in ratings]
        n = [r[1] for r in ratings]
        ij = list(chain.from_iterable(r[2:4] for r in ratings))
        #print(ij)
        subj = [r[4] for r in ratings]
        # f = [] # TODO -> direct SQL query easier???
        mdpref_results, mdpref_svg = mdprefml(f, n, ij, subj)
    except Exception as e:
        print('Exception occured while running mdprefml:', e)
    return (mdpref_results, mdpref_svg)

import random
def get_next_rating(user_id):
    # TODO use user_id to join with Users table
    # ratings = Ratings.objects.values()

    audio_files = get_unrated_pair()

    mdpref_results = None
    mdpref_svg = None
    if len(audio_files) == 0:

        # mdpref_results, mdpref_svg = get_mdpref_results()

        audio_files = get_random_pair()

    a_model = Audio.objects.get(id=audio_files[0][0])
    b_model = Audio.objects.get(id=audio_files[0][1])
    ab = [a_model, b_model]
    random.shuffle(ab)
    a, b = ab

    try:
        sentence = Sentence.objects.get(sentence=a_model.sentence)
    except Exception as e:
        print('Exception getting sentence id="{}"'.format(a_model.sentence))
        sentence = Sentence(sentence=a_model.id, text='')

    return (a, b, sentence.text, (mdpref_results, mdpref_svg))

def ratings_done(user_id):
    return Ratings.objects.filter(user_id=user_id).count()
