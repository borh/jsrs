# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Sentence(models.Model):
    number = models.IntegerField(unique=True, db_index=True)
    text = models.CharField(max_length=255, unique=True, db_index=True)
    order = models.IntegerField(unique=True, db_index=True)
    set = models.IntegerField(db_index=True, blank=True, null=True) # Manually set
    disabled = models.BooleanField(db_index=True, default=False)

    def __str__(self):
        return '{}::{}::{}::{}::{}'.format(self.number, self.text, self.order, self.set, self.disabled)

class Reader(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    native_speaker = models.BooleanField(db_index=True)
    gender = models.CharField(max_length=1, db_index=True)
    set = models.IntegerField(db_index=True, blank=True, null=True)
    disabled = models.BooleanField(db_index=True, default=False)

    def __str__(self):
        return '{}::{}::{}::{}::{}'.format(self.name, self.native_speaker, self.gender, self.set, self.disabled)

class Audio(models.Model):
    path = models.CharField(max_length=255, unique=True, db_index=True)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, db_index=True)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, db_index=True)
    set = models.IntegerField(db_index=True, blank=True, null=True) # FIXME Possibly superfluous
    disabled = models.BooleanField(db_index=True, default=False)
    # length = models.IntegerField() # TODO

    class Meta:
        verbose_name_plural = 'Audio'

    def __str__(self):
        return '{}::{}::{}::{}'.format(self.reader, self.sentence, self.set, self.disabled)

    def get_by_natural_key(self):
        return (self.path) # or (self.sentence, self.reader) ?

    # def get_absolute_url(self):
    #     return reverse('audio:play', kwargs={'sentence': self.sentence, 'reader': self.reader})
