# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='list'
    ),

    # URL pattern for the UserRedirectView
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),

    # URL pattern for the RaterDetailView
    url(
        regex=r'^rater/(?P<user>[\w.@+-]+)/$',
        view=views.RaterDetailView.as_view(),
        name='rater_detail'
    ),

    # # URL pattern for the RaterUpdateView
    # url(
    #     regex=r'^~rater_update/$',
    #     view=views.RaterUpdateView.as_view(),
    #     name='rater_update'
    # ),

    url(
        regex=r'^~rater_survey/$',
        view=views.rater_survey,
        name='rater_survey'
    ),

    url(
        regex=r'^export_table$',
        view=views.export_table,
        name='export_table'
    ),
]
