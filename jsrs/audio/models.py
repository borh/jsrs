# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

@python_2_unicode_compatible
class Audio(models.Model):

    path = models.CharField(max_length=255, unique=True)
    group = models.CharField(max_length=255, db_index=True)
    reader = models.CharField(max_length=255, db_index=True)
    sentence = models.IntegerField(db_index=True) # Currently 1..40
    rating_set = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    # length = models.IntegerField() # TODO
    # Other metadata...

    class Meta:
        verbose_name_plural = 'Audio'

    def __str__(self):
        return '{}::{}::{}::{}'.format(self.group, self.reader, self.sentence, self.rating_set)

    def get_by_natural_key(self):
        return (self.path) # or (self.sentence, self.reader) ?

    # def get_absolute_url(self):
    #     return reverse('audio:play', kwargs={'sentence': self.sentence, 'reader': self.reader})

class Sentence(models.Model):
    sentence = models.IntegerField(db_index=True)
    text = models.CharField(max_length=255, unique=True, db_index=True)
