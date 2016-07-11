# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsrs.users.models import User
from jsrs.audio.models import Audio, Sentence
from .r import mdprefml

from django.utils.translation import ugettext_lazy as _
BOOL_CHOICES = ((True, _('Yes')), (False, _('No')))

@python_2_unicode_compatible
class Ratings(models.Model):
    audio_a = models.ForeignKey(Audio, related_name='audio_a_fk', on_delete=models.CASCADE)
    audio_b = models.ForeignKey(Audio, related_name='audio_b_fk', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    a_gt_b = models.BooleanField(verbose_name='AがBより良い', choices=BOOL_CHOICES, db_index=True) # True/1 -> a is better; False/0 -> b is better
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return '{}-{}-{}-{}'.format(self.audio_a, self.audio_b, self.user, self.a_gt_b)

from django.db import connection

def get_all_ratings():
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
    GROUP BY audio_a_id, audio_b_id, user_id
  ) AS rl
WHERE
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
  rl.audio_b_id''')
    return cursor.fetchall()

def get_all_ratings_summary():
    cursor = connection.cursor()
    cursor.execute('''
WITH reverse_duplicate_pairs AS (
  SELECT DISTINCT
    audio_b_id AS a,
    audio_a_id AS b
  FROM
    ratings_ratings
  WHERE
    (audio_a_id, audio_b_id) IN (SELECT audio_b_id, audio_a_id FROM ratings_ratings)
  GROUP BY
    audio_a_id,
    audio_b_id
)
SELECT
  rl.n,
  COUNT(r.a_gt_b) + (SELECT count(*) FROM ratings_ratings AS r_gt WHERE r.audio_a_id=r_gt.audio_b_id AND r.audio_b_id=r_gt.audio_a_id AND r_gt.a_gt_b IS FALSE) AS f,
  regexp_replace(a.path, '.+([ns])\d(\d\d)/.(\d\d?).+', '\1\2_\3') AS audio_a,
  regexp_replace(b.path, '.+([ns])\d(\d\d)/.(\d\d?).+', '\1\2_\3') AS audio_b,
  a.id AS a_id,
  b.id AS b_id,
  rl.subject
FROM
  ratings_ratings AS r,
  LATERAL (
    SELECT
      r_l.user_id AS subject,
      count(r_l.a_gt_b) + (SELECT count(*) FROM ratings_ratings AS r_c WHERE r_c.audio_b_id=r.audio_a_id AND r_c.audio_a_id=r.audio_b_id) AS n,
      r_l.audio_a_id,
      r_l.audio_b_id
    FROM ratings_ratings AS r_l
    WHERE (r_l.audio_a_id, r_l.audio_b_id) NOT IN (SELECT * FROM reverse_duplicate_pairs)
    GROUP BY r_l.audio_a_id, r_l.audio_b_id, r_l.user_id ORDER BY n DESC
  ) AS rl,
  audio_audio AS a,
  audio_audio AS b
WHERE
  (r.audio_a_id, r.audio_b_id) NOT IN (SELECT * FROM reverse_duplicate_pairs) AND
  a.native_speaker IS FALSE AND b.native_speaker IS FALSE AND
  r.a_gt_b IS TRUE AND
  r.user_id=rl.subject AND
  r.audio_a_id=rl.audio_a_id AND
  r.audio_b_id=rl.audio_b_id AND
  r.audio_a_id=a.id AND
  r.audio_b_id=b.id
GROUP BY
  rl.subject,
  rl.n,
  rl.audio_a_id,
  rl.audio_b_id,
  r.audio_a_id,
  r.audio_b_id,
  a.path,
  b.path,
  a.id,
  b.id
ORDER BY
  n DESC,
  rl.subject,
  rl.audio_a_id,
  rl.audio_b_id
    ''')
    return cursor.fetchall()

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

def get_unrated_pair():
    '''両方あるいは片方の評定データのない任意２名の２センテンス（同じ文）を選ぶ。'''
    cursor = connection.cursor()
    cursor.execute('''
SELECT
  a1.id,
  a2.id,
  count(r.audio_a_id),
  count(r.audio_b_id)
FROM
  ratings_ratings AS r
RIGHT JOIN
  audio_audio AS a1
  ON
    r.audio_a_id=a1.id OR
    r.audio_b_id=a1.id
JOIN -- get the pair --
  audio_audio AS a2
  ON
    a1.id!=a2.id AND
    NOT (a1.native_speaker IS TRUE AND
         a2.native_speaker IS TRUE) AND
    a1.sentence=a2.sentence
WHERE
  r.audio_a_id IS NULL OR
  r.audio_b_id IS NULL
GROUP BY
  a1.id,
  a2.id
ORDER BY
  count(r.audio_a_id) + count(r.audio_b_id) DESC,
  a1.id,
  a2.id
LIMIT 1''')
    return cursor.fetchall()

def get_random_pair():
    '''評価回数が少ない任意２名の２センテンス（同じ文）を選ぶ。'''
    cursor = connection.cursor()
    cursor.execute('''
WITH pairs AS (
  SELECT
    a1.id AS a,
    a2.id AS b,
    count(r.audio_a_id) + count(r.audio_b_id) AS all_count
  FROM
    ratings_ratings AS r
  RIGHT JOIN
    audio_audio AS a1
    ON
      r.audio_a_id=a1.id OR
      r.audio_b_id=a1.id
  JOIN
    audio_audio AS a2
    ON
      NOT (a1.native_speaker IS TRUE AND
           a2.native_speaker IS TRUE) AND
      a1.id!=a2.id AND
      a1.sentence=a2.sentence
  GROUP BY
    a1.id,
    a2.id
  ORDER BY
    all_count ASC)
SELECT a, b
FROM pairs
WHERE all_count=(SELECT min(all_count) FROM pairs)
ORDER BY random()
LIMIT 1''')
    return cursor.fetchall()

## SELECT
##   a.id
## FROM
##   ratings_ratings AS r
## RIGHT JOIN
##   audio_audio AS a
## ON
##   r.audio_a_id=a.id OR
##   r.audio_b_id=a.id
## WHERE
##   r.audio_a_id IS NULL OR
##   r.audio_b_id IS NULL
## GROUP BY
##   a.sentence,
##   a.group,
##   a.id
## ORDER BY
##   a.sentence,
##   a.group
## LIMIT 2

from itertools import chain
def get_mdpref_results():
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
