# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsrs.users.models import User
from jsrs.audio.models import Audio
from .r import mdprefmx

from django.utils.translation import ugettext_lazy as _
BOOL_CHOICES = ((True, _('Yes')), (False, _('No')))

@python_2_unicode_compatible
class Ratings(models.Model):
    audio_a = models.ForeignKey(Audio, related_name='audio_a_fk', on_delete=models.CASCADE)
    audio_b = models.ForeignKey(Audio, related_name='audio_b_fk', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    a_gt_b = models.BooleanField(verbose_name='AがBより良い', choices=BOOL_CHOICES) # True/1 -> a is better; False/0 -> b is better


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
  r.a_gt_b=TRUE AND
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

from itertools import chain
def get_next_rating(user_id):
    # TODO use user_id to join with Users table
    # ratings = Ratings.objects.values()
    ratings = get_all_ratings()
    print('ratings = {}'.format(ratings))
    f = [r[0] for r in ratings]
    n = [r[1] for r in ratings]
    ij = list(chain.from_iterable(r[2:4] for r in ratings))
    print(ij)
    subj = [r[4] for r in ratings]
    # f = [] # TODO -> direct SQL query easier???
    print(mdprefmx(f, n, ij, subj))

    a = Audio.objects.get(reader='JP_EXPERIMENT_1-1', sentence=1)
    b = Audio.objects.get(reader='JP_EXPERIMENT_1-2', sentence=1)
    return (a, b)
