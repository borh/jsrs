# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Ratings, get_next_rating, ratings_done
from .forms import RatingsForm

from ..users.models import Rater

@login_required
def ratings_page(request):
    try:
        rater = Rater.objects.get(user_id=request.user.id)
    except Rater.DoesNotExist:
        return HttpResponseRedirect(reverse('users:rater_survey'))
    #if not request.user.is_authenticated(): return render(request, 'ratings/ratings.html')

    sound_file_a, sound_file_b, (mdpref_results, mdpref_svg) = get_next_rating(request.user.id)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RatingsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            r = Ratings(audio_a=sound_file_a, audio_b=sound_file_b, user=request.user, a_gt_b=form.cleaned_data['a_gt_b'])
            if request.user.is_superuser == False:
                r.save()
            return HttpResponseRedirect(reverse('ratings:ratings'))

        # if a GET (or any other method) we'll create a blank form
    else:
        form = RatingsForm()

    rated = ratings_done(request.user.id)
    rated_goal = 50 # TODO make ratings_set-specific

    # Do not send mdprefmx results for non-admin users.
    if request.user.is_superuser == False:
        mdpref_results = None

    return render(request,
                  'ratings/ratings.html',
                  {'form': form,
                   'user_id': request.user.id,
                   'mdpref_results': mdpref_results,
                   'mdpref_svg': mdpref_svg,
                   'rated': rated,
                   'rated_progress': round(rated / rated_goal * 100),
                   'rated_goal': rated_goal,
                   'sound_file_a': sound_file_a.path,
                   'sound_file_b': sound_file_b.path})

from django.http import JsonResponse
def get_ratings_done(request):
    return JsonResponse({'ratings_done': ratings_done(request.user.id)})
