# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

import pandas as pd
from django_pandas.io import read_frame

from ..users.models import Rater
from ..audio.models import Audio
from .models import Ratings, get_next_rating, ratings_done, get_all_ratings_summary, get_unrated_pair, get_mdpref_results
from .forms import RatingsForm

import logging
logger = logging.getLogger(__name__)

@login_required
def ratings_page(request):
    try:
        rater = Rater.objects.get(user_id=request.user.id)
    except Rater.DoesNotExist:
        return HttpResponseRedirect(reverse('users:rater_survey'))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RatingsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            audio_a = form.cleaned_data['audio_a']
            audio_b = form.cleaned_data['audio_b']

            r = Ratings(
                audio_a=audio_a,
                audio_b=audio_b,
                reader_a=audio_a.reader,
                reader_b=audio_b.reader,
                sentence=audio_a.sentence,
                a_gt_b=form.cleaned_data['a_gt_b'],
                user=request.user
            )
            logger.debug(
                'Rating POST requested for user={} sound_file_a={} sound_file_b={} a_gt_b={}'.format(
                    request.user.id,
                    form.cleaned_data['audio_a'],
                    form.cleaned_data['audio_b'],
                    form.cleaned_data['a_gt_b']
                )
            )
            if request.user.is_superuser == False:
                r.save()
            # Redirect back to ratings page for new rating:
            return HttpResponseRedirect(reverse('ratings:ratings'))
        logger.warning('Rating POST invalid for user={} form={}'.format(request.user.id, form))
        return HttpResponseRedirect(reverse('ratings:ratings'))

    # if a GET (or any other method) we'll create a blank form

    sound_file_a, sound_file_b, sentence_text = get_next_rating(request.user.id)

    form = RatingsForm(
        data={'audio_a': sound_file_a,
              'audio_b': sound_file_b},
        initial={'audio_a': sound_file_a,
                 'audio_b': sound_file_b}
    )

    rated = ratings_done(request.user.id)
    rated_goal = 50 # TODO make sentence set-specific

    logger.debug('New rating requested for user={} sound_file_a={} sound_file_b={}'.format(request.user.id, sound_file_a.id, sound_file_b.id))

    return render(request,
                  'ratings/ratings.html',
                  {'form': form,
                   'user_id': request.user.id,
                   'rated': rated,
                   'rated_progress': round(rated / rated_goal * 100),
                   'rated_goal': rated_goal,
                   'sentence_text': sentence_text,
                   'sound_file_a': sound_file_a.path,
                   'sound_file_b': sound_file_b.path})


@login_required
def mdpref_results(request):
    data = [get_mdpref_results(sentence_id) for sentence_id in range(1,41)]
    return render(request,
                  'ratings/mdpref.html',
                  {'data': data})


@login_required
def get_ratings_done(request):
    return JsonResponse({'ratings_done': ratings_done(request.user.id)})


@login_required
def ratings_export_table(request):
    data = get_all_ratings_summary()
    df = read_frame(data)
    return HttpResponse(df.to_html())


@login_required
def next_pair_export_table(request):
    data = get_unrated_pair(request.user.id)
    df = pd.DataFrame.from_records(data)
    return HttpResponse(df.to_html())

# from io import StringIO
# import datetime
# import hashlib

    # FIXME Pandoc's Excel export errors out in timestampz conversion (both engines).
    #sio = StringIO()
    # PandasWriter = pd.ExcelWriter(sio, engine='openpyxl') #engine='xlsxwriter')
    # PandasDataFrame.to_excel(PandasWriter, sheet_name='ratings_ratings')
    # PandasWriter.save()
    #
    # sio.seek(0)
    # workbook = sio.getvalue()
    #
    # h = hashlib.new('ripemd160')
    # h.update(data)
    # filename = 'jsrs-ratings-data-{}-{}.xlsx'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H%I'), h.hexdigest())
    #
    # response = StreamingHttpResponse(workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename
    # return response
