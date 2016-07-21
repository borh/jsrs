
from unittest import TestCase
from django.core.management import call_command

from concurrent.futures import ThreadPoolExecutor

from ..models import Ratings, get_next_rating, get_all_ratings, get_audio_summary, get_unrated_pair, get_mdpref_results
from ...users.models import Rater, User
from ...audio.models import Audio, Reader

# Using Django's TestCase does not load/unload fixtures at the right level. FIXME
# from django.test import TestCase, TransactionTestCase
class RatingsTestCase(TestCase):
    @classmethod
    def setUpClass(self):
        super(RatingsTestCase, self).setUpClass()
        # We load fixtures manually here because we need to persist them across all tests here. Using the top-level fixtures = [...] will not work.
        call_command('loaddata', 'jsrs/audio/fixtures/audio-sentence-fixtures.json', verbosity=0)
        call_command('loaddata', 'jsrs/audio/fixtures/audio-reader-fixtures.json', verbosity=0)
        call_command('loaddata', 'jsrs/audio/fixtures/audio-audio-fixtures.json', verbosity=0)

        self.n_users = 2
        self.n_ratings = 36 * 8 + 1
        #self.gold_preferences = {r.id: r.id for r in Reader.objects.filter(disabled=False)} # lower id = more proficient
        self.users = [User.objects.create(name='User_{}'.format(i+1),
                                          username=str(i+1))
                      for i in range(self.n_users)]


    def rate(self, user):
        a, b, text = get_next_rating(user.id)

        self.assertNotEqual(a.id, b.id)
        self.assertNotEqual(a.reader, b.reader)
        self.assertEqual(a.sentence, b.sentence)

        # lower id = more proficient
        verdict = a.reader.id < b.reader.id

        r = Ratings.objects.create(
            audio_a=a,
            audio_b=b,
            reader_a=a.reader,
            reader_b=b.reader,
            sentence=a.sentence, # == b.sentence
            a_gt_b=verdict, # random.choice([True, False]),
            user=user
        )

    # FIXME fixtures loading/unloading and ratings loading/unloading interaction must be fixed to allow all tests to run.
    def _test_sequential_ratings(self):
        for user in self.users:
            for _ in range(self.n_ratings):
                self.rate(user)
        self.assertEqual(len(Ratings.objects.all()), self.n_users*self.n_ratings)

    def _test_crossed_ratings(self):
        for _ in range(self.n_ratings):
            for user in self.users:
                self.rate(user)
        self.assertEqual(len(Ratings.objects.all()), self.n_users*self.n_ratings)

        for sentence_id in range(1,41):
            r = get_mdpref_results(sentence_id)
            self.assertNotEqual(r, (None, None))

    def test_concurrent_ratings(self):
        # FIXME Currently the thread pool workers don't close their Postgresql connection, so the test runner bails out after this test.
        with ThreadPoolExecutor(max_workers=self.n_users) as executor:
            for _ in range(self.n_ratings):
                for user in self.users:
                    future = executor.submit(self.rate, user)
        self.assertEqual(len(Ratings.objects.all()), self.n_users*self.n_ratings)
        for sentence_id in range(1,41):
            r = get_mdpref_results(sentence_id)
            self.assertNotEqual(r, (None, None))

# TODO
# from hypothesis.extra.django.models import models
# from hypothesis.extra.django import TestCase
# from hypothesis import given
# from hypothesis.strategies import lists, just
#
# def generate_ratings_with_user(user):
#   return lists(models(Ratings, user=just(user))).map(lambda _: user)
#
# ratings_with_user_strategy = models(Ratings).flatmap(generate_ratings_with_user)
#
# class RatingsTestCase(TestCase):
#     @given(ratings_with_user_strategy(model(Ratings,
#                                             audio_a=models(Audio),
#                                             audio_b=models(Audio),
#                                             reader_a=models(Reader),
#                                             reader_b=models(Reader),
#                                             sentence=models(Sentence))))
