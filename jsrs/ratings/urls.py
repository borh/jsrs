# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^$', view=views.ratings_page, name='ratings'),
    url(regex=r'^ratings_done$', view=views.get_ratings_done, name='ratings_done'),
]
