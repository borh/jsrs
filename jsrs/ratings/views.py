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
from .models import Ratings, get_next_rating, ratings_done, get_all_ratings_summary, get_unrated_pair, get_mdpref_results, get_complete_comparison_matrix, get_thurstone_results, get_c5ml_sentence_biplot, get_c5ml_rater_biplot
from .forms import RatingsForm

import logging
logger = logging.getLogger(__name__)

import random

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
            a_gt_b = form.cleaned_data['a_gt_b']

            # Enforce correct order in database.
            if audio_a.id > audio_b.id:
                audio_a, audio_b = audio_b, audio_a
                a_gt_b = not a_gt_b
                logger.debug('Reversing shuffling in ratings: a => {}, b => {}, a_gt_b => {}'.format(audio_a, audio_b, a_gt_b))

            r = Ratings(
                audio_a=audio_a,
                audio_b=audio_b,
                reader_a=audio_a.reader,
                reader_b=audio_b.reader,
                sentence=audio_a.sentence,
                a_gt_b=a_gt_b,
                user=request.user
            )
            logger.debug(
                'Rating POST requested for user={} sound_file_a={} sound_file_b={} a_gt_b={}'.format(
                    request.user.id,
                    audio_a,
                    audio_b,
                    a_gt_b
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

    # We randomize a and b to not reflect the bias in the data
    # ordering (lower ids for native speakers). Note that it is
    # necessary to reverse a and b and the rating when getting back
    # the results. Failure to do so will invalidate them.
    ab = [sound_file_a, sound_file_b]
    random.shuffle(ab)
    sound_file_a, sound_file_b = ab

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
    data = [get_mdpref_results(sentence_id) + tuple([get_thurstone_results(sentence_id)]) + tuple([get_complete_comparison_matrix(sentence_id)])
            for sentence_id in range(1, 41)]
    c5ml_sentence_biplot_svg = get_c5ml_sentence_biplot([m[1] for m in data])
    c5ml_rater_biplot_svg = get_c5ml_rater_biplot()
    return render(request,
                  'ratings/mdpref.html',
                  {'data': data,
                   'c5ml_sentence_biplot_svg': c5ml_sentence_biplot_svg,
                   'c5ml_rater_biplot_svg': c5ml_rater_biplot_svg})


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
    data = get_unrated_pair(request.user.id, limit=1000)
    df = pd.DataFrame.from_records(data, columns=['a_audio_id', 'b_audio_id', 'a_reader', 'b_reader', 'sentence_id', 'w_a', 'w_b', 'n_a', 'n_b'])
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
