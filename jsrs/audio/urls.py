# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^export_table', view=views.audio_export_table, name='audio_export_table'),
]
