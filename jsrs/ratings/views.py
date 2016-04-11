# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Ratings, get_next_rating
from .forms import RatingsForm

def ratings_page(request):
    sound_file_a, sound_file_b = get_next_rating(request.user.id)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RatingsForm(request.POST)
        print(form)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            r = Ratings(audio_a=sound_file_a, audio_b=sound_file_b, user=request.user, a_gt_b=form.cleaned_data['a_gt_b'])
            r.save()
            return HttpResponseRedirect(reverse('ratings:ratings'))

        # if a GET (or any other method) we'll create a blank form
    else:
        form = RatingsForm()

    return render(request,
                  'ratings/ratings.html',
                  {'form': form,
                   'user_id': request.user.id,
                   'sound_file_a': sound_file_a.path,
                   'sound_file_b': sound_file_b.path})
