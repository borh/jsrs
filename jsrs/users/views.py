# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User, Rater


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


class RaterDetailView(LoginRequiredMixin, DetailView):
    model = Rater
    # These next two lines tell the view to index lookups by username
    slug_field = "user"
    slug_url_kwarg = "user"

class RaterUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['age', 'gender',
              'volunteer_experience_time',
              'time_abroad',
              'job',
              'place_of_birth',
              'language_use_information',
              'dialect_used',
              'best_foreign_language',
              'usual_foreign_language_use',
              'speaking_with_foreigners'
    ]

    template_name = 'rater_update.html'

    model = Rater

    # send the user to the ratings page after a successful update
    def get_success_url(self):
        return reverse("ratings:ratings")

    def get_object(self):
        # Only get the Rater record for the user making the request
        return Rater.objects.get(user_id=self.request.user.id)
