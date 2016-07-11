from hypothesis.extra.django.models import models
from hypothesis.extra.django import TestCase
from hypothesis import given
from django_concurrent_tests.helpers import make_concurrent_calls

from ..models import Ratings
from ...users.models import Rater, User

def is_success(result):
    return result is True and not isinstance(result, Exception)

# def test_concurrent_code():
#     calls = [
#         (first_func, {'first_arg': 1}),
#         (second_func, {'other_arg': 'wtf'}),
#     ] * 3
#     results = make_concurrent_calls(*calls)
#     # results contains the return value from each call
#     successes = list(filter(is_success, results))
#     assert len(successes) == 1

class RatingsTestCase(TestCase):
    @given(models(Rater, user=models(User)))
    def test_ratings_concurrently(self, rater):
        # generate a series of ratings
        calls = [
            (first_func, {'first_arg': 1}),
            (second_func, {'other_arg': 'wtf'}),
        ] * 3
        # send POST requests of ratings concurrently
        results = make_concurrent_calls(*calls)
        # results contains the return value from each call
        successes = list(filter(is_success, results))
        assert len(successes) == 1
