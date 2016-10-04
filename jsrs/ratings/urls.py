# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'^$', view=views.ratings_page, name='ratings'),
    url(regex=r'^ratings_done$', view=views.get_ratings_done, name='ratings_done'),
    url(regex=r'^export_table', view=views.ratings_export_table, name='export_table'),
    url(regex=r'^next_pair', view=views.next_pair_export_table, name='next_pair_export_table'),
    url(regex=r'^mdpref', view=views.mdpref_results, name='ratings_mdpref_results'),
]
