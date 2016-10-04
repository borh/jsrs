# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from django.db import connection

from django_pandas.io import read_frame
#import pandas as pd

from .models import Audio, Reader, Sentence

@login_required
def audio_export_table(request):
#     cursor = connection.cursor()
#     cursor.execute(
# '''
# SELECT
#   a.path AS audio_path,
#   a.disabled AS audio_disabled,
#   r.name AS reader_name,
#   r.native_speaker AS reader_native_speaker,
#   r.gender AS reader_gender,
#   r.set AS reader_set,
#   r.disabled AS reader_disabled,
#   s.number AS sentence_number,
#   s.order AS sentence_order,
#   s.text AS sentence_text,
#   s.set AS sentence_set,
#   s.disabled AS sentence_disabled
# FROM audio_audio AS a
# JOIN audio_reader AS r
#   ON a.reader_id=r.id
# JOIN audio_sentence AS s
#   ON a.sentence_id=s.id
# ORDER BY
#   r.id,
#   s.order
# ''')
    #data = cursor.fetchall()
    #print(data)
    #return HttpResponse(pd.DataFrame.from_records(data).to_html())
    return HttpResponse(read_frame(Audio.objects.all()).to_html())

@login_required
def audio_reader_export_table(request):
    return HttpResponse(read_frame(Reader.objects.all()).to_html())

@login_required
def audio_sentence_export_table(request):
    return HttpResponse(read_frame(Sentence.objects.all()).to_html())
