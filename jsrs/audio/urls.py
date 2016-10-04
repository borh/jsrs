# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^export_table', view=views.audio_export_table, name='export_table'),
    url(regex=r'^export_reader_table', view=views.audio_reader_export_table, name='reader_export_table'),
    url(regex=r'^export_sentence_table', view=views.audio_sentence_export_table, name='sentence_export_table'),
]
